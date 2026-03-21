"""N-gram and token frequency mining."""

from __future__ import annotations

from collections import Counter

import jieba
import pandas as pd

from audit_issue_engine.utils.text import normalize_text


STOPWORDS = {"客户", "银行", "工行", "问题", "情况", "要求", "投诉", "表示", "称", "进行"}


def tokenize(text: str) -> list[str]:
    return [token.strip() for token in jieba.lcut(normalize_text(text)) if token.strip()]


def mine_ngram_terms(texts: list[str], min_support: int = 2, top_k: int = 200) -> pd.DataFrame:
    """Mine frequent domain terms from issue texts."""

    counter: Counter[str] = Counter()
    for text in texts:
        tokens = tokenize(text)
        for token in tokens:
            if len(token) < 2 or token in STOPWORDS:
                continue
            counter[token] += 1

    rows = [
        {"term_text": term, "support_count": count}
        for term, count in counter.most_common(top_k)
        if count >= min_support
    ]
    return pd.DataFrame(rows, columns=["term_text", "support_count"])

