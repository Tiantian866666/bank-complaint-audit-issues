"""Writers for ingest stage artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from audit_issue_engine.config.manifest import RuntimeConfig
from audit_issue_engine.utils.io import ensure_dir, write_json


def write_tickets_artifacts(frame: pd.DataFrame, runtime: RuntimeConfig) -> Path:
    ensure_dir(runtime.run_dir)
    tickets_path = runtime.run_dir / "tickets.parquet"
    frame.to_parquet(tickets_path, index=False)
    write_json(
        runtime.run_dir / "run_manifest.json",
        {
            "dataset_id": runtime.dataset.dataset_id,
            "dataset_name": runtime.dataset.display_name,
            "profile_name": runtime.profile.profile_name,
            "run_id": runtime.run_id,
            "input_path_or_uri": runtime.input_path_or_uri,
            "row_count": int(len(frame)),
        },
    )
    return tickets_path

