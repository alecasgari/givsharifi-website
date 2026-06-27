#!/usr/bin/env python3
"""Generate importable n8n workflow JSON files for givsharifi-website content automation."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parent / "full-workflows"


def nid() -> str:
    return str(uuid.uuid4())


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


def workflow(name: str, nodes: list[dict], connections: dict, tags: list[str] | None = None) -> dict:
    return {
        "name": name,
        "nodes": nodes,
        "connections": connections,
        "pinData": {},
        "active": False,
        "settings": {"executionOrder": "v1"},
        "versionId": str(uuid.uuid4()),
        "meta": {"templateCredsSetupCompleted": False},
        "tags": tags or [{"name": "givsharifi"}],
    }


def gemini_stack(
    agent_name: str,
    model_name: str,
    parser_name: str,
    prompt: str,
    schema: dict,
    position_x: int = 400,
) -> tuple[list[dict], str, str, str]:
    """Return nodes for Agent + Gemini model + structured parser (sub-node wiring done separately)."""
    model = node(
        model_name,
        "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
        [position_x, 200],
        {"options": {"temperature": 0.3}},
        type_version=1,
    )
    parser = node(
        parser_name,
        "@n8n/n8n-nodes-langchain.outputParserStructured",
        [position_x, 400],
        {"jsonSchemaExample": json.dumps(schema, indent=2)},
        type_version=1.2,
    )
    agent = node(
        agent_name,
        "@n8n/n8n-nodes-langchain.agent",
        [position_x, 0],
        {
            "promptType": "define",
            "text": prompt,
            "hasOutputParser": True,
            "options": {"systemMessage": "You are a medical website content assistant for Prof. Giv Sharifi, a neurosurgeon in Dubai and Tehran. Output valid JSON only via the parser. All public text must be professional English suitable for SEO."},
        },
        type_version=1.7,
    )
    return [model, parser, agent], agent_name, model_name, parser_name


def wire_agent(connections: dict, agent: str, model: str, parser: str, upstream: str) -> None:
    connect(connections, upstream, agent)
    connect(connections, model, agent, ctype="ai_languageModel")
    connect(connections, parser, agent, ctype="ai_outputParser")


MANIFEST_SCHEMA = {
    "slug": "prof-giv-sharifi-neurosurgery-clinic",
    "alt": "Descriptive alt text for SEO",
    "title": "Short gallery title",
    "category": "Surgery",
    "featured": False,
}

VIDEO_META_SCHEMA = {
    "title": "English video title max 80 chars",
    "description": "English description max 160 chars",
    "category": "Patient Stories",
}

BLOG_SCHEMA = {
    "slug": "example-blog-slug",
    "title": "Article title",
    "metaDescription": "SEO meta description max 155 chars",
    "excerpt": "Card excerpt 2 sentences",
    "date": "2026-06-27",
    "category": "Neurosurgery",
    "tags": ["brain surgery", "neurosurgery Dubai"],
    "readingTimeMinutes": 6,
    "featuredImagePath": "assets/images/blog/example.webp",
    "content": [
        {"type": "paragraph", "text": "Opening paragraph."},
        {"type": "heading", "level": 2, "text": "Section heading"},
        {"type": "paragraph", "text": "Body text."},
    ],
}


def build_photo_workflow() -> dict:
    nodes: list[dict] = []
    c: dict = {}

    trigger = node("When called by router", "n8n-nodes-base.executeWorkflowTrigger", [0, 0], type_version=1.1)
    nodes.append(trigger)

    dl = node(
        "Download Telegram photo",
        "n8n-nodes-base.telegram",
        [220, 0],
        {
            "resource": "file",
            "fileId": "={{ $json.photo_file_id }}",
        },
        type_version=1.2,
    )
    nodes.append(dl)

    fname = node(
        "Set incoming filename",
        "n8n-nodes-base.set",
        [440, 0],
        {
            "mode": "manual",
            "duplicateItem": False,
            "assignments": {
                "assignments": [
                    {"id": nid(), "name": "incoming_name", "value": "={{ 'tg-' + $now.toFormat('yyyyMMdd-HHmmss') + '.jpg' }}", "type": "string"},
                    {"id": nid(), "name": "chat_id", "value": "={{ $('When called by router').item.json.chat_id }}", "type": "number"},
                    {"id": nid(), "name": "caption", "value": "={{ $('When called by router').item.json.caption || '' }}", "type": "string"},
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(fname)

    prompt = (
        "=Caption (may be Persian or English): {{ $json.caption }}\n\n"
        "Generate SEO gallery metadata for Prof. Giv Sharifi neurosurgery website.\n"
        "category must be one of: Surgery, Team, Clinic, Patient Care, Diagnostics.\n"
        "featured: true only if exceptional hero/clinic/team shot."
    )
    stack, agent, model, parser = gemini_stack(
        "Gemini photo metadata",
        "Gemini photo model",
        "Photo metadata parser",
        prompt,
        MANIFEST_SCHEMA,
        660,
    )
    nodes.extend(stack)

    gh_manifest_get = node(
        "Get manifest.json",
        "n8n-nodes-base.github",
        [880, 0],
        {
            "resource": "file",
            "operation": "get",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "assets/images/gallery/_incoming/manifest.json",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_manifest_get)

    merge_manifest = node(
        "Merge manifest entry",
        "n8n-nodes-base.set",
        [1100, 0],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {
                        "id": nid(),
                        "name": "manifest_json",
                        "value": "={{ JSON.stringify(Object.assign(JSON.parse($json.content || '{}'), { [$('Set incoming filename').item.json.incoming_name]: $('Gemini photo metadata').item.json.output } }), null, 2) }}",
                        "type": "string",
                    }
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(merge_manifest)

    gh_upload = node(
        "Upload photo to _incoming",
        "n8n-nodes-base.github",
        [1320, -80],
        {
            "resource": "file",
            "operation": "create",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "={{ 'assets/images/gallery/_incoming/' + $('Set incoming filename').item.json.incoming_name }}",
            "fileContent": "={{ $('Download Telegram photo').item.binary.data }}",
            "commitMessage": "content: add gallery photo via Telegram bot",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_upload)

    gh_manifest_put = node(
        "Update manifest.json",
        "n8n-nodes-base.github",
        [1320, 80],
        {
            "resource": "file",
            "operation": "edit",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "assets/images/gallery/_incoming/manifest.json",
            "fileContent": "={{ $('Merge manifest entry').item.json.manifest_json }}",
            "commitMessage": "content: update gallery manifest via Telegram bot",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_manifest_put)

    dispatch = node(
        "Dispatch process-gallery",
        "n8n-nodes-base.httpRequest",
        [1540, 0],
        {
            "method": "POST",
            "url": "=https://api.github.com/repos/{{ $env.GIV_GITHUB_OWNER }}/{{ $env.GIV_GITHUB_REPO }}/dispatches",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "githubApi",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": '={"event_type":"process-gallery","client_payload":{"source":"n8n"}}',
        },
        type_version=4.2,
        notes="Requires GitHub credential. Triggers GitHub Actions to run scripts/process-gallery.py",
    )
    nodes.append(dispatch)

    notify = node(
        "Telegram success",
        "n8n-nodes-base.telegram",
        [1760, 0],
        {
            "chatId": "={{ $('When called by router').item.json.chat_id }}",
            "text": "=Photo queued for processing.\n\nTitle: {{ $('Gemini photo metadata').item.json.output.title }}\nSlug: {{ $('Gemini photo metadata').item.json.output.slug }}\n\nGallery will update in ~2 min: {{ $env.GIV_SITE_URL }}/gallery/",
        },
        type_version=1.2,
    )
    nodes.append(notify)

    connect(c, "When called by router", "Download Telegram photo")
    connect(c, "Download Telegram photo", "Set incoming filename")
    wire_agent(c, "Gemini photo metadata", "Gemini photo model", "Photo metadata parser", "Set incoming filename")
    connect(c, "Gemini photo metadata", "Get manifest.json")
    connect(c, "Get manifest.json", "Merge manifest entry")
    connect(c, "Merge manifest entry", "Upload photo to _incoming")
    connect(c, "Merge manifest entry", "Update manifest.json")
    connect(c, "Upload photo to _incoming", "Dispatch process-gallery")
    connect(c, "Update manifest.json", "Dispatch process-gallery")
    connect(c, "Dispatch process-gallery", "Telegram success")

    nodes.append(
        node(
            "Note: Photo flow",
            "n8n-nodes-base.stickyNote",
            [-40, -180],
            {"content": "## Photo publish\nTelegram photo → Gemini (alt/slug) → GitHub `_incoming/` + manifest → `repository_dispatch` → `process-gallery.py` → WebP + gallery.json → GitHub Pages deploy."},
            type_version=1,
        )
    )

    return workflow("GivSharifi — 01 Publish Photo", nodes, c)


def build_video_workflow() -> dict:
    nodes: list[dict] = []
    c: dict = {}

    trigger = node("When called by router", "n8n-nodes-base.executeWorkflowTrigger", [0, 0], type_version=1.1)
    nodes.append(trigger)

    extract = node(
        "Set reel URL",
        "n8n-nodes-base.set",
        [220, 0],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {"id": nid(), "name": "reel_url", "value": "={{ $json.reel_url }}", "type": "string"},
                    {"id": nid(), "name": "chat_id", "value": "={{ $json.chat_id }}", "type": "number"},
                    {"id": nid(), "name": "work_dir", "value": "=/tmp/giv-video-{{ $execution.id }}", "type": "string"},
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(extract)

    ytdlp = node(
        "yt-dlp download",
        "n8n-nodes-base.executeCommand",
        [440, 0],
        {
            "command": "=mkdir -p {{ $json.work_dir }} && yt-dlp --no-playlist -f 'mp4/best' -o '{{ $json.work_dir }}/%(id)s.%(ext)s' --write-info-json --write-thumbnail --convert-thumbnails jpg '{{ $json.reel_url }}'",
        },
        type_version=1,
        notes="Self-hosted n8n only. Installs: pip install yt-dlp",
    )
    nodes.append(ytdlp)

    read_meta = node(
        "Read info JSON",
        "n8n-nodes-base.readWriteFile",
        [660, 0],
        {
            "operation": "read",
            "fileSelector": "={{ $json.work_dir + '/*.info.json' }}",
            "options": {},
        },
        type_version=1,
    )
    nodes.append(read_meta)

    parse_meta = node(
        "Parse reel metadata",
        "n8n-nodes-base.set",
        [880, 0],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {"id": nid(), "name": "reel_meta", "value": "={{ JSON.parse($json.data) }}", "type": "object"},
                    {"id": nid(), "name": "video_id", "value": "={{ JSON.parse($json.data).id }}", "type": "string"},
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(parse_meta)

    prompt = (
        "=Original Instagram description:\n{{ $json.reel_meta.description || $json.reel_meta.title }}\n\n"
        "Write English title and description for a neurosurgery patient-education video page. "
        "No Persian. Professional tone. category: Patient Stories."
    )
    stack, agent, model, parser = gemini_stack(
        "Gemini video copy",
        "Gemini video model",
        "Video copy parser",
        prompt,
        VIDEO_META_SCHEMA,
        1100,
    )
    nodes.extend(stack)

    s3_video = node(
        "Upload MP4 to R2",
        "n8n-nodes-base.awsS3",
        [1320, -80],
        {
            "operation": "upload",
            "bucketName": "={{ $env.GIV_R2_BUCKET }}",
            "fileName": "=library/{{ $('Parse reel metadata').item.json.video_id }}.mp4",
            "additionalFields": {},
            "binaryPropertyName": "data",
        },
        type_version=2,
        notes="AWS credential → R2 endpoint. Read MP4 via Read/Write File node before this if needed.",
    )
    nodes.append(s3_video)

    s3_poster = node(
        "Upload poster to R2",
        "n8n-nodes-base.awsS3",
        [1320, 80],
        {
            "operation": "upload",
            "bucketName": "={{ $env.GIV_R2_BUCKET }}",
            "fileName": "=library/{{ $('Parse reel metadata').item.json.video_id }}.jpg",
            "additionalFields": {},
        },
        type_version=2,
    )
    nodes.append(s3_poster)

    gh_get = node(
        "Get video-library.json",
        "n8n-nodes-base.github",
        [1540, 0],
        {
            "resource": "file",
            "operation": "get",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "assets/data/video-library.json",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_get)

    build_json = node(
        "Prepend new video entry",
        "n8n-nodes-base.set",
        [1760, 0],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {
                        "id": nid(),
                        "name": "library_json",
                        "value": "={{ (() => { const lib = JSON.parse($json.content); const id = $('Parse reel metadata').item.json.video_id; const meta = $('Gemini video copy').item.json.output; const m = $('Parse reel metadata').item.json.reel_meta; const d = m.upload_date || ''; const date = d.length===8 ? d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6,8) : new Date().toISOString().slice(0,10); const entry = { id, file: id+'.mp4', poster: id+'.jpg', title: meta.title, description: meta.description, date, duration: m.duration_string || '', instagram: m.webpage_url || $('Set reel URL').item.json.reel_url, category: meta.category || 'Patient Stories' }; lib.videos = [entry, ...(lib.videos||[])]; lib.updated = new Date().toISOString().slice(0,10); return JSON.stringify(lib, null, 2); })() }}",
                        "type": "string",
                    }
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(build_json)

    gh_put = node(
        "Update video-library.json",
        "n8n-nodes-base.github",
        [1980, 0],
        {
            "resource": "file",
            "operation": "edit",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "assets/data/video-library.json",
            "fileContent": "={{ $json.library_json }}",
            "commitMessage": "content: add video via Telegram bot",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_put)

    notify = node(
        "Telegram success",
        "n8n-nodes-base.telegram",
        [2200, 0],
        {
            "chatId": "={{ $('When called by router').item.json.chat_id }}",
            "text": "=Video published.\n\n{{ $('Gemini video copy').item.json.output.title }}\n\n{{ $env.GIV_SITE_URL }}/videos/",
        },
        type_version=1.2,
    )
    nodes.append(notify)

    connect(c, "When called by router", "Set reel URL")
    connect(c, "Set reel URL", "yt-dlp download")
    connect(c, "yt-dlp download", "Read info JSON")
    connect(c, "Read info JSON", "Parse reel metadata")
    wire_agent(c, "Gemini video copy", "Gemini video model", "Video copy parser", "Parse reel metadata")
    connect(c, "Gemini video copy", "Get video-library.json")
    connect(c, "Get video-library.json", "Prepend new video entry")
    connect(c, "Prepend new video entry", "Update video-library.json")
    connect(c, "Gemini video copy", "Upload MP4 to R2")
    connect(c, "Gemini video copy", "Upload poster to R2")
    connect(c, "Update video-library.json", "Telegram success")

    nodes.append(
        node(
            "Note: Video flow",
            "n8n-nodes-base.stickyNote",
            [-40, -180],
            {"content": "## Video publish\nInstagram URL → yt-dlp → Gemini English copy → R2 `library/` (S3 node) → `video-library.json` on GitHub.\n\nAdd **Read/Write File** nodes for MP4/JPG binaries before S3 uploads if Execute Command output needs wiring."},
            type_version=1,
        )
    )

    return workflow("GivSharifi — 02 Publish Video", nodes, c)


def build_blog_workflow() -> dict:
    nodes: list[dict] = []
    c: dict = {}

    trigger = node("When called by router", "n8n-nodes-base.executeWorkflowTrigger", [0, 0], type_version=1.1)
    nodes.append(trigger)

    has_image = node(
        "Has featured image?",
        "n8n-nodes-base.if",
        [220, 0],
        {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [
                    {
                        "id": nid(),
                        "leftValue": "={{ $json.photo_file_id }}",
                        "rightValue": "",
                        "operator": {"type": "string", "operation": "notEmpty"},
                    }
                ],
                "combinator": "and",
            }
        },
        type_version=2.2,
    )
    nodes.append(has_image)

    dl = node(
        "Download featured image",
        "n8n-nodes-base.telegram",
        [440, -120],
        {"resource": "file", "fileId": "={{ $('When called by router').item.json.photo_file_id }}"},
        type_version=1.2,
    )
    nodes.append(dl)

    prompt = (
        "=Draft (may be Persian or English):\n{{ $('When called by router').item.json.draft_text }}\n\n"
        "Create a full blog post JSON for Prof. Giv Sharifi's neurosurgery website.\n"
        "- All text in professional English\n"
        "- slug: lowercase hyphenated, max 60 chars\n"
        "- content: 6-10 blocks (paragraph, heading level 2, optional list)\n"
        "- tags: 5-8 SEO keywords\n"
        "- date: today ISO\n"
        "- featuredImagePath: assets/images/blog/{slug}.webp (use slug in path)"
    )
    stack, agent, model, parser = gemini_stack(
        "Gemini blog writer",
        "Gemini blog model",
        "Blog JSON parser",
        prompt,
        BLOG_SCHEMA,
        440,
    )
    nodes.extend(stack)

    gh_shell = node(
        "Get post HTML shell",
        "n8n-nodes-base.github",
        [880, 0],
        {
            "resource": "file",
            "operation": "get",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "blog/_post-shell.html",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_shell)

    gh_post = node(
        "Create post JSON",
        "n8n-nodes-base.github",
        [1100, -80],
        {
            "resource": "file",
            "operation": "create",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "={{ 'posts/data/' + $('Gemini blog writer').item.json.output.slug + '.json' }}",
            "fileContent": "={{ JSON.stringify(Object.assign($('Gemini blog writer').item.json.output, { author: { name: 'Prof. Giv Sharifi', title: 'Board-Certified Neurosurgeon', url: 'https://www.givsharifi.com/' }, featuredImage: '/' + $('Gemini blog writer').item.json.output.featuredImagePath }), null, 2) }}",
            "commitMessage": "content: add blog post via Telegram bot",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_post)

    gh_html = node(
        "Create blog HTML page",
        "n8n-nodes-base.github",
        [1100, 80],
        {
            "resource": "file",
            "operation": "create",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "={{ 'blog/' + $('Gemini blog writer').item.json.output.slug + '/index.html' }}",
            "fileContent": "={{ $('Get post HTML shell').item.json.content }}",
            "commitMessage": "content: add blog page shell via Telegram bot",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_html)

    gh_index = node(
        "Get posts index",
        "n8n-nodes-base.github",
        [1320, 0],
        {
            "resource": "file",
            "operation": "get",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "posts/data/index.json",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_index)

    update_index = node(
        "Prepend to index",
        "n8n-nodes-base.set",
        [1540, 0],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {
                        "id": nid(),
                        "name": "index_json",
                        "value": "={{ (() => { const idx = JSON.parse($json.content); const p = $('Gemini blog writer').item.json.output; idx.posts = [{ slug: p.slug, title: p.title, excerpt: p.excerpt, date: p.date, category: p.category, image: '/' + p.featuredImagePath }, ...(idx.posts||[])]; return JSON.stringify(idx, null, 2); })() }}",
                        "type": "string",
                    }
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(update_index)

    gh_index_put = node(
        "Update posts index",
        "n8n-nodes-base.github",
        [1760, 0],
        {
            "resource": "file",
            "operation": "edit",
            "owner": "={{ $env.GIV_GITHUB_OWNER }}",
            "repository": "={{ $env.GIV_GITHUB_REPO }}",
            "filePath": "posts/data/index.json",
            "fileContent": "={{ $json.index_json }}",
            "commitMessage": "content: update blog index via Telegram bot",
            "branch": "={{ $env.GIV_GITHUB_BRANCH || 'main' }}",
        },
        type_version=1.1,
    )
    nodes.append(gh_index_put)

    notify = node(
        "Telegram success",
        "n8n-nodes-base.telegram",
        [1980, 0],
        {
            "chatId": "={{ $('When called by router').item.json.chat_id }}",
            "text": "=Blog post published.\n\n{{ $('Gemini blog writer').item.json.output.title }}\n\n{{ $env.GIV_SITE_URL }}/blog/{{ $('Gemini blog writer').item.json.output.slug }}/",
        },
        type_version=1.2,
    )
    nodes.append(notify)

    connect(c, "When called by router", "Has featured image?")
    connect(c, "Has featured image?", "Download featured image", src_index=0)
    connect(c, "Has featured image?", "Gemini blog writer", src_index=1)
    connect(c, "Download featured image", "Gemini blog writer")
    connect(c, "Gemini blog model", "Gemini blog writer", ctype="ai_languageModel")
    connect(c, "Blog JSON parser", "Gemini blog writer", ctype="ai_outputParser")
    connect(c, "Gemini blog writer", "Get post HTML shell")
    connect(c, "Get post HTML shell", "Create post JSON")
    connect(c, "Get post HTML shell", "Create blog HTML page")
    connect(c, "Create post JSON", "Get posts index")
    connect(c, "Create blog HTML page", "Get posts index")
    connect(c, "Get posts index", "Prepend to index")
    connect(c, "Prepend to index", "Update posts index")
    connect(c, "Update posts index", "Telegram success")

    nodes.append(
        node(
            "Note: Blog flow",
            "n8n-nodes-base.stickyNote",
            [-40, -200],
            {"content": "## Blog publish\nDraft text → Gemini (full JSON) → GitHub post JSON + HTML shell + index.json.\n\nOptional: upload featured WebP to `assets/images/blog/` via GitHub node on the **true** branch of If."},
            type_version=1,
        )
    )

    return workflow("GivSharifi — 03 Publish Blog", nodes, c)


def build_router_workflow() -> dict:
    nodes: list[dict] = []
    c: dict = {}

    tg = node(
        "Telegram Trigger",
        "n8n-nodes-base.telegramTrigger",
        [0, 0],
        {"updates": ["message", "callback_query"]},
        type_version=1.1,
    )
    nodes.append(tg)

    auth = node(
        "Authorized chat?",
        "n8n-nodes-base.if",
        [220, 0],
        {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [
                    {
                        "id": nid(),
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

    route = node(
        "Route message type",
        "n8n-nodes-base.switch",
        [440, 0],
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
                                    "leftValue": "={{ $json.message?.photo ? 'yes' : 'no' }}",
                                    "rightValue": "yes",
                                    "operator": {"type": "string", "operation": "equals"},
                                }
                            ],
                            "combinator": "and",
                        },
                        "renameOutput": True,
                        "outputKey": "photo",
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.message?.text || '' }}",
                                    "rightValue": "instagram.com",
                                    "operator": {"type": "string", "operation": "contains"},
                                }
                            ],
                            "combinator": "and",
                        },
                        "renameOutput": True,
                        "outputKey": "video",
                    },
                    {
                        "conditions": {
                            "options": {"caseSensitive": False, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.message?.text || '' }}",
                                    "rightValue": "/blog",
                                    "operator": {"type": "string", "operation": "startsWith"},
                                }
                            ],
                            "combinator": "and",
                        },
                        "renameOutput": True,
                        "outputKey": "blog",
                    },
                ]
            },
            "options": {"fallbackOutput": "extra"},
        },
        type_version=3.2,
    )
    nodes.append(route)

    menu = node(
        "Send menu",
        "n8n-nodes-base.telegram",
        [660, -200],
        {
            "chatId": "={{ $json.message.chat.id }}",
            "text": "Prof. Giv Sharifi — Content Bot\n\n📷 Send a photo → gallery\n🎬 Send Instagram reel URL → videos\n📝 Send /blog then your draft text\n\nImages → GitHub | Videos → Cloudflare R2",
            "replyMarkup": "inlineKeyboard",
            "inlineKeyboard": {
                "rows": [
                    [{"text": "📷 Photo help", "callback_data": "help_photo"}],
                    [{"text": "🎬 Video help", "callback_data": "help_video"}],
                    [{"text": "📝 Blog help", "callback_data": "help_blog"}],
                ]
            },
        },
        type_version=1.2,
    )
    nodes.append(menu)

    prep_photo = node(
        "Prepare photo payload",
        "n8n-nodes-base.set",
        [660, 0],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {"id": nid(), "name": "chat_id", "value": "={{ $json.message.chat.id }}", "type": "number"},
                    {"id": nid(), "name": "photo_file_id", "value": "={{ $json.message.photo.slice(-1)[0].file_id }}", "type": "string"},
                    {"id": nid(), "name": "caption", "value": "={{ $json.message.caption || '' }}", "type": "string"},
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(prep_photo)

    exec_photo = node(
        "Run publish photo",
        "n8n-nodes-base.executeWorkflow",
        [880, 0],
        {"workflowId": "={{ $env.GIV_WF_PHOTO_ID }}", "mode": "each", "options": {}},
        type_version=1.2,
        notes="After import: set GIV_WF_PHOTO_ID to workflow ID of 01-publish-photo",
    )
    nodes.append(exec_photo)

    prep_video = node(
        "Prepare video payload",
        "n8n-nodes-base.set",
        [660, 160],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {"id": nid(), "name": "chat_id", "value": "={{ $json.message.chat.id }}", "type": "number"},
                    {"id": nid(), "name": "reel_url", "value": "={{ $json.message.text.trim() }}", "type": "string"},
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(prep_video)

    exec_video = node(
        "Run publish video",
        "n8n-nodes-base.executeWorkflow",
        [880, 160],
        {"workflowId": "={{ $env.GIV_WF_VIDEO_ID }}", "mode": "each", "options": {}},
        type_version=1.2,
        notes="Set GIV_WF_VIDEO_ID after import",
    )
    nodes.append(exec_video)

    prep_blog = node(
        "Prepare blog payload",
        "n8n-nodes-base.set",
        [660, 320],
        {
            "mode": "manual",
            "assignments": {
                "assignments": [
                    {"id": nid(), "name": "chat_id", "value": "={{ $json.message.chat.id }}", "type": "number"},
                    {"id": nid(), "name": "draft_text", "value": "={{ $json.message.text.replace(/^\\/blog\\s*/i, '').trim() }}", "type": "string"},
                    {"id": nid(), "name": "photo_file_id", "value": "={{ $json.message.photo ? $json.message.photo.slice(-1)[0].file_id : '' }}", "type": "string"},
                ]
            },
        },
        type_version=3.4,
    )
    nodes.append(prep_blog)

    exec_blog = node(
        "Run publish blog",
        "n8n-nodes-base.executeWorkflow",
        [880, 320],
        {"workflowId": "={{ $env.GIV_WF_BLOG_ID }}", "mode": "each", "options": {}},
        type_version=1.2,
        notes="Set GIV_WF_BLOG_ID after import",
    )
    nodes.append(exec_blog)

    help = node(
        "Send help",
        "n8n-nodes-base.telegram",
        [660, 480],
        {
            "chatId": "={{ $json.message.chat.id }}",
            "text": "Send:\n• Photo (with optional caption)\n• Instagram reel link\n• /blog Your article draft…",
        },
        type_version=1.2,
    )
    nodes.append(help)

    deny = node(
        "Unauthorized",
        "n8n-nodes-base.telegram",
        [440, 200],
        {
            "chatId": "={{ $json.message?.chat?.id || $json.callback_query?.message?.chat?.id }}",
            "text": "Unauthorized.",
        },
        type_version=1.2,
    )
    nodes.append(deny)

    connect(c, "Telegram Trigger", "Authorized chat?")
    connect(c, "Authorized chat?", "Route message type", src_index=0)
    connect(c, "Authorized chat?", "Unauthorized", src_index=1)
    connect(c, "Route message type", "Send menu", src_index=0)
    connect(c, "Route message type", "Prepare photo payload", src_index=1)
    connect(c, "Route message type", "Prepare video payload", src_index=2)
    connect(c, "Route message type", "Prepare blog payload", src_index=3)
    connect(c, "Route message type", "Send help", src_index=4)
    connect(c, "Prepare photo payload", "Run publish photo")
    connect(c, "Prepare video payload", "Run publish video")
    connect(c, "Prepare blog payload", "Run publish blog")

    nodes.append(
        node(
            "Note: Router",
            "n8n-nodes-base.stickyNote",
            [-40, -220],
            {"content": "## Telegram router\nImport sub-workflows first. Copy their workflow IDs into env vars:\n`GIV_WF_PHOTO_ID`, `GIV_WF_VIDEO_ID`, `GIV_WF_BLOG_ID`\n\nOr replace Execute Workflow nodes with manual workflow picker after import."},
            type_version=1,
        )
    )

    return workflow("GivSharifi — 00 Telegram Router", nodes, c)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "01-publish-photo.json": build_photo_workflow(),
        "02-publish-video.json": build_video_workflow(),
        "03-publish-blog.json": build_blog_workflow(),
        "00-telegram-router.json": build_router_workflow(),
    }
    for name, wf in files.items():
        path = OUT / name
        path.write_text(json.dumps(wf, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {path} ({len(wf['nodes'])} nodes)")


if __name__ == "__main__":
    main()
