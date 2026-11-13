(() => {
  const NAV = [
    { slug: "home", title: "Home", href: "/" },
    { slug: "overview", title: "Overview", href: "/topics/overview.html" },
    { slug: "metadata", title: "Metadata", href: "/topics/metadata.html" },
    { slug: "persistent-identifiers", title: "Identifiers", href: "/topics/persistent-identifiers.html" },
    { slug: "apis", title: "APIs", href: "/topics/apis.html" },
    { slug: "citation", title: "Citation", href: "/topics/citation.html" },
    { slug: "outreach", title: "Outreach", href: "/topics/outreach.html" },
    { slug: "chat", title: "Chat", href: "/chatbp.html" },
  ];

  function currentSlug() {
    return document.body.dataset.page || "home";
  }

  function header() {
    const page = currentSlug();
    const nav = NAV.map((item) => {
      const current = item.slug === page ? ' aria-current="page"' : "";
      return `<a href="${item.href}"${current}>${item.title}</a>`;
    }).join("");

    return `
      <header class="site-header">
        <div class="header-row">
          <div>
            <p class="site-title"><a href="/">NIAID Blueprint Handbook</a></p>
            <p class="site-tag">Static test pages for Chrome WebMCP</p>
          </div>
          <span id="webmcp-badge" class="webmcp-badge" data-state="missing">Checking WebMCP…</span>
        </div>
        <nav class="site-nav" aria-label="Handbook">${nav}</nav>
      </header>
    `;
  }

  function footer() {
    return `
      <footer class="site-footer">
        Topic pages paraphrase Blueprint themes from <code>okf/bundles/niaid_blueprint/</code>.
        They are not an OKF bundle and not the MCP knowledge server in <code>mcp_bp/</code>.
        Serve with <code>python webmcp/serve.py</code> so origin isolation headers are set.
      </footer>
    `;
  }

  function extras() {
    const open = currentSlug() === "home" ? " open" : "";
    return `
      <div id="tool-result" class="tool-result" hidden>
        <strong data-result-title>Last tool result</strong>
        <pre></pre>
      </div>
      <details class="tester-wrap"${open}>
        <summary>WebMCP tester</summary>
        <div id="webmcp-tester" class="tester"></div>
      </details>
    `;
  }

  const mountHeader = document.getElementById("site-header");
  const mountFooter = document.getElementById("site-footer");
  const mountExtras = document.getElementById("page-extras");
  if (mountHeader) mountHeader.outerHTML = header();
  else document.body.insertAdjacentHTML("afterbegin", header());
  if (mountExtras) mountExtras.innerHTML = extras();
  if (mountFooter) mountFooter.outerHTML = footer();
  else document.body.insertAdjacentHTML("beforeend", footer());
})();
