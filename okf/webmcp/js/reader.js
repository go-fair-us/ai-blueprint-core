(() => {
  const mount = () => document.getElementById("reader");

  function escapeHtml(text) {
    return String(text ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function rewriteFootnotes(src) {
    const notes = {};
    let body = String(src || "").replace(/^\[\^([^\]]+)\]:\s*(.+)$/gm, (_, id, text) => {
      notes[id] = text.trim();
      return "";
    });
    body = body.replace(/\[\^([^\]]+)\]/g, (_, id) => {
      const title = escapeHtml(notes[id] || id);
      return `<sup class="fn" title="${title}">${escapeHtml(id)}</sup>`;
    });
    return body;
  }

  function renderMarkdown(src) {
    const prepared = rewriteFootnotes(src);
    if (typeof marked !== "undefined" && typeof marked.parse === "function") {
      return marked.parse(prepared, { gfm: true, breaks: false, async: false });
    }
    return `<pre>${escapeHtml(prepared)}</pre>`;
  }

  function chips(doc) {
    const items = [];
    if (doc.kind && doc.kind !== "concept") items.push(["kind", doc.kind]);
    if (doc.type) items.push(["type", doc.type]);
    if (doc.status) items.push(["status", doc.status]);
    if (doc.normative === true) items.push(["normative", "true"]);
    if (doc.normative === false) items.push(["normative", "false"]);
    if (doc.section) items.push(["section", doc.section]);
    if (doc.source_lines) items.push(["source lines", doc.source_lines]);
    if (doc.concept_range) items.push(["atomics", doc.concept_range]);
    if (doc.pillar) items.push(["pillar", doc.pillar]);
    for (const tag of doc.tags || []) items.push(["tag", tag]);
    if (!items.length) return "";
    return `<div class="chips">${items
      .map(([k, v]) => `<span class="chip"><strong>${escapeHtml(k)}</strong> ${escapeHtml(v)}</span>`)
      .join("")}</div>`;
  }

  function atomicsTable(doc) {
    const rows = doc.atomics || [];
    if (!rows.length) return "";
    const body = rows
      .map(
        (a) => `<tr data-atomic="${a.number}">
        <td class="num">${a.number}</td>
        <td>${escapeHtml(a.text)}</td>
        <td>${escapeHtml(a.source_lines)}</td>
      </tr>`,
      )
      .join("");
    return `<h2>Atomic concepts</h2>
      <table class="atomics">
        <thead><tr><th>#</th><th>Concept</th><th>Lines</th></tr></thead>
        <tbody>${body}</tbody>
      </table>`;
  }

  function relatedBlock(doc) {
    const out = doc.links_to || [];
    const inbound = (doc.linked_from || []).map((x) => x.id || x);
    if (!out.length && !inbound.length) return "";
    const linkList = (ids) =>
      `<ul>${ids
        .map((cid) => {
          const id = typeof cid === "string" ? cid : cid.id;
          const title = typeof cid === "string" ? (window.OkfApp.getDocument(cid)?.title || cid) : cid.title || cid.id;
          return `<li><a href="#/${id}" data-okf-id="${escapeHtml(id)}">${escapeHtml(title)}</a></li>`;
        })
        .join("")}</ul>`;
    let html = `<section class="related"><h2>Related</h2>`;
    if (out.length) html += `<h3>See also</h3>${linkList(out)}`;
    if (inbound.length) html += `<h3>Cited by</h3>${linkList(doc.linked_from)}`;
    html += `</section>`;
    return html;
  }

  function render(doc, atomic) {
    const el = mount();
    if (!el || !doc) return;
    const source = doc.kind === "concept" ? doc.prose || doc.body : doc.body;
    const html = `
      <p class="doc-id">${escapeHtml(doc.id)}</p>
      <h1>${escapeHtml(doc.title || doc.id)}</h1>
      ${chips(doc)}
      ${doc.description ? `<p class="lede">${escapeHtml(doc.description)}</p>` : ""}
      <div class="prose">${renderMarkdown(source)}</div>
      ${atomicsTable(doc)}
      ${relatedBlock(doc)}
    `;
    el.innerHTML = html;

    el.querySelectorAll("a").forEach((a) => {
      const href = a.getAttribute("href") || "";
      const viaData = a.getAttribute("data-okf-id");
      const id = viaData || window.OkfApp.hrefToId(href, doc.id);
      if (!id) return;
      a.setAttribute("href", `#/${id}`);
      a.addEventListener("click", (ev) => {
        ev.preventDefault();
        window.OkfApp.open(id);
      });
    });

    el.querySelectorAll(".atomics tr[data-atomic]").forEach((row) => {
      row.addEventListener("click", () => {
        const n = Number(row.dataset.atomic);
        window.OkfApp.open(doc.id, { atomic: n });
      });
    });

    if (atomic != null) highlightAtomic(atomic);
    const pane = document.getElementById("pane-reader");
    if (pane) pane.scrollTop = 0;
  }

  function highlightAtomic(number) {
    const el = mount();
    if (!el) return;
    el.querySelectorAll(".atomics tr").forEach((row) => {
      row.classList.toggle("is-active", Number(row.dataset.atomic) === Number(number));
    });
    const active = el.querySelector(`.atomics tr[data-atomic="${Number(number)}"]`);
    if (active) active.scrollIntoView({ block: "center" });
  }

  document.addEventListener("okf-open", (ev) => {
    render(ev.detail.doc, ev.detail.atomic);
  });
})();
