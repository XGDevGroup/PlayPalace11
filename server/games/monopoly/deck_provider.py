"""Deck provider abstraction for board-specific card pipelines."""

from __future__ import annotations

from dataclasses import dataclass


VALID_DECK_MODES: tuple[str, ...] = ("classic", "board_specific")


@dataclass(frozen=True)
class DeckProvider:
    """Resolved deck provider for one board."""

    board_id: str
    mode: str


def resolve_deck_provider(board_id: str, deck_mode: str) -> DeckProvider:
    """Resolve normalized deck provider mode for a board."""
    mode = deck_mode if deck_mode in VALID_DECK_MODES else "classic"
    return DeckProvider(board_id=board_id, mode=mode)
