# Evaluation

Different checks answer different questions. Is the documentation technically easy for an agent to discover and read? Can an agent answer the questions repository users care about? Are the documentation examples and prose accurate? No single score covers all three.

## Check agent access and readability

[AFDocs](https://afdocs.dev/) is an open-source CLI that tests documentation sites against the [Agent-Friendly Documentation Spec](https://agentdocsspec.com/). It checks practical access and presentation issues, such as whether an `llms.txt` file is discoverable, Markdown is available, pages are too large, and links or redirects work. It does not establish that the documentation is factually correct or that an agent can answer a particular domain question.

The [AFDocs repository](https://github.com/agent-ecosystem/afdocs) has installation and CI integration details; consult the current [CLI reference](https://www.afdocs.dev/reference/cli) for supported options. For example:

```bash
npx afdocs check https://docs.your-site.com --format scorecard
```

AFDocs is in early development, so check the current documentation for supported flags and output formats before relying on them in automation. An [Agent Score](https://afdocs.dev/what-is-agent-score) or similar readiness score is a useful diagnostic, not a measure of answer accuracy.

## Test whether agents can answer your questions

For retrieval-augmented generation (RAG) or other documentation-grounded applications, evaluation frameworks can help test retrieval and answer quality. They need a test set, expected answers or judging criteria, and the system being evaluated; results depend on that setup and are not a score of the documents alone.

- [DeepEval](https://github.com/confident-ai/deepeval) provides LLM evaluation methods, including checks for groundedness, relevance, and task completion.
- [Ragas](https://github.com/explodinggradients/ragas) provides metrics and test-set generation for RAG systems.
- [Evidently](https://github.com/evidentlyai/evidently) supports evaluation and monitoring of AI/LLM applications, including LLM-as-a-judge workflows.

For a small, repository-specific test, write questions people should be able to answer from the public site, then try them with the same agent and record whether each answer is supported by fetched evidence. The webinar's [competency-question prompts](evaluationPrompts.md#competency-questions) and [answerability prompt](../../../prompts/evals/competency-answerability.md) provide a starting point.

## Check documentation accuracy and style

These tools complement agent-readability and answerability checks by testing examples or enforcing editorial conventions:

- [Doc Detective](https://github.com/doc-detective/doc-detective) tests documentation by executing supported code snippets, commands, and API calls.
- [Vale](https://github.com/errata-ai/vale) is a configurable prose linter for enforcing a style guide and catching common writing issues.

Use the checks that fit your site: a syntax or style pass cannot verify every technical claim, and a passing agent-readiness check cannot replace human review of content.

