#!/usr/bin/env python3
"""Download self-hosted font files from Google Fonts CSS (latin subset)."""

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "assets" / "fonts"
FONTS.mkdir(parents=True, exist_ok=True)

CSS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&"
    "family=Outfit:wght@400;500;600&display=swap"
)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

OUTFIT_MAP = {
    ("normal", "400"): "outfit-400.woff2",
    ("normal", "500"): "outfit-500.woff2",
    ("normal", "600"): "outfit-600.woff2",
}
CORMORANT_MAP = {
    ("normal", "500"): "cormorant-500.woff2",
    ("normal", "600"): "cormorant-600.woff2",
    ("normal", "700"): "cormorant-700.woff2",
    ("italic", "500"): "cormorant-500-italic.woff2",
}


def parse_blocks(css: str) -> list[dict]:
    blocks = []
    parts = re.split(r"/\*\s*([^*]+)\s*\*/", css)
    for i in range(1, len(parts), 2):
        comment = parts[i].strip().lower()
        block = parts[i + 1] if i + 1 < len(parts) else ""
        if "latin" not in comment or "latin-ext" in comment:
            continue
        family_m = re.search(r"font-family:\s*'([^']+)'", block)
        style_m = re.search(r"font-style:\s*(\w+)", block)
        weight_m = re.search(r"font-weight:\s*(\d+)", block)
        url_m = re.search(r"url\((https://[^)]+\.woff2)\)", block)
        if family_m and style_m and weight_m and url_m:
            blocks.append(
                {
                    "family": family_m.group(1),
                    "style": style_m.group(1),
                    "weight": weight_m.group(1),
                    "url": url_m.group(1),
                }
            )
    return blocks


def main() -> None:
    req = urllib.request.Request(CSS_URL, headers={"User-Agent": UA})
    css = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    blocks = parse_blocks(css)
    seen = set()

    for block in blocks:
        key = (block["style"], block["weight"])
        if block["family"] == "Outfit":
            fname = OUTFIT_MAP.get(key)
        elif block["family"] == "Cormorant Garamond":
            fname = CORMORANT_MAP.get(key)
        else:
            continue
        if not fname or fname in seen:
            continue
        seen.add(fname)
        dest = FONTS / fname
        data = urllib.request.urlopen(block["url"], timeout=30).read()
        dest.write_bytes(data)
        print(f"  {fname} ({len(data) // 1024} KB)")

    missing = [
        f
        for f in sorted(set(OUTFIT_MAP.values()) | set(CORMORANT_MAP.values()))
        if not (FONTS / f).exists() or (FONTS / f).stat().st_size < 1000
    ]
    if missing:
        raise SystemExit(f"Missing fonts: {', '.join(missing)}")


if __name__ == "__main__":
    main()
