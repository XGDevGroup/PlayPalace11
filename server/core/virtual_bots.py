"""Virtual bot management for simulating users on the server."""

import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .config_paths import get_default_config_path

if TYPE_CHECKING:
    from .server import Server


class VirtualBotState(Enum):
    """State machine for virtual bots."""

    OFFLINE = "offline"
    ONLINE_IDLE = "online_idle"
    IN_GAME = "in_game"
    LEAVING_GAME = "leaving_game"
    WAITING_FOR_TABLE = "waiting_for_table"


class FallbackBehavior(Enum):
    """Behavior when no guided-table rule applies."""

    DEFAULT = "default"
    DISABLED = "disabled"


class AllocationMode(Enum):
    """How guided-table requirements are enforced when bots run short."""

    BEST_EFFORT = "best_effort"
    STRICT = "strict"


@dataclass
class VirtualBotConfig:
    """Configuration for virtual bots loaded from config.toml."""

    names: list[str] = field(default_factory=list)

    # Timing (in ticks; tick rate configured via server settings)
    min_idle_ticks: int = 100  # 5 sec minimum between actions when idle
    max_idle_ticks: int = 600  # 30 sec maximum between actions when idle
    min_online_ticks: int = 1200  # 1 min minimum online before considering going offline
    max_online_ticks: int = 6000  # 5 min maximum online
    min_offline_ticks: int = 600  # 30 sec minimum offline
    max_offline_ticks: int = 3000  # 2.5 min maximum offline
    leave_game_delay_ticks: int = 200  # 10 sec - spread bot departures after game ends
    start_game_delay_ticks: int = 400  # 20 sec - wait for players before starting

    # Behavior probabilities (per decision tick when idle)
    join_game_chance: float = 0.3
    create_game_chance: float = 0.1
    go_offline_chance: float = 0.05

    # Post-game logout behavior
    logout_after_game_chance: float = 0.33  # 33% chance to log off after a game
    logout_after_game_min_ticks: int = 40  # 2 sec minimum delay before logout
    logout_after_game_max_ticks: int = 100  # 5 sec maximum delay before logout

    # Maximum tables bots can own per game type (0 = unlimited)
    # This limit applies to each game type separately.
    max_tables_per_game: int = 0

    # Guided-table / profile settings
    min_bots_per_table: int = 0
    max_bots_per_table: int = 0
    waiting_min_ticks: int = 40
    waiting_max_ticks: int = 100
    fallback_behavior: FallbackBehavior = FallbackBehavior.DEFAULT
    default_profile: str = "default"
    allocation_mode: AllocationMode = AllocationMode.BEST_EFFORT


@dataclass
class VirtualBotProfileOverride:
    """Per-profile overrides layered on top of the base config."""

    name: str
    min_idle_ticks: int | None = None
    max_idle_ticks: int | None = None
    min_online_ticks: int | None = None
    max_online_ticks: int | None = None
    min_offline_ticks: int | None = None
    max_offline_ticks: int | None = None
    leave_game_delay_ticks: int | None = None
    start_game_delay_ticks: int | None = None
    join_game_chance: float | None = None
    create_game_chance: float | None = None
    go_offline_chance: float | None = None
    logout_after_game_chance: float | None = None
    logout_after_game_min_ticks: int | None = None
    logout_after_game_max_ticks: int | None = None
    min_bots_per_table: int | None = None
    max_bots_per_table: int | None = None
    waiting_min_ticks: int | None = None
    waiting_max_ticks: int | None = None


@dataclass
class BotGroupConfig:
    """Explicit grouping of bot names for guided-table routing."""

    name: str
    bots: list[str]
    profile: str | None = None


@dataclass
class GuidedTableConfig:
    """Static configuration for a guided table/channel."""

    name: str
    game: str
    min_bots: int
    max_bots: int
    bot_groups: list[str]
    profile: str | None = None
    priority: int = 100
    cycle_ticks: int = 0
    active_window: tuple[int, int] | None = None


@dataclass
class GuidedTableState:
    """Runtime state for a guided table requirement."""

    config: GuidedTableConfig
    table_id: str | None = None
    assigned_bots: set[str] = field(default_factory=set)
    warned_shortage: bool = False


@dataclass
class VirtualBot:
    """State tracking for a single virtual bot."""

    name: str
    state: VirtualBotState = VirtualBotState.OFFLINE

    # Timing state
    cooldown_ticks: int = 0  # Ticks until next state change allowed
    online_ticks: int = 0  # How long this bot has been online
    target_online_ticks: int = 0  # Random target for when to consider going offline
    think_ticks: int = 0  # Ticks until next decision when idle

    # Game state
    table_id: str | None = None  # Current table ID if in game
    game_join_tick: int = 0  # Tick when bot joined/created the game (for start delay)
    logout_after_game: bool = False  # If True, will log off shortly after leaving game
    profile: str = "default"
    groups: tuple[str, ...] = field(default_factory=tuple)
    target_rule: str | None = None


class VirtualBotManager:
    """
    Manages virtual bots that simulate real users on the server.

    Virtual bots navigate menus, create/join games, and play autonomously.
    They come online and go offline on their own schedules to create
    a natural-feeling server population.
    """

    def __init__(self, server: "Server"):
        """Initialize the virtual bot manager for a server."""
        self._server = server
        self._config = VirtualBotConfig()
        self._bots: dict[str, VirtualBot] = {}  # name -> VirtualBot
        self._profiles: dict[str, VirtualBotProfileOverride] = {}
        self._bot_groups: dict[str, BotGroupConfig] = {}
        self._bot_memberships: dict[str, set[str]] = {}
        self._bot_profiles_map: dict[str, str] = {}
        self._guided_tables: dict[str, GuidedTableState] = {}
        self._tick_counter = 0

    def load_config(self, path: str | Path | None = None) -> None:
        """Load bot configuration from config.toml."""
        if path is None:
            path = get_default_config_path()

        path = Path(path)
        if not path.exists():
            print(f"Virtual bots config not found at {path}, using defaults")
            return

        import tomllib

        with open(path, "rb") as f:
            data = tomllib.load(f)

        vb_config = data.get("virtual_bots", {})

        fallback_behavior = vb_config.get("fallback_behavior", "default")
        allocation_mode = vb_config.get("allocation_mode", "best_effort")

        try:
            fallback_enum = FallbackBehavior(fallback_behavior)
        except ValueError as exc:
            raise ValueError(f"Invalid fallback_behavior '{fallback_behavior}'") from exc

        try:
            allocation_enum = AllocationMode(allocation_mode)
        except ValueError as exc:
            raise ValueError(f"Invalid allocation_mode '{allocation_mode}'") from exc

        import dataclasses as _dc

        _SKIP = {"fallback_behavior", "allocation_mode"}
        kwargs: dict[str, Any] = {
            "fallback_behavior": fallback_enum,
            "allocation_mode": allocation_enum,
        }
        for f in _dc.fields(VirtualBotConfig):
            if f.name in _SKIP or f.name not in vb_config:
                continue
            kwargs[f.name] = vb_config[f.name]
        self._config = VirtualBotConfig(**kwargs)

        if not self._config.names:
            raise ValueError("virtual_bots.names must list at least one bot")

        profiles_section = vb_config.get("profiles", {})
        self._profiles = self._parse_profiles(profiles_section)
        # Always provide a default profile entry (even if empty overrides)
        self._profiles.setdefault("default", VirtualBotProfileOverride(name="default"))

        bot_groups_section = vb_config.get("bot_groups", {})
        self._bot_groups = self._parse_bot_groups(bot_groups_section)

        self._bot_memberships = self._build_bot_memberships()
        self._bot_profiles_map = self._resolve_bot_profiles()

        guided_tables_section = vb_config.get("guided_tables", [])
        self._guided_tables = self._parse_guided_tables(guided_tables_section)
        self._validate_guided_tables()

        # Update any instantiated bots with the latest metadata
        for bot in self._bots.values():
            bot.profile = self._bot_profiles_map.get(bot.name, self._config.default_profile)
            bot.groups = tuple(sorted(self._bot_memberships.get(bot.name, set())))

    def _parse_profiles(
        self, profiles_section: dict[str, Any]
    ) -> dict[str, VirtualBotProfileOverride]:
        """Parse bot profile overrides from configuration."""
        profiles: dict[str, VirtualBotProfileOverride] = {}
        for name, overrides in profiles_section.items():
            if not isinstance(overrides, dict):
                continue
            profiles[name] = VirtualBotProfileOverride(
                name=name,
                min_idle_ticks=overrides.get("min_idle_ticks"),
                max_idle_ticks=overrides.get("max_idle_ticks"),
                min_online_ticks=overrides.get("min_online_ticks"),
                max_online_ticks=overrides.get("max_online_ticks"),
                min_offline_ticks=overrides.get("min_offline_ticks"),
                max_offline_ticks=overrides.get("max_offline_ticks"),
                leave_game_delay_ticks=overrides.get("leave_game_delay_ticks"),
                start_game_delay_ticks=overrides.get("start_game_delay_ticks"),
                join_game_chance=overrides.get("join_game_chance"),
                create_game_chance=overrides.get("create_game_chance"),
                go_offline_chance=overrides.get("go_offline_chance"),
                logout_after_game_chance=overrides.get("logout_after_game_chance"),
                logout_after_game_min_ticks=overrides.get("logout_after_game_min_ticks"),
                logout_after_game_max_ticks=overrides.get("logout_after_game_max_ticks"),
                min_bots_per_table=overrides.get("min_bots_per_table"),
                max_bots_per_table=overrides.get("max_bots_per_table"),
                waiting_min_ticks=overrides.get("waiting_min_ticks"),
                waiting_max_ticks=overrides.get("waiting_max_ticks"),
            )
        return profiles

    def _parse_bot_groups(self, groups_section: dict[str, Any]) -> dict[str, BotGroupConfig]:
        """Parse named bot groups from configuration."""
        groups: dict[str, BotGroupConfig] = {}
        for name, payload in groups_section.items():
            if not isinstance(payload, dict):
                continue
            bots = payload.get("bots", [])
            if not bots:
                raise ValueError(f"virtual_bots.bot_groups.{name} must list at least one bot")
            profile = payload.get("profile")
            groups[name] = BotGroupConfig(name=name, bots=bots, profile=profile)
        return groups

    def _build_bot_memberships(self) -> dict[str, set[str]]:
        """Build a mapping of bot names to their group memberships."""
        memberships = {name: set() for name in self._config.names}
        for group in self._bot_groups.values():
            for bot_name in group.bots:
                if bot_name not in memberships:
                    raise ValueError(
                        f"Bot '{bot_name}' referenced in group '{group.name}' is not defined in names list"
                    )
                memberships[bot_name].add(group.name)
        return memberships

    def _resolve_bot_profiles(self) -> dict[str, str]:
        """Resolve the effective profile for each bot."""
        resolved: dict[str, str] = {}
        default_profile = self._config.default_profile
        self._profiles.setdefault(default_profile, VirtualBotProfileOverride(name=default_profile))

        for bot_name in self._config.names:
            profile_name = default_profile
            profile_overrides = {
                self._bot_groups[group].profile
                for group in self._bot_memberships.get(bot_name, set())
                if self._bot_groups[group].profile
            }
            profile_overrides.discard(None)
            if len(profile_overrides) > 1:
                raise ValueError(
                    f"Conflicting profile assignments for bot '{bot_name}' via bot groups"
                )
            if profile_overrides:
                profile_name = profile_overrides.pop()
            self._profiles.setdefault(profile_name, VirtualBotProfileOverride(name=profile_name))
            resolved[bot_name] = profile_name
        return resolved

    def _parse_guided_tables(
        self, guided_section: list[dict[str, Any]]
    ) -> dict[str, GuidedTableState]:
        """Parse guided table configuration into runtime state."""
        guided: dict[str, GuidedTableState] = {}
        for entry in guided_section:
            if not isinstance(entry, dict):
                continue
            table_name = entry.get("table")
            if not table_name:
                raise ValueError("Each guided table entry must include a 'table' label")
            if table_name in guided:
                raise ValueError(f"Duplicate guided table definition for '{table_name}'")

            game = entry.get("game")
            if not game:
                raise ValueError(f"Guided table '{table_name}' must set 'game'")

            min_bots = entry.get("min_bots", 0)
            max_bots = entry.get("max_bots", 0)
            if min_bots < 0:
                raise ValueError(f"Guided table '{table_name}' min_bots cannot be negative")
            if max_bots != 0 and max_bots < min_bots:
                raise ValueError(
                    f"Guided table '{table_name}' max_bots must be >= min_bots or 0 for unlimited"
                )

            bot_groups = entry.get("bot_groups") or []
            if not bot_groups:
                raise ValueError(f"Guided table '{table_name}' must list at least one bot group")

            profile = entry.get("profile")
            if profile:
                self._profiles.setdefault(profile, VirtualBotProfileOverride(name=profile))

            priority = entry.get("priority", 100)
            cycle_ticks = entry.get("cycle_ticks", 0)
            active_window = entry.get("active_ticks")
            window_tuple: tuple[int, int] | None = None
            if active_window:
                if not isinstance(active_window, list) or len(active_window) != 2:
                    raise ValueError(
                        f"Guided table '{table_name}' active_ticks must be a two-value list [start, end]"
                    )
                window_tuple = (int(active_window[0]), int(active_window[1]))

            config = GuidedTableConfig(
                name=table_name,
                game=game,
                min_bots=int(min_bots),
                max_bots=int(max_bots),
                bot_groups=list(bot_groups),
                profile=profile,
                priority=int(priority),
                cycle_ticks=int(cycle_ticks),
                active_window=window_tuple,
            )
            guided[table_name] = GuidedTableState(config=config)
        return guided

    def _eligible_bots_for_rule(self, config: GuidedTableConfig) -> set[str]:
        """Return the set of bots eligible to satisfy a guided table rule."""
        eligible: set[str] = set()
        for group_name in config.bot_groups:
            group = self._bot_groups.get(group_name)
            if not group:
                raise ValueError(
                    f"Guided table '{config.name}' references unknown bot group '{group_name}'"
                )
            eligible.update(group.bots)
        return eligible

    def _validate_guided_tables(self) -> None:
        """Validate guided table rules against available games and bot counts."""
        from server.games.registry import GameRegistry

        available_games = {cls.get_type() for cls in GameRegistry.get_all()}
        for state in self._guided_tables.values():
            config = state.config
            if config.game not in available_games:
                raise ValueError(
                    f"Guided table '{config.name}' references unknown game '{config.game}'"
                )
            if config.profile and config.profile not in self._profiles:
                raise ValueError(
                    f"Guided table '{config.name}' references undefined profile '{config.profile}'"
                )

            eligible = self._eligible_bots_for_rule(config)
            if config.min_bots > len(eligible):
                message = (
                    f"Guided table '{config.name}' requires {config.min_bots} bots but only "
                    f"{len(eligible)} eligible bots are tagged"
                )
                if self._config.allocation_mode == AllocationMode.STRICT:
                    raise ValueError(message)
                print(f"[virtual_bots] WARNING: {message}")

            if config.active_window:
                start, end = config.active_window
                if config.cycle_ticks <= 0:
                    raise ValueError(
                        f"Guided table '{config.name}' defines active_ticks without cycle_ticks > 0"
                    )
                if not (0 <= start < config.cycle_ticks and 0 <= end <= config.cycle_ticks):
                    raise ValueError(
                        f"Guided table '{config.name}' active_ticks must fall within cycle_ticks bounds"
                    )

    def _rule_is_active(self, state: GuidedTableState) -> bool:
        """Return True if the guided rule is active for the current tick."""
        config = state.config
        if config.cycle_ticks <= 0 or not config.active_window:
            return True
        start, end = config.active_window
        cycle = config.cycle_ticks
        tick = self._tick_counter % cycle
        if start == end:
            return False
        if start < end:
            return start <= tick < end
        # Wrap-around window
        return tick >= start or tick < end

    def _ticks_until_next_change(self, state: GuidedTableState) -> int | None:
        """Return ticks until the next active/inactive transition for a rule."""
        config = state.config
        if config.cycle_ticks <= 0 or not config.active_window:
            return None
        start, end = config.active_window
        cycle = config.cycle_ticks
        tick = self._tick_counter % cycle
        active = self._rule_is_active(state)
        if start == end:
            return None
        if active:
            if start < end:
                return max(end - tick, 0)
            if tick >= start:
                return (cycle - tick) + end
            return max(end - tick, 0)
        # inactive - time until window opens
        if start < end:
            if tick < start:
                return start - tick
            return (cycle - tick) + start
        # wrap-around window: active when tick >= start or tick < end
        if tick < start and tick >= end:
            return start - tick
        return (cycle - tick) + start

    def _get_config_value(self, bot: VirtualBot, field: str):
        """Resolve a config field from the bot's profile override or defaults."""
        profile = self._profiles.get(bot.profile)
        if profile and hasattr(profile, field):
            value = getattr(profile, field)
            if value is not None:
                return value
        return getattr(self._config, field)

    def _iter_guided_states(self) -> list[GuidedTableState]:
        """Return guided table states ordered by priority and name."""
        return sorted(
            self._guided_tables.values(),
            key=lambda state: (state.config.priority, state.config.name),
        )

    def save_state(self) -> None:
        """Save all virtual bot state to the database for persistence."""
        db = self._server._db
        if not db:
            return

        # Clear existing saved state
        db.delete_all_virtual_bots()

        # Save each bot's state
        for bot in self._bots.values():
            db.save_virtual_bot(
                name=bot.name,
                state=bot.state.value,
                online_ticks=bot.online_ticks,
                target_online_ticks=bot.target_online_ticks,
                table_id=bot.table_id,
                game_join_tick=bot.game_join_tick,
            )

    def load_state(self) -> int:
        """
        Load virtual bot state from the database.

        Returns the number of bots loaded.
        """
        db = self._server._db
        if not db:
            return 0

        bot_data = db.load_all_virtual_bots()
        count = 0

        for data in bot_data:
            name = data["name"]
            # Only load bots that are in our config
            if name not in self._config.names:
                continue

            bot = VirtualBot(
                name=name,
                state=VirtualBotState(data["state"]),
                online_ticks=data["online_ticks"],
                target_online_ticks=data["target_online_ticks"],
                table_id=data["table_id"],
                game_join_tick=data["game_join_tick"],
            )
            bot.profile = self._bot_profiles_map.get(name, self._config.default_profile)
            bot.groups = tuple(sorted(self._bot_memberships.get(name, set())))
            self._bots[name] = bot
            count += 1

            # If the bot was online or in a game, recreate their VirtualUser
            if bot.state in (
                VirtualBotState.ONLINE_IDLE,
                VirtualBotState.IN_GAME,
                VirtualBotState.LEAVING_GAME,
                VirtualBotState.WAITING_FOR_TABLE,
            ):
                self._restore_bot_user(bot)

        return count

    def _refresh_guided_tables(self) -> None:
        """Sync guided table targets with live server tables."""
        if not self._guided_tables:
            for bot in self._bots.values():
                bot.target_rule = None
            return

        self._prune_missing_tables()
        self._resolve_guided_assignments()

    def _prune_missing_tables(self) -> None:
        """Clear guided table references for missing or mismatched tables."""
        for state in self._guided_tables.values():
            if not state.table_id:
                continue
            table = self._server._tables.get_table(state.table_id)
            if not table or table.game_type != state.config.game:
                # table vanished; clear references
                stale_id = state.table_id
                state.table_id = None
                for bot_name in state.assigned_bots:
                    bot = self._bots.get(bot_name)
                    if bot and bot.table_id == stale_id:
                        bot.table_id = None

    def _resolve_guided_assignments(self) -> None:
        """Assign bots to guided tables based on availability and rules."""
        for bot in self._bots.values():
            bot.target_rule = None

        available = set(self._bots.keys())

        for state in self._iter_guided_states():
            if not self._rule_is_active(state):
                state.assigned_bots.clear()
                continue

            eligible = self._eligible_bots_for_rule(state.config).intersection(available)

            # Keep already assigned bots if they are still eligible
            retained = sorted(name for name in state.assigned_bots if name in eligible)
            for name in retained:
                available.discard(name)

            assigned = retained
            max_bots = state.config.max_bots if state.config.max_bots > 0 else None

            for name in sorted(eligible):
                if name in assigned:
                    continue
                if max_bots is not None and len(assigned) >= max_bots:
                    break
                available.discard(name)
                assigned.append(name)

            state.assigned_bots = set(assigned)
            for name in assigned:
                self._bots[name].target_rule = state.config.name

            if len(assigned) < state.config.min_bots:
                if self._config.allocation_mode == AllocationMode.STRICT:
                    raise RuntimeError(
                        f"Guided table '{state.config.name}' could not allocate "
                        f"{state.config.min_bots} bots (only {len(assigned)} available)."
                    )
                if not state.warned_shortage:
                    print(
                        f"[virtual_bots] WARNING: guided table '{state.config.name}' "
                        f"underfilled ({len(assigned)}/{state.config.min_bots})"
                    )
                    state.warned_shortage = True
            else:
                state.warned_shortage = False

    def _restore_bot_user(self, bot: VirtualBot) -> None:
        """Restore a VirtualUser for a bot that was online."""
        from .users.virtual_user import VirtualUser

        # Check if user already exists (e.g., from table loading for IN_GAME bots)
        existing_user = self._server._users.get(bot.name)
        if existing_user:
            # If it's already a VirtualUser, just update state
            if hasattr(existing_user, "is_virtual_bot") and existing_user.is_virtual_bot:
                if bot.state == VirtualBotState.ONLINE_IDLE:
                    self._server._user_states[bot.name] = {"menu": "main_menu"}
                elif bot.state in (VirtualBotState.IN_GAME, VirtualBotState.LEAVING_GAME):
                    self._server._user_states[bot.name] = {
                        "menu": "in_game",
                        "table_id": bot.table_id,
                    }
                return
            else:
                # Username taken by a real user - mark bot as offline
                bot.state = VirtualBotState.OFFLINE
                bot.cooldown_ticks = random.randint(200, 400)  # nosec B311
                return

        # Create virtual user and add to server
        user = VirtualUser(bot.name)
        self._server._users[bot.name] = user

        if bot.state in (VirtualBotState.ONLINE_IDLE, VirtualBotState.WAITING_FOR_TABLE):
            self._server._user_states[bot.name] = {"menu": "main_menu"}
        elif bot.state in (VirtualBotState.IN_GAME, VirtualBotState.LEAVING_GAME):
            self._server._user_states[bot.name] = {
                "menu": "in_game",
                "table_id": bot.table_id,
            }

    def fill_server(self) -> tuple[int, int]:
        """
        Instantiate bots from config that don't already exist.

        50% come online immediately, rest stay offline with random cooldowns.
        Does not replace existing bots or delete bots not in config.

        Returns tuple of (bots_added, bots_brought_online).
        """
        if not self._config.names:
            return 0, 0

        # Collect new bot names (not already instantiated)
        new_names = [name for name in self._config.names if name not in self._bots]
        if not new_names:
            return 0, 0

        # Shuffle so we get a random 50% online
        random.shuffle(new_names)
        half = len(new_names) // 2

        added = 0
        online = 0

        for i, name in enumerate(new_names):
            profile_name = self._bot_profiles_map.get(name, self._config.default_profile)
            groups = tuple(sorted(self._bot_memberships.get(name, set())))
            if i < half:
                # Bring online immediately
                bot = VirtualBot(
                    name=name,
                    state=VirtualBotState.OFFLINE,
                    cooldown_ticks=0,  # Will come online on next tick
                    profile=profile_name,
                    groups=groups,
                )
                self._bots[name] = bot
                # Actually bring them online now
                self._bring_bot_online(bot)
                online += 1
            else:
                # Stay offline with random long cooldown
                bot = VirtualBot(
                    name=name,
                    state=VirtualBotState.OFFLINE,
                    profile=profile_name,
                    groups=groups,
                )
                min_offline = self._get_config_value(bot, "min_offline_ticks")
                max_offline = self._get_config_value(bot, "max_offline_ticks")
                cooldown = random.randint(min_offline, max_offline)  # nosec B311
                bot.cooldown_ticks = cooldown
                self._bots[name] = bot
            added += 1

        return added, online

    def clear_bots(self) -> tuple[int, int]:
        """
        Remove all instantiated bots and kill tables they're in.

        Returns tuple of (bots_cleared, tables_killed).
        """
        bot_count = len(self._bots)
        tables_killed = set()

        for name, bot in list(self._bots.items()):
            # If bot is in a table, kill the table
            if bot.table_id:
                table = self._server._tables.get_table(bot.table_id)
                if table and bot.table_id not in tables_killed:
                    # Notify members that table is being closed
                    if table.game:
                        table.game.broadcast_l("virtual-bot-table-closed")
                    # Remove the table
                    self._server._tables.remove_table(bot.table_id)
                    tables_killed.add(bot.table_id)

            # Take bot offline (removes from server users)
            if bot.state in (
                VirtualBotState.ONLINE_IDLE,
                VirtualBotState.IN_GAME,
                VirtualBotState.LEAVING_GAME,
            ):
                self._take_bot_offline_silent(bot)

        self._bots.clear()

        # Also clear from database
        if self._server._db:
            self._server._db.delete_all_virtual_bots()

        return bot_count, len(tables_killed)

    def _take_bot_offline_silent(self, bot: VirtualBot) -> None:
        """Take a bot offline without broadcasting presence."""
        # Remove from server
        self._server._users.pop(bot.name, None)
        self._server._user_states.pop(bot.name, None)

        # Update bot state
        bot.state = VirtualBotState.OFFLINE
        bot.online_ticks = 0
        bot.table_id = None

    def get_status(self) -> dict[str, int]:
        """
        Get counts of bots in each state.

        Returns dict with keys: total, offline, online, in_game
        """
        offline = 0
        online = 0
        in_game = 0

        for bot in self._bots.values():
            if bot.state == VirtualBotState.OFFLINE:
                offline += 1
            elif bot.state in (VirtualBotState.ONLINE_IDLE, VirtualBotState.WAITING_FOR_TABLE):
                online += 1
            elif bot.state in (VirtualBotState.IN_GAME, VirtualBotState.LEAVING_GAME):
                in_game += 1

        return {
            "total": len(self._bots),
            "offline": offline,
            "online": online,
            "in_game": in_game,
        }

    def get_admin_snapshot(self) -> dict[str, Any]:
        """Collect structured debug info for admin tooling."""
        config_summary = self._build_admin_config_summary()
        profile_usage = self._build_admin_profile_usage()
        return {
            "config": config_summary,
            "profiles": self._build_admin_profiles_snapshot(profile_usage),
            "groups": self._build_admin_groups_snapshot(),
            "guided_tables": self._build_admin_guided_snapshot(),
        }

    def _build_admin_config_summary(self) -> dict[str, Any]:
        """Summarize configuration values for admin tooling."""
        return {
            "allocation_mode": self._config.allocation_mode.value,
            "fallback_behavior": self._config.fallback_behavior.value,
            "default_profile": self._config.default_profile,
            "configured_bots": len(self._config.names),
            "instantiated_bots": len(self._bots),
            "tick_counter": self._tick_counter,
        }

    def _build_admin_profile_usage(self) -> dict[str, int]:
        """Count how many bots use each profile."""
        profile_usage: dict[str, int] = {}
        for _bot_name, profile in self._bot_profiles_map.items():
            profile_usage[profile] = profile_usage.get(profile, 0) + 1
        return profile_usage

    def _build_admin_profiles_snapshot(self, profile_usage: dict[str, int]) -> list[dict[str, Any]]:
        """Build snapshot data for configured profiles."""
        profiles_snapshot = []
        for name in sorted(self._profiles.keys()):
            profile = self._profiles[name]
            overrides = {
                field: getattr(profile, field)
                for field in (
                    "min_idle_ticks",
                    "max_idle_ticks",
                    "min_online_ticks",
                    "max_online_ticks",
                    "min_offline_ticks",
                    "max_offline_ticks",
                    "leave_game_delay_ticks",
                    "start_game_delay_ticks",
                    "join_game_chance",
                    "create_game_chance",
                    "go_offline_chance",
                    "logout_after_game_chance",
                    "logout_after_game_min_ticks",
                    "logout_after_game_max_ticks",
                    "min_bots_per_table",
                    "max_bots_per_table",
                    "waiting_min_ticks",
                    "waiting_max_ticks",
                )
                if getattr(profile, field) is not None
            }
            profiles_snapshot.append(
                {
                    "name": name,
                    "overrides": overrides,
                    "bot_count": profile_usage.get(name, 0),
                }
            )
        return profiles_snapshot

    def _build_admin_groups_snapshot(self) -> list[dict[str, Any]]:
        """Build snapshot data for bot groups."""
        groups_snapshot = []
        for group_name in sorted(self._bot_groups.keys()):
            group = self._bot_groups[group_name]
            counts, assigned_rules = self._summarize_bot_group(group.bots)
            groups_snapshot.append(
                {
                    "name": group_name,
                    "profile": group.profile,
                    "counts": counts,
                    "bot_names": list(group.bots),
                    "assigned_rules": sorted(assigned_rules),
                }
            )
        return groups_snapshot

    def _summarize_bot_group(self, bot_names: list[str]) -> tuple[dict[str, int], set[str]]:
        """Count bot states and assigned rules for a group."""
        counts = {"total": 0, "online": 0, "waiting": 0, "in_game": 0, "offline": 0}
        assigned_rules: set[str] = set()
        for bot_name in bot_names:
            counts["total"] += 1
            bot = self._bots.get(bot_name)
            if not bot:
                counts["offline"] += 1
                continue
            if bot.target_rule:
                assigned_rules.add(bot.target_rule)
            if bot.state in (VirtualBotState.IN_GAME, VirtualBotState.LEAVING_GAME):
                counts["in_game"] += 1
            elif bot.state == VirtualBotState.WAITING_FOR_TABLE:
                counts["waiting"] += 1
            elif bot.state == VirtualBotState.ONLINE_IDLE:
                counts["online"] += 1
            else:
                counts["offline"] += 1
        return counts, assigned_rules

    def _build_admin_guided_snapshot(self) -> list[dict[str, Any]]:
        """Build snapshot data for guided table rules."""
        return [self._build_guided_state_snapshot(state) for state in self._iter_guided_states()]

    def _build_guided_state_snapshot(self, state: "GuidedTableRuleState") -> dict[str, Any]:
        """Build a snapshot for a single guided rule state."""
        config = state.config
        assigned = len(state.assigned_bots)
        seated = self._count_rule_bots(state)
        waiting, unavailable = self._count_guided_availability(state)
        active = self._rule_is_active(state)
        ticks_until_next = self._ticks_until_next_change(state)
        table_state, host, total_players, human_players = self._describe_guided_table(state)

        return {
            "name": config.name,
            "game": config.game,
            "priority": config.priority,
            "min_bots": config.min_bots,
            "max_bots": config.max_bots if config.max_bots > 0 else None,
            "assigned_bots": assigned,
            "seated_bots": seated,
            "waiting_bots": waiting,
            "bot_groups": list(config.bot_groups),
            "profile": config.profile,
            "active": active,
            "table_state": table_state,
            "table_id": state.table_id,
            "human_players": human_players,
            "total_players": total_players,
            "host": host,
            "cycle_ticks": config.cycle_ticks,
            "active_window": config.active_window,
            "ticks_until_next_change": ticks_until_next,
            "warning": state.warned_shortage or (assigned < config.min_bots),
            "unavailable_bots": unavailable,
        }

    def _count_guided_availability(self, state: "GuidedTableRuleState") -> tuple[int, int]:
        """Count guided bots waiting vs unavailable for a rule."""
        waiting = 0
        unavailable = 0
        for name in state.assigned_bots:
            bot = self._bots.get(name)
            if not bot:
                unavailable += 1
                continue
            if bot.table_id == state.table_id and bot.state in (
                VirtualBotState.IN_GAME,
                VirtualBotState.LEAVING_GAME,
            ):
                continue
            if bot.state == VirtualBotState.OFFLINE:
                unavailable += 1
            else:
                waiting += 1
        return waiting, unavailable

    def _describe_guided_table(
        self, state: "GuidedTableRuleState"
    ) -> tuple[str, str | None, int, int]:
        """Describe the guided table link and player counts."""
        if not state.table_id:
            return "unassigned", None, 0, 0

        table = self._server._tables.get_table(state.table_id)
        if not table or not table.game:
            return "stale", None, 0, 0

        human_players = len(
            [player for player in table.game.players if player.name not in self._bots]
        )
        return "linked", table.game.host, len(table.game.players), human_players

    def on_tick(self) -> None:
        """Process bot decisions each server tick."""
        self._tick_counter += 1
        self._refresh_guided_tables()
        for bot in list(self._bots.values()):
            self._process_bot_tick(bot)

    def _process_bot_tick(self, bot: VirtualBot) -> None:
        """Process a single bot's tick."""
        # Handle cooldown
        if bot.cooldown_ticks > 0:
            bot.cooldown_ticks -= 1
            return

        if bot.state == VirtualBotState.OFFLINE:
            self._process_offline_bot(bot)
        elif bot.state == VirtualBotState.ONLINE_IDLE:
            self._process_online_idle_bot(bot)
        elif bot.state == VirtualBotState.IN_GAME:
            self._process_in_game_bot(bot)
        elif bot.state == VirtualBotState.LEAVING_GAME:
            self._process_leaving_game_bot(bot)
        elif bot.state == VirtualBotState.WAITING_FOR_TABLE:
            self._process_waiting_bot(bot)

    def _process_offline_bot(self, bot: VirtualBot) -> None:
        """Process a bot that is currently offline - bring them online."""
        if self._config.fallback_behavior == FallbackBehavior.DISABLED and not bot.target_rule:
            # Stay offline until a guided assignment needs this bot
            bot.cooldown_ticks = random.randint(  # nosec B311
                self._get_config_value(bot, "min_offline_ticks"),
                self._get_config_value(bot, "max_offline_ticks"),
            )
            return
        self._bring_bot_online(bot)

    def _process_online_idle_bot(self, bot: VirtualBot) -> None:
        """Process a bot that is online and idle."""
        bot.online_ticks += 1

        # Count down think time
        if bot.think_ticks > 0:
            bot.think_ticks -= 1
            return

        if bot.target_rule and self._handle_guided_bot(bot):
            return

        # Decision time!
        config = self._config

        # Consider going offline if we've been online long enough
        if (
            bot.online_ticks >= self._get_config_value(bot, "min_online_ticks")
            and bot.online_ticks >= bot.target_online_ticks
            and random.random() < self._get_config_value(bot, "go_offline_chance")  # nosec B311
        ):
            self._take_bot_offline(bot)
            return

        # Try to join an existing game
        if random.random() < self._get_config_value(bot, "join_game_chance"):  # nosec B311
            if self._try_join_game(bot):
                return

        # Try to create a new game
        if random.random() < self._get_config_value(bot, "create_game_chance"):  # nosec B311
            if self._try_create_game(bot):
                return

        # Set next think delay
        bot.think_ticks = random.randint(  # nosec B311
            self._get_config_value(bot, "min_idle_ticks"),
            self._get_config_value(bot, "max_idle_ticks"),
        )

    def _process_in_game_bot(self, bot: VirtualBot) -> None:
        """Process a bot that is in a game."""
        bot.online_ticks += 1

        # Check if the game has ended
        if bot.table_id:
            table = self._server._tables.get_table(bot.table_id)
            if not table or not table.game:
                # Table or game no longer exists - transition to leaving
                self._start_leaving_game(bot)
                return

            game = table.game
            if game.status == "finished":
                # Game has ended - transition to leaving
                self._start_leaving_game(bot)
            elif game.status == "waiting":
                # Game hasn't started yet - check if we're host and should start
                # Wait for the configured delay to give players time to join
                ticks_in_game = bot.online_ticks - bot.game_join_tick
                if (
                    game.host == bot.name
                    and len(game.players) >= game.get_min_players()
                    and ticks_in_game >= self._get_config_value(bot, "start_game_delay_ticks")
                ):
                    player = game.get_player_by_name(bot.name)
                    if player:
                        game.execute_action(player, "start_game")

    def _process_leaving_game_bot(self, bot: VirtualBot) -> None:
        """Process a bot that is leaving a game (staggered departure)."""
        bot.online_ticks += 1

        # Leave the table and return to idle (or go offline)
        self._leave_current_table(bot)

        # Decide whether to stay online or go offline
        if bot.logout_after_game:
            # Log off after a short delay (2-5 seconds)
            bot.logout_after_game = False  # Reset flag
            bot.state = VirtualBotState.ONLINE_IDLE
            bot.cooldown_ticks = random.randint(  # nosec B311
                self._get_config_value(bot, "logout_after_game_min_ticks"),
                self._get_config_value(bot, "logout_after_game_max_ticks"),
            )
            # Set target so they go offline on next process_online_idle
            bot.target_online_ticks = 0
        elif bot.online_ticks >= bot.target_online_ticks:
            self._take_bot_offline(bot)
        else:
            bot.state = VirtualBotState.ONLINE_IDLE
            bot.think_ticks = random.randint(  # nosec B311
                self._get_config_value(bot, "min_idle_ticks"),
                self._get_config_value(bot, "max_idle_ticks"),
            )

    def _process_waiting_bot(self, bot: VirtualBot) -> None:
        """Bots waiting for a guided table retry after their waiting window."""
        if bot.cooldown_ticks > 0:
            bot.cooldown_ticks -= 1
            return
        bot.state = VirtualBotState.ONLINE_IDLE
        bot.think_ticks = 0

    def _handle_guided_bot(self, bot: VirtualBot) -> bool:
        """Direct bot behavior toward its assigned guided table."""
        state = self._guided_tables.get(bot.target_rule or "")
        if not state or not self._rule_is_active(state):
            bot.target_rule = None
            return False

        config = state.config
        if config.profile and bot.profile != config.profile:
            bot.profile = config.profile

        table = None
        if state.table_id:
            table = self._server._tables.get_table(state.table_id)
            if not table or table.game_type != config.game:
                table = None
                state.table_id = None

        if bot.table_id and bot.table_id != (state.table_id or bot.table_id):
            # Bot is in another table; leave and wait
            self._leave_current_table(bot)
            self._enter_waiting_for_table(bot)
            return True

        if not table:
            if self._should_try_create_guided_table(bot):
                if self._create_guided_table(bot, state):
                    return True
            self._enter_waiting_for_table(bot)
            return True

        # Table exists; ensure bot is seated
        if bot.table_id == table.table_id:
            return False

        if not self._should_bot_join_rule(bot, state, table):
            self._enter_waiting_for_table(bot)
            return True

        if self._join_specific_table(bot, table):
            state.table_id = table.table_id
            return True

        self._enter_waiting_for_table(bot)
        return True

    def _should_try_create_guided_table(self, bot: VirtualBot) -> bool:
        """Host-style bots (min_bots_per_table == 0) are allowed to spawn tables."""
        return self._get_config_value(bot, "min_bots_per_table") == 0

    def _enter_waiting_for_table(self, bot: VirtualBot) -> None:
        """Move a bot into the waiting-for-table state with cooldown."""
        wait_min = self._get_config_value(bot, "waiting_min_ticks")
        wait_max = self._get_config_value(bot, "waiting_max_ticks")
        bot.state = VirtualBotState.WAITING_FOR_TABLE
        bot.cooldown_ticks = random.randint(wait_min, wait_max)  # nosec B311
        bot.think_ticks = 0

    def _count_rule_bots(self, state: GuidedTableState, exclude: str | None = None) -> int:
        """Count bots currently seated for a guided rule's table."""
        if not state.table_id:
            return 0
        count = 0
        for name in state.assigned_bots:
            if exclude and name == exclude:
                continue
            bot = self._bots.get(name)
            if (
                bot
                and bot.table_id == state.table_id
                and bot.state
                in (
                    VirtualBotState.IN_GAME,
                    VirtualBotState.LEAVING_GAME,
                )
            ):
                count += 1
        return count

    def _should_bot_join_rule(self, bot: VirtualBot, state: GuidedTableState, table) -> bool:
        """Return True if the bot should join the guided table right now."""
        game = table.game
        if not game or game.status != "waiting":
            return False
        if (
            sum(1 for p in game.players if not getattr(p, "is_spectator", False))
            >= game.get_max_players()
        ):
            return False

        current = self._count_rule_bots(state, exclude=bot.name)
        min_required = self._get_config_value(bot, "min_bots_per_table")
        max_allowed = self._get_config_value(bot, "max_bots_per_table")
        if current < min_required:
            return False
        if max_allowed > 0 and (current + 1) > max_allowed:
            return False
        if state.config.max_bots > 0 and (current + 1) > state.config.max_bots:
            return False
        return True

    def _create_guided_table(self, bot: VirtualBot, state: GuidedTableState) -> bool:
        """Create a guided table and seat the bot as host."""
        from server.games.registry import GameRegistry

        user = self._server._users.get(bot.name)
        if not user:
            return False
        if not self._can_create_game_type(state.config.game):
            return False

        game_class = GameRegistry.get_game_class(state.config.game)
        if not game_class:
            return False

        table = self._server._tables.create_table(state.config.game, bot.name, user)
        game = game_class()
        table.game = game
        game._table = table
        game.initialize_lobby(bot.name, user)

        self._server._broadcast_table_created(bot.name, state.config.game)

        bot.state = VirtualBotState.IN_GAME
        bot.table_id = table.table_id
        bot.game_join_tick = bot.online_ticks
        self._server._user_states[bot.name] = {"menu": "in_game", "table_id": table.table_id}
        state.table_id = table.table_id
        return True

    def _join_specific_table(self, bot: VirtualBot, table) -> bool:
        """Join a specific table instance for guided matching."""
        game = table.game
        if not game or game.status != "waiting":
            return False
        if (
            sum(1 for p in game.players if not getattr(p, "is_spectator", False))
            >= game.get_max_players()
        ):
            return False

        user = self._server._users.get(bot.name)
        if not user:
            return False

        table.add_member(bot.name, user, as_spectator=False)
        game.add_player(bot.name, user)
        game.broadcast_l("table-joined", player=bot.name)
        game.broadcast_sound("join.ogg")
        game.rebuild_all_menus()

        bot.state = VirtualBotState.IN_GAME
        bot.table_id = table.table_id
        bot.game_join_tick = bot.online_ticks
        self._server._user_states[bot.name] = {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        return True

    def _bring_bot_online(self, bot: VirtualBot) -> None:
        """Bring a bot online."""
        from .users.virtual_user import VirtualUser

        # Check if username is already taken by a real user
        if bot.name in self._server._users:
            # Reschedule for later
            bot.cooldown_ticks = random.randint(200, 400)  # nosec B311
            return

        # Create virtual user and add to server
        user = VirtualUser(bot.name)
        self._server._users[bot.name] = user
        self._server._user_states[bot.name] = {"menu": "main_menu"}

        # Set up bot state
        bot.state = VirtualBotState.ONLINE_IDLE
        bot.online_ticks = 0
        bot.target_online_ticks = random.randint(  # nosec B311
            self._get_config_value(bot, "min_online_ticks"),
            self._get_config_value(bot, "max_online_ticks"),
        )
        bot.think_ticks = random.randint(  # nosec B311
            self._get_config_value(bot, "min_idle_ticks"),
            self._get_config_value(bot, "max_idle_ticks"),
        )

        # Broadcast online announcement
        self._server._broadcast_presence_l("user-online", bot.name, "online.ogg")

    def _take_bot_offline(self, bot: VirtualBot) -> None:
        """Take a bot offline."""
        # Leave any table first
        self._leave_current_table(bot)

        # Remove from server
        self._server._users.pop(bot.name, None)
        self._server._user_states.pop(bot.name, None)

        # Broadcast offline announcement
        self._server._broadcast_presence_l("user-offline", bot.name, "offline.ogg")

        # Set up offline state
        bot.state = VirtualBotState.OFFLINE
        bot.cooldown_ticks = random.randint(  # nosec B311
            self._get_config_value(bot, "min_offline_ticks"),
            self._get_config_value(bot, "max_offline_ticks"),
        )
        bot.online_ticks = 0
        bot.table_id = None

    def _leave_current_table(self, bot: VirtualBot) -> None:
        """Leave the current table if in one."""
        if not bot.table_id:
            return

        table = self._server._tables.get_table(bot.table_id)
        if table and table.game:
            user = self._server._users.get(bot.name)
            if user:
                # Find player and handle leave properly
                player = table.game.get_player_by_name(bot.name)
                if player:
                    # The game's leave action will handle bot replacement etc.
                    table.game.execute_action(player, "leave")

            # Remove from table members
            table.remove_member(bot.name)

        bot.table_id = None

    def _start_leaving_game(self, bot: VirtualBot) -> None:
        """Start the leaving game process with a staggered delay."""
        bot.state = VirtualBotState.LEAVING_GAME
        bot.cooldown_ticks = random.randint(  # nosec B311
            0, self._get_config_value(bot, "leave_game_delay_ticks")
        )
        # Decide if this bot will log off after the game
        bot.logout_after_game = random.random() < self._get_config_value(  # nosec B311
            bot, "logout_after_game_chance"
        )

    def _try_join_game(self, bot: VirtualBot) -> bool:
        """Try to join an existing waiting table. Returns True if joined."""
        # Get all waiting tables
        tables = self._server._tables.get_waiting_tables()
        if not tables:
            return False

        # Pick a random table
        table = random.choice(tables)  # nosec B311
        game = table.game
        if not game:
            return False

        # Only join games that haven't started yet
        if game.status != "waiting":
            return False

        # Check if there's room
        if (
            sum(1 for p in game.players if not getattr(p, "is_spectator", False))
            >= game.get_max_players()
        ):
            return False

        # Join the table
        user = self._server._users.get(bot.name)
        if not user:
            return False

        table.add_member(bot.name, user, as_spectator=False)
        game.add_player(bot.name, user)
        game.broadcast_l("table-joined", player=bot.name)
        game.broadcast_sound("join.ogg")
        game.rebuild_all_menus()

        # Update bot state
        bot.state = VirtualBotState.IN_GAME
        bot.table_id = table.table_id
        bot.game_join_tick = bot.online_ticks  # Track when we joined for start delay
        self._server._user_states[bot.name] = {
            "menu": "in_game",
            "table_id": table.table_id,
        }

        return True

    def _count_bot_owned_tables(self, game_type: str) -> int:
        """Count how many tables of a game type are owned by virtual bots."""
        count = 0
        for table in self._server._tables.get_all_tables():
            if not table.game:
                continue
            if table.game.get_type() != game_type:
                continue
            # Check if the host is a virtual bot
            host = table.game.host
            if host and host in self._bots:
                count += 1
        return count

    def _can_create_game_type(self, game_type: str) -> bool:
        """Check if bots can create another table of this game type."""
        max_tables = self._config.max_tables_per_game
        if max_tables == 0:
            return True  # 0 means unlimited
        current = self._count_bot_owned_tables(game_type)
        return current < max_tables

    def _get_available_game_types(self) -> list:
        """Get game classes that bots can still create tables for."""
        from server.games.registry import GameRegistry

        available = []
        for game_class in GameRegistry.get_all():
            game_type = game_class.get_type()
            if self._can_create_game_type(game_type):
                available.append(game_class)
        return available

    def _try_create_game(self, bot: VirtualBot) -> bool:
        """Try to create a new game table. Returns True if created."""
        # Get game types that aren't at their limit
        available_game_classes = self._get_available_game_types()
        if not available_game_classes:
            # All game types are maxed out, try to join instead
            if self._try_join_game(bot):
                return True
            # Can't join either, silently stop
            return False

        # Pick a random available game type
        game_class = random.choice(available_game_classes)  # nosec B311
        game_type = game_class.get_type()

        user = self._server._users.get(bot.name)
        if not user:
            return False

        # Create table
        table = self._server._tables.create_table(game_type, bot.name, user)

        # Create game and initialize lobby
        game = game_class()
        table.game = game
        game._table = table
        game.initialize_lobby(bot.name, user)

        # Broadcast table creation to all approved users
        self._server._broadcast_table_created(bot.name, game_type)

        # Update bot state
        bot.state = VirtualBotState.IN_GAME
        bot.table_id = table.table_id
        bot.game_join_tick = bot.online_ticks  # Track when we created for start delay
        self._server._user_states[bot.name] = {
            "menu": "in_game",
            "table_id": table.table_id,
        }

        return True

    def on_game_ended(self, table_id: str) -> None:
        """
        Called when a game ends. Triggers bots to start leaving.

        This is called from the server when a table's game finishes.
        """
        for bot in self._bots.values():
            if bot.table_id == table_id and bot.state == VirtualBotState.IN_GAME:
                self._start_leaving_game(bot)
