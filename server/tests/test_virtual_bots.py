"""Tests for the VirtualBotManager core behaviors."""

from types import SimpleNamespace

import pytest

import server.core.virtual_bots as vb_module
import server.games.registry as registry_module

from server.core.virtual_bots import (
    VirtualBot,
    VirtualBotManager,
    VirtualBotState,
)
from server.core.users.base import TrustLevel

from server.core.administration import AdministrationMixin


class FakeTables:
    def __init__(self):
        self.tables = {}
        self.waiting_tables = []

    def get_table(self, table_id):
        return self.tables.get(table_id)

    def remove_table(self, table_id):
        self.tables.pop(table_id, None)

    def get_waiting_tables(self):
        return list(self.waiting_tables)

    def create_table(self, *args, **kwargs):
        raise AssertionError("Not expected in this test")

    def get_all_tables(self):
        return list(self.tables.values())


class FakeServer:
    def __init__(self, db=None):
        self._db = db
        self._users = {}
        self._user_states = {}
        self._tables = FakeTables()
        self.broadcasts = []
        self.table_broadcasts = []

    def _broadcast_presence_l(self, message_id, username, sound):
        self.broadcasts.append((message_id, username, sound))

    def _broadcast_table_created(self, host_name, game_name):
        self.table_broadcasts.append((host_name, game_name))


class DummyNetworkUser:
    def __init__(self):
        self.approved = True


class DummyTableForJoin:
    def __init__(self, table_id, game):
        self.table_id = table_id
        self.game = game
        self.members = []

    def add_member(self, name, user, as_spectator=False):
        self.members.append((name, as_spectator))

    def remove_member(self, name):
        def member_name(member):
            if hasattr(member, "username"):
                return member.username
            if isinstance(member, tuple):
                return member[0]
            return getattr(member, "name", None)

        self.members = [m for m in self.members if member_name(m) != name]


class DummyGameForJoin:
    def __init__(self, host):
        self.status = "waiting"
        self.players = []
        self.host = host
        self.broadcasts = []
        self.table = None

    def get_min_players(self):
        return 2

    def get_max_players(self):
        return 4

    def add_player(self, name, user):
        self.players.append(SimpleNamespace(name=name))

    def broadcast_l(self, message_id, **kwargs):
        self.broadcasts.append((message_id, kwargs))

    def broadcast_sound(self, sound):
        self.broadcasts.append(("sound", sound))

    def rebuild_all_menus(self):
        pass

    def initialize_lobby(self, host_name, user):
        self.players.append(SimpleNamespace(name=host_name))


def _make_single_bot_manager(names: list[str] | None = None) -> VirtualBotManager:
    """Utility builder for tests that need a minimal guided-table setup."""
    if not names:
        names = ["BotA"]
    server = FakeServer()
    manager = VirtualBotManager(server)
    manager._config.names = list(names)
    manager._profiles = {"default": vb_module.VirtualBotProfileOverride(name="default")}
    manager._bot_groups = {
        "hosts": vb_module.BotGroupConfig(name="hosts", bots=list(names), profile=None)
    }
    manager._bot_memberships = {name: {"hosts"} for name in names}
    manager._bot_profiles_map = {name: "default" for name in names}
    manager._guided_tables = {}
    for name in names:
        manager._bots[name] = VirtualBot(name, state=VirtualBotState.ONLINE_IDLE)
    return manager


def test_virtual_bots_load_config_and_fill_server(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["BotA", "BotB", "BotC", "BotD"]
        min_idle_ticks = 10
        max_idle_ticks = 20
        min_online_ticks = 30
        max_online_ticks = 40
        min_offline_ticks = 50
        max_offline_ticks = 60
        """
    )

    server = FakeServer()
    manager = VirtualBotManager(server)
    manager.load_config(config_path)
    assert manager._config.names == ["BotA", "BotB", "BotC", "BotD"]
    assert manager._config.min_idle_ticks == 10
    assert manager._config.max_offline_ticks == 60

    monkeypatch.setattr("server.core.virtual_bots.random.shuffle", lambda seq: seq)
    monkeypatch.setattr("server.core.virtual_bots.random.randint", lambda a, b: a)

    added, online = manager.fill_server()
    assert added == 4
    assert online == 2  # half rounded down
    assert set(server._users.keys()) == {"BotA", "BotB"}
    assert all(state["menu"] == "main_menu" for state in server._user_states.values())
    assert server.broadcasts == [
        ("user-online", "BotA", "online.ogg"),
        ("user-online", "BotB", "online.ogg"),
    ]


def test_bot_group_requires_known_bot(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["BotA"]

        [virtual_bots.bot_groups.mixers]
        bots = ["Ghost"]
        """
    )

    manager = VirtualBotManager(FakeServer())
    with pytest.raises(ValueError) as exc:
        manager.load_config(config_path)
    assert "Ghost" in str(exc.value)


def test_guided_table_strict_allocation_fails(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["HostA"]
        allocation_mode = "strict"

        [virtual_bots.profiles.host]
        min_bots_per_table = 0
        max_bots_per_table = 0

        [virtual_bots.bot_groups.hosts]
        bots = ["HostA"]
        profile = "host"

        [[virtual_bots.guided_tables]]
        table = "solo"
        game = "crazyeights"
        min_bots = 2
        max_bots = 2
        bot_groups = ["hosts"]
        priority = 1
        """
    )

    manager = VirtualBotManager(FakeServer())
    with pytest.raises(ValueError) as exc:
        manager.load_config(config_path)
    assert "requires 2 bots" in str(exc.value)


def test_guided_assignment_respects_priority(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["Host1", "Mix1", "Mix2"]
        fallback_behavior = "disabled"

        [virtual_bots.profiles.host]
        min_bots_per_table = 0
        max_bots_per_table = 0

        [virtual_bots.profiles.mixer]
        min_bots_per_table = 1
        max_bots_per_table = 4

        [virtual_bots.bot_groups.hosts]
        bots = ["Host1"]
        profile = "host"

        [virtual_bots.bot_groups.mixers]
        bots = ["Mix1", "Mix2"]
        profile = "mixer"

        [[virtual_bots.guided_tables]]
        table = "high"
        game = "crazyeights"
        min_bots = 2
        max_bots = 2
        bot_groups = ["hosts", "mixers"]
        priority = 1

        [[virtual_bots.guided_tables]]
        table = "low"
        game = "crazyeights"
        min_bots = 1
        max_bots = 1
        bot_groups = ["mixers"]
        priority = 10
        """
    )

    server = FakeServer()
    manager = VirtualBotManager(server)
    manager.load_config(config_path)
    monkeypatch.setattr("server.core.virtual_bots.random.shuffle", lambda seq: seq)
    monkeypatch.setattr("server.core.virtual_bots.random.randint", lambda a, b: a)

    manager.fill_server()
    manager._refresh_guided_tables()

    assert manager._bots["Host1"].target_rule == "high"
    assert manager._bots["Mix1"].target_rule == "high"
    assert manager._bots["Mix2"].target_rule == "low"


def test_admin_snapshot_reports_guided_tables(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["Host1", "Mix1"]
        fallback_behavior = "disabled"

        [virtual_bots.profiles.host]
        min_bots_per_table = 0
        max_bots_per_table = 0
        waiting_min_ticks = 5
        waiting_max_ticks = 5

        [virtual_bots.bot_groups.hosts]
        bots = ["Host1"]
        profile = "host"

        [virtual_bots.bot_groups.mixers]
        bots = ["Mix1"]
        profile = "mixer"

        [[virtual_bots.guided_tables]]
        table = "alpha"
        game = "crazyeights"
        min_bots = 1
        max_bots = 2
        bot_groups = ["hosts", "mixers"]
        priority = 5
        cycle_ticks = 100
        active_ticks = [0, 50]
        """
    )

    class DummyGame:
        def __init__(self):
            self.host = "Host1"
            self.players = [
                SimpleNamespace(name="Host1"),
                SimpleNamespace(name="Mix1"),
                SimpleNamespace(name="HumanPlayer"),
            ]
            self.status = "waiting"

    class DummyTable:
        def __init__(self):
            self.table_id = "tbl-alpha"
            self.game_type = "crazyeights"
            self.game = DummyGame()

    server = FakeServer()
    manager = VirtualBotManager(server)
    manager.load_config(config_path)

    host_bot = VirtualBot("Host1", state=VirtualBotState.IN_GAME, table_id="tbl-alpha")
    host_bot.profile = "host"
    host_bot.target_rule = "alpha"
    mix_bot = VirtualBot("Mix1", state=VirtualBotState.WAITING_FOR_TABLE)
    mix_bot.profile = "mixer"
    mix_bot.target_rule = "alpha"
    manager._bots["Host1"] = host_bot
    manager._bots["Mix1"] = mix_bot
    manager._guided_tables["alpha"].assigned_bots = {"Host1", "Mix1"}
    manager._guided_tables["alpha"].table_id = "tbl-alpha"
    manager._tick_counter = 25
    server._tables.tables["tbl-alpha"] = DummyTable()

    snapshot = manager.get_admin_snapshot()
    guided = snapshot["guided_tables"][0]
    assert guided["name"] == "alpha"
    assert guided["assigned_bots"] == 2
    assert guided["seated_bots"] == 1
    assert guided["waiting_bots"] == 1
    assert guided["human_players"] == 1
    assert guided["table_state"] == "linked"
    assert guided["ticks_until_next_change"] is not None

    group_index = {entry["name"]: entry for entry in snapshot["groups"]}
    assert group_index["hosts"]["counts"]["in_game"] == 1
    assert group_index["mixers"]["counts"]["waiting"] == 1

    profile_index = {entry["name"]: entry for entry in snapshot["profiles"]}
    assert profile_index["host"]["overrides"]["min_bots_per_table"] == 0
    assert profile_index["mixer"]["bot_count"] == 1


def test_load_config_rejects_invalid_fallback(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["OnlyBot"]
        fallback_behavior = "nonsense"
        """
    )

    manager = VirtualBotManager(FakeServer())
    with pytest.raises(ValueError):
        manager.load_config(config_path)


def test_load_config_requires_names(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = []
        """
    )
    manager = VirtualBotManager(FakeServer())
    with pytest.raises(ValueError):
        manager.load_config(config_path)


def test_load_config_rejects_invalid_allocation(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["OnlyBot"]
        allocation_mode = "nonsense"
        """
    )
    manager = VirtualBotManager(FakeServer())
    with pytest.raises(ValueError):
        manager.load_config(config_path)


def test_load_config_conflicting_group_profiles(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["BotA"]

        [virtual_bots.bot_groups.alpha]
        bots = ["BotA"]
        profile = "host"

        [virtual_bots.bot_groups.beta]
        bots = ["BotA"]
        profile = "mixer"
        """
    )

    manager = VirtualBotManager(FakeServer())
    with pytest.raises(ValueError):
        manager.load_config(config_path)


def test_guided_rule_scheduler_windows(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["BotA"]

        [virtual_bots.bot_groups.hosts]
        bots = ["BotA"]

        [[virtual_bots.guided_tables]]
        table = "wrap"
        game = "crazyeights"
        bot_groups = ["hosts"]
        min_bots = 1
        max_bots = 1
        priority = 1
        cycle_ticks = 100
        active_ticks = [70, 10]
        """
    )

    manager = VirtualBotManager(FakeServer())
    manager.load_config(config_path)
    state = manager._guided_tables["wrap"]

    manager._tick_counter = 75  # inside first segment (>=70)
    assert manager._rule_is_active(state) is True
    assert manager._ticks_until_next_change(state) == 35  # to wrap end at tick 10 next cycle

    manager._tick_counter = 5  # wrap portion before 10
    assert manager._rule_is_active(state) is True
    assert manager._ticks_until_next_change(state) == 5

    manager._tick_counter = 20  # inactive region between 10 and 70
    assert manager._rule_is_active(state) is False
    assert manager._ticks_until_next_change(state) == 50

    manager._tick_counter = 40  # still inactive
    assert manager._rule_is_active(state) is False
    assert manager._ticks_until_next_change(state) == 30


def test_guided_rule_scheduler_non_wrap(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["BotA"]

        [virtual_bots.bot_groups.hosts]
        bots = ["BotA"]

        [[virtual_bots.guided_tables]]
        table = "normal"
        game = "crazyeights"
        bot_groups = ["hosts"]
        min_bots = 1
        max_bots = 1
        priority = 1
        cycle_ticks = 50
        active_ticks = [10, 20]
        """
    )

    manager = VirtualBotManager(FakeServer())
    manager.load_config(config_path)
    state = manager._guided_tables["normal"]

    manager._tick_counter = 5
    assert manager._rule_is_active(state) is False
    assert manager._ticks_until_next_change(state) == 5

    manager._tick_counter = 12
    assert manager._rule_is_active(state) is True
    assert manager._ticks_until_next_change(state) == 8


def test_try_join_game_success(monkeypatch):
    server = FakeServer()
    game = DummyGameForJoin(host="HostBot")
    table = DummyTableForJoin("table1", game)
    server._tables.waiting_tables.append(table)
    server._users["Joiner"] = DummyNetworkUser()

    manager = VirtualBotManager(server)
    bot = VirtualBot("Joiner", state=VirtualBotState.ONLINE_IDLE)
    manager._bots["Joiner"] = bot

    joined = manager._try_join_game(bot)
    assert joined is True
    assert bot.state == VirtualBotState.IN_GAME
    assert bot.table_id == "table1"
    assert server._user_states["Joiner"]["menu"] == "in_game"
    assert table.members == [("Joiner", False)]
    assert any(msg[0] == "table-joined" for msg in game.broadcasts)


def test_try_join_game_no_waiting_tables():
    server = FakeServer()
    manager = VirtualBotManager(server)
    bot = VirtualBot("Idle", state=VirtualBotState.ONLINE_IDLE)
    manager._bots["Idle"] = bot
    server._users["Idle"] = DummyNetworkUser()

    assert manager._try_join_game(bot) is False
    assert bot.state == VirtualBotState.ONLINE_IDLE


def test_try_join_game_rejects_full_table(monkeypatch):
    server = FakeServer()
    manager = VirtualBotManager(server)
    bot = VirtualBot("Joiner", state=VirtualBotState.ONLINE_IDLE)
    manager._bots["Joiner"] = bot
    server._users["Joiner"] = DummyNetworkUser()

    class FullGame(DummyGameForJoin):
        def __init__(self):
            super().__init__("Host")
            self.players = [SimpleNamespace(name=f"P{i}", is_spectator=False) for i in range(4)]

        def get_max_players(self):
            return 4

    table = DummyTableForJoin("table1", FullGame())
    server._tables.waiting_tables.append(table)
    monkeypatch.setattr("server.core.virtual_bots.random.choice", lambda seq: seq[0])

    assert manager._try_join_game(bot) is False
    assert bot.table_id is None


def test_try_create_game_requires_user(monkeypatch):
    _patch_game_registry(monkeypatch)
    server = FakeServer()
    manager = VirtualBotManager(server)
    bot = VirtualBot("Creator", state=VirtualBotState.ONLINE_IDLE)
    manager._bots["Creator"] = bot

    class State(vb_module.GuidedTableState):
        pass

    state = vb_module.GuidedTableState(
        config=vb_module.GuidedTableConfig(
            name="alpha",
            game="crazyeights",
            min_bots=1,
            max_bots=1,
            bot_groups=["hosts"],
            profile=None,
            priority=1,
            cycle_ticks=0,
            active_window=None,
        )
    )

    assert manager._create_guided_table(bot, state) is False
    assert bot.table_id is None


def test_process_offline_bot_disabled_without_target(monkeypatch):
    manager = _make_single_bot_manager()
    manager._config.fallback_behavior = vb_module.FallbackBehavior.DISABLED
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.OFFLINE
    bot.target_rule = None

    monkeypatch.setattr("server.core.virtual_bots.random.randint", lambda a, b: a)

    manager._process_offline_bot(bot)

    assert bot.state == VirtualBotState.OFFLINE
    assert bot.cooldown_ticks == manager._config.min_offline_ticks


def test_can_create_game_type_respects_limit():
    server = FakeServer()
    manager = VirtualBotManager(server)
    manager._config.max_tables_per_game = 1

    class DummyGameObj:
        def __init__(self):
            self.host = "BotHost"

        def get_type(self):
            return "crazyeights"

    table = SimpleNamespace(
        table_id="tbl1",
        game=DummyGameObj(),
    )
    server._tables.tables["tbl1"] = table
    manager._bots["BotHost"] = VirtualBot("BotHost")

    assert manager._can_create_game_type("crazyeights") is False


def test_leave_current_table_executes_game_leave():
    server = FakeServer()

    class FakeGame:
        def __init__(self, name):
            self.players = [SimpleNamespace(name=name)]
            self.actions = []

        def get_player_by_name(self, name):
            return self.players[0]

        def execute_action(self, player, action_id):
            self.actions.append((player.name, action_id))

    fake_table = DummyTableForJoin("tbl1", FakeGame("BotA"))
    fake_table.members = [SimpleNamespace(username="BotA", is_spectator=False)]
    server._tables.tables["tbl1"] = fake_table
    server._users["BotA"] = DummyNetworkUser()

    manager = VirtualBotManager(server)
    bot = VirtualBot("BotA", state=VirtualBotState.IN_GAME)
    bot.table_id = "tbl1"
    manager._bots["BotA"] = bot

    manager._leave_current_table(bot)
    assert bot.table_id is None
    assert fake_table.members == []
    assert fake_table.game.actions == [("BotA", "leave")]


def test_waiting_bot_retries_after_cooldown():
    manager = VirtualBotManager(FakeServer())
    bot = VirtualBot("BotA", state=VirtualBotState.WAITING_FOR_TABLE)
    bot.cooldown_ticks = 2
    manager._bots["BotA"] = bot

    manager._process_waiting_bot(bot)
    assert bot.state == VirtualBotState.WAITING_FOR_TABLE
    assert bot.cooldown_ticks == 1

    manager._process_waiting_bot(bot)
    assert bot.state == VirtualBotState.WAITING_FOR_TABLE
    assert bot.cooldown_ticks == 0

    manager._process_waiting_bot(bot)
    assert bot.state == VirtualBotState.ONLINE_IDLE
    assert bot.think_ticks == 0


def test_fallback_behavior_disabled_keeps_bot_offline(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["BotA"]
        fallback_behavior = "disabled"
        """
    )
    server = FakeServer()
    manager = VirtualBotManager(server)
    manager.load_config(config_path)
    bot = VirtualBot("BotA", state=VirtualBotState.OFFLINE)
    manager._bots["BotA"] = bot

    manager._process_offline_bot(bot)
    assert bot.state == VirtualBotState.OFFLINE
    assert bot.cooldown_ticks > 0


def test_profile_overrides_online_offline_ticks(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["BotA"]
        min_online_ticks = 500
        max_online_ticks = 500
        min_idle_ticks = 50
        max_idle_ticks = 50
        min_offline_ticks = 500
        max_offline_ticks = 500

        [virtual_bots.profiles.host]
        min_online_ticks = 1000
        max_online_ticks = 1000
        min_idle_ticks = 10
        max_idle_ticks = 10
        min_offline_ticks = 2000
        max_offline_ticks = 2000

        [virtual_bots.bot_groups.hosts]
        bots = ["BotA"]
        profile = "host"
        """
    )

    server = FakeServer()
    manager = VirtualBotManager(server)
    manager.load_config(config_path)
    bot = VirtualBot("BotA", state=VirtualBotState.OFFLINE)
    bot.profile = manager._bot_profiles_map["BotA"]
    bot.groups = tuple(manager._bot_memberships.get("BotA", []))
    manager._bots["BotA"] = bot
    manager._bring_bot_online(bot)
    assert bot.target_online_ticks == 1000
    assert bot.think_ticks == 10

    manager._take_bot_offline(bot)
    assert 2000 >= bot.cooldown_ticks >= 2000  # deterministic due to same min/max


def test_guided_bot_enters_waiting_when_table_missing(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["Host1"]

        [virtual_bots.profiles.host]
        min_bots_per_table = 0
        max_bots_per_table = 0

        [virtual_bots.bot_groups.hosts]
        bots = ["Host1"]
        profile = "host"

        [[virtual_bots.guided_tables]]
        table = "alpha"
        game = "crazyeights"
        bot_groups = ["hosts"]
        min_bots = 1
        max_bots = 1
        priority = 1
        """
    )

    server = FakeServer()
    manager = VirtualBotManager(server)
    manager.load_config(config_path)
    bot = VirtualBot("Host1", state=VirtualBotState.ONLINE_IDLE)
    bot.profile = "host"
    bot.target_rule = "alpha"
    manager._bots["Host1"] = bot

    state = manager._guided_tables["alpha"]
    state.assigned_bots = {"Host1"}
    state.table_id = "ghost-id"  # table missing

    transitioned = manager._handle_guided_bot(bot)
    assert transitioned is True
    assert bot.state == VirtualBotState.WAITING_FOR_TABLE
    assert bot.table_id is None
    assert bot.target_rule == "alpha"  # still targeting rule


def test_guided_bot_waits_when_table_full(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["Mix1"]

        [virtual_bots.profiles.mixer]
        min_bots_per_table = 0
        max_bots_per_table = 2

        [virtual_bots.bot_groups.mixers]
        bots = ["Mix1"]
        profile = "mixer"

        [[virtual_bots.guided_tables]]
        table = "beta"
        game = "crazyeights"
        bot_groups = ["mixers"]
        min_bots = 1
        max_bots = 2
        priority = 1
        """
    )

    class FullGame:
        def __init__(self):
            self.status = "waiting"
            self.players = [
                SimpleNamespace(name="Host", is_spectator=False),
                SimpleNamespace(name="Human", is_spectator=False),
            ]
            self.host = "Host"

        def get_min_players(self):
            return 2

        def get_max_players(self):
            return 2

    class FullTable:
        def __init__(self):
            self.table_id = "tbl-beta"
            self.game_type = "crazyeights"
            self.game = FullGame()

    server = FakeServer()
    server._tables.tables["tbl-beta"] = FullTable()
    manager = VirtualBotManager(server)
    manager.load_config(config_path)

    bot = VirtualBot("Mix1", state=VirtualBotState.ONLINE_IDLE)
    bot.profile = "mixer"
    bot.target_rule = "beta"
    manager._bots["Mix1"] = bot

    state = manager._guided_tables["beta"]
    state.assigned_bots = {"Mix1"}
    state.table_id = "tbl-beta"

    transitioned = manager._handle_guided_bot(bot)
    assert transitioned is True
    assert bot.state == VirtualBotState.WAITING_FOR_TABLE
    assert bot.table_id is None


def test_refresh_guided_tables_without_rules_clears_targets():
    manager = _make_single_bot_manager()
    bot = manager._bots["BotA"]
    bot.target_rule = "ghost"
    manager._guided_tables = {}

    manager._refresh_guided_tables()

    assert bot.target_rule is None


def test_rule_inactive_when_window_empty():
    manager = _make_single_bot_manager()
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=0,
        max_bots=0,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=100,
        active_window=(10, 10),
    )
    state = vb_module.GuidedTableState(config=config)
    manager._guided_tables = {"alpha": state}

    assert manager._rule_is_active(state) is False
    assert manager._ticks_until_next_change(state) is None


def test_enter_waiting_for_table_uses_profile_override():
    manager = _make_single_bot_manager()
    profile = manager._profiles["default"]
    profile.waiting_min_ticks = 5
    profile.waiting_max_ticks = 5
    bot = manager._bots["BotA"]

    manager._enter_waiting_for_table(bot)

    assert bot.state == VirtualBotState.WAITING_FOR_TABLE
    assert bot.cooldown_ticks == 5


def test_handle_guided_bot_leaves_wrong_table(monkeypatch):
    manager = _make_single_bot_manager()
    manager._profiles["default"].min_bots_per_table = 1
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=1,
        max_bots=1,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config, table_id="tbl-alpha")
    state.assigned_bots = {"BotA"}
    manager._guided_tables = {"alpha": state}

    bot = manager._bots["BotA"]
    bot.target_rule = "alpha"
    bot.state = VirtualBotState.IN_GAME
    bot.table_id = "tbl-other"
    manager._server._users["BotA"] = DummyNetworkUser()

    class MinimalGame:
        def __init__(self):
            self.status = "waiting"
            self.players = [SimpleNamespace(name="BotA")]
            self.host = "BotA"
            self.leaves = []

        def get_min_players(self):
            return 1

        def get_max_players(self):
            return 4

        def get_player_by_name(self, name):
            return self.players[0] if self.players and self.players[0].name == name else None

        def execute_action(self, player, action_id):
            self.leaves.append((player.name, action_id))

    table = DummyTableForJoin("tbl-other", MinimalGame())
    table.add_member("BotA", DummyNetworkUser())
    manager._server._tables.tables["tbl-other"] = table
    manager._server._tables.tables["tbl-alpha"] = SimpleNamespace(
        table_id="tbl-alpha",
        game_type="crazyeights",
        game=SimpleNamespace(
            status="waiting",
            players=[],
            host="Host",
            get_min_players=lambda: 1,
            get_max_players=lambda: 4,
        ),
    )

    monkeypatch.setattr("server.core.virtual_bots.random.randint", lambda a, b: a)

    transitioned = manager._handle_guided_bot(bot)

    assert transitioned is True
    assert bot.state == VirtualBotState.WAITING_FOR_TABLE
    assert bot.table_id is None
    assert table.members == []


def test_should_bot_join_rule_respects_profile_limits():
    manager = _make_single_bot_manager()
    profile = manager._profiles["default"]
    profile.min_bots_per_table = 1
    profile.max_bots_per_table = 2
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=0,
        max_bots=0,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config, table_id="tbl-alpha")
    state.assigned_bots = {"BotA", "BotB", "BotC"}
    manager._guided_tables = {"alpha": state}

    class JoinableGame:
        def __init__(self):
            self.status = "waiting"
            self.players = [SimpleNamespace(name="Host")]
            self.host = "Host"

        def get_min_players(self):
            return 1

        def get_max_players(self):
            return 4

    game = JoinableGame()
    table = SimpleNamespace(
        table_id="tbl-alpha",
        game_type="crazyeights",
        game=game,
    )

    bot = manager._bots["BotA"]

    # Initially no other seated bots -> below min threshold.
    assert manager._should_bot_join_rule(bot, state, table) is False

    # Add another assigned bot already in the table to satisfy min requirement.
    manager._bots["BotB"] = VirtualBot("BotB", state=VirtualBotState.IN_GAME, table_id="tbl-alpha")
    assert manager._should_bot_join_rule(bot, state, table) is True

    # Add third bot already seated, exceeding max_bots_per_table.
    manager._bots["BotC"] = VirtualBot("BotC", state=VirtualBotState.IN_GAME, table_id="tbl-alpha")
    assert manager._should_bot_join_rule(bot, state, table) is False


def test_process_offline_bot_respects_target_even_when_disabled(monkeypatch):
    manager = _make_single_bot_manager()
    manager._config.fallback_behavior = vb_module.FallbackBehavior.DISABLED
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.OFFLINE
    bot.target_rule = "alpha"

    called = {}

    def fake_bring(online_bot):
        called["bot"] = online_bot
        online_bot.state = VirtualBotState.ONLINE_IDLE

    monkeypatch.setattr(manager, "_bring_bot_online", fake_bring)

    manager._process_offline_bot(bot)

    assert called["bot"] is bot
    assert bot.state == VirtualBotState.ONLINE_IDLE


def test_should_bot_join_rule_enforces_guided_max():
    manager = _make_single_bot_manager()
    profile = manager._profiles["default"]
    profile.min_bots_per_table = 0
    profile.max_bots_per_table = 0  # unlimited at profile level
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=0,
        max_bots=2,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config, table_id="tbl-alpha")
    state.assigned_bots = {"BotA", "BotB", "BotC"}
    manager._guided_tables = {"alpha": state}

    class JoinableGame:
        def __init__(self):
            self.status = "waiting"
            self.players = [SimpleNamespace(name="Host")]
            self.host = "Host"

        def get_min_players(self):
            return 1

        def get_max_players(self):
            return 4

    game = JoinableGame()
    table = SimpleNamespace(
        table_id="tbl-alpha",
        game_type="crazyeights",
        game=game,
    )

    manager._bots["BotB"] = VirtualBot("BotB", state=VirtualBotState.IN_GAME, table_id="tbl-alpha")
    manager._bots["BotC"] = VirtualBot("BotC", state=VirtualBotState.IN_GAME, table_id="tbl-alpha")

    bot = manager._bots["BotA"]
    assert manager._should_bot_join_rule(bot, state, table) is False


def test_count_rule_bots_only_counts_assigned_present():
    manager = _make_single_bot_manager()
    state = vb_module.GuidedTableState(
        config=vb_module.GuidedTableConfig(
            name="alpha",
            game="crazyeights",
            min_bots=0,
            max_bots=0,
            bot_groups=["hosts"],
            profile=None,
            priority=1,
            cycle_ticks=0,
            active_window=None,
        ),
        table_id="tbl-alpha",
    )
    state.assigned_bots = {"BotA", "BotB", "BotC"}
    manager._guided_tables = {"alpha": state}

    manager._bots["BotA"].state = VirtualBotState.IN_GAME
    manager._bots["BotA"].table_id = "tbl-alpha"
    manager._bots["BotB"] = VirtualBot("BotB", state=VirtualBotState.ONLINE_IDLE, table_id=None)
    # BotC assigned but missing from instantiated bots

    assert manager._count_rule_bots(state) == 1
    assert manager._count_rule_bots(state, exclude="BotA") == 0


def test_should_try_create_guided_table_respects_profile_override():
    manager = _make_single_bot_manager()
    bot = manager._bots["BotA"]

    manager._profiles["default"].min_bots_per_table = 0
    assert manager._should_try_create_guided_table(bot) is True

    manager._profiles["default"].min_bots_per_table = 2
    assert manager._should_try_create_guided_table(bot) is False


def test_should_bot_join_rule_checks_waiting_and_capacity():
    manager = _make_single_bot_manager()
    profile = manager._profiles["default"]
    profile.min_bots_per_table = 0
    profile.max_bots_per_table = 0
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=0,
        max_bots=0,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config, table_id="tbl-alpha")
    state.assigned_bots = {"BotA"}
    manager._guided_tables = {"alpha": state}

    class DummyGame:
        def __init__(self, status, player_count, max_players=4):
            self.status = status
            self.host = "Host"
            self.players = [SimpleNamespace(name=f"Player{i}") for i in range(player_count)]
            self._max = max_players

        def get_min_players(self):
            return 1

        def get_max_players(self):
            return self._max

    table = SimpleNamespace(
        table_id="tbl-alpha",
        game_type="crazyeights",
        game=DummyGame(status="finished", player_count=1),
    )

    bot = manager._bots["BotA"]
    assert manager._should_bot_join_rule(bot, state, table) is False  # wrong status

    table.game = DummyGame(status="waiting", player_count=4, max_players=4)
    assert manager._should_bot_join_rule(bot, state, table) is False  # full table

    table.game = DummyGame(status="waiting", player_count=2, max_players=4)
    assert manager._should_bot_join_rule(bot, state, table) is True


def test_join_specific_table_requires_user():
    manager = _make_single_bot_manager()
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.ONLINE_IDLE

    table = DummyTableForJoin("tbl-1", DummyGameForJoin(host="Host"))

    assert manager._join_specific_table(bot, table) is False
    assert bot.state == VirtualBotState.ONLINE_IDLE


def test_create_guided_table_aborts_when_cannot_create(monkeypatch):
    _patch_game_registry(monkeypatch)
    manager = _make_single_bot_manager()
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.ONLINE_IDLE
    manager._server._users["BotA"] = DummyNetworkUser()

    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=1,
        max_bots=1,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config)

    monkeypatch.setattr(manager, "_can_create_game_type", lambda game_type: False)

    created = manager._create_guided_table(bot, state)
    assert created is False
    assert state.table_id is None
    assert bot.state == VirtualBotState.ONLINE_IDLE


def test_refresh_guided_tables_clears_inactive_assignments():
    manager = _make_single_bot_manager()
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=1,
        max_bots=1,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=20,
        active_window=(0, 5),
    )
    state = vb_module.GuidedTableState(config=config)
    state.assigned_bots = {"BotA"}
    manager._guided_tables = {"alpha": state}
    bot = manager._bots["BotA"]
    bot.target_rule = "alpha"

    manager._tick_counter = 10  # outside active window
    manager._refresh_guided_tables()

    assert state.assigned_bots == set()
    assert bot.target_rule is None


def test_handle_guided_bot_no_action_when_seated():
    manager = _make_single_bot_manager()
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=1,
        max_bots=1,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    table = SimpleNamespace(
        table_id="tbl-alpha",
        game_type="crazyeights",
        game=SimpleNamespace(
            status="waiting",
            players=[SimpleNamespace(name="BotA")],
            host="BotA",
            get_min_players=lambda: 1,
            get_max_players=lambda: 4,
        ),
    )
    manager._server._tables.tables["tbl-alpha"] = table
    state = vb_module.GuidedTableState(config=config, table_id="tbl-alpha")
    state.assigned_bots = {"BotA"}
    manager._guided_tables = {"alpha": state}

    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.IN_GAME
    bot.table_id = "tbl-alpha"
    bot.target_rule = "alpha"

    result = manager._handle_guided_bot(bot)
    assert result is False


def test_on_tick_advances_waiting_bot(monkeypatch):
    manager = _make_single_bot_manager()
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.WAITING_FOR_TABLE
    bot.cooldown_ticks = 0
    bot.think_ticks = 5

    monkeypatch.setattr(manager, "_refresh_guided_tables", lambda: None)

    manager.on_tick()

    assert bot.state == VirtualBotState.ONLINE_IDLE
    assert bot.think_ticks == 0


def test_process_in_game_bot_starts_game_when_host(monkeypatch):
    manager = _make_single_bot_manager()
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.IN_GAME
    bot.online_ticks = 500
    bot.game_join_tick = 0
    manager._profiles["default"].start_game_delay_ticks = 0

    class StartableGame:
        def __init__(self):
            self.status = "waiting"
            self.host = "BotA"
            self.players = [SimpleNamespace(name="BotA"), SimpleNamespace(name="Human")]
            self.actions = []

        def get_min_players(self):
            return 2

        def get_player_by_name(self, name):
            for player in self.players:
                if player.name == name:
                    return player

        def execute_action(self, player, action_id):
            self.actions.append((player.name, action_id))

    table = SimpleNamespace(table_id="tbl-start", game_type="crazyeights", game=StartableGame())
    manager._server._tables.tables["tbl-start"] = table
    bot.table_id = "tbl-start"

    manager._process_in_game_bot(bot)

    assert table.game.actions == [("BotA", "start_game")]


def test_on_tick_processes_all_bots(monkeypatch):
    manager = _make_single_bot_manager(["BotA", "BotB"])
    calls = []

    def fake_process(bot):
        calls.append(bot.name)

    monkeypatch.setattr(manager, "_process_bot_tick", fake_process)

    manager.on_tick()

    assert manager._tick_counter == 1
    assert set(calls) == {"BotA", "BotB"}


def test_resolve_guided_assignments_warning_clears_when_min_met():
    manager = _make_single_bot_manager()
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=2,
        max_bots=2,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config)
    manager._guided_tables = {"alpha": state}

    manager._resolve_guided_assignments()
    assert state.warned_shortage is True

    # Add a second eligible bot and rerun assignment.
    manager._config.names.append("BotB")
    manager._bot_groups["hosts"].bots.append("BotB")
    manager._bot_memberships["BotB"] = {"hosts"}
    manager._bot_profiles_map["BotB"] = "default"
    manager._bots["BotB"] = VirtualBot("BotB", state=VirtualBotState.ONLINE_IDLE)

    manager._resolve_guided_assignments()
    assert state.warned_shortage is False
    assert state.assigned_bots == {"BotA", "BotB"}


def test_resolve_guided_assignments_retains_existing_when_capped():
    manager = _make_single_bot_manager(["BotA", "BotB"])
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=1,
        max_bots=1,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config)
    state.assigned_bots = {"BotA"}
    manager._guided_tables = {"alpha": state}

    manager._resolve_guided_assignments()

    assert state.assigned_bots == {"BotA"}
    assert manager._bots["BotA"].target_rule == "alpha"
    assert manager._bots["BotB"].target_rule is None


def test_prune_missing_tables_drops_stale_state():
    manager = _make_single_bot_manager()
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=1,
        max_bots=1,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config, table_id="tbl-alpha")
    state.assigned_bots = {"BotA"}
    manager._guided_tables = {"alpha": state}
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.IN_GAME
    bot.table_id = "tbl-alpha"
    manager._server._tables.tables["tbl-alpha"] = SimpleNamespace(
        table_id="tbl-alpha",
        game_type="scopa",
        game=None,
    )

    manager._prune_missing_tables()

    assert state.table_id is None
    assert bot.table_id is None


def test_resolve_guided_assignments_warns_on_shortage(monkeypatch):
    manager = _make_single_bot_manager()
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=2,
        max_bots=2,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config)
    manager._guided_tables = {"alpha": state}

    manager._resolve_guided_assignments()

    assert state.assigned_bots == {"BotA"}
    assert state.warned_shortage is True
    assert manager._bots["BotA"].target_rule == "alpha"


def test_resolve_guided_assignments_strict_mode_raises():
    manager = _make_single_bot_manager()
    manager._config.allocation_mode = vb_module.AllocationMode.STRICT
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=2,
        max_bots=2,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=0,
        active_window=None,
    )
    state = vb_module.GuidedTableState(config=config)
    manager._guided_tables = {"alpha": state}

    with pytest.raises(RuntimeError):
        manager._resolve_guided_assignments()


def test_resolve_guided_assignments_drops_inactive_rule():
    manager = _make_single_bot_manager()
    config = vb_module.GuidedTableConfig(
        name="alpha",
        game="crazyeights",
        min_bots=1,
        max_bots=1,
        bot_groups=["hosts"],
        profile=None,
        priority=1,
        cycle_ticks=20,
        active_window=(0, 5),
    )
    state = vb_module.GuidedTableState(config=config)
    state.assigned_bots = {"BotA"}
    manager._guided_tables = {"alpha": state}
    manager._bots["BotA"].target_rule = "alpha"
    manager._tick_counter = 10  # outside active window

    manager._resolve_guided_assignments()

    assert state.assigned_bots == set()
    assert manager._bots["BotA"].target_rule is None


class TableHarness:
    def __init__(self):
        self.tables = {}
        self.created = 0

    def create_table(self, game_type, host_username, host_user):
        self.created += 1
        table_id = f"tbl-{self.created}"
        table = SimpleNamespace(
            table_id=table_id,
            game_type=game_type,
            host=host_username,
            members=[],
            game=None,
        )

        def add_member(name, user, as_spectator=False):
            table.members.append(name)

        table.add_member = add_member
        self.tables[table_id] = table
        return table

    def get_table(self, table_id):
        return self.tables.get(table_id)

    def get_all_tables(self):
        return list(self.tables.values())

    def get_waiting_tables(self, game_type: str | None = None):
        return []


class TableServer(FakeServer):
    def __init__(self):
        super().__init__()
        self.manager = TableHarness()
        self._tables = self.manager


class DummyAdminUser:
    def __init__(self):
        self.locale = "en"
        self.trust_level = SimpleNamespace(value=TrustLevel.SERVER_OWNER.value)
        self.messages = []
        self.menus = []
        self.username = "Owner"

    def speak(self, text, buffer="activity"):
        self.messages.append(text)

    def speak_l(self, message_id, buffer="activity", **kwargs):
        self.messages.append((message_id, kwargs))

    def play_sound(self, sound):
        pass

    def show_menu(self, menu_id, items, **kwargs):
        self.menus.append((menu_id, items))


class SnapshotManager:
    def __init__(self, snapshot):
        self._snapshot = snapshot

    def get_admin_snapshot(self):
        return self._snapshot


class AdminHarness(AdministrationMixin):
    def __init__(self, manager):
        self._virtual_bots = manager
        self._users = {}
        self._user_states = {}
        self.menus = []

    def _show_main_menu(self, user):
        self.menus.append("main")

    def _show_admin_menu(self, user):
        self.menus.append("main")

    def _show_virtual_bots_menu(self, user):
        self.menus.append("virtual")


class VirtualBotStub:
    """Stub manager for admin interface tests."""

    def __init__(self, fill_result=(1, 1), clear_result=(2, 1)):
        self.fill_result = fill_result
        self.clear_result = clear_result
        self.fill_calls = 0
        self.save_calls = 0
        self.clear_calls = 0
        self.status = {"total": 2, "online": 1, "offline": 1, "in_game": 0}

    def fill_server(self):
        self.fill_calls += 1
        return self.fill_result

    def save_state(self):
        self.save_calls += 1

    def clear_bots(self):
        self.clear_calls += 1
        return self.clear_result

    def get_status(self):
        return self.status


def _patch_game_registry(monkeypatch):
    class DummyGame:
        status = "waiting"

        def __init__(self):
            self.players = []
            self.status = "waiting"
            self.host = None

        @staticmethod
        def get_type():
            return "crazyeights"

        @staticmethod
        def get_name():
            return "Dummy Game"

        @staticmethod
        def get_category():
            return "card"

        def initialize_lobby(self, host_name, user):
            self.host = host_name
            self.players = [SimpleNamespace(name=host_name)]

        def get_min_players(self):
            return 1

    def fake_get_all(cls):
        return [DummyGame]

    def fake_get_game_class(cls, game_type):
        if game_type == "crazyeights":
            return DummyGame
        return None

    monkeypatch.setattr(
        registry_module.GameRegistry,
        "get_all",
        classmethod(fake_get_all),
        raising=False,
    )
    monkeypatch.setattr(
        registry_module.GameRegistry,
        "get_game_class",
        classmethod(fake_get_game_class),
        raising=False,
    )


def test_guided_host_creates_table(tmp_path, monkeypatch):
    _patch_game_registry(monkeypatch)
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["Host1"]

        [virtual_bots.profiles.host]
        min_bots_per_table = 0
        max_bots_per_table = 0

        [virtual_bots.bot_groups.hosts]
        bots = ["Host1"]
        profile = "host"

        [[virtual_bots.guided_tables]]
        table = "alpha"
        game = "crazyeights"
        bot_groups = ["hosts"]
        min_bots = 1
        max_bots = 1
        priority = 1
        """
    )

    server = TableServer()
    server._users["Host1"] = SimpleNamespace(name="Host1")
    manager = VirtualBotManager(server)
    manager.load_config(config_path)
    bot = VirtualBot("Host1", state=VirtualBotState.ONLINE_IDLE)
    bot.profile = "host"
    bot.target_rule = "alpha"
    manager._bots["Host1"] = bot

    state = manager._guided_tables["alpha"]
    state.assigned_bots = {"Host1"}
    state.table_id = None

    transitioned = manager._handle_guided_bot(bot)
    assert transitioned is True
    assert state.table_id is not None
    assert bot.state == VirtualBotState.IN_GAME
    assert server.table_broadcasts == [("Host1", "crazyeights")]


def test_guided_mixer_does_not_create_table(tmp_path, monkeypatch):
    _patch_game_registry(monkeypatch)
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["Mix1"]

        [virtual_bots.profiles.mixer]
        min_bots_per_table = 1
        max_bots_per_table = 4

        [virtual_bots.bot_groups.mixers]
        bots = ["Mix1"]
        profile = "mixer"

        [[virtual_bots.guided_tables]]
        table = "beta"
        game = "crazyeights"
        bot_groups = ["mixers"]
        min_bots = 1
        max_bots = 4
        priority = 5
        """
    )

    server = TableServer()
    server._users["Mix1"] = SimpleNamespace(name="Mix1")
    manager = VirtualBotManager(server)
    manager.load_config(config_path)
    bot = VirtualBot("Mix1", state=VirtualBotState.ONLINE_IDLE)
    bot.profile = "mixer"
    bot.target_rule = "beta"
    manager._bots["Mix1"] = bot

    state = manager._guided_tables["beta"]
    state.assigned_bots = {"Mix1"}

    transitioned = manager._handle_guided_bot(bot)
    assert transitioned is True
    assert bot.state == VirtualBotState.WAITING_FOR_TABLE
    assert state.table_id is None
    assert server.table_broadcasts == []


def test_guided_rule_profile_override_applies(tmp_path, monkeypatch):
    _patch_game_registry(monkeypatch)
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["Host1"]

        [virtual_bots.profiles.host]
        min_bots_per_table = 0
        max_bots_per_table = 0

        [virtual_bots.profiles.mixer]
        min_bots_per_table = 0
        max_bots_per_table = 0

        [virtual_bots.bot_groups.hosts]
        bots = ["Host1"]
        profile = "host"

        [[virtual_bots.guided_tables]]
        table = "alpha"
        game = "crazyeights"
        bot_groups = ["hosts"]
        min_bots = 1
        max_bots = 1
        priority = 1
        profile = "mixer"
        """
    )

    server = TableServer()
    server._users["Host1"] = SimpleNamespace(name="Host1")
    manager = VirtualBotManager(server)
    manager.load_config(config_path)
    bot = VirtualBot("Host1", state=VirtualBotState.ONLINE_IDLE)
    bot.profile = "host"
    bot.target_rule = "alpha"
    manager._bots["Host1"] = bot

    state = manager._guided_tables["alpha"]
    state.assigned_bots = {"Host1"}

    transitioned = manager._handle_guided_bot(bot)

    assert transitioned is True
    assert bot.profile == "mixer"  # forced by rule
    assert bot.state == VirtualBotState.IN_GAME
    assert state.table_id is not None


@pytest.mark.asyncio
async def test_admin_overviews_emit_output():
    snapshot = {
        "config": {
            "allocation_mode": "best_effort",
            "fallback_behavior": "default",
            "default_profile": "default",
            "configured_bots": 2,
            "instantiated_bots": 2,
            "tick_counter": 10,
        },
        "guided_tables": [
            {
                "name": "alpha",
                "game": "crazyeights",
                "priority": 1,
                "min_bots": 2,
                "max_bots": 4,
                "assigned_bots": 2,
                "seated_bots": 2,
                "waiting_bots": 0,
                "unavailable_bots": 0,
                "bot_groups": ["hosts", "mixers"],
                "profile": "mixer",
                "active": True,
                "table_state": "linked",
                "table_id": "tbl-1",
                "human_players": 1,
                "total_players": 4,
                "host": "HostBot",
                "cycle_ticks": 0,
                "active_window": None,
                "ticks_until_next_change": None,
                "warning": False,
            }
        ],
        "groups": [
            {
                "name": "hosts",
                "profile": "host",
                "counts": {"total": 2, "online": 1, "waiting": 0, "in_game": 1, "offline": 0},
                "bot_names": ["Host1", "Host2"],
                "assigned_rules": ["alpha"],
            }
        ],
        "profiles": [
            {"name": "host", "bot_count": 2, "overrides": {"min_idle_ticks": 10}},
            {"name": "default", "bot_count": 0, "overrides": {}},
        ],
    }

    manager = SnapshotManager(snapshot)
    harness = AdminHarness(manager)
    owner = DummyAdminUser()

    await harness._show_virtual_bots_guided_overview(owner)
    assert "Guided tables" in owner.messages[-1]

    await harness._show_virtual_bots_groups_overview(owner)
    assert "Bot groups" in owner.messages[-1]

    await harness._show_virtual_bots_profiles_overview(owner)
    assert "Profiles" in owner.messages[-1]


@pytest.mark.asyncio
async def test_admin_overviews_require_manager():
    harness = AdminHarness(None)
    owner = DummyAdminUser()
    harness._virtual_bots = None

    await harness._show_virtual_bots_guided_overview(owner)
    assert owner.messages[-1][0] == "virtual-bots-not-available"

    await harness._show_virtual_bots_groups_overview(owner)
    assert owner.messages[-1][0] == "virtual-bots-not-available"

    await harness._show_virtual_bots_profiles_overview(owner)
    assert owner.messages[-1][0] == "virtual-bots-not-available"


@pytest.mark.asyncio
async def test_admin_menu_guided_selection(monkeypatch):
    snapshot = {
        "config": {
            "allocation_mode": "best_effort",
            "fallback_behavior": "default",
            "default_profile": "default",
            "configured_bots": 1,
            "instantiated_bots": 1,
            "tick_counter": 0,
        },
        "guided_tables": [],
        "groups": [],
        "profiles": [],
    }

    harness = AdminHarness(SnapshotManager(snapshot))
    owner = DummyAdminUser()

    await harness._handle_virtual_bots_selection(owner, "guided")
    assert "Guided tables" in owner.messages[-1]

    await harness._handle_virtual_bots_selection(owner, "groups")
    assert "Bot groups" in owner.messages[-1]

    await harness._handle_virtual_bots_selection(owner, "profiles")
    assert "Profiles" in owner.messages[-1]


@pytest.mark.asyncio
async def test_admin_fill_and_status_flow():
    stub = VirtualBotStub(fill_result=(2, 1))
    harness = AdminHarness(stub)
    owner = DummyAdminUser()

    await harness._handle_virtual_bots_selection(owner, "fill")
    assert stub.fill_calls == 1
    assert stub.save_calls == 1
    assert owner.messages[-1][0] == "virtual-bots-filled"

    await harness._handle_virtual_bots_selection(owner, "status")
    assert owner.messages[-1][0] == "virtual-bots-status-report"


@pytest.mark.asyncio
async def test_admin_fill_already_active():
    stub = VirtualBotStub(fill_result=(0, 0))
    harness = AdminHarness(stub)
    owner = DummyAdminUser()

    await harness._handle_virtual_bots_selection(owner, "fill")
    assert owner.messages[-1][0] == "virtual-bots-already-filled"


@pytest.mark.asyncio
async def test_admin_clear_flow():
    stub = VirtualBotStub()
    harness = AdminHarness(stub)
    owner = DummyAdminUser()

    await harness._handle_virtual_bots_selection(owner, "clear")
    assert owner.menus[-1][0] == "virtual_bots_clear_confirm_menu"

    await harness._handle_virtual_bots_clear_confirm_selection(owner, "yes")
    assert stub.clear_calls == 1
    assert owner.messages[-1][0] == "virtual-bots-cleared"


@pytest.mark.asyncio
async def test_admin_clear_cancel():
    stub = VirtualBotStub()
    harness = AdminHarness(stub)
    owner = DummyAdminUser()

    await harness._handle_virtual_bots_selection(owner, "clear")
    await harness._handle_virtual_bots_clear_confirm_selection(owner, "no")
    assert stub.clear_calls == 0


@pytest.mark.asyncio
async def test_admin_back_selection():
    stub = VirtualBotStub()
    harness = AdminHarness(stub)
    owner = DummyAdminUser()

    await harness._handle_virtual_bots_selection(owner, "back")
    assert harness.menus[-1] == "main"


def test_show_virtual_bots_menu_includes_status():
    stub = VirtualBotStub()
    harness = AdminHarness(stub)
    owner = DummyAdminUser()

    AdministrationMixin._show_virtual_bots_menu(harness, owner)

    menu_id, items = owner.menus[-1]
    assert menu_id == "virtual_bots_menu"
    assert items[0].text == "Fill Server (1/2)"
    assert harness._user_states["Owner"]["menu"] == "virtual_bots_menu"


def test_show_virtual_bots_menu_without_manager():
    harness = AdminHarness(None)
    owner = DummyAdminUser()

    AdministrationMixin._show_virtual_bots_menu(harness, owner)

    menu_id, items = owner.menus[-1]
    assert menu_id == "virtual_bots_menu"
    assert items[0].text == "Fill Server"


def test_show_virtual_bots_clear_confirm_menu_outputs_prompt():
    harness = AdminHarness(None)
    owner = DummyAdminUser()

    AdministrationMixin._show_virtual_bots_clear_confirm_menu(harness, owner)

    menu_id, items = owner.menus[-1]
    assert menu_id == "virtual_bots_clear_confirm_menu"
    assert [item.text for item in items] == [
        "Are you sure you want to clear all virtual bots? This will also destroy any tables they are in.",
        "Yes",
        "No",
    ]
    assert (
        owner.messages[-1]
        == "Are you sure you want to clear all virtual bots? This will also destroy any tables they are in."
    )


@pytest.mark.asyncio
async def test_admin_status_without_manager():
    harness = AdminHarness(None)
    owner = DummyAdminUser()

    await harness._handle_virtual_bots_selection(owner, "status")
    assert owner.messages[-1][0] == "virtual-bots-not-available"


@pytest.mark.asyncio
async def test_admin_fill_without_manager():
    harness = AdminHarness(None)
    owner = DummyAdminUser()

    await harness._handle_virtual_bots_selection(owner, "fill")
    assert owner.messages[-1][0] == "virtual-bots-not-available"


@pytest.mark.asyncio
async def test_admin_clear_without_manager():
    harness = AdminHarness(None)
    owner = DummyAdminUser()

    await harness._handle_virtual_bots_clear_confirm_selection(owner, "yes")
    assert owner.messages[-1][0] == "virtual-bots-not-available"


@pytest.mark.asyncio
async def test_admin_fill_no_new_bots_no_save():
    stub = VirtualBotStub(fill_result=(0, 0))
    harness = AdminHarness(stub)
    owner = DummyAdminUser()

    await harness._fill_virtual_bots(owner)
    assert stub.save_calls == 0
    assert owner.messages[-1][0] == "virtual-bots-already-filled"


@pytest.mark.asyncio
async def test_admin_clear_none_to_clear():
    stub = VirtualBotStub(clear_result=(0, 0))
    harness = AdminHarness(stub)
    owner = DummyAdminUser()

    await harness._clear_virtual_bots(owner)
    assert owner.messages[-1][0] == "virtual-bots-none-to-clear"


@pytest.mark.asyncio
async def test_admin_status_reports_counts():
    stub = VirtualBotStub()
    harness = AdminHarness(stub)
    owner = DummyAdminUser()

    await harness._show_virtual_bots_status(owner)
    assert owner.messages[-1][0] == "virtual-bots-status-report"


@pytest.mark.asyncio
async def test_admin_guided_groups_profiles_empty_snapshots():
    snapshot = {
        "config": {
            "allocation_mode": "best_effort",
            "fallback_behavior": "default",
            "default_profile": "default",
            "configured_bots": 0,
            "instantiated_bots": 0,
            "tick_counter": 0,
        },
        "guided_tables": [],
        "groups": [],
        "profiles": [],
    }
    harness = AdminHarness(SnapshotManager(snapshot))
    owner = DummyAdminUser()

    await harness._show_virtual_bots_guided_overview(owner)
    assert "No guided table rules" in owner.messages[-1]

    await harness._show_virtual_bots_groups_overview(owner)
    assert "No bot groups are defined." in owner.messages[-1]

    await harness._show_virtual_bots_profiles_overview(owner)
    assert "No profiles are defined." in owner.messages[-1]


@pytest.mark.asyncio
async def test_admin_guided_overview_with_warning(monkeypatch):
    snapshot = {
        "config": {
            "allocation_mode": "strict",
            "fallback_behavior": "disabled",
            "default_profile": "host",
            "configured_bots": 4,
            "instantiated_bots": 3,
            "tick_counter": 42,
        },
        "guided_tables": [
            {
                "name": "alpha",
                "game": "crazyeights",
                "priority": 5,
                "min_bots": 4,
                "max_bots": None,
                "assigned_bots": 3,
                "seated_bots": 2,
                "waiting_bots": 1,
                "unavailable_bots": 1,
                "bot_groups": ["hosts"],
                "profile": None,
                "active": True,
                "table_state": "linked",
                "table_id": "tbl-1",
                "human_players": 2,
                "total_players": 4,
                "host": "HostBot",
                "cycle_ticks": 100,
                "active_window": [0, 50],
                "ticks_until_next_change": 10,
                "warning": True,
            }
        ],
        "groups": [
            {
                "name": "hosts",
                "profile": None,
                "counts": {"total": 4, "online": 2, "waiting": 1, "in_game": 1, "offline": 0},
                "bot_names": ["A", "B", "C", "D"],
                "assigned_rules": [],
            }
        ],
        "profiles": [
            {"name": "host", "bot_count": 4, "overrides": {"min_idle_ticks": 10}},
        ],
    }

    harness = AdminHarness(SnapshotManager(snapshot))
    owner = DummyAdminUser()

    await harness._show_virtual_bots_guided_overview(owner)
    message = owner.messages[-1]
    assert "Guided tables" in message
    assert "underfilled" in message

    await harness._show_virtual_bots_groups_overview(owner)
    assert "hosts" in owner.messages[-1]

    await harness._show_virtual_bots_profiles_overview(owner)
    assert "host" in owner.messages[-1]


def test_virtual_bots_save_and_load_state(monkeypatch):
    saved = []

    class FakeDB:
        def delete_all_virtual_bots(self):
            saved.clear()

        def save_virtual_bot(self, **payload):
            saved.append(payload)

        def load_all_virtual_bots(self):
            return [
                {
                    "name": "Alpha",
                    "state": "online_idle",
                    "online_ticks": 12,
                    "target_online_ticks": 25,
                    "table_id": None,
                    "game_join_tick": 3,
                },
                {
                    "name": "Ignored",
                    "state": "offline",
                    "online_ticks": 0,
                    "target_online_ticks": 0,
                    "table_id": None,
                    "game_join_tick": 0,
                },
            ]

    server = FakeServer(db=FakeDB())
    manager = VirtualBotManager(server)
    manager._config.names = ["Alpha"]
    manager._bots["Alpha"] = VirtualBot(
        name="Alpha",
        state=VirtualBotState.ONLINE_IDLE,
        online_ticks=5,
        target_online_ticks=10,
    )

    manager.save_state()
    assert saved[0]["name"] == "Alpha"
    assert saved[0]["state"] == VirtualBotState.ONLINE_IDLE.value

    manager._bots.clear()
    loaded = manager.load_state()
    assert loaded == 1
    assert "Alpha" in manager._bots
    assert "Alpha" in server._users
    assert server._user_states["Alpha"]["menu"] == "main_menu"
    assert "Ignored" not in manager._bots


def test_restore_bot_user_conflict_sets_offline(monkeypatch):
    server = FakeServer()
    server._users["Taken"] = DummyNetworkUser()  # Represents real user, not virtual
    manager = VirtualBotManager(server)
    bot = VirtualBot("Taken", state=VirtualBotState.ONLINE_IDLE)

    monkeypatch.setattr("server.core.virtual_bots.random.randint", lambda a, b: a)

    manager._restore_bot_user(bot)

    assert bot.state == VirtualBotState.OFFLINE
    assert bot.cooldown_ticks == 200  # from patched randint
    assert server._users["Taken"] is not None  # original user untouched


def test_leave_current_table_executes_leave_and_removes_member():
    class DummyGame:
        def __init__(self, name):
            self.player = SimpleNamespace(name=name)
            self.leaves = []

        def get_player_by_name(self, name):
            if name == self.player.name:
                return self.player

        def execute_action(self, player, action_id):
            self.leaves.append((player.name, action_id))

    class DummyTable:
        def __init__(self, table_id, bot_name):
            self.table_id = table_id
            self.game = DummyGame(bot_name)
            self.members_removed = []

        def remove_member(self, name):
            self.members_removed.append(name)

    server = FakeServer()
    manager = VirtualBotManager(server)
    bot = VirtualBot("Zed", state=VirtualBotState.IN_GAME, table_id="T1")
    table = DummyTable("T1", "Zed")
    server._tables.tables["T1"] = table
    server._users["Zed"] = DummyNetworkUser()

    manager._leave_current_table(bot)

    assert bot.table_id is None
    assert table.members_removed == ["Zed"]
    assert table.game.leaves == [("Zed", "leave")]


def test_take_bot_offline_removes_user_and_broadcasts(monkeypatch):
    server = FakeServer()
    manager = VirtualBotManager(server)
    bot = VirtualBot("Yin", state=VirtualBotState.ONLINE_IDLE)
    server._users["Yin"] = DummyNetworkUser()
    server._user_states["Yin"] = {"menu": "main"}

    monkeypatch.setattr("server.core.virtual_bots.random.randint", lambda a, b: a)

    manager._take_bot_offline(bot)

    assert bot.state == VirtualBotState.OFFLINE
    assert "Yin" not in server._users
    assert "Yin" not in server._user_states
    assert server.broadcasts[-1] == ("user-offline", "Yin", "offline.ogg")
    assert bot.cooldown_ticks == manager._config.min_offline_ticks


def test_process_online_idle_bot_goes_offline_when_threshold_met(monkeypatch):
    server = FakeServer()
    manager = VirtualBotManager(server)
    bot = VirtualBot("Ada", state=VirtualBotState.ONLINE_IDLE)
    manager._bots["Ada"] = bot
    server._users["Ada"] = DummyNetworkUser()
    bot.online_ticks = manager._config.min_online_ticks
    bot.target_online_ticks = 0
    bot.think_ticks = 0

    monkeypatch.setattr("server.core.virtual_bots.random.random", lambda: 0.0)
    monkeypatch.setattr("server.core.virtual_bots.random.randint", lambda a, b: a)

    manager._process_online_idle_bot(bot)

    assert bot.state == VirtualBotState.OFFLINE
    assert server.broadcasts[-1][0] == "user-offline"


def test_process_online_idle_prioritizes_guided(monkeypatch):
    manager = _make_single_bot_manager()
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.ONLINE_IDLE
    bot.target_rule = "alpha"

    called = {}

    def fake_handle(target_bot):
        called["bot"] = target_bot
        target_bot.state = VirtualBotState.WAITING_FOR_TABLE
        return True

    monkeypatch.setattr(manager, "_handle_guided_bot", fake_handle)
    monkeypatch.setattr(
        manager, "_try_join_game", lambda b: (_ for _ in ()).throw(AssertionError("join called"))
    )
    monkeypatch.setattr(
        manager,
        "_try_create_game",
        lambda b: (_ for _ in ()).throw(AssertionError("create called")),
    )

    manager._process_online_idle_bot(bot)

    assert called["bot"] is bot
    assert bot.state == VirtualBotState.WAITING_FOR_TABLE


def test_process_online_idle_attempts_join_first(monkeypatch):
    manager = _make_single_bot_manager()
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.ONLINE_IDLE
    bot.target_online_ticks = 9999
    bot.online_ticks = 0
    manager._profiles["default"].join_game_chance = 1.0

    monkeypatch.setattr(manager, "_handle_guided_bot", lambda b: False)
    join_calls = {}

    def fake_join(target_bot):
        join_calls["bot"] = target_bot
        target_bot.state = VirtualBotState.IN_GAME
        return True

    monkeypatch.setattr(manager, "_try_join_game", fake_join)
    monkeypatch.setattr(
        manager,
        "_try_create_game",
        lambda b: (_ for _ in ()).throw(AssertionError("create should not run")),
    )
    monkeypatch.setattr("server.core.virtual_bots.random.random", lambda: 0.0)

    manager._process_online_idle_bot(bot)

    assert join_calls["bot"] is bot
    assert bot.state == VirtualBotState.IN_GAME


def test_process_online_idle_attempts_create_when_join_fails(monkeypatch):
    manager = _make_single_bot_manager()
    bot = manager._bots["BotA"]
    bot.state = VirtualBotState.ONLINE_IDLE
    bot.online_ticks = 0
    bot.target_online_ticks = 9999
    profile = manager._profiles["default"]
    profile.join_game_chance = 0.0
    profile.create_game_chance = 1.0
    profile.go_offline_chance = 0.0
    profile.min_idle_ticks = 1
    profile.max_idle_ticks = 1

    monkeypatch.setattr(manager, "_handle_guided_bot", lambda b: False)
    monkeypatch.setattr(manager, "_try_join_game", lambda b: False)

    create_calls = {}

    def fake_create(target_bot):
        create_calls["bot"] = target_bot
        target_bot.state = VirtualBotState.IN_GAME
        return True

    monkeypatch.setattr(manager, "_try_create_game", fake_create)
    monkeypatch.setattr("server.core.virtual_bots.random.random", lambda: 0.5)

    manager._process_online_idle_bot(bot)

    assert create_calls["bot"] is bot
    assert bot.state == VirtualBotState.IN_GAME


def test_start_leaving_game_sets_state_and_logout_flag(monkeypatch):
    server = FakeServer()
    manager = VirtualBotManager(server)
    bot = VirtualBot("Hex", state=VirtualBotState.IN_GAME)

    monkeypatch.setattr("server.core.virtual_bots.random.randint", lambda a, b: a)
    monkeypatch.setattr("server.core.virtual_bots.random.random", lambda: 0.9)

    manager._start_leaving_game(bot)

    assert bot.state == VirtualBotState.LEAVING_GAME
    assert bot.cooldown_ticks == 0
    # Since random.random returned 0.9 and logout chance default 0.33, flag False
    assert bot.logout_after_game is False


def test_process_leaving_game_logout_branch(monkeypatch):
    manager = VirtualBotManager(FakeServer())
    bot = VirtualBot("Leaf", state=VirtualBotState.LEAVING_GAME)
    bot.logout_after_game = True
    bot.online_ticks = 10
    bot.target_online_ticks = 999
    manager._bots["Leaf"] = bot
    monkeypatch.setattr("server.core.virtual_bots.random.randint", lambda a, b: a)

    manager._process_leaving_game_bot(bot)

    assert bot.state == VirtualBotState.ONLINE_IDLE
    assert bot.cooldown_ticks == manager._config.logout_after_game_min_ticks


def test_process_leaving_game_offline_path(monkeypatch):
    manager = VirtualBotManager(FakeServer())
    bot = VirtualBot("Leaf", state=VirtualBotState.LEAVING_GAME)
    bot.logout_after_game = False
    bot.online_ticks = 100
    bot.target_online_ticks = 50
    manager._bots["Leaf"] = bot
    taken_offline = {}

    def fake_take(target_bot):
        taken_offline["bot"] = target_bot
        target_bot.state = VirtualBotState.OFFLINE

    monkeypatch.setattr(manager, "_take_bot_offline", fake_take)

    manager._process_leaving_game_bot(bot)

    assert taken_offline["bot"] is bot
    assert bot.state == VirtualBotState.OFFLINE


def test_try_join_game_adds_bot_to_waiting_table(monkeypatch):
    server = FakeServer()
    manager = VirtualBotManager(server)
    bot = VirtualBot("Joiner", state=VirtualBotState.ONLINE_IDLE)
    manager._bots["Joiner"] = bot
    user = DummyNetworkUser()
    server._users["Joiner"] = user

    game = DummyGameForJoin(host="other")
    table = DummyTableForJoin("table-1", game)
    server._tables.waiting_tables = [table]

    monkeypatch.setattr("server.core.virtual_bots.random.choice", lambda seq: seq[0])

    joined = manager._try_join_game(bot)

    assert joined
    assert bot.state == VirtualBotState.IN_GAME
    assert bot.table_id == "table-1"
    assert server._user_states["Joiner"]["menu"] == "in_game"
    assert table.members == [("Joiner", False)]
    assert game.broadcasts[0][0] == "table-joined"


def test_try_create_game_builds_table(monkeypatch):
    server = FakeServer()
    manager = VirtualBotManager(server)
    bot = VirtualBot("Creator", state=VirtualBotState.ONLINE_IDLE)
    manager._bots["Creator"] = bot
    server._users["Creator"] = DummyNetworkUser()

    class DummyGameClass:
        @classmethod
        def get_type(cls):
            return "dummy"

        @classmethod
        def get_name(cls):
            return "Dummy Game"

        def __init__(self):
            self.players = []

        def initialize_lobby(self, host_name, user):
            self.players.append(SimpleNamespace(name=host_name))
            self.host = host_name

        def get_min_players(self):
            return 2

        def get_max_players(self):
            return 4

    dummy_table = SimpleNamespace(
        table_id="new-table",
        game=None,
    )

    def fake_create_table(game_type, host_name, user):
        assert game_type == "dummy"
        return dummy_table

    monkeypatch.setattr(
        registry_module.GameRegistry,
        "get_all",
        classmethod(lambda cls: [DummyGameClass]),
    )
    monkeypatch.setattr("server.core.virtual_bots.random.choice", lambda seq: seq[0])
    monkeypatch.setattr(server._tables, "create_table", fake_create_table)

    created = manager._try_create_game(bot)

    assert created
    assert bot.state == VirtualBotState.IN_GAME
    assert bot.table_id == "new-table"
    assert dummy_table.game is not None
    assert server._user_states["Creator"]["menu"] == "in_game"
    assert server.table_broadcasts[-1] == ("Creator", "dummy")


def test_clear_bots_removes_tables_and_calls_db(monkeypatch):
    tables_removed = []

    class TableWithGame:
        def __init__(self):
            self.game = SimpleNamespace(broadcast_l=lambda *args, **kwargs: None)

        def remove_member(self, name):
            tables_removed.append(name)

    class DBTracker:
        def __init__(self):
            self.cleared = 0

        def delete_all_virtual_bots(self):
            self.cleared += 1

    server = FakeServer(db=DBTracker())
    manager = VirtualBotManager(server)
    bot = VirtualBot("Cleaner", state=VirtualBotState.IN_GAME, table_id="table-clean")
    manager._bots["Cleaner"] = bot
    server._users["Cleaner"] = DummyNetworkUser()
    server._tables.tables["table-clean"] = SimpleNamespace(
        game=SimpleNamespace(broadcast_l=lambda *args, **kwargs: None),
    )

    bots_cleared, tables_killed = manager.clear_bots()

    assert bots_cleared == 1
    assert tables_killed == 1
    assert "Cleaner" not in manager._bots
    assert server._db.cleared == 1


def test_load_config_with_max_tables_per_game(tmp_path):
    """Test that max_tables_per_game config is loaded correctly."""
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [virtual_bots]
        names = ["BotA"]
        max_tables_per_game = 2
        """
    )

    server = FakeServer()
    manager = VirtualBotManager(server)
    manager.load_config(config_path)

    assert manager._config.max_tables_per_game == 2


def test_count_bot_owned_tables():
    """Test counting tables owned by virtual bots."""

    class FakeTablesWithAll(FakeTables):
        def __init__(self, tables_list):
            super().__init__()
            self._all_tables = tables_list

        def get_all_tables(self):
            return self._all_tables

    # Create mock tables with games
    table1 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "scopa", host="BotA"))
    table2 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "scopa", host="BotB"))
    table3 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "ninetynine", host="BotA"))
    table4 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "scopa", host="HumanPlayer"))

    server = FakeServer()
    server._tables = FakeTablesWithAll([table1, table2, table3, table4])

    manager = VirtualBotManager(server)
    manager._bots["BotA"] = VirtualBot("BotA")
    manager._bots["BotB"] = VirtualBot("BotB")
    # HumanPlayer is not a bot

    assert manager._count_bot_owned_tables("scopa") == 2  # BotA and BotB
    assert manager._count_bot_owned_tables("ninetynine") == 1  # Only BotA
    assert manager._count_bot_owned_tables("othergame") == 0


def test_can_create_game_type_with_limits():
    """Test that _can_create_game_type respects limits."""

    class FakeTablesWithAll(FakeTables):
        def __init__(self, tables_list):
            super().__init__()
            self._all_tables = tables_list

        def get_all_tables(self):
            return self._all_tables

    # Create 2 scopa tables owned by bots
    table1 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "scopa", host="BotA"))
    table2 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "scopa", host="BotB"))

    server = FakeServer()
    server._tables = FakeTablesWithAll([table1, table2])

    manager = VirtualBotManager(server)
    manager._bots["BotA"] = VirtualBot("BotA")
    manager._bots["BotB"] = VirtualBot("BotB")

    # Set limit of 2 per game type
    manager._config.max_tables_per_game = 2

    # Should not be able to create more scopa tables (at limit)
    assert manager._can_create_game_type("scopa") is False

    # Should be able to create ninetynine (0 tables exist)
    assert manager._can_create_game_type("ninetynine") is True

    # Increase limit to 3
    manager._config.max_tables_per_game = 3
    assert manager._can_create_game_type("scopa") is True

    # 0 means unlimited
    manager._config.max_tables_per_game = 0
    assert manager._can_create_game_type("scopa") is True


def test_try_create_game_respects_limits_and_falls_back_to_join(monkeypatch):
    """Test that _try_create_game picks alternative game or joins when limited."""

    class FakeTablesWithAll(FakeTables):
        def __init__(self):
            super().__init__()
            self._all_tables = []

        def get_all_tables(self):
            return self._all_tables

        def create_table(self, game_type, host_name, user):
            return SimpleNamespace(table_id="new-table", game=None)

    # Create 2 scopa tables owned by bots (at limit)
    table1 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "scopa", host="BotA"))
    table2 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "scopa", host="BotB"))

    server = FakeServer()
    server._tables = FakeTablesWithAll()
    server._tables._all_tables = [table1, table2]

    manager = VirtualBotManager(server)
    manager._bots["BotA"] = VirtualBot("BotA")
    manager._bots["BotB"] = VirtualBot("BotB")
    manager._config.max_tables_per_game = 2  # Limit of 2 per game type

    # Create a bot that wants to create a game
    bot = VirtualBot("Creator", state=VirtualBotState.ONLINE_IDLE)
    manager._bots["Creator"] = bot
    server._users["Creator"] = DummyNetworkUser()

    # Mock registry to only return scopa (which is at limit)
    class ScopaGameClass:
        @classmethod
        def get_type(cls):
            return "scopa"

        @classmethod
        def get_name(cls):
            return "Scopa"

    monkeypatch.setattr(
        registry_module.GameRegistry,
        "get_all",
        classmethod(lambda cls: [ScopaGameClass]),
    )

    # No waiting tables to join either
    server._tables.waiting_tables = []

    # Should fail since scopa is at limit and no other games available
    created = manager._try_create_game(bot)
    assert created is False
    assert bot.state == VirtualBotState.ONLINE_IDLE  # State unchanged

    # Now add a waiting table - should fall back to joining
    game = DummyGameForJoin(host="other")
    table = DummyTableForJoin("table-1", game)
    server._tables.waiting_tables = [table]

    monkeypatch.setattr("server.core.virtual_bots.random.choice", lambda seq: seq[0])

    created = manager._try_create_game(bot)
    assert created is True
    assert bot.state == VirtualBotState.IN_GAME
    assert bot.table_id == "table-1"  # Joined existing table


def test_try_create_game_picks_available_game_type(monkeypatch):
    """Test that _try_create_game picks a game type that isn't at its limit."""

    class FakeTablesWithAll(FakeTables):
        def __init__(self):
            super().__init__()
            self._all_tables = []
            self.created_game_types = []

        def get_all_tables(self):
            return self._all_tables

        def create_table(self, game_type, host_name, user):
            self.created_game_types.append(game_type)
            return SimpleNamespace(table_id="new-table", game=None)

    # Create 2 scopa tables (at limit)
    table1 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "scopa", host="BotA"))
    table2 = SimpleNamespace(game=SimpleNamespace(get_type=lambda: "scopa", host="BotB"))

    server = FakeServer()
    server._tables = FakeTablesWithAll()
    server._tables._all_tables = [table1, table2]

    manager = VirtualBotManager(server)
    manager._bots["BotA"] = VirtualBot("BotA")
    manager._bots["BotB"] = VirtualBot("BotB")
    manager._config.max_tables_per_game = 2  # Limit of 2 per game type

    bot = VirtualBot("Creator", state=VirtualBotState.ONLINE_IDLE)
    manager._bots["Creator"] = bot
    server._users["Creator"] = DummyNetworkUser()

    # Mock registry with scopa (at limit) and ninetynine (available)
    class ScopaGameClass:
        @classmethod
        def get_type(cls):
            return "scopa"

        @classmethod
        def get_name(cls):
            return "Scopa"

    class NinetyNineGameClass:
        @classmethod
        def get_type(cls):
            return "ninetynine"

        @classmethod
        def get_name(cls):
            return "Ninety Nine"

        def __init__(self):
            self.players = []

        def initialize_lobby(self, host_name, user):
            self.players.append(SimpleNamespace(name=host_name))

    monkeypatch.setattr(
        registry_module.GameRegistry,
        "get_all",
        classmethod(lambda cls: [ScopaGameClass, NinetyNineGameClass]),
    )
    # Force random.choice to pick the first available (ninetynine since scopa is filtered)
    monkeypatch.setattr("server.core.virtual_bots.random.choice", lambda seq: seq[0])

    created = manager._try_create_game(bot)

    assert created is True
    assert server._tables.created_game_types == ["ninetynine"]
    assert bot.state == VirtualBotState.IN_GAME
