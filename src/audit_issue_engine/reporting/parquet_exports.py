"""Parquet export helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from audit_issue_engine.utils.io import ensure_dir


def export_parquet_tables(run_dir: Path, tables: dict[str, pd.DataFrame]) -> None:
    """Write a set of dataframes to parquet files."""

    ensure_dir(run_dir)
    for file_name, frame in tables.items():
        frame.to_parquet(run_dir / file_name, index=False)

