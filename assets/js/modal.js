(function () {
  let lastFocus = null;
  let scrollLockCount = 0;
  let savedScrollY = 0;

  function getModal() {
    return document.getElementById('consultation-modal');
  }

  function getSheet() {
    return document.getElementById('whatsapp-sheet');
  }

  function setScrollLock(on) {
    if (on) {
      if (scrollLockCount === 0) {
        savedScrollY = window.scrollY || document.documentElement.scrollTop;
        document.body.classList.add('giv-scroll-lock');
        document.body.style.position = 'fixed';
        document.body.style.top = `-${savedScrollY}px`;
        document.body.style.left = '0';
        document.body.style.right = '0';
        document.body.style.width = '100%';
        document.documentElement.style.overflow = 'hidden';
      }
      scrollLockCount += 1;
      return;
    }

    if (scrollLockCount === 0) return;
    scrollLockCount -= 1;
    if (scrollLockCount !== 0) return;

    document.body.classList.remove('giv-scroll-lock');
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.left = '';
    document.body.style.right = '';
    document.body.style.width = '';
    document.body.style.overflow = '';
    document.documentElement.style.overflow = '';
    window.scrollTo(0, savedScrollY);
  }

  window.givSetScrollLock = setScrollLock;

  function openConsultationModal() {
    const modal = getModal();
    if (!modal) return;
    lastFocus = document.activeElement;
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    setScrollLock(true);
    const closeBtn = modal.querySelector('[data-close-modal].giv-modal__close');
    if (closeBtn) closeBtn.focus();
  }

  function closeConsultationModal() {
    const modal = getModal();
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    setScrollLock(false);
    if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
  }

  function openWhatsAppSheet() {
    const sheet = getSheet();
    if (!sheet) return;
    lastFocus = document.activeElement;
    sheet.hidden = false;
    sheet.setAttribute('aria-hidden', 'false');
    setScrollLock(true);
    const closeBtn = sheet.querySelector('[data-close-sheet]');
    if (closeBtn) closeBtn.focus();
  }

  function closeWhatsAppSheet() {
    const sheet = getSheet();
    if (!sheet || sheet.hidden) return;
    sheet.hidden = true;
    sheet.setAttribute('aria-hidden', 'true');
    setScrollLock(false);
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

      if (e.target.closest('[data-close-modal]')) {
        closeConsultationModal();
      }
      if (e.target.closest('[data-close-sheet]')) {
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

  if (window.location.hash === '#consultation') {
    setTimeout(openConsultationModal, 300);
  }
})();
