(() => {
  function getModelContext() {
    if (document.modelContext) return document.modelContext;
    if (navigator.modelContext) return navigator.modelContext;
    return null;
  }

  function availability() {
    const ctx = getModelContext();
    if (!ctx) {
      return {
        state: "missing",
        label: "WebMCP not available",
        detail:
          "This browser does not expose document.modelContext. In Chrome, enable chrome://flags/#enable-webmcp-testing, relaunch, and load this site from http://127.0.0.1 (a secure context).",
      };
    }
    if (typeof ctx.registerTool !== "function") {
      return {
        state: "error",
        label: "WebMCP incomplete",
        detail: "modelContext exists but registerTool is missing.",
      };
    }
    return {
      state: "available",
      label: "WebMCP available",
      detail: "document.modelContext is present. Agents and the in-page tester can call registered tools.",
    };
  }

  function showResult(payload, title) {
    const box = document.getElementById("tool-result");
    if (!box) return payload;
    const heading = box.querySelector("[data-result-title]");
    const pre = box.querySelector("pre");
    if (heading) heading.textContent = title || "Last tool result";
    if (pre) {
      pre.textContent =
        typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
    }
    box.hidden = false;
    return payload;
  }

  async function registerTool(tool, options = {}) {
    const ctx = getModelContext();
    if (!ctx) return { ok: false, reason: "missing-api" };
    try {
      await ctx.registerTool(tool, options);
      return { ok: true };
    } catch (err) {
      console.warn("registerTool failed", tool.name, err);
      return { ok: false, reason: err && err.message ? err.message : String(err) };
    }
  }

  function paintBadge() {
    const badge = document.getElementById("webmcp-badge");
    if (!badge) return;
    const info = availability();
    badge.dataset.state = info.state;
    badge.textContent = info.label;
    badge.title = info.detail;
  }

  window.WebMCPHandbook = {
    getModelContext,
    availability,
    registerTool,
    showResult,
    paintBadge,
  };
})();
