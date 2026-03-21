"""CLI smoke test."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CliSmokeTests(unittest.TestCase):
    def test_full_run_smoke(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        command = [
            sys.executable,
            "-m",
            "audit_issue_engine.cli",
            "full-run",
            "--dataset",
            "sample_local",
            "--profile",
            "cpu",
            "--run-id",
            "SMOKE-TEST",
        ]
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        run_dir = ROOT / "data" / "runs" / "sample_local" / "SMOKE-TEST"
        self.assertTrue((run_dir / "issues.parquet").exists())
        self.assertTrue((run_dir / "issue_assignments.parquet").exists())
        self.assertTrue((run_dir / "category_summary.xlsx").exists())


if __name__ == "__main__":
    unittest.main()

