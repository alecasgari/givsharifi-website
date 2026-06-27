#!/usr/bin/env python3
"""Concatenate core CSS into site.bundle.css (single render-blocking request)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "assets" / "css"
PARTS = (
    "fonts.css",
    "variables.css",
    "base.css",
    "theme.css",
    "layout.css",
    "components.css",
)
OUT = CSS / "site.bundle.css"


def main() -> None:
    chunks = []
    for name in PARTS:
        path = CSS / name
        chunks.append(f"/* === {name} === */\n")
        chunks.append(path.read_text(encoding="utf-8"))
        chunks.append("\n")
    OUT.write_text("".join(chunks), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
