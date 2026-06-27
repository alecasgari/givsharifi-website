(function () {
  let lastFocus = null;

  function getModal() {
    return document.getElementById('consultation-modal');
  }

  function getSheet() {
    return document.getElementById('whatsapp-sheet');
  }

  function lockScroll(on) {
    document.body.classList.toggle('giv-scroll-lock', on);
  }

  function openConsultationModal() {
    const modal = getModal();
    if (!modal) return;
    lastFocus = document.activeElement;
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    lockScroll(true);
    const closeBtn = modal.querySelector('[data-close-modal].giv-modal__close');
    if (closeBtn) closeBtn.focus();
  }

  function closeConsultationModal() {
    const modal = getModal();
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    if (!getSheet() || getSheet().hidden) lockScroll(false);
    if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
  }

  function openWhatsAppSheet() {
    const sheet = getSheet();
    if (!sheet) return;
    lastFocus = document.activeElement;
    sheet.hidden = false;
    sheet.setAttribute('aria-hidden', 'false');
    lockScroll(true);
    const closeBtn = sheet.querySelector('[data-close-sheet]');
    if (closeBtn) closeBtn.focus();
  }

  function closeWhatsAppSheet() {
    const sheet = getSheet();
    if (!sheet || sheet.hidden) return;
    sheet.hidden = true;
    sheet.setAttribute('aria-hidden', 'true');
    if (!getModal() || getModal().hidden) lockScroll(false);
    if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
  }

  function isConsultationLink(el) {
    if (!el || !el.getAttribute) return false;
    const href = el.getAttribute('href') || '';
    return el.hasAttribute('data-open-consultation') ||
      href === '#consultation' ||
      href.endsWith('/#consultation');
  }

  function bindTriggers() {
    document.addEventListener('click', (e) => {
      const consultBtn = e.target.closest('[data-open-consultation]');
      if (consultBtn) {
        e.preventDefault();
        openConsultationModal();
        return;
      }

      const waBtn = e.target.closest('[data-open-whatsapp]');
      if (waBtn) {
        e.preventDefault();
        openWhatsAppSheet();
        return;
      }

      const link = e.target.closest('a');
      if (link && isConsultationLink(link)) {
        e.preventDefault();
        openConsultationModal();
        return;
      }

      if (e.target.matches('[data-close-modal]')) {
        closeConsultationModal();
      }
      if (e.target.matches('[data-close-sheet]')) {
        closeWhatsAppSheet();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;
      closeConsultationModal();
      closeWhatsAppSheet();
    });

    document.querySelectorAll('[data-whatsapp-link]').forEach((link) => {
      link.addEventListener('click', () => closeWhatsAppSheet());
    });
  }

  window.givOpenConsultation = openConsultationModal;
  window.givOpenWhatsApp = openWhatsAppSheet;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindTriggers);
  } else {
    bindTriggers();
  }

  document.addEventListener('giv:layout-ready', bindTriggers);

  if (document.readyState !== 'loading') {
    bindTriggers();
  }

  if (window.location.hash === '#consultation') {
    setTimeout(openConsultationModal, 300);
  }
})();
