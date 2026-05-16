"""Base game class and player dataclass."""

from dataclasses import dataclass, field
from typing import Any, ClassVar, TYPE_CHECKING, Protocol, runtime_checkable
from abc import ABC, abstractmethod
import logging
import threading

from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.config import BaseConfig

from server.core.users.base import User
from server.core.users.bot import Bot
from ..game_utils.actions import ActionSet
from ..game_utils.options import (
    GameOptions as DeclarativeGameOptions,
    OptionsHandlerMixin,
)
from ..game_utils.game_result import GameResult, PlayerResult
from ..game_utils.teams import TeamManager
from ..game_utils.game_sound_mixin import GameSoundMixin
from ..game_utils.game_communication_mixin import GameCommunicationMixin
from ..game_utils.game_result_mixin import GameResultMixin
from ..game_utils.duration_estimate_mixin import DurationEstimateMixin
from ..game_utils.game_scores_mixin import GameScoresMixin
from ..game_utils.game_prediction_mixin import GamePredictionMixin
from ..game_utils.turn_management_mixin import TurnManagementMixin
from ..game_utils.menu_management_mixin import MenuManagementMixin
from ..game_utils.action_visibility_mixin import ActionVisibilityMixin
from ..game_utils.lobby_actions_mixin import LobbyActionsMixin, BOT_NAMES
from ..game_utils.event_handling_mixin import EventHandlingMixin
from ..game_utils.action_set_creation_mixin import ActionSetCreationMixin
from ..game_utils.action_execution_mixin import ActionExecutionMixin
from ..game_utils.action_set_system_mixin import ActionSetSystemMixin
from ..game_utils.game_status import GameStatus
from server.core.ui.keybinds import Keybind


@dataclass
class ActionContext:
    """Context passed to action handlers when triggered by keybind.

    Attributes:
        menu_item_id: ID of the selected menu item when the keybind fired.
        menu_index: 1-based index of the selected menu item.
        from_keybind: True if triggered via keybind, False if via menu.
    """

    menu_item_id: str | None = None  # ID of selected menu item when keybind pressed
    menu_index: int | None = None  # 1-based index of selected menu item
    from_keybind: bool = False  # True if triggered by keybind, False if by menu selection


@dataclass
class TransientDisplayState:
    """Runtime-only state for an in-game transient display."""

    kind: str
    path: list[str] = field(default_factory=list)
    positions: dict[tuple[str, ...], int] = field(default_factory=dict)


@dataclass
class Player(DataClassJSONMixin):
    """A player in a game (serialized with game state).

    The associated User object is not serialized and is reattached after load.

    Attributes:
        id: Unique identifier (user UUID for humans, generated for bots).
        name: Display name.
        is_bot: True for bot players.
        is_virtual_bot: True for server-level virtual bots (count in stats).
        is_spectator: True if spectating.
        bot_think_ticks: Ticks until bot can act.
        bot_pending_action: Action to execute when ready.
        bot_target: Game-specific target (e.g., score to reach).
    """

    id: str  # UUID - unique identifier (from user.uuid for humans, generated for bots)
    name: str  # Display name
    is_bot: bool = False
    is_virtual_bot: bool = False  # True for server-level virtual bots (should appear in stats)
    is_spectator: bool = False
    # Bot AI state (serialized for persistence)
    bot_think_ticks: int = 0  # Ticks until bot can act
    bot_pending_action: str | None = None  # Action to execute when ready
    bot_target: int | None = None  # Game-specific target (e.g., score to reach)
    replaced_human: bool = False  # True if this slot was a human replaced by a bot


# Re-export GameOptions from options module for backwards compatibility
GameOptions = DeclarativeGameOptions


if TYPE_CHECKING:

    @runtime_checkable
    class GameProtocol(Protocol):
        """Protocol documenting the interface that Game mixins expect.

        This is a compile-time-only contract. Each mixin in the Game class
        assumes these attributes and methods exist on ``self``. Defining them
        here lets type-checkers verify that the concrete Game class (and its
        subclasses) satisfy the contract.
        """

        players: list[Player]
        status: GameStatus
        game_active: bool
        host: str
        round: int
        turn_index: int
        turn_direction: int

        def get_user(self, player: Player) -> User | None: ...
        def broadcast_l(self, message_id: str, **kwargs: Any) -> None: ...
        def broadcast_personal_l(
            self, player: Player, message_id: str, **kwargs: Any
        ) -> None: ...
        def advance_turn(self) -> None: ...
        def finish_game(self) -> None: ...


@dataclass
class Game(
    ABC,
    DataClassJSONMixin,
    GameSoundMixin,
    GameCommunicationMixin,
    GameResultMixin,
    DurationEstimateMixin,
    GameScoresMixin,
    GamePredictionMixin,
    TurnManagementMixin,
    MenuManagementMixin,
    ActionVisibilityMixin,
    LobbyActionsMixin,
    EventHandlingMixin,
    ActionSetCreationMixin,
    ActionExecutionMixin,
    OptionsHandlerMixin,
    ActionSetSystemMixin,
):
    """Abstract base class for all games.

    Games are dataclasses serialized with Mashumaro. All authoritative state
    must live in dataclass fields; runtime-only objects are rebuilt after load.

    Responsibilities:
        - Maintain authoritative game state.
        - Expose actions and keybinds for players.
        - Advance turns and manage lifecycle (waiting/playing/finished).
        - Provide menu content for the client.

    Phases:
        - waiting: Lobby phase; host can add bots and start.
        - playing: Game in progress.
        - finished: Game over.

    Notes:
        - Use broadcast_l / broadcast_personal_l for table transcript messages.
        - Use user.speak_l for command responses or private status checks.
    """

    class Config(BaseConfig):
        # Serialize all fields (don't omit defaults - breaks state restoration)
        serialize_by_alias = True

    # Game state
    players: list[Player] = field(default_factory=list)
    round: int = 0
    game_active: bool = False
    status: GameStatus = GameStatus.WAITING
    host: str = ""  # Username of the host
    current_music: str = ""  # Currently playing music track
    current_ambience: str = ""  # Currently playing ambience loop
    turn_index: int = 0  # Current turn index (serialized for persistence)
    turn_direction: int = 1  # Turn direction: 1 = forward, -1 = reverse
    turn_skip_count: int = 0  # Number of players to skip on next advance
    turn_player_ids: list[str] = field(
        default_factory=list
    )  # Player IDs in turn order (serialized)
    # Round timer state (serialized for persistence)
    round_timer_state: str = "idle"  # idle, counting, paused
    round_timer_ticks: int = 0  # Remaining ticks in countdown
    # Sound scheduler state (serialized for persistence)
    scheduled_sounds: list = field(default_factory=list)  # [[tick, sound, vol, pan, pitch], ...]
    sound_scheduler_tick: int = 0  # Current tick counter
    # Event queue state (serialized for persistence)
    event_queue: list[tuple[int, str, dict]] = field(
        default_factory=list
    )  # [(tick, event_type, data), ...]
    is_animating: bool = False  # True while event sequence is playing
    # Action sets (serialized - actions are pure data now)
    player_action_sets: dict[str, list[ActionSet]] = field(default_factory=dict)
    # Team manager (serialized for persistence)
    _team_manager: TeamManager = field(default_factory=TeamManager)

    def __post_init__(self):
        """Initialize non-serialized state."""
        # These are runtime-only, not serialized
        self._users: dict[str, User] = {}  # player_id -> User
        self._table: Any = None  # Reference to Table (set by server)
        self._keybinds: dict[
            str, list[Keybind]
        ] = {}  # key -> list of Keybinds (allows same key for different states)
        self._pending_actions: dict[str, str] = {}  # player_id -> action_id (waiting for input)
        self._action_context: dict[
            str, ActionContext
        ] = {}  # player_id -> context during action execution
        self._transient_display_state: dict[str, TransientDisplayState] = {}
        self._actions_menu_open: set[str] = set()  # player_ids with actions menu open
        self._destroyed: bool = False  # Whether game has been destroyed
        # Duration estimation state
        self._estimate_threads: list[threading.Thread] = []  # Running simulation threads
        self._estimate_results: list[int] = []  # Collected tick counts
        self._estimate_errors: list[str] = []  # Collected errors
        self._estimate_running: bool = False  # Whether estimation is in progress
        self._estimate_lock: threading.Lock = threading.Lock()  # Protect results list
        self._transcripts: dict[str, list[dict[str, str]]] = {}
        self._options_path: dict[str, list[str]] = {}  # player_id -> options nav stack

    def rebuild_runtime_state(self) -> None:
        """Rebuild runtime-only state after deserialization.

        Subclasses can override to rebuild non-serialized objects. Base turn
        management and sound scheduling are stored in serialized fields, so
        they do not require rebuilding.
        """
        pass

    def validate_actions(self) -> None:
        """Verify all action handler/callback strings resolve to methods.

        Logs warnings for any handler strings that cannot be found on the
        game instance via ``getattr``.  Called after ``on_start()`` so that
        typos in handler names are caught early during development.
        """
        _LOG = logging.getLogger("playpalace.actions")
        for action_sets in self.player_action_sets.values():
            for action_set in action_sets:
                for action in action_set._actions.values():
                    for attr_name in ("handler", "is_enabled", "is_hidden", "get_label", "get_sound"):
                        method_name = getattr(action, attr_name, None)
                        if method_name and getattr(self, method_name, None) is None:
                            _LOG.warning(
                                "Action '%s': %s='%s' does not resolve on %s",
                                action.id, attr_name, method_name, type(self).__name__,
                            )

    # Abstract methods games must implement

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Return the display name of this game (English fallback)."""
        ...

    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        """Return the type identifier for this game."""
        ...

    #: User preferences this game is relevant to (for per-game overrides).
    relevant_preferences: ClassVar[list[str]] = []

    @classmethod
    def get_name_key(cls) -> str:
        """Return the localization key for this game's name."""
        return f"game-name-{cls.get_type()}"

    @classmethod
    def get_category(cls) -> str:
        """Return the category localization key for this game."""
        return "category-uncategorized"

    @classmethod
    def get_min_players(cls) -> int:
        """Return minimum number of players."""
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        """Return maximum number of players."""
        return 4

    @classmethod
    def get_leaderboard_types(cls) -> list[dict]:
        """Return additional leaderboard types this game supports.

        Override in subclasses to add game-specific leaderboards.
        Each dict should have:
        - "id": leaderboard type identifier (e.g., "best_single_turn")
        - "path": dot-separated path to value in custom_data
                  Use {player_id} or {player_name} as placeholders
                  e.g., "player_stats.{player_name}.best_turn"
                  OR for ratio calculations, use:
        - "numerator": path to numerator value
        - "denominator": path to denominator value
                  (values are summed across games, then divided)
        - "aggregate": how to combine values across games
                       "sum", "max", or "avg"
        - "format": entry format key suffix (e.g., "score" for leaderboard-score-entry)
        - "decimals": optional, number of decimal places (default 0)

        The server will look up localization keys like:
        - "leaderboard-type-{id}" for menu display (with underscores as hyphens)
        - "leaderboard-{format}-entry" for each entry
        """
        return []

    def prestart_validate(self) -> list[str] | list[tuple[str, dict]]:
        """Validate game configuration before starting.

        Returns a list of localization keys for any errors found,
        or a list of (error_key, kwargs) tuples for errors that need context.
        Override in subclasses to add game-specific validation.

        Examples:
            return ["pig-error-min-bank-too-high"]
            return [("scopa-error-not-enough-cards", {"decks": 1, "players": 4})]
        """
        errors: list[str] = []
        active_count = len([p for p in self.players if not p.is_spectator])
        if active_count < self.get_min_players():
            errors.append(
                (
                    "action-need-more-players",
                    {"min_players": self.get_min_players()},
                )
            )
        return errors

    def _validate_team_mode(self, team_mode: str) -> str | None:
        """Helper to validate team mode for current player count.

        Args:
            team_mode: Internal team mode string (e.g., "individual", "2v2").

        Returns:
            Localization key for error if invalid, None if valid.
        """
        active_players = self.get_active_players()
        num_players = len(active_players)

        # Parse old display format if needed
        if " " in team_mode or any(c.isupper() for c in team_mode if c != "v"):
            team_mode = TeamManager.parse_display_to_team_mode(team_mode)

        # Check if team mode is valid for player count
        if not TeamManager.is_valid_team_mode(team_mode, num_players):
            return "game-error-invalid-team-mode"

        return None

    def _sync_table_status(self) -> None:
        """Synchronize table status with game status."""
        if self._table:
            self._table.status = self.status

    def _replace_with_bot(self, player: "Player") -> None:
        """Replace a human player with a bot (shared logic)."""
        if self.status != "playing":
            return

        player.replaced_human = True
        player.is_bot = True
        self._users.pop(player.id, None)

        bot_user = Bot(player.name, uuid=player.id)
        self.attach_user(player.id, bot_user)

    @abstractmethod
    def on_start(self) -> None:
        """Start game logic after lobby transitions to playing."""
        ...

    def on_tick(self) -> None:
        """Run per-tick logic (50ms). Override for bots/timers.

        Subclasses should call super().on_tick() to ensure base functionality runs.
        """
        self.process_scheduled_sounds()
        # Check if duration estimation has completed
        self.check_estimate_completion()

    def on_round_timer_ready(self) -> None:
        """Handle round-timer expiry for games using RoundTransitionTimer."""
        pass

    # Player management

    def attach_user(self, player_id: str, user: User) -> None:
        """Attach a user to a player by ID."""
        self._users[player_id] = user
        # Play current music/ambience for the joining user
        if self.current_music:
            user.play_music(self.current_music)
        if self.current_ambience:
            user.play_ambience(self.current_ambience)

    def get_user(self, player: Player) -> User | None:
        """Get the user for a player."""
        return self._users.get(player.id)

    def get_player_by_id(self, player_id: str) -> Player | None:
        """Get a player by ID (UUID)."""
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def get_player_by_name(self, name: str) -> Player | None:
        """Get a player by display name. Note: Names may not be unique."""
        for player in self.players:
            if player.name == name:
                return player
        return None

    def _reset_transcripts(self) -> None:
        """Initialize transcript storage for seated players."""
        self._transcripts = {player.id: [] for player in self.players if not player.is_spectator}

    def record_transcript_event(
        self, player: Player | None, text: str, buffer: str = "table"
    ) -> None:
        """Store a transcript entry for a player."""
        if not player or player.is_spectator:
            return
        self._transcripts.setdefault(player.id, []).append({"text": text, "buffer": buffer})

    def get_transcript(self, player_id: str) -> list[dict[str, str]]:
        """Return the transcript history for a player."""
        return list(self._transcripts.get(player_id, []))

    @property
    def team_manager(self) -> TeamManager:
        """Get the team manager for this game."""
        return self._team_manager
