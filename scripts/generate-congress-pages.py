#!/usr/bin/env python3
"""Render congress event pages and listing cards as full HTML (SEO)."""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONGRESS = ROOT / "congress"
PAGES_LISTING = ROOT / "pages" / "congress" / "index.html"
SITE = "https://www.givsharifi.com"

BASE_SCRIPT = """(function(){var b=document.getElementById('site-base');var r='/';if(/\\.github\\.io$/i.test(location.hostname)){var s=location.pathname.split('/').filter(Boolean)[0];if(s)r='/'+s+'/';b.href=r;}window.__SITE_ROOT__=r;window.siteUrl=function(p){if(p==null||p==='')return r;if(/^https?:\\/\\//i.test(p)||p.startsWith('tel:')||p.startsWith('mailto:'))return p;return r+String(p).replace(/^\\//,'');};})();"""


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def esc_text(text: str) -> str:
    return html.escape(str(text), quote=False)


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Skip {path}: {e}", file=sys.stderr)
        return None


def site_path(path: str) -> str:
    return str(path).lstrip("/")


def abs_url(path: str) -> str:
    if path.startswith("http"):
        return path
    return f"{SITE}/{site_path(path)}"


def format_date(iso: str) -> str:
    try:
        return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%d %B %Y").lstrip("0")
    except ValueError:
        return iso


def truncate(text: str, max_len: int) -> str:
    if not text or len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def render_slideshow(event: dict) -> str:
    gallery = event.get("gallery") or []
    if not gallery:
        return ""
    first = gallery[0]
    multi = len(gallery) > 1
    dots = ""
    if multi:
        buttons = "".join(
            f'<button type="button" class="cong-slideshow__dot{" is-active" if i == 0 else ""}" '
            f'data-slideshow-dot="{i}" role="tab" aria-label="Photo {i + 1}" '
            f'aria-selected="{"true" if i == 0 else "false"}"></button>'
            for i in range(len(gallery))
        )
        dots = f'<div class="cong-slideshow__dots" data-slideshow-dots role="tablist" aria-label="Photo thumbnails">{buttons}</div>'
    nav_hidden = "" if multi else " hidden"
    hint = "Use arrows or swipe · Click image to enlarge" if multi else "Click image to enlarge"
    return f"""
      <section class="cong-slideshow" aria-label="Event photo slideshow">
        <div class="container">
          <div class="cong-slideshow__frame" id="cong-slideshow">
            <div class="cong-slideshow__viewport">
              <button type="button" class="cong-slideshow__nav cong-slideshow__nav--prev" data-slideshow-prev aria-label="Previous photo"{nav_hidden}>&lsaquo;</button>
              <figure class="cong-slideshow__figure" data-slideshow-figure tabindex="0" role="button" aria-label="Open full-size photo">
                <img class="cong-slideshow__img" src="{esc(site_path(first.get("file", "")))}" alt="{esc(first.get("alt") or "")}" width="1200" height="675">
                <figcaption class="cong-slideshow__caption" data-slideshow-caption>{esc_text(first.get("caption") or first.get("alt") or "")}</figcaption>
              </figure>
              <button type="button" class="cong-slideshow__nav cong-slideshow__nav--next" data-slideshow-next aria-label="Next photo"{nav_hidden}>&rsaquo;</button>
            </div>
          </div>
          <div class="cong-slideshow__meta">
            <span class="cong-slideshow__counter" data-slideshow-counter>1 / {len(gallery)}</span>
            <span class="cong-slideshow__hint">{esc_text(hint)}</span>
          </div>
          {dots}
        </div>
      </section>
    """


def render_event_body(event: dict) -> str:
    facts: list[str] = []
    if event.get("dateDisplay") or event.get("date"):
        facts.append(
            f'<li><strong>Date:</strong> {esc_text(event.get("dateDisplay") or format_date(event.get("date", "")))}</li>'
        )
    if event.get("city"):
        loc = esc_text(event["city"])
        if event.get("country"):
            loc += f', {esc_text(event["country"])}'
        facts.append(f"<li><strong>Location:</strong> {loc}</li>")
    if event.get("venue"):
        facts.append(f'<li><strong>Venue:</strong> {esc_text(event["venue"])}</li>')
    if event.get("type"):
        facts.append(f'<li><strong>Event type:</strong> {esc_text(event["type"])}</li>')

    sections = "".join(
        f"""
      <section class="cong-event-section">
        <h2>{esc_text(s.get("heading", ""))}</h2>
        {"".join(f"<p>{esc_text(p)}</p>" for p in (s.get("paragraphs") or []))}
      </section>
    """
        for s in event.get("sections") or []
    )

    organizers = ""
    if event.get("organizers"):
        items = "".join(f"<li>{esc_text(o)}</li>" for o in event["organizers"])
        organizers = f"""
      <div class="cong-event-organizers">
        <h3>Organisers</h3>
        <ul>{items}</ul>
      </div>
    """

    videos = ""
    if event.get("videos"):
        video_cards = []
        for v in event["videos"]:
            poster = f' poster="{esc(site_path(v["poster"]))}"' if v.get("poster") else ""
            title = f"<h3>{esc_text(v['title'])}</h3>" if v.get("title") else ""
            caption = f"<p>{esc_text(v['caption'])}</p>" if v.get("caption") else ""
            video_cards.append(
                f"""
              <article class="cong-event-video">
                <video controls preload="none" playsinline{poster}>
                  <source src="{esc(site_path(v.get("file", "")))}" type="video/mp4">
                </video>
                {title}
                {caption}
              </article>
            """
            )
        videos = f"""
      <section class="cong-event-videos" aria-label="Event videos">
        <div class="container">
          <h2>Congress videos</h2>
          <div class="cong-event-videos__grid">
            {"".join(video_cards)}
          </div>
        </div>
      </section>
    """

    gallery = event.get("gallery") or []
    gallery_html = ""
    if len(gallery) > 1:
        items = "".join(
            f"""
              <button type="button" class="cong-event-gallery__item" data-lightbox data-lightbox-index="{i}"
                aria-label="{esc(img.get("alt") or img.get("caption") or "Event photo")}">
                <img src="{esc(site_path(img.get("file", "")))}" alt="{esc(img.get("alt") or "")}" loading="lazy" width="480" height="360">
              </button>
            """
            for i, img in enumerate(gallery)
        )
        gallery_html = f"""
      <section class="cong-event-gallery" aria-label="All event photos">
        <div class="container">
          <h2>All Photos</h2>
          <div class="cong-event-gallery__grid" id="cong-event-gallery">
            {items}
          </div>
        </div>
      </section>
    """

    has_gallery = bool(gallery)
    cover_only = ""
    if not has_gallery and event.get("coverImage"):
        cover_only = (
            f'<section class="cong-event-cover"><div class="container">'
            f'<img src="{esc(site_path(event["coverImage"]))}" alt="{esc(event.get("title") or "")}" '
            f'width="1200" height="675"></div></section>'
        )

    type_line = (
        f'<p class="cong-event-hero__type">{esc_text(event["type"])}</p>' if event.get("type") else ""
    )
    subtitle = (
        f'<p class="cong-event-hero__subtitle">{esc_text(event["subtitle"])}</p>'
        if event.get("subtitle")
        else ""
    )
    summary = (
        f'<p class="cong-event-summary">{esc_text(event["summary"])}</p>' if event.get("summary") else ""
    )
    title = event.get("title") or event.get("slug") or "Congress"

    return f"""
      <section class="cong-event-hero">
        <div class="container">
          <nav class="blog-breadcrumb" aria-label="Breadcrumb">
            <ol>
              <li><a href="./">Home</a></li>
              <li><a href="congress/">Congress &amp; Symposia</a></li>
              <li aria-current="page">{esc_text(truncate(title, 48))}</li>
            </ol>
          </nav>
          {type_line}
          <h1>{esc_text(title)}</h1>
          {subtitle}
          <ul class="cong-event-hero__facts">{"".join(facts)}</ul>
        </div>
      </section>

      {render_slideshow(event) if has_gallery else cover_only}

      <section class="cong-event-content">
        <div class="container">
          {summary}
          {sections}
          {organizers}
        </div>
      </section>

      {videos}

      {gallery_html}

      <section class="pg-cta" aria-label="Consultation">
        <div class="container pg-cta__inner">
          <h2>Discuss your case with an internationally active neurosurgeon</h2>
          <p>Free consultation in Dubai, Tehran, or online — bring your MRI for specialist review.</p>
          <div class="pg-cta__actions">
            <button type="button" class="btn btn--primary btn--lg" data-open-consultation>Free Consultation</button>
            <a href="congress/" class="btn btn--secondary btn--lg">All Congress Events</a>
          </div>
        </div>
      </section>
    """


def build_event_page(event: dict) -> str:
    slug = event["slug"]
    title = event.get("title") or slug
    meta = event.get("metaDescription") or event.get("summary") or ""
    keywords = event.get("keywords") or ""
    date_iso = event.get("date") or ""
    cover = event.get("coverImage") or "assets/images/home/og-share.webp"
    page_url = f"{SITE}/congress/{slug}/"
    image_url = abs_url(cover)

    try:
        event_day = datetime.strptime(date_iso[:10], "%Y-%m-%d").date()
        status = "EventCompleted" if event_day < date.today() else "EventScheduled"
    except ValueError:
        status = "EventScheduled"

    schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": title,
        "description": meta,
        "startDate": date_iso,
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "eventStatus": f"https://schema.org/{status}",
        "image": image_url,
        "url": page_url,
        "location": {
            "@type": "Place",
            "name": event.get("venue") or event.get("city"),
            "address": {
                "@type": "PostalAddress",
                "addressLocality": event.get("city"),
                "addressCountry": event.get("country"),
            },
        },
        "organizer": [{"@type": "Organization", "name": name} for name in (event.get("organizers") or [])],
        "performer": {
            "@type": "Physician",
            "name": "Prof. Guive Sharifi",
            "medicalSpecialty": "Neurosurgery",
            "url": f"{SITE}/",
        },
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Congress & Symposia", "item": f"{SITE}/congress/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": page_url},
        ],
    }
    keywords_tag = f'\n  <meta name="keywords" content="{esc(keywords)}">' if keywords else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <base href='/' id="site-base">
  <script>
{BASE_SCRIPT}
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc_text(title)} | Prof. Guive Sharifi — Neurosurgeon</title>
  <meta name="description" content="{esc(meta)}">{keywords_tag}
  <link rel="canonical" href="{esc(page_url)}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Prof. Guive Sharifi">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(meta)}">
  <meta property="og:url" content="{esc(page_url)}">
  <meta property="og:image" content="{esc(image_url)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(meta)}">
  <meta name="twitter:image" content="{esc(image_url)}">
  <link rel="stylesheet" href="assets/css/site.bundle.css">
  <link rel="stylesheet" href="assets/css/pages.css">
  <link rel="stylesheet" href="assets/css/congress.css?v=20260831">
  <link rel="icon" href="assets/images/brand/favicon.svg" type="image/svg+xml">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script>
</head>
<body class="site-page cong-event-page">
  <div id="site-header"></div>
  <main id="congress-event-root" data-ssr="1">
{render_event_body(event)}
  </main>
  <div id="site-footer"></div>
  <script src="assets/js/layout.js"></script>
  <script src="assets/js/form.js"></script>
  <script src="assets/js/lightbox.js"></script>
  <script src="assets/js/video-playback.js"></script>
  <script src="assets/js/congress-single.js?v=20260831"></script>
  <script src="assets/js/analytics.js" defer></script>
</body>
</html>
"""


def listing_card(event: dict) -> str:
    slug = event.get("slug") or ""
    title = event.get("title") or slug
    cover = site_path(event.get("coverImage") or "assets/images/home/og-share.webp")
    typ = event.get("type") or ""
    date_iso = event.get("date") or ""
    city = event.get("city") or ""
    country = event.get("country") or ""
    excerpt = event.get("excerpt") or ""
    loc = esc_text(city)
    if city and country:
        loc += f", {esc_text(country)}"
    type_html = f'<span class="cong-card__type">{esc_text(typ)}</span>' if typ else ""
    date_html = f"<span>{esc_text(format_date(date_iso))}</span>" if date_iso else ""
    city_html = f"<span>{loc}</span>" if city else ""
    excerpt_html = f'<p class="cong-card__excerpt">{esc_text(excerpt)}</p>' if excerpt else ""
    return f"""        <a class="cong-card" href="congress/{esc(slug)}/" data-event-slug="{esc(slug)}">
          <div class="cong-card__media">
            <img src="{esc(cover)}" alt="{esc(title)}" loading="lazy" width="640" height="400">
          </div>
          <div class="cong-card__body">
            <div class="cong-card__meta">
              {type_html}
              {date_html}
              {city_html}
            </div>
            <h2 class="cong-card__title">{esc_text(title)}</h2>
            {excerpt_html}
            <span class="cong-card__footer">View event details →</span>
          </div>
        </a>"""


def inject_listing(events: list[dict]) -> None:
    cards = "\n".join(listing_card(e) for e in events)
    replacement = f'<div class="cong-grid" id="cong-grid" data-ssr="1">\n{cards}\n        </div>'
    pattern = r'<div class="cong-grid" id="cong-grid"[^>]*>.*?</div>'
    for path in (CONGRESS / "index.html", PAGES_LISTING):
        if not path.is_file():
            continue
        html_text = path.read_text(encoding="utf-8")
        updated, n = re.subn(pattern, replacement, html_text, count=1, flags=re.S)
        if n:
            if 'property="og:image"' not in updated:
                updated = updated.replace(
                    '<meta name="twitter:card" content="summary">',
                    '<meta property="og:image" content="https://www.givsharifi.com/assets/images/home/og-share.webp">\n  <meta name="twitter:card" content="summary">',
                    1,
                )
            path.write_text(updated, encoding="utf-8")
            print(f"  congress listing SSR: {path.relative_to(ROOT)}")
        else:
            print(f"  congress listing: #cong-grid not found in {path}", file=sys.stderr)


def main() -> int:
    index = load_json(CONGRESS / "data" / "index.json")
    if not index:
        print("congress/data/index.json missing", file=sys.stderr)
        return 1

    events = [e for e in (index.get("events") or []) if e.get("slug")]
    events = sorted(events, key=lambda e: e.get("date") or "", reverse=True)

    count = 0
    for meta in events:
        slug = meta["slug"]
        event = load_json(CONGRESS / slug / "data.json") or dict(meta)
        event.setdefault("slug", slug)
        dest = CONGRESS / slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(build_event_page(event), encoding="utf-8")
        print(f"  congress SSR: {dest.relative_to(ROOT)}")
        count += 1

    inject_listing(events)
    print(f"Rendered {count} congress event page(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
