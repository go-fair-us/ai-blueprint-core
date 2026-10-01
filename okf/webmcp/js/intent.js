(() => {
  if (!window.OkfApp) {
    console.warn("intent.js requires bundle.js");
    return;
  }

  const PILLAR_ALIASES = [
    { key: "citation", words: ["citation", "citations", "cite", "citing", "cited"] },
    { key: "metadata", words: ["metadata", "schema.org", "schemaorg", "table-1", "table1"] },
    { key: "identifiers", words: ["identifier", "identifiers", "pid", "pids", "persistent-identifiers"] },
    { key: "api", words: ["api", "apis", "json-ld", "jsonld", "openapi"] },
    { key: "outreach", words: ["outreach", "training"] },
  ];

  const DIR_ALIASES = {
    overview: ["overview", "background", "scope"],
    audience: ["audience", "repository owners", "data generators"],
    implementation: ["implementation"],
    appendix: ["appendix", "appendices"],
  };

  const FILLER_PHRASES = [
    /\bshow me\b/gi,
    /\bshow us\b/gi,
    /\bgive me\b/gi,
    /\btell me\b/gi,
    /\bfind me\b/gi,
    /\blook up\b/gi,
    /\blook for\b/gi,
    /\bsearch for\b/gi,
    /\bi want\b/gi,
    /\bi need\b/gi,
    /\bcan you\b/gi,
    /\bcould you\b/gi,
    /\bplease\b/gi,
    /\bmaterial(?:s)?\b/gi,
    /\binformation\b/gi,
    /\bcontent\b/gi,
    /\bdocuments?\b/gi,
    /\bpages?\b/gi,
    /\bstuff\b/gi,
    /\brelated to\b/gi,
    /\bregarding\b/gi,
    /\bconcerning\b/gi,
    /\bon the topic of\b/gi,
    /\babout\b/gi,
  ];

  function normalize(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function stripFiller(text) {
    let out = normalize(text);
    for (const re of FILLER_PHRASES) out = out.replace(re, " ");
    return out.replace(/[?!.]+$/g, "").replace(/\s+/g, " ").trim();
  }

  function detectPillar(text) {
    const raw = String(text || "");
    if (/\btable\s*1\b/i.test(raw)) return "metadata";
    const lower = ` ${raw.toLowerCase()} `;
    for (const { key, words } of PILLAR_ALIASES) {
      for (const w of words) {
        if (lower.includes(` ${w} `) || lower.includes(` ${w}.`)) return key;
      }
    }
    for (const [dir, words] of Object.entries(DIR_ALIASES)) {
      for (const w of words) {
        if (lower.includes(` ${w} `)) return dir;
      }
    }
    return null;
  }

  function matchDocument(text) {
    const app = window.OkfApp;
    if (!app || !app.byId) return null;
    let q = stripFiller(text).toLowerCase().replace(/\.md$/, "").replace(/^\//, "").trim();
    q = q.replace(/^(the )?(document|concept|page|file)\s+/i, "").trim();
    if (!q) return null;
    if (app.byId[q]) return q;

    const dashed = q.replace(/\s+/g, "-");
    if (app.byId[dashed]) return dashed;

    const pillar = detectPillar(text);
    const prefix = (app.PILLAR_PREFIXES && app.PILLAR_PREFIXES[pillar]) || pillar;
    if (prefix) {
      for (const section of ["requirements", "motivation", "impact", "index"]) {
        if (q.includes(section) && app.byId[`${prefix}/${section}`]) {
          return `${prefix}/${section}`;
        }
      }
    }

    const ids = Object.keys(app.byId);
    const idHits = ids.filter((id) => id === dashed || id.endsWith(`/${dashed}`) || id.endsWith(`/${q}`));
    if (idHits.length === 1) return idHits[0];

    const docs = Object.values(app.byId);
    if (q.includes(" ") || q.includes("/")) {
      const exactTitle = docs.filter((d) => String(d.title || "").toLowerCase() === q);
      if (exactTitle.length === 1) return exactTitle[0].id;
      const contained = docs.filter((d) => String(d.title || "").toLowerCase().includes(q) && q.length >= 8);
      if (contained.length === 1) return contained[0].id;
    }
    return null;
  }

  function atomicNumber(text) {
    const m =
      String(text).match(/\b(?:atomic(?:\s+concept)?|claim)\s*#?\s*(\d+)\b/i) ||
      String(text).match(/#(\d+)\b/) ||
      String(text).match(/^(\d+)$/);
    return m ? Number(m[1]) : null;
  }

  function planIntent(text) {
    const raw = normalize(text);
    if (!raw) {
      return { tool: "search_okf", args: { query: "" }, reason: "empty query" };
    }

    if (/\b(current (doc|document|page)|what am i (looking at|reading)|what(?:'s| is) open)\b/i.test(raw)) {
      return { tool: "get_current_document", args: {}, reason: "asked for the open document" };
    }

    if (/\b(list|show|what(?: are|'s)?)\b.{0,24}\b(tags|types|pillars|facets)\b/i.test(raw) ||
        /\bwhat can i search\b/i.test(raw)) {
      return { tool: "list_facets", args: {}, reason: "asked for search facets" };
    }

    const n = atomicNumber(raw);
    if (n != null && window.OkfApp.getAtomic(n)) {
      return { tool: "get_atomic", args: { number: n }, reason: `atomic #${n}` };
    }

    const asId = raw.replace(/\.md$/, "").replace(/^\//, "");
    if (window.OkfApp.byId[asId]) {
      return { tool: "open_concept", args: { id: asId }, reason: "exact concept id" };
    }

    const relatedThis = /\b(related|links?|see also)\b/i.test(raw) &&
      /\b(this|current|here|open document)\b/i.test(raw);
    if (relatedThis && window.OkfApp.currentId) {
      return {
        tool: "get_related",
        args: { id: window.OkfApp.currentId },
        reason: "related concepts for the open document",
      };
    }

    if (/\brelated (to|for)\b/i.test(raw)) {
      const docForRelated = matchDocument(raw);
      if (docForRelated && docForRelated.includes("/") && !docForRelated.endsWith("/index")) {
        return { tool: "get_related", args: { id: docForRelated }, reason: `related to ${docForRelated}` };
      }
    }

    if (/\b(open|go to|navigate to|bring up)\b/i.test(raw)) {
      const id = matchDocument(raw);
      if (id) return { tool: "open_concept", args: { id }, reason: `open ${id}` };
    }

    if (/\b(list|catalog)\b.{0,20}\b(concepts?|files?)\b/i.test(raw) ||
        /\bwhich concepts\b/i.test(raw)) {
      const cleaned = stripFiller(raw);
      const pillar = detectPillar(cleaned) || detectPillar(raw);
      const args = {};
      if (pillar) args.prefix = window.OkfApp.PILLAR_PREFIXES[pillar] || pillar;
      return { tool: "list_concepts", args, reason: "concept catalog" };
    }

    if (/\b(list|show)\b.{0,20}\batomics?\b/i.test(raw) || /\batomic claims\b/i.test(raw)) {
      const cleaned = stripFiller(raw.replace(/\batomics?\b/gi, " "));
      const parent = matchDocument(raw);
      const args = {};
      if (parent) args.parent_id = parent;
      if (cleaned) args.query = cleaned;
      return { tool: "list_atomics", args, reason: "list atomic claims" };
    }

    if (/\b(describe|read|get concept|look at concept)\b/i.test(raw)) {
      const id = matchDocument(raw);
      if (id) return { tool: "get_concept", args: { id }, reason: `read ${id}` };
    }

    const cleaned = stripFiller(raw);
    const pillar = detectPillar(raw) || detectPillar(cleaned);
    const query = cleaned || raw;
    const args = { query: query || (pillar || "") };
    if (pillar) args.pillar = pillar;
    return {
      tool: "search_okf",
      args,
      openBest: true,
      reason: pillar ? `search in ${pillar}` : "keyword search",
    };
  }

  function runToolLocal(name, args) {
    const app = window.OkfApp;
    switch (name) {
      case "search_okf":
        return app.search(args || {});
      case "list_concepts":
        return app.listConcepts(args || {});
      case "open_concept":
        return app.open(args.id, { atomic: args.atomic });
      case "get_concept": {
        const doc = app.getDocument(args.id);
        return doc || { error: `Unknown id "${args.id}".` };
      }
      case "get_atomic": {
        const a = app.getAtomic(args.number);
        if (!a) return { error: `Atomic ${args.number} not found.` };
        app.open(a.parent_id, { atomic: a.number });
        return a;
      }
      case "list_atomics":
        return app.listAtomics(args || {});
      case "get_related":
        return app.getRelated(args.id);
      case "get_current_document":
        return app.getCurrentDocument();
      case "list_facets":
        return app.listFacets();
      default:
        return { error: `Unknown tool "${name}".` };
    }
  }

  function parseToolResult(raw) {
    if (raw == null) return raw;
    if (typeof raw === "object") return raw;
    const text = String(raw);
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }

  async function executeViaWebMCP(name, args) {
    const api = window.OkfWebMCP;
    if (!api) return null;
    const ctx = api.getModelContext && api.getModelContext();
    if (!ctx || typeof ctx.getTools !== "function" || typeof ctx.executeTool !== "function") {
      return null;
    }
    const tools = await ctx.getTools();
    const tool = (tools || []).find((t) => t.name === name);
    if (!tool) return null;
    let raw;
    try {
      raw = await ctx.executeTool(tool, args || {});
    } catch {
      raw = await ctx.executeTool(tool, JSON.stringify(args || {}));
    }
    return parseToolResult(raw);
  }

  async function routeChat(text) {
    const plan = planIntent(text);
    let via = "local";
    let result;
    try {
      const remote = await executeViaWebMCP(plan.tool, plan.args);
      if (remote != null) {
        result = remote;
        via = "webmcp";
      }
    } catch (err) {
      console.warn("WebMCP executeTool failed, using local tools", err);
    }
    if (result == null) result = runToolLocal(plan.tool, plan.args);

    if (plan.openBest && result && Array.isArray(result.hits) && result.hits.length) {
      const prefix = plan.args && (window.OkfApp.PILLAR_PREFIXES[plan.args.pillar] || plan.args.pillar);
      const preferred = prefix
        ? result.hits.find((h) => h.id === `${prefix}/index`) ||
          result.hits.find((h) => h.id === `${prefix}/requirements`)
        : null;
      const best =
        preferred ||
        result.hits.find((h) => h.kind === "concept" || h.kind === "index") ||
        result.hits[0];
      if (best && best.id) {
        window.OkfApp.open(best.id, { atomic: best.atomic_number });
        result = { ...result, opened: best.id, opened_title: best.title };
      }
    }

    return {
      tool: plan.tool,
      args: plan.args,
      reason: plan.reason,
      via,
      result,
    };
  }

  window.OkfApp.planIntent = planIntent;
  window.OkfApp.runToolLocal = runToolLocal;
  window.OkfApp.routeChat = routeChat;
  window.OkfApp.stripFiller = stripFiller;
})();
