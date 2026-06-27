#!/usr/bin/env python3
"""List referenced images and sizes."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pat = re.compile(r"/assets/images/[^\s\"'\\)>]+")

refs = set()
for p in ROOT.rglob("*"):
    if p.suffix not in {".html", ".js", ".json", ".css", ".xml"}:
        continue
    if "PLAYGROUND" in p.parts:
        continue
    try:
        refs.update(pat.findall(p.read_text(encoding="utf-8", errors="ignore")))
    except OSError:
        pass

print(f"{len(refs)} referenced paths\n")
for r in sorted(refs):
    fp = ROOT / r.lstrip("/")
    if fp.exists():
        print(f"{fp.stat().st_size // 1024:4} KB  {r}")
    else:
        print(f" MISS  {r}")
