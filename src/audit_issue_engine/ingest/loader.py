"""Dataset loading logic."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from audit_issue_engine.utils.io import is_http_uri


def load_input_table(input_path_or_uri: str) -> pd.DataFrame:
    """Load a CSV or Excel file from local disk or URL."""

    suffix = Path(input_path_or_uri).suffix.lower()
    if is_http_uri(input_path_or_uri):
        suffix = Path(input_path_or_uri.split("?")[0]).suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(input_path_or_uri)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(input_path_or_uri)
    raise ValueError(f"Unsupported input format: {input_path_or_uri}")

