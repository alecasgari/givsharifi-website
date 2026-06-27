#!/usr/bin/env python3
"""Local dev server — maps /brain-surgery/ etc. to pages/ source."""

import argparse
import http.server
import socketserver
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
PAGES = ROOT / "pages"


def resolve_file(url_path: str) -> Path:
    clean = unquote(url_path.split("?")[0].split("#")[0])
    rel = clean.strip("/")

    if not rel:
        return ROOT / "index.html"

    candidates = [
        PAGES / rel / "index.html",
        PAGES / rel,
        ROOT / rel / "index.html",
        ROOT / rel,
    ]
    for path in candidates:
        if path.is_file():
            return path

    fallback = PAGES / "404.html"
    return fallback if fallback.is_file() else ROOT / "index.html"


class DevHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path: str) -> str:
        resolved = resolve_file(path)
        return str(resolved.resolve())

    def log_message(self, format: str, *args) -> None:
        if args and str(args[0]).startswith("2"):
            super().log_message(format, *args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local dev server for givsharifi.com")
    parser.add_argument("port", nargs="?", type=int, default=8080, help="Port (default: 8080)")
    args = parser.parse_args()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", args.port), DevHandler) as httpd:
        print(f"Serving at http://localhost:{args.port}/")
        print("Service pages load from pages/ — do not use python -m http.server")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
