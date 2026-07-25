/**
 * Homepage "Patient Feedback & Reviews" strip — reverse auto-scroll below photo gallery.
 * Shows the latest Patient Care photos from the gallery; the strip links to videos/.
 */
(function () {
  const STRIP_LIMIT = 10;
  const CATEGORY = "Patient Care";
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
      // Latest uploads = last entries in gallery.json
      const patientCare = (data.images || [])
        .filter((img) => img.category === CATEGORY)
        .slice()
        .reverse()
        .slice(0, STRIP_LIMIT);
      if (!patientCare.length) {
        track.closest(".hp-media-strip")?.remove();
        return;
      }

      const items = patientCare.map((img, i) => renderItem(img, i)).join("");
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
