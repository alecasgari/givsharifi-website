#!/usr/bin/env python3
"""Render blog/{slug}/index.html from posts/data/*.json with full HTML body (SEO / Soft 404 fix)."""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts" / "data"
BLOG_DIR = ROOT / "blog"
SITE = "https://www.givsharifi.com"

SERVICE_LINKS = {
    "Spinal Surgery": ("spinal-surgery/", "Spine Surgery Services"),
    "Brain Surgery": ("brain-surgery/", "Brain Tumor Specialist — Dubai & Tehran"),
    "Neurosurgery": ("brain-surgery/", "Brain Tumor Specialist — Dubai & Tehran"),
}

# Contextual in-article images (existing site assets)
INLINE_IMAGES: dict[str, list[dict[str, str]]] = {
    "brain-tumour-surgery-dubai": [
        {
            "src": "assets/images/services/brain-surgery/team.webp",
            "alt": "Prof. Giv Sharifi neurosurgical team performing brain surgery in the operating theatre",
        },
        {
            "src": "assets/images/gallery/prof-giv-sharifi-neurosurgery-microscope-operating-room.webp",
            "alt": "Neurosurgery with a surgical microscope in the operating room",
        },
    ],
    "minimally-invasive-neurosurgery": [
        {
            "src": "assets/images/gallery/minimally-invasive-surgery-team-monitor.webp",
            "alt": "Minimally invasive neurosurgery team reviewing monitors in the operating room",
        },
        {
            "src": "assets/images/services/pituitary-surgery/surgery.webp",
            "alt": "Endoscopic minimally invasive pituitary surgery",
        },
        {
            "src": "assets/images/services/brain-surgery/hero.webp",
            "alt": "Advanced cranial neurosurgery environment in Dubai and Tehran",
        },
    ],
    "lumbar-disc-herniation-treatment": [
        {
            "src": "assets/images/services/spinal-surgery/hero.webp",
            "alt": "Spinal surgery consultation and care with Prof. Giv Sharifi",
        },
        {
            "src": "assets/images/gallery/cervical-disc-surgery-sharifi.webp",
            "alt": "Disc surgery procedure with Prof. Giv Sharifi",
        },
    ],
    "pituitary-adenoma-symptoms": [
        {
            "src": "assets/images/services/pituitary-surgery/hero.webp",
            "alt": "Endoscopic pituitary surgery for pituitary adenoma",
        },
        {
            "src": "assets/images/gallery/prof-giv-sharifi-brain-mri-scan-operating-room.webp",
            "alt": "Brain MRI review related to pituitary and sellar lesions",
        },
    ],
    "the-future-of-spinal-surgery": [
        {
            "src": "assets/images/services/spinal-surgery/care.webp",
            "alt": "Modern spinal surgery patient care",
        },
    ],
    "the-future-of-brain-surgery-advancements-and-innovations": [
        {
            "src": "assets/images/services/brain-surgery/team.webp",
            "alt": "Neurosurgical team during brain surgery",
        },
    ],
    "spinal-cord-injuries": [
        {
            "src": "assets/images/services/spinal-surgery/hero.webp",
            "alt": "Spinal neurosurgery and cord injury care",
        },
    ],
    "ai-and-robotics-in-neurosurgery": [
        {
            "src": "assets/images/gallery/neurosurgeon-laparoscopic-instruments-operating-room.webp",
            "alt": "Advanced neurosurgical instruments in the operating room",
        },
    ],
    "groundbreaking-advances-in-non-invasive-neurosurgery-techniques": [
        {
            "src": "assets/images/gallery/minimally-invasive-surgery-team-monitor.webp",
            "alt": "Minimally invasive and advanced neurosurgery techniques",
        },
    ],
    "pediatric-neurosurgery": [
        {
            "src": "assets/images/gallery/prof-giv-sharifi-clinic-consultation-office.webp",
            "alt": "Neurosurgery consultation with Prof. Giv Sharifi",
        },
    ],
}

CATEGORY_FALLBACK_IMAGES = {
    "Brain Surgery": [
        {
            "src": "assets/images/services/brain-surgery/hero.webp",
            "alt": "Brain surgery with Prof. Giv Sharifi in Dubai and Tehran",
        }
    ],
    "Spinal Surgery": [
        {
            "src": "assets/images/services/spinal-surgery/hero.webp",
            "alt": "Spinal surgery with Prof. Giv Sharifi",
        }
    ],
    "Neurosurgery": [
        {
            "src": "assets/images/gallery/expert-surgical-team-operating-theatre.webp",
            "alt": "Expert neurosurgical team in the operating theatre",
        }
    ],
}

BASE_SCRIPT = """(function(){var b=document.getElementById('site-base');var r='/';if(/\\.github\\.io$/i.test(location.hostname)){var s=location.pathname.split('/').filter(Boolean)[0];if(s)r='/'+s+'/';b.href=r;}window.__SITE_ROOT__=r;window.siteUrl=function(p){if(p==null||p==='')return r;if(/^https?:\\/\\//i.test(p)||p.startsWith('tel:')||p.startsWith('mailto:'))return p;return r+String(p).replace(/^\\//,'');};})();"""


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def esc_text(text: str) -> str:
    return html.escape(str(text), quote=False)


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Skip {path.name}: {e}", file=sys.stderr)
        return None


def format_date(iso: str) -> str:
    try:
        return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%d %B %Y").lstrip("0")
    except ValueError:
        return iso


def estimate_reading(blocks: list) -> int:
    parts: list[str] = []
    for b in blocks or []:
        if b.get("text"):
            parts.append(b["text"])
        if b.get("items"):
            parts.extend(b["items"])
    words = len(re.findall(r"\S+", " ".join(parts)))
    return max(1, (words + 199) // 200)


def site_path(path: str) -> str:
    return path.lstrip("/")


def abs_url(path: str) -> str:
    p = path if path.startswith("http") else f"{SITE}/{site_path(path)}"
    return p


def render_block(block: dict) -> str:
    t = block.get("type")
    if t == "heading":
        level = int(block.get("level") or 2)
        level = min(max(level, 2), 4)
        return f"<h{level}>{esc_text(block.get('text', ''))}</h{level}>"
    if t == "paragraph":
        return f"<p>{esc_text(block.get('text', ''))}</p>"
    if t == "image":
        src = site_path(block.get("src", ""))
        alt = block.get("alt") or ""
        return (
            f'<figure><img src="{esc(src)}" alt="{esc(alt)}" loading="lazy" width="800" height="450">'
            f"<figcaption>{esc_text(alt)}</figcaption></figure>"
        )
    if t == "list":
        items = "".join(f"<li>{esc_text(i)}</li>" for i in block.get("items") or [])
        return f"<ul>{items}</ul>"
    if t == "ordered-list":
        items = "".join(f"<li>{esc_text(i)}</li>" for i in block.get("items") or [])
        return f"<ol>{items}</ol>"
    if t == "blockquote":
        return f"<blockquote><p>{esc_text(block.get('text', ''))}</p></blockquote>"
    if t == "cta":
        href = site_path(block.get("href", ""))
        return (
            f'<p class="blog-prose__cta"><a href="{esc(href)}" class="blog-inline-cta">'
            f"{esc_text(block.get('text', ''))} →</a></p>"
        )
    if t == "html":
        return block.get("html") or ""
    return ""


def inject_images(slug: str, category: str, blocks: list) -> list:
    """Insert existing site images into article body without duplicating featured cover."""
    images = INLINE_IMAGES.get(slug) or CATEGORY_FALLBACK_IMAGES.get(category) or []
    if not images or not blocks:
        return list(blocks)

    out = list(blocks)
    # Drop image blocks already in content with same src
    existing = {
        site_path(b.get("src", ""))
        for b in out
        if b.get("type") == "image" and b.get("src")
    }
    to_add = [img for img in images if site_path(img["src"]) not in existing]
    if not to_add:
        return out

    # Insert first image after first heading or after 2nd paragraph
    insert_at = 0
    headings = [i for i, b in enumerate(out) if b.get("type") == "heading"]
    paras = [i for i, b in enumerate(out) if b.get("type") == "paragraph"]
    if headings:
        insert_at = headings[0] + 1
    elif len(paras) >= 2:
        insert_at = paras[1] + 1
    elif paras:
        insert_at = paras[0] + 1

    out.insert(insert_at, {"type": "image", **to_add[0]})

    # Second image mid-article
    if len(to_add) > 1:
        mid = max(insert_at + 3, len(out) // 2)
        mid = min(mid, len(out))
        out.insert(mid, {"type": "image", **to_add[1]})

    # Third near end (before FAQ if present)
    if len(to_add) > 2:
        faq_idx = next(
            (i for i, b in enumerate(out) if b.get("type") == "heading" and "faq" in (b.get("text") or "").lower()),
            None,
        )
        pos = faq_idx if faq_idx is not None else len(out)
        out.insert(pos, {"type": "image", **to_add[2]})

    return out


def render_share(page_url: str, title: str, placement: str = "") -> str:
    from urllib.parse import quote

    enc_url = html.escape(page_url, quote=True)
    q_url = quote(page_url, safe="")
    q_title = quote(title, safe="")
    mod = " blog-share-card--sidebar" if placement == "sidebar" else " blog-share-card--main"
    ico = {
        "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
        "li": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 114.126 0 2.063 2.063 0 01-2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
        "fb": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
        "x": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
        "link": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>',
    }
    return f"""
      <div class="blog-share-card{mod}" aria-label="Share this post">
        <span class="blog-share-card__label">Share this post</span>
        <div class="blog-share-card__icons">
          <a class="blog-share-card__icon blog-share-card__icon--wa" href="https://wa.me/?text={q_title}%20{q_url}" target="_blank" rel="noopener noreferrer" aria-label="Share on WhatsApp">{ico["wa"]}</a>
          <a class="blog-share-card__icon blog-share-card__icon--li" href="https://www.linkedin.com/sharing/share-offsite/?url={q_url}" target="_blank" rel="noopener noreferrer" aria-label="Share on LinkedIn">{ico["li"]}</a>
          <a class="blog-share-card__icon blog-share-card__icon--fb" href="https://www.facebook.com/sharer/sharer.php?u={q_url}" target="_blank" rel="noopener noreferrer" aria-label="Share on Facebook">{ico["fb"]}</a>
          <a class="blog-share-card__icon blog-share-card__icon--x" href="https://twitter.com/intent/tweet?url={q_url}&amp;text={q_title}" target="_blank" rel="noopener noreferrer" aria-label="Share on X">{ico["x"]}</a>
          <button type="button" class="blog-share-card__icon blog-share-card__icon--copy" data-copy-url="{enc_url}" aria-label="Copy link">{ico["link"]}</button>
        </div>
      </div>"""


def render_recent(recent: list[dict]) -> str:
    items = []
    for p in recent:
        items.append(
            f"""<li>
          <a href="blog/{esc(p['slug'])}/">
            <span class="blog-sidebar__post-cat">{esc_text(p.get('category') or 'Blog')}</span>
            <span class="blog-sidebar__post-title">{esc_text(p.get('title') or '')}</span>
          </a>
        </li>"""
        )
    return f'<ul class="blog-sidebar__posts">{"".join(items)}</ul>'


def build_article_html(post: dict, recent: list[dict]) -> str:
    slug = post["slug"]
    title = post.get("title") or slug
    excerpt = post.get("excerpt") or ""
    category = post.get("category") or ""
    date = post.get("date") or ""
    author = post.get("author") or {
        "name": "Prof. Giv Sharifi",
        "title": "Board-Certified Neurosurgeon",
    }
    tags = post.get("tags") or []
    featured = post.get("featuredImage") or ""
    page_url = f"{SITE}/blog/{slug}/"
    reading = post.get("readingTimeMinutes") or estimate_reading(post.get("content") or [])
    service_href, service_label = SERVICE_LINKS.get(
        category, ("brain-surgery/", "Our Services")
    )

    blocks = inject_images(slug, category, post.get("content") or [])
    body = "".join(render_block(b) for b in blocks)

    cover = ""
    if featured:
        cover = f"""<figure class="blog-post__cover">
              <img src="{esc(site_path(featured))}" alt="{esc(title)}" width="800" height="450" itemprop="image" fetchpriority="high">
            </figure>"""

    tags_html = ""
    if tags:
        tag_items = "".join(
            f'<li><span class="blog-post__tag">{esc_text(t)}</span></li>' for t in tags
        )
        tags_html = f"""<div class="blog-post__tags" aria-label="Tags">
                <span class="blog-post__tags-label">Tags</span>
                <ul class="blog-post__tags-list">{tag_items}</ul>
              </div>"""

    recent_html = render_recent(recent) if recent else ""
    more_mobile = ""
    if recent:
        more_mobile = f"""<section class="blog-post__more blog-post__more--mobile" aria-labelledby="more-mobile-heading">
                <h2 id="more-mobile-heading" class="blog-post__more-title">More articles</h2>
                {recent_html}
              </section>"""

    sidebar_recent = ""
    if recent:
        sidebar_recent = f"""<div class="blog-sidebar__card blog-sidebar__card--posts">
                <p class="blog-sidebar__title">More articles</p>
                {recent_html}
              </div>"""

    cat_line = (
        f'<p class="blog-post__category" itemprop="articleSection">{esc_text(category)}</p>'
        if category
        else ""
    )
    lead = (
        f'<p class="blog-post__lead" itemprop="description">{esc_text(excerpt)}</p>'
        if excerpt
        else ""
    )
    trunc_title = title if len(title) <= 48 else title[:47].rstrip() + "…"

    return f"""
      <article class="blog-post" itemscope itemtype="https://schema.org/BlogPosting">
        <meta itemprop="headline" content="{esc(title)}">
        <meta itemprop="datePublished" content="{esc(date)}">

        <div class="blog-post__hero">
          <div class="container">
            <nav class="blog-breadcrumb" aria-label="Breadcrumb">
              <ol>
                <li><a href="./">Home</a></li>
                <li><a href="blog/">Blog</a></li>
                <li aria-current="page">{esc_text(trunc_title)}</li>
              </ol>
            </nav>

            {cat_line}
            <h1 class="blog-post__title" itemprop="name">{esc_text(title)}</h1>

            <p class="blog-post__meta">
              <time datetime="{esc(date)}" itemprop="datePublished">{format_date(date)}</time>
              <span class="blog-post__meta-sep" aria-hidden="true">·</span>
              <span>{reading} min read</span>
              <span class="blog-post__meta-sep" aria-hidden="true">·</span>
              <span itemprop="author" itemscope itemtype="https://schema.org/Person">
                <span itemprop="name">{esc_text(author.get('name', 'Prof. Giv Sharifi'))}</span>
              </span>
            </p>

            {cover}
            {lead}
            {render_share(page_url, title)}
          </div>
        </div>

        <div class="blog-post__body">
          <div class="container blog-post__body-grid">
            <div class="blog-post__content">
              <div class="blog-prose pg-prose" itemprop="articleBody">
                {body}
              </div>

              {tags_html}

              <footer class="blog-post__author">
                <div class="blog-author-card">
                  <div class="blog-author-card__avatar" aria-hidden="true">GS</div>
                  <div>
                    <p class="blog-author-card__name">{esc_text(author.get('name', 'Prof. Giv Sharifi'))}</p>
                    <p class="blog-author-card__role">{esc_text(author.get('title') or 'Board-Certified Neurosurgeon')}</p>
                    <p class="blog-author-card__bio">Professor of neurosurgery with 25+ years of experience in brain, spine, and pituitary surgery — Dubai &amp; Tehran.</p>
                  </div>
                </div>
              </footer>

              {more_mobile}

              <p class="blog-post__back"><a href="blog/">← All articles</a></p>
            </div>

            <aside class="blog-post__sidebar" aria-label="Article sidebar">
              {render_share(page_url, title, 'sidebar')}
              <div class="blog-sidebar__card blog-sidebar__card--cta">
                <p class="blog-sidebar__title">Need expert advice?</p>
                <p>Book a free consultation with Prof. Sharifi in Dubai or Tehran.</p>
                <button type="button" class="btn btn--primary btn--block" data-open-consultation>Free Consultation</button>
                <button type="button" class="btn btn--whatsapp btn--block" data-open-whatsapp>WhatsApp</button>
              </div>
              <div class="blog-sidebar__card">
                <p class="blog-sidebar__title">Related service</p>
                <a href="{esc(service_href)}" class="blog-sidebar__link">{esc_text(service_label)} →</a>
              </div>
              {sidebar_recent}
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
            <a href="{esc(service_href)}" class="btn btn--secondary btn--lg">{esc_text(service_label)}</a>
          </div>
        </div>
      </section>
    """


def build_page(post: dict, recent: list[dict]) -> str:
    slug = post["slug"]
    title = post.get("title") or slug
    meta = post.get("metaDescription") or post.get("excerpt") or ""
    date = post.get("date") or ""
    category = post.get("category") or ""
    featured = post.get("featuredImage") or "/assets/images/home/og-share.webp"
    page_url = f"{SITE}/blog/{slug}/"
    image_url = abs_url(featured)
    author = post.get("author") or {"name": "Prof. Giv Sharifi", "url": SITE + "/"}
    tags = post.get("tags") or []

    article_schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": meta,
        "image": image_url,
        "datePublished": date,
        "dateModified": post.get("updatedDate") or date,
        "author": {
            "@type": "Person",
            "name": author.get("name", "Prof. Giv Sharifi"),
            "url": author.get("url") or f"{SITE}/",
        },
        "publisher": {
            "@type": "Organization",
            "name": "Prof. Giv Sharifi",
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE}/assets/images/brand/logo.svg",
            },
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
        "articleSection": category,
        "keywords": ", ".join(tags),
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": page_url},
        ],
    }

    article_html = build_article_html(post, recent)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <base href='/' id="site-base">
  <script>
{BASE_SCRIPT}
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc_text(title)} | Prof. Giv Sharifi</title>
  <meta name="description" content="{esc(meta)}">
  <link rel="canonical" href="{esc(page_url)}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Prof. Giv Sharifi">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(meta)}">
  <meta property="og:url" content="{esc(page_url)}">
  <meta property="og:image" content="{esc(image_url)}">
  <meta property="article:published_time" content="{esc(date)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(meta)}">
  <meta name="twitter:image" content="{esc(image_url)}">
  <link rel="stylesheet" href="assets/css/site.bundle.css">
  <link rel="stylesheet" href="assets/css/pages.css">
  <link rel="stylesheet" href="assets/css/blog.css">
  <link rel="icon" href="assets/images/brand/favicon.svg" type="image/svg+xml">
  <script type="application/ld+json">{json.dumps(article_schema, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script>
</head>
<body class="site-page blog-post-page">
  <div id="site-header"></div>
  <main id="blog-post-root" data-ssr="1">
{article_html}
  </main>
  <div id="site-footer"></div>
  <script src="assets/js/layout.js"></script>
  <script src="assets/js/form.js"></script>
  <script src="assets/js/blog-single.js"></script>
  <script src="assets/js/analytics.js" defer></script>
</body>
</html>
"""


def main() -> int:
    index = load_json(POSTS_DIR / "index.json")
    if not index:
        print("posts/data/index.json missing", file=sys.stderr)
        return 1

    posts_meta = index.get("posts") or []
    seen: set[str] = set()
    unique_meta: list[dict] = []
    for p in posts_meta:
        slug = (p.get("slug") or "").strip()
        if not slug or slug in seen:
            continue
        seen.add(slug)
        unique_meta.append(p)

    count = 0
    for meta in unique_meta:
        slug = meta["slug"]
        post_path = POSTS_DIR / f"{slug}.json"
        post = load_json(post_path)
        if not post:
            continue
        post.setdefault("slug", slug)
        recent = [p for p in unique_meta if p.get("slug") != slug][:4]
        html_out = build_page(post, recent)
        dest = BLOG_DIR / slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_out, encoding="utf-8")
        print(f"  blog SSR: {dest.relative_to(ROOT)}")
        count += 1

    print(f"Rendered {count} blog post page(s) with full HTML content.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
