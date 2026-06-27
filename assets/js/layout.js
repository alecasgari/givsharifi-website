const SITE = {
  components: {
    header: 'components/header.html',
    footer: 'components/footer.html',
    modal: 'components/consultation-modal.html'
  }
};

function sitePath(path) {
  return typeof window.siteUrl === 'function' ? window.siteUrl(path) : path;
}

async function loadHTML(url) {
  const res = await fetch(sitePath(url));
  if (!res.ok) throw new Error('Failed to load ' + url);
  return res.text();
}

function currentSitePath() {
  let path = window.location.pathname.replace(/\/$/, '') || '/';
  const root = (window.__SITE_ROOT__ || '/').replace(/\/$/, '');
  if (root && root !== '/' && path.startsWith(root)) {
    path = path.slice(root.length) || '/';
  }
  if (!path.startsWith('/')) path = '/' + path;
  return path;
}

function setActiveNav() {
  const path = currentSitePath();
  document.querySelectorAll('.site-nav a, .mobile-nav a').forEach((link) => {
    const raw = link.getAttribute('href');
    if (!raw || /^https?:/i.test(raw) || raw.startsWith('tel:')) return;
    let href = raw.replace(/^\.\//, '').replace(/\/$/, '') || '/';
    if (!href.startsWith('/')) href = '/' + href;
    if (href === path || (href !== '/' && path.startsWith(href))) {
      link.classList.add('is-active');
    }
  });
}

function setNavScrollLock(locked) {
  if (typeof window.givSetScrollLock === 'function') {
    window.givSetScrollLock('nav', locked);
  } else {
    document.body.style.overflow = locked ? 'hidden' : '';
  }
}

function closeMobileNav() {
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('mobile-nav');
  if (!toggle || !nav) return;
  toggle.classList.remove('is-open');
  nav.classList.remove('is-open');
  nav.hidden = true;
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-label', 'Open menu');
  document.body.classList.remove('nav-open');
  setNavScrollLock(false);
}

function initMobileNav() {
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('mobile-nav');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => {
    const open = !toggle.classList.contains('is-open');
    toggle.classList.toggle('is-open', open);
    nav.classList.toggle('is-open', open);
    nav.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('nav-open', open);
    setNavScrollLock(open);
  });

  nav.querySelector('[data-close-nav]')?.addEventListener('click', closeMobileNav);

  nav.querySelectorAll('a').forEach((a) => {
    a.addEventListener('click', closeMobileNav);
  });

  nav.querySelectorAll('button').forEach((btn) => {
    if (btn.hasAttribute('data-open-consultation') || btn.hasAttribute('data-open-whatsapp')) {
      btn.addEventListener('click', closeMobileNav);
    }
  });
}

function initHeaderScroll() {
  const header = document.getElementById('site-header');
  if (!header) return;
  const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

async function loadScript(src) {
  const resolved = sitePath(src);
  if (document.querySelector(`script[src="${resolved}"]`)) return;
  await new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = resolved;
    s.onload = resolve;
    s.onerror = reject;
    document.body.appendChild(s);
  });
}

async function loadConsultationForm() {
  const formSlot = document.getElementById('consultation-form-slot');
  if (!formSlot || formSlot.dataset.loaded) return;
  try {
    formSlot.innerHTML = await loadHTML('components/consultation-form.html');
    formSlot.dataset.loaded = '1';
    document.dispatchEvent(new CustomEvent('giv:forms-ready'));
  } catch (e) {
    console.error('Form load error:', e);
  }
}

async function initLayout() {
  const headerEl = document.getElementById('site-header');
  const footerEl = document.getElementById('site-footer');

  try {
    if (headerEl) {
      headerEl.outerHTML = await loadHTML(SITE.components.header);
    }
    if (footerEl) {
      footerEl.outerHTML = await loadHTML(SITE.components.footer);
    }

    const modalWrap = document.createElement('div');
    modalWrap.id = 'giv-overlays';
    modalWrap.innerHTML = await loadHTML(SITE.components.modal);
    document.body.appendChild(modalWrap);
    document.body.classList.add('has-mobile-bar');
  } catch (e) {
    console.error('Layout load error:', e);
  }

  const year = document.getElementById('footer-year');
  if (year) year.textContent = new Date().getFullYear();

  await loadConsultationForm();
  await loadScript('assets/js/modal.js');

  document.dispatchEvent(new CustomEvent('giv:layout-ready'));

  setActiveNav();
  initMobileNav();
  initHeaderScroll();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initLayout);
} else {
  initLayout();
}
