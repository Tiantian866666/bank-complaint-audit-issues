"""Working type title generation tests."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from audit_issue_engine.discovery.title_generator import build_working_types  # noqa: E402


class TitleGeneratorTests(unittest.TestCase):
    def test_titles_reflect_structured_facts(self) -> None:
        issues = pd.DataFrame(
            [
                {"ticket_id": "T1", "issue_id": "T1-I01", "issue_text": "车贷合同金额不一致", "source_field": "desc_clean", "evidence_text": "车贷合同金额不一致"},
                {"ticket_id": "T2", "issue_id": "T2-I01", "issue_text": "车贷合同金额和客户认知不一致", "source_field": "desc_clean", "evidence_text": "车贷合同金额和客户认知不一致"},
            ]
        )
        facts = pd.DataFrame(
            [
                {"issue_id": "T1-I01", "ticket_id": "T1", "biz_object": "汽车专项分期", "product_name": "", "card_type": "", "system_name": "", "process_stage": "签约放款", "problem_type": "合同金额争议", "activity_name": ""},
                {"issue_id": "T2-I01", "ticket_id": "T2", "biz_object": "汽车专项分期", "product_name": "", "card_type": "", "system_name": "", "process_stage": "签约放款", "problem_type": "合同金额争议", "activity_name": ""},
            ]
        )
        working_types, issue_map = build_working_types(issues, facts, ["cluster_0", "cluster_0"])
        self.assertEqual(len(working_types), 1)
        self.assertIn("汽车专项分期", working_types.loc[0, "auto_title"])
        self.assertEqual(len(issue_map), 2)


if __name__ == "__main__":
    unittest.main()

