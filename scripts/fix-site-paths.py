#!/usr/bin/env python3
"""Insert site-base bootstrap and convert root-absolute paths to base-relative paths."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SITE_BASE_BLOCK = """<base href='/' id="site-base">
  <script>
(function(){var b=document.getElementById('site-base');var r='/';if(/\\.github\\.io$/i.test(location.hostname)){var s=location.pathname.split('/').filter(Boolean)[0];if(s)r='/'+s+'/';b.href=r;}window.__SITE_ROOT__=r;window.siteUrl=function(p){if(p==null||p==='')return r;if(/^https?:\\/\\//i.test(p)||p.startsWith('tel:')||p.startsWith('mailto:'))return p;return r+String(p).replace(/^\\//,'');};})();
</script>"""

OLD_BASE_SCRIPT = re.compile(
    r'<base href=["\']/?["\'] id="site-base">\s*<script>\s*\(function\(\)\{var b=document\.getElementById\(\'site-base\'\);.*?\}\)\(\);\s*</script>',
    re.DOTALL,
)
BROKEN_BASE = re.compile(
    r'<base href="\./" id="site-base">\s*<script>\s*\(function\(\)\{var b=document\.getElementById\(\'site-base\'\);.*?\}\)\(\);\s*</script>',
    re.DOTALL,
)

GLOBS = (
    ROOT / "index.html",
    ROOT / "pages",
    ROOT / "blog",
    ROOT / "components",
)

ROOT_ATTR = re.compile(r'\b(href|src|action|poster)="/(?![/])')
HOME_HREF = re.compile(r'\bhref="/"')


def fix_html(text: str) -> str:
    if BROKEN_BASE.search(text) or OLD_BASE_SCRIPT.search(text):
        text = BROKEN_BASE.sub(SITE_BASE_BLOCK, text, count=1)
        text = OLD_BASE_SCRIPT.sub(SITE_BASE_BLOCK, text, count=1)
    elif 'id="site-base"' not in text and 'window.__SITE_ROOT__' not in text:
        marker = '<meta charset="UTF-8">'
        if marker in text:
            text = text.replace(marker, marker + "\n  " + SITE_BASE_BLOCK, 1)
        else:
            text = text.replace("<head>", "<head>\n  " + SITE_BASE_BLOCK, 1)

    text = HOME_HREF.sub('href="./"', text)
    text = ROOT_ATTR.sub(r'\1="', text)
    return text


def main() -> int:
    count = 0
    paths: list[Path] = []
    for item in GLOBS:
        if item.is_file():
            paths.append(item)
        elif item.is_dir():
            paths.extend(sorted(item.rglob("*.html")))

    for path in paths:
        if path.name.startswith("_") and path.name != "_post-shell.html":
            continue
        original = path.read_text(encoding="utf-8")
        updated = fix_html(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"  fixed {path.relative_to(ROOT)}")
            count += 1

    print(f"\nUpdated {count} HTML file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
