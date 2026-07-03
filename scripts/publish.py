#!/usr/bin/env python3
"""Flatten pages/ to site root for GitHub Pages deploy (preserves indexed URLs)."""

import json
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

SITE_ROOT_FILES = ("index.html", "404.html", "CNAME", "robots.txt", "sitemap.xml")
SITE_DIRS = (
    "assets",
    "blog",
    "components",
    *PUBLISH_DIRS,
)
SITE_OUTPUT = ROOT / "_site"


def should_publish(rel: Path) -> bool:
    if rel.name in SKIP_NAMES:
        return False
    if any(part.startswith("_") for part in rel.parts):
        return False
    return True


def sync_blog_post_shells() -> int:
    """Copy _post-shell.html to blog/{slug}/index.html for every post in index.json."""
    shell_src = ROOT / "blog" / "_post-shell.html"
    index_path = ROOT / "posts" / "data" / "index.json"
    if not shell_src.is_file() or not index_path.is_file():
        return 0
    shell = shell_src.read_text(encoding="utf-8")
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("posts/data/index.json invalid JSON", file=sys.stderr)
        return 0
    created = 0
    for post in index.get("posts", []):
        slug = post.get("slug")
        if not slug:
            continue
        dest = ROOT / "blog" / slug / "index.html"
        if dest.is_file():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(shell, encoding="utf-8")
        print(f"  blog shell: {dest.relative_to(ROOT)}")
        created += 1
    return created


def copy_tree(src: Path, dest: Path) -> int:
    """Copy file or directory tree; return number of files copied."""
    if not src.exists():
        return 0
    count = 0
    if src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return 1
    for item in sorted(src.rglob("*")):
        if not item.is_file():
            continue
        rel = item.relative_to(src)
        if any(part.startswith("_") for part in rel.parts):
            continue
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, out)
        count += 1
    return count


def copy_posts_data(dest_root: Path) -> int:
    """Copy published post JSON only (exclude _drafts/)."""
    src = ROOT / "posts" / "data"
    if not src.is_dir():
        return 0
    count = 0
    for item in sorted(src.glob("*.json")):
        out = dest_root / "posts" / "data" / item.name
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, out)
        count += 1
    return count


def build_pages_artifact() -> int:
    """Stage a slim GitHub Pages artifact (no n8n, drafts, or source pages/)."""
    if SITE_OUTPUT.exists():
        shutil.rmtree(SITE_OUTPUT)
    SITE_OUTPUT.mkdir(parents=True)

    count = 0
    for name in SITE_ROOT_FILES:
        count += copy_tree(ROOT / name, SITE_OUTPUT / name)
    for name in SITE_DIRS:
        count += copy_tree(ROOT / name, SITE_OUTPUT / name)
    count += copy_posts_data(SITE_OUTPUT)

    (SITE_OUTPUT / ".nojekyll").write_text("", encoding="utf-8")
    count += 1
    print(f"\nStaged {count} file(s) in {SITE_OUTPUT.relative_to(ROOT)}/ for GitHub Pages.")
    return count


def main() -> int:
    import subprocess

    bundle = ROOT / "scripts" / "bundle-css.py"
    if bundle.is_file():
        subprocess.run([sys.executable, str(bundle)], check=True)

    fix_paths = ROOT / "scripts" / "fix-site-paths.py"
    if fix_paths.is_file():
        subprocess.run([sys.executable, str(fix_paths)], check=True)

    shells = sync_blog_post_shells()
    if shells:
        print(f"\nCreated {shells} missing blog post shell(s).")

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
    build_pages_artifact()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
