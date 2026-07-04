/**
 * Congress event detail page — loads data.json from congress/{slug}/.
 */
(function () {
  const root = document.getElementById('congress-event-root');
  if (!root) return;

  const SITE = 'https://www.givsharifi.com';

  function u(path) {
    return typeof window.siteUrl === 'function' ? window.siteUrl(path) : path;
  }

  function sitePathname() {
    let path = window.location.pathname.replace(/\/$/, '') || '/';
    const siteRoot = (window.__SITE_ROOT__ || '/').replace(/\/$/, '');
    if (siteRoot && siteRoot !== '/' && path.startsWith(siteRoot)) {
      path = path.slice(siteRoot.length) || '/';
    }
    return path;
  }

  const parts = sitePathname().replace(/^\//, '').split('/').filter(Boolean);
  const slug = parts[parts.length - 1] || parts[parts.length - 2];

  if (!slug || slug === 'congress') return;

  async function loadEvent() {
    try {
      const res = await fetch(u('congress/' + slug + '/data.json'));
      if (!res.ok) throw new Error('Not found');
      const event = await res.json();
      const pageUrl = SITE + '/congress/' + slug + '/';
      const imageUrl = event.coverImage ? SITE + '/' + event.coverImage.replace(/^\//, '') : SITE + '/assets/images/home/og-share.webp';

      applyHead(event, pageUrl, imageUrl);
      root.innerHTML = renderEvent(event, pageUrl);
      initGalleryLightbox(event);
    } catch (e) {
      root.innerHTML =
        '<div class="container cong-event__error"><h1>Event not found</h1><p><a href="' +
        u('congress/') +
        '">← Back to Congress</a></p></div>';
    }
  }

  function applyHead(event, pageUrl, imageUrl) {
    document.title = event.title + ' | Prof. Giv Sharifi';

    setMeta('name', 'description', event.metaDescription || event.summary || '');
    if (event.keywords) setMeta('name', 'keywords', event.keywords);
    setLink('canonical', pageUrl);

    setMeta('property', 'og:title', event.title);
    setMeta('property', 'og:description', event.metaDescription || event.summary || '');
    setMeta('property', 'og:url', pageUrl);
    setMeta('property', 'og:image', imageUrl);
    setMeta('property', 'og:type', 'article');

    setMeta('name', 'twitter:title', event.title);
    setMeta('name', 'twitter:description', event.metaDescription || event.summary || '');
    setMeta('name', 'twitter:image', imageUrl);

    injectJsonLd(event, pageUrl, imageUrl);
  }

  function setMeta(attr, key, value) {
    if (!value) return;
    let el = document.querySelector('meta[' + attr + '="' + key + '"]');
    if (!el) {
      el = document.createElement('meta');
      el.setAttribute(attr, key);
      document.head.appendChild(el);
    }
    el.content = value;
  }

  function setLink(rel, href) {
    let el = document.querySelector('link[rel="' + rel + '"]');
    if (!el) {
      el = document.createElement('link');
      el.rel = rel;
      document.head.appendChild(el);
    }
    el.href = href;
  }

  function injectJsonLd(event, pageUrl, imageUrl) {
    const schema = {
      '@context': 'https://schema.org',
      '@type': 'Event',
      name: event.title,
      description: event.metaDescription || event.summary,
      startDate: event.date,
      eventAttendanceMode: 'https://schema.org/OfflineEventAttendanceMode',
      eventStatus: 'https://schema.org/EventScheduled',
      image: imageUrl,
      url: pageUrl,
      location: {
        '@type': 'Place',
        name: event.venue || event.city,
        address: {
          '@type': 'PostalAddress',
          addressLocality: event.city,
          addressCountry: event.country,
        },
      },
      organizer: (event.organizers || []).map((name) => ({
        '@type': 'Organization',
        name: name,
      })),
      performer: {
        '@type': 'Physician',
        name: 'Prof. Giv Sharifi',
        medicalSpecialty: 'Neurosurgery',
        url: SITE + '/',
      },
    };

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(schema);
    document.head.appendChild(script);

    const breadcrumb = {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: SITE + '/' },
        { '@type': 'ListItem', position: 2, name: 'Congress', item: SITE + '/congress/' },
        { '@type': 'ListItem', position: 3, name: event.title, item: pageUrl },
      ],
    };
    const bcScript = document.createElement('script');
    bcScript.type = 'application/ld+json';
    bcScript.textContent = JSON.stringify(breadcrumb);
    document.head.appendChild(bcScript);
  }

  function renderEvent(event, pageUrl) {
    const facts = [];
    if (event.dateDisplay || event.date) {
      facts.push('<li><strong>Date:</strong> ' + escapeHtml(event.dateDisplay || formatDate(event.date)) + '</li>');
    }
    if (event.city) {
      facts.push(
        '<li><strong>Location:</strong> ' +
          escapeHtml(event.city) +
          (event.country ? ', ' + escapeHtml(event.country) : '') +
          '</li>'
      );
    }
    if (event.venue) {
      facts.push('<li><strong>Venue:</strong> ' + escapeHtml(event.venue) + '</li>');
    }
    if (event.type) {
      facts.push('<li><strong>Type:</strong> ' + escapeHtml(event.type) + '</li>');
    }

    const sections = (event.sections || [])
      .map(
        (s) => `
      <section class="cong-event-section">
        <h2>${escapeHtml(s.heading)}</h2>
        ${(s.paragraphs || []).map((p) => '<p>' + escapeHtml(p) + '</p>').join('')}
      </section>
    `
      )
      .join('');

    const organizers =
      event.organizers && event.organizers.length
        ? `
      <div class="cong-event-organizers">
        <h3>Organizers</h3>
        <ul>${event.organizers.map((o) => '<li>' + escapeHtml(o) + '</li>').join('')}</ul>
      </div>
    `
        : '';

    const gallery =
      event.gallery && event.gallery.length
        ? `
      <section class="cong-event-gallery" aria-label="Event photo gallery">
        <div class="container">
          <h2>Photo Gallery</h2>
          <div class="cong-event-gallery__grid" id="cong-event-gallery">
            ${event.gallery
              .map(
                (img, i) => `
              <button type="button" class="cong-event-gallery__item" data-lightbox data-lightbox-index="${i}"
                aria-label="${escapeAttr(img.alt || img.caption || 'Event photo')}">
                <img src="${escapeAttr(u(img.file))}" alt="${escapeAttr(img.alt || '')}" loading="lazy" width="480" height="360">
              </button>
            `
              )
              .join('')}
          </div>
        </div>
      </section>
    `
        : '';

    return `
      <section class="cong-event-hero">
        <div class="container">
          <nav class="blog-breadcrumb" aria-label="Breadcrumb">
            <ol>
              <li><a href="${u('./')}">Home</a></li>
              <li><a href="${u('congress/')}">Congress</a></li>
              <li aria-current="page">${escapeHtml(truncate(event.title, 48))}</li>
            </ol>
          </nav>
          ${event.type ? '<p class="cong-event-hero__type">' + escapeHtml(event.type) + '</p>' : ''}
          <h1>${escapeHtml(event.title)}</h1>
          ${event.subtitle ? '<p class="cong-event-hero__subtitle">' + escapeHtml(event.subtitle) + '</p>' : ''}
          <ul class="cong-event-hero__facts">${facts.join('')}</ul>
        </div>
      </section>

      ${
        event.coverImage
          ? '<section class="cong-event-cover"><div class="container"><img src="' +
            escapeAttr(u(event.coverImage)) +
            '" alt="' +
            escapeAttr(event.title) +
            '" width="1200" height="675"></div></section>'
          : ''
      }

      <section class="cong-event-content">
        <div class="container">
          ${event.summary ? '<p class="cong-event-summary">' + escapeHtml(event.summary) + '</p>' : ''}
          ${sections}
          ${organizers}
        </div>
      </section>

      ${gallery}

      <section class="pg-cta" aria-label="Consultation">
        <div class="container pg-cta__inner">
          <h2>Book a consultation</h2>
          <p>Discuss your neurological condition with Prof. Giv Sharifi — Dubai, Tehran, or online.</p>
          <div class="pg-cta__actions">
            <button type="button" class="btn btn--primary btn--lg" data-open-consultation>Free Consultation</button>
            <a href="${u('congress/')}" class="btn btn--secondary btn--lg">All Congress Events</a>
          </div>
        </div>
      </section>
    `;
  }

  function initGalleryLightbox(event) {
    if (!event.gallery || !event.gallery.length || !window.GivLightbox) return;
    const items = event.gallery.map((img) => ({
      src: u(img.file),
      alt: img.alt || '',
      caption: img.caption || img.alt || '',
    }));
    const gallery = document.getElementById('cong-event-gallery');
    if (gallery) window.GivLightbox.bindGalleryGrid(gallery, items);
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

  loadEvent();
})();
