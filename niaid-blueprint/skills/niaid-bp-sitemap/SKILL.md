---
name: niaid-bp-sitemap
description: >
  Check that a public site publishes a sitemap, that the XML is well formed,
  and that a sample of its URLs answer. Looks in robots.txt, then
  /sitemap.xml and /sitemap_index.xml. Use when the user gives a repository
  or site URL and asks about sitemap.xml, or runs /niaid-bp-sitemap.
license: Apache-2.0
metadata:
  author: GoFAIR US
  version: "0.1"
---

# niaid-bp-sitemap

You check one sitemap. You run `scripts/check_sitemap.py` and report its JSON. You do not invent statuses, URLs, or `lastmod` values.

This check does not decide whether a `loc` is a dataset or study record. That question is `prompts/evals/sitemap.md`.

## On skill start

1. Take the site origin or a sitemap URL from the skill argument or the user message. If none was given, ask once for it, then stop until the user provides one.
2. Run the script from any working directory. `uv` installs `httpx` for this script and does not sync the Blueprint project:

```bash
uv run --no-project SKILL_DIR/scripts/check_sitemap.py TARGET
```

`SKILL_DIR` is the absolute path of the directory containing this `SKILL.md`. `TARGET` is an `http(s)` origin or a URL ending in `.xml` or `.xml.gz`.

Optional: `--sample 10` (default) and `--seed 0`. The seed keeps a repeat run on the same file requesting the same URLs.

3. Read the JSON on stdout. Exit 0 means the file was found and the XML parsed. Sampled URLs may still be broken. Exit 1 means the sitemap is missing or the XML did not parse. Exit 2 means the target was not an `http(s)` URL.

## What you report

Say where the file was found (`given`, `robots`, or `well-known`), the sitemap URL, whether the XML parsed, and whether the document is a `urlset` or a `sitemapindex`.

For an index, say how many children it names and which one child was opened. The others are in `not_opened`.

List each warning in the JSON. Then a table of `samples`: requested URL, status, and final URL. A `lastmod` that fails `lastmod_ok` is a bad date. A missing `lastmod` is optional and is not a failure.

Name one next step when the file is missing, the XML did not parse, or a sampled URL did not return a successful status.

## Constraints

- Do not fetch URLs the script did not request.
- Do not send credentials.
- Do not treat `changefreq`, `priority`, or a missing `lastmod` as a failed sitemap.
- Do not claim the sampled URLs are dataset records.
