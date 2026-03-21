"""Reduce high-dimensional feature spaces before clustering."""

from __future__ import annotations

import numpy as np
from scipy.sparse import issparse
from sklearn.decomposition import TruncatedSVD

from audit_issue_engine.config.manifest import ProfileSettings


def reduce_features(
    sparse_matrix,
    dense_embeddings: np.ndarray | None,
    profile: ProfileSettings,
) -> tuple[np.ndarray, str]:
    """Reduce sparse or dense features into a clustering-friendly space."""

    if dense_embeddings is not None:
        feature_source = dense_embeddings
    else:
        feature_source = sparse_matrix

    if feature_source.shape[0] <= 2:
        dense = feature_source.toarray() if issparse(feature_source) else np.asarray(feature_source)
        return dense, "identity"

    if profile.use_umap:
        try:
            import umap

            reducer = umap.UMAP(
                n_components=min(10, max(2, feature_source.shape[0] - 1)),
                metric="cosine",
                random_state=profile.random_seed,
            )
            reduced = reducer.fit_transform(feature_source)
            return np.asarray(reduced), "umap"
        except Exception:
            pass

    if issparse(feature_source):
        n_components = min(50, max(2, feature_source.shape[0] - 1), feature_source.shape[1] - 1)
        reducer = TruncatedSVD(n_components=n_components, random_state=profile.random_seed)
        return reducer.fit_transform(feature_source), "truncated_svd"

    return np.asarray(feature_source), "dense_identity"

