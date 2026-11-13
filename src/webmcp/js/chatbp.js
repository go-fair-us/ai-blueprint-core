(() => {
  const SUGGESTIONS = [
    "What metadata does the Blueprint require?",
    "Which persistent identifiers should a repository use?",
    "How should datasets be cited?",
    "What is the minimum API pattern?",
  ];

  const logEl = () => document.getElementById("chat-log");
  const formEl = () => document.getElementById("chat-form");
  const inputEl = () => document.getElementById("chat-input");
  const sendEl = () => document.getElementById("chat-send");
  const statusEl = () => document.getElementById("chat-status");

  let busy = false;
  let narrativeOn = false;
  let started = false;

  function escapeHtml(text) {
    return String(text ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function renderMarkdown(text) {
    const escaped = escapeHtml(text);
    const withLinks = escaped.replace(
      /\[([^\]]+)\]\((\/[^)\s]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>',
    );
    const withBold = withLinks.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    const blocks = withBold.split(/\n{2,}/).map((block) => {
      const lines = block.split("\n");
      if (lines.every((line) => /^\s*[-*]\s+/.test(line))) {
        const items = lines
          .map((line) => `<li>${line.replace(/^\s*[-*]\s+/, "")}</li>`)
          .join("");
        return `<ul>${items}</ul>`;
      }
      return `<p>${lines.join("<br>")}</p>`;
    });
    return blocks.join("");
  }

  function setStatus(text) {
    const el = statusEl();
    if (!el) return;
    if (!text) {
      el.hidden = true;
      el.textContent = "";
      return;
    }
    el.hidden = false;
    el.textContent = text;
  }

  function resizeInput() {
    const input = inputEl();
    if (!input) return;
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 136)}px`;
  }

  function scrollLog() {
    const log = logEl();
    if (log) log.scrollTop = log.scrollHeight;
  }

  function welcome() {
    const log = logEl();
    if (!log || log.dataset.ready) return;
    log.dataset.ready = "1";
    log.innerHTML = `
      <div class="chat-empty">
        <h1>Ask the Blueprint</h1>
        <p>
          Ask a question in plain language. Matching handbook pages are gathered
          first, then turned into a short answer with links you can open to read
          the details.
        </p>
        <div class="suggestions">
          ${SUGGESTIONS.map(
            (s) =>
              `<button type="button" data-suggest="${escapeHtml(s)}">${escapeHtml(s)}</button>`,
          ).join("")}
        </div>
      </div>
    `;
    log.querySelectorAll("[data-suggest]").forEach((btn) => {
      btn.addEventListener("click", () => submit(btn.dataset.suggest));
    });
  }

  function ensureThread() {
    const log = logEl();
    if (!log) return log;
    if (!log.classList.contains("has-messages")) {
      log.classList.add("has-messages");
      log.innerHTML = "";
    }
    return log;
  }

  function appendUser(text) {
    const log = ensureThread();
    const row = document.createElement("div");
    row.className = "msg msg-user";
    row.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
    log.appendChild(row);
    scrollLog();
  }

  function appendPending() {
    const log = ensureThread();
    const row = document.createElement("div");
    row.className = "msg msg-assistant msg-pending";
    row.innerHTML = `<div class="dots" aria-hidden="true"><span></span><span></span><span></span></div>`;
    log.appendChild(row);
    scrollLog();
    return row;
  }

  function sourceCards(passages) {
    const usable = (passages || []).filter((p) => p && (p.href || p.slug));
    if (!usable.length) return "";
    const cards = usable
      .map((p) => {
        const href = p.href || `/topics/${p.slug}.html`;
        const title = p.title || p.slug;
        const summary = p.summary || p.excerpt || "Open this handbook page.";
        return `<a class="source-card" href="${escapeHtml(href)}" target="_blank" rel="noopener">
          <strong>${escapeHtml(title)}</strong>
          <span>${escapeHtml(summary)}</span>
        </a>`;
      })
      .join("");
    return `<div class="sources"><p class="sources-label">Read more</p>${cards}</div>`;
  }

  function fillAssistant(row, markdown, passages) {
    row.classList.remove("msg-pending");
    row.innerHTML = `<div class="prose">${renderMarkdown(markdown)}</div>${sourceCards(passages)}`;
    scrollLog();
  }

  function unwrap(result) {
    if (result == null) return result;
    if (typeof result === "string") {
      try {
        return JSON.parse(result);
      } catch {
        return { text: result };
      }
    }
    if (Array.isArray(result.content) && result.content[0] && result.content[0].text) {
      try {
        return JSON.parse(result.content[0].text);
      } catch {
        return result;
      }
    }
    return result;
  }

  async function localTool(name, args) {
    const catalog = window.HandbookCatalog;
    const topics = await catalog.topics();
    if (name === "list_topics") {
      return topics.map(({ slug, title, href, summary }) => ({ slug, title, href, summary }));
    }
    if (name === "search_topics") {
      const q = String((args && args.query) || "").trim();
      if (!q) return { error: "Provide a non-empty query." };
      const hits = catalog.searchTopics(topics, q).map(({ slug, title, href, summary }) => ({
        slug,
        title,
        href,
        summary,
      }));
      return { query: q, count: hits.length, hits };
    }
    if (name === "get_topic") {
      const slug = args && args.slug;
      const topic = topics.find((t) => t.slug === slug);
      if (!topic) return { error: `Unknown slug "${slug}".` };
      return topic;
    }
    if (name === "navigate_to_topic") {
      const slug = args && args.slug;
      const topic = topics.find((t) => t.slug === slug);
      if (!topic) return { error: `Unknown slug "${slug}".` };
      return { navigating: topic.href, title: topic.title };
    }
    return { error: `Unknown tool "${name}".` };
  }

  async function callTool(name, args) {
    const ctx = window.WebMCPHandbook && window.WebMCPHandbook.getModelContext();
    if (ctx && typeof ctx.executeTool === "function" && typeof ctx.getTools === "function") {
      try {
        const tools = await ctx.getTools();
        const tool = (tools || []).find((t) => t.name === name);
        if (tool) {
          try {
            return unwrap(await ctx.executeTool(tool, args || {}));
          } catch {
            return unwrap(await ctx.executeTool(tool, JSON.stringify(args || {})));
          }
        }
      } catch (err) {
        console.debug("WebMCP executeTool unavailable, using local catalog", name, err);
      }
    }
    return localTool(name, args);
  }

  async function retrieve(question) {
    const search = await callTool("search_topics", { query: question });
    const hits = Array.isArray(search && search.hits) ? search.hits.slice(0, 6) : [];
    const details = [];
    for (const hit of hits) {
      const topic = await callTool("get_topic", { slug: hit.slug });
      if (topic && !topic.error) details.push(topic);
    }
    if (!details.length) {
      const listed = await callTool("list_topics", {});
      const all = Array.isArray(listed) ? listed : listed && listed.topics;
      return { passages: Array.isArray(all) ? all : [], matched: false };
    }
    return { passages: details, matched: true };
  }

  function localNarrative(question, passages, matched) {
    if (!matched || !passages.length) {
      const names = (passages || [])
        .slice(0, 6)
        .map((p) => `[${p.title}](${p.href || `/topics/${p.slug}.html`})`)
        .join(", ");
      return (
        "I could not find a handbook page that directly answers that. " +
        "The Blueprint pages on this site cover " +
        (names || "overview, metadata, identifiers, APIs, citation, and outreach") +
        ". Try one of those topics, or rephrase with a Blueprint term such as DOI, JSON-LD, or Contact Point."
      );
    }
    const blocks = passages.map((p) => {
      const href = p.href || `/topics/${p.slug}.html`;
      const body = p.excerpt || p.summary || "";
      return `**[${p.title}](${href})** — ${body}`;
    });
    return (
      `Here is what the handbook says that relates to “${question}”.\n\n` +
      blocks.join("\n\n") +
      "\n\nOpen a page below for the full guidance."
    );
  }

  async function writeNarrative(question, passages, matched) {
    if (!narrativeOn) return localNarrative(question, passages, matched);
    try {
      const res = await fetch("/api/narrative", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, passages }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.text) {
        console.debug("narrative fallback", res.status, data.error);
        return localNarrative(question, passages, matched);
      }
      return data.text;
    } catch (err) {
      console.debug("narrative request failed", err);
      return localNarrative(question, passages, matched);
    }
  }

  async function submit(text) {
    const q = String(text || "").trim();
    if (!q || busy) return;
    busy = true;
    const send = sendEl();
    const input = inputEl();
    if (send) send.disabled = true;
    if (input && input.value === q) input.value = "";
    resizeInput();
    appendUser(q);
    const pending = appendPending();
    setStatus("Looking through the handbook…");
    try {
      const retrieved = await retrieve(q);
      setStatus("Writing a short answer…");
      const narrative = await writeNarrative(q, retrieved.passages, retrieved.matched);
      fillAssistant(pending, narrative, retrieved.matched ? retrieved.passages : []);
    } catch (err) {
      fillAssistant(
        pending,
        "Something went wrong while searching the handbook. Try again in a moment.",
        [],
      );
      console.warn(err);
    } finally {
      busy = false;
      if (send) send.disabled = false;
      setStatus("");
      inputEl()?.focus();
    }
  }

  async function loadStatus() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();
      narrativeOn = Boolean(data && data.narrative);
    } catch {
      narrativeOn = false;
    }
  }

  function bind() {
    formEl()?.addEventListener("submit", (ev) => {
      ev.preventDefault();
      submit(inputEl()?.value);
    });
    inputEl()?.addEventListener("input", resizeInput);
    inputEl()?.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && !ev.shiftKey) {
        ev.preventDefault();
        formEl()?.requestSubmit();
      }
    });
  }

  async function start() {
    if (started) return;
    started = true;
    if (window.WebMCPHandbook && window.WebMCPHandbook.paintBadge) {
      window.WebMCPHandbook.paintBadge();
    }
    welcome();
    bind();
    resizeInput();
    await loadStatus();
  }

  document.addEventListener("webmcp-site-tools-ready", start, { once: true });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setTimeout(start, 0), { once: true });
  } else {
    setTimeout(start, 0);
  }
})();
