"""Cluster issue representations into working types."""

from __future__ import annotations

import numpy as np
from sklearn.cluster import DBSCAN

from audit_issue_engine.config.manifest import ProfileSettings


def cluster_issue_space(reduced_features: np.ndarray, profile: ProfileSettings) -> tuple[np.ndarray, str]:
    """Cluster reduced issue embeddings with HDBSCAN or a sklearn fallback."""

    if len(reduced_features) == 0:
        return np.array([], dtype=int), "empty"
    if len(reduced_features) == 1:
        return np.array([0], dtype=int), "singleton"

    if profile.use_hdbscan:
        try:
            import hdbscan

            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=min(profile.min_cluster_size, len(reduced_features)),
                min_samples=min(profile.min_samples, max(1, len(reduced_features) - 1)),
            )
            labels = clusterer.fit_predict(reduced_features)
            return labels.astype(int), "hdbscan"
        except Exception:
            pass

    fallback = DBSCAN(eps=1.1, min_samples=max(2, profile.min_samples))
    labels = fallback.fit_predict(reduced_features)
    return labels.astype(int), "dbscan"

