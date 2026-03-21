"""Simple scoring helpers for issue-to-type matching."""

from __future__ import annotations

from rapidfuzz import fuzz


def score_type_match(issue_text: str, label_text: str) -> float:
    """Score an issue against a candidate type label."""

    if not issue_text or not label_text:
        return 0.0
    return round(fuzz.token_sort_ratio(issue_text, label_text) / 100.0, 4)

