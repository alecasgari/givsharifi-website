/**
 * Homepage video poster strip — reverse auto-scroll below photo gallery.
 */
(function () {
  const STRIP_LIMIT = 4;
  const track = document.getElementById("home-video-strip-track");
  if (!track) return;

  function u(path) {
    return typeof window.siteUrl === "function" ? window.siteUrl(path) : path;
  }

  function posterUrl(config, poster) {
    if (!poster) return "";
    const prefix = (config.pathPrefix || "").replace(/^\/|\/$/g, "");
    const name = String(poster).replace(/^\//, "");
    if (config.baseUrl) {
      const base = config.baseUrl.replace(/\/$/, "");
      return prefix ? `${base}/${prefix}/${name}` : `${base}/${name}`;
    }
    return prefix ? `${prefix}/${name}` : name;
  }

  function showSkeleton() {
    if (window.GivSkeleton) {
      track.innerHTML = window.GivSkeleton.homeGalleryStrip(STRIP_LIMIT)
        .replace(/skeleton-strip-item/g, "skeleton-strip-item skeleton-strip-item--video");
    }
    const section = document.getElementById("home-video-strip-section");
    if (section) section.hidden = false;
  }

  function renderItem(poster, index) {
    const eager = index < 2 ? "eager" : "lazy";
    return `
      <div class="hp-media-strip__item hp-media-strip__item--video" aria-hidden="true">
        <img src="${escapeAttr(poster)}" alt=""
          width="280" height="498"
          sizes="(max-width: 768px) 18vw, 9.5rem"
          decoding="async" loading="${eager}">
      </div>
    `;
  }

  async function init() {
    showSkeleton();
    try {
      const res = await fetch(u("assets/data/video-library.json"));
      if (!res.ok) throw new Error("Failed to load");
      const config = await res.json();
      const videos = (config.videos || []).slice(0, STRIP_LIMIT);
      if (!videos.length) {
        track.closest(".hp-media-strip")?.remove();
        return;
      }

      const items = videos
        .map((v, i) => renderItem(posterUrl(config, v.poster), i))
        .join("");

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
