# Reflective Prompt Optimization with GEPA

*A More Efficient Path to Improving AI System Performance*

**White Paper | July 2026**

---

## Executive Summary

Teams that want better AI results on a specific task have two common options. They can craft prompts by hand. They can also use expensive reinforcement learning (RL) that updates the model itself.

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

