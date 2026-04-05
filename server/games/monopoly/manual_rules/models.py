"""Dataclass models for manual-cited Monopoly board rule artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Citation:
    """Source citation for one rule path in a manual rule set."""

    rule_path: str
    edition_id: str
    page_ref: str
    confidence: str


@dataclass(frozen=True)
class ManualRuleSet:
    """Canonical manual-backed rule artifact for one board."""

    board_id: str
    anchor_edition_id: str
    board: dict[str, Any]
    economy: dict[str, Any]
    cards: dict[str, Any]
    mechanics: dict[str, Any]
    win_condition: dict[str, Any]
    citations: tuple[Citation, ...]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ManualRuleSet":
        """Build a validated manual rule set from dictionary payload."""
        citations = tuple(Citation(**row) for row in payload.get("citations", ()))
        if not citations:
            raise ValueError("citations must be non-empty")
        return cls(
            board_id=str(payload["board_id"]),
            anchor_edition_id=str(payload["anchor_edition_id"]),
            board=dict(payload["board"]),
            economy=dict(payload["economy"]),
            cards=dict(payload["cards"]),
            mechanics=dict(payload["mechanics"]),
            win_condition=dict(payload["win_condition"]),
            citations=citations,
        )
