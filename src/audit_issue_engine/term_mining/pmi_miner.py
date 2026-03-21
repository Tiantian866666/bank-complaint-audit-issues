"""Lightweight PMI-based term scoring."""

from __future__ import annotations

import math
from collections import Counter

import pandas as pd

from audit_issue_engine.term_mining.ngram_miner import tokenize


def mine_pmi_terms(texts: list[str], min_support: int = 2) -> pd.DataFrame:
    """Compute a simple bigram PMI score for candidate phrases."""

    unigram_counter: Counter[str] = Counter()
    bigram_counter: Counter[tuple[str, str]] = Counter()
    total_tokens = 0

    for text in texts:
        tokens = tokenize(text)
        total_tokens += len(tokens)
        unigram_counter.update(tokens)
        bigram_counter.update(zip(tokens, tokens[1:]))

    rows: list[dict[str, float | int | str]] = []
    for (left, right), count in bigram_counter.items():
        if count < min_support:
            continue
        left_count = unigram_counter[left]
        right_count = unigram_counter[right]
        if not left_count or not right_count or not total_tokens:
            continue
        pmi = math.log2((count * total_tokens) / (left_count * right_count))
        rows.append(
            {
                "term_text": f"{left}{right}",
                "support_count": count,
                "pmi_score": round(pmi, 4),
            }
        )
    return pd.DataFrame(rows, columns=["term_text", "support_count", "pmi_score"])

