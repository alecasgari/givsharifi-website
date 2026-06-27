#!/usr/bin/env python3
"""Flatten pages/ to site root for GitHub Pages deploy (preserves indexed URLs)."""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"

PUBLISH_DIRS = (
    "brain-surgery",
    "spinal-surgery",
    "endoscopic-pituitary-surgery",
    "physiotherapy",
    "medical-tourism",
    "publications",
    "videos",
    "gallery",
    "done",
)


SKIP_NAMES = frozenset({"README.md"})


def should_publish(rel: Path) -> bool:
    if rel.name in SKIP_NAMES:
        return False
    if any(part.startswith("_") for part in rel.parts):
        return False
    return True


def main() -> int:
    import subprocess

    bundle = ROOT / "scripts" / "bundle-css.py"
    if bundle.is_file():
        subprocess.run([sys.executable, str(bundle)], check=True)

    fix_paths = ROOT / "scripts" / "fix-site-paths.py"
    if fix_paths.is_file():
        subprocess.run([sys.executable, str(fix_paths)], check=True)

    if not PAGES.is_dir():
        print("pages/ folder not found", file=sys.stderr)
        return 1

    for name in PUBLISH_DIRS:
        target = ROOT / name
        if target.exists():
            if name == "publications" and (target / "data").is_dir():
                # Keep publications/data/index.json — only replace page files from pages/
                for child in target.iterdir():
                    if child.name != "data":
                        if child.is_dir():
                            shutil.rmtree(child)
                        else:
                            child.unlink()
            else:
                shutil.rmtree(target)

    root_404 = ROOT / "404.html"
    if root_404.exists():
        root_404.unlink()

    count = 0
    for src in sorted(PAGES.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(PAGES)
        if not should_publish(rel):
            continue
        dest = ROOT / "404.html" if rel.name == "404.html" else ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"  {rel} -> {dest.relative_to(ROOT)}")
        count += 1

    print(f"\nPublished {count} file(s) from pages/ to site root.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
