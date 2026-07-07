# PLAN.md — NIAID Blueprint Prompt Library

**Project:** Blueprint Prompt Explorer  
**Goal:** Build a clean, data-driven static site with sidebar tree navigation and one-click prompt loading into multiple LLM interfaces.  
**Approach:** Small multi-file static site (HTML + Tailwind CDN + vanilla JS + `data.json`)

---

## Phase Overview

| Phase | Focus                          | Estimated Effort | Deliverable                     |
|-------|--------------------------------|------------------|---------------------------------|
| 0     | Project setup & data model     | Low              | Folder structure + sample data  |
| 1     | Core layout & sidebar tree     | Medium           | Working collapsible tree        |
| 2     | Main panel + prompt display    | Medium           | Detail view with prompt text    |
| 3     | LLM action buttons             | Low–Medium       | All 5 buttons functional        |
| 4     | Polish, search, mobile, seed   | Medium           | Search, responsive drawer, real content from Blueprint |

---

## Phase 0: Project Setup & Data Model

**Tasks:**
- Create project folder with the following structure:
  ```
  blueprint-prompts/
  ├── index.html
  ├── app.js
  ├── data.json
  ├── styles.css          (optional)
  └── README.md
  ```
- Define the final `data.json` schema in SPEC.md and create an initial version with 4–6 seeded entries pulled from the NIAID Blueprint (Metadata Schema elements, PIDs, APIs, etc.).
- Add a few realistic prompts as examples.
- Decide on Tailwind version (CDN link for v4 or latest stable).

**Deliverable:** Working skeleton with `data.json` loaded and console logging the structure.

---

## Phase 1: Core Layout & Sidebar Tree Navigation

**Tasks:**
- Build responsive layout in `index.html`:
  - Top navigation bar (logo + search input)
  - Left sidebar (desktop) / hamburger + drawer (mobile)
  - Main content area
- Implement recursive tree rendering from `data.json` using vanilla JS.
- Add expand/collapse behavior with chevrons.
- Highlight the currently selected prompt.
- Make the sidebar scrollable and visually clean (Tailwind classes).

**Mobile consideration:** Use a hidden checkbox + CSS or simple JS to toggle a full-screen drawer on small screens.

**Deliverable:** Interactive, collapsible sidebar tree that works on desktop and mobile.

---

## Phase 2: Main Panel & Prompt Display

**Tasks:**
- When a prompt leaf is clicked:
  - Clear previous content in main panel
  - Render: title, short description, full prompt in a styled `<pre><code>` block
  - Show action button row
- Add basic breadcrumb or "You are viewing: Category > Sub-topic" text.
- Handle the case when nothing is selected (show welcome / instructions panel).

**Deliverable:** Clicking any prompt in the tree populates the main panel correctly.

---

## Phase 3: LLM Action Buttons

**Tasks:**
- Implement the five buttons:
  1. **Copy to clipboard** → `navigator.clipboard.writeText()` + toast notification
  2. **Claude (web)** → `https://claude.ai/new?q=${encodeURIComponent(prompt)}`
  3. **Claude Desktop** → `claude://claude.ai/new?q=${encodeURIComponent(prompt)}`
  4. **ChatGPT** → `https://chatgpt.com/?q=${encodeURIComponent(prompt)}`
  5. **OpenWebUI** → `http://localhost:8080/?q=${encodeURIComponent(prompt)}` (make the base URL configurable later if needed)
- All external buttons open in a new tab (`window.open(..., '_blank')`).
- Add subtle hover states and icons (can use inline SVG or Heroicons via CDN if desired).

**Deliverable:** All action buttons work as specified in SPEC.md.

---

## Phase 4: Polish, Search, Mobile Refinement & Content Seeding

**Tasks:**
- Add real-time global search that filters the tree (hide non-matching nodes).
- Improve mobile experience (test drawer behavior, touch targets).
- Seed `data.json` with meaningful content from the NIAID Blueprint:
  - Minimal Metadata Schema (several key elements)
  - Persistent Identifiers section
  - Minimal API requirements
  - Citation guidance
  - Possibly one or two from the FAIR questionnaire
- Add a small footer with "Edit on GitHub" or "Contribute via data.json" note.
- Basic accessibility improvements (ARIA on tree items).
- Final visual polish (spacing, typography, colors that feel professional and trustworthy).

**Deliverable:** Production-ready MVP that looks good and is useful.

---

## File Responsibilities

| File         | Responsibility                                      |
|--------------|-----------------------------------------------------|
| `index.html` | Overall layout, Tailwind link, initial structure    |
| `app.js`     | All logic: load data, render tree, handle clicks, search, LLM actions |
| `data.json`  | All content — categories, sub-topics, and prompts   |
| `styles.css` | Only custom CSS that Tailwind cannot easily handle (optional) |

---

## Recommended Order of Implementation

1. Set up files + load `data.json` and render a basic tree (Phase 0 + start of 1)
2. Make the tree interactive (expand/collapse + selection)
3. Build the main detail panel
4. Wire up the action buttons (start with Copy, then the URL ones)
5. Add search
6. Make it mobile-friendly
7. Seed real Blueprint content and test end-to-end

---

## Risks & Mitigations

- **Tree rendering complexity** → Keep the data depth shallow (max 3 levels) in v1. Use a simple recursive function.
- **Mobile sidebar** → Use a proven pattern (Tailwind + JS toggle or `<details>` for very simple version).
- **Long prompts** → Use `white-space: pre-wrap` and a max-height with scroll on the prompt block.
- **OpenWebUI port** → Document clearly that users may need to change `localhost:8080`.

---

## Future Enhancements (Post-MVP)

- Dark mode
- Favorites / "My Prompts" section (localStorage)
- Tags + faceted filtering
- Ability to edit prompts in-browser (with export)
- Multiple OpenWebUI instances / custom endpoints
- Export selected prompts as a JSON collection

---

## Success Metrics for v1

- A user can find a relevant prompt and send it to Claude in **under 30 seconds**.
- Adding a new prompt only requires editing `data.json`.
- The site works smoothly on both desktop and mobile.

---

*This plan is intentionally lightweight. The goal is a useful, beautiful, and extremely maintainable tool.*