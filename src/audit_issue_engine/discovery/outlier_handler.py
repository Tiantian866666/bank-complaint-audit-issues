"""Handle outliers so every issue receives at least one working type."""

from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def resolve_outliers(
    labels: np.ndarray,
    reduced_features: np.ndarray,
    issue_ids: list[str],
    threshold: float,
) -> list[str]:
    """Convert raw cluster labels into stable working labels and absorb close outliers."""

    if len(labels) == 0:
        return []

    resolved: list[str | None] = [None] * len(labels)
    clustered_labels = sorted({int(label) for label in labels if int(label) >= 0})

    centroids = {}
    for label in clustered_labels:
        indices = np.where(labels == label)[0]
        centroids[label] = reduced_features[indices].mean(axis=0)
        for index in indices:
            resolved[index] = f"cluster_{label}"

    for index, label in enumerate(labels):
        if int(label) >= 0:
            continue
        if centroids:
            current = reduced_features[index].reshape(1, -1)
            centroid_keys = list(centroids.keys())
            centroid_matrix = np.vstack([centroids[key] for key in centroid_keys])
            similarities = cosine_similarity(current, centroid_matrix)[0]
            best_position = int(np.argmax(similarities))
            if float(similarities[best_position]) >= threshold:
                resolved[index] = f"cluster_{centroid_keys[best_position]}"
                continue
        resolved[index] = f"singleton_{issue_ids[index]}"

    return [label or f"singleton_{issue_ids[index]}" for index, label in enumerate(resolved)]

