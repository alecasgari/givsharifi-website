#!/usr/bin/env python3
"""Remove the repeated YMYL boilerplate paragraph from blog JSON files."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts" / "data"

BOILERPLATE = (
    "In real clinical practice, treatment choice depends on MRI findings, "
    "neurological exam, and risk profile in Dubai and Tehran. Your neurosurgeon "
    "will explain alternatives, expected recovery timeline, and follow-up imaging "
    "requirements before final decisions are made. This balanced approach improves "
    "safety, aligns expectations for patients and families, and avoids over-promising outcomes."
)

BOILER_RE = re.compile(
    r"In real clinical practice, treatment choice depends on MRI findings, "
    r"neurological exam, and risk profile[^.]*\.\s*"
    r"Your neurosurgeon will explain alternatives, expected recovery timeline, "
    r"and follow-up imaging requirements before final decisions are made\.\s*"
    r"This balanced approach improves safety, aligns expectations for patients "
    r"and families, and avoids over-promising outcomes\.\s*",
    re.I,
)


def clean_text(text: str) -> str:
    out = BOILER_RE.sub("", text)
    return re.sub(r"\s{2,}", " ", out).strip()


def clean_value(value):
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, list):
        cleaned = [clean_value(item) for item in value]
        out = []
        for item in cleaned:
            if isinstance(item, dict) and item.get("type") == "paragraph" and not (item.get("text") or "").strip():
                continue
            if item == "" or item == []:
                continue
            out.append(item)
        return out
    if isinstance(value, dict):
        return {k: clean_value(v) for k, v in value.items()}
    return value


def main() -> int:
    changed = 0
    for path in sorted(POSTS.rglob("*.json")):
        if path.name == "index.json":
            continue
        raw = path.read_text(encoding="utf-8")
        if "In real clinical practice, treatment choice depends on MRI findings" not in raw:
            continue
        data = json.loads(raw)
        cleaned = clean_value(data)
        path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  cleaned {path.relative_to(ROOT)}")
        changed += 1
    print(f"Removed boilerplate from {changed} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
