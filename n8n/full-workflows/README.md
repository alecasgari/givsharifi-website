# Giv Sharifi — n8n Content Workflows

Import these workflows into n8n (`Workflows → Import from File`). Import **sub-workflows first**, then the router.

| File | Purpose |
|------|---------|
| `01-publish-photo.json` | Telegram photo → Gemini SEO metadata → GitHub `_incoming/` → dispatch processing |
| `02-publish-video.json` | Instagram reel URL → yt-dlp → Gemini English copy → R2 `library/` → `video-library.json` |
| `03-publish-blog.json` | Draft text (+ optional image) → Gemini full post JSON → GitHub blog files |
| `00-telegram-router.json` | Main bot menu — routes to sub-workflows |

## Prerequisites

### 1. n8n credentials (create in n8n UI)

| Credential | Used for |
|------------|----------|
| **Telegram API** | Bot token from [@BotFather](https://t.me/BotFather) |
| **Google Gemini (PaLM)** | Gemini API key — connect to every **Google Gemini Chat Model** sub-node |
| **GitHub API** | Personal access token with `repo` scope on `alecasgari/givsharifi-website` |
| **AWS (S3)** | Cloudflare R2 — see R2 section below |

### 2. Environment variables (n8n instance)

Set in n8n **Settings → Variables** (or `.env` on self-hosted):

```
GIV_GITHUB_OWNER=alecasgari
GIV_GITHUB_REPO=givsharifi-website
GIV_GITHUB_BRANCH=main
GIV_TELEGRAM_ALLOWED_CHAT_ID=YOUR_NUMERIC_CHAT_ID
GIV_R2_BUCKET=givsharifi-videos
GIV_R2_PUBLIC_BASE=https://media.givsharifi.com
GIV_SITE_URL=https://www.givsharifi.com
```

Get your Telegram chat ID: message [@userinfobot](https://t.me/userinfobot).

### 3. Cloudflare R2 (S3 credential in n8n)

Create credential **AWS** with:

- **Access Key ID** / **Secret** — R2 API token
- **Custom Endpoints** → ON
- **S3 Endpoint**: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`
- **Force Path Style**: ON
- **Region**: `auto`

Videos upload to prefix `library/` (matches `video-library.json` `pathPrefix`).

### 4. Self-hosted n8n only — video download

Workflow `02-publish-video` uses **Execute Command** to run `yt-dlp` (no native n8n node exists).

On the n8n server:

```bash
pip install yt-dlp
# or: apt install yt-dlp
```

If you use **n8n Cloud**, replace the **Execute Command** node with an HTTP call to your own small download service, or run n8n self-hosted.

### 5. GitHub Actions dispatch (photos)

After a photo is pushed to `_incoming/`, workflow `01` calls `repository_dispatch` event `process-gallery`.

Add this job to `.github/workflows/content-automation.yml` (or merge into deploy):

```yaml
on:
  repository_dispatch:
    types: [process-gallery]

jobs:
  process-gallery:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install Pillow
      - run: python scripts/process-gallery.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: process gallery images from n8n"
```

Push to `main` triggers existing **Deploy to GitHub Pages** workflow automatically.

## Bot usage

1. `/start` — show menu
2. **Add Photo** — send a photo (optional caption in Persian/English). Gemini writes `alt`, `title`, `slug`. Approve with inline button → publishes.
3. **Add Video** — send Instagram reel URL. Downloads, uploads to R2, updates `video-library.json` in English.
4. **Add Blog** — send `/blog` then your draft text (Persian OK). Optionally send a featured image next. Gemini produces SEO English JSON → approve → publishes.

## Workflow design notes

- **If / Switch** nodes for routing — no Code node for branching
- **AI Agent** + **Google Gemini Chat Model** + **Structured Output Parser** for metadata
- **GitHub** node for repo files (images, JSON, HTML shell)
- **AWS S3** node for R2 video/poster upload
- **HTTP Request** only for `repository_dispatch` (no native GitHub dispatch node)
- **Execute Command** only for `yt-dlp` (no native download node)

## After import

1. Open each workflow → assign credentials on every node that shows a warning
2. Link **Execute Workflow** nodes in `00-telegram-router` to the imported sub-workflow IDs (n8n may ask you to pick them from a dropdown)
3. Activate **sub-workflows** first, then **00-telegram-router**
4. Test with `/start` from your allowed chat only

## Security

- `GIV_TELEGRAM_ALLOWED_CHAT_ID` blocks all other Telegram users
- Never commit API keys — use n8n credentials only
- Review Gemini-generated English copy before tapping **Approve** on blog posts
