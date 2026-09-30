const species = {
  hyena: {
    name: "Spotted hyena", anchor: "Whoop", duration: "1.78 s",
    prompt: "A vocalization is heard from a spotted hyena when it seeks distant clan contact.",
    sample: "whoop_sample_1009.wav", audio: "audio/hyena-whoop-generated.wav",
  },
  meerkat: {
    name: "Meerkat", anchor: "Alarm call", duration: "0.88 s",
    prompt: "An animal sound comes from a warning meerkat when it watches for a predator.",
    sample: "alarm_call_sample_408.wav", audio: "audio/meerkat-alarm-generated.wav",
  },
  marmoset: {
    name: "Common marmoset", anchor: "Phee", duration: "2.15 s",
    prompt: "An audible sound is heard when a marmoset reaches conspecifics outside sight.",
    sample: "Phee_sample_1.wav", audio: "audio/marmoset-phee-generated.wav",
  },
  goat: {
    name: "Domestic goat", anchor: "Mother-kid reunion", duration: "2.00 s",
    prompt: "A sound occurs when a goat kid reaches its mother goat after separation.",
    sample: "Mother-kid reunion_sample_0.wav", audio: "audio/goat-reunion-generated.wav",
  },
  zebra: {
    name: "Plains zebra", anchor: "Quagga quagga", duration: "1.75 s",
    prompt: "A vocal sound occurs while a separated plains zebra seeks contact.",
    sample: "quagga quagga_sample_0.wav", audio: "audio/zebra-contact-generated.wav",
  },
  "zebra-finch": {
    name: "Zebra finch", anchor: "Song", duration: "4.22 s",
    prompt: "An animal sound is audible while an adult male zebra finch performs courtship.",
    sample: "song_sample_1.wav", audio: "audio/zebra-finch-song-generated.wav",
  },
};

const tabs = [...document.querySelectorAll("[data-species]")];
const prompt = document.querySelector("[data-prompt]");
const speciesName = document.querySelector("[data-species-name]");
const anchor = document.querySelector("[data-anchor]");
const duration = document.querySelector("[data-duration]");
const sampleId = document.querySelector("[data-sample-id]");
const generatedAudio = document.querySelector("[data-generated-audio]");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const selected = species[tab.dataset.species];
    tabs.forEach((candidate) => candidate.setAttribute("aria-selected", String(candidate === tab)));
    speciesName.textContent = selected.name;
    anchor.textContent = selected.anchor;
    duration.textContent = selected.duration;
    prompt.textContent = selected.prompt;
    sampleId.textContent = selected.sample;
    generatedAudio.pause();
    generatedAudio.src = selected.audio;
    generatedAudio.setAttribute("aria-label", `Generated ${selected.name} vocalization`);
    generatedAudio.load();
  });
});

const menuButton = document.querySelector(".menu-button");
const mobileMenu = document.querySelector("#mobile-menu");

menuButton.addEventListener("click", () => {
  const isOpen = menuButton.getAttribute("aria-expanded") === "true";
  menuButton.setAttribute("aria-expanded", String(!isOpen));
  mobileMenu.hidden = isOpen;
});

mobileMenu.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    menuButton.setAttribute("aria-expanded", "false");
    mobileMenu.hidden = true;
  });
});

const copyButton = document.querySelector("[data-copy-citation]");
const citation = document.querySelector("[data-citation]");
const copyStatus = document.querySelector("[data-copy-status]");

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(citation.textContent);
    copyButton.textContent = "Copied";
    copyStatus.textContent = "Citation copied to clipboard.";
    window.setTimeout(() => {
      copyButton.textContent = "Copy BibTeX";
      copyStatus.textContent = "";
    }, 2200);
  } catch {
    copyStatus.textContent = "Select the citation text to copy it manually.";
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
