"""Mixin providing action set creation for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player

from .actions import Action, ActionSet, EditboxInput
from ..messages.localization import Localization
from server.core.ui.keybinds import Keybind, KeybindState


class ActionSetCreationMixin:
    """Create standard/lobby action sets and define keybinds.

    Games override `create_turn_action_set` to define turn-specific actions.
    This mixin also defines the global keybinds used across games.

    Expected Game attributes:
        players: list[Player].
        player_action_sets: dict[str, list[ActionSet]].
        _keybinds: dict[str, list[Keybind]].
        get_user(player) -> User | None.
        add_action_set(player, action_set).
    """

    def create_lobby_action_set(self, player: "Player") -> ActionSet:
        """Create the lobby action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="lobby")
        action_set.add(
            Action(
                id="start_game",
                label=Localization.get(locale, "start-game"),
                handler="_action_start_game",
                is_enabled="_is_start_game_enabled",
                is_hidden="_is_start_game_hidden",
            )
        )
        action_set.add(
            Action(
                id="add_bot",
                label=Localization.get(locale, "add-bot"),
                handler="_action_add_bot",
                is_enabled="_is_add_bot_enabled",
                is_hidden="_is_add_bot_hidden",
                input_request=EditboxInput(
                    prompt="enter-bot-name",
                    default="",
                    bot_input="_bot_input_add_bot",
                ),
            )
        )
        action_set.add(
            Action(
                id="remove_bot",
                label=Localization.get(locale, "remove-bot"),
                handler="_action_remove_bot",
                is_enabled="_is_remove_bot_enabled",
                is_hidden="_is_remove_bot_hidden",
            )
        )
        action_set.add(
            Action(
                id="toggle_spectator",
                label=Localization.get(locale, "spectate"),
                handler="_action_toggle_spectator",
                is_enabled="_is_toggle_spectator_enabled",
                is_hidden="_is_toggle_spectator_hidden",
                get_label="_get_toggle_spectator_label",
            )
        )
        return action_set

    def create_estimate_action_set(self, player: "Player") -> ActionSet:
        """Create the estimate duration action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="estimate")
        action_set.add(
            Action(
                id="estimate_duration",
                label=Localization.get(locale, "estimate-duration"),
                handler="_action_estimate_duration",
                is_enabled="_is_estimate_duration_enabled",
                is_hidden="_is_estimate_duration_hidden",
            )
        )
        return action_set

    def create_standard_action_set(self, player: "Player") -> ActionSet:
        """Create the standard action set (F5, save) for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="standard")
        action_set.add(
            Action(
                id="show_actions",
                label=Localization.get(locale, "actions-menu"),
                handler="_action_show_actions_menu",
                is_enabled="_is_always_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="show_rules",
                label=Localization.get(locale, "show-rules"),
                handler="_action_show_rules",
                is_enabled="_is_always_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=True,
            )
        )
        action_set.add(
            Action(
                id="save_table",
                label=Localization.get(locale, "save-table"),
                handler="_action_save_table",
                is_enabled="_is_save_table_enabled",
                is_hidden="_is_save_table_hidden",
            )
        )

        # Common status actions (available during play)
        action_set.add(
            Action(
                id="whose_turn",
                label=Localization.get(locale, "whose-turn"),
                handler="_action_whose_turn",
                is_enabled="_is_whose_turn_enabled",
                is_hidden="_is_whose_turn_hidden",
            )
        )
        action_set.add(
            Action(
                id="whos_at_table",
                label=Localization.get(locale, "whos-at-table"),
                handler="_action_whos_at_table",
                is_enabled="_is_whos_at_table_enabled",
                is_hidden="_is_whos_at_table_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_scores",
                label=Localization.get(locale, "check-scores"),
                handler="_action_check_scores",
                is_enabled="_is_check_scores_enabled",
                is_hidden="_is_check_scores_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_scores_detailed",
                label=Localization.get(locale, "check-scores-detailed"),
                handler="_action_check_scores_detailed",
                is_enabled="_is_check_scores_detailed_enabled",
                is_hidden="_is_check_scores_detailed_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_game_options",
                label=Localization.get(locale, "check-game-options"),
                handler="_action_check_game_options",
                is_enabled="_is_check_game_options_enabled",
                is_hidden="_is_check_game_options_hidden",
            )
        )
        action_set.add(
            Action(
                id="predict_outcomes",
                label=Localization.get(locale, "predict-outcomes"),
                handler="_action_predict_outcomes",
                is_enabled="_is_predict_outcomes_enabled",
                is_hidden="_is_predict_outcomes_hidden",
            )
        )
        action_set.add(
            Action(
                id="leave_game",
                label=Localization.get(locale, "leave-table"),
                handler="_action_leave_game",
                is_enabled="_is_always_enabled",
                is_hidden="_is_leave_game_hidden",
            )
        )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        # Lobby keybinds
        self.define_keybind(
            "enter",
            "Start game",
            ["start_game"],
            state=KeybindState.IDLE,
            include_spectators=True,
        )
        self.define_keybind(
            "b",
            "Add bot",
            ["add_bot"],
            state=KeybindState.IDLE,
            include_spectators=True,
        )
        self.define_keybind(
            "shift+b",
            "Remove bot",
            ["remove_bot"],
            state=KeybindState.IDLE,
            include_spectators=True,
        )
        self.define_keybind(
            "f3",
            "Toggle spectator",
            ["toggle_spectator"],
            state=KeybindState.IDLE,
            include_spectators=True,
        )
        self.define_keybind(
            "ctrl+q",
            "Leave table",
            ["leave_game"],
            state=KeybindState.ALWAYS,
            include_spectators=True,
        )
        # Standard keybinds
        self.define_keybind(
            "f1",
            "Show rules",
            ["show_rules"],
            state=KeybindState.ALWAYS,
            include_spectators=True,
        )
        self.define_keybind(
            "escape",
            "Actions menu",
            ["show_actions"],
            state=KeybindState.ALWAYS,
            include_spectators=True,
        )
        self.define_keybind(
            "ctrl+e",
            "Estimate duration",
            ["estimate_duration"],
            state=KeybindState.IDLE,
            players=[self.host],
            include_spectators=True,
        )
        self.define_keybind("ctrl+s", "Save table", ["save_table"], state=KeybindState.ALWAYS)

        # Status keybinds (during play)
        self.define_keybind(
            "t",
            "Whose turn",
            ["whose_turn"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "ctrl+w",
            "Who's at the table",
            ["whos_at_table"],
            state=KeybindState.ALWAYS,
            include_spectators=True,
        )
        self.define_keybind(
            "s",
            "Check scores",
            ["check_scores"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "shift+s",
            "Detailed scores",
            ["check_scores_detailed"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "alt+o",
            "Check game options",
            ["check_game_options"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "ctrl+r",
            "Predict outcomes",
            ["predict_outcomes"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def create_turn_action_set(self, player: "Player") -> ActionSet | None:
        """Create the turn action set for a player.

        Override in subclasses to add game-specific turn actions.
        Returns None by default (no turn actions).
        """
        return None

    def setup_player_actions(self, player: "Player") -> None:
        """Set up action sets for a player. Called when player joins."""
        # Create and add action sets in order (first = appears first in menu)
        # Turn actions first (if any), then lobby, options, standard
        turn_set = self.create_turn_action_set(player)
        if turn_set:
            self.add_action_set(player, turn_set)

        lobby_set = self.create_lobby_action_set(player)
        self.add_action_set(player, lobby_set)

        # Only add options if the game defines them
        if hasattr(self, "options"):
            options_set = self.create_options_action_set(player)
            self.add_action_set(player, options_set)

        # Add estimate action set (after options)
        estimate_set = self.create_estimate_action_set(player)
        self.add_action_set(player, estimate_set)

        standard_set = self.create_standard_action_set(player)
        self.add_action_set(player, standard_set)

    # Keybind management

    def define_keybind(
        self,
        key: str,
        name: str,
        actions: list[str],
        *,
        requires_focus: bool = False,
        state: KeybindState = KeybindState.ALWAYS,
        players: list[str] | None = None,
        include_spectators: bool = False,
    ) -> None:
        """
        Define a keybind that triggers one or more actions.

        Args:
            key: The key combination (e.g., "space", "shift+b", "f5")
            name: Human-readable name for the keybind (e.g., "Roll dice")
            actions: List of action IDs this keybind triggers
            requires_focus: If True, must be focused on a valid menu item
            state: When the keybind is active (NEVER, IDLE, ACTIVE, ALWAYS)
            players: List of player names who can use (empty/None = all)
            include_spectators: Whether spectators can use this keybind
        """
        keybind = Keybind(
            name=name,
            default_key=key,
            actions=actions,
            requires_focus=requires_focus,
            state=state,
            players=players or [],
            include_spectators=include_spectators,
        )
        if key not in self._keybinds:
            self._keybinds[key] = []
        self._keybinds[key].append(keybind)

    def _get_keybind_for_action(self, action_id: str) -> str | None:
        """Get the keybind string for an action, if any."""
        for key, keybinds in self._keybinds.items():
            for keybind in keybinds:
                if action_id in keybind.actions:
                    return key
        return None
