"""Issue segmentation tests."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from audit_issue_engine.issue_split.issue_segmenter import build_issue_records  # noqa: E402


class IssueSplitTests(unittest.TestCase):
    def test_issue_records_are_created(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "ticket_id": "T1",
                    "desc_clean": "客户称车贷合同金额不符, 要求核实并解决",
                    "resolution_cause_clean": "需要联系支行核实合同与放款照片",
                    "biz_type": "信用卡",
                    "biz_subtype": "汽车专项分期",
                }
            ]
        )
        issues = build_issue_records(frame, "desc_clean", "resolution_cause_clean")
        self.assertGreaterEqual(len(issues), 2)
        self.assertTrue(issues["issue_id"].str.startswith("T1-I").all())
        self.assertIn("source_field", issues.columns)


if __name__ == "__main__":
    unittest.main()

