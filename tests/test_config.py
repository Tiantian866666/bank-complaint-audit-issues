"""Configuration loading tests."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from audit_issue_engine.config.settings import load_runtime_config  # noqa: E402


class ConfigTests(unittest.TestCase):
    def test_sample_runtime_config_loads(self) -> None:
        runtime = load_runtime_config(ROOT, "sample_local", "cpu", run_id="TEST-RUN")
        self.assertEqual(runtime.dataset.dataset_id, "sample_local")
        self.assertEqual(runtime.profile.profile_name, "cpu")
        self.assertEqual(runtime.primary_text_field, "desc_clean")
        self.assertTrue(str(runtime.input_path_or_uri).endswith("sample_tickets.csv"))


if __name__ == "__main__":
    unittest.main()

