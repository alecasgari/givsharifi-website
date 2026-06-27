# Inner pages (source of truth)

Edit service pages here, then deploy:

```bash
python scripts/publish.py   # copies pages/ → site root for GitHub Pages
```

Local development:

```bash
python server.py     # http://localhost:8080
```

## URL mapping

| URL | Source |
|-----|--------|
| `/brain-surgery/` | `pages/brain-surgery/index.html` |
| `/spinal-surgery/` | `pages/spinal-surgery/index.html` |
| `/endoscopic-pituitary-surgery/` | `pages/endoscopic-pituitary-surgery/index.html` |
| `/physiotherapy/` | `pages/physiotherapy/index.html` |
| `/medical-tourism/` | `pages/medical-tourism/index.html` |
| `/done/` | `pages/done/index.html` |
| `404` | `pages/404.html` |
| `/blog/` | `blog/` (root — not in pages/) |

Published copies (`brain-surgery/`, `done/`, `404.html`, …) are **gitignored**. GitHub Action runs `publish.py` on deploy.
