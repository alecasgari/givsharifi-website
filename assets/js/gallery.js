/**
 * Photo gallery page — /gallery/
 */
(function () {
  const grid = document.getElementById("gal-grid");
  const searchInput = document.getElementById("gal-search");
  const countEl = document.getElementById("gal-count");
  const updatedEl = document.getElementById("gal-updated");
  const filtersEl = document.getElementById("gal-filters");

  if (!grid) return;

  function u(path) {
    return typeof window.siteUrl === "function" ? window.siteUrl(path) : path;
  }

  let allImages = [];
  let debounceTimer;
  let activeCategory = "";

  function normalizeCategory(value) {
    if (!value) return "";
    return String(value).replace(/,+\s*$/, "").trim();
  }

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
      buildFilters();
      render();
      bindEvents();
    } catch (e) {
      grid.innerHTML = '<p class="gal-loading">Unable to load gallery. Please try again later.</p>';
      console.error(e);
    }
  }

  function getCategories() {
    const counts = new Map();
    allImages.forEach((img) => {
      const cat = normalizeCategory(img.category);
      if (!cat) return;
      counts.set(cat, (counts.get(cat) || 0) + 1);
    });
    return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  }

  function buildFilters() {
    if (!filtersEl) return;
    const categories = getCategories();
    const buttons = [
      `<button type="button" class="gal-filter-btn is-active" data-gal-category="" aria-pressed="true">All photos</button>`,
      ...categories.map(
        ([cat, count]) =>
          `<button type="button" class="gal-filter-btn" data-gal-category="${escapeAttr(cat)}" aria-pressed="false">${escapeHtml(cat)} <span class="gal-filter-btn__count">(${count})</span></button>`
      ),
    ];
    filtersEl.innerHTML = buttons.join("");
  }

  function bindEvents() {
    if (searchInput) {
      searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(render, 200);
      });
    }
    if (filtersEl) {
      filtersEl.addEventListener("click", (e) => {
        const btn = e.target.closest("[data-gal-category]");
        if (!btn) return;
        activeCategory = btn.dataset.galCategory || "";
        filtersEl.querySelectorAll(".gal-filter-btn").forEach((el) => {
          const on = el === btn;
          el.classList.toggle("is-active", on);
          el.setAttribute("aria-pressed", on ? "true" : "false");
        });
        render();
      });
    }
  }

  function getFiltered() {
    const q = (searchInput?.value || "").trim().toLowerCase();
    return allImages.filter((img) => {
      if (activeCategory && normalizeCategory(img.category) !== activeCategory) return false;
      if (!q) return true;
      const hay = [img.title, img.alt, normalizeCategory(img.category)].join(" ").toLowerCase();
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
    const filtered = list.length !== allImages.length || activeCategory || (searchInput?.value || "").trim();

    if (countEl) {
      countEl.textContent = filtered
        ? `Showing ${list.length} of ${allImages.length}`
        : `${list.length} photo${list.length !== 1 ? "s" : ""}`;
    }

    if (!list.length) {
      grid.innerHTML =
        '<p class="gal-empty">No photos match your search or category filter.</p>';
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
          ${normalizeCategory(img.category) ? `<span class="gal-card__cat">${escapeHtml(normalizeCategory(img.category))}</span>` : ""}
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
