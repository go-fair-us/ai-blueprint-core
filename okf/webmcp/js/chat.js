(() => {
  const SUGGESTIONS = [
    "Show me material related to citation",
    "Open metadata requirements",
    "What tags can I search?",
    "JSON-LD",
    "atomic 63",
    "What am I looking at?",
  ];

  const logEl = () => document.getElementById("chat-log");
  const resultsEl = () => document.getElementById("search-results");
  const formEl = () => document.getElementById("chat-form");
  const inputEl = () => document.getElementById("chat-input");

  function escapeHtml(text) {
    return String(text ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function setResults(html) {
    const box = resultsEl();
    if (!box) return null;
    box.innerHTML = html;
    box.scrollTop = 0;
    return box;
  }

  function appendActivity(query, tool) {
    const log = logEl();
    if (!log) return;
    const line = document.createElement("div");
    line.className = "activity-line";
    line.innerHTML = `<span class="mono">${escapeHtml(tool || "…")}</span><span class="q">${escapeHtml(query)}</span>`;
    log.appendChild(line);
    log.scrollTop = log.scrollHeight;
  }

  function renderHits(hits) {
    if (!hits.length) return `<p>No matches.</p>`;
    return hits
      .map((hit) => {
        const meta = hit.kind === "atomic"
          ? `${hit.parent_id} · atomic ${hit.atomic_number}`
          : hit.id;
        return `<button type="button" class="hit" data-id="${escapeHtml(hit.id)}" data-atomic="${hit.atomic_number || ""}">
          <div class="hit-title">${escapeHtml(hit.title)}</div>
          <div class="hit-meta">${escapeHtml(meta)}</div>
          ${hit.snippet ? `<div class="hit-snip">${escapeHtml(hit.snippet)}</div>` : ""}
        </button>`;
      })
      .join("");
  }

  function bindHits(container) {
    container.querySelectorAll(".hit").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        const atomic = btn.dataset.atomic ? Number(btn.dataset.atomic) : null;
        window.OkfApp.open(id, { atomic });
      });
    });
  }

  function welcome() {
    const box = resultsEl();
    if (!box || box.dataset.ready) return;
    box.dataset.ready = "1";
    const html = `<p class="tool-name">Ask the page</p>
      <p>Type a sentence. The chat picks a WebMCP tool (<code>search_okf</code>, <code>open_concept</code>, <code>get_atomic</code>, …) and shows the result here. Each new search replaces this panel.</p>
      <div class="suggestions">${SUGGESTIONS.map((s) => `<button type="button" data-suggest="${escapeHtml(s)}">${escapeHtml(s)}</button>`).join("")}</div>`;
    setResults(html);
    box.querySelectorAll("[data-suggest]").forEach((btn) => {
      btn.addEventListener("click", () => submit(btn.dataset.suggest));
    });
  }

  function formatArgs(args) {
    if (!args || !Object.keys(args).length) return "";
    const bits = Object.entries(args)
      .filter(([, v]) => v !== undefined && v !== null && v !== "")
      .map(([k, v]) => `${k}=${typeof v === "object" ? JSON.stringify(v) : v}`);
    return bits.length ? ` · ${escapeHtml(bits.join(" · "))}` : "";
  }

  function asHitsFromConcepts(list) {
    return (list || []).map((c) => ({
      id: c.id,
      title: c.title || c.id,
      kind: "concept",
      snippet: c.description || "",
      atomic_number: null,
    }));
  }

  function renderResult(tool, result) {
    if (!result) return `<p>No result.</p>`;
    if (result.error) return `<p>${escapeHtml(result.error)}</p>`;

    if (tool === "search_okf") {
      const hits = result.hits || [];
      let html = `<p>${result.count || 0} hit${result.count === 1 ? "" : "s"}${result.total && result.total > result.count ? ` (of ${result.total})` : ""}.`;
      if (result.opened) html += ` Opened <code>${escapeHtml(result.opened)}</code>.`;
      html += `</p>${renderHits(hits)}`;
      return html;
    }
    if (tool === "get_atomic") {
      return `<p>Opened <code>${escapeHtml(result.parent_id)}</code> at atomic ${result.number}.</p><p>${escapeHtml(result.text)}</p>`;
    }
    if (tool === "open_concept") {
      return `<p>Opened <code>${escapeHtml(result.opened)}</code> — ${escapeHtml(result.title || "")}.</p>`;
    }
    if (tool === "list_concepts") {
      const hits = asHitsFromConcepts(Array.isArray(result) ? result : result.concepts);
      return `<p>${hits.length} concept${hits.length === 1 ? "" : "s"}.</p>${renderHits(hits)}`;
    }
    if (tool === "list_atomics") {
      const rows = Array.isArray(result) ? result : [];
      const hits = rows.map((a) => ({
        id: a.parent_id,
        title: `Atomic ${a.number}`,
        kind: "atomic",
        snippet: a.text,
        atomic_number: a.number,
      }));
      return `<p>${hits.length} atomic claim${hits.length === 1 ? "" : "s"}.</p>${renderHits(hits)}`;
    }
    if (tool === "get_related") {
      const to = asHitsFromConcepts(result.links_to);
      const from = asHitsFromConcepts(result.linked_from);
      let html = `<p>Related to <code>${escapeHtml(result.id)}</code>.</p>`;
      if (to.length) html += `<p>See also</p>${renderHits(to)}`;
      if (from.length) html += `<p>Cited by</p>${renderHits(from)}`;
      if (!to.length && !from.length) html += `<p>No in-bundle links.</p>`;
      return html;
    }
    if (tool === "get_current_document") {
      return `<p>Reading <code>${escapeHtml(result.id || "")}</code> — ${escapeHtml(result.title || "")}${result.atomic ? ` (atomic ${result.atomic})` : ""}.</p>`;
    }
    if (tool === "list_facets") {
      const tags = (result.tags || []).slice(0, 24).join(", ");
      const types = (result.types || []).join(", ");
      const pillars = Object.keys(result.pillars || {}).join(", ");
      return `<p><strong>Pillars:</strong> ${escapeHtml(pillars)}</p><p><strong>Types:</strong> ${escapeHtml(types)}</p><p><strong>Tags:</strong> ${escapeHtml(tags)}</p>`;
    }
    if (tool === "get_concept") {
      const doc = result;
      return `<p><code>${escapeHtml(doc.id)}</code> — ${escapeHtml(doc.title || "")}</p><p>${escapeHtml(doc.description || "")}</p>`;
    }
    return `<pre>${escapeHtml(JSON.stringify(result, null, 2))}</pre>`;
  }

  async function submit(text) {
    const q = String(text || "").trim();
    if (!q) return;
    appendActivity(q, "…");
    const pending = setResults(`<p class="tool-name">Choosing a tool…</p>`);
    let routed;
    try {
      routed = await window.OkfApp.routeChat(q);
    } catch (err) {
      setResults(`<p>Tool routing failed: ${escapeHtml(String(err))}</p>`);
      return;
    }
    const tool = routed.tool;
    const result = routed.result;
    window.OkfWebMCP.showResult(result, tool);
    const via = routed.via === "webmcp" ? " via WebMCP" : "";
    const box = setResults(
      `<p class="tool-name">${escapeHtml(tool)}${formatArgs(routed.args)}${via}</p>${renderResult(tool, result)}`,
    );
    bindHits(box);
    const log = logEl();
    const last = log && log.lastElementChild;
    if (last && last.classList.contains("activity-line")) {
      last.querySelector(".mono").textContent = tool;
    }
    if (log) log.scrollTop = log.scrollHeight;
  }

  formEl()?.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const input = inputEl();
    const q = input.value;
    input.value = "";
    submit(q);
  });

  inputEl()?.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && !ev.shiftKey) {
      ev.preventDefault();
      formEl()?.requestSubmit();
    }
  });

  document.addEventListener("okf-loaded", welcome);
})();
