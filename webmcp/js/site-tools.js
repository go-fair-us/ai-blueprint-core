(async () => {
  try {
  const { registerTool, showResult } = window.WebMCPHandbook;
  const catalog = window.HandbookCatalog;
  const topics = await catalog.topics();

  const readOnly = { readOnlyHint: true, untrustedContentHint: false };

  await registerTool({
    name: "list_topics",
    title: "List handbook topics",
    description:
      "List the Blueprint handbook topic pages. Use this to see which subjects this site covers before searching or navigating.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    annotations: readOnly,
    execute: async () =>
      showResult(
        topics.map(({ slug, title, href, summary }) => ({ slug, title, href, summary })),
        "list_topics",
      ),
  });

  await registerTool({
    name: "search_topics",
    title: "Search handbook topics",
    description:
      "Search handbook pages by keyword. Matches titles, summaries, and keywords such as DOI, JSON-LD, citation, or Contact Point.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Free-text search terms" },
      },
      required: ["query"],
    },
    annotations: readOnly,
    execute: async ({ query }) => {
      const q = String(query || "").trim();
      if (!q) return showResult({ error: "Provide a non-empty query." }, "search_topics");
      const hits = catalog.searchTopics(topics, q).map(({ slug, title, href, summary }) => ({
        slug,
        title,
        href,
        summary,
      }));
      return showResult({ query: q, count: hits.length, hits }, "search_topics");
    },
  });

  await registerTool({
    name: "get_topic",
    title: "Get one handbook topic",
    description:
      "Return the summary and excerpt for one handbook topic. Use slug values from list_topics: overview, metadata, persistent-identifiers, apis, citation, outreach.",
    inputSchema: {
      type: "object",
      properties: {
        slug: {
          type: "string",
          description: "Topic slug",
          enum: topics.map((t) => t.slug),
        },
      },
      required: ["slug"],
    },
    annotations: readOnly,
    execute: async ({ slug }) => {
      const topic = topics.find((t) => t.slug === slug);
      if (!topic) {
        return showResult(
          { error: `Unknown slug "${slug}". Use list_topics to see valid values.` },
          "get_topic",
        );
      }
      return showResult(topic, "get_topic");
    },
  });

  await registerTool({
    name: "navigate_to_topic",
    title: "Open a handbook topic",
    description:
      "Navigate this browser tab to a handbook topic page. Use after list_topics or search_topics when the user wants to read that page.",
    inputSchema: {
      type: "object",
      properties: {
        slug: {
          type: "string",
          description: "Topic slug to open",
          enum: topics.map((t) => t.slug),
        },
      },
      required: ["slug"],
    },
    annotations: { readOnlyHint: false, untrustedContentHint: false },
    execute: async ({ slug }) => {
      const topic = topics.find((t) => t.slug === slug);
      if (!topic) {
        return showResult(
          { error: `Unknown slug "${slug}". Use list_topics to see valid values.` },
          "navigate_to_topic",
        );
      }
      const href = topic.href;
      showResult({ navigating: href, title: topic.title }, "navigate_to_topic");
      window.location.assign(href);
      return `Navigating to ${topic.title} at ${href}`;
    },
  });

  } catch (err) {
    console.warn("site-tools failed", err);
  } finally {
    document.dispatchEvent(new Event("webmcp-site-tools-ready"));
  }
})();
