(async () => {
  const readOnly = { readOnlyHint: true, untrustedContentHint: false };
  const writeNav = { readOnlyHint: false, untrustedContentHint: false };

  function waitLoaded() {
    if (window.OkfApp && window.OkfApp.payload) return Promise.resolve();
    return new Promise((resolve) => {
      document.addEventListener("okf-loaded", () => resolve(), { once: true });
    });
  }

  try {
    await waitLoaded();
    const { registerTool, showResult, paintBadge } = window.OkfWebMCP;
    const app = window.OkfApp;
    paintBadge();

    await registerTool({
      name: "search_okf",
      title: "Search the OKF bundle",
      description:
        "Search NIAID Blueprint OKF concepts and atomic claims by keyword. Optional facets: tag, type, pillar (metadata, identifiers, api, citation, outreach), normative, kind (concept, atomic, index).",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "Free-text search. Facet tokens like tag:doi are also accepted." },
          tag: { type: "string", description: "Exact tag match, e.g. doi" },
          type: { type: "string", description: "Substring on concept type, e.g. Requirements" },
          pillar: {
            type: "string",
            description:
              "FAIR pillar (metadata, identifiers, api, citation, outreach) or a directory prefix such as metadata-schema, overview, appendix",
          },
          normative: { type: "boolean", description: "If set, only concepts with that normative flag" },
          kind: { type: "string", enum: ["concept", "atomic", "index"] },
          max_results: { type: "number", description: "Maximum hits (default 25)" },
        },
        required: ["query"],
      },
      annotations: readOnly,
      execute: async (input) => showResult(app.search(input || {}), "search_okf"),
    });

    await registerTool({
      name: "list_concepts",
      title: "List OKF concepts",
      description:
        "List concept catalog entries (no full body). Filters: type, prefix/pillar, tag, normative.",
      inputSchema: {
        type: "object",
        properties: {
          type: { type: "string" },
          prefix: { type: "string", description: "Concept id prefix such as metadata-schema" },
          tag: { type: "string" },
          normative: { type: "boolean" },
        },
        additionalProperties: false,
      },
      annotations: readOnly,
      execute: async (input) => showResult(app.listConcepts(input || {}), "list_concepts"),
    });

    await registerTool({
      name: "open_concept",
      title: "Open an OKF document",
      description:
        "Load a concept, index, or log file into the reader so the human and agent share the same view. Use ids from list_concepts or search_okf, e.g. metadata-schema/requirements. Optional atomic number scrolls that claim into view.",
      inputSchema: {
        type: "object",
        properties: {
          id: { type: "string", description: "Concept id without .md" },
          atomic: { type: "number", description: "Optional atomic claim number to highlight" },
        },
        required: ["id"],
      },
      annotations: writeNav,
      execute: async ({ id, atomic }) => showResult(app.open(id, { atomic }), "open_concept"),
    });

    await registerTool({
      name: "get_concept",
      title: "Get one OKF concept",
      description:
        "Return structured frontmatter, atomics, and a prose excerpt for one concept. Does not change the visible document; use open_concept to navigate.",
      inputSchema: {
        type: "object",
        properties: {
          id: { type: "string", description: "Concept id, e.g. persistent-identifiers/requirements" },
          include_body: { type: "boolean", description: "Include full body (default true)" },
        },
        required: ["id"],
      },
      annotations: readOnly,
      execute: async ({ id, include_body }) => {
        const doc = app.getDocument(id);
        if (!doc) return showResult({ error: `Unknown id "${id}".` }, "get_concept");
        const out = { ...doc };
        if (include_body === false) {
          delete out.body;
          delete out.prose;
        }
        return showResult(out, "get_concept");
      },
    });

    await registerTool({
      name: "get_atomic",
      title: "Get one atomic claim",
      description:
        "Return a single atomic claim by global number (1–239 in niaid_blueprint) and open its parent concept in the reader.",
      inputSchema: {
        type: "object",
        properties: {
          number: { type: "number", description: "Global atomic number" },
        },
        required: ["number"],
      },
      annotations: writeNav,
      execute: async ({ number }) => {
        const a = app.getAtomic(number);
        if (!a) return showResult({ error: `Atomic ${number} not found.` }, "get_atomic");
        app.open(a.parent_id, { atomic: a.number });
        return showResult(a, "get_atomic");
      },
    });

    await registerTool({
      name: "list_atomics",
      title: "List atomic claims",
      description: "List atomic claims, optionally filtered by parent concept id or substring query.",
      inputSchema: {
        type: "object",
        properties: {
          parent_id: { type: "string" },
          query: { type: "string" },
          max_results: { type: "number" },
        },
      },
      annotations: readOnly,
      execute: async (input) => showResult(app.listAtomics(input || {}), "list_atomics"),
    });

    await registerTool({
      name: "get_related",
      title: "Related OKF concepts",
      description: "Return concepts linked from / linking to an OKF concept id.",
      inputSchema: {
        type: "object",
        properties: { id: { type: "string" } },
        required: ["id"],
      },
      annotations: readOnly,
      execute: async ({ id }) => showResult(app.getRelated(id), "get_related"),
    });

    await registerTool({
      name: "get_current_document",
      title: "Current OKF document",
      description:
        "Return the document currently shown in the reader (what the human is looking at), including the highlighted atomic if any.",
      inputSchema: { type: "object", properties: {}, additionalProperties: false },
      annotations: readOnly,
      execute: async () => showResult(app.getCurrentDocument(), "get_current_document"),
    });

    await registerTool({
      name: "list_facets",
      title: "List search facets",
      description: "Tags, types, FAIR pillars, and bundle stats for building search_okf queries.",
      inputSchema: { type: "object", properties: {}, additionalProperties: false },
      annotations: readOnly,
      execute: async () => showResult(app.listFacets(), "list_facets"),
    });
  } catch (err) {
    console.warn("OKF WebMCP tools failed", err);
  } finally {
    document.dispatchEvent(new Event("webmcp-tools-ready"));
  }
})();
