"""Helpers around working type tables."""

from __future__ import annotations

import pandas as pd


def build_working_type_lookup(working_types: pd.DataFrame) -> dict[str, dict[str, str]]:
    return {
        row["working_type_id"]: {
            "auto_title": row["auto_title"],
            "keywords": row["keywords"],
        }
        for row in working_types.to_dict(orient="records")
    }

