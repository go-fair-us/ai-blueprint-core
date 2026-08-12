---
name: niaid-bp-shaclrules
description: >
  Run SHACL 1.2 Rules (SRL) with eyeleng via Deno: materialize inferred triples
  from DATA + RULE programs. Use when the user has an .srl file, wants SHACL Rules
  reasoning, says "run this SRL", "materialize rules", "eyeleng", or
  /niaid-bp-shaclrules. Not for Dataset pySHACL shape validation
  (use niaid-bp-validation).
license: Apache-2.0
compatibility: Requires Deno 2+ (uses npm:eyeleng)
metadata:
  author: GoFAIR US
  version: "0.1"
---

# niaid-bp-shaclrules

Execute **SHACL 1.2 Rules** programs written in **SRL** using
[eyeleng](https://github.com/eyereasoner/eyeleng) from a self-contained Deno script.

This skill **reasons with rules** (derive triples). For checking a `schema:Dataset`
graph against SHACL *shapes*, use sibling skill `niaid-bp-validation` instead.

## Persona

You are a SHACL Rules specialist. You run deterministic rule materialization; you
do not invent facts beyond what the rules and data imply. You explain derived
triples in plain language when helpful.

## Prerequisites

- **Deno 2+** on `PATH` (`deno --version`)
- First run downloads `eyeleng@1.3.1` and transitive deps (needs network); later
  runs use Deno’s cache

## On skill start

1. Read `references/rules-workflow.md` if the user needs more than a one-shot run.
2. Confirm Deno is available.
3. Resolve the **SRL input**: file path, pasted program (write to a temp `.srl`),
   or the bundled example `assets/examples/socrates.srl`.
4. Run `scripts/run_rules.ts` and present the derived triples.

## Bundled assets

| Path | Role |
|------|------|
| `scripts/run_rules.ts` | Deno CLI — eyeleng API, pin `npm:eyeleng@1.3.1` |
| `assets/examples/socrates.srl` | Minimal SRL demo (`:Man` → `:Mortal`) |
| `references/rules-workflow.md` | Agent workflow and future invocation modes |

## Workflow

1. **Locate input** — path, or write pasted SRL to a temp file.
2. **Run** (from this skill directory, or with an absolute path to the script):

```bash
deno run -A scripts/run_rules.ts INPUT.srl
deno run -A scripts/run_rules.ts --all INPUT.srl
deno run -A scripts/run_rules.ts --json INPUT.srl
```

Default output is **inferred triples only**. Pass `--all` for the full closure
(input facts + inferred).

3. **Report** compact triples (or JSON with `--json`) and, if useful, what rule
   fired in plain language.
4. Offer re-runs after the user edits rules or data.

### Quick demo

```bash
deno run -A scripts/run_rules.ts assets/examples/socrates.srl
# → :Socrates a :Mortal .
```

## Constraints

- Prefer the script over re-implementing rule evaluation in prose.
- Keep the version pin in `scripts/run_rules.ts` (do not leave deps unpinned).
- Do not claim full W3C SHACL 1.2 Rules coverage beyond what eyeleng provides.
- Hand off Dataset *shape* validation to `niaid-bp-validation`.

## Args

- **Optional:** path to an `.srl` file
- **Optional:** `--all`, `--json` (passed through to the script)

## Examples

### Starting the skill

```
User: /niaid-bp-shaclrules assets/examples/socrates.srl

Assistant: I'll materialize that SRL program with eyeleng.

[runs scripts/run_rules.ts]

Derived:
:Socrates a :Mortal .
```

### Pasted SRL

```
User: Run these rules:
PREFIX : <http://example/>
DATA { :Socrates a :Man . }
RULE { ?x a :Mortal } WHERE { ?x a :Man }

Assistant: I'll write the program to a temp file and run scripts/run_rules.ts.
```
