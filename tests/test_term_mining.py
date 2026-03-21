"""Term mining tests."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from audit_issue_engine.term_mining.ngram_miner import mine_ngram_terms  # noqa: E402
from audit_issue_engine.term_mining.normalizer import normalize_terms  # noqa: E402
from audit_issue_engine.term_mining.pmi_miner import mine_pmi_terms  # noqa: E402


class TermMiningTests(unittest.TestCase):
    def test_term_catalog_contains_domain_terms(self) -> None:
        texts = [
            "宝宝成长卡办理失败, 客户不认可",
            "宝宝成长卡系统提示无法办理",
            "车贷合同金额不一致, 客户要求核实合同",
        ]
        ngrams = mine_ngram_terms(texts, min_support=1, top_k=20)
        pmi = mine_pmi_terms(texts, min_support=1)
        catalog = normalize_terms(ngrams, pmi)
        self.assertIn("term_type", catalog.columns)
        self.assertTrue((catalog["term_text"].str.contains("成长卡")).any())


if __name__ == "__main__":
    unittest.main()

