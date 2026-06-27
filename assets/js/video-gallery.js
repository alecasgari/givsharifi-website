/**
 * Video gallery — /videos/
 */
(function () {
  const grid = document.getElementById('vid-grid');
  const searchInput = document.getElementById('vid-search');
  const countEl = document.getElementById('vid-count');
  const updatedEl = document.getElementById('vid-updated');

  if (!grid) return;

  function u(path) {
    return typeof window.siteUrl === 'function' ? window.siteUrl(path) : path;
  }

  function assetUrl(config, file) {
    const prefix = (config.pathPrefix || '').replace(/^\/|\/$/g, '');
    const name = String(file).replace(/^\//, '');
    if (!name) return '';
    if (config.baseUrl) {
      const base = config.baseUrl.replace(/\/$/, '');
      return prefix ? base + '/' + prefix + '/' + name : base + '/' + name;
    }
    return prefix ? prefix + '/' + name : name;
  }

  const videoUrl = assetUrl;

  let allVideos = [];
  let config = {};
  let debounceTimer;

  function showSkeleton() {
    if (window.GivSkeleton) {
      grid.innerHTML = window.GivSkeleton.videoPage(3);
    }
  }

  async function init() {
    showSkeleton();
    try {
      const res = await fetch(u('assets/data/video-library.json'));
      if (!res.ok) throw new Error('Failed to load');
      config = await res.json();
      allVideos = config.videos || [];
      if (updatedEl && config.updated) {
        updatedEl.textContent = `Last updated ${config.updated}`;
      }
      render();
      bindEvents();
    } catch (e) {
      grid.innerHTML = '<p class="vid-loading">Unable to load videos. Please try again later.</p>';
      console.error(e);
    }
  }

  function bindEvents() {
    if (!searchInput) return;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(render, 200);
    });
  }

  function getFiltered() {
    const q = (searchInput?.value || '').trim().toLowerCase();
    if (!q) return allVideos;
    return allVideos.filter((v) => {
      const hay = [v.title, v.description, v.category, v.date].join(' ').toLowerCase();
      return hay.includes(q);
    });
  }

  function render() {
    const list = getFiltered();
    if (countEl) {
      countEl.textContent =
        list.length === allVideos.length
          ? `${list.length} videos`
          : `${list.length} of ${allVideos.length}`;
    }

    if (!list.length) {
      grid.innerHTML = '<p class="vid-empty">No videos match your search.</p>';
      return;
    }

    grid.innerHTML = list
      .map(
        (v) => `
      <article class="vid-card">
        <video controls preload="none" playsinline${
          v.poster ? ` poster="${escapeAttr(assetUrl(config, v.poster))}"` : ''
        }>
          <source src="${escapeAttr(videoUrl(config, v.file))}" type="video/mp4">
        </video>
        <div class="vid-card__body">
          <p class="vid-card__meta">
            <span class="vid-card__cat">${escapeHtml(v.category || 'Video')}</span>
            ${v.date ? `<time datetime="${escapeAttr(v.date)}">${escapeHtml(formatDate(v.date))}</time>` : ''}
            ${v.duration ? `<span>${escapeHtml(v.duration)}</span>` : ''}
          </p>
          <h2 class="vid-card__title">${escapeHtml(v.title)}</h2>
          ${v.description ? `<p class="vid-card__desc">${escapeHtml(v.description)}</p>` : ''}
          <div class="vid-card__links">
            ${
              v.instagram
                ? `<a class="vid-card__ig" href="${escapeAttr(v.instagram)}" target="_blank" rel="noopener noreferrer">View on Instagram ↗</a>`
                : ''
            }
          </div>
        </div>
      </article>
    `
      )
      .join('');

    if (window.GivVideoPlayback) {
      window.GivVideoPlayback.bindSingleVideoPlayback(grid);
    }
    if (window.GivVideoPoster) {
      window.GivVideoPoster.bindVideoPosterFallback(grid);
    }
  }

  function formatDate(iso) {
    try {
      return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    } catch {
      return iso;
    }
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function escapeAttr(str) {
    return escapeHtml(str).replace(/'/g, '&#39;');
  }

  init();
})();
