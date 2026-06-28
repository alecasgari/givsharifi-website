/**
 * Photo gallery page — /gallery/
 */
(function () {
  const grid = document.getElementById("gal-grid");
  const searchInput = document.getElementById("gal-search");
  const countEl = document.getElementById("gal-count");
  const updatedEl = document.getElementById("gal-updated");

  if (!grid) return;

  function u(path) {
    return typeof window.siteUrl === "function" ? window.siteUrl(path) : path;
  }

  let allImages = [];
  let debounceTimer;

  async function init() {
    if (window.GivSkeleton) {
      grid.innerHTML = window.GivSkeleton.galleryGrid(8);
    }
    try {
      const res = await fetch(u("assets/data/gallery.json"));
      if (!res.ok) throw new Error("Failed to load");
      const data = await res.json();
      allImages = (data.images || []).slice().reverse();
      if (updatedEl && data.updated) updatedEl.textContent = `Last updated ${data.updated}`;
      render();
      bindEvents();
    } catch (e) {
      grid.innerHTML = '<p class="gal-loading">Unable to load gallery. Please try again later.</p>';
      console.error(e);
    }
  }

  function bindEvents() {
    if (!searchInput) return;
    searchInput.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(render, 200);
    });
  }

  function getFiltered() {
    const q = (searchInput?.value || "").trim().toLowerCase();
    if (!q) return allImages;
    return allImages.filter((img) => {
      const hay = [img.title, img.alt, img.category].join(" ").toLowerCase();
      return hay.includes(q);
    });
  }

  function toLightboxItems(list) {
    return list.map((img) => ({
      src: u(img.file),
      alt: img.alt || "",
      caption: img.title || img.alt || "",
    }));
  }

  function render() {
    const list = getFiltered();
    if (countEl) {
      countEl.textContent =
        list.length === allImages.length
          ? `${list.length} photos`
          : `${list.length} of ${allImages.length}`;
    }

    if (!list.length) {
      grid.innerHTML =
        '<p class="gal-empty">No photos yet. Check back soon.</p>';
      return;
    }

    grid.innerHTML = list
      .map(
        (img, index) => `
      <button type="button" class="gal-card" data-lightbox data-lightbox-index="${index}"
        data-lightbox-src="${escapeAttr(u(img.file))}"
        data-lightbox-alt="${escapeAttr(img.alt)}"
        data-lightbox-caption="${escapeAttr(img.title || img.alt)}">
        <img class="gal-card__img" src="${escapeAttr(u(img.thumb || img.file))}"
          alt="${escapeAttr(img.alt)}" width="${img.width || 640}" height="${img.height || 480}" loading="lazy">
        <span class="gal-card__overlay">
          <span class="gal-card__title">${escapeHtml(img.title || img.alt)}</span>
          ${img.category ? `<span class="gal-card__cat">${escapeHtml(img.category)}</span>` : ""}
        </span>
      </button>
    `
      )
      .join("");

    if (window.GivLightbox) {
      window.GivLightbox.bindGalleryGrid(grid, toLightboxItems(list));
    }
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(str) {
    return escapeHtml(str).replace(/'/g, "&#39;");
  }

  init();
})();
