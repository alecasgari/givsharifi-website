/**
 * Landing strip — 5 random landscape gallery photos, infinite horizontal scroll.
 */
(function () {
  const SLIDE_COUNT = 5;
  const track = document.getElementById("gl-track");
  if (!track) return;

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

  function isLandscape(img) {
    const w = Number(img.width) || 0;
    const h = Number(img.height) || 0;
    return w > 0 && h > 0 && w > h;
  }

  function mixedLandscape(images, limit) {
    const landscape = images.filter(isLandscape);
    const byCategory = new Map();
    landscape.forEach((img) => {
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
    return shuffle(mixed).slice(0, limit);
  }

  function renderItem(img, index) {
    const src = u(img.thumb || img.file);
    const eager = index < 2 ? "eager" : "lazy";
    return `
      <div class="gl__item">
        <img src="${escapeAttr(src)}" alt="" width="640" height="400" decoding="async" loading="${eager}">
      </div>
    `;
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
      const picks = mixedLandscape(data.images || [], SLIDE_COUNT);
      if (!picks.length) return;
      const items = picks.map((img, i) => renderItem(img, i)).join("");
      track.innerHTML = items + items;
      track.classList.add("is-ready");
    } catch (e) {
      // Leave empty if gallery cannot load.
    }
  }

  init();
})();
