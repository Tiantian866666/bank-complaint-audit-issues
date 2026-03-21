"""Promote reviewed working types into canonical types."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from audit_issue_engine.taxonomy.canonical_store import load_canonical_store, save_canonical_store


def promote_working_types(project_root: Path, mapping_file: Path) -> pd.DataFrame:
    """Apply a working-type review file and update canonical types."""

    canonical = load_canonical_store(project_root)
    mapping = pd.read_csv(mapping_file)

    next_index = len(canonical) + 1
    new_rows = []
    for row in mapping.to_dict(orient="records"):
        action = str(row.get("action", "")).strip().lower()
        if action != "promote":
            continue
        new_rows.append(
            {
                "canonical_type_id": f"CT-{next_index:04d}",
                "canonical_name": row.get("canonical_name", row.get("working_type_id", "")),
                "definition": row.get("notes", ""),
                "status": "active",
                "source_working_type_id": row.get("working_type_id", ""),
            }
        )
        next_index += 1

    if new_rows:
        canonical = pd.concat([canonical, pd.DataFrame(new_rows)], ignore_index=True)
        canonical = canonical.drop_duplicates(subset=["canonical_name"], keep="last").reset_index(drop=True)
    save_canonical_store(project_root, canonical)
    return canonical

