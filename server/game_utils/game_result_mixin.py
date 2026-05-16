"""Mixin providing game result handling and persistence."""

from typing import TYPE_CHECKING, Any

from .game_status import GameStatus

if TYPE_CHECKING:
    from ..games.base import Player
    from server.core.users.base import User

from .game_result import GameResult, PlayerResult
from .stats_helpers import RatingHelper
from ..messages.localization import Localization
from server.core.users.base import MenuItem


class GameResultMixin:
    """Build, persist, and display game results.

    Expected Game attributes:
        game_active: bool.
        status: str.
        players: list[Player].
        sound_scheduler_tick: int.
        _table: Table or server reference.
        _is_transient_display_open(player) -> bool.
        _close_transient_display(player, rebuild_menu=False).
        get_user(player) -> User | None.
        get_type() -> str.
        get_active_players() -> list[Player].
        destroy().
    """

    def finish_game(self, show_end_screen: bool = True) -> None:
        """Mark the game as finished, persist result, and optionally show end screen.

        Call this instead of setting status directly to ensure proper cleanup.
        If no humans remain, the table is automatically destroyed.

        Args:
            show_end_screen: Whether to show the end screen (default True).
                             Set to False if you want to show it manually.
        """
        self.game_active = False
        self.status = GameStatus.FINISHED

        # Build and persist the game result
        result = self.build_game_result()
        self._last_game_result = result
        self._persist_result(result)

        # Show end screen
        if show_end_screen:
            self._show_end_screen(result)

        # Auto-destroy if no humans remain (bot-only games, but not virtual bot games)
        has_humans = any(not p.is_bot or getattr(p, "is_virtual_bot", False) for p in self.players)
        if not has_humans:
            self.destroy()

    def build_game_result(self) -> GameResult:
        """Build the game result. Override in subclasses for custom data.

        Returns:
            A GameResult with game-specific data in custom_data.
        """
        from datetime import datetime

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot,
                    is_virtual_bot=getattr(p, "is_virtual_bot", False),
                )
                for p in self.get_active_players()
            ],
            custom_data={},
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen lines from a game result. Override for custom display.

        Args:
            result: The game result to format
            locale: The locale to use for localization

        Returns:
            List of lines to display on the end screen
        """
        # Default implementation - just show "Game Over" and player names
        lines = [Localization.get(locale, "game-over")]
        for p in result.player_results:
            lines.append(p.player_name)
        return lines

    def _persist_result(self, result: GameResult) -> None:
        """Persist the game result to the database and update ratings."""
        # Only persist if there are human players
        if not result.has_human_players():
            return

        if self._table:
            self._table.save_game_result(result)
            # Update player ratings
            self._update_ratings(result)

    def _update_ratings(self, result: GameResult) -> None:
        """Update player ratings based on game result."""
        if not self._table or not self._table._db:
            return

        rating_helper = RatingHelper(self._table._db, self.get_type())

        # Get rankings from the result
        rankings = self.get_rankings_for_rating(result)
        if not rankings or len(rankings) < 2:
            # Need at least 2 teams/players to update ratings
            return

        # Update ratings
        rating_helper.update_ratings(rankings)

    def get_rankings_for_rating(self, result: GameResult) -> list[list[str]]:
        """Get player rankings for rating update. Override for custom ranking logic.

        Returns a list of player ID groups ordered by placement.
        First group = 1st place, second = 2nd place, etc.
        Players in same group = tie for that position.

        Default: Winner first, everyone else tied for second.
        """
        winner_name = result.custom_data.get("winner_name")
        # Include humans and virtual bots, exclude table bots
        human_players = [p for p in result.player_results if not p.is_bot or p.is_virtual_bot]

        if not human_players:
            return []

        if winner_name:
            winner_id = None
            others = []
            for p in human_players:
                if p.player_name == winner_name:
                    winner_id = p.player_id
                else:
                    others.append(p.player_id)

            if winner_id:
                if others:
                    return [[winner_id], others]
                return [[winner_id]]

        # No clear winner - everyone ties
        return [[p.player_id for p in human_players]]

    def _show_end_screen(self, result: GameResult) -> None:
        """Show the end screen to all players using structured result."""
        for player in self.players:
            if self._is_transient_display_open(player):
                self._close_transient_display(player, rebuild_menu=False)
            user = self.get_user(player)
            if user:
                lines = self.format_end_screen(result, user.locale)
                items = [MenuItem(text=line, id="score_line") for line in lines]
                # Add Leave button at the end
                items.append(MenuItem(text=Localization.get(user.locale, "game-over-leave"), id="leave_game"))
                user.show_menu("game_over", items, multiletter=False)

    def show_game_end_menu(self, score_lines: list[str]) -> None:
        """Show the game end menu to all players.

        DEPRECATED: Use finish_game() with build_game_result() and format_end_screen()
        instead. This method is kept for backwards compatibility during migration.

        Args:
            score_lines: List of score lines to display
                         (e.g., ["Final Scores:", "1. Alice: 100 points", ...])
        """
        for player in self.players:
            if self._is_transient_display_open(player):
                self._close_transient_display(player, rebuild_menu=False)
            user = self.get_user(player)
            if user:
                items = [MenuItem(text=line, id="score_line") for line in score_lines]
                user.show_menu("game_over", items, multiletter=False)
