/**
 * Homepage featured gallery strip — auto-scroll below hero stats.
 */
(function () {
  const track = document.getElementById("home-gallery-track");
  if (!track) return;

  function u(path) {
    return typeof window.siteUrl === "function" ? window.siteUrl(path) : path;
  }

  function showSkeleton() {
    if (window.GivSkeleton) {
      track.innerHTML = window.GivSkeleton.homeGalleryStrip(6);
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
      const featured = (data.images || []).filter((img) => img.featured);
      if (!featured.length) {
        track.closest(".hp-gallery-strip")?.remove();
        return;
      }

      const items = featured
        .map(
          (img) => `
        <a class="hp-gallery-strip__item" href="gallery/" title="${escapeAttr(img.title || img.alt)}">
          <img src="${escapeAttr(u(img.thumb || img.file))}" alt="${escapeAttr(img.alt)}"
            width="${img.width || 400}" height="${img.height || 300}" loading="lazy">
        </a>
      `
        )
        .join("");

      track.innerHTML = items + items;
      track.classList.add("is-ready");
      const section = document.getElementById("home-gallery-section");
      if (section) section.hidden = false;
    } catch (e) {
      track.closest(".hp-gallery-strip")?.remove();
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
