"""Mixin providing lobby action handlers for games."""

from typing import TYPE_CHECKING, Any

from .game_status import GameStatus

if TYPE_CHECKING:
    from ..games.base import Player
    from server.core.users.base import User
    from .actions import ResolvedAction

from server.core.users.base import MenuItem, EscapeBehavior
from server.core.users.bot import Bot
from ..messages.localization import Localization


# Default bot names available for selection
BOT_NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "Diana",
    "Eve",
    "Frank",
    "Grace",
    "Henry",
    "Ivy",
    "Jack",
    "Kate",
    "Leo",
    "Mia",
    "Noah",
    "Olivia",
    "Pete",
    "Quinn",
    "Rose",
    "Sam",
    "Tina",
    "Uma",
    "Vic",
    "Wendy",
    "Xander",
    "Yara",
    "Zack",
]


class LobbyActionsMixin:
    """Handle lobby actions and player lifecycle management.

    Expected Game attributes:
        status: str.
        host: str.
        players: list[Player].
        _table: Table reference.
        _users: dict.
        _destroyed: bool.
        _actions_menu_open: set[str].
        player_action_sets: dict.
        get_user(player) -> User | None.
        broadcast_l(), broadcast_sound().
        prestart_validate(), on_start().
        attach_user(), rebuild_all_menus().
        get_all_enabled_actions().
        _get_keybind_for_action().
        setup_keybinds(), setup_player_actions().
    """

    def _action_start_game(self, player: "Player", action_id: str) -> None:
        """Start the game."""
        # Validate configuration before starting
        errors = self.prestart_validate()
        if errors:
            for error in errors:
                # Handle both plain strings and (key, kwargs) tuples
                if isinstance(error, tuple):
                    error_key, kwargs = error
                    self.broadcast_l(error_key, buffer="table", **kwargs)
                else:
                    self.broadcast_l(error, buffer="table")
            return

        # Announce game is starting
        self.broadcast_l("game-starting")

        # Start the game (subclasses implement this)
        self.on_start()
        self.validate_actions()

    def _bot_input_add_bot(self, player: "Player") -> str | None:
        """Get bot name for add_bot action."""
        return next(
            (n for n in BOT_NAMES if n.lower() not in {x.name.lower() for x in self.players}),
            None,
        )

    def _action_add_bot(self, player: "Player", bot_name: str, action_id: str) -> None:
        """Add a bot with the selected name."""
        # If blank, use an available name from the list
        if not bot_name.strip():
            bot_name = next(
                (n for n in BOT_NAMES if n.lower() not in {x.name.lower() for x in self.players}),
                None,
            )
            if not bot_name:
                # No names available
                user = self.get_user(player)
                if user:
                    user.speak_l("no-bot-names-available")
                return

        bot_user = Bot(bot_name)
        bot_player = self.create_player(bot_user.uuid, bot_name, is_bot=True)
        self.players.append(bot_player)
        self.attach_user(bot_player.id, bot_user)
        # Set up action sets for the bot
        self.setup_player_actions(bot_player)
        self.broadcast_l("table-joined", player=bot_name)
        self.broadcast_sound("join.ogg")
        self.rebuild_all_menus()

    def _action_remove_bot(self, player: "Player", action_id: str) -> None:
        """Remove the last bot from the game."""
        for i in range(len(self.players) - 1, -1, -1):
            if self.players[i].is_bot:
                bot = self.players.pop(i)
                # Clean up action sets
                self.player_action_sets.pop(bot.id, None)
                self._users.pop(bot.id, None)
                self.broadcast_l("table-left", player=bot.name)
                self.broadcast_sound("leave.ogg")
                break
        self.rebuild_all_menus()

    def _action_toggle_spectator(self, player: "Player", action_id: str) -> None:
        """Toggle spectator mode for a player."""
        if self.status != "waiting":
            return  # Can only toggle before game starts

        player.is_spectator = not player.is_spectator
        if player.is_spectator:
            self.broadcast_l("now-spectating", player=player.name)
            self.broadcast_sound("join_spectator.ogg")
        else:
            self.broadcast_l("now-playing", player=player.name)
            self.broadcast_sound("leave_spectator.ogg")

        self.rebuild_all_menus()

    def _action_leave_game(self, player: "Player", action_id: str) -> None:
        """Prompt for confirmation before leaving the game."""
        user = self.get_user(player)
        if not user:
            return
        self._pending_actions[player.id] = "leave_game_confirm"
        user.speak_l("confirm-leave-game")
        items = [
            MenuItem(text=Localization.get(user.locale, "confirm-no"), id="no"),
            MenuItem(text=Localization.get(user.locale, "confirm-yes"), id="yes"),
        ]
        user.show_menu(
            "leave_game_confirm",
            items,
            multiletter=False,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )

    def _perform_leave_game(self, player: "Player") -> None:
        """Leave the game."""
        # Spectators can always leave cleanly (no bot replacement)
        if player.is_spectator:
            self.players = [p for p in self.players if p.id != player.id]
            self.player_action_sets.pop(player.id, None)
            self._users.pop(player.id, None)
            self.broadcast_l("spectator-left", player=player.name)
            self.broadcast_sound("leave_spectator.ogg")
            self.rebuild_all_menus()
            return

        if self.status == "playing" and not player.is_bot:
            # Mid-game: replace human with bot instead of removing
            # Keep the same player ID so they can rejoin and take over
            player.is_bot = True
            self._users.pop(player.id, None)

            # Create a bot user with the same UUID to control this player
            bot_user = Bot(player.name, uuid=player.id)
            self.attach_user(player.id, bot_user)

            self.broadcast_l("player-replaced-by-bot", player=player.name)
            self.broadcast_sound("leave.ogg")

            # Check if any humans remain
            has_humans = any(not p.is_bot for p in self.players)
            if not has_humans:
                # Destroy the game - no humans left
                self.destroy()
                return

                # Rebuild menus for remaining players
                self.rebuild_all_menus()
            return

        # Lobby or bot leaving: fully remove the player
        self.players = [p for p in self.players if p.id != player.id]
        self.player_action_sets.pop(player.id, None)
        self._users.pop(player.id, None)

        self.broadcast_l("table-left", player=player.name)
        self.broadcast_sound("leave.ogg")

        # Check if any humans remain
        has_humans = any(not p.is_bot for p in self.players)
        if not has_humans:
            # Destroy the game - no humans left
            self.destroy()
            return

        if self.status == "waiting":
            # If host left, assign new host
            if player.name == self.host and self.players:
                # Find first human to be new host
                for p in self.players:
                    if not p.is_bot:
                        self.host = p.name
                        self.broadcast_l("new-host", player=p.name)
                        break

            self.rebuild_all_menus()

    def _action_show_actions_menu(self, player: "Player", action_id: str) -> None:
        """Show the actions menu."""
        items = []
        for resolved in self.get_all_enabled_actions(player):
            label = resolved.label
            keybind_key = self._get_keybind_for_action(resolved.action.id)
            if keybind_key:
                label += f" ({keybind_key.upper()})"
            items.append(MenuItem(text=label, id=resolved.action.id))

        user = self.get_user(player)
        if user and items:
            # Add "Go back" option at the end
            items.append(MenuItem(text=Localization.get(user.locale, "back"), id="go_back"))
            self._actions_menu_open.add(player.id)
            user.speak_l("context-menu")
            user.show_menu(
                "actions_menu",
                items,
                multiletter=True,
                escape_behavior=EscapeBehavior.SELECT_LAST,
            )
        elif user:
            user.speak_l("no-actions-available")

    def _action_save_table(self, player: "Player", action_id: str) -> None:
        """Save the current table state (host only). This destroys the table."""
        if self._table:
            self._table.save_and_close(player.name)

    # Game lifecycle

    def destroy(self) -> None:
        """Request destruction of this game/table."""
        self._destroyed = True
        if self._table:
            self._table.destroy()

    def initialize_lobby(self, host_name: str, host_user: "User") -> None:
        """Initialize the game in lobby mode with a host."""
        self.host = host_name
        self.status = GameStatus.WAITING
        self.setup_keybinds()
        self.add_player(host_name, host_user)
        if hasattr(self, "_reset_transcripts"):
            self._reset_transcripts()
        self.rebuild_all_menus()

    # Player management

    def get_human_count(self) -> int:
        """Get the number of human players."""
        return sum(1 for p in self.players if not p.is_bot)

    def get_bot_count(self) -> int:
        """Get the number of bot players."""
        return sum(1 for p in self.players if p.is_bot)

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> "Player":
        """Create a new player. Override in subclasses for custom player types."""
        # Import here to avoid circular dependency at module level
        from ..games.base import Player

        return Player(id=player_id, name=name, is_bot=is_bot)

    def add_player(self, name: str, user: "User") -> "Player":
        """Add a player to the game."""
        is_bot = user.is_bot
        is_virtual_bot = getattr(user, "is_virtual_bot", False)
        player = self.create_player(user.uuid, name, is_bot=is_bot)
        player.is_virtual_bot = is_virtual_bot
        self.players.append(player)
        self.attach_user(player.id, user)
        # Set up action sets for the new player
        self.setup_player_actions(player)
        if hasattr(self, "_transcripts"):
            self._transcripts.setdefault(player.id, [])
        return player

    def add_spectator(self, name: str, user: "User") -> "Player":
        """Add a spectator to the game."""
        player = self.create_player(user.uuid, name, is_bot=False)
        player.is_spectator = True
        self.players.append(player)
        self.attach_user(player.id, user)
        self.setup_player_actions(player)
        if hasattr(self, "_transcripts"):
            self._transcripts.setdefault(player.id, [])
        return player
