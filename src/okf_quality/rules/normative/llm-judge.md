# P3 — LLM faithfulness judge (design)

## Purpose

Assess whether an OKF atomic claim **faithfully restates** the cited Blueprint span without upgrading “encouraged” to “required” or inventing content.

## Non-goals

- Sole CI gate  
- Replacing SHACL or line-existence checks  
- Full STE certification  

## Inputs

| Input | Source |
|-------|--------|
| Claim text | `AtomicConcept.text` / `schema:text` |
| Line span | `okf:sourceLines` |
| Blueprint excerpt | Lines from `docs/BluePrint/…md` |
| Parent normative flag | `okf:normative` |

## Rubric (draft)

| Score | Meaning |
|-------|---------|
| 1.0 | Faithful paraphrase; modality preserved |
| 0.7 | Mostly faithful; minor omission |
| 0.4 | Material drift or modality change |
| 0.0 | Unsupported or contradictory |

Return JSON: `{ "atomic": n, "score": 0-1, "rationale": "…", "modality_ok": bool }`.

## Guardrails

- Judges **report**; humans or hard checks **gate**.  
- Prompt + model version recorded in report (OKF `generated`-like metadata).  
- Do not allow the agent under test to edit this rubric file in the same run.
