import uuid
from types import SimpleNamespace

import pytest

from server.game_utils.lobby_actions_mixin import LobbyActionsMixin, BOT_NAMES
from server.game_utils.actions import Action, ResolvedAction
from server.core.users.base import MenuItem, EscapeBehavior
from server.games.base import Player
from server.messages.localization import Localization


class StubUser:
    def __init__(self, name: str, locale: str = "en"):
        self.name = name
        self.locale = locale
        self.uuid = str(uuid.uuid4())
        self.is_bot = False
        self.is_virtual_bot = False
        self.spoken: list[tuple[str, str, dict]] = []
        self.menus: list[dict] = []
        self.sounds: list[str] = []

    def speak(self, text: str, buffer: str = "misc") -> None:
        self.spoken.append(("speak", text, {"buffer": buffer}))

    def speak_l(self, key: str, buffer: str = "misc", **kwargs) -> None:
        self.spoken.append(("speak_l", key, {"buffer": buffer, **kwargs}))

    def show_menu(
        self,
        menu_id: str,
        items: list[MenuItem | str],
        *,
        multiletter: bool = True,
        escape_behavior: EscapeBehavior = EscapeBehavior.KEYBIND,
        position: int | None = None,
        grid_enabled: bool = False,
        grid_width: int = 1,
    ) -> None:
        self.menus.append(
            {
                "menu_id": menu_id,
                "items": items,
                "multiletter": multiletter,
                "escape_behavior": escape_behavior,
                "position": position,
                "grid_enabled": grid_enabled,
                "grid_width": grid_width,
            }
        )

    def play_sound(self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100) -> None:
        self.sounds.append(name)


class TableMock:
    def __init__(self):
        self.saved_with: list[str] = []
        self.destroyed = False

    def save_and_close(self, player_name: str) -> None:
        self.saved_with.append(player_name)

    def destroy(self) -> None:
        self.destroyed = True


class DummyLobbyGame(LobbyActionsMixin):
    def __init__(self):
        self.status = "waiting"
        self.host = ""
        self.players: list[Player] = []
        self._table = TableMock()
        self._users: dict[str, StubUser] = {}
        self._destroyed = False
        self._actions_menu_open: set[str] = set()
        self.player_action_sets: dict[str, list] = {}
        self._pending_actions: dict[str, str] = {}
        self.enabled_actions: list[ResolvedAction] = []
        self.keybinds: dict[str, str] = {}
        self.broadcasts: list[tuple[str, dict]] = []
        self.broadcast_sounds: list[str] = []
        self.rebuild_count = 0
        self.setup_player_actions_calls: list[str] = []
        self.attached_users: list[tuple[str, StubUser]] = []
        self.on_start_called = False
        self._prestart_errors: list = []
        self._keybinds: dict = {}

    # Helpers expected by mixin -------------------------------------------------
    def prestart_validate(self):
        return list(self._prestart_errors)

    def on_start(self):
        self.on_start_called = True

    def validate_actions(self):
        pass

    def create_player(self, player_uuid: str, name: str, is_bot: bool = False):
        return Player(id=player_uuid, name=name, is_bot=is_bot)

    def attach_user(self, player_id: str, user: StubUser) -> None:
        self._users[player_id] = user
        self.attached_users.append((player_id, user))

    def setup_player_actions(self, player: Player) -> None:
        self.setup_player_actions_calls.append(player.id)

    def rebuild_all_menus(self) -> None:
        self.rebuild_count += 1

    def broadcast_l(self, key: str, **kwargs) -> None:
        self.broadcasts.append((key, kwargs))

    def broadcast_sound(self, name: str) -> None:
        self.broadcast_sounds.append(name)

    def get_user(self, player: Player) -> StubUser | None:
        return self._users.get(player.id)

    def get_all_enabled_actions(self, player: Player) -> list[ResolvedAction]:
        return list(self.enabled_actions)

    def _get_keybind_for_action(self, action_id: str) -> str | None:
        return self.keybinds.get(action_id)

    def setup_keybinds(self) -> None:
        pass

    def setup_player_actions_for_existing(self) -> None:
        pass

    # Convenience for tests ----------------------------------------------------
    def add_human(self, name: str) -> tuple[Player, StubUser]:
        player = Player(id=str(uuid.uuid4()), name=name)
        user = StubUser(name)
        self.players.append(player)
        self.attach_user(player.id, user)
        return player, user


def _add_host(game: DummyLobbyGame, name: str = "Host") -> tuple[Player, StubUser]:
    player, user = game.add_human(name)
    game.host = name
    return player, user


def test_start_game_handles_validation_errors():
    game = DummyLobbyGame()
    host, _ = _add_host(game)
    game._prestart_errors = ["generic-error", ("tuple-error", {"foo": 1})]

    game._action_start_game(host, "start")

    assert game.on_start_called is False
    keys = [entry[0] for entry in game.broadcasts]
    assert "generic-error" in keys
    assert "tuple-error" in keys


def test_start_game_success_triggers_on_start():
    game = DummyLobbyGame()
    host, _ = _add_host(game)
    game._prestart_errors = []

    game._action_start_game(host, "start")

    assert game.on_start_called is True
    assert ("game-starting", {}) in game.broadcasts


def test_add_bot_assigns_default_name_and_attaches_user(monkeypatch):
    game = DummyLobbyGame()
    player, _ = _add_host(game)

    game._action_add_bot(player, "", "add_bot")

    assert any(p.is_bot for p in game.players)
    assert game.rebuild_count == 1
    assert game.broadcast_sounds[-1] == "join.ogg"
    bot_player = next(p for p in game.players if p.is_bot)
    assert bot_player.id in dict(game.attached_users)
    assert bot_player.id in game.setup_player_actions_calls


def test_add_bot_no_available_names_notifies_user(monkeypatch):
    monkeypatch.setattr("server.game_utils.lobby_actions_mixin.BOT_NAMES", ["SoloBot"])
    game = DummyLobbyGame()
    host, user = _add_host(game)
    existing_bot = Player(id=str(uuid.uuid4()), name="SoloBot", is_bot=True)
    game.players.append(existing_bot)

    game._action_add_bot(host, "", "add_bot")

    assert "no-bot-names-available" in [entry[1] for entry in user.spoken if entry[0] == "speak_l"]


def test_remove_bot_drops_last_bot():
    game = DummyLobbyGame()
    human, _ = _add_host(game)
    bot = Player(id=str(uuid.uuid4()), name="Bot", is_bot=True)
    game.players.extend([bot])
    game.player_action_sets[bot.id] = ["actions"]
    game._users[bot.id] = StubUser("Bot")

    game._action_remove_bot(human, "remove")

    assert all(not p.is_bot for p in game.players)
    assert bot.id not in game.player_action_sets
    assert game.rebuild_count == 1


def test_toggle_spectator_announces_changes():
    game = DummyLobbyGame()
    player, _ = _add_host(game)

    game._action_toggle_spectator(player, "toggle")
    assert player.is_spectator is True
    game._action_toggle_spectator(player, "toggle")
    assert player.is_spectator is False


def test_leave_game_spectator_removed_and_menus_rebuilt():
    game = DummyLobbyGame()
    player, _ = _add_host(game)
    player.is_spectator = True

    game._perform_leave_game(player)

    assert player.id not in [p.id for p in game.players]
    assert game.rebuild_count == 1


def test_leave_game_midgame_converts_human_to_bot():
    game = DummyLobbyGame()
    player, user = _add_host(game)
    opponent = Player(id=str(uuid.uuid4()), name="BotMate", is_bot=False)
    game.players.append(opponent)
    game.attach_user(opponent.id, StubUser("BotMate"))
    game.status = "playing"

    game._perform_leave_game(player)

    assert player.is_bot is True
    assert player.id in game._users  # reattached bot user
    assert game._destroyed is False


def test_leave_game_all_humans_depart_triggers_destroy():
    game = DummyLobbyGame()
    player, _ = _add_host(game)
    game.status = "playing"

    game._perform_leave_game(player)

    assert game._destroyed is True
    assert game._table.destroyed is True


def test_leave_game_reassigns_host_when_needed():
    game = DummyLobbyGame()
    host, _ = _add_host(game)
    other, _ = game.add_human("Charlie")
    game.status = "waiting"

    game._perform_leave_game(host)

    assert game.host == "Charlie"
    assert ("new-host", {"player": "Charlie"}) in game.broadcasts


def test_show_actions_menu_lists_enabled_actions():
    game = DummyLobbyGame()
    player, user = _add_host(game)
    action = Action(
        id="do_it",
        label="Do it",
        handler="_handler",
        is_enabled="",
        is_hidden="",
    )
    resolved = ResolvedAction(
        action=action, label="Do it", enabled=True, disabled_reason=None, visible=True
    )
    game.enabled_actions = [resolved]
    game.keybinds["do_it"] = "x"

    game._action_show_actions_menu(player, "menu")

    assert user.menus
    menu = user.menus[-1]
    labels = [item.text if isinstance(item, MenuItem) else item for item in menu["items"]]
    assert any("Do it" in text for text in labels)
    assert Localization.get(user.locale, "back") in labels


def test_show_actions_menu_handles_no_actions():
    game = DummyLobbyGame()
    player, user = _add_host(game)
    game.enabled_actions = []

    game._action_show_actions_menu(player, "menu")

    assert "no-actions-available" in [entry[1] for entry in user.spoken if entry[0] == "speak_l"]


def test_action_save_table_delegates_to_table():
    game = DummyLobbyGame()
    player, _ = _add_host(game)

    game._action_save_table(player, "save")

    assert game._table.saved_with == [player.name]


def test_destroy_marks_game_destroyed_and_table():
    game = DummyLobbyGame()

    game.destroy()

    assert game._destroyed is True
    assert game._table.destroyed is True


def test_initialize_lobby_sets_host_and_state():
    game = DummyLobbyGame()
    host_user = StubUser("HostPerson")

    game.initialize_lobby("HostPerson", host_user)

    assert game.status == "waiting"
    assert game.host == "HostPerson"
    assert game.players[0].name == "HostPerson"
    assert game.rebuild_count == 1
