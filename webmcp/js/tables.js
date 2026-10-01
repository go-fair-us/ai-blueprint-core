(async () => {
  const page = document.body.dataset.page || "home";
  const catalog = window.HandbookCatalog;

  function fill(id, html) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
  }

  if (page === "home") {
    const topics = await catalog.topics();
    fill(
      "topic-cards",
      topics
        .map(
          (t) => `
        <article class="card">
          <h2><a href="${t.href}">${t.title}</a></h2>
          <p>${t.summary}</p>
        </article>`,
        )
        .join(""),
    );
  }

  if (page === "metadata") {
    const elements = await catalog.metadataElements();
    fill(
      "element-table-body",
      elements
        .map(
          (el) => `
        <tr data-element="${el.name}">
          <td><code>${el.name}</code>${el.repeatable ? " **" : ""}</td>
          <td>${el.meaning}</td>
          <td>${el.defaultFormat}</td>
          <td>${el.pidOrOntology || "—"}</td>
        </tr>`,
        )
        .join(""),
    );
  }

  if (page === "persistent-identifiers") {
    const schemes = await catalog.pidSchemes();
    fill(
      "pid-table-body",
      schemes
        .map(
          (s) => `
        <tr data-scheme="${s.id}">
          <td>${s.abbreviation}</td>
          <td>${s.name}</td>
          <td>${s.covers.join(", ")}</td>
          <td>${s.summary}</td>
        </tr>`,
        )
        .join(""),
    );
  }

  if (page === "apis") {
    const data = await catalog.apiObjectives();
    fill(
      "api-objectives",
      data.objectives
        .map((o) => `<li><strong>${o.name}.</strong> ${o.summary}</li>`)
        .join(""),
    );
    fill(
      "api-fallbacks",
      data.fallbacks
        .map((o) => `<li><strong>${o.name}.</strong> ${o.summary}</li>`)
        .join(""),
    );
  }
})();
