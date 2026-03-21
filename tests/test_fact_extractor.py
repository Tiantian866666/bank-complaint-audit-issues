"""Fact extractor tests."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from audit_issue_engine.extraction.fact_extractor import extract_issue_facts  # noqa: E402


class FactExtractorTests(unittest.TestCase):
    def test_fact_extractor_finds_problem_type_and_stage(self) -> None:
        issues = pd.DataFrame(
            [
                {
                    "issue_id": "I1",
                    "ticket_id": "T1",
                    "issue_text": "客户称车贷合同金额不一致, 要求提前还款, 只还本金7万元",
                    "biz_type": "信用卡",
                    "biz_subtype": "汽车专项分期",
                }
            ]
        )
        term_catalog = pd.DataFrame(
            [
                {"term_text": "车贷", "term_type": "contract", "normalized_term": "车贷", "support_count": 2},
            ]
        )
        facts = extract_issue_facts(issues, term_catalog)
        self.assertEqual(facts.loc[0, "problem_type"], "合同金额争议")
        self.assertIn(facts.loc[0, "process_stage"], {"签约放款", "还款扣款"})


if __name__ == "__main__":
    unittest.main()

