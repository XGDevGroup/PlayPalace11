"""Validation helpers for manual-cited Monopoly rule artifacts."""

from __future__ import annotations

from .models import ManualRuleSet


REQUIRED_CITATION_PATHS = (
    "board.spaces",
    "economy.properties",
    "cards.chance",
    "cards.community_chest",
    "win_condition",
)


def validate_manual_rule_set(rule_set: ManualRuleSet) -> list[str]:
    """Return validation errors for one manual rule set."""
    errors: list[str] = []
    cited_paths = {citation.rule_path for citation in rule_set.citations}
    for path in REQUIRED_CITATION_PATHS:
        if path not in cited_paths:
            errors.append(f"missing citation for {path}")
    return errors
