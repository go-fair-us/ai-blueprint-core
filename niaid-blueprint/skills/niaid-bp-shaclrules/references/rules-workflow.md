# SHACL Rules workflow (eyeleng)

## What this skill does

Runs a **SHACL 1.2 Rules** program in **SRL** syntax through
[eyeleng](https://github.com/eyereasoner/eyeleng) and prints the materialization
result (inferred triples, or the full closure with `--all`).

SRL is *not* Dataset SHACL shape validation. Shapes checks on
`schema:Dataset` graphs belong to `niaid-bp-validation` (pySHACL).

## Prerequisites

```bash
deno --version   # Deno 2+
```

First invocation downloads `eyeleng@1.3.1` and its npm tree. Subsequent runs use
the Deno cache.

## Steps for the agent

1. Obtain SRL source (path, paste → temp file, or `assets/examples/socrates.srl`).
2. From the skill directory:

```bash
deno run -A scripts/run_rules.ts INPUT.srl
```

3. Read stdout (triples or JSON). Treat stderr diagnostics as warnings/errors.
4. Summarize derived facts for the user.

## CLI surface (v1)

| Invocation | Result |
|------------|--------|
| `… FILE.srl` | Inferred triples only |
| `… --all FILE.srl` | Input facts + inferred |
| `… --json FILE.srl` | Structured JSON via eyeleng `toJSON` |
| `… -` | Read program from stdin |
| `… --help` | Usage text |

Exit non-zero on missing file, unknown flags, or eyeleng parse/analysis/runtime
failure.

## Socrates example

Input (`assets/examples/socrates.srl`):

```text
PREFIX : <http://example/>

DATA {
  :Socrates a :Man .
}

RULE { ?x a :Mortal } WHERE { ?x a :Man }
```

Default output:

```text
:Socrates a :Mortal .
```

With `--all`:

```text
:Socrates a :Man .
:Socrates a :Mortal .
```

## How the script loads eyeleng

The npm package has no `main`/`exports` root. The skill imports the API entry:

```typescript
import { run, formatTriples, resultTriples, toJSON } from "npm:eyeleng@1.3.1/src/api.js";
```

One-liner alternative (no skill wrapper):

```bash
deno run -A npm:eyeleng@1.3.1 path/to/file.srl
```

Prefer `scripts/run_rules.ts` so flags and pins stay consistent for agents.

## Future invocation modes

Not implemented yet; extend `scripts/run_rules.ts` when needed (see eyeleng README):

| Mode | eyeleng surface |
|------|-----------------|
| RDF Rules (Turtle) | `runAsync(source, { syntax: 'rdf' })` |
| Query | `runQuery` / `--query` / `--query-file` |
| Shapes + targeted `FOR` | shapes graph + shape engine |
| Rules then validate | `runAndValidateAsync` / `--shapes` + `--validate` |
| Check only | `compile` / `analyze` / `--check` / `--deps` |
| Hybrid / no-hybrid | `{ hybrid: true \| false }` |

Keep new flags agent-friendly: no prompts, `--help`, structured errors, data on
stdout.
