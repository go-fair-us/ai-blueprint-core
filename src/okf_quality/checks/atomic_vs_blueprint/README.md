# Atomic ↔ Blueprint alignment (P1)

## Levels

| Level | Script / design | What it checks |
|-------|-----------------|----------------|
| L1 line existence | `scripts/check_atomic_lines.py` | `source_lines` within Blueprint file |
| L2 token overlap | *future* | claim tokens ⊆ line window |
| L3 LLM judge | `rules/normative/llm-judge.md` | faithfulness + modality |

## Blueprint path (default)

`docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`
