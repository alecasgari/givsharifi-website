/**
 * Publications list — search, filter, card grid (client-side).
 */
(function () {
  const grid = document.getElementById('pub-grid');
  const searchInput = document.getElementById('pub-search');
  const yearSelect = document.getElementById('pub-year');
  const topicSelect = document.getElementById('pub-topic');
  const sortSelect = document.getElementById('pub-sort');
  const countEl = document.getElementById('pub-count');
  const statsEl = document.getElementById('pub-stats');

  if (!grid) return;

  function u(path) {
    return typeof window.siteUrl === 'function' ? window.siteUrl(path) : path;
  }

  let allPubs = [];
  let debounceTimer;

  function showSkeleton() {
    if (window.GivSkeleton) {
      grid.innerHTML = window.GivSkeleton.publications(6);
    }
  }

  async function init() {
    showSkeleton();
    try {
      const res = await fetch(u('publications/data/index.json'));
      if (!res.ok) throw new Error('Failed to load');
      const data = await res.json();
      allPubs = data.publications || [];
      renderStats(data.stats || {}, data.updated);
      populateFilters(allPubs);
      render();
      bindEvents();
      injectSchema(data);
    } catch (e) {
      grid.innerHTML = '<p class="pub-loading">Unable to load publications. Please try again later.</p>';
      console.error(e);
    }
  }

  function renderStats(stats, updated) {
    if (!statsEl) return;
    const parts = [];
    if (stats.total != null) parts.push(`<strong>${stats.total}</strong> publications`);
    if (stats.citations != null) parts.push(`<strong>${stats.citations.toLocaleString()}</strong> citations`);
    if (stats.hIndex != null) parts.push(`h-index <strong>${stats.hIndex}</strong>`);
    if (stats.i10Index != null) parts.push(`i10-index <strong>${stats.i10Index}</strong>`);
    statsEl.innerHTML = parts.join(' · ');
    if (updated) {
      const note = document.getElementById('pub-updated');
      if (note) note.textContent = `Last updated ${formatDate(updated)}`;
    }
    const scholar = document.getElementById('pub-scholar-link');
    if (scholar && stats.scholarUrl) scholar.href = stats.scholarUrl;
  }

  function populateFilters(pubs) {
    const years = [...new Set(pubs.map((p) => p.year).filter(Boolean))].sort((a, b) => b - a);
    const topics = [...new Set(pubs.map((p) => p.topic).filter(Boolean))].sort();

    if (yearSelect) {
      yearSelect.innerHTML =
        '<option value="">All years</option>' + years.map((y) => `<option value="${y}">${y}</option>`).join('');
    }
    if (topicSelect) {
      topicSelect.innerHTML =
        '<option value="">All topics</option>' + topics.map((t) => `<option value="${escapeAttr(t)}">${escapeHtml(t)}</option>`).join('');
    }
  }

  function bindEvents() {
    [yearSelect, topicSelect, sortSelect].forEach((el) => {
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
    const topic = topicSelect?.value || '';
    const sort = sortSelect?.value || 'year';

    let list = allPubs.filter((p) => {
      if (year && String(p.year) !== year) return false;
      if (topic && p.topic !== topic) return false;
      if (!q) return true;
      const hay = `${p.title} ${p.authors} ${p.journal} ${p.topic}`.toLowerCase();
      return hay.includes(q);
    });

    if (sort === 'citations') {
      list = [...list].sort((a, b) => (b.citations || 0) - (a.citations || 0));
    } else {
      list = [...list].sort((a, b) => (b.year || 0) - (a.year || 0) || (b.citations || 0) - (a.citations || 0));
    }
    return list;
  }

  function render() {
    const list = getFiltered();
    if (countEl) {
      countEl.textContent =
        list.length === allPubs.length
          ? `${list.length} articles`
          : `Showing ${list.length} of ${allPubs.length}`;
    }

    if (!list.length) {
      grid.innerHTML = '<p class="pub-empty">No publications match your search.</p>';
      return;
    }

    grid.innerHTML = list
      .map(
        (p) => `
      <a class="pub-card" href="${escapeAttr(p.url)}" target="_blank" rel="noopener noreferrer">
        <div class="pub-card__top">
          ${p.topic ? `<span class="pub-card__topic">${escapeHtml(p.topic)}</span>` : ''}
          ${p.year ? `<span class="pub-card__year">${p.year}</span>` : ''}
        </div>
        <h3 class="pub-card__title">${escapeHtml(p.title)}</h3>
        ${p.authors ? `<p class="pub-card__authors">${escapeHtml(truncate(p.authors, 120))}</p>` : ''}
        ${p.journal ? `<p class="pub-card__journal">${escapeHtml(truncate(p.journal, 100))}</p>` : ''}
        <p class="pub-card__footer">
          <span class="pub-card__cites">${formatCitations(p.citations)}</span>
          <span class="pub-card__arrow" aria-hidden="true">↗</span>
        </p>
      </a>
    `
      )
      .join('');
  }

  function injectSchema(data) {
    const items = (data.publications || []).slice(0, 50).map((p, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      item: {
        '@type': 'ScholarlyArticle',
        name: p.title,
        author: p.authors,
        datePublished: p.year ? String(p.year) : undefined,
        url: p.url,
        isPartOf: p.journal ? { '@type': 'PublicationIssue', name: p.journal } : undefined,
      },
    }));

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Prof. Giv Sharifi — Publications',
      numberOfItems: data.stats?.total || data.publications?.length,
      itemListElement: items,
    });
    document.head.appendChild(script);
  }

  function formatCitations(n) {
    const count = Number(n) || 0;
    return `Total citations: <strong>${count.toLocaleString()}</strong>`;
  }

  function formatDate(iso) {
    return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  }

  function truncate(str, max) {
    if (!str || str.length <= max) return str;
    return str.slice(0, max - 1) + '…';
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
