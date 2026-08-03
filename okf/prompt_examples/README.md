# Prompt examples (filled placeholders)

Filled, ready-to-run copies of the templated prompts from the
[NIAID Blueprint Prompt Library OKF bundle](../../src/promptLibrary/okf-bundle/).

Each source prompt uses `{{placeholders}}`. Here those placeholders are
replaced with **logical, domain-grounded values** drawn from NIAID-supported
infectious and immune-mediated disease resources (and Blueprint worked
examples where available).

## Source templates

| Example file | Source template | Placeholders filled |
|---|---|---|
| [`metadata-schema/core-elements/identifier.md`](metadata-schema/core-elements/identifier.md) | `okf-bundle/.../identifier.md` | `type`, `existing_ids`, `repository` |
| [`metadata-schema/core-elements/name-description.md`](metadata-schema/core-elements/name-description.md) | `.../name-description.md` | `digital_object_info` |
| [`metadata-schema/attribution-provenance/author.md`](metadata-schema/attribution-provenance/author.md) | `.../author.md` | `creators_list` |
| [`metadata-schema/attribution-provenance/funder-grant.md`](metadata-schema/attribution-provenance/funder-grant.md) | `.../funder-grant.md` | `project_title`, `funders`, `grant_numbers` |
| [`metadata-schema/domain-specific/health-condition.md`](metadata-schema/domain-specific/health-condition.md) | `.../health-condition.md` | `conditions` |
| [`metadata-schema/domain-specific/infectious-agent-host.md`](metadata-schema/domain-specific/infectious-agent-host.md) | `.../infectious-agent-host.md` | `study_description` |
| [`persistent-identifiers/pid-strategy.md`](persistent-identifiers/pid-strategy.md) | `.../pid-strategy.md` | `repository_type`, `object_types`, `current_practice` |
| [`apis-metadata-exposure/api-requirements.md`](apis-metadata-exposure/api-requirements.md) | `.../api-requirements.md` | `repo_name`, `tech_stack` |
| [`citation-outreach/citation-guidance.md`](citation-outreach/citation-guidance.md) | `.../citation-guidance.md` | `object_details` |
| [`citation-outreach/outreach-training.md`](citation-outreach/outreach-training.md) | `.../outreach-training.md` | `repo_name`, `team_info` |

## Domain sources used for fill-ins

| Domain | URL | Used in |
|---|---|---|
| AccessClinicalData@NIAID (ACDN) | https://accessclinicaldata.niaid.nih.gov/ | name/description, funder-grant, infectious agent/host, citation |
| BV-BRC | https://www.bv-brc.org/ | PID strategy, API design |
| CEIRR Network | https://www.ceirr-network.org/ | infectious agent/host (influenza) |
| ClinEpiDB | https://clinepidb.org/ | health conditions (epidemiology) |
| IEDB | https://www.iedb.org/ | PID strategy, outreach |
| ImmPort | https://www.immport.org/ | identifier, author, funder-grant, citation (SDY998 / SDY2968) |
| ITN TrialShare | https://www.itntrialshare.org/ | health conditions (immune tolerance / autoimmunity) |
| MWCCS | https://statepi.jhsph.edu/mwccs/ | health conditions (HIV) |
| TB Portals | https://tbportals.niaid.nih.gov/ | name/description, infectious agent/host, API |
| VEuPathDB | https://veupathdb.org/ | PID strategy, outreach |
| ImmuneSpace / HIPC | https://immunespace.org/ | outreach-training, PID / object types |

Blueprint worked examples (Supplementary Tables 3–4, ImmPort SDY998, ACDN ACTT-4)
are used when the Blueprint already publishes concrete DOIs, ORCIDs, RORs, and
grant numbers.

## How to use

Copy any file’s body under `# Prompt` into an LLM session. Placeholders are
already substituted; you can still edit the filled values for another study or
repository.

To regenerate `data.json` for the interactive prompt library, edit the source
templates in `src/promptLibrary/okf-bundle/` — not these examples.
