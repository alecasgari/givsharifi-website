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
OG_SHARE = f"{SITE}/assets/images/home/og-share.webp"
OG_SHARE_ALT = "Prof. Guive Sharifi — neurosurgeon in Dubai and Tehran"
PHYSICIAN_ID = f"{SITE}/about/#physician"

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
        date_iso = (event.get("date") or "")[:10]
        date_label = event.get("dateDisplay") or format_date(date_iso)
        time_attr = f' datetime="{esc(date_iso)}"' if date_iso else ""
        facts.append(f"<li><strong>Date:</strong> <time{time_attr}>{esc_text(date_label)}</time></li>")
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
            label = v.get("title") or v.get("caption") or "Congress video"
            video_cards.append(
                f"""
              <article class="cong-event-video">
                <video controls preload="metadata" playsinline{poster} aria-label="{esc(label)}">
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


def physician_node() -> dict:
    return {
        "@type": "Physician",
        "@id": PHYSICIAN_ID,
        "name": "Prof. Guive Sharifi",
        "alternateName": ["Dr Guive Sharifi", "Guive Sharifi"],
        "honorificPrefix": "Prof.",
        "url": f"{SITE}/about/",
        "medicalSpecialty": "Neurosurgery",
        "jobTitle": "Professor of Neurosurgery",
        "image": f"{SITE}/assets/images/home/about-giv.webp",
    }


def event_status_url(event: dict) -> str:
    raw = (event.get("endDate") or event.get("date") or "")[:10]
    try:
        day = datetime.strptime(raw, "%Y-%m-%d").date()
        name = "EventCompleted" if day < date.today() else "EventScheduled"
    except ValueError:
        name = "EventScheduled"
    return f"https://schema.org/{name}"


def attendance_url(event: dict) -> str:
    mode = str(event.get("attendanceMode") or "offline").lower()
    name = {
        "online": "OnlineEventAttendanceMode",
        "mixed": "MixedEventAttendanceMode",
        "hybrid": "MixedEventAttendanceMode",
        "offline": "OfflineEventAttendanceMode",
    }.get(mode, "OfflineEventAttendanceMode")
    return f"https://schema.org/{name}"


def image_objects(event: dict) -> list[dict]:
    images: list[dict] = []
    seen: set[str] = set()

    def add(path: str, caption: str = "", alt: str = "") -> None:
        if not path:
            return
        url = abs_url(path)
        if url in seen:
            return
        seen.add(url)
        node: dict = {"@type": "ImageObject", "url": url}
        text = caption or alt
        if text:
            node["caption"] = text
        if alt:
            node["description"] = alt
        images.append(node)

    cover = event.get("coverImage") or ""
    add(cover, event.get("title") or "", event.get("title") or "")
    for img in event.get("gallery") or []:
        add(img.get("file") or "", img.get("caption") or "", img.get("alt") or "")
    images.append(
        {
            "@type": "ImageObject",
            "url": OG_SHARE,
            "width": 1200,
            "height": 800,
            "caption": OG_SHARE_ALT,
            "description": OG_SHARE_ALT,
        }
    )
    return images


def video_nodes(event: dict, page_url: str, event_id: str) -> list[dict]:
    date_iso = (event.get("date") or "")[:10]
    upload = f"{date_iso}T00:00:00+04:00" if date_iso else None
    nodes: list[dict] = []
    for i, video in enumerate(event.get("videos") or [], start=1):
        file_url = abs_url(video.get("file") or "")
        if not file_url:
            continue
        node = {
            "@type": "VideoObject",
            "@id": f"{page_url}#video-{i}",
            "name": video.get("title") or event.get("title") or "Congress video",
            "description": video.get("caption") or event.get("metaDescription") or event.get("summary") or "",
            "contentUrl": file_url,
            "encodingFormat": "video/mp4",
            "inLanguage": "en",
            "about": {"@id": event_id},
            "publisher": {
                "@type": "Organization",
                "name": "Prof. Guive Sharifi",
                "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/images/brand/logo.svg"},
            },
        }
        if video.get("poster"):
            node["thumbnailUrl"] = abs_url(video["poster"])
        if upload:
            node["uploadDate"] = upload
        nodes.append(node)
    return nodes


def build_event_graph(event: dict) -> dict:
    slug = event["slug"]
    title = event.get("title") or slug
    meta = event.get("metaDescription") or event.get("summary") or ""
    date_iso = (event.get("date") or "")[:10]
    end_iso = (event.get("endDate") or date_iso)[:10]
    page_url = f"{SITE}/congress/{slug}/"
    event_id = f"{page_url}#event"
    crumb_id = f"{page_url}#breadcrumb"
    images = image_objects(event)
    videos = video_nodes(event, page_url, event_id)
    keywords = event.get("keywords") or ""
    if isinstance(keywords, list):
        keywords = ", ".join(keywords)

    event_node: dict = {
        "@type": "Event",
        "@id": event_id,
        "name": title,
        "description": meta,
        "url": page_url,
        "image": images,
        "eventAttendanceMode": attendance_url(event),
        "eventStatus": event_status_url(event),
        "inLanguage": "en",
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
        "about": {"@type": "MedicalSpecialty", "name": "Neurosurgery"},
    }
    if date_iso:
        event_node["startDate"] = date_iso
    if end_iso:
        event_node["endDate"] = end_iso
    person = {"@id": PHYSICIAN_ID}
    if str(event.get("participation") or "speaker").lower() == "attendee":
        event_node["attendee"] = person
    else:
        event_node["performer"] = person
    if videos:
        event_node["subjectOf"] = [{"@id": v["@id"]} for v in videos]

    webpage = {
        "@type": "WebPage",
        "@id": f"{page_url}#webpage",
        "url": page_url,
        "name": title,
        "description": meta,
        "inLanguage": "en",
        "keywords": keywords,
        "isPartOf": {"@type": "WebSite", "name": "Prof. Guive Sharifi", "url": f"{SITE}/"},
        "primaryImageOfPage": images[0] if images else {"@type": "ImageObject", "url": OG_SHARE},
        "mainEntity": {"@id": event_id},
        "about": {"@id": PHYSICIAN_ID},
        "breadcrumb": {"@id": crumb_id},
        "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["h1", ".cong-event-summary"]},
    }
    breadcrumb = {
        "@type": "BreadcrumbList",
        "@id": crumb_id,
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Congress & Symposia", "item": f"{SITE}/congress/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": page_url},
        ],
    }
    return {"@context": "https://schema.org", "@graph": [webpage, event_node, breadcrumb, physician_node(), *videos]}


def build_event_page(event: dict) -> str:
    slug = event["slug"]
    title = event.get("title") or slug
    meta = event.get("metaDescription") or event.get("summary") or ""
    keywords = event.get("keywords") or ""
    if isinstance(keywords, list):
        keywords = ", ".join(keywords)
    date_iso = (event.get("date") or "")[:10]
    cover = event.get("coverImage") or "assets/images/home/og-share.webp"
    page_url = f"{SITE}/congress/{slug}/"
    image_url = abs_url(cover)
    graph = build_event_graph(event)
    keywords_tag = f'\n  <meta name="keywords" content="{esc(keywords)}">' if keywords else ""
    published = f'\n  <meta property="article:published_time" content="{esc(date_iso)}">' if date_iso else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <base href='/' id="site-base">
  <script>
{BASE_SCRIPT}
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <title>{esc_text(title)} | Prof. Guive Sharifi — Neurosurgeon</title>
  <meta name="description" content="{esc(meta)}">{keywords_tag}
  <link rel="canonical" href="{esc(page_url)}">
  <meta property="og:locale" content="en_US">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Prof. Guive Sharifi">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(meta)}">
  <meta property="og:url" content="{esc(page_url)}">
  <meta property="og:image" content="{esc(image_url)}">
  <meta property="og:image:alt" content="{esc(title)}">
  <meta property="og:image" content="{esc(OG_SHARE)}">
  <meta property="og:image:alt" content="{esc(OG_SHARE_ALT)}">
  <meta property="og:image:type" content="image/webp">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="800">{published}
  <meta property="article:author" content="Prof. Guive Sharifi">
  <meta property="article:section" content="Congress &amp; Symposia">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(meta)}">
  <meta name="twitter:image" content="{esc(image_url)}">
  <meta name="twitter:image:alt" content="{esc(title)}">
  <link rel="stylesheet" href="assets/css/site.bundle.css">
  <link rel="stylesheet" href="assets/css/pages.css">
  <link rel="stylesheet" href="assets/css/congress.css?v=20260831">
  <link rel="icon" href="assets/images/brand/favicon.svg" type="image/svg+xml">
  <script type="application/ld+json">{json.dumps(graph, ensure_ascii=False)}</script>
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
    date_iso = (event.get("date") or "")[:10]
    city = event.get("city") or ""
    country = event.get("country") or ""
    excerpt = event.get("excerpt") or ""
    loc = esc_text(city)
    if city and country:
        loc += f", {esc_text(country)}"
    type_html = f'<span class="cong-card__type">{esc_text(typ)}</span>' if typ else ""
    date_label = event.get("dateDisplay") or (format_date(date_iso) if date_iso else "")
    date_html = (
        f'<span><time datetime="{esc(date_iso)}">{esc_text(date_label)}</time></span>' if date_iso else ""
    )
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


def replace_balanced_div(html_text: str, start_marker: str, replacement: str) -> tuple[str, int]:
    start = html_text.find(start_marker)
    if start < 0:
        return html_text, 0
    i = start
    depth = 0
    while i < len(html_text):
        next_open = html_text.find("<div", i)
        next_close = html_text.find("</div>", i)
        if next_close < 0:
            return html_text, 0
        if next_open != -1 and next_open < next_close:
            depth += 1
            i = next_open + 4
        else:
            depth -= 1
            i = next_close + len("</div>")
            if depth == 0:
                return html_text[:start] + replacement + html_text[i:], 1
    return html_text, 0


def listing_schema_block(events: list[dict]) -> str:
    list_url = f"{SITE}/congress/"
    items = []
    for i, event in enumerate(events, start=1):
        slug = event.get("slug") or ""
        url = f"{list_url}{slug}/"
        date_iso = (event.get("date") or "")[:10]
        end_iso = (event.get("endDate") or date_iso)[:10]
        cover = abs_url(event.get("coverImage") or "assets/images/home/og-share.webp")
        node = {
            "@type": "Event",
            "@id": f"{url}#event",
            "name": event.get("title") or slug,
            "description": event.get("excerpt") or event.get("metaDescription") or "",
            "url": url,
            "image": [cover, OG_SHARE],
            "eventAttendanceMode": attendance_url(event),
            "eventStatus": event_status_url(event),
            "location": {
                "@type": "Place",
                "name": event.get("venue") or event.get("city"),
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": event.get("city"),
                    "addressCountry": event.get("country"),
                },
            },
        }
        person = {"@id": PHYSICIAN_ID}
        if str(event.get("participation") or "speaker").lower() == "attendee":
            node["attendee"] = person
        else:
            node["performer"] = person
        if date_iso:
            node["startDate"] = date_iso
        if end_iso:
            node["endDate"] = end_iso
        items.append({"@type": "ListItem", "position": i, "url": url, "name": node["name"], "item": node})

    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": f"{list_url}#webpage",
        "url": list_url,
        "name": "Congress & Symposia",
        "description": "International congresses, symposia, and academic events featuring Prof. Guive Sharifi — board-certified neurosurgeon in Dubai and Tehran.",
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "name": "Prof. Guive Sharifi", "url": f"{SITE}/"},
        "about": {"@id": PHYSICIAN_ID},
        "primaryImageOfPage": {
            "@type": "ImageObject",
            "url": OG_SHARE,
            "width": 1200,
            "height": 800,
            "caption": OG_SHARE_ALT,
        },
        "mainEntity": {
            "@type": "ItemList",
            "name": "Prof. Guive Sharifi — Congress & Symposia",
            "itemListOrder": "https://schema.org/ItemListOrderDescending",
            "numberOfItems": len(items),
            "itemListElement": items,
        },
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "@id": f"{list_url}#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Congress & Symposia", "item": list_url},
        ],
    }
    physician = {"@context": "https://schema.org", **physician_node()}
    return (
        "  <!-- congress-seo -->\n"
        f'  <script id="congress-listing-schema" type="application/ld+json">{json.dumps(collection, ensure_ascii=False)}</script>\n'
        f'  <script id="congress-breadcrumb-schema" type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script>\n'
        f'  <script id="congress-physician-schema" type="application/ld+json">{json.dumps(physician, ensure_ascii=False)}</script>\n'
        "  <!-- /congress-seo -->"
    )


def ensure_listing_meta(html_text: str) -> str:
    html_text = html_text.replace(
        '<meta name="twitter:card" content="summary">',
        '<meta name="twitter:card" content="summary_large_image">',
        1,
    )
    if 'name="robots"' not in html_text:
        html_text = html_text.replace(
            '<meta name="viewport"',
            '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">\n  <meta name="viewport"',
            1,
        )
    if "og:image:width" not in html_text:
        html_text = html_text.replace(
            '<meta property="og:image" content="https://www.givsharifi.com/assets/images/home/og-share.webp">',
            '<meta property="og:locale" content="en_US">\n'
            '  <meta property="og:image" content="https://www.givsharifi.com/assets/images/home/og-share.webp">\n'
            f'  <meta property="og:image:alt" content="{esc(OG_SHARE_ALT)}">\n'
            '  <meta property="og:image:type" content="image/webp">\n'
            '  <meta property="og:image:width" content="1200">\n'
            '  <meta property="og:image:height" content="800">',
            1,
        )
    if 'name="twitter:image"' not in html_text:
        html_text = html_text.replace(
            '<meta name="twitter:description" content="Academic congresses and symposia featuring Prof. Guive Sharifi.">',
            '<meta name="twitter:description" content="Academic congresses and symposia featuring Prof. Guive Sharifi.">\n'
            '  <meta name="twitter:image" content="https://www.givsharifi.com/assets/images/home/og-share.webp">\n'
            f'  <meta name="twitter:image:alt" content="{esc(OG_SHARE_ALT)}">',
            1,
        )
    return html_text


def inject_listing_schema(html_text: str, events: list[dict]) -> str:
    block = listing_schema_block(events)
    if "<!-- congress-seo -->" in html_text:
        return re.sub(r"  <!-- congress-seo -->.*?<!-- /congress-seo -->", block, html_text, count=1, flags=re.S)
    pattern = r'\s*<script type="application/ld\+json">\s*\{[\s\S]*?"@type": "BreadcrumbList"[\s\S]*?</script>'
    updated, n = re.subn(pattern, "\n" + block, html_text, count=1)
    if not n:
        print("  congress listing: breadcrumb schema not found", file=sys.stderr)
        return html_text
    return updated


def inject_listing(events: list[dict]) -> None:
    cards = "\n".join(listing_card(e) for e in events)
    replacement = f'<div class="cong-grid" id="cong-grid" data-ssr="1">\n{cards}\n        </div>'
    for path in (CONGRESS / "index.html", PAGES_LISTING):
        if not path.is_file():
            continue
        html_text = path.read_text(encoding="utf-8")
        updated, n = replace_balanced_div(html_text, '<div class="cong-grid" id="cong-grid"', replacement)
        if not n:
            print(f"  congress listing: #cong-grid not found in {path}", file=sys.stderr)
            continue
        updated = ensure_listing_meta(updated)
        updated = inject_listing_schema(updated, events)
        path.write_text(updated, encoding="utf-8")
        print(f"  congress listing SSR: {path.relative_to(ROOT)}")


def main() -> int:
    index = load_json(CONGRESS / "data" / "index.json")
    if not index:
        print("congress/data/index.json missing", file=sys.stderr)
        return 1

    events = [e for e in (index.get("events") or []) if e.get("slug")]
    events = sorted(events, key=lambda e: e.get("date") or "", reverse=True)

    count = 0
    rendered: list[dict] = []
    for meta in events:
        slug = meta["slug"]
        event = dict(meta)
        detail = load_json(CONGRESS / slug / "data.json") or {}
        event.update({k: v for k, v in detail.items() if v not in (None, "", [])})
        if meta.get("excerpt"):
            event["excerpt"] = meta["excerpt"]
        event["slug"] = slug
        dest = CONGRESS / slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(build_event_page(event), encoding="utf-8")
        print(f"  congress SSR: {dest.relative_to(ROOT)}")
        rendered.append(event)
        count += 1

    inject_listing(rendered)
    print(f"Rendered {count} congress event page(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
