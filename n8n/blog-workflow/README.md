# GivSharifi Blog Automation (n8n)

Telegram bot + Google Sheets content calendar + Gemini SEO articles + AI images + GitHub publish.

## Files

| File | Purpose |
|------|---------|
| `content-calendar-template.csv` | Import into Google Sheets — 30 posts (Jun–Sep 2026) |
| `00-blog-telegram-router.json` | Telegram commands + Approve/Regenerate callbacks |
| `01-blog-scheduler.json` | Mon/Wed/Fri 09:00 — pick today's queued row |
| `02-blog-draft-preview.json` | Gemini 1000+ words + DALL-E image + Telegram preview |
| `03-blog-publish.json` | On ✅ Publish → GitHub + update sheet |
| `generate-blog-workflows.py` | Regenerate JSON after edits |

## Google Sheets setup

1. Create a new Google Sheet (e.g. **GivSharifi Blog Calendar**).
2. Import `content-calendar-template.csv` into tab **`Calendar`** (File → Import).
3. Keep the header row exactly as exported (column names are used by n8n).
4. Copy the Sheet ID from the URL:  
   `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
5. Share the sheet with your Google OAuth account used in n8n.

### Column reference

| Column | Description |
|--------|-------------|
| `id` | Unique row ID (1–30) — used in Telegram callbacks |
| `scheduled_date` | `YYYY-MM-DD` — must match Mon/Wed/Fri dates |
| `weekday` | Human reference only |
| `cluster` | Brain / Spine / Pituitary / Patient Journey / Local SEO |
| `pillar_url` | Internal link target (e.g. `/spinal-surgery/`) |
| `primary_keyword` | One unique keyword per row — cannibalization guard |
| `search_intent` | informational / condition / procedure / local |
| `proposed_title` | Seed title for Gemini |
| `proposed_slug` | Seed slug (final slug normalized in workflow) |
| `secondary_keywords` | Semicolon-separated |
| `category` | Brain Surgery / Spinal Surgery / Neurosurgery |
| `status` | `queued` → `drafting` → `preview` → `published` (or `skipped`) |
| `published_slug` | Filled when draft is ready |
| `published_url` | Filled on publish |
| `notes` | Editorial notes |

## n8n import order

1. Import `01-blog-scheduler.json`
2. Import `02-blog-draft-preview.json`
3. Import `03-blog-publish.json`
4. Import `00-blog-telegram-router.json`
5. Copy each workflow ID into n8n **environment variables**:

| Variable | Workflow |
|----------|----------|
| `GIV_BLOG_WF_SCHEDULER_ID` | 01 Scheduler |
| `GIV_BLOG_WF_DRAFT_ID` | 02 Draft and Preview |
| `GIV_BLOG_WF_PUBLISH_ID` | 03 Publish |
| `GIV_BLOG_SHEET_ID` | Google Sheet ID |
| `GIV_BLOG_SHEET_TAB` | `Calendar` (optional) |
| `GIV_TELEGRAM_ALLOWED_CHAT_ID` | Your Telegram chat ID |
| `GIV_SITE_URL` | `https://www.givsharifi.com` |

6. Assign credentials on every node:
   - Telegram
   - Google Sheets OAuth
   - Google Gemini
   - GitHub API
   - OpenAI API (DALL-E 3 for featured images)

7. Activate workflows **01 → 02 → 03 → 00** (router last).

## Manual wiring after import

- **02 → Send preview photo**: Add **Convert to File** between OpenAI response and Telegram if binary is missing.
- **03 → Upload featured WebP**: Convert base64 to WebP before GitHub upload.
- Create folder `posts/data/_drafts/` in GitHub repo before first run.

## Bot commands

| Command | Action |
|---------|--------|
| `/start` | Help menu |
| `/blogstatus` | Count queued / preview / published rows |
| `/blogrun` | Force today's scheduler (draft + preview) |

## Regenerate workflows

```bash
python n8n/blog-workflow/generate-blog-workflows.py
```
