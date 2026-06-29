from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from config import Settings, load_settings, resolve_cookies_file
from download import cleanup_work_dir, download_video
from r2_upload import upload_video_assets

_download_lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    settings: Settings

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            s = self.settings
            self._json(
                200,
                {
                    "ok": True,
                    "service": "giv-ytdlp",
                    "r2_configured": s.r2_configured,
                    "cookies_file": str(resolve_cookies_file(s) or ""),
                    "data_dir": str(s.data_dir),
                },
            )
            return
        self._json(404, {"ok": False, "error": "not found"})

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

        token = self.settings.token
        if token and data.get("token") != token:
            self._json(401, {"ok": False, "error": "unauthorized"})
            return

        url = str(data.get("url", "")).strip()
        work_id = str(data.get("work_id", "manual")).strip() or "manual"
        if not url:
            self._json(400, {"ok": False, "error": "url required"})
            return

        upload_r2 = data.get("upload_r2", True)
        if isinstance(upload_r2, str):
            upload_r2 = upload_r2.lower() not in ("0", "false", "no")

        if upload_r2 and not self.settings.r2_configured:
            self._json(
                500,
                {
                    "ok": False,
                    "error": "R2 not configured — set R2_* env vars or pass upload_r2: false",
                },
            )
            return

        if not _download_lock.acquire(blocking=False):
            self._json(503, {"ok": False, "error": "another download is in progress"})
            return

        work_dir = None
        try:
            result = download_video(url, work_id, self.settings)
            work_dir = result["work_dir"]
            video_id = result["video_id"]

            payload: dict = {
                "ok": True,
                "video_id": video_id,
                "source": result["source"],
                "video_meta": result["video_meta"],
            }

            if upload_r2:
                payload["r2"] = upload_video_assets(
                    self.settings,
                    video_id,
                    result["mp4"],
                    result["poster"],
                )
                cleanup_work_dir(work_dir)
                work_dir = None
                payload["work_dir"] = None
            else:
                payload["work_dir"] = str(work_dir)
                payload["mp4_path"] = str(result["mp4"])
                payload["poster_path"] = str(result["poster"])

            self._json(200, payload)
        except Exception as exc:
            if work_dir is not None:
                cleanup_work_dir(work_dir)
            self._json(500, {"ok": False, "error": str(exc)})
        finally:
            _download_lock.release()


def run_server(settings: Settings | None = None) -> int:
    settings = settings or load_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    class BoundHandler(Handler):
        pass

    BoundHandler.settings = settings

    server = HTTPServer((settings.host, settings.port), BoundHandler)
    print(
        f"giv-ytdlp on http://{settings.host}:{settings.port} "
        f"(r2={'yes' if settings.r2_configured else 'no'}, data={settings.data_dir})",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
    return 0
