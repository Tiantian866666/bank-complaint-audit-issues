"""Data validation rules for input tickets."""

from __future__ import annotations

import pandas as pd


def validate_required_fields(frame: pd.DataFrame, required_fields: list[str]) -> None:
    missing = [field for field in required_fields if field not in frame.columns]
    if missing:
        raise ValueError(f"Input is missing required fields: {missing}")


def validate_ticket_ids(frame: pd.DataFrame) -> None:
    if frame["ticket_id"].isna().any():
        raise ValueError("Input contains empty ticket_id values.")

