# ai-blueprint-core

AI agent tools help NIAID-funded data repositories apply the [NIAID Blueprint for Digital Objects](https://datascience.niaid.nih.gov/resources).

The Blueprint is a FAIR data program from NIAID/ODSET. It defines minimal metadata schemas, persistent identifiers (PIDs), API standards, and citation practices for research data repositories.

This project supplies LLM-driven agents, guided by structured prompt personas. The agents help repository owners and staff assess and apply Blueprint requirements in five areas:

1. **Metadata schema**: schema.org-based metadata elements for digital objects
2. **Persistent identifiers**: DOIs, ORCIDs, RORs, RRIDs, and ontology terms
3. **APIs and machine access**: JSON-LD endpoints, OpenAPI documentation, structured data
4. **Citation guidance**: PID-based citation examples in standard formats
5. **Outreach and training**: Contact Points, training materials, Portal onboarding

## Flipped Interaction Pattern

This is not an agent. It is a pattern that reverses normal chat mode. The language model starts from a prompt and waits for user input to continue the conversation.

An example lives in the `prompts` directory. That example is long and verbose. A shorter, clearer version would help.

| Prompt | Purpose |
|--------|---------|
| `fairAssessmentInterview.md` | Runs a structured 6-phase interview to assess a repository Blueprint alignment and produces a gap report with ranked recommendations |

Paste the document into your prompt. Modern models start the interview and end with a summary of the responses. The exchange can get long. If you want to stop, tell the model: "stop the interview and give me the summary now".

## Usage

This repository has no executable code that you must run. The tooling converts PDF to Markdown. The converted results already live in the `docs` directory.

## Requirements

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) for environment and dependency management

## Setup

```bash
# Clone and install
git clone <repo-url>
cd ai-blueprint-core
uv sync
```

## Reference

The authoritative Blueprint specification is in `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`. The tools `docling` and `marker-pdf` converted that file from the PDF.

To pass this to a model, use the GitHub raw link: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md

## Dependencies

- [`docling`](https://github.com/docling-project/docling): structured document parsing and extraction
- [`marker-pdf`](https://github.com/VikParuchuri/marker): PDF-to-Markdown conversion

Both are ML-based libraries. Expect a large `.venv` and model downloads on the first run.
