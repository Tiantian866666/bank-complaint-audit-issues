"""Excel report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_category_summary(assignments: pd.DataFrame) -> pd.DataFrame:
    summary = (
        assignments.groupby("display_name", dropna=False)
        .agg(issue_count=("issue_id", "nunique"), ticket_count=("ticket_id", "nunique"))
        .reset_index()
        .sort_values(["issue_count", "ticket_count"], ascending=False)
    )
    return summary


def build_category_drilldown(assignments: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "display_name",
        "ticket_id",
        "issue_id",
        "assigned_type_id",
        "type_level",
        "score",
        "assignment_reason",
        "evidence_text",
    ]
    return assignments[columns].sort_values(["display_name", "ticket_id", "issue_id"]).reset_index(drop=True)


def build_new_type_candidates(working_types: pd.DataFrame) -> pd.DataFrame:
    return working_types.sort_values("cluster_size", ascending=False).reset_index(drop=True)


def write_excel_reports(run_dir: Path, assignments: pd.DataFrame, working_types: pd.DataFrame) -> None:
    summary = build_category_summary(assignments)
    drilldown = build_category_drilldown(assignments)
    new_types = build_new_type_candidates(working_types)

    summary.to_excel(run_dir / "category_summary.xlsx", index=False)
    drilldown.to_excel(run_dir / "category_drilldown.xlsx", index=False)
    new_types.to_excel(run_dir / "new_type_candidates.xlsx", index=False)

