#!/usr/bin/env python3
"""Download Instagram reels into video/library/ (requires: pip install yt-dlp)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "video" / "library"

URLS = [
    "https://www.instagram.com/reel/DZ455nVtZ30/",
    "https://www.instagram.com/reel/DSVeg6sDVL0/",
    "https://www.instagram.com/reel/DSSIaiVjbg7/",
    "https://www.instagram.com/reel/DSCLtu8De9d/",
    "https://www.instagram.com/reel/DSAHZOojaFD/",
    "https://www.instagram.com/reel/DRmRS5IDT3h/",
    "https://www.instagram.com/reel/DRH6wYfjHfx/",
    "https://www.instagram.com/reel/DQl4VOejdFv/",
    "https://www.instagram.com/reel/DQT7SyljbrE/",
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for url in URLS:
        print(f"\n→ {url}")
        rc = subprocess.call(
            [
                sys.executable,
                "-m",
                "yt_dlp",
                "--no-playlist",
                "-f",
                "mp4/best",
                "-o",
                str(OUT / "%(id)s.%(ext)s"),
                "--write-info-json",
                "--write-thumbnail",
                "--convert-thumbnails",
                "jpg",
                url,
            ]
        )
        if rc != 0:
            print(f"  failed: {url}", file=sys.stderr)
    build = ROOT / "scripts" / "build-video-library.py"
    if build.is_file():
        subprocess.run([sys.executable, str(build)], check=True)
    print(f"\nDone. Upload {OUT}/*.mp4 to R2 folder library/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
