(function () {
  let lastFocus = null;
  let savedScrollY = 0;
  const lockSources = new Set();
  let triggersBound = false;

  function getModal() {
    return document.getElementById('consultation-modal');
  }

  function getSheet() {
    return document.getElementById('whatsapp-sheet');
  }

  function applyScrollLock() {
    savedScrollY = window.scrollY || document.documentElement.scrollTop || 0;
    document.body.classList.add('giv-scroll-lock');
    document.body.style.position = 'fixed';
    document.body.style.top = `-${savedScrollY}px`;
    document.body.style.left = '0';
    document.body.style.right = '0';
    document.body.style.width = '100%';
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    document.documentElement.style.touchAction = 'none';
  }

  function releaseScrollLock() {
    const y = savedScrollY;
    document.body.classList.remove('giv-scroll-lock');
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.left = '';
    document.body.style.right = '';
    document.body.style.width = '';
    document.body.style.overflow = '';
    document.documentElement.style.overflow = '';
    document.documentElement.style.touchAction = '';

    requestAnimationFrame(() => {
      window.scrollTo(0, y);
      requestAnimationFrame(() => window.scrollTo(0, y));
    });
  }

  function setScrollLock(source, on) {
    if (on) {
      if (lockSources.size === 0) applyScrollLock();
      lockSources.add(source);
      return;
    }

    lockSources.delete(source);
    if (lockSources.size === 0) releaseScrollLock();
  }

  window.givSetScrollLock = setScrollLock;

  function restoreFocus() {
    if (!lastFocus || typeof lastFocus.focus !== 'function') return;
    try {
      lastFocus.focus({ preventScroll: true });
    } catch {
      lastFocus.focus();
    }
  }

  function openConsultationModal() {
    const modal = getModal();
    if (!modal || !modal.hidden) return;
    lastFocus = document.activeElement;
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    setScrollLock('consultation', true);
    const closeBtn = modal.querySelector('[data-close-modal].giv-modal__close');
    if (closeBtn) closeBtn.focus();
  }

  function closeConsultationModal() {
    const modal = getModal();
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    setScrollLock('consultation', false);
    restoreFocus();
  }

  function openWhatsAppSheet() {
    const sheet = getSheet();
    if (!sheet || !sheet.hidden) return;
    lastFocus = document.activeElement;
    sheet.hidden = false;
    sheet.setAttribute('aria-hidden', 'false');
    setScrollLock('whatsapp', true);
    const closeBtn = sheet.querySelector('[data-close-sheet]');
    if (closeBtn) closeBtn.focus();
  }

  function closeWhatsAppSheet() {
    const sheet = getSheet();
    if (!sheet || sheet.hidden) return;
    sheet.hidden = true;
    sheet.setAttribute('aria-hidden', 'true');
    setScrollLock('whatsapp', false);
    restoreFocus();
  }

  function isConsultationLink(el) {
    if (!el || !el.getAttribute) return false;
    const href = el.getAttribute('href') || '';
    return el.hasAttribute('data-open-consultation') ||
      href === '#consultation' ||
      href.endsWith('/#consultation');
  }

  function bindTriggers() {
    if (triggersBound) return;
    triggersBound = true;

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
        e.preventDefault();
        closeConsultationModal();
        return;
      }

      if (e.target.closest('[data-close-sheet]')) {
        e.preventDefault();
        closeWhatsAppSheet();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;
      closeConsultationModal();
      closeWhatsAppSheet();
    });

    document.addEventListener('click', (e) => {
      if (e.target.closest('[data-whatsapp-link]')) closeWhatsAppSheet();
    });
  }

  window.givOpenConsultation = openConsultationModal;
  window.givOpenWhatsApp = openWhatsAppSheet;

  bindTriggers();
  document.addEventListener('giv:layout-ready', bindTriggers);

  if (window.location.hash === '#consultation') {
    document.addEventListener('giv:layout-ready', () => {
      setTimeout(openConsultationModal, 300);
    }, { once: true });
  }
})();
