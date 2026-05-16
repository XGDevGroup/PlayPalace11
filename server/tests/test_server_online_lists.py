"""Coverage for online user listing handlers in core.server."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from server.core.server import Server


class DummyUser:
    """Lightweight user stub to capture menu/speak interactions."""

    def __init__(self, username: str, approved: bool = True, locale: str = "en") -> None:
        self.username = username
        self.approved = approved
        self.locale = locale
        self.spoken: list[tuple[str, dict]] = []
        self.last_menu_id: str | None = None
        self.menu_items: list | None = None
        self._current_menus: dict = {}
        self.uuid = f"uuid-{username}"
        self.client_type = ""
        self.platform = ""

    def format_time_online(self) -> str:
        return "1m"

    def speak_l(self, message_id: str, buffer: str = "misc", **kwargs) -> None:
        self.spoken.append((message_id, kwargs))

    def show_menu(
        self,
        menu_id: str,
        items: list,
        *,
        multiletter: bool = True,
        escape_behavior=None,
        position=None,
        grid_enabled: bool = False,
        grid_width: int = 1,
    ) -> None:
        self.last_menu_id = menu_id
        self.menu_items = items

    def play_music(self, name: str, looping: bool = True) -> None:
        return None


class FakeTables:
    """Minimal table manager stub."""

    def __init__(self, tables: dict[str, object] | None = None) -> None:
        self.tables = tables or {}

    def find_user_table(self, username: str):
        return self.tables.get(username)


class FakeGame:
    """Game stub capturing status box calls."""

    def __init__(self, user_uuid: str, *, transient_open: bool = False) -> None:
        self.user_uuid = user_uuid
        self.transient_open = transient_open
        self.status_calls: list[list[str]] = []

    def get_player_by_id(self, player_id: str):
        return SimpleNamespace(id=player_id) if player_id == self.user_uuid else None

    def _is_transient_display_open(self, _player) -> bool:
        return self.transient_open

    def status_box(self, player, lines: list[str]) -> None:
        self.status_calls.append(lines)


@pytest.fixture
def server(tmp_path, monkeypatch):
    # Use real server wiring but avoid real tables/network.
    srv = Server(host="127.0.0.1", port=0, db_path=tmp_path / "db.sqlite", preload_locales=True)

    # Deterministic localization to avoid locale file dependencies in assertions.
    monkeypatch.setattr(
        "server.messages.localization.Localization.get",
        lambda _locale, key, **kwargs: f"{key}:{kwargs}",
    )
    monkeypatch.setattr(
        "server.messages.localization.Localization.format_list_and",
        lambda _locale, names: " and ".join(names),
    )
    return srv


@pytest.mark.asyncio
async def test_handle_list_online_speaks_one(server):
    user = DummyUser("alice")
    server._users = {"alice": user}
    client = SimpleNamespace(username="alice")

    await server._handle_list_online(client)

    assert user.spoken == [("online-users-one", {"users": "alice"})]


@pytest.mark.asyncio
async def test_handle_list_online_speaks_many(server):
    alice = DummyUser("alice")
    bob = DummyUser("bob")
    server._users = {"alice": alice, "bob": bob}
    client = SimpleNamespace(username="alice")

    await server._handle_list_online(client)

    assert alice.spoken == [("online-users-many", {"count": 2, "users": "alice and bob"})]


@pytest.mark.asyncio
async def test_handle_list_online_with_games_status_box(server):
    user = DummyUser("alice")
    game = FakeGame(user.uuid)
    table = SimpleNamespace(game=game, game_type="mock")
    server._users = {"alice": user}
    server._tables = FakeTables({"alice": table})
    client = SimpleNamespace(username="alice")

    await server._handle_list_online_with_games(client)

    assert game.status_calls, "expected status_box to be invoked"
    # Should not open menu when status box path is taken
    assert user.last_menu_id is None


@pytest.mark.asyncio
async def test_handle_list_online_with_games_menu(server):
    user = DummyUser("alice")
    other = DummyUser("bob")
    server._users = {"alice": user, "bob": other}
    server._tables = FakeTables()  # no table for alice
    client = SimpleNamespace(username="alice")

    await server._handle_list_online_with_games(client)

    assert user.last_menu_id == "online_users"
    assert user.menu_items is not None and len(user.menu_items) >= 1


@pytest.mark.asyncio
async def test_handle_list_online_with_games_ignored_while_transient_open(server):
    user = DummyUser("alice")
    game = FakeGame(user.uuid, transient_open=True)
    table = SimpleNamespace(game=game, game_type="mock")
    server._users = {"alice": user}
    server._tables = FakeTables({"alice": table})
    client = SimpleNamespace(username="alice")

    await server._handle_list_online_with_games(client)

    assert game.status_calls == []
    assert user.last_menu_id is None
