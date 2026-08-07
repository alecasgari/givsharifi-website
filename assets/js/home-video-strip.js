/**
 * Homepage Videos strip — reverse auto-scroll below photo gallery.
 * Latest gallery photos excluding Patient Care; strip links to videos/.
 */
(function () {
  const STRIP_LIMIT = 10;
  const EXCLUDE_CATEGORY = "Patient Care";
  const track = document.getElementById("home-video-strip-track");
  if (!track) return;

  function u(path) {
    return typeof window.siteUrl === "function" ? window.siteUrl(path) : path;
  }

  function showSkeleton() {
    if (window.GivSkeleton) {
      track.innerHTML = window.GivSkeleton.homeGalleryStrip(STRIP_LIMIT);
    }
    const section = document.getElementById("home-video-strip-section");
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
      // Newest uploads first; skip Patient Care (those stay in the top gallery strip when recent)
      const photos = (data.images || [])
        .filter((img) => img.category !== EXCLUDE_CATEGORY)
        .slice()
        .reverse()
        .slice(0, STRIP_LIMIT);
      if (!photos.length) {
        track.closest(".hp-media-strip")?.remove();
        return;
      }

      const items = photos.map((img, i) => renderItem(img, i)).join("");
      track.innerHTML = items + items;
      track.classList.add("is-ready");
      const section = document.getElementById("home-video-strip-section");
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
