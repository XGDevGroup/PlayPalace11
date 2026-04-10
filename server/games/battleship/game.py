"""
Battleship Game Implementation for PlayPalace v11.

Classic naval combat on a 2D grid.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import TYPE_CHECKING

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.grid_mixin import GridGameMixin, GridCursor
from ...game_utils.options import MenuOption, BoolOption, option_field
from ...game_utils.poker_timer import PokerTurnTimer
from ...game_utils.turn_timer_mixin import TurnTimerMixin
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState
from server.core.users.base import MenuItem, EscapeBehavior
from .bot import bot_think as _bot_think

if TYPE_CHECKING:
    from server.core.users.base import User

# ------------------------------------------------------------------ #
# Constants                                                            #
# ------------------------------------------------------------------ #

SOUND_FIRE = "game_battleship/fire.ogg"
SOUND_MISS = "game_battleship/miss.ogg"
SOUND_HIT = "game_battleship/hit.ogg"
SOUND_SUNK = [
    "game_battleship/sunk1.ogg",
    "game_battleship/sunk2.ogg",
]
SOUND_PLACE = "game_battleship/place.ogg"
SOUND_DEPLOY_DONE = "game_battleship/deploy_done.ogg"
SOUND_WIN = "game_pig/wingame.ogg"
SOUND_LOSE = "game_pig/lose.ogg"
SOUND_MUSIC = "game_battleship/mus.ogg"

# Timing: 1.0s delay between fire and result (20 ticks/sec)
FIRE_DELAY_TICKS = 20

# Cell state constants
CELL_EMPTY = 0
CELL_SHIP = 1
CELL_MISS = 2
CELL_HIT = 3

# Ship definitions: (type_key, size)
FLEET = [
    ("carrier", 5),
    ("battleship", 4),
    ("destroyer", 3),
    ("submarine", 3),
    ("patrol", 2),
]

GRID_SIZE_CHOICES = ["6", "8", "10", "12"]
GRID_SIZE_LABELS = {
    "6": "battleship-grid-6x6",
    "8": "battleship-grid-8x8",
    "10": "battleship-grid-10x10",
    "12": "battleship-grid-12x12",
}

PLACEMENT_CHOICES = ["auto", "manual"]
PLACEMENT_LABELS = {
    "auto": "battleship-placement-auto",
    "manual": "battleship-placement-manual",
}

ORIENTATION_CHOICES = ["horizontal", "vertical"]


# ------------------------------------------------------------------ #
# Data classes                                                         #
# ------------------------------------------------------------------ #


@dataclass
class Ship(DataClassJSONMixin):
    """A ship placed on a player's board."""

    type_key: str
    size: int
    row: int = 0
    col: int = 0
    horizontal: bool = True
    hits: int = 0

    @property
    def sunk(self) -> bool:
        return self.hits >= self.size

    def cells(self) -> list[tuple[int, int]]:
        """Return all (row, col) cells occupied by this ship."""
        result = []
        for i in range(self.size):
            if self.horizontal:
                result.append((self.row, self.col + i))
            else:
                result.append((self.row + i, self.col))
        return result


@dataclass
class BattleshipPlayer(Player):
    """Player with own board, shot tracking, and ship fleet."""

    # own_board[row][col] = CELL_EMPTY or CELL_SHIP
    own_board: list[list[int]] = field(default_factory=list)
    # shot_board[row][col] = CELL_EMPTY, CELL_MISS, or CELL_HIT
    shot_board: list[list[int]] = field(default_factory=list)
    ships: list[Ship] = field(default_factory=list)
    ships_placed: int = 0
    deploy_ready: bool = False
    viewing_own: bool = True  # True = own board, False = opponent shots
    total_shots: int = 0
    total_hits: int = 0


@dataclass
class BattleshipOptions(GameOptions):
    grid_size: str = option_field(
        MenuOption(
            choices=GRID_SIZE_CHOICES,
            default="10",
            value_key="size",
            label="battleship-set-grid-size",
            prompt="battleship-select-grid-size",
            change_msg="battleship-option-changed-grid-size",
            choice_labels=GRID_SIZE_LABELS,
            description="battleship-desc-grid-size",
        )
    )
    placement_mode: str = option_field(
        MenuOption(
            choices=PLACEMENT_CHOICES,
            default="auto",
            value_key="mode",
            label="battleship-set-placement-mode",
            prompt="battleship-select-placement-mode",
            change_msg="battleship-option-changed-placement-mode",
            choice_labels=PLACEMENT_LABELS,
            description="battleship-desc-placement-mode",
        )
    )
    replay_on_hit: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="battleship-set-replay-on-hit",
            change_msg="battleship-option-changed-replay-on-hit",
            description="battleship-desc-replay-on-hit",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=["0", "30", "45", "60"],
            default="0",
            value_key="seconds",
            label="battleship-set-turn-timer",
            prompt="battleship-select-turn-timer",
            change_msg="battleship-option-changed-turn-timer",
            choice_labels={
                "0": "battleship-timer-off",
                "30": "battleship-timer-30",
                "45": "battleship-timer-45",
                "60": "battleship-timer-60",
            },
            description="battleship-desc-turn-timer",
        )
    )


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #


def _make_board(size: int, fill: int = CELL_EMPTY) -> list[list[int]]:
    return [[fill] * size for _ in range(size)]


def _can_place_ship(
    board: list[list[int]],
    size: int,
    row: int,
    col: int,
    horizontal: bool,
    grid_size: int,
) -> bool:
    """Check if a ship can be placed at the given position."""
    for i in range(size):
        r = row if horizontal else row + i
        c = col + i if horizontal else col
        if r < 0 or r >= grid_size or c < 0 or c >= grid_size:
            return False
        if board[r][c] != CELL_EMPTY:
            return False
    return True


def _place_ship_on_board(
    board: list[list[int]],
    ship: Ship,
) -> None:
    """Mark ship cells on the board."""
    for r, c in ship.cells():
        board[r][c] = CELL_SHIP


def _random_place_fleet(
    board: list[list[int]],
    grid_size: int,
    fleet: list[tuple[str, int]],
) -> list[Ship]:
    """Randomly place all ships. Returns list of placed Ships."""
    ships: list[Ship] = []
    for type_key, size in fleet:
        placed = False
        for _ in range(1000):  # safety limit
            horizontal = random.choice([True, False])
            if horizontal:
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - size)
            else:
                row = random.randint(0, grid_size - size)
                col = random.randint(0, grid_size - 1)
            if _can_place_ship(board, size, row, col, horizontal, grid_size):
                ship = Ship(
                    type_key=type_key,
                    size=size,
                    row=row,
                    col=col,
                    horizontal=horizontal,
                )
                _place_ship_on_board(board, ship)
                ships.append(ship)
                placed = True
                break
        if not placed:
            raise RuntimeError(f"Could not place {type_key} after 1000 attempts")
    return ships


def _get_opponent(
    game: "BattleshipGame",
    player: BattleshipPlayer,
) -> BattleshipPlayer | None:
    """Get the other player."""
    for p in game.get_active_players():
        if p.id != player.id:
            return p
    return None


# ------------------------------------------------------------------ #
# Game                                                                 #
# ------------------------------------------------------------------ #


@register_game
@dataclass
class BattleshipGame(GridGameMixin, TurnTimerMixin, Game):
    players: list[BattleshipPlayer] = field(default_factory=list)
    options: BattleshipOptions = field(default_factory=BattleshipOptions)

    # Grid mixin fields
    grid_rows: int = 10
    grid_cols: int = 10
    grid_cursors: dict[str, GridCursor] = field(default_factory=dict)
    grid_row_labels: list[str] = field(default_factory=list)
    grid_col_labels: list[str] = field(default_factory=list)

    # Turn timer
    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)
    _timer_warning_played: bool = False

    # Game phase: "deploying" or "battling"
    phase: str = "deploying"
    deploy_wait_ticks: int = 0

    # Placement state for manual mode
    placing_ship_index: dict[str, int] = field(default_factory=dict)
    placing_orientation_pending: dict[str, bool] = field(default_factory=dict)
    placing_row: dict[str, int] = field(default_factory=dict)
    placing_col: dict[str, int] = field(default_factory=dict)

    # Pending shot (fire.ogg → delay → result)
    # Stores (player_id, row, col) while the shell is "in flight"
    shot_pending_player_id: str = ""
    shot_pending_row: int = -1
    shot_pending_col: int = -1
    shot_pending_ticks: int = 0

    # ------------------------------------------------------------------ #
    # Class methods                                                       #
    # ------------------------------------------------------------------ #

    @classmethod
    def get_name(cls) -> str:
        return "Battleship"

    @classmethod
    def get_type(cls) -> str:
        return "battleship"

    @classmethod
    def get_category(cls) -> str:
        return "category-playaural"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 2

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(
        self,
        player_id: str,
        name: str,
        is_bot: bool = False,
    ) -> BattleshipPlayer:
        return BattleshipPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors: list[str | tuple[str, dict]] = []
        errors.extend(super().prestart_validate())
        return errors

    # ------------------------------------------------------------------ #
    # Action sets                                                         #
    # ------------------------------------------------------------------ #

    def create_turn_action_set(self, player: BattleshipPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        # Grid cell actions (from mixin)
        for action in self.build_grid_actions(player):
            action_set.add(action)

        # Grid nav actions (hidden, keybind-only)
        for action in self.build_grid_nav_actions():
            action_set.add(action)

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Toggle view (own board ↔ shot board)
        action_set.add(
            Action(
                id="toggle_view",
                label=Localization.get(locale, "battleship-toggle-view"),
                handler="_action_toggle_view",
                is_enabled="_is_toggle_view_enabled",
                is_hidden="_is_toggle_view_hidden",
            )
        )

        # Read fleet status
        action_set.add(
            Action(
                id="read_fleet",
                label=Localization.get(locale, "battleship-read-fleet"),
                handler="_action_read_fleet",
                is_enabled="_is_read_fleet_enabled",
                is_hidden="_is_read_fleet_hidden",
            )
        )

        # Read enemy fleet status (how many sunk)
        action_set.add(
            Action(
                id="read_enemy_fleet",
                label=Localization.get(locale, "battleship-read-enemy-fleet"),
                handler="_action_read_enemy_fleet",
                is_enabled="_is_read_enemy_fleet_enabled",
                is_hidden="_is_read_enemy_fleet_hidden",
            )
        )

        self._apply_standard_action_order(action_set, user)
        return action_set

    def _apply_standard_action_order(self, action_set: ActionSet, user: "User | None") -> None:
        custom_ids = ["toggle_view", "read_fleet", "read_enemy_fleet"]
        action_set._order = [aid for aid in action_set._order if aid not in custom_ids] + [
            aid for aid in custom_ids if action_set.get_action(aid)
        ]
        if user and getattr(user, "client_type", "") == "web":
            target_order = [
                "toggle_view",
                "read_fleet",
                "read_enemy_fleet",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            new_order = [aid for aid in action_set._order if aid not in target_order]
            for aid in target_order:
                if action_set.get_action(aid):
                    new_order.append(aid)
            action_set._order = new_order

    # ------------------------------------------------------------------ #
    # Keybinds                                                            #
    # ------------------------------------------------------------------ #

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.setup_grid_keybinds()
        self.define_keybind(
            "v",
            "Toggle view",
            ["toggle_view"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "f",
            "Read fleet",
            ["read_fleet"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "e",
            "Read enemy fleet",
            ["read_enemy_fleet"],
            state=KeybindState.ACTIVE,
        )

    # ------------------------------------------------------------------ #
    # Menu overrides                                                      #
    # ------------------------------------------------------------------ #

    def rebuild_player_menu(self, player: Player) -> None:
        self._sync_turn_actions(player)
        self._sync_standard_actions(player)
        super().rebuild_player_menu(player)

    def update_player_menu(
        self,
        player: Player,
        selection_id: str | None = None,
    ) -> None:
        self._sync_turn_actions(player)
        self._sync_standard_actions(player)
        super().update_player_menu(player, selection_id=selection_id)

    def rebuild_all_menus(self) -> None:
        for player in self.players:
            self._sync_turn_actions(player)
            self._sync_standard_actions(player)
        super().rebuild_all_menus()

    def _sync_turn_actions(self, player: Player) -> None:
        """Keep turn actions in sync with game phase."""
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return
        bp = self._as_bp(player)
        if not bp:
            return
        # No special reordering needed — grid cells only

    def _sync_standard_actions(self, player: Player) -> None:
        standard_set = self.get_action_set(player, "standard")
        if not standard_set:
            return
        self._apply_standard_action_order(standard_set, self.get_user(player))

    def _handle_menu_event(self, player: Player, event: dict) -> None:
        """Handle orientation sub-menu selection."""
        menu_id = event.get("menu_id")
        selection_id = event.get("selection_id", "")

        if menu_id == "orient_menu":
            self._pending_actions.pop(player.id, None)
            bp = self._as_bp(player)
            if not bp:
                self.rebuild_player_menu(player)
                return
            if selection_id == "_cancel" or not selection_id:
                # Cancel — reset pending and return to grid
                self.placing_orientation_pending[bp.id] = False
                self.rebuild_player_menu(bp)
                return
            horizontal = selection_id == "horizontal"
            self._try_place_ship(bp, horizontal)
            return

        super()._handle_menu_event(player, event)

    # ------------------------------------------------------------------ #
    # Game lifecycle                                                      #
    # ------------------------------------------------------------------ #

    def on_start(self) -> None:
        size = int(self.options.grid_size)
        self.grid_rows = size
        self.grid_cols = size
        self.status = GameStatus.PLAYING
        self._sync_table_status()
        self.game_active = True

        # Initialize boards for all active players
        for player in self.get_active_players():
            bp = self._as_bp(player)
            if bp:
                bp.own_board = _make_board(size)
                bp.shot_board = _make_board(size)
                bp.ships = []
                bp.ships_placed = 0
                bp.deploy_ready = False
                bp.viewing_own = True
                bp.total_shots = 0
                bp.total_hits = 0

        self._init_grid()

        # Rebuild turn action sets — they were created during lobby when
        # grid_rows/grid_cols were still at their default (10×10).
        for player in self.get_active_players():
            self.remove_action_set(player, "turn")
            turn_set = self.create_turn_action_set(player)
            if turn_set:
                # Insert at position 0 so turn set stays first
                sets = self.player_action_sets.get(player.id, [])
                sets.insert(0, turn_set)
                self.player_action_sets[player.id] = sets

        if self.options.placement_mode == "auto":
            self._auto_deploy_all()
        else:
            # Manual: initialize placing state
            for player in self.get_active_players():
                self.placing_ship_index[player.id] = 0
                self.placing_orientation_pending[player.id] = False
            self._announce_deploy_phase()

        self.rebuild_all_menus()

    def _auto_deploy_all(self) -> None:
        """Auto-place ships for all players, then start battle."""
        size = int(self.options.grid_size)
        for player in self.get_active_players():
            bp = self._as_bp(player)
            if not bp:
                continue
            bp.ships = _random_place_fleet(bp.own_board, size, FLEET)
            bp.ships_placed = len(FLEET)
            bp.deploy_ready = True
        self._start_battle()

    def _announce_deploy_phase(self) -> None:
        """Tell each player to start placing ships."""
        for player in self.get_active_players():
            bp = self._as_bp(player)
            user = self.get_user(player)
            if not bp or not user:
                continue
            ship_key, ship_size = FLEET[0]
            user.speak_l(
                "battleship-deploy-start",
                "game",
                ship=Localization.get(user.locale, f"battleship-ship-{ship_key}"),
                size=str(ship_size),
            )

    def _start_battle(self) -> None:
        """Transition from deploying to battling phase."""
        self.phase = "battling"
        # Switch all players to opponent view for battle
        for player in self.get_active_players():
            bp = self._as_bp(player)
            if bp:
                bp.viewing_own = False
        self.set_turn_players(self.get_active_players())
        self.play_music(SOUND_MUSIC)
        self.broadcast_l("battleship-battle-start", buffer="table")
        self.announce_turn()
        self._maybe_start_timer()
        self._jolt_bots()
        self.rebuild_all_menus()

    def _maybe_start_timer(self) -> None:
        try:
            seconds = int(self.options.turn_timer)
        except (ValueError, AttributeError):
            seconds = 0
        if seconds > 0:
            self.start_turn_timer()

    # ------------------------------------------------------------------ #
    # Grid mixin overrides                                                #
    # ------------------------------------------------------------------ #

    def get_cell_label(
        self,
        row: int,
        col: int,
        player: "Player",
        locale: str,
    ) -> str:
        """Return cell description based on phase and view mode."""
        bp = self._as_bp(player)
        coord = self._grid_cell_coordinate(row, col)
        if not bp or row >= self.grid_rows or col >= self.grid_cols:
            return coord
        if not bp.own_board:
            return coord

        if self.phase == "deploying":
            cell = bp.own_board[row][col]
            if cell == CELL_SHIP:
                ship_name = self._ship_name_at(bp, row, col, locale)
                return Localization.get(
                    locale,
                    "battleship-cell-ship-placed",
                    coord=coord,
                    ship=ship_name,
                )
            return Localization.get(
                locale,
                "battleship-cell-empty",
                coord=coord,
            )

        # Battle phase
        if bp.viewing_own:
            cell = bp.own_board[row][col]
            # Check if this cell has been hit by opponent
            opponent = _get_opponent(self, bp)
            opponent_shot = CELL_EMPTY
            if opponent:
                opponent_shot = opponent.shot_board[row][col]
            if opponent_shot == CELL_HIT:
                ship_name = self._ship_name_at(bp, row, col, locale)
                ship = self._find_ship_at(bp, row, col)
                if ship and ship.sunk:
                    return Localization.get(
                        locale,
                        "battleship-cell-own-sunk",
                        coord=coord,
                        ship=ship_name,
                    )
                return Localization.get(
                    locale,
                    "battleship-cell-own-hit",
                    coord=coord,
                    ship=ship_name,
                )
            if opponent_shot == CELL_MISS:
                return Localization.get(
                    locale,
                    "battleship-cell-own-miss",
                    coord=coord,
                )
            if cell == CELL_SHIP:
                ship_name = self._ship_name_at(bp, row, col, locale)
                return Localization.get(
                    locale,
                    "battleship-cell-own-ship",
                    coord=coord,
                    ship=ship_name,
                )
            return Localization.get(
                locale,
                "battleship-cell-empty",
                coord=coord,
            )
        else:
            # Viewing shot board (opponent's waters)
            cell = bp.shot_board[row][col]
            if cell == CELL_HIT:
                opponent = _get_opponent(self, bp)
                if opponent:
                    ship = self._find_ship_at(opponent, row, col)
                    if ship and ship.sunk:
                        ship_name = Localization.get(
                            locale,
                            f"battleship-ship-{ship.type_key}",
                        )
                        return Localization.get(
                            locale,
                            "battleship-cell-sunk",
                            coord=coord,
                            ship=ship_name,
                        )
                return Localization.get(
                    locale,
                    "battleship-cell-hit",
                    coord=coord,
                )
            if cell == CELL_MISS:
                return Localization.get(
                    locale,
                    "battleship-cell-miss",
                    coord=coord,
                )
            return Localization.get(
                locale,
                "battleship-cell-unknown",
                coord=coord,
            )

    def on_grid_select(self, player: "Player", row: int, col: int) -> None:
        """Handle cell selection based on phase."""
        bp = self._as_bp(player)
        if not bp:
            return

        if self.phase == "deploying":
            self._on_deploy_select(bp, row, col)
        elif self.phase == "battling":
            self._on_battle_select(bp, row, col)

    def is_grid_cell_enabled(
        self,
        player: "Player",
        row: int,
        col: int,
    ) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if row >= self.grid_rows or col >= self.grid_cols:
            return "action-not-available"
        if player.is_spectator:
            return "action-spectator"
        bp = self._as_bp(player)
        if not bp:
            return "action-not-available"

        if self.phase == "deploying":
            if bp.deploy_ready:
                return "battleship-deploy-complete"
            return None

        # Battle phase — all cells remain enabled (visible in grid).
        # Invalid targets are handled in _on_battle_select with feedback.
        return None

    def is_grid_cell_hidden(
        self,
        player: "Player",
        row: int,
        col: int,
    ) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if row >= self.grid_rows or col >= self.grid_cols:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # ------------------------------------------------------------------ #
    # Deployment logic                                                     #
    # ------------------------------------------------------------------ #

    def _on_deploy_select(
        self,
        bp: BattleshipPlayer,
        row: int,
        col: int,
    ) -> None:
        """Handle cell selection during deployment."""
        if bp.deploy_ready:
            return

        user = self.get_user(bp)
        if not user:
            return

        ship_idx = self.placing_ship_index.get(bp.id, 0)
        if ship_idx >= len(FLEET):
            return

        # Store selected position and show orientation sub-menu
        self.placing_row[bp.id] = row
        self.placing_col[bp.id] = col
        self.placing_orientation_pending[bp.id] = True

        ship_key, ship_size = FLEET[ship_idx]
        coord = self._grid_cell_coordinate(row, col)
        user.speak_l(
            "battleship-choose-orientation",
            "game",
            ship=Localization.get(user.locale, f"battleship-ship-{ship_key}"),
            coord=coord,
            size=str(ship_size),
        )

        # Show proper orientation selection sub-menu
        self._pending_actions[bp.id] = "orient_placement"
        h_label = Localization.get(user.locale, "battleship-orient-horizontal")
        v_label = Localization.get(user.locale, "battleship-orient-vertical")
        cancel_label = Localization.get(user.locale, "cancel")
        items = [
            MenuItem(text=h_label, id="horizontal"),
            MenuItem(text=v_label, id="vertical"),
            MenuItem(text=cancel_label, id="_cancel"),
        ]
        user.show_menu(
            "orient_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        return

    def _try_place_ship(
        self,
        bp: BattleshipPlayer,
        horizontal: bool,
    ) -> None:
        """Try to place ship at stored position with given orientation."""
        user = self.get_user(bp)
        if not user:
            return

        ship_idx = self.placing_ship_index.get(bp.id, 0)
        if ship_idx >= len(FLEET):
            return

        row = self.placing_row.get(bp.id, 0)
        col = self.placing_col.get(bp.id, 0)
        ship_key, ship_size = FLEET[ship_idx]
        size = int(self.options.grid_size)

        if not _can_place_ship(bp.own_board, ship_size, row, col, horizontal, size):
            coord = self._grid_cell_coordinate(row, col)
            orientation_key = "battleship-horizontal" if horizontal else "battleship-vertical"
            user.speak_l(
                "battleship-cannot-place",
                "game",
                ship=Localization.get(user.locale, f"battleship-ship-{ship_key}"),
                coord=coord,
                orientation=Localization.get(user.locale, orientation_key),
            )
            # Reset orientation pending so they can pick again
            self.placing_orientation_pending[bp.id] = False
            self.rebuild_player_menu(bp)
            return

        # Place the ship
        ship = Ship(
            type_key=ship_key,
            size=ship_size,
            row=row,
            col=col,
            horizontal=horizontal,
        )
        _place_ship_on_board(bp.own_board, ship)
        bp.ships.append(ship)
        bp.ships_placed += 1
        self.placing_orientation_pending[bp.id] = False

        user.play_sound(SOUND_PLACE)
        coord = self._grid_cell_coordinate(row, col)
        orientation_key = "battleship-horizontal" if horizontal else "battleship-vertical"
        user.speak_l(
            "battleship-ship-placed",
            "game",
            ship=Localization.get(user.locale, f"battleship-ship-{ship_key}"),
            coord=coord,
            orientation=Localization.get(user.locale, orientation_key),
        )

        # Move to next ship
        next_idx = ship_idx + 1
        self.placing_ship_index[bp.id] = next_idx
        if next_idx < len(FLEET):
            next_key, next_size = FLEET[next_idx]
            user.speak_l(
                "battleship-place-next-ship",
                "game",
                ship=Localization.get(user.locale, f"battleship-ship-{next_key}"),
                size=str(next_size),
            )
        else:
            bp.deploy_ready = True
            user.play_sound(SOUND_DEPLOY_DONE)
            user.speak_l("battleship-deploy-done", "game")
            self._check_all_deployed()

        self.rebuild_player_menu(bp)

    def _check_all_deployed(self) -> None:
        """Check if all players have finished deploying."""
        for player in self.get_active_players():
            bp = self._as_bp(player)
            if not bp or not bp.deploy_ready:
                return
        # All deployed — start battle after a brief delay
        self.deploy_wait_ticks = 40  # 2 seconds

    # ------------------------------------------------------------------ #
    # Battle logic                                                        #
    # ------------------------------------------------------------------ #

    def _on_battle_select(
        self,
        bp: BattleshipPlayer,
        row: int,
        col: int,
    ) -> None:
        """Handle firing a shot during battle phase."""
        if self.shot_pending_ticks > 0:
            return
        if self.current_player != bp:
            return
        if bp.viewing_own:
            user = self.get_user(bp)
            if user:
                user.speak_l("battleship-switch-to-shots", "game")
            return

        # Can't fire at already-shot cells
        if bp.shot_board[row][col] != CELL_EMPTY:
            user = self.get_user(bp)
            if user:
                user.speak_l("battleship-already-shot", "game")
            return

        self._fire_shot(bp, row, col)

    def _fire_shot(
        self,
        bp: BattleshipPlayer,
        row: int,
        col: int,
    ) -> None:
        """Initiate a shot: play fire sound and queue the result after delay."""
        opponent = _get_opponent(self, bp)
        if not opponent:
            return

        bp.total_shots += 1
        self.play_sound(SOUND_FIRE)

        # Store pending shot — result resolves after FIRE_DELAY_TICKS
        self.shot_pending_player_id = bp.id
        self.shot_pending_row = row
        self.shot_pending_col = col
        self.shot_pending_ticks = FIRE_DELAY_TICKS

    def _resolve_shot(self) -> None:
        """Resolve a pending shot after the fire delay has elapsed."""
        bp = self._as_bp(
            self.get_player_by_id(self.shot_pending_player_id),
        )
        if not bp:
            return
        row = self.shot_pending_row
        col = self.shot_pending_col

        opponent = _get_opponent(self, bp)
        if not opponent:
            return

        coord = self._grid_cell_coordinate(row, col)

        if opponent.own_board[row][col] == CELL_SHIP:
            # HIT
            bp.shot_board[row][col] = CELL_HIT
            bp.total_hits += 1

            # Find which ship was hit
            hit_ship = self._find_ship_at(opponent, row, col)
            if hit_ship:
                hit_ship.hits += 1

            self.play_sound(SOUND_HIT)

            if hit_ship and hit_ship.sunk:
                # Ship sunk! Play sunk sound almost immediately after hit
                self.schedule_sound(random.choice(SOUND_SUNK), delay_ticks=2)
                # Announce with per-player localized ship name and perspective
                for p in self.players:
                    u = self.get_user(p)
                    if not u:
                        continue
                    ship_name = Localization.get(
                        u.locale,
                        f"battleship-ship-{hit_ship.type_key}",
                    )
                    if p.id == bp.id:
                        u.speak_l("battleship-sunk-self", "game", ship=ship_name)
                    elif p.id == opponent.id:
                        u.speak_l(
                            "battleship-sunk-target",
                            "game",
                            player=bp.name,
                            ship=ship_name,
                        )
                    else:
                        u.speak_l(
                            "battleship-sunk-spectator",
                            "game",
                            player=bp.name,
                            target=opponent.name,
                            ship=ship_name,
                        )

                # Check win
                if self._all_ships_sunk(opponent):
                    self._handle_victory(bp)
                    return
            else:
                self._speak_perspective(
                    bp,
                    opponent,
                    "battleship-hit-self",
                    "battleship-hit-target",
                    "battleship-hit-spectator",
                    coord=coord,
                )

            self.stop_turn_timer()

            # Replay on hit: same player gets another turn
            if self.options.replay_on_hit:
                self._maybe_start_timer()
                self._jolt_bots()
                self.rebuild_all_menus()
                return

        else:
            # MISS
            bp.shot_board[row][col] = CELL_MISS
            self.play_sound(SOUND_MISS)
            self._speak_perspective(
                bp,
                opponent,
                "battleship-miss-self",
                "battleship-miss-target",
                "battleship-miss-spectator",
                coord=coord,
            )

        # Advance turn
        self.stop_turn_timer()
        self.advance_turn()
        self._maybe_start_timer()
        self._jolt_bots()

    def _find_ship_at(
        self,
        player: BattleshipPlayer,
        row: int,
        col: int,
    ) -> Ship | None:
        """Find the ship occupying the given cell."""
        for ship in player.ships:
            if (row, col) in ship.cells():
                return ship
        return None

    def _all_ships_sunk(self, player: BattleshipPlayer) -> bool:
        return all(ship.sunk for ship in player.ships)

    def _handle_victory(self, winner: BattleshipPlayer) -> None:
        """Handle game over when a player sinks all opponent ships."""
        loser = _get_opponent(self, winner)
        loser_name = loser.name if loser else ""
        # Personalized victory/defeat messages + sounds
        for p in self.players:
            u = self.get_user(p)
            if not u:
                continue
            if p.id == winner.id:
                u.speak_l("battleship-victory-self", "game")
                u.play_sound(SOUND_WIN)
            elif loser and p.id == loser.id:
                u.speak_l(
                    "battleship-victory-target",
                    "game",
                    player=winner.name,
                )
                u.play_sound(SOUND_LOSE)
            else:
                u.speak_l(
                    "battleship-victory-spectator",
                    "game",
                    player=winner.name,
                    target=loser_name,
                )
                u.play_sound(SOUND_LOSE)

        self.stop_turn_timer()
        self.finish_game()

    # ------------------------------------------------------------------ #
    # Turn timer                                                          #
    # ------------------------------------------------------------------ #

    def _on_turn_timeout(self) -> None:
        """Auto-fire at a random valid cell when timer expires."""
        current = self.current_player
        if not current:
            return
        bp = self._as_bp(current)
        if not bp:
            return

        # Switch to shot view if needed
        bp.viewing_own = False

        # Find random untargeted cell
        target = self._random_valid_target(bp)
        if target:
            row, col = target
            user = self.get_user(bp)
            if user:
                coord = self._grid_cell_coordinate(row, col)
                user.speak_l("battleship-timeout-fire", "game", coord=coord)
            self._fire_shot(bp, row, col)
        else:
            self.advance_turn()
            self._maybe_start_timer()

    def _random_valid_target(
        self,
        bp: BattleshipPlayer,
    ) -> tuple[int, int] | None:
        """Pick a random un-shot cell."""
        size = int(self.options.grid_size)
        candidates = [
            (r, c) for r in range(size) for c in range(size) if bp.shot_board[r][c] == CELL_EMPTY
        ]
        return random.choice(candidates) if candidates else None

    # ------------------------------------------------------------------ #
    # Bot auto-deploy (internal only)                                      #
    # ------------------------------------------------------------------ #

    def _bot_auto_deploy(self, bp: BattleshipPlayer) -> None:
        """Auto-place all ships for a bot player."""
        size = int(self.options.grid_size)
        bp.own_board = _make_board(size)
        bp.ships = _random_place_fleet(bp.own_board, size, FLEET)
        bp.ships_placed = len(FLEET)
        bp.deploy_ready = True
        self.placing_ship_index[bp.id] = len(FLEET)
        self._check_all_deployed()

    # ------------------------------------------------------------------ #
    # Toggle view action                                                   #
    # ------------------------------------------------------------------ #

    def _action_toggle_view(
        self,
        player: "Player",
        action_id: str,
    ) -> None:
        bp = self._as_bp(player)
        if not bp:
            return
        bp.viewing_own = not bp.viewing_own
        user = self.get_user(player)
        if user:
            if bp.viewing_own:
                user.speak_l("battleship-view-own", "game")
            else:
                user.speak_l("battleship-view-shots", "game")
            # Announce current cell after switching
            cursor = self._get_cursor(bp)
            label = self.get_cell_label(cursor.row, cursor.col, bp, user.locale)
            user.speak(label, buffer="table")
        self.update_player_menu(bp)

    def _is_toggle_view_enabled(self, player: "Player") -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.phase == "deploying":
            return "battleship-deploy-in-progress"
        return None

    def _is_toggle_view_hidden(self, player: "Player") -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.phase == "deploying":
            return Visibility.HIDDEN
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ------------------------------------------------------------------ #
    # Fleet status actions                                                 #
    # ------------------------------------------------------------------ #

    def _action_read_fleet(
        self,
        player: "Player",
        action_id: str,
    ) -> None:
        bp = self._as_bp(player)
        if not bp:
            return
        user = self.get_user(player)
        if not user:
            return
        lines = [Localization.get(user.locale, "battleship-fleet-header")]
        for ship in bp.ships:
            ship_name = Localization.get(user.locale, f"battleship-ship-{ship.type_key}")
            if ship.sunk:
                status = Localization.get(user.locale, "battleship-status-sunk")
            elif ship.hits > 0:
                status = Localization.get(
                    user.locale,
                    "battleship-status-damaged",
                    hits=str(ship.hits),
                    size=str(ship.size),
                )
            else:
                status = Localization.get(user.locale, "battleship-status-intact")
            lines.append(f"{ship_name}: {status}")
        self.status_box(bp, lines)

    def _is_read_fleet_enabled(self, player: "Player") -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_read_fleet_hidden(self, player: "Player") -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _action_read_enemy_fleet(
        self,
        player: "Player",
        action_id: str,
    ) -> None:
        bp = self._as_bp(player)
        user = self.get_user(player)
        if not user:
            return

        # Find opponent
        opponent = None
        if bp:
            opponent = _get_opponent(self, bp)
        else:
            # Spectator — pick first active player's opponent
            active = self.get_active_players()
            if len(active) >= 2:
                opponent = active[1]

        if not opponent:
            return

        lines = [Localization.get(user.locale, "battleship-enemy-fleet-header")]
        sunk_count = sum(1 for s in opponent.ships if s.sunk)
        total = len(opponent.ships)
        lines.append(
            Localization.get(
                user.locale,
                "battleship-enemy-fleet-summary",
                sunk=str(sunk_count),
                total=str(total),
            )
        )
        for ship in opponent.ships:
            if ship.sunk:
                ship_name = Localization.get(
                    user.locale,
                    f"battleship-ship-{ship.type_key}",
                )
                lines.append(
                    Localization.get(
                        user.locale,
                        "battleship-enemy-ship-sunk",
                        ship=ship_name,
                        size=str(ship.size),
                    )
                )
        self.status_box(player, lines)

    def _is_read_enemy_fleet_enabled(self, player: "Player") -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.phase == "deploying":
            return "battleship-deploy-in-progress"
        return None

    def _is_read_enemy_fleet_hidden(self, player: "Player") -> Visibility:
        if self.status != "playing" or self.phase == "deploying":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ------------------------------------------------------------------ #
    # Whose turn / scores overrides for web visibility                    #
    # ------------------------------------------------------------------ #

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web" and self.status == "playing":
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    # ------------------------------------------------------------------ #
    # Tick                                                                 #
    # ------------------------------------------------------------------ #

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()

        if not self.game_active:
            return

        # Deploy wait (brief pause after all ships placed)
        if self.deploy_wait_ticks > 0:
            self.deploy_wait_ticks -= 1
            if self.deploy_wait_ticks == 0:
                self._start_battle()
            return

        # Bot deployment (no turn system during deploy)
        if self.phase == "deploying":
            for player in self.get_active_players():
                bp = self._as_bp(player)
                if bp and bp.is_bot and not bp.deploy_ready:
                    self._bot_auto_deploy(bp)
            return

        # Pending shot delay (shell in flight)
        if self.shot_pending_ticks > 0:
            self.shot_pending_ticks -= 1
            if self.shot_pending_ticks == 0:
                self._resolve_shot()
            return  # freeze game during shell flight

        # Turn timer
        if self.phase == "battling":
            self.on_tick_turn_timer()

        # Bot AI
        BotHelper.on_tick(self)

    # ------------------------------------------------------------------ #
    # Bot                                                                  #
    # ------------------------------------------------------------------ #

    def bot_think(self, player: BattleshipPlayer) -> str | None:
        return _bot_think(self, player)

    # ------------------------------------------------------------------ #
    # Game result                                                          #
    # ------------------------------------------------------------------ #

    def build_game_result(self) -> GameResult:
        active = self.get_active_players()
        winner = None
        for p in active:
            bp = self._as_bp(p)
            if bp:
                opponent = _get_opponent(self, bp)
                if opponent and self._all_ships_sunk(opponent):
                    winner = bp
                    break

        winner_ids = [winner.id] if winner else []
        custom = {
            "winner_ids": winner_ids,
            "winner_name": winner.name if winner else None,
        }
        # Add per-player stats
        for p in active:
            bp = self._as_bp(p)
            if bp:
                custom[f"{bp.name}_shots"] = bp.total_shots
                custom[f"{bp.name}_hits"] = bp.total_hits
                custom[f"{bp.name}_ships_lost"] = sum(1 for s in bp.ships if s.sunk)

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot and not p.replaced_human,
                )
                for p in active
            ],
            custom_data=custom,
        )

    def format_end_screen(
        self,
        result: GameResult,
        locale: str,
    ) -> list[str]:
        lines: list[str] = []
        winner_name = result.custom_data.get("winner_name")
        if winner_name:
            lines.append(
                Localization.get(
                    locale,
                    "battleship-winner-line",
                    player=winner_name,
                )
            )
        for pr in result.player_results:
            shots = result.custom_data.get(f"{pr.player_name}_shots", 0)
            hits = result.custom_data.get(f"{pr.player_name}_hits", 0)
            accuracy = (hits / shots * 100) if shots > 0 else 0
            lines.append(
                Localization.get(
                    locale,
                    "battleship-stats-line",
                    player=pr.player_name,
                    shots=str(shots),
                    hits=str(hits),
                    accuracy=f"{accuracy:.0f}",
                )
            )
        return lines

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _as_bp(self, player: "Player") -> BattleshipPlayer | None:
        if isinstance(player, BattleshipPlayer):
            return player
        return None

    def _jolt_bots(self) -> None:
        """Add a 2-5 second thinking delay to all bots."""
        for player in self.get_active_players():
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(40, 100))

    def _speak_perspective(
        self,
        shooter: BattleshipPlayer,
        opponent: BattleshipPlayer,
        key_self: str,
        key_target: str,
        key_spectator: str,
        **kwargs,
    ) -> None:
        """Send a personalized TTS message to each player/spectator."""
        for p in self.players:
            u = self.get_user(p)
            if not u:
                continue
            if p.id == shooter.id:
                u.speak_l(key_self, "game", **kwargs)
            elif p.id == opponent.id:
                u.speak_l(
                    key_target,
                    "game",
                    player=shooter.name,
                    target=opponent.name,
                    **kwargs,
                )
            else:
                u.speak_l(
                    key_spectator,
                    "game",
                    player=shooter.name,
                    target=opponent.name,
                    **kwargs,
                )

    def _ship_name_at(
        self,
        bp: BattleshipPlayer,
        row: int,
        col: int,
        locale: str,
    ) -> str:
        """Get the localized name of the ship at the given cell."""
        ship = self._find_ship_at(bp, row, col)
        if ship:
            return Localization.get(locale, f"battleship-ship-{ship.type_key}")
        return Localization.get(locale, "battleship-ship-unknown")
