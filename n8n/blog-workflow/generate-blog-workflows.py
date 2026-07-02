#!/usr/bin/env python3
"""Generate importable n8n blog automation workflows (Google Sheets + Telegram + GitHub)."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parent

GITHUB_OWNER = "alecasgari"
GITHUB_REPO = "givsharifi-website"
GITHUB_BRANCH = "main"
GEMINI_MODEL = "models/gemini-flash-lite-latest"
SITE_URL = "https://www.givsharifi.com"

# Google Sheet — list mode (self-hosted n8n cannot use $env in documentId picker)
BLOG_SHEET_DOC = {
    "__rl": True,
    "value": "1yMd8rsnzDq8zXmOm-XnCC_jYU5NcjW5P84MdYnTi-ms",
    "mode": "list",
    "cachedResultName": "giv-content-calendar-template",
    "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1yMd8rsnzDq8zXmOm-XnCC_jYU5NcjW5P84MdYnTi-ms/edit?usp=drivesdk",
}
BLOG_SHEET_TAB = {
    "__rl": True,
    "value": 521343457,
    "mode": "list",
    "cachedResultName": "content-calendar-template",
    "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1yMd8rsnzDq8zXmOm-XnCC_jYU5NcjW5P84MdYnTi-ms/edit#gid=521343457",
}


def sheets_read_params() -> dict:
    return {
        "operation": "read",
        "documentId": BLOG_SHEET_DOC,
        "sheetName": BLOG_SHEET_TAB,
        "options": {},
    }


def sheets_update_params(columns: dict) -> dict:
    return {
        "operation": "update",
        "documentId": BLOG_SHEET_DOC,
        "sheetName": BLOG_SHEET_TAB,
        "columns": {
            "mappingMode": "defineBelow",
            "value": columns,
            "matchingColumns": ["id"],
        },
        "options": {},
    }


def nid() -> str:
    return str(uuid.uuid4())


def gh_owner() -> dict:
    return {
        "__rl": True,
        "value": GITHUB_OWNER,
        "mode": "list",
        "cachedResultName": GITHUB_OWNER,
        "cachedResultUrl": f"https://github.com/{GITHUB_OWNER}",
    }


def gh_repo() -> dict:
    return {
        "__rl": True,
        "value": GITHUB_REPO,
        "mode": "list",
        "cachedResultName": GITHUB_REPO,
        "cachedResultUrl": f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}",
    }


def gh_repo_params(**extra: object) -> dict:
    return {"owner": gh_owner(), "repository": gh_repo(), "branch": GITHUB_BRANCH, **extra}


def node(
    name: str,
    ntype: str,
    position: list[int],
    parameters: dict | None = None,
    type_version: float | int = 1,
    notes: str = "",
) -> dict:
    n: dict = {
        "parameters": parameters or {},
        "id": nid(),
        "name": name,
        "type": ntype,
        "typeVersion": type_version,
        "position": position,
    }
    if notes:
        n["notes"] = notes
    return n


def connect(connections: dict, src: str, dst: str, src_index: int = 0, dst_index: int = 0, ctype: str = "main") -> None:
    connections.setdefault(src, {}).setdefault(ctype, [])
    while len(connections[src][ctype]) <= src_index:
        connections[src][ctype].append([])
    connections[src][ctype][src_index].append({"node": dst, "type": ctype, "index": dst_index})


def workflow(name: str, nodes: list[dict], connections: dict) -> dict:
    return {
        "name": name,
        "nodes": nodes,
        "connections": connections,
        "pinData": {},
        "active": False,
        "settings": {"executionOrder": "v1"},
        "versionId": str(uuid.uuid4()),
        "meta": {"templateCredsSetupCompleted": False},
        "tags": [{"name": "givsharifi"}, {"name": "blog"}],
    }


def sticky(content: str, pos: list[int]) -> dict:
    return node("Note", "n8n-nodes-base.stickyNote", pos, {"content": content}, type_version=1)


BLOG_SCHEMA = {
    "slug": "brain-tumour-surgery-dubai",
    "title": "Brain Tumour Surgery Dubai: Types, Process and Recovery",
    "metaDescription": "Considering brain tumour surgery in Dubai? Learn types of surgery, what happens before and after, and when to seek a specialist. Speak with Prof. Giv Sharifi.",
    "excerpt": "A clear guide to brain tumour surgery in Dubai — surgical types, the hospital pathway, and realistic recovery expectations for patients and families.",
    "date": "2026-07-02",
    "category": "Brain Surgery",
    "tags": [
        "brain tumour surgery Dubai",
        "neurosurgeon Dubai",
        "neurosurgery Dubai",
        "glioma surgery",
        "brain cancer treatment",
        "neurosurgeon Tehran",
    ],
    "readingTimeMinutes": 8,
    "featuredImagePath": "assets/images/blog/brain-tumour-surgery-dubai.webp",
    "content": [
        {
            "type": "paragraph",
            "text": "Brain tumour surgery in Dubai is a major decision that patients and families often face after an MRI or CT scan shows a growth inside the skull. The goal of surgery is to remove all or part of the tumour while protecting healthy brain tissue, nerves, and blood vessels. Prof. Giv Sharifi explains each step in plain language so you know what tests are needed, what happens in the operating room, and how recovery usually progresses. This article covers common tumour types, surgical options, and when a second opinion may help.",
        },
        {
            "type": "heading",
            "level": 2,
            "text": "What Is a Brain Tumour?",
        },
        {
            "type": "paragraph",
            "text": "A brain tumour is an abnormal mass of cells within the brain or its coverings. Some tumours are benign and grow slowly; others are malignant and may spread more quickly. Symptoms can include headaches, seizures, weakness, speech changes, or vision problems, depending on the tumour location. Imaging with MRI is the main tool for diagnosis. Your neurosurgeon will also review your medical history and neurological examination before recommending surgery, observation, or other treatments.",
        },
        {
            "type": "list",
            "items": [
                "Persistent headaches that worsen over weeks",
                "New seizures in an adult",
                "Weakness or numbness on one side of the body",
                "Personality or memory changes",
            ],
        },
        {
            "type": "cta",
            "text": "Explore brain surgery services",
            "href": "/brain-surgery/",
        },
        {
            "type": "heading",
            "level": 2,
            "text": "Frequently Asked Questions",
        },
        {
            "type": "heading",
            "level": 3,
            "text": "How long is hospital stay after brain tumour surgery?",
        },
        {
            "type": "paragraph",
            "text": "Most patients stay in hospital for several days after craniotomy, but the exact length depends on the tumour type, surgery complexity, and recovery from anaesthesia. Some people go to a high-dependency unit for closer monitoring. Your team will check speech, movement, and wound healing before discharge. Physiotherapy and follow-up scans are often arranged. Prof. Giv Sharifi discusses expected timelines during your pre-operative consultation so you can plan work and family support.",
        },
    ],
}


NORMALIZE_SLUG_CODE = r"""const out = $('Gemini blog writer').first().json.output || {};
const row = $('When called by scheduler').first().json;

const STOP = new Set([
  'a','an','the','and','or','for','of','in','on','to','with','at','by','from','as','is','are','was','were','be','been','being',
]);

function slugify(s) {
  return String(s || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .split(/\s+/)
    .filter((w) => w && !STOP.has(w))
    .join('-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 60);
}

function countBodyWords(blocks) {
  let n = 0;
  for (const b of blocks || []) {
    if (b.type === 'paragraph' && b.text) {
      n += String(b.text).split(/\s+/).filter(Boolean).length;
    }
    if ((b.type === 'list' || b.type === 'ordered-list') && Array.isArray(b.items)) {
      for (const item of b.items) {
        n += String(item).split(/\s+/).filter(Boolean).length;
      }
    }
    if (b.type === 'blockquote' && b.text) {
      n += String(b.text).split(/\s+/).filter(Boolean).length;
    }
  }
  return n;
}

function normalizeBlocks(blocks) {
  const outBlocks = [];
  for (const b of blocks || []) {
    if (!b || typeof b !== 'object') continue;
    if (b.type === 'text' || b.type === 'paragraph') {
      const t = String(b.text || '').trim();
      if (!t) continue;
      if (t.split(/\s+/).length < 15 && !t.includes('.')) {
        outBlocks.push({ type: 'heading', level: b.level === 3 ? 3 : 2, text: t });
      } else {
        outBlocks.push({ type: 'paragraph', text: t });
      }
      continue;
    }
    if (b.type === 'heading') {
      const level = b.level === 1 ? 2 : (b.level || 2);
      outBlocks.push({ type: 'heading', level, text: String(b.text || '').trim() });
      continue;
    }
    if (['list', 'ordered-list', 'cta', 'blockquote', 'image', 'html'].includes(b.type)) {
      outBlocks.push(b);
    }
  }
  return outBlocks;
}

const slug = slugify(out.slug || row.proposed_slug || row.primary_keyword);
if (!slug) throw new Error('Could not build SEO slug');

out.content = normalizeBlocks(out.content);
const paragraphCount = out.content.filter((b) => b.type === 'paragraph').length;
const words = countBodyWords(out.content);

if (paragraphCount < 10) {
  throw new Error(
    `Gemini returned an outline, not a full article: only ${paragraphCount} paragraph blocks. `
    + 'Regenerate. Need 10+ paragraph blocks with 70+ words each.'
  );
}
if (words < 1000) {
  throw new Error(
    `Article too short: ~${words} words in paragraphs (minimum 1000). Regenerate with full prose.`
  );
}

out.slug = slug;
out.featuredImagePath = `assets/images/blog/${slug}.webp`;
out.date = String(row.scheduled_date || new Date().toISOString().slice(0, 10)).slice(0, 10);
out.readingTimeMinutes = Math.max(8, Math.round(words / 200));
delete out.primaryKeyword;
delete out.wordCountEstimate;

return [{
  json: {
    ...row,
    normalized: out,
    word_count: words,
    paragraph_count: paragraphCount,
    image_prompt: `Professional medical illustration for a patient education article titled "${out.title}". `
      + `Topic: ${row.primary_keyword}. Style: clean modern healthcare illustration, soft blue and white tones, `
      + `abstract anatomy or MRI scan motif. No blood, no surgery scenes, no patient faces, no text, no logos. 16:9.`,
  },
}];
"""


BUILD_POST_JSON_CODE = r"""const p = $('Normalize blog output').first().json.normalized;
const post = {
  ...p,
  author: {
    name: 'Prof. Giv Sharifi',
    title: 'Board-Certified Neurosurgeon',
    url: 'https://www.givsharifi.com/',
  },
  featuredImage: `/${p.featuredImagePath}`,
};
delete post.primaryKeyword;
delete post.wordCountEstimate;
return [{ json: { post_json: JSON.stringify(post, null, 2) + '\n', slug: p.slug } }];
"""


PREPEND_INDEX_CODE = r"""const ghItem = $('Get posts index').first().json;
const github = ghItem.body ?? ghItem;
if (github.message && !github.content) {
  throw new Error(`GitHub API: ${github.message}`);
}
let raw = github.content ?? '';
if (github.encoding === 'base64' && raw) {
  raw = Buffer.from(String(raw).replace(/\n/g, ''), 'base64').toString('utf8');
}
raw = String(raw).trim();
if (!raw) throw new Error('posts/data/index.json content empty');
const idx = JSON.parse(raw);
const p = $('Normalize blog output').first().json.normalized;
idx.posts = [{
  slug: p.slug,
  title: p.title,
  excerpt: p.excerpt,
  date: p.date,
  category: p.category,
  image: `/${p.featuredImagePath}`,
}, ...(idx.posts || [])];
return [{ json: { index_json: JSON.stringify(idx, null, 2) + '\n', index_sha: github.sha || '' } }];
"""


PREVIEW_TEXT_CODE = r"""const row = $('Extract image base64').first().json;
const p = row.normalized;
const blocks = (p.content || []).filter((b) => b.type === 'paragraph').slice(0, 2);
const preview = blocks.map((b) => b.text).join('\n\n').slice(0, 400);
const cal = $('When called by scheduler').first().json;
const chatId = cal.chat_id || cal.telegram_chat_id;
if (!chatId) {
  throw new Error('chat_id missing on scheduler payload — set in workflow 01 Set calendar row');
}
return [{
  json: {
    chat_id: chatId,
    row_id: row.id,
    slug: p.slug,
    image_base64: row.image_base64,
    preview_message:
      `📋 <b>Blog preview</b> (row ${row.id})\n\n`
      + `<b>Title:</b> ${p.title}\n`
      + `<b>Slug:</b> ${p.slug}\n`
      + `<b>Meta:</b> ${p.metaDescription}\n`
      + `<b>Words:</b> ~${row.word_count}\n`
      + `<b>Cluster:</b> ${row.cluster}\n`
      + `<b>Primary KW:</b> ${row.primary_keyword}\n\n`
      + `<b>Excerpt:</b>\n${preview}…`,
    callback_publish: `blog_publish_${row.id}`,
    callback_regen_article: `blog_regen_article_${row.id}`,
    callback_regen_image: `blog_regen_image_${row.id}`,
    callback_skip: `blog_skip_${row.id}`,
  },
}];
"""


def build_router() -> dict:
    nodes: list[dict] = []
    c: dict = {}

    trigger = node(
        "Telegram Trigger",
        "n8n-nodes-base.telegramTrigger",
        [0, 0],
        {"updates": ["message", "callback_query"]},
        type_version=1.1,
    )
    nodes.append(trigger)

    auth = node(
        "Allowed chat?",
        "n8n-nodes-base.if",
        [220, 0],
        {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [
                    {
                        "leftValue": "={{ String($json.message?.chat?.id || $json.callback_query?.message?.chat?.id) }}",
                        "rightValue": "={{ $env.GIV_TELEGRAM_ALLOWED_CHAT_ID }}",
                        "operator": {"type": "string", "operation": "equals"},
                    }
                ],
                "combinator": "and",
            }
        },
        type_version=2.2,
    )
    nodes.append(auth)

    is_callback = node(
        "Is callback?",
        "n8n-nodes-base.if",
        [440, 0],
        {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [
                    {
                        "leftValue": "={{ $json.callback_query ? 'yes' : 'no' }}",
                        "rightValue": "yes",
                        "operator": {"type": "string", "operation": "equals"},
                    }
                ],
                "combinator": "and",
            }
        },
        type_version=2.2,
    )
    nodes.append(is_callback)

    route_cb = node(
        "Route blog callback",
        "n8n-nodes-base.switch",
        [660, -80],
        {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.callback_query.data }}",
                                    "rightValue": "blog_publish_",
                                    "operator": {"type": "string", "operation": "startsWith"},
                                }
                            ],
                            "combinator": "and",
                        },
                        "renameOutput": True,
                        "outputKey": "publish",
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.callback_query.data }}",
                                    "rightValue": "blog_regen_",
                                    "operator": {"type": "string", "operation": "startsWith"},
                                }
                            ],
                            "combinator": "and",
                        },
                        "renameOutput": True,
                        "outputKey": "regen",
                    },
                ]
            },
            "options": {"fallbackOutput": "extra"},
        },
        type_version=3.2,
    )
    nodes.append(route_cb)

    prep_publish = node(
        "Prepare publish payload",
        "n8n-nodes-base.set",
        [880, -160],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {
                        "id": nid(),
                        "name": "row_id",
                        "value": "={{ $json.callback_query.data.replace('blog_publish_', '') }}",
                        "type": "string",
                    },
                    {
                        "id": nid(),
                        "name": "chat_id",
                        "value": "={{ $json.callback_query.message.chat.id }}",
                        "type": "number",
                    },
                    {
                        "id": nid(),
                        "name": "action",
                        "value": "publish",
                        "type": "string",
                    },
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(prep_publish)

    prep_regen = node(
        "Prepare regen payload",
        "n8n-nodes-base.set",
        [880, 0],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {
                        "id": nid(),
                        "name": "row_id",
                        "value": "={{ $json.callback_query.data.replace(/blog_regen_(article|image)_/, '') }}",
                        "type": "string",
                    },
                    {
                        "id": nid(),
                        "name": "regen_type",
                        "value": "={{ $json.callback_query.data.includes('image') ? 'image' : 'article' }}",
                        "type": "string",
                    },
                    {
                        "id": nid(),
                        "name": "chat_id",
                        "value": "={{ $json.callback_query.message.chat.id }}",
                        "type": "number",
                    },
                    {
                        "id": nid(),
                        "name": "action",
                        "value": "regen",
                        "type": "string",
                    },
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(prep_regen)

    ack = node(
        "Answer callback",
        "n8n-nodes-base.telegram",
        [880, 160],
        {
            "resource": "callback",
            "queryId": "={{ $json.callback_query.id }}",
            "additionalFields": {"text": "Processing…"},
        },
        type_version=1.2,
    )
    nodes.append(ack)

    exec_publish = node(
        "Run blog publish",
        "n8n-nodes-base.executeWorkflow",
        [1100, -160],
        {"workflowId": "={{ $env.GIV_BLOG_WF_PUBLISH_ID }}", "mode": "each", "options": {}},
        type_version=1.2,
        notes="Set GIV_BLOG_WF_PUBLISH_ID to 03-blog-publish workflow ID after import",
    )
    nodes.append(exec_publish)

    exec_regen = node(
        "Run blog draft",
        "n8n-nodes-base.executeWorkflow",
        [1100, 0],
        {"workflowId": "={{ $env.GIV_BLOG_WF_DRAFT_ID }}", "mode": "each", "options": {}},
        type_version=1.2,
        notes="Set GIV_BLOG_WF_DRAFT_ID to 02-blog-draft-preview workflow ID",
    )
    nodes.append(exec_regen)

    route_msg = node(
        "Route command",
        "n8n-nodes-base.switch",
        [660, 200],
        {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.message?.text || '' }}",
                                    "rightValue": "/start",
                                    "operator": {"type": "string", "operation": "startsWith"},
                                }
                            ],
                            "combinator": "and",
                        },
                        "renameOutput": True,
                        "outputKey": "start",
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.message?.text || '' }}",
                                    "rightValue": "/blogstatus",
                                    "operator": {"type": "string", "operation": "startsWith"},
                                }
                            ],
                            "combinator": "and",
                        },
                        "renameOutput": True,
                        "outputKey": "status",
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.message?.text || '' }}",
                                    "rightValue": "/blogrun",
                                    "operator": {"type": "string", "operation": "startsWith"},
                                }
                            ],
                            "combinator": "and",
                        },
                        "renameOutput": True,
                        "outputKey": "run",
                    },
                ]
            },
            "options": {"fallbackOutput": "extra"},
        },
        type_version=3.2,
    )
    nodes.append(route_msg)

    menu = node(
        "Send blog menu",
        "n8n-nodes-base.telegram",
        [880, 120],
        {
            "chatId": "={{ $json.message.chat.id }}",
            "text": "Prof. Giv Sharifi — Blog Bot\n\n📅 Mon/Wed/Fri: auto draft from Google Sheet\n✅ Approve previews here\n\n/blogstatus — next queued posts\n/blogrun — force today's draft now",
            "additionalFields": {"parse_mode": "HTML"},
        },
        type_version=1.2,
    )
    nodes.append(menu)

    exec_scheduler = node(
        "Run scheduler now",
        "n8n-nodes-base.executeWorkflow",
        [880, 280],
        {"workflowId": "={{ $env.GIV_BLOG_WF_SCHEDULER_ID }}", "mode": "each", "options": {}},
        type_version=1.2,
        notes="Set GIV_BLOG_WF_SCHEDULER_ID to 01-blog-scheduler workflow ID",
    )
    nodes.append(exec_scheduler)

    sheet_status = node(
        "Read calendar sheet",
        "n8n-nodes-base.googleSheets",
        [880, 400],
        sheets_read_params(),
        type_version=4.5,
        notes="Credential: Google Sheets OAuth. Document + tab from list (see GOOGLE-SHEETS-NODES.md).",
    )
    nodes.append(sheet_status)

    status_msg = node(
        "Send sheet status",
        "n8n-nodes-base.telegram",
        [1100, 400],
        {
            "chatId": "={{ $('Telegram Trigger').item.json.message.chat.id }}",
            "text": "={{ 'Queued: ' + $input.all().filter(i => i.json.status === 'queued').length + '\\nPreview: ' + $input.all().filter(i => i.json.status === 'preview').length + '\\nPublished: ' + $input.all().filter(i => i.json.status === 'published').length }}",
        },
        type_version=1.2,
    )
    nodes.append(status_msg)

    unauth = node(
        "Unauthorized",
        "n8n-nodes-base.telegram",
        [440, 200],
        {"chatId": "={{ $json.message?.chat?.id || $json.callback_query?.message?.chat?.id }}", "text": "Unauthorized."},
        type_version=1.2,
    )
    nodes.append(unauth)

    nodes.append(
        sticky(
            "## Blog Telegram router\n"
            "Callbacks: `blog_publish_{id}`, `blog_regen_article_{id}`, `blog_regen_image_{id}`\n\n"
            "Env: `GIV_TELEGRAM_ALLOWED_CHAT_ID`, `GIV_BLOG_WF_DRAFT_ID`, `GIV_BLOG_WF_PUBLISH_ID`, "
            "`GIV_BLOG_WF_SCHEDULER_ID` — see GOOGLE-SHEETS-NODES.md for Sheet nodes",
            [-40, -220],
        )
    )

    connect(c, "Telegram Trigger", "Allowed chat?")
    connect(c, "Allowed chat?", "Is callback?", 0)
    connect(c, "Allowed chat?", "Unauthorized", 1)
    connect(c, "Is callback?", "Route blog callback", 0)
    connect(c, "Is callback?", "Route command", 1)
    connect(c, "Route blog callback", "Prepare publish payload", 0)
    connect(c, "Route blog callback", "Prepare regen payload", 1)
    connect(c, "Route blog callback", "Answer callback", 2)
    connect(c, "Prepare publish payload", "Run blog publish")
    connect(c, "Prepare regen payload", "Run blog draft")
    connect(c, "Route command", "Send blog menu", 0)
    connect(c, "Route command", "Read calendar sheet", 1)
    connect(c, "Route command", "Run scheduler now", 2)
    connect(c, "Read calendar sheet", "Send sheet status")

    return workflow("GivSharifi Blog — 00 Telegram Router", nodes, c)


def build_scheduler() -> dict:
    nodes: list[dict] = []
    c: dict = {}

    sched = node(
        "Mon Wed Fri 9am",
        "n8n-nodes-base.scheduleTrigger",
        [0, 0],
        {
            "rule": {
                "interval": [
                    {
                        "field": "cronExpression",
                        "expression": "0 9 * * 1,3,5",
                    }
                ]
            }
        },
        type_version=1.2,
        notes="09:00 server time — set VPS timezone to Asia/Dubai or adjust cron",
    )
    nodes.append(sched)

    manual = node("When called manually", "n8n-nodes-base.executeWorkflowTrigger", [0, 200], type_version=1.1)
    nodes.append(manual)

    today = node(
        "Set today ISO",
        "n8n-nodes-base.set",
        [220, 100],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {
                        "id": nid(),
                        "name": "today",
                        "value": "={{ $now.toFormat('yyyy-MM-dd') }}",
                        "type": "string",
                    }
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(today)

    sheet = node(
        "Read calendar",
        "n8n-nodes-base.googleSheets",
        [440, 100],
        sheets_read_params(),
        type_version=4.5,
    )
    nodes.append(sheet)

    pick = node(
        "Pick today queued row",
        "n8n-nodes-base.code",
        [660, 100],
        {
            "jsCode": """const today = $('Set today ISO').first().json.today;
const rows = $input.all().map((i) => i.json);
const match = rows.find((r) => r.status === 'queued' && String(r.scheduled_date).trim() === today);
if (!match) {
  return [{ json: { found: false, today, message: `No queued row for ${today}` } }];
}
return [{ json: { found: true, ...match } }];
"""
        },
        type_version=2,
    )
    nodes.append(pick)

    attach_chat = node(
        "Set calendar row",
        "n8n-nodes-base.set",
        [880, 0],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {
                        "id": nid(),
                        "name": "chat_id",
                        "value": "REPLACE_WITH_YOUR_TELEGRAM_CHAT_ID",
                        "type": "string",
                    }
                ]
            },
            "includeOtherFields": True,
        },
        type_version=3.4,
        notes="Replace chat_id with your numeric Telegram chat ID (same as router allowed chat).",
    )
    nodes.append(attach_chat)

    found = node(
        "Row found?",
        "n8n-nodes-base.if",
        [880, 100],
        {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [
                    {
                        "leftValue": "={{ $json.found }}",
                        "rightValue": True,
                        "operator": {"type": "boolean", "operation": "true"},
                    }
                ],
                "combinator": "and",
            }
        },
        type_version=2.2,
    )
    nodes.append(found)

    mark_drafting = node(
        "Sheet status drafting",
        "n8n-nodes-base.googleSheets",
        [1100, 0],
        sheets_update_params({
            "id": "={{ $json.id }}",
            "status": "drafting",
        }),
        type_version=4.5,
        notes="Update Row — match column: id",
    )
    nodes.append(mark_drafting)

    exec_draft = node(
        "Run draft and preview",
        "n8n-nodes-base.executeWorkflow",
        [1320, 0],
        {"workflowId": "={{ $env.GIV_BLOG_WF_DRAFT_ID }}", "mode": "each", "options": {}},
        type_version=1.2,
    )
    nodes.append(exec_draft)

    notify_none = node(
        "Telegram no row",
        "n8n-nodes-base.telegram",
        [1100, 200],
        {
            "chatId": "={{ $env.GIV_TELEGRAM_ALLOWED_CHAT_ID }}",
            "text": "={{ 'Blog scheduler: ' + $json.message }}",
        },
        type_version=1.2,
    )
    nodes.append(notify_none)

    nodes.append(
        sticky(
            "## Blog scheduler\n"
            "Reads Google Sheet `content-calendar-template.csv` → finds `status=queued` + `scheduled_date=today` → runs draft workflow.\n\n"
            "Import `content-calendar-template.csv` into Google Sheets tab named `Calendar`.",
            [-40, -180],
        )
    )

    connect(c, "Mon Wed Fri 9am", "Set today ISO")
    connect(c, "When called manually", "Set today ISO")
    connect(c, "Set today ISO", "Read calendar")
    connect(c, "Read calendar", "Pick today queued row")
    connect(c, "Pick today queued row", "Row found?")
    connect(c, "Row found?", "Set calendar row", 0)
    connect(c, "Row found?", "Telegram no row", 1)
    connect(c, "Set calendar row", "Sheet status drafting")
    connect(c, "Set calendar row", "Run draft and preview")

    return workflow("GivSharifi Blog — 01 Scheduler", nodes, c)


def build_draft_preview() -> dict:
    nodes: list[dict] = []
    c: dict = {}

    trigger = node("When called by scheduler", "n8n-nodes-base.executeWorkflowTrigger", [0, 0], type_version=1.1)
    nodes.append(trigger)

    gh_index = node(
        "Get posts index",
        "n8n-nodes-base.github",
        [220, -120],
        {"resource": "file", "operation": "get", **gh_repo_params(), "filePath": "posts/data/index.json"},
        type_version=1.1,
    )
    nodes.append(gh_index)

    existing_kw = node(
        "Build existing keywords context",
        "n8n-nodes-base.code",
        [440, -120],
        {
            "jsCode": """const ghItem = $('Get posts index').first().json;
const github = ghItem.body ?? ghItem;
let raw = github.content ?? '';
if (github.encoding === 'base64' && raw) {
  raw = Buffer.from(String(raw).replace(/\\n/g, ''), 'base64').toString('utf8');
}
const idx = JSON.parse(String(raw).trim() || '{"posts":[]}');
const titles = (idx.posts || []).map((p) => `- ${p.slug}: ${p.title}`).join('\\n');
return [{ json: { existing_posts: titles } }];
"""
        },
        type_version=2,
    )
    nodes.append(existing_kw)

    model = node(
        "Gemini blog model",
        "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
        [440, 120],
        {"modelName": GEMINI_MODEL, "options": {"temperature": 0.45, "maxOutputTokens": 8192}},
        type_version=1,
    )
    nodes.append(model)

    parser = node(
        "Blog JSON parser",
        "@n8n/n8n-nodes-langchain.outputParserStructured",
        [440, 320],
        {"jsonSchemaExample": json.dumps(BLOG_SCHEMA, indent=2)},
        type_version=1.2,
    )
    nodes.append(parser)

    blog_prompt = (
        "=Calendar row:\\n"
        "id: {{ $('When called by scheduler').item.json.id }}\\n"
        "cluster: {{ $('When called by scheduler').item.json.cluster }}\\n"
        "pillar_url: {{ $('When called by scheduler').item.json.pillar_url }}\\n"
        "primary_keyword: {{ $('When called by scheduler').item.json.primary_keyword }}\\n"
        "search_intent: {{ $('When called by scheduler').item.json.search_intent }}\\n"
        "proposed_title: {{ $('When called by scheduler').item.json.proposed_title }}\\n"
        "proposed_slug: {{ $('When called by scheduler').item.json.proposed_slug }}\\n"
        "secondary_keywords: {{ $('When called by scheduler').item.json.secondary_keywords }}\\n"
        "category: {{ $('When called by scheduler').item.json.category }}\\n"
        "scheduled_date: {{ $('When called by scheduler').item.json.scheduled_date }}\\n\\n"
        "Already published (avoid duplicate intent):\\n"
        "{{ $('Build existing keywords context').item.json.existing_posts }}\\n\\n"
        "Write a COMPLETE long-form SEO blog post JSON for Prof. Giv Sharifi's website.\\n\\n"
        "CRITICAL — FULL ARTICLE, NOT AN OUTLINE:\\n"
        "- Minimum 1000 words in paragraph + list text combined\\n"
        "- Minimum 12 paragraph blocks; EACH paragraph 70-120 words (4-7 sentences)\\n"
        "- Do NOT output section titles only. Every H2 section needs 2+ full paragraphs.\\n"
        "- Allowed content types ONLY: paragraph, heading, list, ordered-list, cta\\n"
        "- NEVER use type text. NEVER use heading level 1.\\n"
        "- heading level 2 = main sections; level 3 = FAQ questions only\\n"
        "- Structure: intro paragraph (120+ words) → 5-6 H2 sections (each with 2 paragraphs + optional list) "
        "→ 2 cta blocks (href=pillar_url and href=/) → H2 FAQ → 5x (H3 question + paragraph answer 80+ words)\\n"
        "- date: use scheduled_date from calendar row\\n"
        "- slug: 3-5 words, lowercase hyphenated, NO stop words (the, and, for, of, in, to, with)\\n"
        "- title: 50-65 chars, primary keyword near start\\n"
        "- metaDescription: 150-155 chars, unique from excerpt, soft CTA\\n"
        "- 5-8 tags including neurosurgery Dubai and neurosurgeon Tehran where natural\\n"
        "- YMYL: no guaranteed outcomes; use may, can, your surgeon will assess\\n"
        "- featuredImagePath: assets/images/blog/{slug}.webp"
    )

    agent = node(
        "Gemini blog writer",
        "@n8n/n8n-nodes-langchain.agent",
        [660, 0],
        {
            "promptType": "define",
            "text": blog_prompt,
            "hasOutputParser": True,
            "options": {
                "systemMessage": (
                    "You are an expert medical SEO writer for Prof. Giv Sharifi, neurosurgeon in Dubai and Tehran. "
                    "Output valid JSON only via the parser. Write FULL prose paragraphs — never bullet-point outlines "
                    "disguised as headings. Simple B2 English. Never use Persian. If you cannot reach 1000 words, "
                    "add more paragraph blocks before returning JSON."
                )
            },
        },
        type_version=1.7,
    )
    nodes.append(agent)

    normalize = node("Normalize blog output", "n8n-nodes-base.code", [880, 0], {"jsCode": NORMALIZE_SLUG_CODE}, type_version=2)
    nodes.append(normalize)

    image_req = node(
        "Generate featured image",
        "n8n-nodes-base.httpRequest",
        [1100, -80],
        {
            "method": "POST",
            "url": "https://api.openai.com/v1/images/generations",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "openAiApi",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ { model: 'dall-e-3', prompt: $json.image_prompt, n: 1, size: '1792x1024', response_format: 'b64_json' } }}",
        },
        type_version=4.2,
        notes="Assign OpenAI API credential. Or swap for Google Imagen HTTP node.",
    )
    nodes.append(image_req)

    image_b64 = node(
        "Extract image base64",
        "n8n-nodes-base.code",
        [1320, -80],
        {
            "jsCode": """const body = $input.first().json;
const b64 = body.data?.[0]?.b64_json;
if (!b64) throw new Error('No image returned from OpenAI');
const row = $('Normalize blog output').first().json;
return [{ json: { ...row, image_base64: b64 } }];
"""
        },
        type_version=2,
    )
    nodes.append(image_b64)

    save_draft = node(
        "Save draft JSON GitHub",
        "n8n-nodes-base.github",
        [1540, 0],
        {
            "resource": "file",
            "operation": "create",
            **gh_repo_params(),
            "filePath": "={{ 'posts/data/_drafts/' + $('Extract image base64').item.json.normalized.slug + '.json' }}",
            "fileContent": "={{ JSON.stringify($('Extract image base64').item.json, null, 2) }}",
            "commitMessage": "=blog: save draft {{ $('Extract image base64').item.json.normalized.slug }}",
        },
        type_version=1.1,
        notes="On re-run change operation to edit if file exists",
    )
    nodes.append(save_draft)

    preview = node("Build preview message", "n8n-nodes-base.code", [1760, 0], {"jsCode": PREVIEW_TEXT_CODE}, type_version=2)
    nodes.append(preview)

    pack_binary = node(
        "Pack image binary",
        "n8n-nodes-base.code",
        [1980, -80],
        {
            "jsCode": """const item = $input.first().json;
const b64 = item.image_base64;
if (!b64) throw new Error('No image_base64 for Telegram photo');
return [{
  json: item,
  binary: {
    data: {
      data: b64,
      mimeType: 'image/png',
      fileName: `${item.slug}.png`,
      encoding: 'base64',
    },
  },
}];
"""
        },
        type_version=2,
    )
    nodes.append(pack_binary)

    send_photo = node(
        "Send preview photo",
        "n8n-nodes-base.telegram",
        [1760, -80],
        {
            "operation": "sendPhoto",
            "chatId": "={{ $json.chat_id }}",
            "binaryData": True,
            "additionalFields": {
                "caption": "={{ $json.preview_message }}",
                "parse_mode": "HTML",
            },
        },
        type_version=1.2,
        notes="Wire binary from image — map in n8n UI: binary property from previous HTTP node converted to file",
    )
    nodes.append(send_photo)

    send_buttons = node(
        "Send approve buttons",
        "n8n-nodes-base.telegram",
        [1760, 80],
        {
            "chatId": "={{ $('Build preview message').item.json.chat_id }}",
            "text": "Approve this blog post?",
            "replyMarkup": "inlineKeyboard",
            "inlineKeyboard": {
                "rows": [
                    [
                        {"row": {"buttons": [
                            {"text": "✅ Publish", "additionalFields": {"callback_data": "={{ $('Build preview message').item.json.callback_publish }}"}},
                            {"text": "🔄 Regen article", "additionalFields": {"callback_data": "={{ $('Build preview message').item.json.callback_regen_article }}"}},
                        ]}},
                    ],
                    [
                        {"row": {"buttons": [
                            {"text": "🖼 Regen image", "additionalFields": {"callback_data": "={{ $('Build preview message').item.json.callback_regen_image }}"}},
                            {"text": "❌ Skip", "additionalFields": {"callback_data": "={{ $('Build preview message').item.json.callback_skip }}"}},
                        ]}},
                    ],
                ]
            },
        },
        type_version=1.2,
    )
    nodes.append(send_buttons)

    sheet_preview = node(
        "Sheet status preview",
        "n8n-nodes-base.googleSheets",
        [2420, 80],
        sheets_update_params({
            "id": "={{ $('When called by scheduler').item.json.id }}",
            "status": "preview",
            "published_slug": "={{ $('Normalize blog output').item.json.normalized.slug }}",
        }),
        type_version=4.5,
    )
    nodes.append(sheet_preview)

    nodes.append(
        sticky(
            "## Draft + preview\n"
            "Gemini 1000+ words → slug normalize → DALL-E image → Telegram preview → Sheet status=preview\n\n"
            "After import: connect binary image path to Send preview photo (Convert to File node if needed).",
            [-40, -200],
        )
    )

    connect(c, "When called by scheduler", "Get posts index")
    connect(c, "Get posts index", "Build existing keywords context")
    connect(c, "Build existing keywords context", "Gemini blog writer")
    connect(c, "Gemini blog model", "Gemini blog writer", ctype="ai_languageModel")
    connect(c, "Blog JSON parser", "Gemini blog writer", ctype="ai_outputParser")
    connect(c, "Gemini blog writer", "Normalize blog output")
    connect(c, "Normalize blog output", "Generate featured image")
    connect(c, "Generate featured image", "Extract image base64")
    connect(c, "Extract image base64", "Save draft JSON GitHub")
    connect(c, "Save draft JSON GitHub", "Build preview message")
    connect(c, "Build preview message", "Pack image binary")
    connect(c, "Build preview message", "Send approve buttons")
    connect(c, "Pack image binary", "Send preview photo")
    connect(c, "Send approve buttons", "Sheet status preview")

    return workflow("GivSharifi Blog — 02 Draft and Preview", nodes, c)


def build_publish() -> dict:
    nodes: list[dict] = []
    c: dict = {}

    trigger = node("When called by router", "n8n-nodes-base.executeWorkflowTrigger", [0, 0], type_version=1.1)
    nodes.append(trigger)

    sheet_row = node(
        "Read sheet row",
        "n8n-nodes-base.googleSheets",
        [220, 0],
        sheets_read_params(),
        type_version=4.5,
    )
    nodes.append(sheet_row)

    pick_row = node(
        "Find row by id",
        "n8n-nodes-base.code",
        [440, 0],
        {
            "jsCode": """const rowId = String($('When called by router').first().json.row_id);
const row = $input.all().map((i) => i.json).find((r) => String(r.id) === rowId);
if (!row) throw new Error('Sheet row not found: ' + rowId);
if (!row.published_slug) throw new Error('No published_slug on row — run draft first');
return [{ json: row }];
"""
        },
        type_version=2,
    )
    nodes.append(pick_row)

    get_draft = node(
        "Get draft JSON",
        "n8n-nodes-base.github",
        [660, 0],
        {
            "resource": "file",
            "operation": "get",
            **gh_repo_params(),
            "filePath": "={{ 'posts/data/_drafts/' + $json.published_slug + '.json' }}",
        },
        type_version=1.1,
    )
    nodes.append(get_draft)

    parse_draft = node(
        "Parse draft",
        "n8n-nodes-base.code",
        [880, 0],
        {
            "jsCode": """const gh = $input.first().json;
let raw = gh.content ?? '';
if (gh.encoding === 'base64' && raw) {
  raw = Buffer.from(String(raw).replace(/\\n/g, ''), 'base64').toString('utf8');
}
const draft = JSON.parse(String(raw).trim());
const p = draft.normalized;
if (!p) throw new Error('Draft missing normalized post');
return [{ json: { row: $('Find row by id').first().json, normalized: p, image_base64: draft.image_base64 || '' } }];
"""
        },
        type_version=2,
    )
    nodes.append(parse_draft)

    publish_build_post_code = r"""const p = $('Parse draft').first().json.normalized;
const post = {
  ...p,
  author: {
    name: 'Prof. Giv Sharifi',
    title: 'Board-Certified Neurosurgeon',
    url: 'https://www.givsharifi.com/',
  },
  featuredImage: `/${p.featuredImagePath}`,
};
delete post.primaryKeyword;
delete post.wordCountEstimate;
return [{ json: { post_json: JSON.stringify(post, null, 2) + '\n', slug: p.slug } }];
"""
    build_post = node("Build post JSON", "n8n-nodes-base.code", [1100, -80], {"jsCode": publish_build_post_code}, type_version=2)
    nodes.append(build_post)

    shell = node(
        "Get post HTML shell",
        "n8n-nodes-base.github",
        [1100, 80],
        {"resource": "file", "operation": "get", **gh_repo_params(), "filePath": "blog/_post-shell.html"},
        type_version=1.1,
    )
    nodes.append(shell)

    create_json = node(
        "Create post JSON",
        "n8n-nodes-base.github",
        [1320, -160],
        {
            "resource": "file",
            "operation": "create",
            **gh_repo_params(),
            "filePath": "={{ 'posts/data/' + $('Parse draft').item.json.normalized.slug + '.json' }}",
            "fileContent": "={{ $('Build post JSON').item.json.post_json }}",
            "commitMessage": "=content: publish blog {{ $('Parse draft').item.json.normalized.slug }}",
        },
        type_version=1.1,
    )
    nodes.append(create_json)

    create_html = node(
        "Create blog HTML page",
        "n8n-nodes-base.github",
        [1320, 0],
        {
            "resource": "file",
            "operation": "create",
            **gh_repo_params(),
            "filePath": "={{ 'blog/' + $('Parse draft').item.json.normalized.slug + '/index.html' }}",
            "fileContent": "={{ $('Get post HTML shell').item.json.content }}",
            "commitMessage": "=content: add blog shell {{ $('Parse draft').item.json.normalized.slug }}",
        },
        type_version=1.1,
    )
    nodes.append(create_html)

    create_image = node(
        "Upload featured WebP",
        "n8n-nodes-base.github",
        [1320, 160],
        {
            "resource": "file",
            "operation": "create",
            **gh_repo_params(),
            "filePath": "={{ $('Parse draft').item.json.normalized.featuredImagePath }}",
            "fileContent": "={{ $('Parse draft').item.json.image_base64 }}",
            "commitMessage": "=content: add blog image {{ $('Parse draft').item.json.normalized.slug }}",
        },
        type_version=1.1,
        notes="Prefer WebP via Convert to File node before upload — wire after import",
    )
    nodes.append(create_image)

    gh_index = node(
        "Get posts index",
        "n8n-nodes-base.github",
        [1540, 0],
        {"resource": "file", "operation": "get", **gh_repo_params(), "filePath": "posts/data/index.json"},
        type_version=1.1,
    )
    nodes.append(gh_index)

    publish_prepend_code = r"""const ghItem = $('Get posts index').first().json;
const github = ghItem.body ?? ghItem;
if (github.message && !github.content) {
  throw new Error(`GitHub API: ${github.message}`);
}
let raw = github.content ?? '';
if (github.encoding === 'base64' && raw) {
  raw = Buffer.from(String(raw).replace(/\n/g, ''), 'base64').toString('utf8');
}
raw = String(raw).trim();
if (!raw) throw new Error('posts/data/index.json content empty');
const idx = JSON.parse(raw);
const p = $('Parse draft').first().json.normalized;
idx.posts = [{
  slug: p.slug,
  title: p.title,
  excerpt: p.excerpt,
  date: p.date,
  category: p.category,
  image: `/${p.featuredImagePath}`,
}, ...(idx.posts || [])];
return [{ json: { index_json: JSON.stringify(idx, null, 2) + '\n', index_sha: github.sha || '' } }];
"""
    prepend = node(
        "Prepend to index",
        "n8n-nodes-base.code",
        [1760, 0],
        {"jsCode": publish_prepend_code},
        type_version=2,
    )
    nodes.append(prepend)

    update_index = node(
        "Update posts index",
        "n8n-nodes-base.github",
        [1980, 0],
        {
            "resource": "file",
            "operation": "edit",
            **gh_repo_params(),
            "filePath": "posts/data/index.json",
            "fileContent": "={{ $json.index_json }}",
            "commitMessage": "=content: update blog index {{ $('Parse draft').item.json.normalized.slug }}",
            "additionalParameters": {"sha": "={{ $json.index_sha }}"},
        },
        type_version=1.1,
    )
    nodes.append(update_index)

    sheet_pub = node(
        "Sheet status published",
        "n8n-nodes-base.googleSheets",
        [2200, 0],
        sheets_update_params({
            "id": "={{ $('Parse draft').item.json.row.id }}",
            "status": "published",
            "published_url": "={{ 'https://www.givsharifi.com/blog/' + $('Parse draft').item.json.normalized.slug + '/' }}",
        }),
        type_version=4.5,
    )
    nodes.append(sheet_pub)

    success = node(
        "Telegram published",
        "n8n-nodes-base.telegram",
        [2420, 0],
        {
            "chatId": "={{ $('When called by router').item.json.chat_id || $env.GIV_TELEGRAM_ALLOWED_CHAT_ID }}",
            "text": "={{ '✅ Blog published\\n\\n' + $('Parse draft').item.json.normalized.title + '\\n\\n' + $env.GIV_SITE_URL + '/blog/' + $('Parse draft').item.json.normalized.slug + '/' }}",
            "replyMarkup": "inlineKeyboard",
            "inlineKeyboard": {
                "rows": [
                    [
                        {
                            "row": {
                                "buttons": [
                                    {
                                        "text": "Open on website",
                                        "additionalFields": {
                                            "url": "={{ $env.GIV_SITE_URL + '/blog/' + $('Parse draft').item.json.normalized.slug + '/' }}"
                                        },
                                    }
                                ]
                            }
                        }
                    ]
                ]
            },
        },
        type_version=1.2,
    )
    nodes.append(success)

    nodes.append(
        sticky(
            "## Publish on approve\n"
            "Loads draft from `posts/data/_drafts/{slug}.json` → GitHub post + shell + image + index → Sheet published",
            [-40, -180],
        )
    )

    connect(c, "When called by router", "Read sheet row")
    connect(c, "Read sheet row", "Find row by id")
    connect(c, "Find row by id", "Get draft JSON")
    connect(c, "Get draft JSON", "Parse draft")
    connect(c, "Parse draft", "Build post JSON")
    connect(c, "Parse draft", "Get post HTML shell")
    connect(c, "Parse draft", "Upload featured WebP")
    connect(c, "Build post JSON", "Create post JSON")
    connect(c, "Get post HTML shell", "Create blog HTML page")
    connect(c, "Create post JSON", "Get posts index")
    connect(c, "Create blog HTML page", "Get posts index")
    connect(c, "Create post JSON", "Get posts index")
    connect(c, "Get posts index", "Prepend to index")
    connect(c, "Prepend to index", "Update posts index")
    connect(c, "Update posts index", "Sheet status published")
    connect(c, "Sheet status published", "Telegram published")

    return workflow("GivSharifi Blog — 03 Publish", nodes, c)


def main() -> None:
    files = {
        "00-blog-telegram-router.json": build_router(),
        "01-blog-scheduler.json": build_scheduler(),
        "02-blog-draft-preview.json": build_draft_preview(),
        "03-blog-publish.json": build_publish(),
    }
    for name, wf in files.items():
        path = OUT / name
        path.write_text(json.dumps(wf, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
