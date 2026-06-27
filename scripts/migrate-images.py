#!/usr/bin/env python3
"""Reorganize assets/images: move used files, update refs, delete legacy WP tree."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"

# old URL -> new URL (semantic paths)
MOVES: dict[str, str] = {
    # brand
    "/assets/images/2023/03/aaa.svg": "/assets/images/brand/favicon.svg",
    "/assets/images/2023/03/Main-AI-White-SVG.svg": "/assets/images/brand/logo.svg",
    # icons
    "/assets/images/2023/03/expertise.svg": "/assets/images/icons/expertise.svg",
    "/assets/images/2023/03/idea-exchange.svg": "/assets/images/icons/idea-exchange.svg",
    "/assets/images/2023/03/worldwide-150x150.webp": "/assets/images/icons/worldwide.webp",
    # blog
    "/assets/images/2023/04/GS-Website.webp": "/assets/images/blog/future-of-spinal-surgery.webp",
    "/assets/images/2023/05/image-21.webp": "/assets/images/blog/ai-and-robotics.webp",
    "/assets/images/2023/05/image-57.webp": "/assets/images/blog/non-invasive-neurosurgery.webp",
    "/assets/images/2023/05/image-33.webp": "/assets/images/blog/minimally-invasive-neurosurgery.webp",
    "/assets/images/2023/04/GS-Website-1.webp": "/assets/images/blog/pediatric-neurosurgery.webp",
    "/assets/images/2023/04/The-Future-of-Brain-Surgery.webp": "/assets/images/blog/future-of-brain-surgery.webp",
    "/assets/images/2023/04/Understanding-Spinal-Cord-Injuries-and-Neurosurgical-Treatments.webp": "/assets/images/blog/spinal-cord-injuries.webp",
    # home
    "/assets/images/2024/04/image-2.webp": "/assets/images/home/hero.webp",
    "/assets/images/2023/03/Giv.webp": "/assets/images/home/about-giv.webp",
    "/assets/images/2023/03/Group-18.webp": "/assets/images/home/service-brain.webp",
    "/assets/images/2023/03/Group-17.webp": "/assets/images/home/service-spine.webp",
    "/assets/images/2023/03/Group-16.webp": "/assets/images/home/service-pituitary.webp",
    "/assets/images/2023/03/Group-15.webp": "/assets/images/home/service-physio.webp",
    "/assets/images/2023/05/image-28.webp": "/assets/images/home/og-share.webp",
    "/assets/images/2024/04/image-3-768x512.webp": "/assets/images/home/video-poster-cyst.webp",
    # services
    "/assets/images/2023/05/image-24.webp": "/assets/images/services/brain-surgery/hero.webp",
    "/assets/images/2024/04/AG9A8700-768x512.webp": "/assets/images/services/brain-surgery/team.webp",
    "/assets/images/2024/06/IMG-20230619-WA0022.webp": "/assets/images/services/spinal-surgery/hero.webp",
    "/assets/images/2023/05/image-25.webp": "/assets/images/services/spinal-surgery/care.webp",
    "/assets/images/2023/05/image-27.webp": "/assets/images/services/pituitary-surgery/hero.webp",
    "/assets/images/2024/06/image-16-1024x682.webp": "/assets/images/services/pituitary-surgery/surgery.webp",
    "/assets/images/2023/05/pexels-yan-krukau-5794048.webp": "/assets/images/services/physiotherapy/hero.webp",
    "/assets/images/2024/06/looking-for-1.webp": "/assets/images/services/medical-tourism/hero.webp",
    "/assets/images/2024/06/image-14-1024x678.webp": "/assets/images/services/medical-tourism/gallery-1.webp",
    "/assets/images/2024/06/image-15-1024x680.webp": "/assets/images/services/medical-tourism/gallery-2.webp",
}

SKIP_DIRS = {"PLAYGROUND"}
TEXT_EXT = {".html", ".js", ".json", ".css", ".xml", ".md", ".py"}
LEGACY_DIRS = ("2023", "2024", "2025")


def move_files() -> None:
    for old_url, new_url in MOVES.items():
        src = ROOT / old_url.lstrip("/")
        dest = ROOT / new_url.lstrip("/")
        if not src.is_file():
            raise FileNotFoundError(f"Missing source: {src}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"  {dest.relative_to(IMAGES)}")


def update_references() -> int:
    files_changed = 0
    # longest paths first to avoid partial replacements
    pairs = sorted(MOVES.items(), key=lambda x: len(x[0]), reverse=True)
    for path in ROOT.rglob("*"):
        if path.suffix not in TEXT_EXT:
            continue
        if SKIP_DIRS & set(path.parts):
            continue
        if path.name in ("migrate-images.py", "audit-images.py", "optimize-images.py"):
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in pairs:
            text = text.replace(old, new)
            # full canonical URLs in meta/schema
            text = text.replace(
                "https://www.givsharifi.com" + old,
                "https://www.givsharifi.com" + new,
            )
        if text != original:
            path.write_text(text, encoding="utf-8")
            files_changed += 1
            print(f"  updated {path.relative_to(ROOT)}")
    return files_changed


def remove_legacy() -> None:
    for name in LEGACY_DIRS:
        legacy = IMAGES / name
        if legacy.exists():
            shutil.rmtree(legacy)
            print(f"  removed {legacy.relative_to(ROOT)}")


def main() -> None:
    print("Copying files to new structure...")
    move_files()
    print("\nUpdating references...")
    n = update_references()
    print(f"\nRemoving legacy folders...")
    remove_legacy()
    remaining = list(IMAGES.rglob("*"))
    file_count = sum(1 for p in remaining if p.is_file())
    print(f"\nDone. {file_count} files in assets/images/, {n} text files updated.")


if __name__ == "__main__":
    main()
