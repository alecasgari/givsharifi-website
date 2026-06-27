(function () {
  const root = document.getElementById('blog-post-root');
  if (!root) return;

  const SITE = 'https://www.givsharifi.com';

  function u(path) {
    return typeof window.siteUrl === 'function' ? window.siteUrl(path) : path;
  }

  function sitePathname() {
    let path = window.location.pathname.replace(/\/$/, '') || '/';
    const root = (window.__SITE_ROOT__ || '/').replace(/\/$/, '');
    if (root && root !== '/' && path.startsWith(root)) {
      path = path.slice(root.length) || '/';
    }
    return path;
  }

  const parts = sitePathname().replace(/^\//, '').split('/').filter(Boolean);
  const slug = parts[parts.length - 1] || parts[parts.length - 2];

  if (!slug || slug === 'blog') return;

  const SERVICE_LINKS = {
    'Spinal Surgery': { href: 'spinal-surgery/', label: 'Spinal Surgery Services' },
    'Brain Surgery': { href: 'brain-surgery/', label: 'Brain Surgery Services' },
    'Neurosurgery': { href: 'brain-surgery/', label: 'Neurosurgery Services' },
  };

  async function loadPost() {
    try {
      const [postRes, indexRes] = await Promise.all([
        fetch(u('posts/data/' + slug + '.json')),
        fetch(u('posts/data/index.json')),
      ]);
      if (!postRes.ok) throw new Error('Not found');
      const post = await postRes.json();
      const index = indexRes.ok ? await indexRes.json() : { posts: [] };
      const recent = (index.posts || []).filter((p) => p.slug !== slug).slice(0, 4);
      const pageUrl = SITE + '/blog/' + slug + '/';
      const imageUrl = post.featuredImage ? SITE + post.featuredImage : SITE + '/assets/images/home/og-share.webp';

      applyHead(post, pageUrl, imageUrl);
      root.innerHTML = renderPost(post, pageUrl, recent);
      initShare(pageUrl);
    } catch (e) {
      root.innerHTML =
        '<div class="container blog-post__error"><h1>Article not found</h1><p><a href="' + u('blog/') + '">← Back to blog</a></p></div>';
    }
  }

  function applyHead(post, pageUrl, imageUrl) {
    document.title = post.title + ' | Prof. Giv Sharifi';

    setMeta('name', 'description', post.metaDescription || post.excerpt || '');
    setLink('canonical', pageUrl);

    setMeta('property', 'og:title', post.title);
    setMeta('property', 'og:description', post.metaDescription || post.excerpt || '');
    setMeta('property', 'og:url', pageUrl);
    setMeta('property', 'og:image', imageUrl);
    setMeta('property', 'article:published_time', post.date);
    if (post.category) setMeta('property', 'article:section', post.category);

    setMeta('name', 'twitter:title', post.title);
    setMeta('name', 'twitter:description', post.metaDescription || post.excerpt || '');
    setMeta('name', 'twitter:image', imageUrl);

    injectJsonLd(post, pageUrl, imageUrl);
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

  function injectJsonLd(post, pageUrl, imageUrl) {
    const author = post.author || { name: 'Prof. Giv Sharifi', url: SITE + '/' };
    const schema = {
      '@context': 'https://schema.org',
      '@type': 'BlogPosting',
      headline: post.title,
      description: post.metaDescription || post.excerpt,
      image: imageUrl,
      datePublished: post.date,
      dateModified: post.updatedDate || post.date,
      author: {
        '@type': 'Person',
        name: author.name,
        url: author.url || SITE + '/',
      },
      publisher: {
        '@type': 'Organization',
        name: 'Prof. Giv Sharifi',
        logo: {
          '@type': 'ImageObject',
          url: SITE + '/assets/images/brand/logo.svg',
        },
      },
      mainEntityOfPage: { '@type': 'WebPage', '@id': pageUrl },
      articleSection: post.category,
      keywords: (post.tags || []).join(', '),
    };

    let script = document.getElementById('blog-post-schema');
    if (!script) {
      script = document.createElement('script');
      script.id = 'blog-post-schema';
      script.type = 'application/ld+json';
      document.head.appendChild(script);
    }
    script.textContent = JSON.stringify(schema);

    const breadcrumb = {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: SITE + '/' },
        { '@type': 'ListItem', position: 2, name: 'Blog', item: SITE + '/blog/' },
        { '@type': 'ListItem', position: 3, name: post.title, item: pageUrl },
      ],
    };

    let bc = document.getElementById('blog-breadcrumb-schema');
    if (!bc) {
      bc = document.createElement('script');
      bc.id = 'blog-breadcrumb-schema';
      bc.type = 'application/ld+json';
      document.head.appendChild(bc);
    }
    bc.textContent = JSON.stringify(breadcrumb);
  }

  function renderPost(post, pageUrl, recent) {
    const author = post.author || { name: 'Prof. Giv Sharifi', title: 'Board-Certified Neurosurgeon' };
    const reading = post.readingTimeMinutes || estimateReading(post.content);
    const service = SERVICE_LINKS[post.category] || { href: 'spinal-surgery/', label: 'Our Services' };
    const tags = post.tags || [];

    return `
      <article class="blog-post" itemscope itemtype="https://schema.org/BlogPosting">
        <meta itemprop="headline" content="${escapeAttr(post.title)}">
        <meta itemprop="datePublished" content="${escapeAttr(post.date)}">

        <div class="blog-post__hero">
          <div class="container">
            <nav class="blog-breadcrumb" aria-label="Breadcrumb">
              <ol>
                <li><a href="./">Home</a></li>
                <li><a href="blog/">Blog</a></li>
                <li aria-current="page">${escapeHtml(truncate(post.title, 48))}</li>
              </ol>
            </nav>

            ${post.category ? `<p class="blog-post__category" itemprop="articleSection">${escapeHtml(post.category)}</p>` : ''}
            <h1 class="blog-post__title" itemprop="name">${escapeHtml(post.title)}</h1>

            <p class="blog-post__meta">
              <time datetime="${escapeAttr(post.date)}" itemprop="datePublished">${formatDate(post.date)}</time>
              <span class="blog-post__meta-sep" aria-hidden="true">·</span>
              <span>${reading} min read</span>
              <span class="blog-post__meta-sep" aria-hidden="true">·</span>
              <span itemprop="author" itemscope itemtype="https://schema.org/Person">
                <span itemprop="name">${escapeHtml(author.name)}</span>
              </span>
            </p>

            ${
              post.featuredImage
                ? `<figure class="blog-post__cover">
              <img src="${escapeAttr(u(post.featuredImage))}" alt="" width="800" height="450" itemprop="image" fetchpriority="high">
            </figure>`
                : ''
            }

            ${
              post.excerpt
                ? `<p class="blog-post__lead" itemprop="description">${escapeHtml(post.excerpt)}</p>`
                : ''
            }

            ${renderShareCard(pageUrl, post.title)}
          </div>
        </div>

        <div class="blog-post__body">
          <div class="container blog-post__body-grid">
            <div class="blog-post__content">
              <div class="blog-prose pg-prose" itemprop="articleBody">
                ${renderContent(post.content)}
              </div>

              ${
                tags.length
                  ? `<div class="blog-post__tags" aria-label="Tags">
                <span class="blog-post__tags-label">Tags</span>
                <ul class="blog-post__tags-list">
                  ${tags.map((t) => '<li><span class="blog-post__tag">' + escapeHtml(t) + '</span></li>').join('')}
                </ul>
              </div>`
                  : ''
              }

              <footer class="blog-post__author">
                <div class="blog-author-card">
                  <div class="blog-author-card__avatar" aria-hidden="true">GS</div>
                  <div>
                    <p class="blog-author-card__name">${escapeHtml(author.name)}</p>
                    <p class="blog-author-card__role">${escapeHtml(author.title || 'Board-Certified Neurosurgeon')}</p>
                    <p class="blog-author-card__bio">Professor of neurosurgery with 25+ years of experience in brain, spine, and pituitary surgery — Dubai &amp; Tehran.</p>
                  </div>
                </div>
              </footer>

              ${
                recent.length
                  ? `<section class="blog-post__more blog-post__more--mobile" aria-labelledby="more-mobile-heading">
                <h2 id="more-mobile-heading" class="blog-post__more-title">More articles</h2>
                ${renderRecentPostsList(recent)}
              </section>`
                  : ''
              }

              <p class="blog-post__back"><a href="blog/">← All articles</a></p>
            </div>

            <aside class="blog-post__sidebar" aria-label="Article sidebar">
              ${renderShareCard(pageUrl, post.title, 'sidebar')}
              <div class="blog-sidebar__card blog-sidebar__card--cta">
                <p class="blog-sidebar__title">Need expert advice?</p>
                <p>Book a free consultation with Prof. Sharifi in Dubai or Tehran.</p>
                <button type="button" class="btn btn--primary btn--block" data-open-consultation>Free Consultation</button>
                <button type="button" class="btn btn--whatsapp btn--block" data-open-whatsapp>WhatsApp</button>
              </div>
              <div class="blog-sidebar__card">
                <p class="blog-sidebar__title">Related service</p>
                <a href="${service.href}" class="blog-sidebar__link">${escapeHtml(service.label)} →</a>
              </div>
              ${
                recent.length
                  ? `<div class="blog-sidebar__card blog-sidebar__card--posts">
                <p class="blog-sidebar__title">More articles</p>
                ${renderRecentPostsList(recent)}
              </div>`
                  : ''
              }
            </aside>
          </div>
        </div>
      </article>

      <section class="blog-post-cta pg-cta" aria-label="Consultation">
        <div class="container pg-cta__inner">
          <h2>Considering spinal or neurosurgery?</h2>
          <p>Discuss your MRI and treatment options — free consultation in Dubai, Tehran, or online.</p>
          <div class="pg-cta__actions">
            <button type="button" class="btn btn--primary btn--lg" data-open-consultation>Free Consultation</button>
            <a href="${service.href}" class="btn btn--secondary btn--lg">${escapeHtml(service.label)}</a>
          </div>
        </div>
      </section>
    `;
  }

  const SHARE_ICONS = {
    wa: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
    li: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 114.126 0 2.063 2.063 0 01-2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
    fb: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
    link: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>',
  };

  function renderShareCard(url, title, placement) {
    const encUrl = encodeURIComponent(url);
    const encTitle = encodeURIComponent(title);
    const mod = placement === 'sidebar' ? ' blog-share-card--sidebar' : '';
    const hiddenOnDesktop = placement === 'sidebar' ? '' : ' blog-share-card--main';

    return `
      <div class="blog-share-card${mod}${hiddenOnDesktop}" aria-label="Share this post">
        <span class="blog-share-card__label">Share this post</span>
        <div class="blog-share-card__icons">
          <a class="blog-share-card__icon blog-share-card__icon--wa" href="https://wa.me/?text=${encTitle}%20${encUrl}" target="_blank" rel="noopener noreferrer" aria-label="Share on WhatsApp">${SHARE_ICONS.wa}</a>
          <a class="blog-share-card__icon blog-share-card__icon--li" href="https://www.linkedin.com/sharing/share-offsite/?url=${encUrl}" target="_blank" rel="noopener noreferrer" aria-label="Share on LinkedIn">${SHARE_ICONS.li}</a>
          <a class="blog-share-card__icon blog-share-card__icon--fb" href="https://www.facebook.com/sharer/sharer.php?u=${encUrl}" target="_blank" rel="noopener noreferrer" aria-label="Share on Facebook">${SHARE_ICONS.fb}</a>
          <a class="blog-share-card__icon blog-share-card__icon--x" href="https://twitter.com/intent/tweet?url=${encUrl}&text=${encTitle}" target="_blank" rel="noopener noreferrer" aria-label="Share on X">${SHARE_ICONS.x}</a>
          <button type="button" class="blog-share-card__icon blog-share-card__icon--copy" data-copy-url="${escapeAttr(url)}" aria-label="Copy link">${SHARE_ICONS.link}</button>
        </div>
      </div>
    `;
  }

  function renderRecentPostsList(posts) {
    return `<ul class="blog-sidebar__posts">
      ${posts
        .map(
          (p) => `
        <li>
          <a href="blog/${p.slug}/">
            <span class="blog-sidebar__post-cat">${escapeHtml(p.category || 'Blog')}</span>
            <span class="blog-sidebar__post-title">${escapeHtml(p.title)}</span>
          </a>
        </li>`
        )
        .join('')}
    </ul>`;
  }

  function initShare(url) {
    root.querySelectorAll('[data-copy-url]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(url);
          btn.classList.add('is-copied');
          btn.innerHTML = SHARE_ICONS.check;
          btn.setAttribute('aria-label', 'Link copied');
          setTimeout(() => {
            btn.classList.remove('is-copied');
            btn.innerHTML = SHARE_ICONS.link;
            btn.setAttribute('aria-label', 'Copy link');
          }, 2000);
        } catch (e) {
          window.prompt('Copy this link:', url);
        }
      });
    });
  }

  function renderContent(blocks) {
    if (!Array.isArray(blocks)) return '';
    return blocks
      .map((b) => {
        switch (b.type) {
          case 'heading':
            return `<h${b.level || 2}>${escapeHtml(b.text)}</h${b.level || 2}>`;
          case 'paragraph':
            return `<p>${escapeHtml(b.text)}</p>`;
          case 'image':
            return `<figure><img src="${escapeAttr(u(b.src))}" alt="${escapeAttr(b.alt || '')}" loading="lazy" width="800" height="450"><figcaption>${escapeHtml(b.alt || '')}</figcaption></figure>`;
          case 'list':
            return `<ul>${(b.items || []).map((i) => '<li>' + escapeHtml(i) + '</li>').join('')}</ul>`;
          case 'ordered-list':
            return `<ol>${(b.items || []).map((i) => '<li>' + escapeHtml(i) + '</li>').join('')}</ol>`;
          case 'blockquote':
            return `<blockquote><p>${escapeHtml(b.text)}</p></blockquote>`;
          case 'cta':
            return `<p class="blog-prose__cta"><a href="${escapeAttr(b.href)}" class="blog-inline-cta">${escapeHtml(b.text)} →</a></p>`;
          case 'html':
            return b.html || '';
          default:
            return '';
        }
      })
      .join('');
  }

  function estimateReading(blocks) {
    const text = (blocks || [])
      .map((b) => {
        if (b.text) return b.text;
        if (b.items) return b.items.join(' ');
        return '';
      })
      .join(' ');
    const words = text.split(/\s+/).filter(Boolean).length;
    return Math.max(1, Math.ceil(words / 200));
  }

  function formatDate(iso) {
    return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  }

  function truncate(str, max) {
    if (str.length <= max) return str;
    return str.slice(0, max - 1).trim() + '…';
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

  loadPost();
})();
