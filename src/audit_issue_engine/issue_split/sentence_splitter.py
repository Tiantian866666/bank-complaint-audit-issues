"""Sentence and clause splitting helpers."""

from __future__ import annotations

import re

from audit_issue_engine.utils.text import normalize_clause, normalize_text


SENTENCE_BOUNDARY_RE = re.compile(r"[。！？；;\n]+")
CLAUSE_SPLIT_RE = re.compile(
    r"[，,](?=(?:要求|无法|未|不满|不认可|投诉称|请求|希望|需|但是|但|并要求|并称|并表示))"
)


def split_sentences(text: str | None) -> list[str]:
    """Split a long text into normalized clauses."""

    normalized = normalize_text(text)
    if not normalized:
        return []

    sentences: list[str] = []
    for sentence in SENTENCE_BOUNDARY_RE.split(normalized):
        sentence = normalize_clause(sentence)
        if not sentence:
            continue
        clauses = [normalize_clause(part) for part in CLAUSE_SPLIT_RE.split(sentence)]
        sentences.extend([clause for clause in clauses if clause])
    return sentences

