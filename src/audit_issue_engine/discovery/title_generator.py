"""Generate human-readable working type titles."""

from __future__ import annotations

from collections import Counter

import jieba
import pandas as pd

from audit_issue_engine.utils.text import top_items


STOPWORDS = {"客户", "银行", "工行", "表示", "要求", "投诉", "问题", "情况"}


def _top_keywords(texts: list[str], limit: int = 5) -> list[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        for token in jieba.lcut(text):
            token = token.strip()
            if len(token) < 2 or token in STOPWORDS:
                continue
            counter[token] += 1
    return [token for token, _ in counter.most_common(limit)]


def _build_title(group: pd.DataFrame) -> str:
    facts_columns = [
        "biz_object",
        "product_name",
        "card_type",
        "system_name",
        "process_stage",
        "problem_type",
        "activity_name",
    ]
    parts: list[str] = []
    for column in facts_columns:
        parts.extend(top_items(group[column].fillna("").astype(str).tolist(), limit=1))
    deduped = []
    for part in parts:
        if part and part not in deduped:
            deduped.append(part)
    if deduped:
        return "-".join(deduped[:4])
    keywords = _top_keywords(group["issue_text"].astype(str).tolist(), limit=3)
    return "-".join(keywords) if keywords else "未命名问题簇"


def build_working_types(
    issues: pd.DataFrame,
    facts: pd.DataFrame,
    resolved_labels: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create working types and an issue-to-working-type map."""

    merged = issues.copy()
    merged["raw_working_label"] = resolved_labels
    merged = merged.merge(facts, on=["issue_id", "ticket_id"], how="left")

    working_rows = []
    assignment_rows = []
    label_to_id: dict[str, str] = {}

    for index, raw_label in enumerate(sorted(merged["raw_working_label"].unique()), start=1):
        label_to_id[raw_label] = f"WT-{index:04d}"

    for raw_label, group in merged.groupby("raw_working_label", dropna=False):
        working_type_id = label_to_id[raw_label]
        title = _build_title(group)
        keywords = ",".join(_top_keywords(group["issue_text"].astype(str).tolist()))
        representatives = ",".join(group["issue_id"].astype(str).head(3).tolist())
        working_rows.append(
            {
                "working_type_id": working_type_id,
                "raw_working_label": raw_label,
                "auto_title": title,
                "keywords": keywords,
                "cluster_size": int(len(group)),
                "status": "candidate",
                "representative_issue_ids": representatives,
            }
        )
        for issue_id in group["issue_id"].astype(str):
            assignment_rows.append(
                {
                    "issue_id": issue_id,
                    "working_type_id": working_type_id,
                    "raw_working_label": raw_label,
                }
            )

    return (
        pd.DataFrame(working_rows).sort_values("cluster_size", ascending=False).reset_index(drop=True),
        pd.DataFrame(assignment_rows),
    )

