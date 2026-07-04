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
      initSlideshow(event);
      initGalleryLightbox(event);
    } catch (e) {
      root.innerHTML =
        '<div class="container cong-event__error"><h1>Event not found</h1><p><a href="' +
        u('congress/') +
        '">← Back to Congress &amp; Symposia</a></p></div>';
    }
  }

  function applyHead(event, pageUrl, imageUrl) {
    document.title = event.title + ' | Prof. Giv Sharifi — Neurosurgeon';

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
        { '@type': 'ListItem', position: 2, name: 'Congress & Symposia', item: SITE + '/congress/' },
        { '@type': 'ListItem', position: 3, name: event.title, item: pageUrl },
      ],
    };
    const bcScript = document.createElement('script');
    bcScript.type = 'application/ld+json';
    bcScript.textContent = JSON.stringify(breadcrumb);
    document.head.appendChild(bcScript);
  }

  function renderSlideshow(event) {
    if (!event.gallery || !event.gallery.length) return '';

    const multi = event.gallery.length > 1;
    const first = event.gallery[0];

    return `
      <section class="cong-slideshow" aria-label="Event photo slideshow">
        <div class="container">
          <div class="cong-slideshow__frame" id="cong-slideshow">
            <div class="cong-slideshow__viewport">
              <button type="button" class="cong-slideshow__nav cong-slideshow__nav--prev" data-slideshow-prev aria-label="Previous photo"${multi ? '' : ' hidden'}>&lsaquo;</button>
              <figure class="cong-slideshow__figure" data-slideshow-figure tabindex="0" role="button" aria-label="Open full-size photo">
                <img class="cong-slideshow__img" src="${escapeAttr(u(first.file))}" alt="${escapeAttr(first.alt || '')}" width="1200" height="675">
                <figcaption class="cong-slideshow__caption" data-slideshow-caption>${escapeHtml(first.caption || first.alt || '')}</figcaption>
              </figure>
              <button type="button" class="cong-slideshow__nav cong-slideshow__nav--next" data-slideshow-next aria-label="Next photo"${multi ? '' : ' hidden'}>&rsaquo;</button>
            </div>
          </div>
          <div class="cong-slideshow__meta">
            <span class="cong-slideshow__counter" data-slideshow-counter>1 / ${event.gallery.length}</span>
            <span class="cong-slideshow__hint">${multi ? 'Use arrows or swipe · Click image to enlarge' : 'Click image to enlarge'}</span>
          </div>
          ${multi ? `<div class="cong-slideshow__dots" data-slideshow-dots role="tablist" aria-label="Photo thumbnails">${event.gallery.map((_, i) => `<button type="button" class="cong-slideshow__dot${i === 0 ? ' is-active' : ''}" data-slideshow-dot="${i}" role="tab" aria-label="Photo ${i + 1}" aria-selected="${i === 0}"></button>`).join('')}</div>` : ''}
        </div>
      </section>
    `;
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
      facts.push('<li><strong>Event type:</strong> ' + escapeHtml(event.type) + '</li>');
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
        <h3>Organisers</h3>
        <ul>${event.organizers.map((o) => '<li>' + escapeHtml(o) + '</li>').join('')}</ul>
      </div>
    `
        : '';

    const gallery =
      event.gallery && event.gallery.length > 1
        ? `
      <section class="cong-event-gallery" aria-label="All event photos">
        <div class="container">
          <h2>All Photos</h2>
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

    const hasGallery = event.gallery && event.gallery.length;
    const coverOnly =
      !hasGallery && event.coverImage
        ? '<section class="cong-event-cover"><div class="container"><img src="' +
          escapeAttr(u(event.coverImage)) +
          '" alt="' +
          escapeAttr(event.title) +
          '" width="1200" height="675"></div></section>'
        : '';

    return `
      <section class="cong-event-hero">
        <div class="container">
          <nav class="blog-breadcrumb" aria-label="Breadcrumb">
            <ol>
              <li><a href="${u('./')}">Home</a></li>
              <li><a href="${u('congress/')}">Congress &amp; Symposia</a></li>
              <li aria-current="page">${escapeHtml(truncate(event.title, 48))}</li>
            </ol>
          </nav>
          ${event.type ? '<p class="cong-event-hero__type">' + escapeHtml(event.type) + '</p>' : ''}
          <h1>${escapeHtml(event.title)}</h1>
          ${event.subtitle ? '<p class="cong-event-hero__subtitle">' + escapeHtml(event.subtitle) + '</p>' : ''}
          <ul class="cong-event-hero__facts">${facts.join('')}</ul>
        </div>
      </section>

      ${hasGallery ? renderSlideshow(event) : coverOnly}

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
          <h2>Discuss your case with an internationally active neurosurgeon</h2>
          <p>Free consultation in Dubai, Tehran, or online — bring your MRI for specialist review.</p>
          <div class="pg-cta__actions">
            <button type="button" class="btn btn--primary btn--lg" data-open-consultation>Free Consultation</button>
            <a href="${u('congress/')}" class="btn btn--secondary btn--lg">All Congress Events</a>
          </div>
        </div>
      </section>
    `;
  }

  function initSlideshow(event) {
    if (!event.gallery || !event.gallery.length) return;

    const frame = document.getElementById('cong-slideshow');
    if (!frame) return;

    const img = frame.querySelector('.cong-slideshow__img');
    const caption = frame.querySelector('[data-slideshow-caption]');
    const counter = document.querySelector('[data-slideshow-counter]');
    const prevBtn = frame.querySelector('[data-slideshow-prev]');
    const nextBtn = frame.querySelector('[data-slideshow-next]');
    const dotsWrap = document.querySelector('[data-slideshow-dots]');
    const figure = frame.querySelector('[data-slideshow-figure]');

    let index = 0;
    let touchStartX = 0;
    const items = event.gallery;
    const lightboxItems = items.map((imgItem) => ({
      src: u(imgItem.file),
      alt: imgItem.alt || '',
      caption: imgItem.caption || imgItem.alt || '',
    }));

    function showAt(i) {
      index = ((i % items.length) + items.length) % items.length;
      const item = items[index];
      if (img) {
        img.classList.add('is-fading');
        const nextSrc = u(item.file);
        if (img.getAttribute('src') !== nextSrc) {
          img.addEventListener(
            'load',
            () => img.classList.remove('is-fading'),
            { once: true }
          );
          img.src = nextSrc;
          img.alt = item.alt || '';
        } else {
          img.classList.remove('is-fading');
        }
      }
      if (caption) caption.textContent = item.caption || item.alt || '';
      if (counter) counter.textContent = index + 1 + ' / ' + items.length;
      if (dotsWrap) {
        dotsWrap.querySelectorAll('[data-slideshow-dot]').forEach((dot, j) => {
          const active = j === index;
          dot.classList.toggle('is-active', active);
          dot.setAttribute('aria-selected', active ? 'true' : 'false');
        });
      }
    }

    function step(delta) {
      if (items.length < 2) return;
      showAt(index + delta);
    }

    if (prevBtn) prevBtn.addEventListener('click', () => step(-1));
    if (nextBtn) nextBtn.addEventListener('click', () => step(1));

    if (dotsWrap) {
      dotsWrap.querySelectorAll('[data-slideshow-dot]').forEach((dot) => {
        dot.addEventListener('click', () => {
          const i = Number.parseInt(dot.dataset.slideshowDot, 10);
          if (Number.isFinite(i)) showAt(i);
        });
      });
    }

    frame.addEventListener(
      'touchstart',
      (e) => {
        touchStartX = e.changedTouches[0].screenX;
      },
      { passive: true }
    );

    frame.addEventListener(
      'touchend',
      (e) => {
        if (items.length < 2) return;
        const dx = e.changedTouches[0].screenX - touchStartX;
        if (Math.abs(dx) < 48) return;
        step(dx < 0 ? 1 : -1);
      },
      { passive: true }
    );

    if (figure) {
      figure.addEventListener('click', () => {
        if (window.GivLightbox) window.GivLightbox.openGallery(lightboxItems, index);
      });
      figure.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          if (window.GivLightbox) window.GivLightbox.openGallery(lightboxItems, index);
        }
        if (e.key === 'ArrowLeft') step(-1);
        if (e.key === 'ArrowRight') step(1);
      });
    }

    showAt(0);
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
