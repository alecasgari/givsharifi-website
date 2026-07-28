# Cloudflare Redirect Rules

Configure these in **Cloudflare Dashboard → Rules → Redirect Rules** for `givsharifi.com`.

Use **Dynamic** redirects where `$1` / wildcards are needed. Prefer **301** for all SEO migrations.

## Required (apex / HTTPS)

| Source | Destination | Status |
|--------|-------------|--------|
| `givsharifi.com/*` | `https://www.givsharifi.com/$1` | 301 |
| `http://*givsharifi.com/*` | `https://www.givsharifi.com/$1` | 301 |

## Legacy WordPress → current site (priority after apex)

| # | Source (URI Path / Wildcard) | Destination | Status | Notes |
|---|------------------------------|-------------|--------|-------|
| 1 | `/bio` or `/bio/` | `https://www.givsharifi.com/about/` | 301 | Was old bio page |
| 2 | `/ar/bio` or `/ar/bio/` | `https://www.givsharifi.com/about/` | 301 | |
| 3 | `/ar` or `/ar/` | `https://www.givsharifi.com/` | 301 | Arabic locale removed |
| 4 | `/ar/blog/*` | `https://www.givsharifi.com/blog/$1` | 301 | Keep post slug |
| 5 | `/ar/spinal-surgery*` | `https://www.givsharifi.com/spinal-surgery/` | 301 | |
| 6 | `/ar/brain-surgery*` | `https://www.givsharifi.com/brain-surgery/` | 301 | |
| 7 | `/ar/endoscopic-pituitary-surgery*` | `https://www.givsharifi.com/endoscopic-pituitary-surgery/` | 301 | |
| 8 | `/ar/medical-tourism*` | `https://www.givsharifi.com/medical-tourism/` | 301 | |
| 9 | `/ar/physiotherapy*` | `https://www.givsharifi.com/physiotherapy/` | 301 | |
| 10 | `/ar/*` | `https://www.givsharifi.com/` | 301 | Catch-all remaining Arabic |
| 11 | `/category/blog*` | `https://www.givsharifi.com/blog/` | 301 | |
| 12 | `/tag/*` | `https://www.givsharifi.com/blog/` | 301 | Tag archives gone |
| 13 | `/category/*` | `https://www.givsharifi.com/blog/` | 301 | |
| 14 | `/etn-tags*` / `/etn-speaker-category*` / `/etn_category*` | `https://www.givsharifi.com/` | 301 | Event plugin URLs |
| 15 | `/wp-content/*` / `/wp-includes/*` | `https://www.givsharifi.com/` | 301 | Optional; robots also blocks |

Rule order: put **specific** Arabic service/blog rules **before** `/ar/*` catch-all.

## Suggested Cloudflare expression examples

**Arabic blog posts (wildcard):**

- If: URI Path matches `/ar/blog/*`
- Then: Dynamic redirect to `concat("https://www.givsharifi.com/blog/", regex_replace(http.request.uri.path, "^/ar/blog/", ""))`

Or use two static rules for high-traffic slugs if you prefer Static redirects.

**Bio:**

- If: `(http.request.uri.path eq "/bio" or http.request.uri.path eq "/bio/" or http.request.uri.path eq "/ar/bio" or http.request.uri.path eq "/ar/bio/")`
- Then: Static → `https://www.givsharifi.com/about/`

## Trailing slash (optional)

Cloudflare "Normalize URL" or a rule: if URL has no trailing slash and is not a file, append `/`.

## Pages folder (development)

Inner pages are authored in `pages/`. Before GitHub Pages deploy, run `python scripts/publish.py` to flatten them to the site root. Public URLs do not change — this preserves Search Console indexed URLs.

No Cloudflare rewrite rules are required when using the publish script.

## GitHub Pages DNS

- CNAME record: `www` → `YOUR_GITHUB_USERNAME.github.io`
- Pages custom domain: `www.givsharifi.com`
- Add `CNAME` file in repo root containing: `www.givsharifi.com`

## After changing redirects

1. Wait a few minutes for Cloudflare to propagate.
2. In Google Search Console → **Indexing → Pages** → open **Not found (404)** → **Validate fix**.
3. Request indexing only for real pages (home, services, about, blog posts) — not legacy tag URLs.
