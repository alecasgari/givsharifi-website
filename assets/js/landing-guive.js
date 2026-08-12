/**
 * Landing slider — mixed random gallery photos, larger frames.
 */
(function () {
  const SLIDE_COUNT = 12;
  const INTERVAL_MS = 3500;
  const slider = document.getElementById("gl-slider");
  if (!slider) return;

  function u(path) {
    return typeof window.siteUrl === "function" ? window.siteUrl(path) : path;
  }

  function shuffle(list) {
    const arr = list.slice();
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = arr[i];
      arr[i] = arr[j];
      arr[j] = tmp;
    }
    return arr;
  }

  function mixedRandom(images, limit) {
    const byCategory = new Map();
    images.forEach((img) => {
      const cat = img.category || "Other";
      if (!byCategory.has(cat)) byCategory.set(cat, []);
      byCategory.get(cat).push(img);
    });

    const buckets = [...byCategory.values()].map((group) => shuffle(group));
    const mixed = [];
    let added = true;
    while (mixed.length < limit && added) {
      added = false;
      buckets.forEach((group) => {
        if (mixed.length >= limit || !group.length) return;
        mixed.push(group.shift());
        added = true;
      });
    }
    return shuffle(mixed);
  }

  function renderSlides(images) {
    slider.innerHTML = images
      .map((img, i) => {
        const src = u(img.thumb || img.file);
        const eager = i === 0 ? "eager" : "lazy";
        const active = i === 0 ? " is-active" : "";
        return `<img class="gl__slide${active}" src="${escapeAttr(src)}" alt="" width="640" height="480" decoding="async" loading="${eager}">`;
      })
      .join("");
  }

  function startRotation() {
    const slides = slider.querySelectorAll(".gl__slide");
    if (slides.length < 2) return;
    let index = 0;
    setInterval(() => {
      slides[index].classList.remove("is-active");
      index = (index + 1) % slides.length;
      slides[index].classList.add("is-active");
    }, INTERVAL_MS);
  }

  function escapeAttr(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  async function init() {
    try {
      const res = await fetch(u("assets/data/gallery.json"));
      if (!res.ok) throw new Error("Failed to load");
      const data = await res.json();
      const picks = mixedRandom(data.images || [], SLIDE_COUNT);
      if (!picks.length) return;
      renderSlides(picks);
      startRotation();
    } catch (e) {
      // Keep fallback portrait already in HTML.
    }
  }

  init();
})();
