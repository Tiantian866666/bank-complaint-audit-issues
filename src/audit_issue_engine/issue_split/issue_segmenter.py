"""Build issue-level records from ticket-level text."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from audit_issue_engine.issue_split.merge_rules import merge_adjacent_segments
from audit_issue_engine.issue_split.sentence_splitter import split_sentences


@dataclass
class IssueSegment:
    ticket_id: str
    issue_id: str
    issue_text: str
    evidence_text: str
    source_field: str
    issue_order: int


def _build_segments(ticket_id: str, source_field: str, text: str) -> Iterable[IssueSegment]:
    clauses = merge_adjacent_segments(split_sentences(text))
    for index, clause in enumerate(clauses, start=1):
        yield IssueSegment(
            ticket_id=ticket_id,
            issue_id=f"{ticket_id}-{source_field[:1].upper()}{index:02d}",
            issue_text=clause,
            evidence_text=clause,
            source_field=source_field,
            issue_order=index,
        )


def build_issue_records(
    tickets: pd.DataFrame,
    primary_field: str,
    secondary_field: str,
) -> pd.DataFrame:
    """Explode ticket rows into issue-level records."""

    records: list[dict[str, object]] = []
    for row in tickets.to_dict(orient="records"):
        ticket_id = str(row["ticket_id"])
        primary_segments = list(_build_segments(ticket_id, primary_field, str(row.get(primary_field, "") or "")))
        secondary_segments = list(
            _build_segments(ticket_id, secondary_field, str(row.get(secondary_field, "") or ""))
        )

        issue_counter = 1
        for segment in primary_segments + secondary_segments:
            records.append(
                {
                    "ticket_id": segment.ticket_id,
                    "issue_id": f"{ticket_id}-I{issue_counter:02d}",
                    "issue_text": segment.issue_text,
                    "evidence_text": segment.evidence_text,
                    "source_field": segment.source_field,
                    "issue_order": issue_counter,
                    "biz_type": row.get("biz_type", ""),
                    "biz_subtype": row.get("biz_subtype", ""),
                }
            )
            issue_counter += 1

    issues = pd.DataFrame.from_records(records)
    if issues.empty:
        return pd.DataFrame(
            columns=[
                "ticket_id",
                "issue_id",
                "issue_text",
                "evidence_text",
                "source_field",
                "issue_order",
                "biz_type",
                "biz_subtype",
            ]
        )
    return issues.drop_duplicates(subset=["ticket_id", "issue_text", "source_field"]).reset_index(drop=True)

