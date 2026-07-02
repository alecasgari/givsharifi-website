# Google Sheets nodes — manual setup (self-hosted n8n)

On self-hosted n8n, **Document** and **Sheet** must be picked **From list** — not `$env` expressions.

Use the same document + tab on **every** Google Sheets node below.

## Shared values (all 6 nodes)

| Field | Pick from list |
|-------|----------------|
| **Credential** | `Google Sheets account` (your OAuth) |
| **Document** | `giv-content-calendar-template` |
| **Document ID** | `1yMd8rsnzDq8zXmOm-XnCC_jYU5NcjW5P84MdYnTi-ms` |
| **Sheet** | `content-calendar-template` |
| **Sheet GID** | `521343457` |

Header row in the sheet **must** include columns:  
`id`, `status`, `published_slug`, `published_url` (plus all calendar columns from CSV).

---

## Node 1 — `00-blog-telegram-router` → **Read calendar sheet**

| Setting | Value |
|---------|--------|
| Resource | Sheet Within Document |
| Operation | **Get Row(s)** / Read |
| Document | From list → `giv-content-calendar-template` |
| Sheet | From list → `content-calendar-template` |
| Options | default (first row = headers) |

No column mapping needed — reads all rows for `/blogstatus` counts.

---

## Node 2 — `01-blog-scheduler` → **Read calendar**

Same as Node 1:

| Setting | Value |
|---------|--------|
| Operation | **Get Row(s)** / Read |
| Document | `giv-content-calendar-template` |
| Sheet | `content-calendar-template` |

---

## Node 3 — `01-blog-scheduler` → **Sheet status drafting**

| Setting | Value |
|---------|--------|
| Operation | **Update Row** |
| Document | `giv-content-calendar-template` |
| Sheet | `content-calendar-template` |
| Mapping mode | **Map Each Column Manually** / Define below |
| **Column to match on** | `id` |

| Column | Value (expression) |
|--------|-------------------|
| `id` | `{{ $json.id }}` |
| `status` | `drafting` (plain text, no expression) |

---

## Node 4 — `02-blog-draft-preview` → **Sheet status preview**

| Setting | Value |
|---------|--------|
| Operation | **Update Row** |
| Document | `giv-content-calendar-template` |
| Sheet | `content-calendar-template` |
| **Column to match on** | `id` |

| Column | Value (expression) |
|--------|-------------------|
| `id` | `{{ $('When called by scheduler').item.json.id }}` |
| `status` | `preview` |
| `published_slug` | `{{ $('Normalize blog output').item.json.normalized.slug }}` |

---

## Node 5 — `03-blog-publish` → **Read sheet row**

Same as Node 1 (full sheet read — Code node filters by `row_id`):

| Setting | Value |
|---------|--------|
| Operation | **Get Row(s)** / Read |
| Document | `giv-content-calendar-template` |
| Sheet | `content-calendar-template` |

---

## Node 6 — `03-blog-publish` → **Sheet status published**

| Setting | Value |
|---------|--------|
| Operation | **Update Row** |
| Document | `giv-content-calendar-template` |
| Sheet | `content-calendar-template` |
| **Column to match on** | `id` |

| Column | Value (expression) |
|--------|-------------------|
| `id` | `{{ $('Parse draft').item.json.row.id }}` |
| `status` | `published` |
| `published_url` | `{{ 'https://www.givsharifi.com/blog/' + $('Parse draft').item.json.normalized.slug + '/' }}` |

---

## Checklist after editing

1. All 6 nodes show green credential on Google Sheets.
2. Each node shows document name (not empty / not `={{ $env... }}`).
3. Update nodes have **Column to match on = `id`**.
4. Run **01 Scheduler** manually (or `/blogrun` in Telegram) on a day that has `status=queued` in the sheet.

## Common errors

| Error | Fix |
|-------|-----|
| Document not found | Re-pick document from list; re-auth Google OAuth |
| No row updated | `id` in sheet must be number or string matching expression |
| Empty read | Sheet tab name wrong — use `content-calendar-template` not `Calendar` |
| Column not found | Header row must match CSV exactly (`id`, `status`, …) |
