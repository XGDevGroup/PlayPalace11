"""
Game result dataclass for unified game end handling and statistics.

Provides a structured way to capture game results, enabling:
- Consistent end screen presentation
- Database persistence for statistics
- Helper utilities for leaderboards and ratings
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class PlayerResult(DataClassJSONMixin):
    """Player result in a completed game.

    Attributes:
        player_id: Player UUID.
        player_name: Display name.
        is_bot: True for bot players.
        is_virtual_bot: True for server-level bots (included in stats).
    """

    player_id: str
    player_name: str
    is_bot: bool
    is_virtual_bot: bool = False  # True for server-level virtual bots (include in stats)


@dataclass
class GameResult(DataClassJSONMixin):
    """Structured result of a completed game.

    Game-specific data goes in custom_data for flexibility.
    """

    game_type: str
    timestamp: str  # ISO format
    duration_ticks: int
    player_results: list[PlayerResult] = field(default_factory=list)
    custom_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        game_type: str,
        duration_ticks: int,
        players: list[tuple[str, str, bool]],  # (id, name, is_bot)
        custom_data: dict[str, Any] | None = None,
    ) -> "GameResult":
        """
        Convenience factory for creating a GameResult.

        Args:
            game_type: The game type identifier (e.g., "pig", "farkle")
            duration_ticks: Game duration in ticks
            players: List of (player_id, player_name, is_bot) tuples
            custom_data: Game-specific result data

        Returns:
            A new GameResult instance
        """
        return cls(
            game_type=game_type,
            timestamp=datetime.now().isoformat(),
            duration_ticks=duration_ticks,
            player_results=[
                PlayerResult(player_id=pid, player_name=name, is_bot=is_bot)
                for pid, name, is_bot in players
            ],
            custom_data=custom_data or {},
        )

    def get_duration_seconds(self) -> float:
        """Get game duration in seconds assuming default tick rate."""
        return self.duration_ticks / 20.0

    def get_duration_formatted(self) -> str:
        """Get game duration as a formatted string (e.g., '5:32')."""
        total_seconds = int(self.get_duration_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def get_player_ids(self) -> list[str]:
        """Get list of all player IDs."""
        return [p.player_id for p in self.player_results]

    def get_human_player_ids(self) -> list[str]:
        """Get list of human and virtual bot player IDs (excludes table bots)."""
        return [p.player_id for p in self.player_results if not p.is_bot or p.is_virtual_bot]

    def has_human_players(self) -> bool:
        """Check if any human or virtual bot players participated."""
        return any(not p.is_bot or p.is_virtual_bot for p in self.player_results)
