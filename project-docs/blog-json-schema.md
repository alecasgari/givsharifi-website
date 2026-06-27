# Blog JSON Schema (for N8N)

## Index file: `posts/data/index.json`

```json
{
  "posts": [
    {
      "slug": "my-new-post",
      "title": "Post Title",
      "excerpt": "Short summary for blog listing",
      "date": "2026-06-25",
      "category": "Neurosurgery",
      "image": "/assets/images/blog/my-new-post.webp"
    }
  ]
}
```

## Single post: `posts/data/{slug}.json`

```json
{
  "slug": "my-new-post",
  "title": "Post Title",
  "metaDescription": "SEO description (max ~160 chars)",
  "excerpt": "Lead paragraph shown under the featured image",
  "date": "2026-06-25",
  "updatedDate": "2026-06-26",
  "category": "Spinal Surgery",
  "tags": ["spinal surgery", "MISS", "neurosurgery Dubai"],
  "author": {
    "name": "Prof. Giv Sharifi",
    "title": "Board-Certified Neurosurgeon",
    "url": "https://www.givsharifi.com/"
  },
  "featuredImage": "/assets/images/blog/my-new-post.webp",
  "readingTimeMinutes": 7,
  "content": [
    { "type": "paragraph", "text": "Body text..." },
    { "type": "heading", "level": 2, "text": "Section Title" },
    { "type": "list", "items": ["Item 1", "Item 2"] },
    { "type": "ordered-list", "items": ["Step 1", "Step 2"] },
    { "type": "image", "src": "/assets/images/...", "alt": "Description" },
    { "type": "blockquote", "text": "Quoted text" },
    { "type": "cta", "text": "Link label", "href": "/spinal-surgery/" },
    { "type": "html", "html": "<p>Trusted HTML from N8N only</p>" }
  ]
}
```

## Categories → sidebar service link

| category | sidebar link |
|----------|----------------|
| Spinal Surgery | `/spinal-surgery/` |
| Brain Surgery | `/brain-surgery/` |
| Neurosurgery | `/brain-surgery/` |

## After adding a new post via N8N

1. Write `{slug}.json` to `posts/data/`
2. Add entry to `posts/data/index.json`
3. Copy `blog/_post-shell.html` to `blog/{slug}/index.html`
4. Update `sitemap.xml`
5. Git push → GitHub Pages deploys

## Content block types

| type | fields |
|------|--------|
| `paragraph` | `text` |
| `heading` | `text`, `level` (2–4) |
| `list` | `items` (array of strings) |
| `ordered-list` | `items` |
| `image` | `src`, `alt` |
| `blockquote` | `text` |
| `cta` | `text`, `href` (internal link in article body) |
| `html` | `html` (trusted content from N8N only) |

## Tags

- Array of strings in `{slug}.json`
- Rendered at end of post **without links** (SEO keywords only)
- Also included in `BlogPosting` schema `keywords`

## Page template

- Shell: `blog/_post-shell.html`
- Renderer: `assets/js/blog-single.js`
- Styles: `assets/css/blog.css`
- JSON drives all content; shell is identical for every post
