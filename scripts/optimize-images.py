#!/usr/bin/env python3
"""
Optimize all raster images under assets/images/.
- Recompress WebP in place
- Convert PNG/JPEG to WebP (updates references when path changes)
- Downscale if wider than usage max or filename dimension hint
"""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"
RASTER = {".webp", ".png", ".jpg", ".jpeg"}
SKIP_MIN_BYTES = 8 * 1024  # skip tiny webp already
WEBP_QUALITY = 80

USAGE_MAX: dict[str, int] = {
    "/assets/images/home/hero.webp": 1600,
    "/assets/images/home/about-giv.webp": 720,
    "/assets/images/home/service-physio.webp": 180,
    "/assets/images/home/service-pituitary.webp": 180,
    "/assets/images/home/service-spine.webp": 180,
    "/assets/images/home/service-brain.webp": 180,
    "/assets/images/icons/worldwide.webp": 150,
    "/assets/images/services/medical-tourism/hero.webp": 1100,
    "/assets/images/home/video-poster-cyst.webp": 768,
    "/assets/images/services/brain-surgery/hero.webp": 854,
    "/assets/images/services/spinal-surgery/care.webp": 854,
    "/assets/images/services/pituitary-surgery/hero.webp": 854,
    "/assets/images/home/og-share.webp": 1200,
    "/assets/images/blog/minimally-invasive-neurosurgery.webp": 900,
    "/assets/images/blog/ai-and-robotics.webp": 900,
    "/assets/images/blog/non-invasive-neurosurgery.webp": 900,
    "/assets/images/blog/future-of-spinal-surgery.webp": 900,
    "/assets/images/blog/pediatric-neurosurgery.webp": 900,
    "/assets/images/blog/future-of-brain-surgery.webp": 900,
    "/assets/images/blog/spinal-cord-injuries.webp": 900,
    "/assets/images/services/spinal-surgery/hero.webp": 1600,
    "/assets/images/services/medical-tourism/gallery-1.webp": 1024,
    "/assets/images/services/medical-tourism/gallery-2.webp": 1024,
    "/assets/images/services/pituitary-surgery/surgery.webp": 1024,
    "/assets/images/services/brain-surgery/team.webp": 768,
    "/assets/images/services/physiotherapy/hero.webp": 1600,
}


def collect_references() -> set[str]:
    pat = re.compile(r"/assets/images/[^\s\"'\\)>]+")
    refs: set[str] = set()
    for p in ROOT.rglob("*"):
        if p.suffix not in {".html", ".js", ".json", ".css", ".xml"}:
            continue
        if "PLAYGROUND" in p.parts:
            continue
        try:
            refs.update(pat.findall(p.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            pass
    return refs


def path_to_ref(path: Path) -> str:
    return "/" + path.relative_to(ROOT).as_posix()


def infer_max_width(path: Path, ref: str | None) -> int | None:
    if ref and ref in USAGE_MAX:
        return USAGE_MAX[ref]
    m = re.search(r"-(\d+)x\d+$", path.stem)
    if m:
        return int(m.group(1))
    if path.stat().st_size < SKIP_MIN_BYTES:
        return None
    return 1400


def save_webp(im: Image.Image, quality: int = WEBP_QUALITY) -> bytes:
    buf = BytesIO()
    if im.mode == "RGBA":
        im.save(buf, format="WEBP", quality=quality, method=6)
    else:
        if im.mode != "RGB":
            im = im.convert("RGB")
        im.save(buf, format="WEBP", quality=quality, method=6)
    return buf.getvalue()


def optimize_file(path: Path, max_w: int | None) -> tuple[int, int, Path]:
    before = path.stat().st_size
    suffix = path.suffix.lower()

    with Image.open(path) as im:
        im.load()
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        if has_alpha:
            im = im.convert("RGBA")
        elif im.mode != "RGB":
            im = im.convert("RGB")

        w, h = im.size
        if max_w and w > max_w:
            im = im.resize((max_w, round(h * max_w / w)), Image.Resampling.LANCZOS)

        data = save_webp(im)

    out = path.with_suffix(".webp")
    if len(data) >= before and suffix == ".webp" and (max_w is None or w <= (max_w or w)):
        return before, before, path

    out.write_bytes(data)
    if suffix != ".webp":
        path.unlink(missing_ok=True)
    return before, len(data), out


def update_references(old: str, new: str) -> int:
    if old == new:
        return 0
    n = 0
    for p in ROOT.rglob("*"):
        if p.suffix not in {".html", ".js", ".json", ".css", ".xml"}:
            continue
        if "PLAYGROUND" in p.parts:
            continue
        text = p.read_text(encoding="utf-8")
        if old in text:
            p.write_text(text.replace(old, new), encoding="utf-8")
            n += 1
    return n


def main() -> None:
    refs = collect_references()
    ref_by_path = {ROOT / r.lstrip("/"): r for r in refs if not r.endswith((".svg", ".json"))}

    total_before = 0
    total_after = 0
    count = 0
    ref_updates = 0

    for path in sorted(IMAGES.rglob("*")):
        if path.suffix.lower() not in RASTER:
            continue
        ref = ref_by_path.get(path) or path_to_ref(path)
        is_used = path in ref_by_path or path_to_ref(path) in refs

        if not is_used and path.suffix.lower() == ".webp" and path.stat().st_size < SKIP_MIN_BYTES:
            continue

        max_w = infer_max_width(path, ref if is_used else None)
        try:
            before, after, out = optimize_file(path, max_w)
        except Exception as exc:
            print(f"SKIP {path.relative_to(IMAGES)}: {exc}")
            continue

        old_ref = path_to_ref(path) if path.exists() else ref
        new_ref = path_to_ref(out)
        if old_ref != new_ref:
            ref_updates += update_references(old_ref, new_ref)

        if after < before * 0.97 or path.suffix.lower() != ".webp":
            saved = before - after
            total_before += before
            total_after += after
            count += 1
            if saved > 500 or path.suffix.lower() != ".webp":
                rel = str(out.relative_to(IMAGES)).encode("ascii", "replace").decode()
                print(f"{before // 1024:4} -> {after // 1024:4} KB  {rel}")

    print(f"\nOptimized {count} files")
    print(f"Total saved: {(total_before - total_after) // 1024} KB ({total_before // 1024} -> {total_after // 1024} KB)")
    if ref_updates:
        print(f"Reference updates: {ref_updates}")


if __name__ == "__main__":
    main()
