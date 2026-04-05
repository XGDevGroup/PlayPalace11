"""Loader helpers for Monopoly manual rule artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from .models import ManualRuleSet


DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data"


def load_manual_rule_set(board_id: str, data_dir: Path | None = None) -> ManualRuleSet:
    """Load one board manual rule set from JSON artifact."""
    base = data_dir or DEFAULT_DATA_DIR
    path = base / f"{board_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ManualRuleSet.from_dict(payload)
