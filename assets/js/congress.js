/**
 * Congress listing — search, year/city filters, card grid.
 */
(function () {
  const grid = document.getElementById('cong-grid');
  const searchInput = document.getElementById('cong-search');
  const yearSelect = document.getElementById('cong-year');
  const citySelect = document.getElementById('cong-city');
  const countEl = document.getElementById('cong-count');
  const updatedEl = document.getElementById('cong-updated');

  if (!grid) return;

  function u(path) {
    return typeof window.siteUrl === 'function' ? window.siteUrl(path) : path;
  }

  let allEvents = [];
  let debounceTimer;

  function showSkeleton() {
    if (window.GivSkeleton && window.GivSkeleton.congress) {
      grid.innerHTML = window.GivSkeleton.congress(6);
    }
  }

  async function init() {
    showSkeleton();
    try {
      const res = await fetch(u('congress/data/index.json'));
      if (!res.ok) throw new Error('Failed to load');
      const data = await res.json();
      allEvents = (data.events || []).slice().sort((a, b) => (b.date || '').localeCompare(a.date || ''));
      if (updatedEl && data.updated) {
        updatedEl.textContent = `Last updated ${formatDate(data.updated)}`;
      }
      populateFilters(allEvents);
      render();
      bindEvents();
      injectSchema(data);
    } catch (e) {
      grid.innerHTML = '<p class="cong-loading">Unable to load congress events. Please refresh the page or try again later.</p>';
      console.error(e);
    }
  }

  function populateFilters(events) {
    const years = [...new Set(events.map((e) => e.year).filter(Boolean))].sort((a, b) => b - a);
    const cities = [...new Set(events.map((e) => e.city).filter(Boolean))].sort();

    if (yearSelect) {
      yearSelect.innerHTML =
        '<option value="">All years</option>' + years.map((y) => `<option value="${y}">${y}</option>`).join('');
    }
    if (citySelect) {
      citySelect.innerHTML =
        '<option value="">All cities</option>' +
        cities.map((c) => `<option value="${escapeAttr(c)}">${escapeHtml(c)}</option>`).join('');
    }
  }

  function bindEvents() {
    [yearSelect, citySelect].forEach((el) => {
      if (el) el.addEventListener('change', render);
    });
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(render, 180);
      });
    }
  }

  function getFiltered() {
    const q = (searchInput?.value || '').trim().toLowerCase();
    const year = yearSelect?.value || '';
    const city = citySelect?.value || '';

    return allEvents.filter((e) => {
      if (year && String(e.year) !== year) return false;
      if (city && e.city !== city) return false;
      if (!q) return true;
      const hay = [e.title, e.subtitle, e.city, e.country, e.venue, e.type, e.excerpt, ...(e.keywords || [])]
        .join(' ')
        .toLowerCase();
      return hay.includes(q);
    });
  }

  function render() {
    const list = getFiltered();
    if (countEl) {
      countEl.textContent =
        list.length === allEvents.length
          ? `${list.length} event${list.length !== 1 ? 's' : ''}`
          : `Showing ${list.length} of ${allEvents.length}`;
    }

    if (!list.length) {
      grid.innerHTML = '<p class="cong-empty">No events match your search. Try a different keyword, year, or city.</p>';
      return;
    }

    grid.innerHTML = list
      .map(
        (e) => `
      <a class="cong-card" href="${u('congress/' + e.slug + '/')}">
        <div class="cong-card__media">
          <img src="${escapeAttr(u(e.coverImage))}" alt="${escapeAttr(e.title)}" loading="lazy" width="640" height="400">
        </div>
        <div class="cong-card__body">
          <div class="cong-card__meta">
            ${e.type ? `<span class="cong-card__type">${escapeHtml(e.type)}</span>` : ''}
            ${e.date ? `<span>${escapeHtml(formatDate(e.date))}</span>` : ''}
            ${e.city ? `<span>${escapeHtml(e.city)}${e.country ? ', ' + escapeHtml(e.country) : ''}</span>` : ''}
          </div>
          <h2 class="cong-card__title">${escapeHtml(e.title)}</h2>
          ${e.excerpt ? `<p class="cong-card__excerpt">${escapeHtml(e.excerpt)}</p>` : ''}
          <span class="cong-card__footer">View event details →</span>
        </div>
      </a>
    `
      )
      .join('');
  }

  function injectSchema(data) {
    const items = (data.events || []).map((e, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      item: {
        '@type': 'Event',
        name: e.title,
        startDate: e.date,
        location: e.city
          ? {
              '@type': 'Place',
              name: e.venue || e.city,
              address: {
                '@type': 'PostalAddress',
                addressLocality: e.city,
                addressCountry: e.country,
              },
            }
          : undefined,
        url: 'https://www.givsharifi.com/congress/' + e.slug + '/',
        image: e.coverImage ? 'https://www.givsharifi.com/' + e.coverImage.replace(/^\//, '') : undefined,
      },
    }));

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Prof. Giv Sharifi — Congress & Symposia',
      numberOfItems: data.events?.length,
      itemListElement: items,
    });
    document.head.appendChild(script);
  }

  function formatDate(iso) {
    return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
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
