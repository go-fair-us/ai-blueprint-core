(() => {
  const PILLAR_PREFIXES = {
    metadata: "metadata-schema",
    identifiers: "persistent-identifiers",
    api: "api-specification",
    citation: "citation",
    outreach: "outreach-training",
  };

  const STOP = new Set([
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "were",
    "show", "me", "please", "can", "you", "find", "give", "tell", "want",
    "need", "some", "any", "about", "into",
  ]);

  const app = {
    payload: null,
    byId: {},
    atomicsByNumber: {},
    currentId: null,
    currentAtomic: null,
    _hashLock: false,
  };

  function tokenize(text) {
    return String(text || "")
      .toLowerCase()
      .split(/[^a-z0-9]+/i)
      .filter((t) => t.length > 1 && !STOP.has(t));
  }

  function pillarPrefix(pillar) {
    if (!pillar) return null;
    const key = String(pillar).toLowerCase().trim();
    if (PILLAR_PREFIXES[key]) return PILLAR_PREFIXES[key];
    const values = Object.values(PILLAR_PREFIXES);
    if (values.includes(key)) return key;
    return key;
  }

  function parseFacets(query) {
    const filters = {};
    let rest = String(query || "");
    rest = rest.replace(/\b(tag|type|pillar|normative|kind):(\S+)/gi, (_, key, val) => {
      filters[key.toLowerCase()] = val;
      return " ";
    });
    return { query: rest.trim(), filters };
  }

  function snippet(text, tokens, n = 140) {
    const raw = String(text || "").replace(/\s+/g, " ").trim();
    if (!raw) return "";
    const lower = raw.toLowerCase();
    let idx = 0;
    for (const t of tokens) {
      const at = lower.indexOf(t);
      if (at >= 0) {
        idx = Math.max(0, at - 40);
        break;
      }
    }
    const cut = raw.slice(idx, idx + n);
    return (idx > 0 ? "…" : "") + cut + (idx + n < raw.length ? "…" : "");
  }

  function docMatchesFilters(doc, filters) {
    if (!filters) return true;
    if (filters.kind) {
      const want = String(filters.kind).toLowerCase();
      if (want === "index" && doc.kind !== "index" && doc.kind !== "log") return false;
      if (want !== "index" && want !== "atomic" && doc.kind !== want) return false;
    }
    if (filters.tag) {
      const tag = String(filters.tag).toLowerCase();
      if (!(doc.tags || []).some((t) => String(t).toLowerCase() === tag)) return false;
    }
    if (filters.type) {
      const type = String(filters.type).toLowerCase();
      if (!String(doc.type || "").toLowerCase().includes(type)) return false;
    }
    if (filters.pillar) {
      const prefix = pillarPrefix(filters.pillar);
      const id = doc.id || "";
      if (!(id === prefix || id.startsWith(prefix + "/"))) return false;
    }
    if (filters.normative !== undefined && filters.normative !== null && filters.normative !== "") {
      const want = String(filters.normative).toLowerCase();
      const flag = want === "true" || want === "1" || want === "yes";
      const notFlag = want === "false" || want === "0" || want === "no";
      if (flag && doc.normative !== true) return false;
      if (notFlag && doc.normative !== false) return false;
    }
    return true;
  }

  function scoreHay(hay, tokens, weight) {
    if (!tokens.length) return 0;
    let score = 0;
    for (const t of tokens) {
      if (hay.includes(t)) score += weight;
    }
    return score;
  }

  function search(opts = {}) {
    const rawQuery = opts.query || "";
    const parsed = parseFacets(rawQuery);
    const filters = {
      tag: opts.tag || parsed.filters.tag,
      type: opts.type || parsed.filters.type,
      pillar: opts.pillar || parsed.filters.pillar,
      normative: opts.normative !== undefined ? opts.normative : parsed.filters.normative,
      kind: opts.kind || parsed.filters.kind,
    };
    const tokens = tokenize(parsed.query);
    const max = Math.min(Math.max(Number(opts.max_results) || 25, 1), 100);
    const kind = filters.kind ? String(filters.kind).toLowerCase() : "";
    const hits = [];

    const docs = Object.values(app.byId);
    for (const doc of docs) {
      if (!docMatchesFilters(doc, { ...filters, kind: kind === "atomic" ? "concept" : filters.kind })) {
        continue;
      }
      if (kind === "atomic") {
        for (const a of doc.atomics || []) {
          const hay = tokenize(a.text).join(" ");
          const score = tokens.length ? scoreHay(hay, tokens, 3) : 1;
          if (tokens.length && score === 0) continue;
          hits.push({
            id: doc.id,
            title: `Atomic ${a.number}`,
            kind: "atomic",
            score,
            snippet: snippet(a.text, tokens, 180),
            parent_id: doc.id,
            parent_title: doc.title,
            atomic_number: a.number,
          });
        }
        continue;
      }

      const titleHay = tokenize([doc.title, ...(doc.tags || [])].join(" ")).join(" ");
      const descHay = tokenize(doc.description || "").join(" ");
      const bodyHay = tokenize(doc.prose || doc.body || "").join(" ");
      const atomicHay = tokenize((doc.atomics || []).map((a) => a.text).join(" ")).join(" ");
      let score = 0;
      if (tokens.length) {
        score += scoreHay(titleHay, tokens, 5);
        score += scoreHay(descHay, tokens, 3);
        score += scoreHay(atomicHay, tokens, 3);
        score += scoreHay(bodyHay, tokens, 1);
      } else {
        score = 1;
      }
      if (score <= 0) continue;
      hits.push({
        id: doc.id,
        title: doc.title,
        kind: doc.kind,
        score,
        snippet: snippet(doc.description || doc.prose || doc.body, tokens),
        parent_id: null,
        atomic_number: null,
      });

      if (!kind || kind === "atomic" || !kind) {
        for (const a of doc.atomics || []) {
          const aScore = tokens.length ? scoreHay(tokenize(a.text).join(" "), tokens, 4) : 0;
          if (aScore <= 0) continue;
          hits.push({
            id: doc.id,
            title: `Atomic ${a.number}`,
            kind: "atomic",
            score: aScore,
            snippet: snippet(a.text, tokens, 180),
            parent_id: doc.id,
            parent_title: doc.title,
            atomic_number: a.number,
          });
        }
      }
    }

    hits.sort((a, b) => b.score - a.score || String(a.id).localeCompare(b.id));
    const sliced = hits.slice(0, max);
    return {
      query: parsed.query,
      filters,
      count: sliced.length,
      total: hits.length,
      hits: sliced,
    };
  }

  function listConcepts(filters = {}) {
    return Object.values(app.byId)
      .filter((d) => d.kind === "concept")
      .filter((d) =>
        docMatchesFilters(d, {
          type: filters.type,
          tag: filters.tag,
          pillar: filters.prefix || filters.pillar,
          normative: filters.normative,
        }),
      )
      .map((d) => ({
        id: d.id,
        type: d.type,
        title: d.title,
        description: d.description,
        tags: d.tags,
        status: d.status,
        normative: d.normative,
        section: d.section,
        source_lines: d.source_lines,
        concept_range: d.concept_range,
        atomic_count: (d.atomics || []).length,
        links_to: d.links_to,
        pillar: d.pillar,
      }));
  }

  function listAtomics(opts = {}) {
    const parent = opts.parent_id ? String(opts.parent_id).replace(/\.md$/, "") : null;
    const q = opts.query ? String(opts.query).toLowerCase() : "";
    const max = Math.min(Math.max(Number(opts.max_results) || 50, 1), 239);
    const out = [];
    for (const doc of Object.values(app.byId)) {
      if (parent && doc.id !== parent) continue;
      for (const a of doc.atomics || []) {
        if (q && !String(a.text).toLowerCase().includes(q)) continue;
        out.push({
          number: a.number,
          text: a.text,
          source_lines: a.source_lines,
          parent_id: doc.id,
          parent_title: doc.title,
          concept_id: a.concept_id,
        });
        if (out.length >= max) return out;
      }
    }
    return out;
  }

  function getDocument(id) {
    if (!id) return null;
    const cid = String(id).replace(/\.md$/, "").replace(/^\//, "");
    return app.byId[cid] || null;
  }

  function getAtomic(number) {
    const n = Number(number);
    const a = app.atomicsByNumber[n];
    if (!a) return null;
    const parent = app.byId[a.parent_id];
    return {
      number: a.number,
      text: a.text,
      source_lines: a.source_lines,
      parent_id: a.parent_id,
      parent_title: parent ? parent.title : a.parent_id,
      parent_type: parent ? parent.type : "",
      parent_section: parent ? parent.section : "",
      concept_id: a.concept_id,
    };
  }

  function getRelated(id) {
    const doc = getDocument(id);
    if (!doc) return { error: `Concept not found: ${id}` };
    const links_to = (doc.links_to || []).map((cid) => {
      const other = app.byId[cid];
      return { id: cid, title: other ? other.title : cid };
    });
    return {
      id: doc.id,
      links_to,
      linked_from: doc.linked_from || [],
    };
  }

  function getCurrentDocument() {
    const doc = getDocument(app.currentId);
    if (!doc) return { id: null, title: null };
    const nums = (doc.atomics || []).map((a) => a.number);
    return {
      id: doc.id,
      title: doc.title,
      type: doc.type,
      kind: doc.kind,
      path: doc.path,
      atomic: app.currentAtomic,
      atomic_range: nums.length ? `${nums[0]}–${nums[nums.length - 1]}` : "",
      atomic_count: nums.length,
    };
  }

  function listFacets() {
    const p = app.payload || {};
    return {
      tags: p.tags || [],
      types: p.types || [],
      pillars: p.pillars || PILLAR_PREFIXES,
      stats: p.stats || {},
      kinds: ["concept", "atomic", "index"],
    };
  }

  function setHash(id, atomic) {
    const next = atomic ? `#/${id}/atomic/${atomic}` : `#/${id}`;
    if (location.hash === next) return;
    app._hashLock = true;
    location.hash = next;
    setTimeout(() => {
      app._hashLock = false;
    }, 0);
  }

  function parseHash() {
    const h = (location.hash || "").replace(/^#\/?/, "");
    if (!h) return { id: "index", atomic: null };
    const m = h.match(/^(.*)\/atomic\/(\d+)$/);
    if (m) return { id: m[1], atomic: Number(m[2]) };
    return { id: h, atomic: null };
  }

  function open(id, opts = {}) {
    const doc = getDocument(id);
    if (!doc) {
      return { error: `Unknown document "${id}". Use list_concepts or search_okf.` };
    }
    const atomic = opts.atomic != null && opts.atomic !== "" ? Number(opts.atomic) : null;
    const same = app.currentId === doc.id && app.currentAtomic === (Number.isFinite(atomic) ? atomic : null);
    app.currentId = doc.id;
    app.currentAtomic = Number.isFinite(atomic) ? atomic : null;
    if (opts.updateHash !== false) setHash(doc.id, app.currentAtomic);
    document.dispatchEvent(
      new CustomEvent("okf-open", {
        detail: { id: doc.id, atomic: app.currentAtomic, doc, replaced: !same },
      }),
    );
    return {
      opened: doc.id,
      title: doc.title,
      kind: doc.kind,
      atomic: app.currentAtomic,
    };
  }

  function hrefToId(href, fromId) {
    if (!href) return null;
    const raw = String(href).split("#")[0].split("?")[0];
    if (!raw || raw.startsWith("mailto:") || raw.startsWith("http://") || raw.startsWith("https://")) {
      return null;
    }
    let path = raw;
    if (path.startsWith("/")) path = path.slice(1);
    else {
      const base = fromId && fromId.includes("/") ? fromId.slice(0, fromId.lastIndexOf("/")) : "";
      path = base ? `${base}/${path}` : path;
    }
    const parts = [];
    for (const p of path.split("/")) {
      if (!p || p === ".") continue;
      if (p === "..") parts.pop();
      else parts.push(p);
    }
    let cid = parts.join("/");
    if (cid.endsWith(".md")) cid = cid.slice(0, -3);
    return app.byId[cid] ? cid : null;
  }

  function indexDocuments(payload) {
    app.payload = payload;
    app.byId = {};
    app.atomicsByNumber = {};
    for (const doc of payload.documents || []) {
      app.byId[doc.id] = doc;
      for (const a of doc.atomics || []) {
        app.atomicsByNumber[a.number] = a;
      }
    }
  }

  function routeChat(text) {
    const raw = String(text || "").trim();
    if (!raw) return { tool: "search_okf", result: { error: "Provide a non-empty query." } };

    const atomicMatch = raw.match(/^(?:#|atomic\s+)(\d+)$/i) || raw.match(/^(\d+)$/);
    if (atomicMatch) {
      const n = Number(atomicMatch[1]);
      const a = getAtomic(n);
      if (a) {
        open(a.parent_id, { atomic: n });
        return { tool: "get_atomic", result: a };
      }
    }

    const asId = raw.replace(/\.md$/, "").replace(/^\//, "");
    if (app.byId[asId]) {
      const opened = open(asId);
      return { tool: "open_concept", result: { ...opened, title: app.byId[asId].title } };
    }

    const result = search({ query: raw });
    return { tool: "search_okf", result };
  }

  async function load() {
    const res = await fetch("/data/index.json");
    if (!res.ok) throw new Error(`Failed to load index: HTTP ${res.status}`);
    const payload = await res.json();
    indexDocuments(payload);
    const stats = payload.stats || {};
    const el = document.getElementById("bundle-stats");
    if (el) {
      el.textContent = `${payload.bundle || "bundle"} · ${stats.concepts || 0} concepts · ${stats.atomics || 0} atomics`;
    }
    document.dispatchEvent(new CustomEvent("okf-loaded", { detail: payload }));
    const fromHash = parseHash();
    if (getDocument(fromHash.id)) open(fromHash.id, { atomic: fromHash.atomic, updateHash: false });
    else open("index", { updateHash: true });
    return payload;
  }

  window.addEventListener("hashchange", () => {
    if (app._hashLock) return;
    const fromHash = parseHash();
    if (fromHash.id && fromHash.id !== app.currentId) {
      open(fromHash.id, { atomic: fromHash.atomic, updateHash: false });
    } else if (fromHash.atomic !== app.currentAtomic) {
      open(fromHash.id || app.currentId, { atomic: fromHash.atomic, updateHash: false });
    }
  });

  app.search = search;
  app.listConcepts = listConcepts;
  app.listAtomics = listAtomics;
  app.getDocument = getDocument;
  app.getAtomic = getAtomic;
  app.getRelated = getRelated;
  app.getCurrentDocument = getCurrentDocument;
  app.listFacets = listFacets;
  app.open = open;
  app.hrefToId = hrefToId;
  app.routeChat = routeChat;
  app.parseFacets = parseFacets;
  app.load = load;
  app.PILLAR_PREFIXES = PILLAR_PREFIXES;

  window.OkfApp = app;

  load().catch((err) => {
    const el = document.getElementById("reader");
    if (el) el.innerHTML = `<p class="muted">Failed to load bundle index: ${String(err)}</p>`;
    console.error(err);
  });
})();
