(() => {
  async function main() {
    const page = document.body.dataset.page;
  const { registerTool, showResult } = window.WebMCPHandbook;
  const catalog = window.HandbookCatalog;
  const readOnly = { readOnlyHint: true, untrustedContentHint: false };

  async function registerMetadata() {
    const elements = await catalog.metadataElements();
    const names = elements.map((el) => el.name);

    await registerTool({
      name: "list_metadata_elements",
      title: "List metadata elements",
      description:
        "List the Blueprint minimum metadata elements shown on this page (schema.org-oriented Table 1 fields).",
      inputSchema: { type: "object", properties: {}, additionalProperties: false },
      annotations: readOnly,
      execute: async () => showResult(elements, "list_metadata_elements"),
    });

    await registerTool({
      name: "get_metadata_element",
      title: "Get one metadata element",
      description:
        "Return meaning and default format for one metadata element such as identifier, author, infectiousAgent, or license.",
      inputSchema: {
        type: "object",
        properties: {
          name: { type: "string", description: "Element name", enum: names },
        },
        required: ["name"],
      },
      annotations: readOnly,
      execute: async ({ name }) => {
        const hit = elements.find((el) => el.name.toLowerCase() === String(name || "").toLowerCase());
        if (!hit) {
          return showResult(
            { error: `Unknown element "${name}". Use list_metadata_elements.` },
            "get_metadata_element",
          );
        }
        highlightRow(`[data-element="${hit.name}"]`);
        return showResult(hit, "get_metadata_element");
      },
    });
  }

  async function registerPids() {
    const schemes = await catalog.pidSchemes();
    const ids = schemes.map((s) => s.id);

    await registerTool({
      name: "list_pid_schemes",
      title: "List identifier schemes",
      description:
        "List persistent identifier and ontology schemes used by the Blueprint, including which metadata fields they cover.",
      inputSchema: { type: "object", properties: {}, additionalProperties: false },
      annotations: readOnly,
      execute: async () => showResult(schemes, "list_pid_schemes"),
    });

    await registerTool({
      name: "lookup_pid_scheme",
      title: "Look up an identifier scheme",
      description:
        "Look up one identifier or ontology scheme. Use ids such as doi, orcid, ror, rrid, ncbitaxon, mondo, ncit, or spdx.",
      inputSchema: {
        type: "object",
        properties: {
          id: { type: "string", description: "Scheme id", enum: ids },
        },
        required: ["id"],
      },
      annotations: readOnly,
      execute: async ({ id }) => {
        const key = String(id || "").toLowerCase();
        const hit = schemes.find(
          (s) => s.id === key || s.abbreviation.toLowerCase() === key || s.name.toLowerCase() === key,
        );
        if (!hit) {
          return showResult(
            { error: `Unknown scheme "${id}". Use list_pid_schemes.` },
            "lookup_pid_scheme",
          );
        }
        highlightRow(`[data-scheme="${hit.id}"]`);
        return showResult(hit, "lookup_pid_scheme");
      },
    });
  }

  async function registerApis() {
    const data = await catalog.apiObjectives();
    await registerTool({
      name: "get_api_objectives",
      title: "Get API objectives",
      description:
        "Return the Blueprint minimum API objectives (JSON-LD, resource-oriented IRIs, HTTP GET, OpenAPI) and fallback access options when a full API is not available.",
      inputSchema: { type: "object", properties: {}, additionalProperties: false },
      annotations: readOnly,
      execute: async () => showResult(data, "get_api_objectives"),
    });
  }

  function citationInputSchema() {
    return {
      type: "object",
      properties: {
        author: { type: "string", description: "Author names as they should appear" },
        year: { type: "string", description: "Publication year" },
        title: { type: "string", description: "Dataset or software title" },
        version: { type: "string", description: "Version string such as 1.0" },
        repository: { type: "string", description: "Repository name" },
        doi: { type: "string", description: "DOI or https://doi.org/… URL" },
        style: {
          type: "string",
          description: "Citation style",
          enum: ["APA", "MLA", "Chicago"],
        },
      },
      required: ["author", "year", "title", "repository"],
    };
  }

  function applyCitation(fields) {
    const text = catalog.formatCitation(fields);
    const out = document.getElementById("citation-output");
    if (out) out.textContent = text;
    const form = document.getElementById("citation-form");
    if (form) {
      for (const [key, value] of Object.entries(fields)) {
        if (value == null || value === "") continue;
        const field = form.elements.namedItem(key);
        if (field) field.value = value;
      }
    }
    return showResult({ citation: text, fields }, "format_citation");
  }

  async function registerCitation() {
    await registerTool({
      name: "format_citation",
      title: "Format a dataset citation",
      description:
        "Build a copy-ready dataset citation in APA, MLA, or Chicago style using author, year, title, version, repository, and DOI. Use this instead of scraping the citation form.",
      inputSchema: citationInputSchema(),
      annotations: { readOnlyHint: false, untrustedContentHint: false },
      execute: async (fields) => applyCitation(fields),
    });

    const form = document.getElementById("citation-form");
    if (!form) return;

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      const result = applyCitation(data);
      if (event.agentInvoked && typeof event.respondWith === "function") {
        event.respondWith(Promise.resolve(result));
      }
    });
  }

  function highlightRow(selector) {
    document.querySelectorAll("[data-highlight]").forEach((el) => {
      el.removeAttribute("data-highlight");
      el.style.outline = "";
    });
    const row = document.querySelector(selector);
    if (!row) return;
    row.dataset.highlight = "true";
    row.style.outline = "2px solid #c45c26";
    row.scrollIntoView({ block: "center", behavior: "smooth" });
  }

    try {
      if (page === "metadata") await registerMetadata();
      if (page === "persistent-identifiers") await registerPids();
      if (page === "apis") await registerApis();
      if (page === "citation") await registerCitation();
    } catch (err) {
      console.warn("page-tools failed", err);
    } finally {
      document.dispatchEvent(new Event("webmcp-page-tools-ready"));
    }
  }

  document.addEventListener("webmcp-site-tools-ready", main, { once: true });
})();
