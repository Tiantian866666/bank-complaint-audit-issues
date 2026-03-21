"""Configuration loading helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from audit_issue_engine.config.manifest import (
    BaseSettings,
    DatasetManifest,
    ProfileSettings,
    RuntimeConfig,
)
from audit_issue_engine.utils.io import resolve_path_like


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_runtime_config(
    project_root: Path,
    dataset_id: str,
    profile_name: str,
    run_id: str | None = None,
) -> RuntimeConfig:
    """Load and resolve base, profile and dataset config into one object."""

    base_file = project_root / "configs" / "base.yaml"
    profile_file = project_root / "configs" / "profiles" / f"{profile_name}.yaml"
    dataset_file = project_root / "configs" / "datasets" / f"{dataset_id}.yaml"

    base = BaseSettings.model_validate(_read_yaml(base_file))
    profile = ProfileSettings.model_validate(_read_yaml(profile_file))
    dataset = DatasetManifest.model_validate(_read_yaml(dataset_file))

    resolved_run_id = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    runs_dir = project_root / base.paths["runs_dir"]
    run_dir = runs_dir / dataset.dataset_id / resolved_run_id
    input_path_or_uri = resolve_path_like(dataset.input_uri, project_root, dataset_file.parent)

    return RuntimeConfig(
        project_root=project_root,
        dataset_file=dataset_file,
        profile_file=profile_file,
        base_file=base_file,
        dataset=dataset,
        base=base,
        profile=profile,
        run_id=resolved_run_id,
        run_dir=run_dir,
        input_path_or_uri=input_path_or_uri,
        required_fields=list(base.ingest["required_fields"]),
        primary_text_field=base.texts["primary_field"],
        secondary_text_field=base.texts["secondary_field"],
        max_secondary_labels=int(base.assignment["max_secondary_labels"]),
    )

