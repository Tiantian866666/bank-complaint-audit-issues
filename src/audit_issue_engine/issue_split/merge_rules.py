"""Heuristics for merging neighboring short clauses."""

from __future__ import annotations

import re

from audit_issue_engine.utils.text import normalize_clause


STRONG_SIGNAL_RE = re.compile(
    r"(卡|贷款|合同|金额|额度|返现|收费|利息|分期|解押|销户|系统|网点|短信|活动|投诉|办理|规则)"
)


def should_merge(previous_text: str, current_text: str) -> bool:
    """Merge short, weak fragments into the previous clause."""

    previous = normalize_clause(previous_text)
    current = normalize_clause(current_text)
    if not previous or not current:
        return True
    if len(current) <= 10:
        return True
    if not STRONG_SIGNAL_RE.search(current):
        return True
    if previous.endswith(("要求", "希望", "请求", "并")):
        return True
    return False


def merge_adjacent_segments(segments: list[str]) -> list[str]:
    """Merge neighboring segments based on simple semantic cues."""

    merged: list[str] = []
    for segment in segments:
        current = normalize_clause(segment)
        if not current:
            continue
        if merged and should_merge(merged[-1], current):
            merged[-1] = normalize_clause(f"{merged[-1]}，{current}")
            continue
        merged.append(current)
    return merged

