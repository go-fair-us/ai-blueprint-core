#!/usr/bin/env -S deno run --allow-read --allow-env --allow-net --allow-sys
/**
 * Run SHACL 1.2 Rules (SRL) with eyeleng.
 *
 * Usage:
 *   deno run -A scripts/run_rules.ts [--all] [--json] FILE.srl
 *   cat FILE.srl | deno run -A scripts/run_rules.ts [--all] [--json] -
 *
 * Extension points (not yet wired): runAsync (RDF Rules), runQuery,
 * runAndValidateAsync (--shapes/--validate), compile/analyze (--check/--deps).
 */

// eyeleng has no package "main"; import the API entry explicitly.
import {
  run,
  formatTriples,
  resultTriples,
  toJSON,
} from "npm:eyeleng@1.3.1/src/api.js";

const USAGE = `Usage: scripts/run_rules.ts [OPTIONS] FILE

Run a SHACL 1.2 Rules (SRL) program with eyeleng and print derived triples.

Arguments:
  FILE               Path to an .srl file, or "-" for stdin

Options:
  --all              Print full closure (input facts + inferred)
  --json             Print JSON instead of compact triples
  -h, --help         Show this help

Examples:
  deno run -A scripts/run_rules.ts assets/examples/socrates.srl
  deno run -A scripts/run_rules.ts --all assets/examples/socrates.srl
  cat rules.srl | deno run -A scripts/run_rules.ts --json -
`;

function fail(message: string, code = 1): never {
  console.error(`run_rules: ${message}`);
  Deno.exit(code);
}

function parseArgs(argv: string[]): {
  all: boolean;
  json: boolean;
  help: boolean;
  file: string | null;
} {
  let all = false;
  let json = false;
  let help = false;
  let file: string | null = null;

  for (const arg of argv) {
    if (arg === "--all") all = true;
    else if (arg === "--json") json = true;
    else if (arg === "-h" || arg === "--help") help = true;
    else if (arg.startsWith("-") && arg !== "-") {
      fail(`Unknown option ${arg}.\n\n${USAGE}`);
    } else if (file === null) file = arg;
    else fail(`Unexpected argument ${arg}.\n\n${USAGE}`);
  }

  return { all, json, help, file };
}

async function readSource(file: string): Promise<string> {
  if (file === "-") {
    return new TextDecoder().decode(await Deno.readAll(Deno.stdin));
  }
  try {
    return await Deno.readTextFile(file);
  } catch (err) {
    fail(`Cannot read ${file}: ${(err as Error).message}`);
  }
}

async function main(): Promise<void> {
  const opts = parseArgs(Deno.args);

  if (opts.help) {
    console.log(USAGE.trimEnd());
    return;
  }
  if (!opts.file) {
    fail(`FILE is required.\n\n${USAGE}`);
  }

  const source = await readSource(opts.file);

  let result: ReturnType<typeof run>;
  try {
    result = run(source);
  } catch (err) {
    fail((err as Error).message);
  }

  if (Array.isArray(result.diagnostics)) {
    for (const d of result.diagnostics) {
      const severity = d.severity ?? "info";
      console.error(`run_rules: ${severity}: ${d.message}`);
    }
  }

  if (opts.json) {
    console.log(JSON.stringify(toJSON(result, { all: opts.all }), null, 2));
    return;
  }

  const triples = resultTriples(result, null, { all: opts.all });
  const text = formatTriples(triples, result.prefixes);
  if (text) console.log(text);
}

if (import.meta.main) {
  await main();
}
