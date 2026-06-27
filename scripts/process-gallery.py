#!/usr/bin/env python3
"""
Process raw gallery photos from assets/images/gallery/_incoming/
→ optimized WebP in assets/images/gallery/
→ assets/data/gallery.json

Usage:
  python scripts/process-gallery.py
  python scripts/process-gallery.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
INCOMING = ROOT / "assets" / "images" / "gallery" / "_incoming"
OUT_DIR = ROOT / "assets" / "images" / "gallery"
PROCESSED = ROOT / "assets" / "images" / "gallery" / "_processed"
DATA = ROOT / "assets" / "data" / "gallery.json"
MANIFEST = INCOMING / "manifest.json"
RASTER = {".jpg", ".jpeg", ".png", ".webp"}
MAX_WIDTH = 1400
THUMB_WIDTH = 640
WEBP_QUALITY = 82


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80] or "gallery-image"


def load_manifest() -> dict:
    if not MANIFEST.is_file():
        return {}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def load_gallery() -> dict:
    if DATA.is_file():
        return json.loads(DATA.read_text(encoding="utf-8"))
    return {"updated": "", "images": []}


def save_webp(im: Image.Image, quality: int = WEBP_QUALITY) -> bytes:
    buf = BytesIO()
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        im.save(buf, format="WEBP", quality=quality, method=6)
    else:
        im = im.convert("RGB")
        im.save(buf, format="WEBP", quality=quality, method=6)
    return buf.getvalue()


def resize(im: Image.Image, max_w: int) -> Image.Image:
    w, h = im.size
    if w <= max_w:
        return im
    return im.resize((max_w, round(h * max_w / w)), Image.Resampling.LANCZOS)


def unique_slug(base: str, existing: set[str]) -> str:
    slug = base
    n = 2
    while slug in existing:
        slug = f"{base}-{n}"
        n += 1
    return slug


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest()
    gallery = load_gallery()
    existing_slugs = {img["slug"] for img in gallery.get("images", []) if img.get("slug")}

    sources = sorted(
        p for p in INCOMING.iterdir() if p.is_file() and p.suffix.lower() in RASTER
    )
    if not sources:
        print("No images in assets/images/gallery/_incoming/")
        print("Drop JPG/PNG files there, then run again.")
        return 0

    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    new_entries = []

    for src in sources:
        meta = manifest.get(src.name, {})
        alt = (meta.get("alt") or "").strip()
        title = (meta.get("title") or alt or src.stem).strip()
        if not alt:
            alt = f"Prof. Giv Sharifi neurosurgery — {title}"

        base_slug = slugify(meta.get("slug") or title or src.stem)
        slug = unique_slug(base_slug, existing_slugs)
        existing_slugs.add(slug)

        out_main = OUT_DIR / f"{slug}.webp"
        out_thumb = OUT_DIR / f"{slug}-thumb.webp"

        print(f"  {src.name} -> {slug}.webp")

        if args.dry_run:
            continue

        with Image.open(src) as im:
            im.load()
            main_im = resize(im, MAX_WIDTH)
            thumb_im = resize(im, THUMB_WIDTH)
            out_main.write_bytes(save_webp(main_im))
            out_thumb.write_bytes(save_webp(thumb_im, quality=78))

        w, h = main_im.size
        tw, th = thumb_im.size

        new_entries.append(
            {
                "slug": slug,
                "file": f"assets/images/gallery/{slug}.webp",
                "thumb": f"assets/images/gallery/{slug}-thumb.webp",
                "alt": alt,
                "title": title,
                "category": meta.get("category") or "Gallery",
                "featured": bool(meta.get("featured", False)),
                "width": w,
                "height": h,
            }
        )

        shutil.move(str(src), str(PROCESSED / src.name))

    if args.dry_run:
        print(f"\nDry run: {len(sources)} image(s) would be processed.")
        return 0

    if new_entries:
        gallery.setdefault("images", []).extend(new_entries)
        gallery["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        DATA.write_text(json.dumps(gallery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nAdded {len(new_entries)} image(s). Updated {DATA.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
