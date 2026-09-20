const species = {
  hyena: { name: "Spotted hyena", short: "hyena" },
  meerkat: { name: "Meerkat", short: "meerkat" },
  marmoset: { name: "Common marmoset", short: "marmoset" },
  goat: { name: "Domestic goat", short: "goat" },
  zebra: { name: "Plains zebra", short: "zebra" },
  "zebra-finch": { name: "Zebra finch", short: "zebra finch" },
};

const tabs = [...document.querySelectorAll("[data-species]")];
const prompt = document.querySelector("[data-prompt]");
const speciesName = document.querySelector("[data-species-name]");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const selected = species[tab.dataset.species];
    tabs.forEach((candidate) => candidate.setAttribute("aria-selected", String(candidate === tab)));
    speciesName.textContent = selected.name;
    prompt.textContent = `Add a literature-grounded ${selected.short} behavior condition here.`;
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
