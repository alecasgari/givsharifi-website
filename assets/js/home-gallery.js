/**
 * Homepage featured gallery strip — auto-scroll below hero stats.
 */
(function () {
  const STRIP_LIMIT = 4;
  const track = document.getElementById("home-gallery-track");
  if (!track) return;

  function u(path) {
    return typeof window.siteUrl === "function" ? window.siteUrl(path) : path;
  }

  function showSkeleton() {
    if (window.GivSkeleton) {
      track.innerHTML = window.GivSkeleton.homeGalleryStrip(STRIP_LIMIT);
    }
    const section = document.getElementById("home-gallery-section");
    if (section) section.hidden = false;
  }

  function renderItem(img, index) {
    const src = u(img.strip || img.thumb || img.file);
    const eager = index < 2 ? "eager" : "lazy";
    return `
      <div class="hp-media-strip__item" aria-hidden="true">
        <img src="${escapeAttr(src)}" alt=""
          width="280" height="210"
          sizes="(max-width: 768px) 28vw, 16rem"
          decoding="async" loading="${eager}">
      </div>
    `;
  }

  async function init() {
    showSkeleton();
    try {
      const res = await fetch(u("assets/data/gallery.json"));
      if (!res.ok) throw new Error("Failed to load");
      const data = await res.json();
      const featured = (data.images || []).filter((img) => img.featured).slice(0, STRIP_LIMIT);
      if (!featured.length) {
        track.closest(".hp-media-strip")?.remove();
        return;
      }

      const items = featured.map((img, i) => renderItem(img, i)).join("");
      track.innerHTML = items + items;
      track.classList.add("is-ready");
      const section = document.getElementById("home-gallery-section");
      if (section) section.hidden = false;
    } catch (e) {
      track.closest(".hp-media-strip")?.remove();
    }
  }

  function escapeAttr(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  init();
})();
