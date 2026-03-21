"""Text normalization helpers."""

from __future__ import annotations

import re
from collections import Counter


SPACE_RE = re.compile(r"\s+")
PUNCT_TRIM_RE = re.compile(r"^[，,;；:：\-\s]+|[，,;；:：\-\s]+$")


def normalize_text(text: str | None) -> str:
    value = text or ""
    value = value.replace("\u3000", " ")
    value = SPACE_RE.sub(" ", value)
    return value.strip()


def normalize_clause(text: str | None) -> str:
    value = normalize_text(text)
    value = PUNCT_TRIM_RE.sub("", value)
    return value


def safe_join(parts: list[str], sep: str = " | ") -> str:
    return sep.join([part for part in parts if part])


def top_items(values: list[str], limit: int = 5) -> list[str]:
    counter = Counter([item for item in values if item])
    return [item for item, _ in counter.most_common(limit)]

