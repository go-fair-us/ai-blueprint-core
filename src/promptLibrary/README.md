# NIAID Blueprint Prompt Library

A clean, static web app for discovering and using high-quality LLM prompts that
help implement the **NIAID Blueprint for Including Digital Objects in the NIAID
Data Ecosystem** (and FAIR principles more broadly).

Browse a hierarchical tree of Blueprint topics, pick a ready-to-use prompt, and
send it to your preferred AI assistant with one click.

## Features

- **Sidebar tree navigation** — drill down from broad categories to concrete prompts.
- **One-click actions** on every prompt:
  - **Copy** to clipboard (with a success toast)
  - **Claude** (web) — opens `https://claude.ai/new` pre-filled
  - **Claude Desktop** — opens the desktop app via `claude://`
  - **ChatGPT** — opens `https://chatgpt.com` pre-filled
  - **OpenWebUI** — opens `http://localhost:8080` pre-filled (local instance)
- **Real-time search** that filters the tree.
- **Responsive** — the sidebar becomes a slide-in drawer on mobile.
- **100% data-driven** — all content lives in `data.json`.

## Running locally

Because the app fetches `data.json`, it must be served over HTTP (opening
`index.html` directly with `file://` will be blocked by the browser).

```bash
# from this directory
python3 -m http.server 8000
# then open http://localhost:8000
```

Any static file server works (`npx serve`, `caddy`, nginx, etc.).

## Deploying

The site is fully static — no build step. Deploy the folder as-is to GitHub
Pages, Netlify, Cloudflare Pages, or any static host.

## Adding or editing content

There are two ways to manage content:

1. **Edit the OKF bundle** in [`okf-bundle/`](./okf-bundle) (recommended) and
   regenerate `data.json` — see [Content source: the OKF bundle](#content-source-the-okf-bundle).
2. **Edit `data.json` directly** — the app reads this file at runtime; the
   structure is documented below.

> **Note:** `data.json` is a **generated artifact** produced from `okf-bundle/`.
> If you hand-edit `data.json`, your changes will be overwritten the next time
> `build_data.py` runs. Prefer editing the bundle.

Everything the app renders is driven by [`data.json`](./data.json) — **no coding required**.

```jsonc
{
  "meta": { "title": "...", "version": "0.1", "lastUpdated": "2026-07-06" },
  "categories": [
    {
      "id": "unique-id",
      "title": "Category name",
      "description": "What this category covers.",
      "children": [
        {
          "id": "topic-id",
          "title": "Sub-topic",
          "description": "...",
          "prompts": [
            {
              "id": "prompt-id",
              "title": "Short prompt title",
              "description": "What this prompt does.",
              "prompt": "The full prompt text sent to the LLM. Use \\n for newlines."
            }
          ]
        }
      ]
    }
  ]
}
```

**Rules:**

- `categories` / `children` can nest arbitrarily deep (2–3 levels in practice).
- A node can hold `children`, `prompts`, or both.
- Only leaf nodes carry `prompts[]`.
- Every prompt needs `id`, `title`, `description`, and `prompt`.
- `id`s should be unique — they double as deep-link anchors (e.g. `#prompt-id`).

## Content source: the OKF bundle

The prompts also live as an [Open Knowledge Format (OKF) v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
bundle in [`okf-bundle/`](./okf-bundle) — a plain directory of Markdown files
with YAML frontmatter. This is the **editable source of truth**; `data.json` is
generated from it by [`build_data.py`](./build_data.py).

How the bundle maps to `data.json`:

- **Root `index.md`** — frontmatter holds `meta` (title, description, version,
  lastUpdated, source); its link list defines the top-level categories, in order.
- **Each subdirectory** → a category node. Its title is the folder `index.md`'s
  `#` heading; its description is the link text in the parent's `index.md`.
- **Each concept `*.md`** → a prompt. `title`/`description` come from frontmatter;
  the prompt text is the body under `# Prompt` (`{{placeholders}}` are preserved).
- **Ordering** follows the link order inside each `index.md`, not the filesystem.
- Prompt **ids** are the bundle-relative path (e.g. `citation-outreach/how-to-cite`).

To add a prompt: drop a new `*.md` file in the right category folder and add a
line linking to it in that folder's `index.md`, then regenerate.

### Regenerating `data.json`

```bash
# from this directory (stdlib only — no dependencies)
python3 build_data.py                     # reads ./okf-bundle → writes ./data.json

# optional overrides
python3 build_data.py --bundle ./okf-bundle --output ./data.json
```

The script prints a summary (category and prompt counts). It only *reads* the
bundle and *writes* `data.json`, so it is safe to re-run.

## Configuration

The LLM target URLs are defined at the top of [`app.js`](./app.js) in the
`TARGETS` object. To point OpenWebUI at a different host/port, edit that entry.

## File structure

| File / dir     | Responsibility                                             |
|----------------|------------------------------------------------------------|
| `index.html`   | Layout, Tailwind (CDN), top bar, sidebar, main panel shell |
| `app.js`       | Load data, render tree, selection, search, LLM actions     |
| `okf-bundle/`  | **Source of truth** — prompts as an OKF v0.1 Markdown bundle |
| `build_data.py`| Walks `okf-bundle/` and generates `data.json`              |
| `data.json`    | Generated content — categories, topics, and prompts        |
| `styles.css`   | Small custom styles on top of Tailwind                     |

## Tech stack

HTML + [Tailwind CSS](https://tailwindcss.com) (via CDN) + vanilla JavaScript.
No frameworks, no build step, no backend.
