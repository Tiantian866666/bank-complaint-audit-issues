"""Persist sparse and dense feature artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
from scipy.sparse import save_npz

from audit_issue_engine.utils.io import ensure_dir, write_json


def persist_feature_store(
    run_dir: Path,
    sparse_matrix: Any,
    sparse_artifacts: dict[str, Any],
    dense_embeddings: np.ndarray | None,
    metadata: dict[str, Any],
) -> Path:
    """Save feature artifacts into the run directory."""

    feature_dir = ensure_dir(run_dir / "feature_store")
    save_npz(feature_dir / "sparse_features.npz", sparse_matrix)
    joblib.dump(sparse_artifacts, feature_dir / "vectorizers.joblib")
    if dense_embeddings is not None:
        np.save(feature_dir / "dense_features.npy", dense_embeddings)
    write_json(feature_dir / "metadata.json", metadata)
    return feature_dir

