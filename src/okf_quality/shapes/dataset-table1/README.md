# SHACL shapes — schema:Dataset / Blueprint Table 1

**Priority:** P0 (core required) → P1 (Table 1 expansion)  
**Data graph:** JSON-LD / Turtle instance metadata for deposits  
**Related skill:** `skills/niaid-bp-validation/`

## Files

| File | Role |
|------|------|
| `required-core.ttl` | name, description, url (aligned with skill starter) |
| `table1-recommended.ttl` | Soft warnings for key Table 1 fields |

## Source of truth

Until automated sync exists:

1. **Interactive / skill path:** `skills/niaid-bp-validation/assets/blueprint-required.ttl`
2. **Batch / CI path:** shapes in this directory

Keep them intentionally similar; document drift in PRs.

## Blueprint reference

`docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md` — Table 1 metadata elements (identifier, name, description, author/ORCID, funder/ROR, license, conditionsOfAccess, infectiousAgent, …).

## Run

```bash
uv run python skills/niaid-bp-validation/scripts/validate.py DATA.jsonld \
  --shape src/okf_quality/shapes/dataset-table1/required-core.ttl
```
