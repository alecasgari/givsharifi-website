async function renderBlogList() {
  const grid = document.getElementById('blog-grid');
  if (!grid) return;

  try {
    const res = await fetch('/posts/data/index.json');
    const data = await res.json();
    const posts = (data.posts || []).sort((a, b) => new Date(b.date) - new Date(a.date));

    grid.innerHTML = posts
      .map(
        (post) => `
      <article class="blog-index-card">
        <a class="blog-index-card__media" href="/blog/${post.slug}/" tabindex="-1" aria-hidden="true">
          <img class="blog-index-card__img" src="${post.image}" alt="" loading="lazy" width="320" height="200">
        </a>
        <div class="blog-index-card__body">
          <p class="blog-index-card__meta">
            <span class="blog-index-card__cat">${escapeHtml(post.category || 'Blog')}</span>
            <span class="blog-index-card__sep" aria-hidden="true">·</span>
            <time datetime="${escapeAttr(post.date)}">${formatDate(post.date)}</time>
          </p>
          <h3 class="blog-index-card__title">
            <a href="/blog/${post.slug}/">${escapeHtml(post.title)}</a>
          </h3>
          <p class="blog-index-card__excerpt">${escapeHtml(post.excerpt)}</p>
          <a class="blog-index-card__link" href="/blog/${post.slug}/">Read article <span aria-hidden="true">→</span></a>
        </div>
      </article>
    `
      )
      .join('');
  } catch (e) {
    grid.innerHTML = '<p class="blog-index-loading">Unable to load articles. Please try again later.</p>';
    console.error(e);
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeAttr(str) {
  return escapeHtml(str).replace(/'/g, '&#39;');
}

renderBlogList();
