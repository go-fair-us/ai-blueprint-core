"""Write a short markdown run report."""
from __future__ import annotations

from pathlib import Path


def write_report(
    path: Path,
    *,
    slug: str,
    source_prompt: str,
    branch: str,
    score: float,
    seconds: float,
    n_train: int,
    n_val: int,
    n_test: int,
    program_path: str | None,
    optimized_prompt_path: str | None,
    notes: str = "",
) -> Path:
    lines = [
        f"# libraryOptimizer report: `{slug}`",
        "",
        f"- **Source prompt:** `{source_prompt}`",
        f"- **Branch:** {branch}",
        f"- **Test score (0–1):** {score:.4f}",
        f"- **Wall time (s):** {seconds:.1f}",
        f"- **Split:** train={n_train} / val={n_val} / test={n_test}",
    ]
    if program_path:
        lines.append(f"- **Program:** `{program_path}`")
    if optimized_prompt_path:
        lines.append(f"- **Optimized prompt:** `{optimized_prompt_path}`")
    if notes:
        lines.extend(["", "## Notes", "", notes])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
