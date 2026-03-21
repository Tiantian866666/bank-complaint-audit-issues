"""Optional dense sentence encoder."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from audit_issue_engine.config.manifest import ProfileSettings


def encode_dense_features(
    texts: list[str],
    profile: ProfileSettings,
    cache_dir: Path,
) -> tuple[np.ndarray | None, dict[str, str]]:
    """Encode texts with a local sentence-transformers model when available."""

    if not profile.use_dense_encoder or not profile.dense_encoder_name:
        return None, {"encoder_mode": "disabled"}

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None, {"encoder_mode": "sparse_only", "reason": "sentence-transformers not installed"}

    try:
        model = SentenceTransformer(profile.dense_encoder_name, cache_folder=str(cache_dir))
        embeddings = model.encode(
            texts,
            batch_size=profile.dense_batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype="float32"), {"encoder_mode": "dense", "model": profile.dense_encoder_name}
    except Exception as exc:  # pragma: no cover - environment dependent
        if not profile.allow_sparse_only_fallback:
            raise
        return None, {"encoder_mode": "sparse_only", "reason": str(exc)}

