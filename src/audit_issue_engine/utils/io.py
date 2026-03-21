"""Small IO helpers shared across the project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def is_http_uri(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"}


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_path_like(value: str, project_root: Path, base_dir: Path) -> str:
    """Resolve a path-like value against project and config directories."""

    if is_http_uri(value):
        return value

    candidate = Path(value)
    if candidate.is_absolute():
        return str(candidate)

    for prefix in (base_dir, project_root):
        resolved = (prefix / candidate).resolve()
        if resolved.exists():
            return str(resolved)
    return str((project_root / candidate).resolve())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

