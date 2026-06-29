# Giv Sharifi — n8n Content Workflows

Import these workflows into n8n (`Workflows → Import from File`). Import **sub-workflows first**, then the router.

> **Note:** Workflow JSON lives in git for reference. After changes, re-import into your n8n instance — no git push required unless the main website code changed.

| File | Purpose |
|------|---------|
| `01-publish-photo.json` | Telegram photo → Gemini SEO metadata → GitHub `_incoming/` → dispatch processing |
| `02-publish-video.json` | Instagram reel or YouTube URL → yt-dlp → Gemini English copy → R2 `library/` → `video-library.json` |
| `03-publish-blog.json` | Draft text (+ optional image) → Gemini full post JSON → GitHub blog files |
| `00-telegram-router.json` | Main bot menu — routes to sub-workflows |

## Prerequisites

### 1. n8n credentials (create in n8n UI)

| Credential | Used for |
|------------|----------|
| **Telegram API** | Bot token from [@BotFather](https://t.me/BotFather) |
| **Google Gemini (PaLM)** | Gemini API key — connect to every **Google Gemini Chat Model** sub-node |
| **GitHub API** | Personal access token with `repo` scope on `alecasgari/givsharifi-website` |

### 2. Environment variables (n8n instance)

GitHub owner/repo are **hardcoded in workflows** (`alecasgari` / `givsharifi-website`). You only need:

```
GIV_TELEGRAM_ALLOWED_CHAT_ID=YOUR_NUMERIC_CHAT_ID
GIV_WF_PHOTO_ID=<workflow id after import>
GIV_WF_VIDEO_ID=<workflow id after import>
GIV_WF_BLOG_ID=<workflow id after import>
```

Bucket `givsharifi-videos` and site URL `https://www.givsharifi.com` are hardcoded in the video workflow.

Get your Telegram chat ID: message [@userinfobot](https://t.me/userinfobot).

### 3. Gemini model

All **Google Gemini Chat Model** sub-nodes use:

`models/gemini-flash-lite-latest`

### 4. giv-ytdlp service (video workflow)

Workflow `02` calls the **giv-ytdlp** Docker app ([youtube-instagram-downloader](https://github.com/alecasgari/youtube-instagram-downloader)). It downloads Instagram/YouTube videos and uploads MP4 + poster to R2 — n8n no longer needs S3 or Read/Write File nodes for video.

**Server setup (already done if health checks passed):**

- Container `giv-ytdlp` on network `giv-ytdlp-net`
- `docker network connect giv-ytdlp-net n8n-app`
- Health from n8n: `docker exec n8n-app wget -qO- http://giv-ytdlp:9876/health`

**n8n HTTP Request node** posts to `http://giv-ytdlp:9876/download` (no auth token — service is not exposed to the internet).

On the server, leave `GIV_YTDLP_TOKEN` empty in `/home/alecadmin/giv-ytdlp/.env` so the service accepts requests without a token. Only `n8n-app` can reach it on `giv-ytdlp-net`.

### 5. GitHub Actions dispatch (photos)

After photo + manifest are committed, workflow `01` sends **one** `repository_dispatch` (`process-gallery`).

GitHub workflows use **concurrency queues** (`cancel-in-progress: false`):
- `content-automation` — gallery processing runs one at a time
- `pages` — deploy runs one at a time

Pushes to `assets/images/gallery/_incoming/` do **not** trigger Deploy (staging only). Deploy runs after `process-gallery.py` commits processed WebP files.

### 6. n8n photo workflow — sequential GitHub commits

Upload photo → Update manifest → Dispatch → Telegram (not parallel). Parallel branches caused double dispatch and double Telegram messages.

If `N8N_DEFAULT_BINARY_DATA_MODE=filesystem` (n8n v2 default), binary fields are file references — not raw Base64.

Workflow `01` uses **Extract photo base64** (`Extract From File` → *Move File to Base64 String*) right after **Download Telegram photo**. The GitHub upload reads `{{ $('Extract photo base64').item.json.photo_base64 }}`.

Do **not** use a Code node with `getBinaryDataBuffer(item, 'data')` — that API signature is wrong for cross-node reads.

## Bot usage

1. `/start` — show menu
2. **Add Photo** — send a photo (optional caption in Persian/English). Gemini writes `alt`, `title`, `slug`. Approve with inline button → publishes.
3. **Add Video** — send an Instagram reel URL or YouTube link. Downloads with yt-dlp, uploads to R2, updates `video-library.json` in English.
4. **Add Blog** — send `/blog` then your draft text (Persian OK). Optionally send a featured image next. Gemini produces SEO English JSON → approve → publishes.

## Workflow design notes

- **If / Switch** nodes for routing — no Code node for branching
- **Code** nodes for JSON merge/parse (Set node expressions cannot run `Object.assign`, computed keys, or multi-line JS)
- **Extract From File** for binary → Base64 on filesystem mode
- **AI Agent** + **Google Gemini Chat Model** (`models/gemini-flash-lite-latest`) + **Structured Output Parser** for metadata
- **GitHub** node for repo files (images, JSON, HTML shell) — owner `alecasgari`, repo `givsharifi-website`
- **HTTP Request** → `giv-ytdlp` Docker app for video download + R2 upload (Instagram + YouTube)
- **HTTP Request** for `repository_dispatch` (no native GitHub dispatch node)

## After import

1. Open each workflow → assign credentials on every node that shows a warning
2. On GitHub nodes, confirm owner **alecasgari** and repo **givsharifi-website** are selected from the list
3. On each Gemini model sub-node, confirm model is **models/gemini-flash-lite-latest**
4. Link **Execute Workflow** nodes in `00-telegram-router` to the imported sub-workflow IDs (or set `GIV_WF_*_ID` env vars)
5. Activate **sub-workflows** first, then **00-telegram-router**
6. Test with `/start` from your allowed chat only

## Security

- `GIV_TELEGRAM_ALLOWED_CHAT_ID` blocks all other Telegram users
- Never commit API keys — use n8n credentials only
- Review Gemini-generated English copy before tapping **Approve** on blog posts
