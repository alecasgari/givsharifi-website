# Gallery images — where to put files

## Step 1: Drop your originals here

```
givsharifi-website/assets/images/gallery/_incoming/
```

Accepted formats: **JPG, JPEG, PNG, WebP** (any filename is OK).

Optional: edit `manifest.json` in the same folder **before** processing:

```json
{
  "IMG_4521.jpg": {
    "slug": "neurosurgery-team-operating-room-dubai",
    "alt": "Neurosurgical team in operating theatre — Prof. Giv Sharifi, Dubai",
    "title": "Operating theatre — Dubai",
    "category": "Surgery",
    "featured": true
  }
}
```

- **slug** — SEO filename (lowercase, hyphens, English). If omitted, we generate from title.
- **alt** — accessibility & SEO (English description).
- **featured** — `true` = homepage auto-scroll strip (below hero stats).

## Step 2: Run processing

```bash
python scripts/process-gallery.py
```

This will convert to WebP, rename for SEO, update `assets/data/gallery.json`, and archive originals to `_processed/`.

## Step 3: Deploy

Commit new `.webp` files + `gallery.json`, then push.
