#!/usr/bin/env python3
"""Audit image references and inventory assets/images."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"
pat = re.compile(r"/assets/images/[^\s\"'\\)>]+")

refs: set[str] = set()
for p in ROOT.rglob("*"):
    if p.suffix not in {".html", ".js", ".json", ".css", ".xml", ".md", ".py"}:
        continue
    if "PLAYGROUND" in p.parts or p.name == "audit-images.py":
        continue
    try:
        refs.update(pat.findall(p.read_text(encoding="utf-8", errors="ignore")))
    except OSError:
        pass

refs = {r for r in refs if not r.endswith((".json",)) or "83707" not in r}
refs_no_svg_only = refs

all_raster = []
all_files = []
for fp in IMAGES.rglob("*"):
    if fp.is_file():
        all_files.append(fp)
        if fp.suffix.lower() in {".webp", ".png", ".jpg", ".jpeg", ".gif"}:
            all_raster.append(fp)

def to_ref(fp: Path) -> str:
    return "/" + fp.relative_to(ROOT).as_posix()

ref_paths = {ROOT / r.lstrip("/") for r in refs}
used_files = {fp for fp in all_files if to_ref(fp) in refs or fp in ref_paths}

# Also match if any ref is same basename in different path (shouldn't happen)
print(f"Referenced URLs: {len(refs)}")
print(f"Total image files: {len(all_files)}")
print(f"Used files: {len(used_files)}")
print(f"Unused files: {len(all_files) - len(used_files)}")
print("\n=== REFERENCED ===")
for r in sorted(refs):
    fp = ROOT / r.lstrip("/")
    kb = fp.stat().st_size // 1024 if fp.exists() else -1
    print(f"{kb:4} KB  {r}")

print("\n=== UNUSED (sample, first 30) ===")
unused = [fp for fp in all_files if fp not in used_files and fp.suffix.lower() != ".json"]
unused.sort(key=lambda p: p.stat().st_size, reverse=True)
for fp in unused[:30]:
    print(f"{fp.stat().st_size // 1024:4} KB  {fp.relative_to(IMAGES)}")

print(f"\n... and {max(0, len(unused) - 30)} more unused files")
print(f"Unused total size: {sum(f.stat().st_size for f in unused) // (1024*1024)} MB")
