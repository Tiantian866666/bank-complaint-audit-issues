"""Structured fact extraction for issue texts."""

from __future__ import annotations

import json
from collections import Counter
from typing import Iterable

import pandas as pd

from audit_issue_engine.extraction.dictionaries import (
    BUSINESS_OBJECT_KEYWORDS,
    CHANNEL_KEYWORDS,
    FEE_KEYWORDS,
    PROCESS_STAGE_KEYWORDS,
    PROBLEM_TYPE_KEYWORDS,
    THIRD_PARTY_KEYWORDS,
)
from audit_issue_engine.extraction.pattern_rules import (
    extract_activity_mentions,
    extract_card_mentions,
    extract_contract_mentions,
    extract_money_mentions,
    extract_rate_mentions,
)


def _first_keyword_match(text: str, mapping: dict[str, Iterable[str]], fallback: str = "") -> str:
    scores = Counter()
    for label, keywords in mapping.items():
        for keyword in keywords:
            if keyword and keyword in text:
                scores[label] += 1
    return scores.most_common(1)[0][0] if scores else fallback


def _best_term(text: str, term_catalog: pd.DataFrame, term_type: str) -> str:
    candidates = term_catalog.loc[term_catalog["term_type"] == term_type, "normalized_term"].tolist()
    matches = [candidate for candidate in candidates if candidate and candidate in text]
    matches = sorted(set(matches), key=len, reverse=True)
    return matches[0] if matches else ""


def extract_issue_facts(issues: pd.DataFrame, term_catalog: pd.DataFrame) -> pd.DataFrame:
    """Extract structured facts from issue-level text."""

    records: list[dict[str, str]] = []
    for row in issues.to_dict(orient="records"):
        text = str(row["issue_text"])
        money_amounts = extract_money_mentions(text)
        rate_mentions = extract_rate_mentions(text)
        card_mentions = extract_card_mentions(text)
        contract_mentions = extract_contract_mentions(text)
        activity_mentions = extract_activity_mentions(text)

        matched_terms = [
            term
            for term in term_catalog.get("normalized_term", pd.Series(dtype="object")).tolist()
            if isinstance(term, str) and term and term in text
        ]
        third_party = next((item for item in THIRD_PARTY_KEYWORDS if item in text), "")

        biz_object = _first_keyword_match(text, BUSINESS_OBJECT_KEYWORDS, fallback=str(row.get("biz_type", "")))
        process_stage = _first_keyword_match(text, PROCESS_STAGE_KEYWORDS)
        problem_type = _first_keyword_match(text, PROBLEM_TYPE_KEYWORDS)
        channel_name = _first_keyword_match(text, CHANNEL_KEYWORDS)
        fee_type = _first_keyword_match(text, FEE_KEYWORDS)

        card_type = _best_term(text, term_catalog, "card_type")
        system_name = _best_term(text, term_catalog, "system") or channel_name
        activity_name = _best_term(text, term_catalog, "activity")
        contract_type = _best_term(text, term_catalog, "contract")
        product_name = card_type or activity_name or system_name

        records.append(
            {
                "issue_id": row["issue_id"],
                "ticket_id": row["ticket_id"],
                "biz_object": biz_object,
                "product_name": product_name,
                "card_type": card_type or (card_mentions[0] if card_mentions else ""),
                "process_stage": process_stage,
                "problem_type": problem_type,
                "system_name": system_name,
                "channel_name": channel_name,
                "fee_type": fee_type,
                "contract_type": contract_type or (contract_mentions[0] if contract_mentions else ""),
                "activity_name": activity_name or (activity_mentions[0] if activity_mentions else ""),
                "third_party": third_party,
                "extra_facts_json": json.dumps(
                    {
                        "money_amounts": money_amounts,
                        "rate_mentions": rate_mentions,
                        "matched_terms": matched_terms,
                    },
                    ensure_ascii=False,
                ),
            }
        )
    return pd.DataFrame.from_records(records)

