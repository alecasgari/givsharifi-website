/**
 * Accessible image lightbox — open/close with keyboard support.
 */
(function (global) {
  let dialog = null;
  let lastFocus = null;

  function ensureDialog() {
    if (dialog) return dialog;
    dialog = document.createElement("div");
    dialog.className = "giv-lightbox";
    dialog.hidden = true;
    dialog.innerHTML = `
      <div class="giv-lightbox__backdrop" data-close-lightbox tabindex="-1"></div>
      <div class="giv-lightbox__panel" role="dialog" aria-modal="true" aria-label="Image preview">
        <button type="button" class="giv-lightbox__close" data-close-lightbox aria-label="Close">&times;</button>
        <figure class="giv-lightbox__figure">
          <img class="giv-lightbox__img" src="" alt="">
          <figcaption class="giv-lightbox__caption"></figcaption>
        </figure>
      </div>
    `;
    document.body.appendChild(dialog);

    dialog.querySelectorAll("[data-close-lightbox]").forEach((el) => {
      el.addEventListener("click", close);
    });

    document.addEventListener("keydown", (e) => {
      if (!dialog || dialog.hidden) return;
      if (e.key === "Escape") close();
    });

    return dialog;
  }

  function open(src, alt, caption) {
    const lb = ensureDialog();
    lastFocus = document.activeElement;
    const img = lb.querySelector(".giv-lightbox__img");
    const cap = lb.querySelector(".giv-lightbox__caption");
    img.src = src;
    img.alt = alt || "";
    cap.textContent = caption || alt || "";
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

  global.GivLightbox = { open, close, bindLightbox };
})(window);
