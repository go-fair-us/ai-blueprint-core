(() => {
  const cache = {
    topics: null,
    metadataElements: null,
    pidSchemes: null,
    apiObjectives: null,
  };

  async function loadJson(path) {
    const res = await fetch(path);
    if (!res.ok) {
      throw new Error(`Failed to load ${path}: HTTP ${res.status}`);
    }
    return res.json();
  }

  async function topics() {
    if (!cache.topics) cache.topics = await loadJson("/data/topics.json");
    return cache.topics;
  }

  async function metadataElements() {
    if (!cache.metadataElements) {
      cache.metadataElements = await loadJson("/data/metadata-elements.json");
    }
    return cache.metadataElements;
  }

  async function pidSchemes() {
    if (!cache.pidSchemes) cache.pidSchemes = await loadJson("/data/pid-schemes.json");
    return cache.pidSchemes;
  }

  async function apiObjectives() {
    if (!cache.apiObjectives) {
      cache.apiObjectives = await loadJson("/data/api-objectives.json");
    }
    return cache.apiObjectives;
  }

  const STOP = new Set([
    "the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "at",
    "how", "what", "which", "should", "does", "do", "did", "is", "are",
    "can", "i", "me", "my", "we", "you", "about", "with", "from", "that",
    "this", "use", "using", "used",
  ]);

  const ALIASES = {
    cite: ["citation", "citations", "citing"],
    citing: ["citation", "cite"],
    citation: ["cite", "citing"],
    identifier: ["identifiers", "pid", "pids"],
    identifiers: ["identifier", "pid", "pids"],
    pid: ["identifier", "identifiers"],
    pids: ["identifier", "identifiers", "pid"],
    api: ["apis", "openapi"],
    apis: ["api", "openapi"],
  };

  function tokenize(text) {
    return String(text || "")
      .toLowerCase()
      .split(/[^a-z0-9]+/i)
      .filter((t) => t.length > 1);
  }

  function tokenMatches(hay, token) {
    return hay.some((h) => h === token || h.includes(token));
  }

  function searchTopics(list, query) {
    const raw = tokenize(query);
    const tokens = raw.filter((t) => !STOP.has(t));
    const terms = [];
    for (const t of tokens.length ? tokens : raw) {
      if (!terms.includes(t)) terms.push(t);
      for (const alias of ALIASES[t] || []) {
        if (!terms.includes(alias)) terms.push(alias);
      }
    }
    if (!terms.length) return [];
    return list
      .map((topic) => {
        const titleHay = tokenize([topic.title, ...(topic.keywords || [])].join(" "));
        const bodyHay = tokenize([topic.summary, topic.excerpt].join(" "));
        let score = 0;
        for (const t of terms) {
          if (tokenMatches(titleHay, t)) score += 3;
          else if (tokenMatches(bodyHay, t)) score += 1;
        }
        return { topic, score };
      })
      .filter((row) => row.score > 0)
      .sort((a, b) => b.score - a.score)
      .map((row) => row.topic);
  }

  function formatCitation({ author, year, title, version, repository, doi, style }) {
    const who = (author || "Author, A.").trim();
    const when = (year || "YYYY").trim();
    const what = (title || "Untitled dataset").trim();
    const ver = (version || "1.0").trim();
    const repo = (repository || "Repository").trim();
    let id = (doi || "").trim();
    if (id && !id.startsWith("http")) id = `https://doi.org/${id.replace(/^doi:/i, "")}`;
    const chosen = (style || "APA").toUpperCase();

    if (chosen === "MLA") {
      const parts = [`${who}. ${what}.`, `Version ${ver},`, `${repo},`, `${when}.`];
      if (id) parts.push(id);
      return parts.join(" ");
    }
    if (chosen === "CHICAGO") {
      const bits = [`${who}. ${what}.`, `Version ${ver}.`, `${repo}, ${when}.`];
      if (id) bits.push(id);
      return bits.join(" ");
    }
    const apa = `${who}. (${when}). ${what} (Version ${ver}) [Data set]. ${repo}.`;
    return id ? `${apa} ${id}` : apa;
  }

  window.HandbookCatalog = {
    topics,
    metadataElements,
    pidSchemes,
    apiObjectives,
    searchTopics,
    formatCitation,
  };
})();
