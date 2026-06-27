/**
 * Homepage video sources — loaded from assets/data/home-videos.json.
 * After R2 setup, set baseUrl (e.g. https://media.givsharifi.com) and pathPrefix (e.g. homepage).
 */
(function () {
  const grid = document.getElementById('home-video-grid');
  if (!grid) return;

  function videoUrl(config, file) {
    const prefix = (config.pathPrefix || '').replace(/^\/|\/$/g, '');
    const name = String(file).replace(/^\//, '');
    if (config.baseUrl) {
      const base = config.baseUrl.replace(/\/$/, '');
      return prefix ? base + '/' + prefix + '/' + name : base + '/' + name;
    }
    return prefix ? prefix + '/' + name : name;
  }

  function posterUrl(poster) {
    if (!poster) return '';
    if (/^https?:\/\//i.test(poster)) return poster;
    return typeof window.siteUrl === 'function' ? window.siteUrl(poster) : poster;
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function showSkeleton() {
    if (window.GivSkeleton) {
      grid.innerHTML = window.GivSkeleton.homeVideos(4);
    }
  }

  async function init() {
    showSkeleton();
    const configPath =
      typeof window.siteUrl === 'function'
        ? window.siteUrl('assets/data/home-videos.json')
        : 'assets/data/home-videos.json';

    let config;
    try {
      const res = await fetch(configPath);
      if (!res.ok) throw new Error('config missing');
      config = await res.json();
    } catch (e) {
      console.error('Home videos config:', e);
      grid.innerHTML = '<p class="hp-video-loading">Unable to load videos. Please refresh the page.</p>';
      return;
    }

    const videos = config.videos || [];
    grid.innerHTML = videos
      .map(
        (item) => `
      <article class="hp-vid" data-reveal>
        <video controls preload="none" poster="${escapeHtml(posterUrl(item.poster))}" playsinline>
          <source src="${escapeHtml(videoUrl(config, item.file))}" type="video/mp4">
        </video>
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.description)}</p>
      </article>
    `
      )
      .join('');

    if (window.GivVideoPlayback) {
      window.GivVideoPlayback.bindSingleVideoPlayback(grid);
    }

    document.dispatchEvent(new CustomEvent('giv:home-videos-ready'));
  }

  init();
})();
