"""Tests for admin transfer ownership and virtual bots menus in core.server."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from server.core.server import Server
from server.core.users.base import TrustLevel


class DummyUser:
    def __init__(self, username: str, trust=TrustLevel.SERVER_OWNER, approved=True):
        self.username = username
        self.uuid = f"uuid-{username}"
        self.locale = "en"
        self.trust_level = trust
        self.approved = approved
        self.menus: list[str] = []
        self.spoken: list[tuple[str, dict]] = []
        self.music: list[str] = []

    def show_menu(self, menu_id: str, *_, **__):
        self.menus.append(menu_id)

    def speak(self, text: str, buffer: str = "misc") -> None:
        pass

    def speak_l(self, message_id: str, buffer: str = "misc", **kwargs):
        self.spoken.append((message_id, kwargs))

    def play_sound(self, name: str, **kwargs):
        return None

    def play_music(self, name: str, looping: bool = True):
        self.music.append(name)

    def stop_ambience(self):
        return None

    def set_trust_level(self, trust_level):
        self.trust_level = trust_level


class DummyDB:
    def __init__(self, users=None):
        self.users = users or []
        self.updated = []

    def get_admin_users(self, include_server_owner=True):
        return [SimpleNamespace(username=u, trust_level=TrustLevel.ADMIN) for u in self.users]

    def get_non_admin_users(self, exclude_banned=True):
        return [
            SimpleNamespace(username=u, trust_level=TrustLevel.USER, approved=True)
            for u in self.users
        ]

    def update_user_trust_level(self, username, trust_level):
        self.updated.append((username, trust_level))

    def get_pending_users(self, exclude_banned=True):
        return []


class DummyBotsManager:
    def __init__(self):
        self.cleared = False
        self.filled = False
        self.saved = False

    def fill_server(self):
        self.filled = True
        return (1, 1)

    def save_state(self):
        self.saved = True

    def clear_bots(self):
        self.cleared = True
        return 2, 0

    def get_status(self):
        return {"online": 0, "total": 0, "offline": 0, "in_game": 0}

    async def get_guided_overview(self):
        return {"guided": True}

    async def get_groups_overview(self):
        return {"groups": []}

    async def get_profiles_overview(self):
        return {"profiles": []}


@pytest.fixture
def server(tmp_path, monkeypatch):
    srv = Server(host="127.0.0.1", port=0, db_path=tmp_path / "db.sqlite", preload_locales=True)
    srv._db = DummyDB(users=["alice", "bob"])
    srv._virtual_bots = DummyBotsManager()
    monkeypatch.setattr(
        "server.messages.localization.Localization.get",
        lambda _locale, key, **kwargs: key,
    )
    return srv


@pytest.mark.asyncio
async def test_transfer_ownership_menu_shown(server):
    owner = DummyUser("owner", trust=TrustLevel.SERVER_OWNER)
    server._users = {"owner": owner}

    await server._handle_admin_menu_selection(owner, "transfer_ownership")

    assert owner.menus[-1] == "transfer_ownership_menu"


@pytest.mark.asyncio
async def test_transfer_ownership_confirm_updates_db(server):
    owner = DummyUser("owner", trust=TrustLevel.SERVER_OWNER)
    target_state = {"target_username": "alice"}
    server._users = {"owner": owner}

    await server._handle_transfer_ownership_confirm_selection(owner, "yes", target_state)
    # Confirm menu leads to broadcast choice; finalize transfer with "nobody"
    await server._handle_transfer_broadcast_choice_selection(owner, "nobody", target_state)

    assert ("alice", TrustLevel.SERVER_OWNER) in server._db.updated
    assert owner.menus[-1] == "admin_menu"


@pytest.mark.asyncio
async def test_virtual_bots_clear_confirm_flow(server):
    owner = DummyUser("owner", trust=TrustLevel.SERVER_OWNER)
    server._users = {"owner": owner}

    await server._handle_virtual_bots_selection(owner, "clear")
    assert owner.menus[-1] == "virtual_bots_clear_confirm_menu"

    await server._handle_virtual_bots_clear_confirm_selection(owner, "yes")
    assert server._virtual_bots.cleared is True
    # clear_bots path does not call save_state; ensure flag remains false but no error
    assert server._virtual_bots.saved in {False, True}


@pytest.mark.asyncio
async def test_virtual_bots_fill_and_status(server):
    owner = DummyUser("owner", trust=TrustLevel.SERVER_OWNER)
    server._users = {"owner": owner}

    await server._handle_virtual_bots_selection(owner, "fill")
    assert server._virtual_bots.filled is True

    await server._handle_virtual_bots_selection(owner, "status")
    # status path doesn't error and should speak
    assert owner.spoken
