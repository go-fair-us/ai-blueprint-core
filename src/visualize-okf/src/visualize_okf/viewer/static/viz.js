/* Derived from GoogleCloudPlatform/knowledge-catalog reference_agent viewer (Apache-2.0).
 *
 * Local changes:
 *  - Resolve relative .md links in the detail panel against the selected concept dir
 *  - Prefer Publication / Concept / NIAID types for initial selection
 *  - OKF v0.2: show status, generated, trust, sources; style provenance edges
 */
(function () {
  const bundle = window.BUNDLE;
  const bundleName = window.BUNDLE_NAME;
  document.title = `${bundleName} — OKF Viewer`;
  document.getElementById("bundle-name").textContent = bundleName;

  // Populate type filter
  const typeSelect = document.getElementById("filter-type");
  for (const t of bundle.types) {
    const opt = document.createElement("option");
    opt.value = t;
    opt.textContent = t;
    typeSelect.appendChild(opt);
  }

  // Build reverse-link index for backlinks (all edge kinds)
  const backlinks = {};
  for (const edge of bundle.edges) {
    const { source, target } = edge.data;
    (backlinks[target] ||= []).push(source);
  }

  // Look up node label/type by id
  const nodeIndex = {};
  for (const n of bundle.nodes) nodeIndex[n.data.id] = n.data;

  const cy = cytoscape({
    container: document.getElementById("graph"),
    elements: [...bundle.nodes, ...bundle.edges],
    style: [
      {
        selector: "node",
        style: {
          "background-color": "data(color)",
          "label": "data(label)",
          "color": "#0f172a",
          "font-size": 11,
          "text-valign": "bottom",
          "text-margin-y": 4,
          "text-wrap": "wrap",
          "text-max-width": 120,
          "width": "data(size)",
          "height": "data(size)",
          "border-width": 1,
          "border-color": "#0f172a",
        },
      },
      {
        selector: 'node[status = "deprecated"]',
        style: {
          "border-style": "dashed",
          "border-width": 2,
          "border-color": "#94a3b8",
          "opacity": 0.75,
        },
      },
      {
        selector: 'node[status = "draft"]',
        style: {
          "border-style": "dotted",
          "border-width": 2,
          "border-color": "#f59e0b",
        },
      },
      {
        selector: "node:selected",
        style: {
          "border-width": 3,
          "border-color": "#f59e0b",
          "opacity": 1,
        },
      },
      {
        selector: "edge",
        style: {
          "width": 1.5,
          "line-color": "#cbd5e1",
          "target-arrow-color": "#cbd5e1",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          "arrow-scale": 0.9,
        },
      },
      {
        // Provenance edges (sources[].resource → in-bundle concept)
        selector: 'edge[kind = "source"]',
        style: {
          "width": 1.5,
          "line-color": "#a78bfa",
          "target-arrow-color": "#a78bfa",
          "target-arrow-shape": "triangle",
          "line-style": "dashed",
          "curve-style": "bezier",
          "arrow-scale": 0.9,
        },
      },
      {
        selector: "edge:selected",
        style: {
          "line-color": "#f59e0b",
          "target-arrow-color": "#f59e0b",
          "width": 2.5,
        },
      },
      {
        selector: ".dim",
        style: { "opacity": 0.15 },
      },
    ],
    layout: { name: "cose", animate: false, padding: 30 },
    wheelSensitivity: 0.2,
  });

  cy.on("tap", "node", (evt) => showDetail(evt.target.id()));
  cy.on("tap", (evt) => {
    if (evt.target === cy) clearSelection();
  });

  document.getElementById("layout").addEventListener("change", (e) => {
    cy.layout({ name: e.target.value, animate: false, padding: 30 }).run();
  });

  document.getElementById("reset").addEventListener("click", () => {
    cy.fit(null, 30);
    clearSelection();
  });

  document.getElementById("search").addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    if (!q) {
      cy.elements().removeClass("dim");
      return;
    }
    cy.nodes().forEach((n) => {
      const d = n.data();
      const hay =
        (d.label || "").toLowerCase() + " " +
        d.id.toLowerCase() + " " +
        (d.tags || []).join(" ").toLowerCase() + " " +
        (d.generated_by || "").toLowerCase() + " " +
        (d.trust_tier || "").toLowerCase();
      n.toggleClass("dim", !hay.includes(q));
    });
    cy.edges().forEach((edge) => {
      const src = edge.source();
      const tgt = edge.target();
      edge.toggleClass("dim", src.hasClass("dim") || tgt.hasClass("dim"));
    });
  });

  document.getElementById("filter-type").addEventListener("change", (e) => {
    const t = e.target.value;
    if (!t) {
      cy.elements().removeClass("dim");
      return;
    }
    cy.nodes().forEach((n) => {
      n.toggleClass("dim", n.data("type") !== t);
    });
    cy.edges().forEach((edge) => {
      edge.toggleClass("dim", edge.source().hasClass("dim") || edge.target().hasClass("dim"));
    });
  });

  function clearSelection() {
    cy.elements().unselect();
    document.getElementById("detail-empty").hidden = false;
    document.getElementById("detail-content").hidden = true;
  }

  /** Normalize a path (POSIX-style), resolving . and .. segments. */
  function normalizePath(parts) {
    const out = [];
    for (const p of parts) {
      if (!p || p === ".") continue;
      if (p === "..") {
        if (out.length) out.pop();
        continue;
      }
      out.push(p);
    }
    return out.join("/");
  }

  /**
   * Resolve an href from a concept body into a concept id if it targets an in-bundle .md.
   * Supports absolute-from-root (/foo/bar.md) and relative (../examples/x.md) forms.
   */
  function resolveConceptId(href, fromConceptId) {
    if (!href || href.startsWith("#") || href.includes("://") || href.startsWith("mailto:")) {
      return null;
    }
    let path = href.split("#")[0].split("?")[0];
    if (!path.endsWith(".md")) return null;

    let conceptPath;
    if (path.startsWith("/")) {
      conceptPath = path.slice(1);
    } else {
      const baseDir = fromConceptId.includes("/")
        ? fromConceptId.slice(0, fromConceptId.lastIndexOf("/"))
        : "";
      const joined = baseDir ? baseDir + "/" + path : path;
      conceptPath = normalizePath(joined.split("/"));
    }
    if (conceptPath.endsWith(".md")) {
      conceptPath = conceptPath.slice(0, -3);
    }
    return nodeIndex[conceptPath] ? conceptPath : null;
  }

  function setTextOrDash(el, value) {
    el.textContent = value && String(value).trim() ? value : "—";
  }

  function showDetail(conceptId) {
    const data = nodeIndex[conceptId];
    if (!data) return;
    cy.elements().unselect();
    const node = cy.getElementById(conceptId);
    if (node) node.select();

    document.getElementById("detail-empty").hidden = true;
    const content = document.getElementById("detail-content");
    content.hidden = false;

    const chip = document.getElementById("detail-type");
    chip.textContent = data.type;
    chip.style.background = data.color;

    const statusChip = document.getElementById("detail-status");
    const status = data.status || "stable";
    if (status && status !== "stable") {
      statusChip.hidden = false;
      statusChip.textContent = status;
      statusChip.className = "status-chip status-" + status;
    } else {
      statusChip.hidden = true;
    }

    const trustChip = document.getElementById("detail-trust");
    const trust = data.trust_tier || "unverified";
    trustChip.hidden = false;
    trustChip.textContent = trust;
    trustChip.className = "trust-chip trust-" + trust.replace(/[^a-z-]/g, "");

    document.getElementById("detail-title").textContent = data.label;
    document.getElementById("detail-id").textContent = conceptId;
    document.getElementById("detail-description").textContent = data.description || "—";

    const resourceEl = document.getElementById("detail-resource");
    resourceEl.innerHTML = "";
    if (data.resource) {
      const a = document.createElement("a");
      a.href = data.resource;
      a.textContent = data.resource;
      a.target = "_blank";
      a.rel = "noopener";
      a.className = "external";
      resourceEl.appendChild(a);
    } else {
      resourceEl.textContent = "—";
    }

    const tagsEl = document.getElementById("detail-tags");
    tagsEl.innerHTML = "";
    if (data.tags && data.tags.length) {
      for (const t of data.tags) {
        const span = document.createElement("span");
        span.className = "tag";
        span.textContent = t;
        tagsEl.appendChild(span);
      }
    } else {
      tagsEl.textContent = "—";
    }

    setTextOrDash(document.getElementById("detail-status-text"), status);

    const genEl = document.getElementById("detail-generated");
    const by = data.generated_by || "";
    const at = data.generated_at || "";
    if (by || at) {
      genEl.textContent = [by, at].filter(Boolean).join(" · ");
    } else {
      genEl.textContent = "—";
    }

    setTextOrDash(document.getElementById("detail-trust-text"), trust);
    setTextOrDash(document.getElementById("detail-stale"), data.stale_after);

    const sourcesEl = document.getElementById("detail-sources");
    sourcesEl.innerHTML = "";
    const sources = data.sources || [];
    if (sources.length) {
      const ul = document.createElement("ul");
      ul.className = "sources-list";
      for (const s of sources) {
        const li = document.createElement("li");
        const label = s.title || s.id || s.resource || "source";
        if (s.resource && (s.resource.includes("://") || s.resource.startsWith("/"))) {
          const a = document.createElement("a");
          a.textContent = label;
          if (s.resource.includes("://")) {
            a.href = s.resource;
            a.target = "_blank";
            a.rel = "noopener";
            a.className = "external";
          } else {
            // Bundle path — try to open as concept
            const cid = resolveConceptId(
              s.resource.endsWith(".md") ? s.resource : s.resource + ".md",
              conceptId
            );
            if (cid) {
              a.className = "internal";
              a.href = "javascript:void(0)";
              a.addEventListener("click", (e) => {
                e.preventDefault();
                showDetail(cid);
              });
            } else {
              a.href = s.resource;
              a.className = "external";
            }
          }
          li.appendChild(a);
        } else {
          li.textContent = label;
        }
        if (s.id) {
          const code = document.createElement("code");
          code.className = "source-id";
          code.textContent = s.id;
          li.appendChild(document.createTextNode(" "));
          li.appendChild(code);
        }
        ul.appendChild(li);
      }
      sourcesEl.appendChild(ul);
    } else {
      sourcesEl.textContent = "—";
    }

    const body = bundle.bodies[conceptId] || "";
    const html = marked.parse(body, { breaks: false, gfm: true });
    const bodyEl = document.getElementById("detail-body");
    bodyEl.innerHTML = html;
    rewriteInternalLinks(bodyEl, conceptId);

    const bl = backlinks[conceptId] || [];
    const blSection = document.getElementById("detail-backlinks");
    const blList = document.getElementById("backlinks-list");
    blList.innerHTML = "";
    if (bl.length) {
      blSection.hidden = false;
      // unique sources
      const seen = new Set();
      for (const src of bl) {
        if (seen.has(src)) continue;
        seen.add(src);
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.textContent = nodeIndex[src]?.label || src;
        a.dataset.target = src;
        a.addEventListener("click", () => showDetail(src));
        li.appendChild(a);
        const muted = document.createElement("span");
        muted.className = "muted";
        muted.textContent = ` (${src})`;
        li.appendChild(muted);
        blList.appendChild(li);
      }
    } else {
      blSection.hidden = true;
    }

    cy.animate({ center: { eles: node }, zoom: Math.max(cy.zoom(), 1.0) }, { duration: 200 });
  }

  function rewriteInternalLinks(root, fromConceptId) {
    root.querySelectorAll("a[href]").forEach((a) => {
      const href = a.getAttribute("href");
      if (!href) return;
      const target = resolveConceptId(href, fromConceptId);
      if (target) {
        a.className = "internal";
        a.setAttribute("href", "javascript:void(0)");
        a.addEventListener("click", (e) => {
          e.preventDefault();
          showDetail(target);
        });
        return;
      }
      a.className = "external";
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener");
    });
  }

  // Prefer a useful root concept for skill-bundles / NIAID / generic OKF
  const preferredTypes = [
    "Publication",
    "Concept",
    "NIAID Blueprint Requirements",
    "NIAID Blueprint Section",
    "Document Status",
    "BigQuery Dataset",
    "Skill Bundle Example",
  ];
  let initial = null;
  for (const t of preferredTypes) {
    initial = bundle.nodes.find((n) => n.data.type === t);
    if (initial) break;
  }
  if (!initial) initial = bundle.nodes[0];
  if (initial) showDetail(initial.data.id);
})();
