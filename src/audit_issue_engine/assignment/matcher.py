"""Assign issues to canonical or working types."""

from __future__ import annotations

import pandas as pd

from audit_issue_engine.assignment.label_builder import build_display_name
from audit_issue_engine.assignment.scorer import score_type_match


def assign_issue_labels(
    issues: pd.DataFrame,
    facts: pd.DataFrame,
    issue_working_map: pd.DataFrame,
    working_types: pd.DataFrame,
    canonical_types: pd.DataFrame,
    max_secondary_labels: int,
) -> pd.DataFrame:
    """Assign primary and optional secondary labels to each issue."""

    merged = (
        issues.merge(facts, on=["issue_id", "ticket_id"], how="left")
        .merge(issue_working_map, on="issue_id", how="left")
        .merge(working_types[["working_type_id", "auto_title"]], on="working_type_id", how="left")
    )

    canonical_records = canonical_types.to_dict(orient="records")
    rows = []

    for row in merged.to_dict(orient="records"):
        issue_text = str(row.get("issue_text", "") or "")
        primary_type_id = str(row.get("working_type_id", "") or "")
        primary_title = str(row.get("auto_title", "") or "未命名问题簇")
        display_name = build_display_name(pd.Series(row), primary_title)

        best_canonical = None
        best_score = 0.0
        for candidate in canonical_records:
            candidate_text = " ".join(
                [str(candidate.get("canonical_name", "") or ""), str(candidate.get("definition", "") or "")]
            ).strip()
            score = score_type_match(issue_text, candidate_text)
            if score > best_score:
                best_score = score
                best_canonical = candidate

        if best_canonical and best_score >= 0.78:
            rows.append(
                {
                    "issue_id": row["issue_id"],
                    "ticket_id": row["ticket_id"],
                    "assigned_type_id": best_canonical["canonical_type_id"],
                    "type_level": "canonical",
                    "display_name": build_display_name(pd.Series(row), best_canonical["canonical_name"]),
                    "score": best_score,
                    "assignment_reason": "matched existing canonical type",
                    "evidence_text": row["evidence_text"],
                }
            )
            if max_secondary_labels > 0 and primary_type_id:
                rows.append(
                    {
                        "issue_id": row["issue_id"],
                        "ticket_id": row["ticket_id"],
                        "assigned_type_id": primary_type_id,
                        "type_level": "working",
                        "display_name": display_name,
                        "score": 1.0,
                        "assignment_reason": "fallback working type",
                        "evidence_text": row["evidence_text"],
                    }
                )
        else:
            rows.append(
                {
                    "issue_id": row["issue_id"],
                    "ticket_id": row["ticket_id"],
                    "assigned_type_id": primary_type_id,
                    "type_level": "working",
                    "display_name": display_name,
                    "score": 1.0,
                    "assignment_reason": "primary working type",
                    "evidence_text": row["evidence_text"],
                }
            )

    return pd.DataFrame(rows).drop_duplicates(
        subset=["issue_id", "assigned_type_id", "type_level"]
    ).reset_index(drop=True)

