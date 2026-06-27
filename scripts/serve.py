#!/usr/bin/env python3
"""Local dev server: maps public URLs to pages/ source (no publish step needed)."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parent.parent / "server.py"), run_name="__main__")
