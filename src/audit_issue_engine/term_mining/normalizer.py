"""Normalize and classify mined terms."""

from __future__ import annotations

from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz


TERM_TYPE_RULES = {
    "card_type": ["卡", "社保卡", "星座卡", "宝宝成长卡"],
    "system": ["系统", "手机银行", "工银e生活", "平台", "ATM", "POS", "ETC"],
    "activity": ["活动", "返现", "礼", "权益", "消费季", "plus"],
    "fee": ["费", "息", "年费", "违约金", "信使费"],
    "contract": ["合同", "协议", "面签", "签约", "放款"],
}


def infer_term_type(term: str) -> str:
    lowered = term.lower()
    for term_type, signals in TERM_TYPE_RULES.items():
        if any(signal.lower() in lowered for signal in signals):
            return term_type
    return "generic"


def normalize_terms(ngram_terms: pd.DataFrame, pmi_terms: pd.DataFrame) -> pd.DataFrame:
    """Merge mined term tables and normalize close spellings."""

    frames = [frame for frame in (ngram_terms, pmi_terms) if not frame.empty]
    if not frames:
        return pd.DataFrame(columns=["term_text", "term_type", "normalized_term", "support_count"])

    merged = pd.concat(frames, ignore_index=True, sort=False).fillna({"pmi_score": 0.0})
    merged = merged.sort_values(["support_count", "pmi_score"], ascending=False)

    groups: dict[str, list[str]] = defaultdict(list)
    canonical_terms: list[str] = []
    for term in merged["term_text"].astype(str).tolist():
        matched = None
        for canonical in canonical_terms:
            if fuzz.ratio(term, canonical) >= 90 or term in canonical or canonical in term:
                matched = canonical
                break
        if matched is None:
            canonical_terms.append(term)
            matched = term
        groups[matched].append(term)

    rows = []
    for canonical, variants in groups.items():
        support = int(merged.loc[merged["term_text"].isin(variants), "support_count"].sum())
        rows.append(
            {
                "term_text": canonical,
                "term_type": infer_term_type(canonical),
                "normalized_term": canonical,
                "support_count": support,
            }
        )
    return pd.DataFrame(rows).sort_values("support_count", ascending=False).reset_index(drop=True)

