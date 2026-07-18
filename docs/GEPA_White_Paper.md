# Reflective Prompt Optimization with GEPA

*A More Efficient Path to Improving AI System Performance*

**White Paper | July 2026**

---

## Executive Summary

Improving how AI systems perform on specific tasks has traditionally required either careful manual prompt engineering or expensive reinforcement learning (RL) processes that update the model itself. A newer approach called **GEPA** offers a compelling middle path: it automatically improves the natural language instructions (prompts) that guide AI models, often achieving better results than RL methods while using dramatically less computation.

Research published in 2025 and accepted to ICLR 2026 demonstrates that GEPA can outperform leading RL techniques by meaningful margins while requiring up to **35 times fewer model evaluations** during the improvement process. This makes systematic optimization practical for more teams and use cases.

GEPA is particularly valuable for organizations that want to make their AI applications more reliable and capable without the cost and complexity of retraining or fine-tuning large models.

## The Challenge: Getting AI to Perform Consistently Well

Most AI applications today rely on large language models guided by natural language instructions — commonly called **prompts**. The quality of these prompts has an enormous impact on output quality, reliability, and usefulness. However, writing effective prompts remains more art than science. It requires deep task understanding, iterative testing, and often significant trial and error.

When manual prompt crafting is insufficient, teams have historically turned to two main alternatives:

- **Reinforcement Learning (RL) methods**: These techniques update the model's internal parameters based on feedback from many examples. While powerful, RL approaches typically require thousands of model evaluations ("rollouts") and substantial computational resources.
- **Earlier automated prompt optimizers**: Tools that search for better instructions or example sets. These have been helpful but often still demand considerable compute and deliver incremental rather than transformative gains.

The result is a gap: many teams need better performance but cannot justify the cost or complexity of full RL training. This is the gap GEPA aims to fill.

## What is GEPA?

**GEPA** stands for Genetic-Pareto. It is a method for automatically improving the textual instructions that control AI systems. Rather than changing the model weights, GEPA evolves better prompts by leveraging the model's own ability to reason about its performance in natural language.

The core insight is simple but powerful: when an AI system makes a mistake or produces a suboptimal result, a strong language model can often analyze the full sequence of reasoning and actions (called a "trajectory") and suggest clearer, more effective instructions. GEPA systematizes this process and adds an evolutionary component to build on what works.

### How GEPA Works (at a High Level)

The process follows these main steps:

1. **Execute the current prompts** on a set of example tasks and record what happened — including the model's reasoning, any tool use, and the final output.

2. **Reflect in natural language** — A strong model reviews the trajectories, especially the failures, and generates insights such as: *"The instructions were ambiguous about edge cases"* or *"The model needs to be told to verify its arithmetic before concluding."*

3. **Propose improved prompts** based on the reflections.

4. **Maintain a collection of strong candidates** — GEPA keeps track of the most promising prompt versions discovered so far. This collection represents different good trade-offs in performance (sometimes called a **Pareto front** — the set of options where improving one aspect would require sacrificing performance in another).

5. **Combine and evolve** — Good ideas from different strong prompts can be merged to create even better versions. The process repeats within a defined budget of evaluations.

This combination of reflection, evolutionary search, and candidate management allows GEPA to extract a lot of learning from relatively few examples.

## Key Evidence of Effectiveness

The primary research backing GEPA is the paper *"GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning"* by Lakshya A. Agrawal and colleagues (arXiv:2507.19457, accepted as an Oral presentation at ICLR 2026).

### Main Research Findings

Across six diverse tasks, GEPA demonstrated:

- **Superior performance to RL**: GEPA outperformed a strong reinforcement learning baseline (GRPO) by an average of **6 percentage points**, with gains reaching as high as **20 points** on individual tasks.
- **Dramatically better efficiency**: These gains were achieved using up to **35 times fewer model evaluations (rollouts)** than the RL approach.
- **Better than prior prompt optimization**: GEPA also surpassed the previous leading automated prompt optimization method (MIPROv2) by more than **10 percentage points** on average, including a **+12 point gain** on the challenging AIME 2025 mathematics benchmark.

### Concrete Example

In one documented case using the AIME 2025 mathematics competition problems, GEPA improved a smaller, cost-effective model (GPT-4.1 Mini) from a baseline accuracy of **46.6% to 56.6%** — a 10 percentage point absolute improvement. In some runs, performance reached 60%. This demonstrates that thoughtful prompt optimization can allow smaller models to deliver performance previously associated with larger, more expensive ones.

## Why This Matters

GEPA's results suggest several practical advantages for teams building and maintaining AI systems:

- **Lower optimization cost** — The 35× reduction in required rollouts compared to RL methods translates directly into lower API or compute costs during the improvement phase.
- **Accessibility** — Organizations that lack the infrastructure or budget for large-scale RL can still achieve systematic, automated prompt improvement.
- **Interpretability** — Because GEPA works with readable text prompts rather than opaque weight updates, humans can inspect, understand, and further refine the optimized instructions.
- **Model efficiency** — Improved prompts often allow smaller or less expensive models to achieve performance levels that previously required larger models, reducing ongoing inference costs.
- **Complementary to other techniques** — GEPA can be used alongside few-shot examples, structured output formats, and other DSPy capabilities.

## How to Use GEPA in Practice

GEPA is integrated into the **DSPy** framework, which provides a structured way to build AI programs as modular, optimizable components. Using GEPA typically involves:

- Defining your AI task as a DSPy program with clear input/output signatures.
- Creating a metric that scores outputs (ideally one that can also provide textual feedback on why a result was good or bad).
- Specifying a modest set of training and validation examples.
- Running the GEPA optimizer, which handles the reflection, candidate management, and evolution automatically within your chosen evaluation budget.

The framework gives users control over the optimization budget (light, medium, or heavy presets, or custom limits) and allows use of a stronger model specifically for the reflection step while keeping the main task model efficient.

## Limitations and Considerations

Like any optimization technique, GEPA is not a universal solution. Its effectiveness depends on having a reasonable evaluation metric and a sufficient (though often modest) number of examples. The quality of reflections benefits from using a capable model for that step. Results can vary across domains, and teams should validate optimized prompts on held-out test data. Some alternative prompt optimization methods have also shown strong results with even lower evaluation counts on certain benchmarks.

GEPA is best viewed as a powerful, well-documented tool in the growing toolkit for making AI systems more reliable and capable — particularly valuable when the cost of traditional RL is prohibitive.

## Conclusion

GEPA represents a meaningful advance in how we can systematically improve AI applications. By focusing optimization effort on the natural language layer rather than model weights, and by using rich reflective feedback instead of scalar rewards alone, it achieves strong performance gains with substantially lower computational cost than reinforcement learning approaches.

For teams seeking to move beyond ad-hoc prompt engineering toward more reliable, automated improvement — without the overhead of full model retraining — GEPA offers a practical and evidence-backed path forward. Its integration into the DSPy ecosystem makes it accessible for real-world development workflows.

As AI systems become more deeply embedded in critical processes, the ability to efficiently and interpretably optimize their behavior will only grow in importance. Reflective prompt evolution is a technique worth understanding and evaluating for many use cases.

## References & Further Reading

- **Agrawal, L. A., et al.** (2025). *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning*. arXiv:2507.19457. Accepted to ICLR 2026 (Oral).

- **DSPy Documentation**: [https://dspy.ai/](https://dspy.ai/) — Includes tutorials and API reference for using GEPA within DSPy programs.

- **GEPA Implementation**: [https://github.com/gepa-ai/gepa](https://github.com/gepa-ai/gepa)

Additional practical examples and case studies are available in the DSPy tutorials and community resources.

---

*This white paper summarizes publicly available research and documentation as of July 2026. Results may vary by task, data, and implementation details. Always validate optimizations on representative test sets for your specific use case.*