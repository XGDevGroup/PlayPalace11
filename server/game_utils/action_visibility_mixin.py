"""Mixin providing action visibility callbacks for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player
    from server.core.users.base import User
    from .teams import TeamManager

from .actions import Visibility
from ..messages.localization import Localization
from server.core.users.base import TrustLevel


class ActionVisibilityMixin:
    """Provide visibility/enable checks for common actions.

    Includes helpers for lobby actions (start/add bot/spectate) and shared
    status actions (scores, actions menu, whose turn).

    Expected Game attributes:
        status: str.
        host: str.
        players: list[Player].
        team_manager: TeamManager.
        get_user(player) -> User | None.
        get_min_players() -> int.
        get_max_players() -> int.
    """

    # Player helper methods

    def _is_player_spectator(self, player: "Player") -> bool:
        """Check if a player is a spectator."""
        return player.is_spectator

    def get_active_players(self) -> list["Player"]:
        """Get list of players who are not spectators (actually playing)."""
        return [p for p in self.players if not p.is_spectator]

    def get_active_player_count(self) -> int:
        """Get the number of active (non-spectator) players."""
        return len(self.get_active_players())

    # --- Lobby actions ---

    def _is_start_game_enabled(self, player: "Player") -> str | None:
        """Check if start_game action is enabled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if player.name != self.host:
            return "action-not-host"
        return None

    def _is_start_game_hidden(self, player: "Player") -> Visibility:
        """Check if start_game action is hidden."""
        if self.status != "waiting":
            return Visibility.HIDDEN
        if player.name != self.host:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_add_bot_enabled(self, player: "Player") -> str | None:
        """Check if add_bot action is enabled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if player.name != self.host:
            return "action-not-host"
        active_count = sum(1 for p in self.players if not p.is_spectator)
        if active_count >= self.get_max_players():
            return "action-table-full"
        return None

    def _is_add_bot_hidden(self, player: "Player") -> Visibility:
        """Add bot is always hidden (F5/keybind only)."""
        return Visibility.HIDDEN

    def _is_remove_bot_enabled(self, player: "Player") -> str | None:
        """Check if remove_bot action is enabled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if player.name != self.host:
            return "action-not-host"
        if not any(p.is_bot for p in self.players):
            return "action-no-bots"
        return None

    def _is_remove_bot_hidden(self, player: "Player") -> Visibility:
        """Remove bot is always hidden (F5/keybind only)."""
        return Visibility.HIDDEN

    def _is_toggle_spectator_enabled(self, player: "Player") -> str | None:
        """Check if toggle_spectator action is enabled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if player.is_bot:
            return "action-bots-cannot"
        return None

    def _is_toggle_spectator_hidden(self, player: "Player") -> Visibility:
        """Toggle spectator is always hidden (F5/keybind only)."""
        return Visibility.HIDDEN

    def _get_toggle_spectator_label(self, player: "Player", action_id: str) -> str:
        """Get dynamic label for toggle_spectator action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if player.is_spectator:
            return Localization.get(locale, "play")
        return Localization.get(locale, "spectate")

    def _is_leave_game_enabled(self, player: "Player") -> str | None:
        """Leave game is always enabled."""
        return None

    def _is_leave_game_hidden(self, player: "Player") -> Visibility:
        """Leave game is always hidden (F5/keybind only)."""
        return Visibility.HIDDEN

    # --- Option actions ---

    def _is_option_enabled(self, player: "Player") -> str | None:
        """Check if option actions are enabled (waiting state, host only)."""
        if self.status != "waiting":
            return "action-game-in-progress"
        if player.name != self.host:
            return "action-not-host"
        return None

    def _is_option_hidden(self, player: "Player") -> Visibility:
        """Options are visible in waiting state for the host only."""
        if self.status != "waiting":
            return Visibility.HIDDEN
        if player.name != self.host:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # --- Estimate actions ---

    def _is_estimate_duration_enabled(self, player: "Player") -> str | None:
        """Check if estimate_duration action is enabled."""
        if self.status != "waiting":
            return "action-game-in-progress"
        user = self.get_user(player)
        if not user or user.trust_level.value < TrustLevel.ADMIN.value:
            return "action-not-available"
        return None

    def _is_estimate_duration_hidden(self, player: "Player") -> Visibility:
        """Estimate duration is visible in waiting state."""
        if self.status != "waiting":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if not user or user.trust_level.value < TrustLevel.ADMIN.value:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # --- Standard actions ---

    def _is_show_actions_enabled(self, player: "Player") -> str | None:
        """Show actions menu is always enabled."""
        return None

    def _is_show_actions_hidden(self, player: "Player") -> Visibility:
        """Show actions is hidden for players but visible to spectators."""
        if player.is_spectator:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_always_hidden(self, player: "Player") -> Visibility:
        """Always hide an action from menus (keybind only)."""
        return Visibility.HIDDEN

    def _is_always_disabled(self, player: "Player") -> str | None:
        """Always disable an action (used with keep_visible_when_disabled)."""
        return "action-locked"

    def _is_save_table_enabled(self, player: "Player") -> str | None:
        """Check if save_table action is enabled."""
        if player.name != self.host:
            return "action-not-host"
        return None

    def _is_save_table_hidden(self, player: "Player") -> Visibility:
        """Save table is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_whose_turn_enabled(self, player: "Player") -> str | None:
        """Check if whose_turn action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Whose turn is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_whos_at_table_enabled(self, player: "Player") -> str | None:
        """Check if whos_at_table action is enabled."""
        return None

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Whos at table is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_check_scores_enabled(self, player: "Player") -> str | None:
        """Check if check_scores action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if len(self.team_manager.teams) == 0:
            return "action-no-scores"
        return None

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        """Check scores is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_check_scores_detailed_enabled(self, player: "Player") -> str | None:
        """Check if check_scores_detailed action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if len(self.team_manager.teams) == 0:
            return "action-no-scores"
        return None

    def _is_check_scores_detailed_hidden(self, player: "Player") -> Visibility:
        """Check scores detailed is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_check_game_options_enabled(self, player: "Player") -> str | None:
        """Check if readonly game options are available."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_game_options_hidden(self, player: "Player") -> Visibility:
        """Readonly game options are hidden from the turn menu (keybind/actions menu only)."""
        return Visibility.HIDDEN

    def _is_predict_outcomes_enabled(self, player: "Player") -> str | None:
        """Check if predict_outcomes action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        # Need at least 2 human players for meaningful predictions
        human_count = sum(1 for p in self.players if not p.is_bot and not p.is_spectator)
        if human_count < 2:
            return "action-need-more-humans"
        return None

    def _is_predict_outcomes_hidden(self, player: "Player") -> Visibility:
        """Predict outcomes is always hidden (keybind only)."""
        return Visibility.HIDDEN
