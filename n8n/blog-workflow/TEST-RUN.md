# Blog workflow — first test run

## Before you run (5 min)

### 1. Google Sheet — row for today

Pick **one test row** (e.g. `id = 1`):

| Column | Value |
|--------|--------|
| `scheduled_date` | **today** `YYYY-MM-DD` (server/n8n timezone) |
| `status` | `queued` |

All other rows: leave `scheduled_date` as planned or empty status not `queued`.

### 2. Workflow `01` — hotfixes (if not re-imported)

**A. New Set node after `Row found?` (true branch)**

- Name: `Set calendar row`
- Include Other Fields: **ON**
- Add field: `chat_id` = your numeric Telegram chat ID (same as router)

Wire:

```
Row found? (true) → Set calendar row
Set calendar row → Sheet status drafting
Set calendar row → Run draft and preview
```

Remove: `Sheet status drafting → Run draft` (if still connected).

**B. Execute Workflow `Run draft and preview`**

- Pick workflow **02 Draft and Preview** from list (not `$env`).

### 3. Workflow `02` — hotfixes

**A. Gemini blog writer prompt** — calendar fields must use:

```
{{ $('When called by scheduler').item.json.id }}
{{ $('When called by scheduler').item.json.cluster }}
… (all calendar columns)
```

Not `{{ $json.id }}` (that only sees GitHub index context).

**B. Connections**

```
Normalize → Generate image → Extract base64 → Save draft GitHub → Build preview
Build preview → Pack image binary → Send preview photo
Build preview → Send approve buttons → Sheet status preview
```

**C. Code node `Pack image binary`** (before Send preview photo) — paste from regenerated `02-blog-draft-preview.json`.

**D. Send preview photo**

- Binary property: `data`
- Input from `Pack image binary`

### 4. Workflow `00` — Execute Workflow nodes

Pick from list:

- `Run scheduler now` → **01 Scheduler**
- `Run blog draft` → **02 Draft**
- `Run blog publish` → **03 Publish**

### 5. Activate all 4 workflows

Order: 01, 02, 03, then **00 Router** last.

---

## Test steps

### Step A — Manual scheduler (recommended first)

1. Open n8n → **GivSharifi Blog — 01 Scheduler**
2. Click **Test workflow** (uses `When called manually` trigger)
3. Watch execution:
   - Read calendar → Pick row → Set calendar row → Sheet drafting + Run draft

Expected: **02** runs 3–8 minutes (Gemini + DALL-E).

### Step B — Telegram

1. Send `/blogstatus` — should show `Queued: 1` (or your count)
2. Send `/blogrun` — same as Step A
3. Wait for Telegram **photo preview** + **Approve** buttons

### Step C — Publish

1. Tap **✅ Publish**
2. Workflow **03** runs → GitHub commits → Telegram link

Verify:

- https://www.givsharifi.com/blog/{slug}/
- Sheet row: `status=published`, `published_url` filled

---

## If something fails

| Step fails | Likely cause |
|------------|----------------|
| Pick today queued row → false | `scheduled_date` not today or `status` not `queued` |
| Gemini empty/wrong topic | Prompt still uses `$json` instead of `$('When called by scheduler')` |
| Article too short | Regenerate — needs 1000+ words |
| OpenAI image | Check OpenAI credential / billing |
| Send preview photo | Missing `Pack image binary` node |
| Publish no draft | `Save draft` ran before image — fix connection order |
| Execute workflow empty | Sub-workflow not picked from list |

Paste the **failed node name + error message** from n8n execution log for the next fix.
