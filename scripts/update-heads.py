#!/usr/bin/env python3
"""Update HTML heads: bundled CSS, analytics at end of body."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD_HEAD = re.compile(
    r"\s*<link rel=\"preconnect\" href=\"https://fonts\.googleapis\.com\">.*?<script src=\"/assets/js/analytics\.js\"></script>",
    re.S,
)

OLD_HEAD_NO_ANALYTICS = re.compile(
    r"\s*<link rel=\"preconnect\" href=\"https://fonts\.googleapis\.com\">.*?<link rel=\"stylesheet\" href=\"/assets/css/pages\.css\">",
    re.S,
)

INNER_HEAD = (
    '  <link rel="stylesheet" href="/assets/css/site.bundle.css">\n'
    '  <link rel="stylesheet" href="/assets/css/pages.css">\n'
    '  <link rel="icon" href="/assets/images/brand/favicon.svg" type="image/svg+xml">'
)

HOME_HEAD = (
    '  <link rel="preload" as="image" href="/assets/images/home/hero.webp" fetchpriority="high">\n'
    '  <link rel="stylesheet" href="/assets/css/site.bundle.css">\n'
    '  <link rel="stylesheet" href="/assets/css/home.css">\n'
    '  <link rel="icon" href="/assets/images/brand/favicon.svg" type="image/svg+xml">'
)

ANALYTICS = '  <script src="/assets/js/analytics.js" defer></script>\n'


def patch_file(path: Path, is_home: bool = False) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    if is_home:
        text = re.sub(
            r"\s*<link rel=\"preconnect\" href=\"https://fonts\.googleapis\.com\">.*?<link rel=\"icon\"[^>]+>",
            "\n" + HOME_HEAD,
            text,
            count=1,
            flags=re.S,
        )
    else:
        if 'href="/assets/css/site.bundle.css"' in text:
            pass
        elif '<script src="/assets/js/analytics.js"></script>' in text:
            text = OLD_HEAD.sub("\n" + INNER_HEAD, text, count=1)
        else:
            text = OLD_HEAD_NO_ANALYTICS.sub("\n" + INNER_HEAD, text, count=1)

    text = text.replace('<script src="/assets/js/analytics.js"></script>', "")
    if ANALYTICS.strip() not in text:
        text = text.replace("</body>", ANALYTICS + "</body>")

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    count = 0
    if patch_file(ROOT / "index.html", is_home=True):
        count += 1
        print("  index.html")

    for path in ROOT.rglob("*.html"):
        if path.name.startswith("_"):
            continue
        if path.parent.name == "PLAYGROUND":
            continue
        if path.name == "index.html" and path.parent == ROOT:
            continue
        if path.name == "head-links.html":
            continue
        if 'fonts.googleapis.com' in path.read_text(encoding="utf-8"):
            if patch_file(path):
                count += 1
                print(f"  {path.relative_to(ROOT)}")

    head_links = ROOT / "components" / "head-links.html"
    head_links.write_text(INNER_HEAD.strip() + "\n", encoding="utf-8")
    print("  components/head-links.html")
    print(f"\nUpdated {count} page(s).")


if __name__ == "__main__":
    main()
