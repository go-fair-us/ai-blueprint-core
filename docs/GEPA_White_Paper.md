# Reflective Prompt Optimization with GEPA

*A More Efficient Path to Improving AI System Performance*

**White Paper | July 2026**

---

## Executive Summary

Teams that want better AI results on a specific task have some common options. They can craft prompts by hand. They can also use reinforcement learning (RL) that updates the model itself or fine-tuning of a model. 

**GEPA** is a middle path. It improves the natural language instructions (prompts) that guide AI models. It often beats RL methods and uses much less computation.

Research from 2025, accepted at ICLR 2026, shows that GEPA can beat leading RL techniques by clear margins. It needs up to **35 times fewer model evaluations** during the improvement process. That makes systematic optimization practical for more teams and more use cases.

GEPA helps organizations make AI applications more reliable and capable. They do not need the cost and complexity of retraining or fine-tuning large models.

## The Challenge: Getting AI Results That Stay Strong

Most AI applications today use large language models guided by natural language instructions. These instructions are **prompts**. Prompt quality has a large effect on output quality, reliability, and usefulness.

Writing effective prompts is still hard. It needs deep task knowledge, repeated tests, and often much trial and error.

When hand-crafted prompts are not enough, teams often use one of two alternatives:

- **Reinforcement Learning (RL) methods**: These techniques update the model internal parameters from feedback on many examples. RL is strong, but it often needs thousands of model evaluations ("rollouts") and large compute budgets.

- **Earlier automated prompt optimizers**: These tools search for better instructions or example sets. They help, but they still use a lot of compute and often give only small gains.

The result is a gap. Many teams need better performance but cannot pay for full RL training. GEPA aims to fill that gap.

## What is GEPA?

**GEPA** means Genetic-Pareto. It is a method that improves the text instructions that control AI systems. It does not change the model weights. GEPA evolves better prompts by using the model ability to reason about its own performance in natural language.

The main idea is simple. When an AI system fails or gives a weak result, a strong language model can review the full trajectory. A trajectory records the reasoning steps, actions, and tool use. The model can then suggest clearer and more effective instructions. GEPA turns this process into a system and adds an evolutionary step that builds on what works.

### How GEPA Works (at a High Level)

The process has these main steps:

1. **Run the current prompts** on a set of example tasks. Record what happened, including the model reasoning, any tool use, and the final output.

2. **Reflect in natural language**. A strong model reviews the trajectories, with focus on failures. Example insight: the instructions were ambiguous about edge cases. Another insight: tell the model to verify its arithmetic before it concludes.

3. **Propose improved prompts** from those reflections.

4. **Keep a set of strong candidates**. GEPA tracks the best prompt versions found so far. That set holds different good trade-offs in performance. This is a **Pareto front**: options where a gain on one measure would cost performance on another.

5. **Combine and evolve**. Good ideas from different strong prompts can merge into better versions. The process repeats within a set budget of evaluations.

Reflection, evolutionary search, and candidate management let GEPA learn a lot from relatively few examples.

## Key Evidence

The main research for GEPA is the paper *"GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning"* by Lakshya A. Agrawal and colleagues (arXiv:2507.19457, accepted as an Oral presentation at ICLR 2026).

### Main Research Findings

Across six different tasks, GEPA showed:

- **Better performance than RL**: GEPA beat a strong RL baseline (GRPO) by an average of **6 percentage points**. Gains reached **20 points** on some tasks.

- **Much better efficiency**: These gains used up to **35 times fewer model evaluations (rollouts)** than the RL approach.

- **Better than prior prompt optimization**: GEPA also beat the prior leading automated prompt method (MIPROv2) by more than **10 percentage points** on average. That includes a **+12 point gain** on the hard AIME 2025 mathematics benchmark.

### Concrete Example

In one documented case on AIME 2025 mathematics problems, GEPA improved a smaller, lower-cost model (GPT-4.1 Mini). Baseline accuracy moved from **46.6% to 56.6%**. That is a 10 percentage point absolute gain. In some runs, performance reached 60%. Careful prompt optimization can help smaller models reach levels that once needed larger and more expensive models.

## Why This Matters

GEPA results point to several practical benefits for teams that build and maintain AI systems:

- **Lower optimization cost**. The 35× cut in required rollouts versus RL methods lowers API and compute cost during the improvement phase.

- **Accessibility**. Organizations that lack infrastructure or budget for large-scale RL can still run systematic, automated prompt improvement.

- **Interpretability**. GEPA works with readable text prompts, not opaque weight updates. People can inspect, understand, and refine the optimized instructions.

- **Model efficiency**. Better prompts often let smaller or cheaper models match levels that once needed larger models. That can cut ongoing inference cost.

- **Works with other techniques**. Teams can use GEPA with few-shot examples, structured output formats, and other DSPy capabilities.

## How to Use GEPA in Practice

GEPA is part of the **DSPy** framework. DSPy builds AI programs as modular components that you can optimize. A typical GEPA run has these steps:

1. Define the AI task as a DSPy program with clear input and output signatures.
2. Create a metric that scores outputs. Prefer a metric that also gives text feedback on why a result was good or bad.
3. Give a modest set of training and validation examples.
4. Run the GEPA optimizer. It handles reflection, candidate management, and evolution within your evaluation budget.

Users control the optimization budget (light, medium, or heavy presets, or custom limits). They can also use a stronger model only for the reflection step while they keep the main task model efficient.

## Limitations and Considerations

GEPA is not a universal solution. Its value depends on a sound evaluation metric and a sufficient (often modest) set of examples. Reflection quality is better when a capable model does that step. Results vary by domain. Teams should validate optimized prompts on held-out test data. Some other prompt optimization methods also show strong results with even fewer evaluations on some benchmarks.

Treat GEPA as a well-documented tool in a larger toolkit for more reliable AI systems. It is most useful when full RL cost is too high.

## Conclusion

GEPA is a clear step forward in how teams can improve AI applications in a systematic way. It focuses optimization on the natural language layer, not on model weights. It uses rich reflective feedback, not only scalar rewards. It gains strong performance with much lower compute cost than reinforcement learning.

For teams that want reliable, automated prompt improvement without full model retraining, GEPA is a practical and evidence-backed path. Its place in the DSPy ecosystem makes it usable in real development workflows.

As AI systems move deeper into critical processes, efficient and interpretable optimization will matter more. Reflective prompt evolution is a technique worth study and evaluation for many use cases.

## References and Further Reading

- **Agrawal, L. A., et al.** (2025). *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning*. arXiv:2507.19457. Accepted to ICLR 2026 (Oral).

- **DSPy Documentation**: [https://dspy.ai/](https://dspy.ai/). Includes tutorials and API reference for using GEPA within DSPy programs.

- **GEPA Implementation**: [https://github.com/gepa-ai/gepa](https://github.com/gepa-ai/gepa)

More practical examples and case studies are available in the DSPy tutorials and community resources.

---

*This white paper summarizes public research and documentation as of July 2026. Results may vary by task, data, and implementation. Always validate optimizations on representative test sets for your specific use case.*

---

Example results:
The starting prompt at [impact.md](../okf/bundles/niaid_blueprint/citation/impact.md) became [citation-outreach-citation-guidance-optimized-prompt.md](../src/libraryOptimizer/runs/okf-batch/citation-outreach-citation-guidance/citation-outreach-citation-guidance-optimized-prompt.md)

---

# SDY998 citation example

ImmPort study SDY998, grounded in the NIAID Blueprint for Digital Objects (v2, 26 September 2025). The input for this example was the study landing-page URL. Title, description source, ORCIDs, funders, license, and DOI come from the Blueprint’s own SDY998 tables. Those entries give no version number, so this citation omits a version element.

## Where the values come from

- **Section 1.2, “Blueprint Requirements”** (Table 1) — minimal metadata schema: name, description, identifier, author, funder, grant, license, conditionsOfAccess, and the other Table 1 elements.
- **Section 2.2, “Blueprint Requirements”** (Table 2) — PID usage: DOI for identifier, ORCID for author, ROR for funder.
- **Section 3.2, “Blueprint Requirements”** — minimal API specification: JSON-LD encoding, resource-oriented IRIs, GET, OpenAPI documentation.
- **Section 4.2, “Blueprint Requirements”** — citation guidance. Reused-data citations include the object PID (for example a DOI) and, when one exists, a repository-specific ID such as an accession. That is why SDY998 appears alongside the DOI.
- **Table 3** — APA-style dataset citation template.
- **Supplementary Table 4** and **Supplementary Table 7** — ImmPort study SDY998 itself: dateCreated, author ORCIDs, funder RORs, grant number, license URL, measurementTechnique, and healthCondition.

Table 1’s sample description for this study is the study-file text about PERIOD and STUDY_GLOSSARY. The JSON-LD below follows the Supplemental Table 7 shape and does not copy that study-file sentence into `description`.

## Human-readable citation

Table 3’s APA-style dataset pattern is `Author(s). (Year). Title of dataset (Version) [Data set]. Repository. DOI`. ImmPort’s own policy is to cite the ImmPort Shared Data website, the study accession, and the study title, using the DOI when one is available.

> **Investigators registered to ImmPort Study SDY998** [ORCID: 0000-0002-1450-1549; 0000-0002-1219-3845; 0000-0003-4483-0359; 0000-0002-5634-7746]. (2017). *SDY998: AMP Rheumatoid Arthritis Phase 1* [Data set]. ImmPort Shared Data. Study Accession: SDY998. https://doi.org/10.21430/M3KXJHSP4T

Notes on construction:

- **Year (2017)** comes from `dateCreated` in Supplementary Table 4 (2017-11-07), the Blueprint’s default date field for datasets.
- **Author identifiers** are only ORCIDs in the source metadata. No names were supplied, so the citation uses resolvable ORCID PIDs. Resolving those ORCIDs to display names, through the ORCID API and ImmPort’s contributor records, can replace the bracketed list with `Lastname, F. et al.`
- **DOI** is last, per Table 3. Section 2 asks for the resolvable form (`https://doi.org/...`), not the bare `10.21430/...` string.
- **Study accession (SDY998)** is included because reused-data citations carry the repository-specific ID alongside the object PID.

Funder and grant (NIAID, ROR: https://ror.org/043z4tv69; NIAMS, ROR: https://ror.org/006zn3t30; grant 1UH2AR067676-01) are discovery and attribution metadata. Table 1 treats `funder` and `grant` as separate elements from `citation`. An acknowledgment line, when a venue wants one, can read: *Data were generated with support from NIAID and NIAMS (grant 1UH2AR067676-01) as part of the Accelerating Medicines Partnership RA/SLE program.*

When the publication also draws on the associated methods paper, Supplemental Table 7 records that paper on the `citation` element, separate from the dataset DOI:

> Methods for high-dimensional analysis of cell populations in rheumatoid arthritis (2018). https://doi.org/10.1186/s13075-018-1631-y (PMID: 29996944)

## Machine-actionable citation (JSON-LD)

This follows the structure Supplemental Table 7 uses for this study.

```json
{
  "@context": "https://schema.org/",
  "@id": "https://doi.org/10.21430/M3KXJHSP4T",
  "@type": "Dataset",
  "identifier": {
    "@id": "https://doi.org/10.21430/M3KXJHSP4T",
    "@type": "PropertyValue",
    "propertyID": "https://registry.identifiers.org/registry/doi",
    "value": "doi:10.21430/M3KXJHSP4T",
    "url": "https://doi.org/10.21430/M3KXJHSP4T"
  },
  "name": "SDY998: AMP Rheumatoid Arthritis Phase 1",
  "url": "https://www.immport.org/shared/study/SDY998",
  "dateCreated": "2017-11-07",
  "author": [
    { "@type": "Person", "identifier": "https://orcid.org/0000-0002-1450-1549" },
    { "@type": "Person", "identifier": "https://orcid.org/0000-0002-1219-3845" },
    { "@type": "Person", "identifier": "https://orcid.org/0000-0003-4483-0359" },
    { "@type": "Person", "identifier": "https://orcid.org/0000-0002-5634-7746" }
  ],
  "funder": [
    { "@type": "Organization", "identifier": "https://ror.org/043z4tv69", "name": "NIAID" },
    { "@type": "Organization", "identifier": "https://ror.org/006zn3t30", "name": "NIAMS" }
  ],
  "grant": "1UH2AR067676-01",
  "citation": [
    {
      "@type": "ScholarlyArticle",
      "name": "Methods for high-dimensional analysis of cell populations in rheumatoid arthritis",
      "url": "https://pubmed.ncbi.nlm.nih.gov/29996944",
      "identifier": {
        "@id": "https://doi.org/10.1186/s13075-018-1631-y",
        "@type": "PropertyValue",
        "propertyID": "https://registry.identifiers.org/registry/doi",
        "value": "doi:10.1186/s13075-018-1631-y",
        "url": "https://doi.org/10.1186/s13075-018-1631-y"
      }
    }
  ],
  "conditionsOfAccess": "https://www.immport.org/agreement",
  "license": "https://www.immport.org/agreement"
}
```

## Why this shape

1. **Resolvable DOI as the primary identifier.** Section 2 asks for `https://doi.org/10.21430/M3KXJHSP4T` rather than the bare DOI string, because an unresolved DOI is a weaker persistent identifier.
2. **Accession and DOI together.** Section 4.2 distinguishes original-data citation from reused-data citation. For reused data it asks for the object PID and, when one applies, a repository-specific ID. SDY998 is that ID. The DOI still resolves the object on its own.
3. **ORCID PIDs for authorship.** Table 2 designates ORCID as the default PID for `author`. That holds when display names are not yet in the source metadata.
4. **The repository’s own citation policy.** Section 4.2 tells repository owners to give clear, consistent instructions for citing data. ImmPort’s guidance (repository, accession, title, DOI) is what this string follows. The Blueprint standardizes how that guidance is rendered: PID first, and ready for a machine-readable record.
5. **JSON-LD for harvest.** The block mirrors Supplemental Table 7 for this study. Section 3 asks that metadata, including `identifier`, `author`, `funder`, and `citation`, be exposable as schema.org JSON-LD so catalogs and the NIAID Data Ecosystem Discovery Portal can harvest it.

A second draft of this same study used a looser record: `version` set to `null`, authors named “Study Investigator”, `funding` in place of `funder` and `grant`, `license` as a `CreativeWork`, and `citation` set to the dataset’s own DOI. Those fields are left out of the block above. The accession can also be a second `identifier` `PropertyValue` (`propertyID` `Accession`, value `SDY998`) beside the DOI. This example keeps the accession in the human citation and keeps a single DOI `identifier`, matching Supplemental Table 7.

## What the repository would publish

Supplemental Table 7 names ImmPort’s existing call for this study: `https://immport.org/data/query/api/study/SDY998?format=json`. Section 3.2 asks that pattern to be a resource-oriented IRI returning JSON-LD, documented in OpenAPI or Swagger. The Blueprint’s own illustration of that IRI shape is `https://data.<domain.org>/<entity>/<instanceID>?format=json-ld`.

- Populate the Table 1 fields for each study record: type, identifier, name, description, dateCreated, author, funder, grant, license, and conditionsOfAccess.
- Validate the JSON-LD against the Blueprint’s schema.org structure before publishing.
- Put the human-readable citation string on the SDY998 landing page.
- Register that study endpoint in the repository’s OpenAPI or Swagger document.

Training that matches Section 4.2:

- A one-page citation guide showing the Table 3 pattern.
- A short tutorial on copying the human-readable citation and retrieving the JSON-LD from the study endpoint.
- A session for investigators on citing ImmPort datasets, accession and DOI together, including the difference between original-data citation and reused-data citation.

Together the human citation and the JSON-LD cover scholarly credit (ORCID-linked authorship), funder tracking (ROR-linked grant), and machine-readable discovery (resolvable DOI, schema.org JSON-LD).

## Controlled-access aside

The same Table 3 pattern applies to a controlled-access object. For the ACTT-4 package under AccessClinicalData@NIAID, `conditionsOfAccess` and `license` would point at a data-access request or DUA rather than an open user agreement. Supplementary Table 3 gives that repository a Controlled-Data designation. A citation of that object should say that a DAR is required before the data, as distinct from its metadata, can be obtained.
