/**
 * Homepage featured gallery strip — auto-scroll below hero stats.
 */
(function () {
  const STRIP_LIMIT = 6;
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

      const items = featured
        .map(
          (img) => `
        <a class="hp-media-strip__item" href="gallery/" title="${escapeAttr(img.title || img.alt)}">
          <img src="${escapeAttr(u(img.strip || img.thumb || img.file))}" alt="${escapeAttr(img.alt)}"
            width="${img.width || 400}" height="${img.height || 300}"
            sizes="(max-width: 768px) 28vw, 16rem"
            decoding="async" fetchpriority="low" loading="eager">
        </a>
      `
        )
        .join("");

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
