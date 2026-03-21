"""Sparse feature builders."""

from __future__ import annotations

import jieba
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer


def _jieba_tokenizer(text: str) -> list[str]:
    return [token.strip() for token in jieba.lcut(text) if token.strip()]


def build_sparse_features(texts: list[str]) -> tuple[object, dict[str, object]]:
    """Build a char + word TF-IDF feature matrix."""

    char_vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
        min_df=1,
        sublinear_tf=True,
    )
    word_vectorizer = TfidfVectorizer(
        tokenizer=_jieba_tokenizer,
        token_pattern=None,
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )

    char_matrix = char_vectorizer.fit_transform(texts)
    word_matrix = word_vectorizer.fit_transform(texts)
    matrix = hstack([char_matrix, word_matrix]).tocsr()
    artifacts = {
        "char_vectorizer": char_vectorizer,
        "word_vectorizer": word_vectorizer,
    }
    return matrix, artifacts

