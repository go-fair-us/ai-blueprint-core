(() => {
  const mount = () => document.getElementById("webmcp-tester");

  function render() {
    const el = mount();
    if (!el) return;
    const info = window.OkfWebMCP.availability();
    if (info.state !== "available") {
      el.innerHTML = `
        <div class="tester-status fail">${info.detail}</div>
        <p>Chrome setup:</p>
        <ol>
          <li>Open <code>chrome://flags/#enable-webmcp-testing</code> and set it to Enabled, then relaunch.</li>
          <li>Load this site from <code>http://127.0.0.1:8089/</code> (localhost is a secure context).</li>
          <li>Optional: install the Model Context Tool Inspector extension to call tools as an agent would.</li>
        </ol>
      `;
      return;
    }
    el.innerHTML = `
      <div class="tester-status ok">${info.detail}</div>
      <p class="mono" id="tester-count">Loading tools…</p>
      <div class="tool-list" id="tester-tools"></div>
      <label>Selected tool
        <input id="tester-name" readonly>
      </label>
      <label>JSON input
        <textarea id="tester-input">{}</textarea>
      </label>
      <div>
        <button type="button" id="tester-run">executeTool</button>
        <button type="button" class="secondary" id="tester-refresh">Refresh list</button>
      </div>
      <pre id="tester-out"></pre>
    `;
    el.querySelector("#tester-refresh").addEventListener("click", refresh);
    el.querySelector("#tester-run").addEventListener("click", run);
    refresh();
  }

  let selected = null;

  async function refresh() {
    const ctx = window.OkfWebMCP.getModelContext();
    const toolsEl = document.getElementById("tester-tools");
    const countEl = document.getElementById("tester-count");
    const out = document.getElementById("tester-out");
    if (!ctx || !toolsEl) return;
    try {
      const tools = await ctx.getTools();
      countEl.textContent = `${tools.length} tool(s) registered on this page`;
      toolsEl.innerHTML = "";
      for (const tool of tools) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = `${tool.name} — ${tool.description || ""}`;
        btn.addEventListener("click", () => select(tool, btn));
        toolsEl.appendChild(btn);
      }
      if (tools[0] && !selected) select(tools[0], toolsEl.querySelector("button"));
    } catch (err) {
      countEl.textContent = "getTools() failed";
      if (out) out.textContent = String(err);
    }
  }

  function sampleInput(tool) {
    const schema = tool.inputSchema || {};
    const props = schema.properties || {};
    const required = schema.required || [];
    const sample = {};
    for (const [key, def] of Object.entries(props)) {
      if (def.enum && def.enum.length) sample[key] = def.enum[0];
      else if (def.type === "number") sample[key] = 0;
      else if (def.type === "boolean") sample[key] = false;
      else if (required.includes(key) || Object.keys(props).length <= 3) sample[key] = "";
    }
    return sample;
  }

  function select(tool, btn) {
    selected = tool;
    const name = document.getElementById("tester-name");
    const input = document.getElementById("tester-input");
    if (name) name.value = tool.name;
    if (input && !input.dataset.touched) {
      input.value = JSON.stringify(sampleInput(tool), null, 2);
    }
    document.querySelectorAll(".tool-list button").forEach((b) => b.setAttribute("aria-pressed", "false"));
    if (btn) btn.setAttribute("aria-pressed", "true");
  }

  async function run() {
    const ctx = window.OkfWebMCP.getModelContext();
    const out = document.getElementById("tester-out");
    const raw = document.getElementById("tester-input")?.value || "{}";
    if (!ctx || !selected) return;
    let payload;
    try {
      payload = JSON.parse(raw);
    } catch (err) {
      out.textContent = `Input is not JSON: ${err.message}`;
      return;
    }
    try {
      let result;
      try {
        result = await ctx.executeTool(selected, payload);
      } catch (first) {
        result = await ctx.executeTool(selected, JSON.stringify(payload));
      }
      out.textContent = typeof result === "string" ? result : JSON.stringify(result, null, 2);
    } catch (err) {
      out.textContent = String(err);
    }
  }

  document.addEventListener("input", (event) => {
    if (event.target && event.target.id === "tester-input") {
      event.target.dataset.touched = "true";
    }
  });

  function start() {
    window.OkfWebMCP.paintBadge();
    render();
    const ctx = window.OkfWebMCP.getModelContext();
    if (ctx && typeof ctx.addEventListener === "function") {
      ctx.addEventListener("toolchange", refresh);
    }
  }

  let started = false;
  function startOnce() {
    if (started) return;
    started = true;
    start();
  }

  document.addEventListener("webmcp-tools-ready", startOnce, { once: true });
  setTimeout(startOnce, 2000);
})();
