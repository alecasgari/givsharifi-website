#!/usr/bin/env python3
"""Build assets/data/video-library.json from video/library/*.info.json (yt-dlp)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "video" / "library"
OUT = ROOT / "assets" / "data" / "video-library.json"

# Preserve display order (newest Instagram reels first)
ORDER = [
    "DZ455nVtZ30",
    "DSVeg6sDVL0",
    "DSSIaiVjbg7",
    "DSCLtu8De9d",
    "DSAHZOojaFD",
    "DRmRS5IDT3h",
    "DRH6wYfjHfx",
    "DQl4VOejdFv",
    "DQT7SyljbrE",
]


def clean_description(text: str, max_len: int = 160) -> str:
    if not text:
        return ""
    line = text.strip().split("\n")[0].strip()
    line = re.sub(r"#\S+", "", line).strip()
    line = re.sub(r"\s+", " ", line)
    if len(line) > max_len:
        line = line[: max_len - 1].rstrip() + "…"
    return line


def title_from_meta(data: dict) -> str:
    desc = clean_description(data.get("description") or "", 80)
    if desc:
        return desc
    title = (data.get("title") or "").strip()
    if title and title != "Video by dr.guive.sharifi":
        return title
    vid = data.get("id") or "reel"
    return f"Neurosurgery reel — {vid}"


def main() -> int:
    by_id: dict[str, dict] = {}
    for path in sorted(LIBRARY.glob("*.info.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        vid = data.get("id") or path.stem.replace(".info", "")
        mp4 = LIBRARY / f"{vid}.mp4"
        if not mp4.is_file():
            print(f"  skip {vid}: missing {mp4.name}")
            continue
        upload_date = data.get("upload_date") or ""
        if len(upload_date) == 8:
            date_iso = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
        else:
            date_iso = ""
        by_id[vid] = {
            "id": vid,
            "file": f"{vid}.mp4",
            "title": title_from_meta(data),
            "description": clean_description(data.get("description") or ""),
            "date": date_iso,
            "duration": data.get("duration_string") or "",
            "instagram": data.get("webpage_url") or f"https://www.instagram.com/reel/{vid}/",
            "category": "Instagram",
        }

    videos = [by_id[i] for i in ORDER if i in by_id]
    for vid, item in by_id.items():
        if vid not in ORDER:
            videos.append(item)

    payload = {
        "baseUrl": "https://media.givsharifi.com",
        "pathPrefix": "library",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "videos": videos,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(videos)} video(s) to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
