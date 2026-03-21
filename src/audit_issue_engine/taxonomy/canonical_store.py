"""Load and persist canonical issue types."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


CANONICAL_COLUMNS = [
    "canonical_type_id",
    "canonical_name",
    "definition",
    "status",
    "source_working_type_id",
]


def load_canonical_store(project_root: Path) -> pd.DataFrame:
    path = project_root / "data" / "external" / "canonical_types.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=CANONICAL_COLUMNS)


def save_canonical_store(project_root: Path, frame: pd.DataFrame) -> Path:
    path = project_root / "data" / "external" / "canonical_types.csv"
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    return path

