const fallbackSpecies = {
  hyena: {
    name: "Spotted hyena", anchor: "Whoop",
    prompt: "A vocalization is heard from a spotted hyena when it seeks distant clan contact.",
    realAudio: "audio/hyena-whoop-real.wav",
    audio: "audio/hyena-whoop-generated.wav",
  },
  meerkat: {
    name: "Meerkat", anchor: "Alarm call",
    prompt: "An animal sound comes from a warning meerkat when it watches for a predator.",
    realAudio: "audio/meerkat-alarm-real.wav",
    audio: "audio/meerkat-alarm-generated.wav",
  },
  marmoset: {
    name: "Common marmoset", anchor: "Phee",
    prompt: "An audible sound is heard when a marmoset reaches conspecifics outside sight.",
    realAudio: "audio/marmoset-phee-real.wav",
    audio: "audio/marmoset-phee-generated.wav",
  },
  goat: {
    name: "Domestic goat", anchor: "Mother-kid reunion",
    prompt: "A sound occurs when a goat kid reaches its mother goat after separation.",
    realAudio: "audio/goat-reunion-real.wav",
    audio: "audio/goat-reunion-generated.wav",
  },
  zebra: {
    name: "Plains zebra", anchor: "Quagga quagga",
    prompt: "A vocal sound occurs while a separated plains zebra seeks contact.",
    realAudio: "audio/zebra-contact-real.wav",
    audio: "audio/zebra-contact-generated.wav",
  },
  "zebra-finch": {
    name: "Zebra finch", anchor: "Song",
    prompt: "An animal sound is audible while an adult male zebra finch performs courtship.",
    realAudio: "audio/zebra-finch-song-real.wav",
    audio: "audio/zebra-finch-song-generated.wav",
  },
};

// Keep the original playable pairs if the catalog script is unavailable.
const fallbackSamples = Object.fromEntries(
  Object.entries(fallbackSpecies).map(([key, item]) => [key, {
    name: item.name,
    samples: [{
      id: key,
      label: item.anchor,
      prompt: item.prompt,
      realAudio: item.realAudio,
      generatedAudio: item.audio,
    }],
  }]),
);
const sampleCatalog = typeof demoSamples !== "undefined" ? demoSamples : {};
const species = Object.fromEntries(
  Object.entries(fallbackSamples).map(([key, fallback]) => {
    const item = sampleCatalog[key];
    return [key, item && Array.isArray(item.samples) && item.samples.length ? item : fallback];
  }),
);

const tabs = [...document.querySelectorAll("[data-species]")];
const prompt = document.querySelector("[data-prompt]");
const speciesName = document.querySelector("[data-species-name]");
const anchor = document.querySelector("[data-anchor]");
const duration = document.querySelector("[data-duration]");
const referenceAudio = document.querySelector("[data-reference-audio]");
const generatedAudio = document.querySelector("[data-generated-audio]");
const referenceDuration = document.querySelector("[data-reference-duration]");
const generatedDuration = document.querySelector("[data-generated-duration]");
const anchorButtons = document.querySelector("[data-anchor-buttons]");
const anchorCount = document.querySelector("[data-anchor-count]");
const samplePanel = document.querySelector("#sample-panel");
const sampleStatus = document.querySelector("[data-sample-status]");
const spectrumControl = document.querySelector("[data-spectrogram-control]");
const spectrumToggle = document.querySelector("[data-spectrogram-toggle]");
const spectrumFigures = [
  {
    figure: document.querySelector("[data-reference-spectrogram]"),
    image: document.querySelector("[data-reference-spectrogram-image]"),
    link: document.querySelector("[data-reference-spectrogram-link]"),
    pathKey: "realSpectrogram",
    description: "Real test recording",
  },
  {
    figure: document.querySelector("[data-generated-spectrogram]"),
    image: document.querySelector("[data-generated-spectrogram-image]"),
    link: document.querySelector("[data-generated-spectrogram-link]"),
    pathKey: "generatedSpectrogram",
    description: "Final Event-Aware model output",
  },
];
const selectedSamples = new Map();
let selectedSpecies = "hyena";
let selectedSample;
let spectraVisible = true;

function setText(element, value) {
  if (element) element.textContent = value;
}

function formatDuration(value) {
  const seconds = Number(value);
  return Number.isFinite(seconds) && seconds > 0 ? `${seconds.toFixed(2)} s` : "—";
}

function updateSpectrograms() {
  const hasSpectrograms = spectrumFigures.some((item) => selectedSample?.[item.pathKey]);
  if (spectrumControl) spectrumControl.hidden = !hasSpectrograms;
  spectrumFigures.forEach(({ figure, image, link, pathKey, description }) => {
    if (!figure || !image) return;
    const path = selectedSample?.[pathKey];
    figure.hidden = !spectraVisible || !path;
    if (path) {
      if (image.getAttribute("src") !== path) image.src = path;
      image.alt = `${description}: ${species[selectedSpecies].name}, ${selectedSample.label}`;
      if (link) link.href = path;
    } else {
      image.removeAttribute("src");
      if (link) link.removeAttribute("href");
    }
  });
  if (spectrumToggle) {
    spectrumToggle.setAttribute("aria-expanded", String(spectraVisible));
    setText(spectrumToggle, spectraVisible ? "Hide spectrograms" : "Show spectrograms");
  }
}

function selectSample(id, announce = true) {
  const item = species[selectedSpecies];
  const sample = item?.samples.find((candidate) => String(candidate.id) === String(id)) || item?.samples[0];
  if (!sample) return;
  selectedSample = sample;
  selectedSamples.set(selectedSpecies, sample.id);
  setText(speciesName, item.name);
  setText(anchor, sample.label);
  setText(prompt, sample.prompt);
  setText(duration, formatDuration(sample.realDuration ?? sample.duration));
  setText(referenceDuration, `Duration: ${formatDuration(sample.realDuration ?? sample.duration)}`);
  setText(generatedDuration, `Duration: ${formatDuration(sample.generatedDuration ?? sample.duration)}`);
  [
    [referenceAudio, sample.realAudio, "Real test recording"],
    [generatedAudio, sample.generatedAudio, "Final Event-Aware model output"],
  ].forEach(([audio, path, description]) => {
    if (!audio || !path) return;
    audio.pause();
    audio.src = path;
    audio.setAttribute("aria-label", `${description}: ${item.name}, ${sample.label}`);
    audio.load();
  });
  anchorButtons?.querySelectorAll("[data-sample-id]").forEach((button) => {
    const active = button.dataset.sampleId === String(sample.id);
    button.setAttribute("aria-pressed", String(active));
    button.tabIndex = active ? 0 : -1;
  });
  updateSpectrograms();
  if (announce) setText(sampleStatus, `${item.name}: ${sample.label}. Real and generated audio are ready.`);
}

function renderAnchors(item) {
  if (!anchorButtons) return;
  anchorButtons.replaceChildren();
  item.samples.forEach((sample) => {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.sampleId = String(sample.id);
    button.textContent = sample.label;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => selectSample(sample.id));
    anchorButtons.append(button);
  });
  setText(anchorCount, `${item.samples.length} condition ${item.samples.length === 1 ? "label" : "labels"} · 1 pair per label`);
}

function selectSpecies(key, announce = true) {
  const item = species[key];
  if (!item) return;
  selectedSpecies = key;
  tabs.forEach((tab) => {
    const active = tab.dataset.species === key;
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
    if (active && samplePanel) samplePanel.setAttribute("aria-labelledby", tab.id);
  });
  renderAnchors(item);
  selectSample(selectedSamples.get(key) ?? item.samples[0].id, announce);
}

function keyboardSelection(event, buttons) {
  const currentIndex = buttons.indexOf(event.target);
  if (currentIndex < 0) return;
  let nextIndex;
  if (event.key === "ArrowRight" || event.key === "ArrowDown") nextIndex = (currentIndex + 1) % buttons.length;
  else if (event.key === "ArrowLeft" || event.key === "ArrowUp") nextIndex = (currentIndex - 1 + buttons.length) % buttons.length;
  else if (event.key === "Home") nextIndex = 0;
  else if (event.key === "End") nextIndex = buttons.length - 1;
  else return;
  event.preventDefault();
  buttons[nextIndex].click();
  buttons[nextIndex].focus();
  buttons[nextIndex].scrollIntoView({ block: "nearest", inline: "nearest" });
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => selectSpecies(tab.dataset.species));
  tab.addEventListener("keydown", (event) => keyboardSelection(event, tabs));
});
anchorButtons?.addEventListener("keydown", (event) => {
  keyboardSelection(event, [...anchorButtons.querySelectorAll("button")]);
});
spectrumToggle?.addEventListener("click", () => {
  spectraVisible = !spectraVisible;
  updateSpectrograms();
});
referenceAudio?.addEventListener("play", () => generatedAudio?.pause());
generatedAudio?.addEventListener("play", () => referenceAudio?.pause());
referenceAudio?.addEventListener("loadedmetadata", () => {
  setText(duration, formatDuration(referenceAudio.duration));
  setText(referenceDuration, `Duration: ${formatDuration(referenceAudio.duration)}`);
});
generatedAudio?.addEventListener("loadedmetadata", () => {
  setText(generatedDuration, `Duration: ${formatDuration(generatedAudio.duration)}`);
});
spectrumFigures.forEach(({ figure, image }) => {
  image?.addEventListener("error", () => {
    if (figure) figure.hidden = true;
  });
});
selectSpecies(tabs.find((tab) => tab.getAttribute("aria-selected") === "true")?.dataset.species || "hyena", false);

const menuButton = document.querySelector(".menu-button");
const mobileMenu = document.querySelector("#mobile-menu");

menuButton?.addEventListener("click", () => {
  if (!mobileMenu) return;
  const isOpen = menuButton.getAttribute("aria-expanded") === "true";
  menuButton.setAttribute("aria-expanded", String(!isOpen));
  mobileMenu.hidden = isOpen;
});

mobileMenu?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    menuButton?.setAttribute("aria-expanded", "false");
    mobileMenu.hidden = true;
  });
});

const copyButton = document.querySelector("[data-copy-citation]");
const citation = document.querySelector("[data-citation]");
const copyStatus = document.querySelector("[data-copy-status]");

copyButton?.addEventListener("click", async () => {
  if (!citation) return;
  try {
    await navigator.clipboard.writeText(citation.textContent);
    copyButton.textContent = "Copied";
    setText(copyStatus, "Citation copied to clipboard.");
    window.setTimeout(() => {
      copyButton.textContent = "Copy BibTeX";
      setText(copyStatus, "");
    }, 2200);
  } catch {
    setText(copyStatus, "Select the citation text to copy it manually.");
  }
});

const sections = [...document.querySelectorAll("main section[id]")];
const navLinks = [...document.querySelectorAll(".desktop-nav a")];

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      navLinks.forEach((link) => {
        link.toggleAttribute("aria-current", link.getAttribute("href") === `#${visible.target.id}`);
      });
    },
    { rootMargin: "-20% 0px -65%", threshold: [0.05, 0.2, 0.5] },
  );
  sections.forEach((section) => observer.observe(section));
}
