---
name: niaid-bp-llms
description: >
  Check that a site publishes an llms.txt file, that the Markdown follows
  the llms.txt v2 spec (H1, optional blockquote, H2 file lists), and that
  a sample of its same-host links answer. Use when the user gives a
  repository or site URL and asks about llms.txt, or runs /niaid-bp-llms.
license: Apache-2.0
metadata:
  author: GoFAIR US
  version: "0.1"
---

# niaid-bp-llms

You check one `llms.txt`. You run `scripts/check_llms.py` and report its JSON. You do not invent titles, links, or status codes.

`prompts/evals/llms-txt.md` is the scored question, including a record page. This check opens one file and one homepage.

The format is [The /llms.txt file, v2](https://llmstxt.org/) (Jeremy Howard, 10 August 2026). The H1 is the only required section. An `Optional` H2 is a convention. Links may leave the host. A linked `llms.txt` is more specific for its path and is not opened.

## On skill start

1. Take the site origin or an `llms.txt` URL from the skill argument or the user message. If none was given, ask once for it, then stop until the user provides one.
2. Run the script from any working directory. `uv` installs `httpx` for this script and does not sync the Blueprint project:

```bash
uv run --no-project SKILL_DIR/scripts/check_llms.py TARGET
```

`SKILL_DIR` is the absolute path of the directory containing this `SKILL.md`. `TARGET` is an `http(s)` origin or a URL whose path ends in `llms.txt`.

Optional: `--sample 10` (default) and `--seed 0`.

3. Read the JSON on stdout. Exit 0 means the file was found and has a leading H1 with the sections in order. Samples may still fail, and the homepage may lack link relations. Exit 1 means `llms.txt` is missing, the body is HTML, or the section order is not the spec. Exit 2 means the target was not an `http(s)` URL.

## What you report

Say where the file was found (`given`, `well-known`, or `homepage`), the H1, and whether the body is well formed.

For each H2 section, name it and say whether it is `Optional`. Then a table of `samples`: requested URL, status, final URL, and link shape (`html-md`, `md`, `index-md`, or `other`). Off-host links are counted in `off_host_count` and are not requested. URLs in `nested` were not opened.

From `homepage`, say whether `rel="alternate"` with `type="text/markdown"` is present, and whether `rel="describedby"` points at an `llms.txt`.

List each warning. Name one next step when the file is missing, the H1 is missing, or a sampled URL did not return a successful status.

## Constraints

- Do not fetch URLs the script did not request.
- Do not send credentials.
- Do not open a nested `llms.txt`.
- Do not treat an off-host link, a missing blockquote, or a missing `Optional` section as a failed file.
- Do not claim the links are dataset records.
- Do not test `Accept: text/markdown`. That question is `prompts/evals/markdown-negotiation.md`.
