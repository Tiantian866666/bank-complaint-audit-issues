"""Markdown run summary generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_run_summary(
    run_dir: Path,
    dataset_name: str,
    profile_name: str,
    tickets: pd.DataFrame,
    issues: pd.DataFrame,
    working_types: pd.DataFrame,
    assignments: pd.DataFrame,
    diagnostics: dict[str, str],
) -> Path:
    """Write a Markdown summary of the latest run."""

    top_categories = (
        assignments.groupby("display_name")
        .agg(issue_count=("issue_id", "nunique"))
        .sort_values("issue_count", ascending=False)
        .head(10)
        .reset_index()
    )
    lines = [
        f"# Run Summary: {dataset_name}",
        "",
        f"- Profile: `{profile_name}`",
        f"- Ticket count: `{len(tickets)}`",
        f"- Issue count: `{len(issues)}`",
        f"- Working type count: `{len(working_types)}`",
        f"- Assignment count: `{len(assignments)}`",
        "",
        "## Diagnostics",
        "",
    ]
    for key, value in diagnostics.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Top Categories", ""])
    for row in top_categories.to_dict(orient="records"):
        lines.append(f"- {row['display_name']}: `{row['issue_count']}` issues")

    path = run_dir / "run_summary.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

