#!/usr/bin/env python3
"""Build sitemap.xml from static pages, blog posts, and congress events."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://www.givsharifi.com"
OUT = ROOT / "sitemap.xml"

# Service / listing pages (exclude done/ — noindex thank-you page)
STATIC_PAGES: list[tuple[str, str, str]] = [
    ("", "weekly", "1.0"),
    ("brain-surgery/", "monthly", "0.9"),
    ("spinal-surgery/", "monthly", "0.9"),
    ("endoscopic-pituitary-surgery/", "monthly", "0.9"),
    ("physiotherapy/", "monthly", "0.9"),
    ("medical-tourism/", "monthly", "0.9"),
    ("publications/", "monthly", "0.8"),
    ("videos/", "weekly", "0.8"),
    ("gallery/", "weekly", "0.8"),
    ("blog/", "weekly", "0.8"),
    ("congress/", "monthly", "0.8"),
]


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Invalid JSON: {path}", file=sys.stderr)
        return None


def add_url(
    urlset: ET.Element,
    path: str,
    changefreq: str,
    priority: str,
    lastmod: str | None = None,
) -> None:
    loc = f"{SITE_URL}/{path}" if path else f"{SITE_URL}/"
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = loc
    if lastmod:
        ET.SubElement(url, "lastmod").text = lastmod
    ET.SubElement(url, "changefreq").text = changefreq
    ET.SubElement(url, "priority").text = priority


def blog_posts() -> list[tuple[str, str | None]]:
    data = load_json(ROOT / "posts" / "data" / "index.json")
    if not data:
        return []
    seen: set[str] = set()
    posts: list[tuple[str, str | None]] = []
    for post in data.get("posts", []):
        slug = (post.get("slug") or "").strip()
        if not slug or slug in seen:
            continue
        seen.add(slug)
        posts.append((slug, post.get("date")))
    return posts


def congress_events() -> list[tuple[str, str | None]]:
    data = load_json(ROOT / "congress" / "data" / "index.json")
    if not data:
        return []
    events: list[tuple[str, str | None]] = []
    for event in data.get("events", []):
        slug = (event.get("slug") or "").strip()
        if not slug:
            continue
        events.append((slug, event.get("date")))
    return events


def build_sitemap() -> str:
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for path, changefreq, priority in STATIC_PAGES:
        add_url(urlset, path, changefreq, priority)

    for slug, lastmod in blog_posts():
        add_url(urlset, f"blog/{slug}/", "yearly", "0.7", lastmod)

    for slug, lastmod in congress_events():
        add_url(urlset, f"congress/{slug}/", "yearly", "0.7", lastmod)

    ET.indent(urlset, space="  ")
    xml = ET.tostring(urlset, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml + "\n"


def main() -> int:
    content = build_sitemap()
    OUT.write_text(content, encoding="utf-8")
    url_count = content.count("<loc>")
    print(f"Wrote {OUT.relative_to(ROOT)} ({url_count} URLs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
