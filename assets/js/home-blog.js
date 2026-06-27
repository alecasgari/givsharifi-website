async function renderHomeBlog() {
  const grid = document.getElementById('home-blog-grid');
  if (!grid) return;

  try {
    const res = await fetch('/posts/data/index.json');
    const data = await res.json();
    const posts = (data.posts || []).slice(0, 3);

    grid.innerHTML = posts.map((post) => `
      <article class="hp-blog-card">
        <a href="/blog/${post.slug}/" class="hp-blog-card__img-wrap">
          <img class="hp-blog-card__img" src="${post.image}" alt="${escapeAttr(post.title)}" loading="lazy" width="640" height="360">
        </a>
        <div class="hp-blog-card__body">
          <p class="hp-blog-card__date">${formatDate(post.date)}</p>
          <h3 class="hp-blog-card__title"><a href="/blog/${post.slug}/">${escapeHtml(post.title)}</a></h3>
          <p class="hp-blog-card__excerpt">${escapeHtml(post.excerpt)}</p>
          <a class="hp-blog-card__link" href="/blog/${post.slug}/">Read article →</a>
        </div>
      </article>
    `).join('');
  } catch (e) {
    grid.innerHTML = '<p><a href="/blog/">View all articles →</a></p>';
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
}

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeAttr(str) {
  return escapeHtml(str).replace(/'/g, '&#39;');
}

renderHomeBlog();
