---
name: niaid-bp-robots
description: >
  Check a site's robots.txt for AI crawler groups, IETF Content-Usage
  (train-ai), Cloudflare Content-Signal, and Crawl-delay. One homepage
  request records HTTP 429, Retry-After, and a Content-Usage header.
  Use when the user gives a repository or site URL and asks about
  robots.txt, or runs /niaid-bp-robots.
license: Apache-2.0
metadata:
  author: GoFAIR US
  version: "0.1"
---

# niaid-bp-robots

You check one `robots.txt`. You run `scripts/check_robots.py` and report its JSON. You do not invent groups, preferences, or status codes.

`prompts/evals/robots-policy.md` is the scored visitor-class question. This check only says what the file and one homepage response published.

HTTP 429 and `Retry-After` are response headers. A comment in `robots.txt` is not a rate-limit setting. `Content-Usage: train-ai=n` is a preference request, not an enforcement.

## On skill start

1. Take the site origin or a `robots.txt` URL from the skill argument or the user message. If none was given, ask once for it, then stop until the user provides one.
2. Run the script from any working directory. `uv` installs `httpx` for this script and does not sync the Blueprint project:

```bash
uv run --no-project SKILL_DIR/scripts/check_robots.py TARGET
```

`SKILL_DIR` is the absolute path of the directory containing this `SKILL.md`. `TARGET` is an `http(s)` origin or a URL whose path ends in `robots.txt`.

3. Read the JSON on stdout. Exit 0 means the file was fetched and the body is robots text. `train-ai` may still be unknown, and the homepage may not be 429. Exit 1 means `robots.txt` is missing, not HTTP 200, or not a robots body. Exit 2 means the target was not an `http(s)` URL.

## What you report

For each group, say the product tokens, whether `/` may be crawled, and `train_ai` (`y`, `n`, `unknown`, or `not-applicable`). A named group replaces `*`. Usage lines on `*` do not apply to that token.

Say whether any group states `Content-Signal: ai-train=no`, and quote a `Crawl-delay` when one is present. `Crawl-delay` is not part of RFC 9309.

From `http`, say the homepage status, `retry_after`, `content_usage`, and `rate_limit_observed`. `rate_limit_observed` is true only when that one response is 429 and includes `Retry-After`.

List each warning. Name one next step when the file is missing, when a crawlable group does not state `train-ai=n`, or when the homepage did not show a 429.

## Constraints

- Do not fetch URLs the script did not request. Do not send a burst to provoke a 429.
- Do not send credentials.
- Do not treat a `#` comment as a rule.
- Do not recommend that the site allow or deny training.
- Do not open the sitemap. That check is `niaid-bp-sitemap`.
