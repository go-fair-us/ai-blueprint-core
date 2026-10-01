(() => {
  const root = () => document.getElementById("tree-root");
  const filterInput = () => document.getElementById("tree-filter");

  function kindClass(kind) {
    if (kind === "concept") return "concept";
    if (kind === "index") return "index";
    if (kind === "log") return "log";
    return "";
  }

  function renderNode(node) {
    if (node.kind === "dir") {
      const details = document.createElement("details");
      details.dataset.dirId = node.id || "";
      if (!node.id) details.open = true;
      const summary = document.createElement("summary");
      summary.textContent = node.name;
      details.appendChild(summary);
      for (const child of node.children || []) {
        details.appendChild(renderNode(child));
      }
      return details;
    }
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tree-file";
    btn.dataset.id = node.id;
    btn.dataset.title = (node.title || node.name || "").toLowerCase();
    btn.innerHTML = `<span class="kind-dot ${kindClass(node.kind)}"></span>${escapeHtml(node.title || node.name)}`;
    btn.addEventListener("click", () => {
      window.OkfApp.open(node.id);
      closeDrawers();
    });
    return btn;
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function highlight(id) {
    const tree = root();
    if (!tree) return;
    tree.querySelectorAll(".tree-file").forEach((btn) => {
      btn.setAttribute("aria-current", btn.dataset.id === id ? "true" : "false");
    });
    const current = tree.querySelector(`.tree-file[data-id="${CSS.escape(id)}"]`);
    if (current) {
      let parent = current.parentElement;
      while (parent && parent !== tree) {
        if (parent.tagName === "DETAILS") parent.open = true;
        parent = parent.parentElement;
      }
      current.scrollIntoView({ block: "nearest" });
    }
  }

  function applyFilter(q) {
    const tree = root();
    if (!tree) return;
    const needle = String(q || "").trim().toLowerCase();
    tree.querySelectorAll(".tree-file").forEach((btn) => {
      const hay = `${btn.dataset.id} ${btn.dataset.title}`;
      const show = !needle || hay.includes(needle);
      btn.classList.toggle("is-hidden", !show);
      if (show && needle) {
        let parent = btn.parentElement;
        while (parent && parent !== tree) {
          if (parent.tagName === "DETAILS") parent.open = true;
          parent = parent.parentElement;
        }
      }
    });
  }

  function closeDrawers() {
    document.getElementById("pane-tree")?.classList.remove("is-open");
    document.getElementById("pane-chat")?.classList.remove("is-open");
    const backdrop = document.getElementById("drawer-backdrop");
    if (backdrop) backdrop.hidden = true;
  }

  function bindDrawers() {
    const treeBtn = document.getElementById("toggle-tree");
    const chatBtn = document.getElementById("toggle-chat");
    const backdrop = document.getElementById("drawer-backdrop");
    const tree = document.getElementById("pane-tree");
    const chat = document.getElementById("pane-chat");

    function toggle(pane) {
      const other = pane === tree ? chat : tree;
      other?.classList.remove("is-open");
      pane?.classList.toggle("is-open");
      const any = tree?.classList.contains("is-open") || chat?.classList.contains("is-open");
      if (backdrop) backdrop.hidden = !any;
    }

    treeBtn?.addEventListener("click", () => toggle(tree));
    chatBtn?.addEventListener("click", () => toggle(chat));
    backdrop?.addEventListener("click", closeDrawers);
  }

  function paint(payload) {
    const tree = root();
    if (!tree) return;
    tree.innerHTML = "";
    tree.appendChild(renderNode(payload.tree));
    if (window.OkfApp.currentId) highlight(window.OkfApp.currentId);
  }

  document.addEventListener("okf-loaded", (ev) => paint(ev.detail));
  document.addEventListener("okf-open", (ev) => highlight(ev.detail.id));
  filterInput()?.addEventListener("input", (ev) => applyFilter(ev.target.value));
  bindDrawers();
})();
