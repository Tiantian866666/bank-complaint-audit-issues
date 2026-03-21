"""Typed runtime models for the audit issue engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DatasetManifest(BaseModel):
    """Describes a logical dataset and where it is stored."""

    dataset_id: str
    display_name: str
    region: str
    year: int
    input_uri: str
    description: str = ""
    source_repo: str | None = None
    source_commit: str | None = None


class BaseSettings(BaseModel):
    """Top-level project settings shared by all runs."""

    project_name: str
    paths: dict[str, str]
    ingest: dict[str, Any]
    texts: dict[str, str]
    assignment: dict[str, Any]
    discovery: dict[str, Any]
    runtime: dict[str, Any]


class ProfileSettings(BaseModel):
    """Runtime profile that controls algorithm and model choices."""

    profile_name: str
    use_dense_encoder: bool = True
    dense_encoder_name: str | None = None
    allow_sparse_only_fallback: bool = True
    use_umap: bool = True
    use_hdbscan: bool = True
    dense_batch_size: int = 16
    term_top_k: int = 200
    min_cluster_size: int = 3
    min_samples: int = 2
    outlier_similarity_threshold: float = 0.3
    random_seed: int = 20260321


class RuntimeConfig(BaseModel):
    """Fully resolved configuration for a single run."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    project_root: Path
    dataset_file: Path
    profile_file: Path
    base_file: Path
    dataset: DatasetManifest
    base: BaseSettings
    profile: ProfileSettings
    run_id: str
    run_dir: Path
    input_path_or_uri: str
    required_fields: list[str]
    primary_text_field: str
    secondary_text_field: str
    max_secondary_labels: int = Field(default=2)

