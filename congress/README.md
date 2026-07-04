# Congress Events

Each congress or symposium lives in its own folder under `congress/{slug}/`.

## Folder structure

```
congress/
├── data/
│   └── index.json              # Listing metadata (search, filters, cards)
├── _event-shell.html           # Template for new event detail pages
├── {slug}/
│   ├── index.html              # Detail page shell (loads data.json)
│   ├── data.json               # Full event content (English)
│   └── images/                 # Event photos
└── index.html                  # Generated from pages/congress/ on publish
```

## Adding a new congress

1. Create `congress/{slug}/data.json` with event details (see `nanomedicine-symposium-2025/data.json`).
2. Add photos to `congress/{slug}/images/`.
3. Copy `congress/_event-shell.html` to `congress/{slug}/index.html` (or run `python scripts/publish.py` to auto-create missing shells).
4. Add a summary entry to `congress/data/index.json`.
5. Update `sitemap.xml` with the new URL.

All user-facing text must be in English.
