"""Deterministic anchor-backed City engine for Monopoly City preset."""

from __future__ import annotations

from dataclasses import dataclass, field

from .city_profile import CityProfile


@dataclass(frozen=True)
class CityOutcome:
    """Outcome payload returned by City engine hooks."""

    status: str = "allow"
    cash_delta: int = 0
    message_key: str = ""
    reason_code: str = ""


@dataclass
class CityEngine:
    """Deterministic City rule evaluator shared by MonopolyGame hooks."""

    profile: CityProfile
    current_turn_player_id: str | None = None
    current_turn_index: int = -1
    _progress_by_player_id: dict[str, int] = field(default_factory=dict)

    def on_turn_start(self, player_id: str, turn_index: int) -> None:
        """Set the active turn pointer for deterministic City processing."""
        self.current_turn_player_id = player_id
        self.current_turn_index = turn_index
        self._progress_by_player_id.setdefault(player_id, 0)

    def record_progress(self, player_id: str, progress_delta: int) -> int:
        """Record City progress points and return updated total for player."""
        current = self._progress_by_player_id.get(player_id, 0)
        next_value = current + max(0, progress_delta)
        self._progress_by_player_id[player_id] = next_value
        return next_value

    def progress_for(self, player_id: str) -> int:
        """Return tracked City progress for a player."""
        return self._progress_by_player_id.get(player_id, 0)

    def evaluate_winner(self, contender_ids: tuple[str, ...] | list[str]) -> str | None:
        """Evaluate winner from contender ids using profile threshold + deterministic tie-break."""
        contenders = list(contender_ids)
        if not contenders:
            return None

        threshold = self.profile.win_threshold
        if threshold > 0:
            eligible = [
                player_id
                for player_id in contenders
                if self._progress_by_player_id.get(player_id, 0) >= threshold
            ]
            if not eligible:
                return None
            contenders = eligible

        best_player: str | None = None
        best_score = -1
        for player_id in contenders:
            # Untracked players rank below tracked players when threshold is not enforced.
            score = self._progress_by_player_id.get(player_id, -1)
            if score > best_score:
                best_score = score
                best_player = player_id

        return best_player

    def evaluate_richest(self, contender_ids: tuple[str, ...] | list[str], totals: dict[str, int]) -> str | None:
        """Return richest contender id by provided final-value totals."""
        contenders = list(contender_ids)
        if not contenders:
            return None

        best_player: str | None = None
        best_total = -1
        for player_id in contenders:
            total = totals.get(player_id, 0)
            if total > best_total:
                best_total = total
                best_player = player_id

        return best_player
