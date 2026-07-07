# SPEC.md — NIAID Blueprint Prompt Library

**Project Name:** Blueprint Prompt Explorer  
**Version:** 0.1 (MVP)  
**Date:** 2026-07-06  
**Status:** Specification for initial build

---

## 1. Overview

A clean, maintainable, static web application that helps users discover and use high-quality prompts related to the **NIAID Blueprint for Including Digital Objects in the NIAID Data Ecosystem** (and FAIR principles more broadly).

The site uses a **3-level hierarchical drill-down**:
1. Broad category (e.g., Metadata Schema, Persistent Identifiers)
2. Narrower topic / element
3. Concrete, ready-to-use example prompt

Users can then take action on any prompt:
- Copy to clipboard
- Open pre-filled in Claude (web)
- Open pre-filled in Claude Desktop
- Open pre-filled in ChatGPT
- Open pre-filled in OpenWebUI (local)

The entire site is driven by a single `data.json` file so non-developers can easily add or update content.

---

## 2. Goals

- Make the NIAID Blueprint actionable through high-quality LLM prompts.
- Provide a pleasant, fast, browsable experience (sidebar tree navigation).
- Keep the project extremely simple to maintain and extend (static site + `data.json`).
- Support the most popular LLM interfaces used by researchers and data stewards.
- Be mobile-friendly from day one.

---

## 3. User Experience & Key Flows

### Primary Flow
1. User lands on the site.
2. Sees a **collapsible sidebar tree** on the left (Broad → Narrow topics).
3. Clicks items in the tree to expand/collapse folders.
4. Clicks a **leaf node** (prompt) → Main panel updates with:
   - Prompt title
   - Short description / context from the Blueprint
   - The full prompt text (in a readable code block)
   - Action buttons (Copy + 4 LLM targets)
5. User clicks a button → prompt is either copied or the target chat interface opens with the prompt pre-filled.

### Secondary Features (MVP)
- Global search bar (filters the tree in real time)
- "Copy prompt" with success toast
- Responsive layout (sidebar becomes a slide-in drawer on mobile)
- Clean, professional, documentation-like aesthetic

---

## 4. Data Model (`data.json`)

The site is 100% driven by `data.json`. Suggested structure:

```json
{
  "meta": {
    "title": "NIAID Blueprint Prompt Library",
    "version": "0.1",
    "lastUpdated": "2026-07-06"
  },
  "categories": [
    {
      "id": "metadata-schema",
      "title": "NIAID Minimal Metadata Schema",
      "description": "Core metadata elements required or recommended by the Blueprint.",
      "children": [
        {
          "id": "author",
          "title": "author (Person or Organization)",
          "description": "How to properly represent creators with ORCID and ROR.",
          "prompts": [
            {
              "id": "author-orcid-ror",
              "title": "Generate compliant author metadata",
              "description": "Creates properly formatted author entries following NIAID Blueprint guidance, including ORCID and ROR identifiers.",
              "prompt": "You are an expert in the NIAID Blueprint for Digital Objects...\n\nGiven the following digital object description, generate the `author` metadata element..."
            }
          ]
        }
        // more sub-topics...
      ]
    },
    {
      "id": "pids",
      "title": "Persistent Identifiers (PIDs)",
      ...
    }
  ]
}
```

**Rules:**
- `categories` can nest arbitrarily deep (we will use 2–3 levels in practice).
- Only leaf nodes contain `prompts[]`.
- Every prompt has: `id`, `title`, `description`, `prompt` (the actual text to send to the LLM).

---

## 5. UI Layout & Components

### Desktop Layout
- **Left sidebar** (fixed width, ~280–320px): Collapsible tree navigation
- **Main content area**: Detail view for the selected prompt
- **Top bar**: Logo + global search input

### Mobile Layout
- Top bar with hamburger menu
- Tapping hamburger opens the tree as a **slide-in drawer** (full height, overlay)
- Main content takes full width when drawer is closed

### Tree Navigation Behavior
- Folders (categories with `children`) are collapsible/expandable.
- Clicking a folder only expands/collapses (does not load content).
- Clicking a prompt leaf loads it into the main panel and highlights it.
- Visual indicators: chevrons for folders, document icon for prompts.
- Search filters the visible tree nodes in real time (client-side).

### Main Panel (when a prompt is selected)
- Breadcrumb or path (optional but nice)
- Prompt title (large, clear)
- Short description
- Full prompt in a `<pre><code>` block with good wrapping and copy affordance
- Row of action buttons:
  - **Copy to clipboard**
  - **Claude** (web)
  - **Claude Desktop**
  - **ChatGPT**
  - **OpenWebUI**

---

## 6. LLM Integration Details

All buttons that open external interfaces will:

1. URL-encode the prompt text.
2. Open in a new tab (`_blank`).

**Exact targets:**

| Button            | URL Pattern                                      | Notes |
|-------------------|--------------------------------------------------|-------|
| **Claude (web)**     | `https://claude.ai/new?q={encodedPrompt}`       | Opens new chat, prompt pre-filled |
| **Claude Desktop**   | `claude://claude.ai/new?q={encodedPrompt}`      | Opens Claude Desktop app if installed |
| **ChatGPT**          | `https://chatgpt.com/?q={encodedPrompt}`        | Pre-fills input box |
| **OpenWebUI**        | `http://localhost:8080/?q={encodedPrompt}`      | Assumes default local OpenWebUI port. User can change later. |

**Copy button**: Uses `navigator.clipboard.writeText()` + shows a temporary success toast.

---

## 7. Technical Stack (MVP)

- **HTML + Tailwind CSS** (via CDN for maximum simplicity)
- **Vanilla JavaScript** (no frameworks)
- Single `data.json` file
- No build step required for v1
- Fully static — can be hosted on GitHub Pages, Netlify, Cloudflare Pages, or any static host

**File structure (proposed):**
```
/
├── index.html
├── app.js
├── data.json
├── styles.css          (optional custom styles on top of Tailwind)
└── README.md
```

---

## 8. Non-Functional Requirements

- **Performance**: Loads instantly. Tree rendering and search must feel snappy even with 50–100 prompts.
- **Accessibility**: Reasonable keyboard navigation and ARIA labels on the tree (MVP can be good but not perfect).
- **Mobile**: Fully usable on phones and tablets.
- **Maintainability**: Adding a new prompt or category should only require editing `data.json`.
- **No backend** in v1.

---

## 9. Out of Scope (for MVP)

- User accounts / saved prompts / favorites
- Prompt versioning or editing in the UI
- Analytics
- Dark mode toggle (can add later)
- Advanced filtering by tags
- Exporting collections of prompts

These can be added in future phases if needed.

---

## 10. Success Criteria

- User can browse the full hierarchy in under 10 seconds.
- Any prompt can be sent to Claude or ChatGPT with **one or two clicks**.
- A data steward with no coding experience can add a new prompt by editing only `data.json`.
- The site works well on both desktop and mobile.

---

*End of Specification*