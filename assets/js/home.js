(function () {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let revealObserver;

  function getRevealObserver() {
    if (revealObserver) return revealObserver;

    revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    return revealObserver;
  }

  function observeReveal(root) {
    const scope = root || document;
    const items = scope.querySelectorAll('[data-reveal]:not(.is-visible)');
    if (!items.length) return;

    if (prefersReduced) {
      items.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const observer = getRevealObserver();
    items.forEach((el) => observer.observe(el));
  }

  function animateCounter(el) {
    const target = Number(el.dataset.countTo);
    const prefix = el.dataset.prefix || '';
    const suffix = el.dataset.suffix || '';
    const duration = 1800;
    const start = performance.now();

    function frame(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = Math.round(target * eased);
      el.textContent = prefix + value.toLocaleString('en-US') + suffix;
      if (progress < 1) requestAnimationFrame(frame);
    }

    requestAnimationFrame(frame);
  }

  function initCounters() {
    const counters = document.querySelectorAll('[data-count-to]');
    if (!counters.length) return;

    if (prefersReduced) {
      counters.forEach((el) => {
        const target = Number(el.dataset.countTo);
        const prefix = el.dataset.prefix || '';
        const suffix = el.dataset.suffix || '';
        el.textContent = prefix + target.toLocaleString('en-US') + suffix;
      });
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting || entry.target.dataset.counted) return;
          entry.target.dataset.counted = '1';
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.4 }
    );

    counters.forEach((el) => observer.observe(el));
  }

  function init() {
    observeReveal(document);
    initCounters();
  }

  document.addEventListener('giv:home-videos-ready', () => {
    const grid = document.getElementById('home-video-grid');
    if (grid) observeReveal(grid);
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
