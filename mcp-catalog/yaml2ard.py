#!/usr/bin/env python3
"""yaml2ard.py -- convert the curated MCP catalog (YAML) into an ARD v0.91 manifest.

ARD = Agentic Resource Discovery, https://agenticresourcediscovery.org/spec/ (v0.91).

The YAML file is the source of truth. Each item under `entries:` already uses ARD
term names (identifier, displayName, type, url|data, description, tags, version,
updatedAt, representativeQueries, capabilities, metadata, trustManifest). Curation
terms use a namespace prefix (default `cat:`) declared in `catalog["@context"]`.

Output is `{"entries": [...]}` -- the only top-level member ARD defines (§5.1,
Appendix D ArdManifest). A `catalog` member with provenance is added unless
--entries-only is given; ARD ignores other top-level members.

Usage:
  python3 yaml2ard.py                         # bio-nih-mcp.yaml -> ard.json
  python3 yaml2ard.py in.yaml -o out.json
  python3 yaml2ard.py --strip-curation        # pure ARD terms only
  python3 yaml2ard.py --curation-as-metadata  # also copy scalar cat: terms into metadata.*
  python3 yaml2ard.py --role default optional --profile nih-niaid-research
  python3 yaml2ard.py --check                 # validate only, write nothing

Exit status: 0 = ok (warnings allowed), 1 = validation errors, 2 = usage/IO error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

ARD_BASE_CONTEXT = "https://agenticresourcediscovery.org/context/v1"

# Terms defined by the ARD default namespace (spec §4.2, base context, entry schema).
ARD_TERMS = {
    "@context", "@id", "identifier", "displayName", "type", "url", "data",
    "representativeQueries", "capabilities", "description", "tags", "version",
    "updatedAt", "metadata", "trustManifest",
}
# Order used when writing entries (readability only; JSON-LD is unordered).
ARD_ORDER = ["@context", "@id", "identifier", "displayName", "type", "url", "data",
             "description", "tags", "version", "updatedAt", "representativeQueries",
             "capabilities", "metadata", "trustManifest"]

# Entry-schema identifier pattern (spec/schemas/ard-entry.schema.json) ...
URN_SCHEMA_RE = re.compile(r"^urn:air:[a-zA-Z0-9.-]+(:[a-zA-Z0-9._-]+)+$")
# ... and the stricter form the official conformance-test CLI applies.
URN_CONFORMANCE_RE = re.compile(
    r"^urn:air:([a-zA-Z0-9.-]+)(?::([a-zA-Z0-9._:-]+))?:([a-zA-Z0-9._-]+)$")
FQDN_RE = re.compile(r"^(?=.{1,253}$)([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$")
# RFC 6838 restricted-name type/subtype, optional parameters (same idea as conformance-test).
RESTRICTED = r"[0-9A-Za-z][0-9A-Za-z!#$&^_.+\-]{0,126}"
MEDIA_TYPE_RE = re.compile(rf"^{RESTRICTED}/{RESTRICTED}(\s*;\s*[!#$%&'*+\-.^_`|~0-9A-Za-z]+=(\"[^\"]*\"|[!#$%&'*+\-.^_`|~0-9A-Za-z]+))*$")
STANDARD_TYPES = {
    "application/ai-catalog+json", "application/agent-card+json",
    "application/a2a-agent-card+json", "application/mcp-server-card+json",
    "application/agent-skills+json", "application/agent-skills+md",
    "application/agent-skills+zip", "application/agent-skills+gzip",
    'text/markdown; profile="urn:air:agent-skills"',
    "application/agent-plugins+zip", "application/agent-plugins+gzip",
    "application/ai-registry", "application/ai-registry+json",
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"[{where}] {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"[{where}] {msg}")


def json_default(o):
    if isinstance(o, (dt.date, dt.datetime)):
        return o.isoformat()
    raise TypeError(f"not JSON serialisable: {type(o).__name__}")


def normalise(value):
    """YAML may auto-type dates; ARD wants strings."""
    if isinstance(value, dt.datetime):
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: normalise(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalise(v) for v in value]
    return value


def prefixes_from_context(ctx) -> dict[str, str]:
    """Return {prefix: iri} declared in a JSON-LD @context (string/object/array)."""
    out: dict[str, str] = {}
    items = ctx if isinstance(ctx, list) else [ctx]
    for item in items:
        if isinstance(item, dict):
            for k, v in item.items():
                if isinstance(v, str) and not k.startswith("@"):
                    out[k] = v
    return out


def is_datetime(s: str) -> bool:
    if not isinstance(s, str) or "T" not in s:
        return False
    try:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return False
    return d.tzinfo is not None


def validate_entry(e: dict, where: str, prefixes: dict[str, str], rep: Report) -> None:
    # --- required (spec §4.2, Appendix D.1 ArdEntry) ---
    for term in ("identifier", "displayName", "type"):
        if not e.get(term):
            rep.error(where, f"missing required '{term}'")
    has_url, has_data = "url" in e, "data" in e
    if has_url == has_data:
        rep.error(where, "must carry exactly one of 'url' or 'data' (§4.3)")
    if has_url and not re.match(r"^https?://\S+$", str(e["url"])):
        rep.error(where, f"'url' is not an absolute http(s) URI: {e['url']!r}")
    if has_data and not isinstance(e["data"], dict):
        rep.error(where, "'data' must be an object")

    ident = e.get("identifier")
    if isinstance(ident, str):
        if not URN_SCHEMA_RE.match(ident):
            rep.error(where, f"identifier fails schema pattern: {ident}")
        m = URN_CONFORMANCE_RE.match(ident)
        if not m:
            rep.error(where, f"identifier fails conformance URN form urn:air:<publisher>[:<ns>]:<name>: {ident}")
        elif not FQDN_RE.match(m.group(1)):
            rep.error(where, f"URN publisher '{m.group(1)}' is not a fully qualified domain name (Appendix C)")
        if "@id" in e and e["@id"] != ident and not str(e["@id"]).startswith("http"):
            rep.warn(where, "@id differs from identifier; both MUST denote the same resource")

    mt = e.get("type")
    if isinstance(mt, str):
        if not MEDIA_TYPE_RE.match(mt):
            rep.error(where, f"'type' is not a syntactically valid media type: {mt}")
        elif mt not in STANDARD_TYPES:
            rep.warn(where, f"'type' {mt} is not one of the standard ARD discovery types (allowed, but flagged)")

    # --- discovery signals (SHOULD, warnings only, §4.2 / D.2) ---
    rq = e.get("representativeQueries")
    if rq is None:
        rep.warn(where, "no representativeQueries -- valid catalog entry, but not discoverable by ARD search")
    elif not isinstance(rq, list) or not all(isinstance(q, str) and q.strip() for q in rq):
        rep.error(where, "representativeQueries must be an array of non-empty strings")
    elif not 2 <= len(rq) <= 5:
        rep.warn(where, f"representativeQueries has {len(rq)} items; spec recommends 2-5")

    for term in ("capabilities", "tags"):
        if term in e and not (isinstance(e[term], list) and all(isinstance(x, str) for x in e[term])):
            rep.error(where, f"'{term}' must be an array of strings")
    for term in ("description", "version", "displayName"):
        if term in e and not isinstance(e[term], str):
            rep.error(where, f"'{term}' must be a string")
    if "updatedAt" in e and not is_datetime(e["updatedAt"]):
        rep.error(where, f"'updatedAt' must be an ISO 8601 date-time with zone: {e['updatedAt']!r}")
    if "metadata" in e:
        md = e["metadata"]
        if not isinstance(md, dict):
            rep.error(where, "'metadata' must be an object")
        else:
            for k, v in md.items():
                if not (v is None or isinstance(v, (str, int, float, bool))):
                    rep.error(where, f"metadata.{k} must be a scalar (string/number/boolean/null) per the entry schema")
    tm = e.get("trustManifest")
    if tm is not None:
        if not isinstance(tm, dict) or "identity" not in tm:
            rep.error(where, "trustManifest requires 'identity' (§4.5)")
        elif isinstance(ident, str) and (m := URN_CONFORMANCE_RE.match(ident)):
            if m.group(1) not in str(tm["identity"]):
                rep.warn(where, "trustManifest.identity does not appear to align with the URN publisher domain (§4.5.1)")

    # --- namespaced / unknown terms ---
    for k in e:
        if k in ARD_TERMS:
            continue
        if ":" in k:
            pfx = k.split(":", 1)[0]
            if pfx not in prefixes:
                rep.error(where, f"term '{k}' uses undeclared prefix '{pfx}:' (declare it in catalog @context)")
        else:
            rep.warn(where, f"unprefixed term '{k}' is not an ARD core term; it will resolve to the ARD default namespace (@vocab)")


def build(doc: dict, args, rep: Report) -> dict:
    catalog = doc.get("catalog") or {}
    ctx = catalog.get("@context") or [ARD_BASE_CONTEXT]
    if not isinstance(ctx, list):
        ctx = [ctx]
    if ARD_BASE_CONTEXT not in ctx:
        ctx = [ARD_BASE_CONTEXT] + ctx
    prefixes = prefixes_from_context(ctx)
    cur_pfx = args.prefix
    if not args.strip_curation and cur_pfx not in prefixes:
        rep.warn("catalog", f"curation prefix '{cur_pfx}:' not declared in @context")
    ns = prefixes.get(cur_pfx, "")
    if "example.org" in ns:
        rep.warn("catalog", f"curation namespace IRI is a placeholder ({ns}); replace before publishing")

    raw_entries = doc.get("entries")
    if not isinstance(raw_entries, list):
        rep.error("catalog", "YAML must contain an 'entries' list")
        return {"entries": []}

    out_entries, seen = [], set()
    for i, raw in enumerate(raw_entries):
        if not isinstance(raw, dict):
            rep.error(f"entry #{i}", "entry is not a mapping")
            continue
        e = normalise(raw)
        where = e.get("displayName") or e.get("identifier") or f"entry #{i}"
        role = e.get(f"{cur_pfx}:role")
        profiles = e.get(f"{cur_pfx}:profile") or []
        profiles = profiles if isinstance(profiles, list) else [profiles]
        if args.role and role not in args.role:
            continue
        if args.profile and not set(args.profile) & set(profiles):
            continue

        validate_entry(e, where, prefixes, rep)
        ident = e.get("identifier")
        if ident in seen:
            rep.error(where, f"duplicate identifier {ident}")
        seen.add(ident)

        entry = {k: e[k] for k in ARD_ORDER if k in e and k != "@context"}
        cur_terms = {k: v for k, v in e.items() if k not in ARD_TERMS}

        if args.curation_as_metadata:
            md = dict(entry.get("metadata") or {})
            for k, v in cur_terms.items():
                key = k.replace(":", ".", 1)
                if isinstance(v, list):
                    v = "; ".join(str(x) for x in v)
                if v is None or isinstance(v, (str, int, float, bool)):
                    md[key] = v
            if md:
                entry["metadata"] = md

        if args.strip_curation:
            entry_ctx = ARD_BASE_CONTEXT
        else:
            used = {k.split(":", 1)[0] for k in cur_terms if ":" in k}
            local = {p: prefixes[p] for p in sorted(used) if p in prefixes}
            entry_ctx = [ARD_BASE_CONTEXT, local] if local else ARD_BASE_CONTEXT
            entry.update(cur_terms)
        if not args.no_context:
            entry = {"@context": entry_ctx, **entry}
        out_entries.append(entry)

    manifest: dict = {"entries": out_entries}
    if not args.entries_only:
        manifest = {
            "catalog": {  # transport-defined; ignored by ARD consumers (§5.1)
                k: catalog[k] for k in ("id", "name", "description", "version", "license",
                                        "created", "modified", "maintainer", "ardSpec")
                if k in catalog
            } | {
                "generatedBy": "yaml2ard.py",
                "generatedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "entryCount": len(out_entries),
                "curationStripped": bool(args.strip_curation),
            },
            **manifest,
        }
    return normalise(manifest)


def schema_validate(manifest: dict, schema_path: str, rep: Report) -> str:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return "skipped (python 'jsonschema' not installed)"
    if not os.path.exists(schema_path):
        return f"skipped (schema not found at {schema_path})"
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    sub = dict(schema)
    sub["$ref"] = "#/$defs/ArdManifest"
    validator_cls = jsonschema.validators.validator_for(sub)
    v = validator_cls(sub, format_checker=validator_cls.FORMAT_CHECKER)
    n = 0
    for err in v.iter_errors(manifest):
        n += 1
        path = "/".join(str(p) for p in err.absolute_path)
        rep.error("json-schema", f"{path or '<root>'}: {err.message[:300]}")
    return "passed" if n == 0 else f"failed ({n} errors)"


def main(argv=None) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?", default=os.path.join(here, "bio-nih-mcp.yaml"))
    ap.add_argument("-o", "--output", default=os.path.join(here, "ard.json"),
                    help="output path ('-' for stdout)")
    ap.add_argument("--strip-curation", action="store_true",
                    help="emit only ARD core terms (drop cat: terms and their @context prefix)")
    ap.add_argument("--curation-as-metadata", action="store_true",
                    help="also copy scalar curation terms into metadata.* (lists joined with '; ')")
    ap.add_argument("--prefix", default="cat", help="curation namespace prefix (default: cat)")
    ap.add_argument("--role", nargs="+", help="only include entries whose <prefix>:role is one of these")
    ap.add_argument("--profile", nargs="+", help="only include entries tagged with one of these profiles")
    ap.add_argument("--entries-only", action="store_true", help="omit the transport-defined 'catalog' member")
    ap.add_argument("--no-context", action="store_true", help="omit per-entry @context (not recommended)")
    ap.add_argument("--schema", default=os.path.join(here, "vendor/ard-spec/spec/schemas/ard-entry.schema.json"),
                    help="ARD entry JSON Schema used for structural validation")
    ap.add_argument("--check", action="store_true", help="validate only; do not write output")
    ap.add_argument("-q", "--quiet", action="store_true", help="print errors only")
    args = ap.parse_args(argv)

    try:
        with open(args.input, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as exc:
        print(f"error: cannot read {args.input}: {exc}", file=sys.stderr)
        return 2

    rep = Report()
    manifest = build(doc, args, rep)
    schema_result = schema_validate(manifest, args.schema, rep)

    if not args.check:
        text = json.dumps(manifest, indent=2, ensure_ascii=False, default=json_default) + "\n"
        if args.output == "-":
            sys.stdout.write(text)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)

    out = sys.stderr if args.output == "-" else sys.stdout
    if not args.quiet:
        for w in rep.warnings:
            print(f"WARN  {w}", file=out)
    for e in rep.errors:
        print(f"ERROR {e}", file=out)
    print(f"{len(manifest['entries'])} entries | JSON Schema: {schema_result} | "
          f"{len(rep.errors)} errors, {len(rep.warnings)} warnings"
          + ("" if args.check or args.output == "-" else f" | wrote {args.output}"), file=out)
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
