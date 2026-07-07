/* NIAID Blueprint Prompt Library — vanilla JS app
 * All content is driven by data.json. See SPEC.md / PLAN.md.
 */
(function () {
  'use strict';

  // ---- State -------------------------------------------------------------
  var DATA = null;
  var PROMPTS = {};        // id -> { prompt, path[] } for quick lookup
  var selectedId = null;

  // LLM target definitions. Base URLs kept here so they are easy to change.
  var TARGETS = {
    claude:        function (p) { return 'https://claude.ai/new?q=' + enc(p); },
    claudeDesktop: function (p) { return 'claude://claude.ai/new?q=' + enc(p); },
    chatgpt:       function (p) { return 'https://chatgpt.com/?q=' + enc(p); },
    openwebui:     function (p) { return 'http://localhost:8080/?q=' + enc(p); }
  };

  function enc(s) { return encodeURIComponent(s); }

  // ---- DOM refs ----------------------------------------------------------
  var treeEl     = document.getElementById('tree');
  var contentEl  = document.getElementById('content');
  var searchEl   = document.getElementById('searchInput');
  var noResults  = document.getElementById('noResults');
  var sidebar    = document.getElementById('sidebar');
  var backdrop   = document.getElementById('backdrop');
  var toastEl    = document.getElementById('toast');
  var toastTimer = null;

  // ---- Boot --------------------------------------------------------------
  fetch('data.json')
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(init)
    .catch(function (err) {
      contentEl.innerHTML =
        '<div class="rounded-lg border border-red-200 bg-red-50 p-6 text-red-700">' +
        '<h2 class="mb-1 font-semibold">Could not load data.json</h2>' +
        '<p class="text-sm">' + escapeHtml(String(err.message || err)) + '</p>' +
        '<p class="mt-2 text-sm">If you opened this file directly, serve it over HTTP ' +
        '(e.g. <code class="rounded bg-red-100 px-1">python3 -m http.server</code>).</p></div>';
      console.error(err);
    });

  function init(data) {
    DATA = data;
    indexPrompts(data.categories, []);
    renderMeta(data.meta);
    renderTree(data.categories);
    renderWelcome();
    wireEvents();
    // Support deep-linking via hash (#prompt-id)
    var hashId = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (hashId && PROMPTS[hashId]) selectPrompt(hashId);
  }

  // Build a flat lookup of prompts + their breadcrumb path.
  function indexPrompts(nodes, path) {
    (nodes || []).forEach(function (node) {
      var nextPath = path.concat(node.title);
      if (node.children) indexPrompts(node.children, nextPath);
      (node.prompts || []).forEach(function (p) {
        PROMPTS[p.id] = { prompt: p, path: nextPath };
      });
    });
  }

  // ---- Rendering: meta ---------------------------------------------------
  function renderMeta(meta) {
    if (!meta) return;
    document.title = meta.title || document.title;
    var titleEl = document.getElementById('siteTitle');
    if (meta.title) titleEl.textContent = meta.title;
    var metaEl = document.getElementById('siteMeta');
    var bits = [];
    if (meta.version) bits.push('v' + meta.version);
    if (meta.lastUpdated) bits.push('updated ' + meta.lastUpdated);
    metaEl.textContent = bits.join(' · ');
  }

  // ---- Rendering: tree ---------------------------------------------------
  function renderTree(categories) {
    treeEl.innerHTML = '';
    categories.forEach(function (node) {
      treeEl.appendChild(buildNode(node, 0));
    });
  }

  // A node may have `children` (sub-folders) and/or `prompts` (leaves).
  function buildNode(node, depth) {
    var li = document.createElement('div');
    li.setAttribute('role', 'treeitem');

    var isFolder = !!(node.children || node.prompts);
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className =
      'group flex w-full items-center gap-1.5 rounded-md py-1.5 pr-2 text-left ' +
      'font-medium text-slate-700 hover:bg-slate-100';
    btn.style.paddingLeft = (8 + depth * 14) + 'px';
    btn.dataset.nodeTitle = (node.title || '').toLowerCase();

    // Chevron
    var chevron = document.createElement('span');
    chevron.className = 'flex h-4 w-4 shrink-0 items-center justify-center text-slate-400 transition-transform';
    chevron.innerHTML = '<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>';
    btn.appendChild(chevron);

    var label = document.createElement('span');
    label.className = 'truncate';
    label.textContent = node.title || '(untitled)';
    btn.appendChild(label);

    li.appendChild(btn);

    // Children container
    var kids = document.createElement('div');
    kids.className = 'mt-0.5 space-y-0.5';
    // Top-level categories start expanded; deeper ones collapsed.
    var expanded = depth === 0;
    if (!expanded) kids.classList.add('hidden');
    if (expanded) chevron.style.transform = 'rotate(90deg)';

    (node.children || []).forEach(function (child) {
      kids.appendChild(buildNode(child, depth + 1));
    });
    (node.prompts || []).forEach(function (p) {
      kids.appendChild(buildLeaf(p, depth + 1));
    });
    li.appendChild(kids);

    btn.setAttribute('aria-expanded', String(expanded));
    btn.addEventListener('click', function () {
      var nowHidden = kids.classList.toggle('hidden');
      chevron.style.transform = nowHidden ? '' : 'rotate(90deg)';
      btn.setAttribute('aria-expanded', String(!nowHidden));
    });

    li._nodeButton = btn;
    li._kids = kids;
    li._chevron = chevron;
    li._isFolder = isFolder;
    return li;
  }

  function buildLeaf(prompt, depth) {
    var wrap = document.createElement('div');
    wrap.setAttribute('role', 'treeitem');

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.dataset.promptId = prompt.id;
    btn.dataset.nodeTitle = ((prompt.title || '') + ' ' + (prompt.description || '')).toLowerCase();
    btn.className =
      'prompt-leaf flex w-full items-start gap-1.5 rounded-md py-1.5 pr-2 text-left ' +
      'text-slate-600 hover:bg-slate-100';
    btn.style.paddingLeft = (8 + depth * 14) + 'px';

    var icon = document.createElement('span');
    icon.className = 'mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center text-slate-400';
    icon.innerHTML = '<svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>';
    btn.appendChild(icon);

    var label = document.createElement('span');
    label.className = 'leading-snug';
    label.textContent = prompt.title || '(untitled prompt)';
    btn.appendChild(label);

    btn.addEventListener('click', function () {
      selectPrompt(prompt.id);
      closeSidebar();
    });

    wrap._leafButton = btn;
    wrap.appendChild(btn);
    return wrap;
  }

  // ---- Rendering: main panel --------------------------------------------
  function renderWelcome() {
    var count = Object.keys(PROMPTS).length;
    contentEl.innerHTML =
      '<div class="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">' +
        '<h2 class="text-xl font-semibold text-slate-900">Welcome</h2>' +
        '<p class="mt-2 text-slate-600">' +
          (DATA.meta && DATA.meta.description ? escapeHtml(DATA.meta.description) : '') +
        '</p>' +
        '<p class="mt-4 text-slate-600">Browse the categories on the left to find a prompt, then send it to ' +
        'your preferred AI assistant with one click. There ' + (count === 1 ? 'is' : 'are') +
        ' <strong>' + count + '</strong> ready-to-use prompt' + (count === 1 ? '' : 's') + ' available.</p>' +
        '<div class="mt-6 grid gap-3 sm:grid-cols-2">' +
          featureCard('Browse', 'Drill down through Blueprint categories and topics.') +
          featureCard('Copy or send', 'Copy any prompt or open it pre-filled in Claude, ChatGPT, or OpenWebUI.') +
        '</div>' +
        '<p class="mt-6 text-xs text-slate-400">' +
          (DATA.meta && DATA.meta.source ? escapeHtml(DATA.meta.source) : '') + '</p>' +
      '</div>';
  }

  function featureCard(title, body) {
    return '<div class="rounded-lg border border-slate-200 bg-slate-50 p-4">' +
      '<h3 class="text-sm font-semibold text-slate-800">' + escapeHtml(title) + '</h3>' +
      '<p class="mt-1 text-sm text-slate-500">' + escapeHtml(body) + '</p></div>';
  }

  function selectPrompt(id) {
    var entry = PROMPTS[id];
    if (!entry) return;
    selectedId = id;
    if (history.replaceState) history.replaceState(null, '', '#' + encodeURIComponent(id));

    highlightSelected(id);
    var p = entry.prompt;
    var path = entry.path;
    var placeholders = extractPlaceholders(p.prompt);
    var values = {}; // token -> user-supplied value

    contentEl.innerHTML =
      '<article class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">' +
        '<nav class="mb-3 text-xs text-slate-400">' + buildBreadcrumb(path) + '</nav>' +
        '<h2 class="text-2xl font-bold leading-tight text-slate-900">' + escapeHtml(p.title) + '</h2>' +
        (p.description ? '<p class="mt-2 text-slate-600">' + escapeHtml(p.description) + '</p>' : '') +
        '<div id="fillPanel" class="mt-5"></div>' +
        '<div id="actionRow" class="mt-5 flex flex-wrap gap-2"></div>' +
        '<div class="mt-6">' +
          '<div class="mb-1.5 flex items-center justify-between">' +
            '<span class="text-xs font-semibold uppercase tracking-wide text-slate-400">Prompt' +
              (placeholders.length ? ' <span class="ml-1 normal-case tracking-normal text-slate-400">(with your values filled in)</span>' : '') +
            '</span>' +
          '</div>' +
          '<pre class="prompt-block max-h-[28rem] overflow-auto rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-800"><code></code></pre>' +
        '</div>' +
      '</article>';

    var codeEl = contentEl.querySelector('pre code');
    var updateActions = renderActions(document.getElementById('actionRow'));

    // Recompute the effective prompt (substitutions + "ask me" note) and push
    // it into the display block and every action button.
    function refresh() {
      var eff = computeEffective(p.prompt, placeholders, values);
      codeEl.textContent = eff; // textContent avoids HTML injection
      updateActions(eff);
    }

    if (placeholders.length) {
      renderFillForm(document.getElementById('fillPanel'), placeholders, values, refresh);
    }
    refresh();

    contentEl.scrollIntoView({ block: 'start' });
    if (window.innerWidth < 1024) window.scrollTo(0, 0);
  }

  // ---- Placeholders ({{token}}) -----------------------------------------
  var PLACEHOLDER_RE = /\{\{\s*([\w.\-]+)\s*\}\}/g;

  function extractPlaceholders(text) {
    var seen = {}, out = [], m;
    PLACEHOLDER_RE.lastIndex = 0;
    while ((m = PLACEHOLDER_RE.exec(text))) {
      if (!seen[m[1]]) { seen[m[1]] = true; out.push(m[1]); }
    }
    return out;
  }

  // Substitute filled values; for anything left blank, keep the {{token}} in
  // place and append a note asking the assistant to collect it from the user.
  function computeEffective(text, placeholders, values) {
    var out = text.replace(PLACEHOLDER_RE, function (match, name) {
      var v = values[name];
      return (v && v.trim() !== '') ? v : match;
    });
    var missing = placeholders.filter(function (t) {
      return !values[t] || !values[t].trim();
    });
    if (missing.length) {
      out += '\n\n---\n' +
        'Note: I have not yet provided values for the placeholder' +
        (missing.length === 1 ? '' : 's') + ' shown above in double braces: ' +
        missing.map(function (t) { return '{{' + t + '}}'; }).join(', ') + '. ' +
        'Before completing the task, please ask me to provide ' +
        (missing.length === 1 ? 'it' : 'each of these') + ', then continue.';
    }
    return out;
  }

  function humanize(token) {
    var s = token.replace(/[_\-.]+/g, ' ').trim();
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  function renderFillForm(container, placeholders, values, onChange) {
    var panel = document.createElement('div');
    panel.className = 'rounded-lg border border-brand-200 bg-brand-50 p-4';

    var head = document.createElement('div');
    head.innerHTML =
      '<h3 class="text-sm font-semibold text-brand-800">Fill in the details</h3>' +
      '<p class="mt-1 text-xs text-brand-700">Optional. Type a value for any field and it is inserted into the prompt below. ' +
      'Leave a field blank and the assistant will ask you for it.</p>';
    panel.appendChild(head);

    var grid = document.createElement('div');
    grid.className = 'mt-3 space-y-3';
    placeholders.forEach(function (token) {
      var field = document.createElement('label');
      field.className = 'block';

      var lab = document.createElement('span');
      lab.className = 'mb-1 block text-xs font-medium text-slate-600';
      lab.textContent = humanize(token) + '  {{' + token + '}}';

      var ta = document.createElement('textarea');
      ta.rows = 2;
      ta.className = 'w-full resize-y rounded-md border border-slate-300 bg-white px-3 py-2 ' +
        'text-sm text-slate-800 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200';
      ta.setAttribute('aria-label', humanize(token));
      ta.addEventListener('input', function () {
        values[token] = ta.value;
        onChange();
      });

      field.appendChild(lab);
      field.appendChild(ta);
      grid.appendChild(field);
    });
    panel.appendChild(grid);
    container.appendChild(panel);
  }

  function buildBreadcrumb(path) {
    return path.map(function (seg) { return escapeHtml(seg); }).join(
      ' <span class="text-slate-300">/</span> '
    );
  }

  // Builds the action row once and returns an update(text) function that keeps
  // the Copy handler and every link's href pointed at the current prompt text.
  function renderActions(row) {
    var current = '';
    var links = [];

    var copyBtn = document.createElement('button');
    copyBtn.type = 'button';
    copyBtn.className = baseBtnClass('primary');
    copyBtn.innerHTML = copyIcon() + '<span>Copy</span>';
    copyBtn.addEventListener('click', function () { copyToClipboard(current); });
    row.appendChild(copyBtn);

    function addLink(label, iconSvg, urlFn) {
      var a = document.createElement('a');
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.className = baseBtnClass('secondary');
      a.innerHTML = iconSvg + '<span>' + escapeHtml(label) + '</span>';
      a._urlFn = urlFn;
      links.push(a);
      row.appendChild(a);
    }

    addLink('Claude', claudeIcon(), TARGETS.claude);
    addLink('Claude Desktop', claudeIcon(), TARGETS.claudeDesktop);
    addLink('ChatGPT', chatgptIcon(), TARGETS.chatgpt);
    addLink('OpenWebUI', openwebuiIcon(), TARGETS.openwebui);

    return function update(text) {
      current = text;
      links.forEach(function (a) { a.href = a._urlFn(text); });
    };
  }

  function baseBtnClass(variant) {
    var base = 'inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium ' +
               'shadow-sm transition focus:outline-none focus:ring-2 focus:ring-brand-300';
    if (variant === 'primary') {
      return base + ' bg-brand-600 text-white hover:bg-brand-700';
    }
    return base + ' border border-slate-300 bg-white text-slate-700 hover:bg-slate-50';
  }

  // ---- Selection highlight ----------------------------------------------
  function highlightSelected(id) {
    var buttons = treeEl.querySelectorAll('.prompt-leaf');
    buttons.forEach(function (b) {
      var active = b.dataset.promptId === id;
      b.classList.toggle('bg-brand-50', active);
      b.classList.toggle('text-brand-800', active);
      b.classList.toggle('font-semibold', active);
      if (active) revealAncestors(b);
    });
  }

  // Expand any collapsed folders above the selected leaf.
  function revealAncestors(el) {
    var node = el.parentElement;
    while (node && node !== treeEl) {
      if (node.classList && node.classList.contains('hidden')) {
        node.classList.remove('hidden');
        // find the controlling folder button (previous sibling wrapper)
        var owner = node.parentElement;
        if (owner && owner._chevron) owner._chevron.style.transform = 'rotate(90deg)';
        if (owner && owner._nodeButton) owner._nodeButton.setAttribute('aria-expanded', 'true');
      }
      node = node.parentElement;
    }
  }

  // ---- Search ------------------------------------------------------------
  function wireEvents() {
    searchEl.addEventListener('input', debounce(runSearch, 120));

    document.getElementById('menuToggle').addEventListener('click', openSidebar);
    document.getElementById('sidebarClose').addEventListener('click', closeSidebar);
    backdrop.addEventListener('click', closeSidebar);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeSidebar();
    });
    window.addEventListener('hashchange', function () {
      var id = decodeURIComponent(location.hash.replace(/^#/, ''));
      if (id && PROMPTS[id] && id !== selectedId) selectPrompt(id);
    });
  }

  function runSearch() {
    var q = searchEl.value.trim().toLowerCase();
    var anyVisible = filterTree(treeEl, q);
    noResults.classList.toggle('hidden', anyVisible || !q);
  }

  // Recursively show/hide tree items. Returns true if this subtree has a match.
  function filterTree(container, q) {
    var items = container.children;
    var anyMatch = false;
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      if (item.getAttribute && item.getAttribute('role') !== 'treeitem') continue;

      var self = item._nodeButton || item._leafButton;
      var selfText = self ? (self.dataset.nodeTitle || '') : '';
      var selfMatch = !q || selfText.indexOf(q) !== -1;

      var childMatch = false;
      if (item._kids) {
        childMatch = filterTree(item._kids, q);
      }

      var visible = selfMatch || childMatch;
      item.style.display = visible ? '' : 'none';

      // While searching, auto-expand folders that contain matches.
      if (item._kids) {
        if (q && childMatch) {
          item._kids.classList.remove('hidden');
          if (item._chevron) item._chevron.style.transform = 'rotate(90deg)';
        } else if (!q) {
          // Restore default collapsed/expanded state handled elsewhere; leave as-is.
        }
      }

      if (visible) anyMatch = true;
    }
    return anyMatch;
  }

  // ---- Clipboard + toast -------------------------------------------------
  function copyToClipboard(text) {
    var done = function () { showToast('Copied to clipboard'); };
    var fail = function () { fallbackCopy(text); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(fail);
    } else {
      fallbackCopy(text);
    }
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      showToast('Copied to clipboard');
    } catch (e) {
      showToast('Copy failed — select and copy manually');
    }
    document.body.removeChild(ta);
  }

  function showToast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.remove('translate-y-4', 'opacity-0');
    toastEl.classList.add('translate-y-0', 'opacity-100');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toastEl.classList.add('translate-y-4', 'opacity-0');
      toastEl.classList.remove('translate-y-0', 'opacity-100');
    }, 2000);
  }

  // ---- Mobile sidebar ----------------------------------------------------
  function openSidebar() {
    sidebar.classList.remove('-translate-x-full');
    backdrop.classList.remove('hidden');
    document.getElementById('menuToggle').setAttribute('aria-expanded', 'true');
  }
  function closeSidebar() {
    if (window.innerWidth >= 1024) return; // sidebar is static on desktop
    sidebar.classList.add('-translate-x-full');
    backdrop.classList.add('hidden');
    document.getElementById('menuToggle').setAttribute('aria-expanded', 'false');
  }

  // ---- Helpers -----------------------------------------------------------
  function debounce(fn, ms) {
    var t;
    return function () {
      var args = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(self, args); }, ms);
    };
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  // ---- Icons -------------------------------------------------------------
  function copyIcon() {
    return '<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>';
  }
  function claudeIcon() {
    return '<svg class="h-4 w-4 text-[#d97757]" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 3.2l2.1 5.1 5.4.3-4.2 3.4 1.4 5.2L12 16.9 7.3 19.4l1.4-5.2-4.2-3.4 5.4-.3L12 5.2z"/></svg>';
  }
  function chatgptIcon() {
    return '<svg class="h-4 w-4 text-[#10a37f]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4"/></svg>';
  }
  function openwebuiIcon() {
    return '<svg class="h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>';
  }
})();
