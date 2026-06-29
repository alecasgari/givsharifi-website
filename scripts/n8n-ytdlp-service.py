#!/usr/bin/env python3
"""
Deprecated — use apps/giv-ytdlp/ for production (Docker + R2 upload).

This script remains for quick local testing without Docker. On the VPS, deploy
apps/giv-ytdlp instead; see apps/giv-ytdlp/README.md.

Usage:
  pip install yt-dlp
  python scripts/n8n-ytdlp-service.py

POST http://127.0.0.1:9876/download
  {"url": "https://www.youtube.com/watch?v=...", "work_id": "optional-id"}

Files are written under ~/.n8n-files/giv-video-<work_id>/ so n8n Read/Write File nodes can access them.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HOST = os.environ.get("GIV_YTDLP_HOST", "127.0.0.1")
PORT = int(os.environ.get("GIV_YTDLP_PORT", "9876"))
TOKEN = os.environ.get("GIV_YTDLP_TOKEN", "")
FILES_BASE = Path(os.environ.get("N8N_FILES", Path.home() / ".n8n-files"))


def detect_source(url: str) -> str:
    u = url.lower()
    if "instagram.com" in u:
        return "instagram"
    if "youtube.com" in u or "youtu.be" in u:
        return "youtube"
    return "other"


def download(url: str, work_id: str) -> dict:
    work_dir = FILES_BASE / f"giv-video-{work_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-f",
        "bv*+ba/b",
        "--merge-output-format",
        "mp4",
        "-o",
        str(work_dir / "%(id)s.%(ext)s"),
        "--write-info-json",
        "--write-thumbnail",
        "--convert-thumbnails",
        "jpg",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "yt-dlp failed")

    info_files = sorted(work_dir.glob("*.info.json"))
    if not info_files:
        raise RuntimeError("yt-dlp did not write an info.json file")

    meta = json.loads(info_files[0].read_text(encoding="utf-8"))
    video_id = meta.get("id")
    if not video_id:
        raise RuntimeError("Missing video id in yt-dlp metadata")

    mp4 = work_dir / f"{video_id}.mp4"
    poster = work_dir / f"{video_id}.jpg"
    if not mp4.is_file():
        raise RuntimeError(f"Expected mp4 not found: {mp4}")
    if not poster.is_file():
        raise RuntimeError(f"Expected poster jpg not found: {poster}")

    return {
        "ok": True,
        "video_id": video_id,
        "work_dir": str(work_dir),
        "source": detect_source(url),
        "video_meta": meta,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/download":
            self._json(404, {"ok": False, "error": "not found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._json(400, {"ok": False, "error": "invalid json"})
            return

        if TOKEN and data.get("token") != TOKEN:
            self._json(401, {"ok": False, "error": "unauthorized"})
            return

        url = str(data.get("url", "")).strip()
        work_id = str(data.get("work_id", "manual")).strip() or "manual"
        if not url:
            self._json(400, {"ok": False, "error": "url required"})
            return

        try:
            result = download(url, work_id)
            self._json(200, result)
        except Exception as exc:
            self._json(500, {"ok": False, "error": str(exc)})

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"ok": True, "service": "n8n-ytdlp", "files_base": str(FILES_BASE)})
            return
        self._json(404, {"ok": False, "error": "not found"})


def main() -> int:
    FILES_BASE.mkdir(parents=True, exist_ok=True)
    server = HTTPServer((HOST, PORT), Handler)
    print(f"n8n yt-dlp service on http://{HOST}:{PORT} (files: {FILES_BASE})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
