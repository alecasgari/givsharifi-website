# Cloudflare Redirect Rules

Configure these in **Cloudflare Dashboard → Rules → Redirect Rules** for `givsharifi.com`:

## Required

| Source | Destination | Status |
|--------|-------------|--------|
| `givsharifi.com/*` | `https://www.givsharifi.com/$1` | 301 |
| `http://*givsharifi.com/*` | `https://www.givsharifi.com/$1` | 301 |

## Legacy WordPress URLs

| Source | Destination | Status |
|--------|-------------|--------|
| `/bio` | `/` | 301 |
| `/bio/` | `/` | 301 |
| `/etn_category` | `/` | 301 |
| `/etn_category/` | `/` | 301 |
| `/etn-tags` | `/` | 301 |
| `/etn-tags/` | `/` | 301 |
| `/etn-speaker-category` | `/` | 301 |
| `/etn-speaker-category/` | `/` | 301 |
| `/tag/*` | `/blog/` | 301 |
| `/ar/tag/*` | `/blog/` | 301 |

## Trailing slash (optional)

Cloudflare "Normalize URL" or a rule: if URL has no trailing slash and is not a file, append `/`.

## Pages folder (development)

Inner pages are authored in `pages/`. Before GitHub Pages deploy, run `python scripts/publish.py` to flatten them to the site root. Public URLs do not change — this preserves Search Console indexed URLs.

No Cloudflare rewrite rules are required when using the publish script.

## GitHub Pages DNS

- CNAME record: `www` → `YOUR_GITHUB_USERNAME.github.io`
- Pages custom domain: `www.givsharifi.com`
- Add `CNAME` file in repo root containing: `www.givsharifi.com`
