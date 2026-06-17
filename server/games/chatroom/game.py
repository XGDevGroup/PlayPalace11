"""Chat Room game for PlayPalace v11.

A non-competitive chat room where players can socialize.
No gameplay, no bots, just conversation with an optional topic.
"""

from dataclasses import dataclass, field

from ..base import Game, Player
from ..registry import register_game
from ...messages.localization import Localization
from ...game_utils.actions import Action, ActionSet
from ...game_utils.game_result import GameResult
from ...core.ui.keybinds import KeybindState


@dataclass
class ChatRoomPlayer(Player):
    """A player in a chat room (no game-specific state needed)."""


@dataclass
@register_game
class ChatRoomGame(Game):
    """
    Chat Room - a social space with no gameplay.

    Players can join freely and chat. The host can set a topic
    visible to everyone browsing active tables.
    """

    players: list[ChatRoomPlayer] = field(default_factory=list)

    @classmethod
    def get_name(cls) -> str:
        return "Chat Room"

    @classmethod
    def get_type(cls) -> str:
        return "chatroom"

    @classmethod
    def get_category(cls) -> str:
        return "category-uncategorized"

    @classmethod
    def get_min_players(cls) -> int:
        return 1

    @classmethod
    def get_max_players(cls) -> int:
        return 999

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> ChatRoomPlayer:
        return ChatRoomPlayer(id=player_id, name=name, is_bot=is_bot)

    def on_start(self) -> None:
        """Chat rooms never start a game - this is a no-op."""
        pass

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()

    def on_game_event(self, event_type: str, data: dict) -> None:
        """No scheduled events in chat rooms."""

    def build_game_result(self) -> GameResult:
        """Chat rooms don't produce game results."""
        return GameResult(
            game_type=self.get_type(),
            timestamp="",
            duration_ticks=0,
            player_results=[],
            custom_data={},
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        return []

    # --- Visibility overrides: hide gameplay actions ---

    def _is_start_game_hidden(self, player):
        from ...game_utils.actions import Visibility
        return Visibility.HIDDEN

    def _is_start_game_enabled(self, player):
        return "action-not-available"

    def _is_add_bot_hidden(self, player):
        from ...game_utils.actions import Visibility
        return Visibility.HIDDEN

    def _is_add_bot_enabled(self, player):
        return "action-not-available"

    def _is_remove_bot_hidden(self, player):
        from ...game_utils.actions import Visibility
        return Visibility.HIDDEN

    def _is_remove_bot_enabled(self, player):
        return "action-not-available"

    def _is_estimate_duration_hidden(self, player):
        from ...game_utils.actions import Visibility
        return Visibility.HIDDEN

    def _is_estimate_duration_enabled(self, player):
        return "action-not-available"

    # --- Keybind / action setup ---

    def setup_keybinds(self) -> None:
        """Define keybinds for chat rooms (no gameplay keybinds)."""
        self.define_keybind(
            "alt+t",
            "Table topic",
            ["table_topic"],
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
            "ctrl+q",
            "Leave table",
            ["leave_game"],
            state=KeybindState.ALWAYS,
            include_spectators=True,
        )
        self.define_keybind(
            "ctrl+w",
            "Who's at the table",
            ["whos_at_table"],
            state=KeybindState.ALWAYS,
            include_spectators=True,
        )

    def create_lobby_action_set(self, player):
        """Create lobby action set without bot/gameplay actions."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="lobby")
        action_set.add(
            Action(
                id="table_topic",
                label=Localization.get(locale, "chatroom-table-topic-action"),
                handler="_action_table_topic",
                is_enabled="",
                is_hidden="",
            )
        )
        return action_set

    def create_standard_action_set(self, player):
        """Create standard action set without gameplay status actions."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="standard")
        action_set.add(
            Action(
                id="show_actions",
                label=Localization.get(locale, "actions-menu"),
                handler="_action_show_actions_menu",
                is_enabled="_is_show_actions_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
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
                id="leave_game",
                label=Localization.get(locale, "leave-table"),
                handler="_action_leave_game",
                is_enabled="_is_leave_game_enabled",
                is_hidden="_is_leave_game_hidden",
            )
        )
        return action_set

    def _action_table_topic(self, player, action_id):
        """Handle table topic keybind/action."""
        user = self.get_user(player)
        if not user:
            return

        if player.name == self.host:
            # Host can set the topic
            self._pending_actions[player.id] = "table_topic_set"
            current = self._table.topic if self._table else ""
            user.show_editbox("action_input_editbox",
                Localization.get(user.locale, "chatroom-topic-prompt"),
                current)
        else:
            # Non-host views the topic
            topic = self._table.topic if self._table else ""
            if topic:
                user.speak_l("chatroom-topic", topic=topic)
            else:
                user.speak_l("chatroom-no-topic")

    def execute_action(self, player, action_id, input_value=None, context=None):
        """Override to handle table_topic_set action (editbox submission)."""
        if action_id == "table_topic_set" and input_value is not None:
            self._set_table_topic(player, input_value)
            return
        super().execute_action(player, action_id, input_value, context)

    def _set_table_topic(self, player, text):
        """Set the table topic."""
        if not self._table:
            return
        if player.name != self.host:
            return
        if text:
            self._table.topic = text
            self.broadcast_l("chatroom-topic-set", player=player.name, topic=text)
        else:
            self._table.topic = ""
            self.broadcast_l("chatroom-topic-cleared", player=player.name)
