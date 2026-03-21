"""Convenience wrapper for the CLI full-run command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import os


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")
    command = [
        sys.executable,
        "-m",
        "audit_issue_engine.cli",
        "full-run",
        "--dataset",
        "sample_local",
        "--profile",
        "cpu",
    ]
    return subprocess.call(command, cwd=root, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
