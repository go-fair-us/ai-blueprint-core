# Evaluation

 There are several open-source tools that can be used to address SI readiness scoring, documentation linting, and automated evaluation.
 
---

### 1. `afdocs` (Agent-Friendly Documentation Spec)

* **What it does:** This is the underlying open-source standard and CLI tool directly built to test whether AI coding agents can discover, parse, and consume your documentation.
* **Key Features:**
* Checks for `llms.txt` presence and structure.
* Evaluates page size and LLM token truncation risks.
* Audits Markdown availability for AI crawlers.
* Runs directly in CI/CD via Node or Vitest.


* **Quick Start:**
```bash
npx afdocs check https://docs.your-site.com --format scorecard

```

---

### 2. Open-Source AI/LLM Evaluation Frameworks (For RAG & Docs Quality)

If you want to measure whether an LLM/agent can successfully answer user queries using your documentation (the core problem Agent Score tests for), you can run automated evaluation pipelines over your docs using these frameworks:

* **[DeepEval](https://github.com/confident-ai/deepeval):** An open-source LLM evaluation framework. You can pass your documentation pages as context into a RAG pipeline and measure metrics like *Context Relevancy*, *Faithfulness*, *Hallucination Rate*, and *Task Completion*.
* **[Ragas](https://github.com/explodinggradients/ragas):** Designed specifically for testing Retrieval-Augmented Generation (RAG) applications over documentation. It automatically generates test datasets from your Markdown files and measures whether agents can successfully retrieve and synthesize accurate answers from them.
* **[Evidently AI](https://github.com/evidentlyai/evidently):** An open-source observability framework that includes LLM-as-a-judge evaluators to continuously score documentation extraction quality and answer drift.

---

### 3. Open-Source Doc Accuracy & Linting Tools

To complement AI legibility checks, these open-source CLI tools ensure your docs don't contain stale code snippets or broken references (which trip up AI agents):

* **[Doc Detective](https://github.com/doc-detective/doc-detective):** An open-source documentation testing framework that executes code snippets, commands, and API calls directly from your Markdown files to guarantee that what the AI reads actually runs.
* **[Vale](https://github.com/errata-ai/vale):** A syntax-aware, open-source linter for technical documentation that enforces style guide consistency, structure, and readability across Markdown files before AI models index them.

