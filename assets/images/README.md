# Image assets

Organized by purpose — not WordPress year folders.

```
assets/images/
├── brand/          favicon, logo
├── icons/          UI icons (SVG, small WebP)
├── blog/           blog featured images (match post slug)
├── home/           homepage-only images
└── services/
    ├── brain-surgery/
    ├── spinal-surgery/
    ├── pituitary-surgery/
    ├── physiotherapy/
    └── medical-tourism/
```

Add new blog images to `blog/{slug}.webp` and reference in `posts/data/{slug}.json`.

Run after bulk changes:

```bash
python scripts/optimize-images.py
```
