"""Build display labels shown to auditors."""

from __future__ import annotations

import pandas as pd


def build_display_name(facts_row: pd.Series, fallback_title: str) -> str:
    """Build a concrete display name from facts and a fallback cluster title."""

    parts = [
        str(facts_row.get("biz_object", "") or ""),
        str(facts_row.get("product_name", "") or ""),
        str(facts_row.get("card_type", "") or ""),
        str(facts_row.get("system_name", "") or ""),
        str(facts_row.get("process_stage", "") or ""),
        str(facts_row.get("problem_type", "") or ""),
    ]
    deduped = []
    for part in parts:
        if part and part not in deduped:
            deduped.append(part)
    if deduped:
        return "-".join(deduped[:5])
    return fallback_title

