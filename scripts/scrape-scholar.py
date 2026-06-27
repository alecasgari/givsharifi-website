#!/usr/bin/env python3
"""One-time / manual Google Scholar profile scrape → publications/data/index.json"""

from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publications" / "data" / "index.json"

SCHOLAR_USER = "iKoCQCsAAAAJ"
SCHOLAR_PROFILE = f"https://scholar.google.com/citations?user={SCHOLAR_USER}&hl=en"
PAGE_SIZE = 100

TOPIC_RULES: list[tuple[str, str]] = [
    (r"pituitary|sella|transsphenoidal|sphenoid", "Pituitary"),
    (r"skull\s*base|meningioma|sphenoorbital|endonasal", "Skull Base"),
    (r"spine|spinal|lumbar|cervical|spondylolysis|disc|scoliosis", "Spine"),
    (r"glioma|glioblastoma|brain\s*tumou?r|craniotom|intracranial", "Brain Tumour"),
    (r"hydrocephalus|ventricul|colloid\s*cyst|arachnoid", "Hydrocephalus"),
    (r"pediatric|paediatric|craniosynostosis|children", "Pediatric"),
    (r"endoscop", "Endoscopic"),
    (r"epilepsy|vagus", "Epilepsy"),
    (r"rna|glioblast|molecular|genetic|biomarker", "Research"),
]


class ScholarTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[dict] = []
        self._in_row = False
        self._in_title_link = False
        self._in_cite_link = False
        self._in_year = False
        self._in_year_cell = False
        self._capture_gray = False
        self._current: dict | None = None
        self._gray_parts: list[str] = []
        self._title_parts: list[str] = []
        self._cite_parts: list[str] = []
        self._year_parts: list[str] = []
        self.citations_total: int | None = None
        self.h_index: int | None = None
        self.i10_index: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        cls = attr.get("class", "") or ""

        if tag == "tr" and "gsc_a_tr" in cls:
            self._in_row = True
            self._current = {"title": "", "url": "", "authors": "", "journal": "", "year": None, "citations": 0}
            self._gray_parts = []
            return

        if not self._in_row or self._current is None:
            if tag == "td" and "gsc_rsb_std" in cls:
                self._stat_capture = True
            return

        if tag == "a" and self._in_row:
            href = attr.get("href") or ""
            if "gsc_a_at" in cls:
                self._in_title_link = True
                self._title_parts = []
                if href:
                    self._current["url"] = urllib.parse.urljoin("https://scholar.google.com", href)
            elif "gsc_a_ac" in cls or ("gsc_a_c" in cls and href):
                self._in_cite_link = True
                self._cite_parts = []

        if tag == "td" and self._in_row and "gsc_a_y" in cls:
            self._in_year_cell = True
            self._year_parts = []

        if tag == "span" and self._in_row and "gsc_a_y" in cls:
            self._in_year = True
            self._year_parts = []

        if tag == "div" and self._in_row and "gs_gray" in cls:
            self._capture_gray = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self._in_row:
            self._finalize_row()
            return

        if tag == "a" and self._in_title_link:
            self._in_title_link = False
            self._current["title"] = "".join(self._title_parts).strip()
        elif tag == "a" and self._in_cite_link:
            self._in_cite_link = False
            cite = "".join(self._cite_parts).strip()
            self._current["citations"] = int(cite) if cite.isdigit() else 0
        elif tag == "span" and self._in_year:
            self._in_year = False
            year_s = "".join(self._year_parts).strip()
            if year_s.isdigit() and self._current is not None:
                self._current["year"] = int(year_s)
        elif tag == "td" and self._in_year_cell:
            self._in_year_cell = False
            year_s = "".join(self._year_parts).strip()
            if year_s.isdigit() and self._current is not None:
                self._current["year"] = int(year_s)
        elif tag == "div" and self._capture_gray:
            self._capture_gray = False

    def handle_data(self, data: str) -> None:
        if self._in_title_link:
            self._title_parts.append(data)
        elif self._in_cite_link:
            self._cite_parts.append(data)
        elif self._in_year or self._in_year_cell:
            self._year_parts.append(data)
        elif self._capture_gray and self._current is not None:
            text = data.strip()
            if text:
                self._gray_parts.append(text)

    def _finalize_row(self) -> None:
        if self._current and self._current.get("title"):
            if len(self._gray_parts) >= 1:
                self._current["authors"] = self._gray_parts[0]
            if len(self._gray_parts) >= 2:
                self._current["journal"] = self._gray_parts[1]
            elif len(self._gray_parts) == 1:
                self._current["journal"] = ""
            if not self._current.get("year"):
                self._current["year"] = extract_year_from_journal(self._current.get("journal") or "")
            self.rows.append(self._current)
        self._in_row = False
        self._current = None
        self._gray_parts = []


def fetch_html(url: str) -> str:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_stats(html: str) -> dict:
    stats: dict[str, int | None] = {"citations": None, "hIndex": None, "i10Index": None}
    # Table has All-time and Since-2021 columns — take every first value per metric row.
    nums = re.findall(r'class="gsc_rsb_std">(\d+)<', html)
    if len(nums) >= 6:
        stats["citations"] = int(nums[0])
        stats["hIndex"] = int(nums[2])
        stats["i10Index"] = int(nums[4])
    elif len(nums) >= 3:
        stats["citations"] = int(nums[0])
        stats["hIndex"] = int(nums[1])
        stats["i10Index"] = int(nums[2])
    return stats


def extract_year_from_journal(journal: str) -> int | None:
    matches = re.findall(r"\b(19|20)\d{2}\b", journal)
    return int(matches[-1]) if matches else None


def guess_topic(title: str, journal: str) -> str:
    blob = f"{title} {journal}".lower()
    for pattern, label in TOPIC_RULES:
        if re.search(pattern, blob, re.I):
            return label
    return "Neurosurgery"


def slugify(title: str, year: int | None, idx: int) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.lower())[:60].strip("-")
    y = year or 0
    return f"{y}-{base}-{idx}" if base else f"pub-{y}-{idx}"


def scrape_all() -> dict:
    all_rows: list[dict] = []
    cstart = 0
    stats: dict = {}

    while True:
        params = urllib.parse.urlencode(
            {
                "user": SCHOLAR_USER,
                "hl": "en",
                "view_op": "list_works",
                "sortby": "pubdate",
                "cstart": cstart,
                "pagesize": PAGE_SIZE,
            }
        )
        url = f"https://scholar.google.com/citations?{params}"
        print(f"Fetching cstart={cstart}...")
        try:
            html = fetch_html(url)
        except urllib.error.HTTPError as e:
            raise SystemExit(f"HTTP error {e.code} for {url}") from e
        except urllib.error.URLError as e:
            raise SystemExit(f"Network error: {e}") from e

        if cstart == 0:
            stats = parse_stats(html)

        parser = ScholarTableParser()
        parser.feed(html)
        batch = parser.rows
        if not batch:
            break
        all_rows.extend(batch)
        print(f"  +{len(batch)} articles (total {len(all_rows)})")
        if len(batch) < PAGE_SIZE:
            break
        cstart += PAGE_SIZE
        time.sleep(2.5)

    seen_titles: set[str] = set()
    publications = []
    for i, row in enumerate(all_rows):
        title = row["title"]
        if title in seen_titles:
            continue
        seen_titles.add(title)
        year = row.get("year")
        journal = row.get("journal") or ""
        clean_url = row.get("url") or SCHOLAR_PROFILE
        if "citation_for_view=" in clean_url:
            m = re.search(r"(citation_for_view=[^&]+)", clean_url)
            if m:
                clean_url = (
                    f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={SCHOLAR_USER}&"
                    + m.group(1)
                )
        publications.append(
            {
                "id": slugify(title, year, i),
                "title": title,
                "authors": row.get("authors") or "",
                "journal": journal,
                "year": year,
                "citations": row.get("citations") or 0,
                "topic": guess_topic(title, journal),
                "url": clean_url,
            }
        )

    publications.sort(key=lambda p: (p["year"] or 0, p["citations"]), reverse=True)

    return {
        "updated": date.today().isoformat(),
        "stats": {
            "total": len(publications),
            "citations": stats.get("citations"),
            "hIndex": stats.get("hIndex"),
            "i10Index": stats.get("i10Index"),
            "scholarUrl": SCHOLAR_PROFILE,
        },
        "publications": publications,
    }


def main() -> int:
    data = scrape_all()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {len(data['publications'])} publications -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
