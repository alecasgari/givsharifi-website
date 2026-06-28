#!/usr/bin/env python3
"""
Remove one image from the public gallery.

Usage:
  python scripts/delete-gallery-image.py prof-giv-sharifi-neurosurgery-microscope-operating-room
  python scripts/delete-gallery-image.py --dry-run my-slug
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets" / "data" / "gallery.json"
GALLERY = ROOT / "assets" / "images" / "gallery"


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove a gallery image by slug")
    parser.add_argument("slug", help="Image slug from gallery.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not DATA.is_file():
        print("gallery.json not found")
        return 1

    gallery = json.loads(DATA.read_text(encoding="utf-8"))
    images = gallery.get("images", [])
    match = next((img for img in images if img.get("slug") == args.slug), None)
    if not match:
        print(f"Slug not found in gallery.json: {args.slug}")
        return 1

    paths = []
    for key in ("file", "thumb", "strip"):
        rel = match.get(key)
        if rel:
            paths.append(ROOT / rel)

    print(f"Remove: {match.get('title') or args.slug}")
    for path in paths:
        print(f"  delete {path.relative_to(ROOT)}" if path.exists() else f"  skip (missing) {path.relative_to(ROOT)}")

    if args.dry_run:
        return 0

    gallery["images"] = [img for img in images if img.get("slug") != args.slug]
    gallery["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    DATA.write_text(json.dumps(gallery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for path in paths:
        if path.is_file():
            path.unlink()

    print(f"\nRemoved {args.slug}. Commit gallery.json + deleted files, then push.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
