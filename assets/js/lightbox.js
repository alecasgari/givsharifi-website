/**
 * Accessible image lightbox with gallery prev/next and swipe.
 */
(function (global) {
  let dialog = null;
  let lastFocus = null;
  let galleryItems = [];
  let galleryIndex = -1;
  let touchStartX = 0;

  function ensureDialog() {
    if (dialog) return dialog;
    dialog = document.createElement("div");
    dialog.className = "giv-lightbox";
    dialog.hidden = true;
    dialog.innerHTML = `
      <div class="giv-lightbox__backdrop" data-close-lightbox tabindex="-1"></div>
      <div class="giv-lightbox__panel" role="dialog" aria-modal="true" aria-label="Image preview">
        <button type="button" class="giv-lightbox__close" data-close-lightbox aria-label="Close">&times;</button>
        <button type="button" class="giv-lightbox__nav giv-lightbox__nav--prev" data-lightbox-prev aria-label="Previous image">&lsaquo;</button>
        <button type="button" class="giv-lightbox__nav giv-lightbox__nav--next" data-lightbox-next aria-label="Next image">&rsaquo;</button>
        <figure class="giv-lightbox__figure">
          <img class="giv-lightbox__img" src="" alt="">
          <figcaption class="giv-lightbox__caption"></figcaption>
          <p class="giv-lightbox__counter" aria-live="polite"></p>
        </figure>
      </div>
    `;
    document.body.appendChild(dialog);

    dialog.querySelectorAll("[data-close-lightbox]").forEach((el) => {
      el.addEventListener("click", close);
    });

    dialog.querySelector("[data-lightbox-prev]").addEventListener("click", (e) => {
      e.stopPropagation();
      step(-1);
    });

    dialog.querySelector("[data-lightbox-next]").addEventListener("click", (e) => {
      e.stopPropagation();
      step(1);
    });

    const panel = dialog.querySelector(".giv-lightbox__panel");
    panel.addEventListener(
      "touchstart",
      (e) => {
        touchStartX = e.changedTouches[0].screenX;
      },
      { passive: true }
    );

    panel.addEventListener(
      "touchend",
      (e) => {
        if (!dialog || dialog.hidden || galleryItems.length < 2) return;
        const dx = e.changedTouches[0].screenX - touchStartX;
        if (Math.abs(dx) < 48) return;
        step(dx < 0 ? 1 : -1);
      },
      { passive: true }
    );

    document.addEventListener("keydown", (e) => {
      if (!dialog || dialog.hidden) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
    });

    return dialog;
  }

  function updateNav() {
    if (!dialog) return;
    const multi = galleryItems.length > 1;
    const prev = dialog.querySelector("[data-lightbox-prev]");
    const next = dialog.querySelector("[data-lightbox-next]");
    const counter = dialog.querySelector(".giv-lightbox__counter");
    prev.hidden = !multi;
    next.hidden = !multi;
    counter.hidden = !multi;
    if (multi) {
      counter.textContent = `${galleryIndex + 1} / ${galleryItems.length}`;
    } else {
      counter.textContent = "";
    }
  }

  function showAt(index) {
    if (!galleryItems.length) return;
    galleryIndex = ((index % galleryItems.length) + galleryItems.length) % galleryItems.length;
    const item = galleryItems[galleryIndex];
    const lb = ensureDialog();
    const img = lb.querySelector(".giv-lightbox__img");
    const cap = lb.querySelector(".giv-lightbox__caption");
    img.src = item.src;
    img.alt = item.alt || "";
    cap.textContent = item.caption || item.alt || "";
    updateNav();
  }

  function step(delta) {
    if (galleryItems.length < 2) return;
    showAt(galleryIndex + delta);
  }

  function open(src, alt, caption) {
    galleryItems = [{ src, alt, caption }];
    galleryIndex = 0;
    const lb = ensureDialog();
    lastFocus = document.activeElement;
    showAt(0);
    lb.hidden = false;
    document.body.classList.add("lightbox-open");
    lb.querySelector(".giv-lightbox__close").focus();
  }

  function openGallery(items, index) {
    if (!items || !items.length) return;
    galleryItems = items;
    galleryIndex = typeof index === "number" ? index : 0;
    const lb = ensureDialog();
    lastFocus = document.activeElement;
    showAt(galleryIndex);
    lb.hidden = false;
    document.body.classList.add("lightbox-open");
    lb.querySelector(".giv-lightbox__close").focus();
  }

  function close() {
    if (!dialog || dialog.hidden) return;
    dialog.hidden = true;
    document.body.classList.remove("lightbox-open");
    const img = dialog.querySelector(".giv-lightbox__img");
    img.removeAttribute("src");
    galleryItems = [];
    galleryIndex = -1;
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  function bindLightbox(root, selector) {
    const scope = root || document;
    scope.querySelectorAll(selector || "[data-lightbox]").forEach((el) => {
      if (el.dataset.lightboxBound) return;
      el.dataset.lightboxBound = "1";
      el.addEventListener("click", () => {
        const src = el.dataset.lightboxSrc || el.getAttribute("href") || el.src;
        const alt = el.dataset.lightboxAlt || el.alt || "";
        const caption = el.dataset.lightboxCaption || "";
        if (src) open(src, alt, caption);
      });
    });
  }

  function bindGalleryGrid(grid, items) {
    if (!grid || !items || !items.length) return;
    grid.querySelectorAll("[data-lightbox]").forEach((el) => {
      if (el.dataset.lightboxBound) return;
      el.dataset.lightboxBound = "1";
      el.addEventListener("click", () => {
        const index = Number.parseInt(el.dataset.lightboxIndex, 10);
        openGallery(items, Number.isFinite(index) ? index : 0);
      });
    });
  }

  global.GivLightbox = { open, close, bindLightbox, openGallery, bindGalleryGrid };
})(window);
