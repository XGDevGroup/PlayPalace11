"""Mixin for games structured as rounds of sequential player turns."""

from __future__ import annotations

from typing import ClassVar

from server.game_utils.game_status import GameStatus


class RoundBasedGameMixin:
    """Shared lifecycle for round-based turn-taking games.

    Provides default implementations for:
        - on_start(): Initialize game state and start first round.
        - _start_round(): Increment round counter, reset turn order, announce.
        - _start_turn(): Reset player state, announce turn, set up bots, rebuild menus.
        - _on_turn_end(): Advance to next player or end round.

    Games override hooks to customize behavior:
        - get_team_mode(): Return team mode string (default "individual").
        - should_reset_all_scores(): Whether to reset TeamManager scores on start.
        - _reset_player_for_game(player): Per-player init at game start.
        - _reset_player_for_round(player): Per-player init at round start.
        - _reset_player_for_turn(player): Per-player init at turn start.
        - _announce_turn_start(player): Custom turn announcement.
        - _setup_bot_for_turn(player): Bot initialization at turn start.

    Games MUST implement:
        - _on_round_end(): Handle end of a round (too divergent to share).
    """

    round_start_sound: ClassVar[str | None] = "game_pig/roundstart.ogg"
    game_music: ClassVar[str] = "game_pig/mus.ogg"

    # ------------------------------------------------------------------
    # Configuration hooks (override in subclasses)
    # ------------------------------------------------------------------

    def get_team_mode(self) -> str:
        """Return the team mode string. Default: "individual"."""
        return "individual"

    def should_reset_all_scores(self) -> bool:
        """Return True to reset TeamManager scores on game start."""
        return False

    def _reset_player_for_game(self, player) -> None:
        """Reset per-player state at game start. Override in each game."""

    def _reset_player_for_round(self, player) -> None:
        """Reset per-player state at round start. Default: no-op."""

    def _reset_player_for_turn(self, player) -> None:
        """Reset per-player state at turn start. Override in each game."""

    def _announce_turn_start(self, player) -> None:
        """Announce the start of a player's turn. Default: announce_turn()."""
        self.announce_turn()

    def _setup_bot_for_turn(self, player) -> None:
        """Set up bot AI for the current turn. Default: no-op."""

    def _on_round_end(self) -> None:
        """Handle end of a round. Must be implemented by each game."""
        raise NotImplementedError("Games must implement _on_round_end()")

    # ------------------------------------------------------------------
    # Default implementations
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        """Initialize game state and start first round."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 0

        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        self._team_manager.team_mode = self.get_team_mode()
        self._team_manager.setup_teams([p.name for p in active_players])

        if self.should_reset_all_scores():
            self._team_manager.reset_all_scores()

        for player in active_players:
            self._reset_player_for_game(player)

        self.play_music(self.game_music)
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1
        self.set_turn_players(self.get_active_players())

        if self.round_start_sound:
            self.play_sound(self.round_start_sound)

        self.broadcast_l("game-round-start", round=self.round)

        for player in self.get_active_players():
            self._reset_player_for_round(player)

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        self._reset_player_for_turn(player)
        self._announce_turn_start(player)
        self._setup_bot_for_turn(player)
        self.rebuild_all_menus()

    def _on_turn_end(self) -> None:
        """Advance to next player or trigger round end."""
        if self.turn_index >= len(self.turn_players) - 1:
            self._on_round_end()
        else:
            self.advance_turn(announce=False)
            self._start_turn()


__all__ = ["RoundBasedGameMixin"]
