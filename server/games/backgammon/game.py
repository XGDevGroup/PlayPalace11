"""Backgammon game for PlayPalace."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
import random

log = logging.getLogger(__name__)

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.options import IntOption, BoolOption, MenuOption, option_field
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState
from server.core.users.bot import Bot
from server.core.users.base import User, MenuItem, EscapeBehavior
from .bot import bot_think, cleanup_gnubg
from .moves import (
    BackgammonMove,
    apply_move,
    generate_legal_moves,
    has_any_legal_move,
    must_use_both_dice,
    undo_last_move,
)
from .state import (
    BackgammonGameState,
    BackgammonBoardState,
    INITIAL_BOARD,
    all_checkers_in_home,
    bar_count,
    build_initial_game_state,
    color_sign,
    game_multiplier,
    off_count,
    opponent_color,
    pip_count,
    point_count,
    point_number_for_player,
    point_owner,
    remaining_dice,
    remaining_dice_unique,
    roll_dice,
    set_bar,
    set_off,
)


BOT_DIFFICULTY_CHOICES = [
    "random",
    "simple",
    "gnubg_0ply",
    "gnubg_1ply",
    "gnubg_2ply",
    "whackgammon",
]
BOT_DIFFICULTY_LABELS = {
    "random": "backgammon-difficulty-random",
    "simple": "backgammon-difficulty-simple",
    "gnubg_0ply": "backgammon-difficulty-gnubg-0ply",
    "gnubg_1ply": "backgammon-difficulty-gnubg-1ply",
    "gnubg_2ply": "backgammon-difficulty-gnubg-2ply",
    "whackgammon": "backgammon-difficulty-whackgammon",
}
# Maps difficulty name to GNUBG ply depth (None = no GNUBG)
DIFFICULTY_PLY = {
    "random": None,
    "simple": None,  # Algorithmic heuristic, no GNUBG
    "gnubg_0ply": 0,
    "gnubg_1ply": 1,
    "gnubg_2ply": 2,
    "whackgammon": 0,
}


@dataclass
class BackgammonOptions(GameOptions):
    """Configurable options for Backgammon."""

    match_length: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=25,
            value_key="match_length",
            label="backgammon-option-match-length",
            prompt="backgammon-option-select-match-length",
            change_msg="backgammon-option-changed-match-length",
        )
    )
    bot_difficulty: str = option_field(
        MenuOption(
            default="simple",
            choices=BOT_DIFFICULTY_CHOICES,
            choice_labels=BOT_DIFFICULTY_LABELS,
            value_key="bot_difficulty",
            label="backgammon-option-bot-difficulty",
            prompt="backgammon-option-select-bot-difficulty",
            change_msg="backgammon-option-changed-bot-difficulty",
        )
    )
    hints_enabled: bool = option_field(
        BoolOption(
            default=False,
            value_key="hints_enabled",
            label="backgammon-option-hints",
            change_msg="backgammon-option-changed-hints",
        )
    )
    cube_hints_enabled: bool = option_field(
        BoolOption(
            default=False,
            value_key="cube_hints_enabled",
            label="backgammon-option-cube-hints",
            change_msg="backgammon-option-changed-cube-hints",
        )
    )


@dataclass
class BackgammonPlayer(Player):
    """Player state for Backgammon."""

    color: str = ""  # "red" or "white"


@register_game
@dataclass
class BackgammonGame(Game):
    """Backgammon with accessibility-first design."""

    relevant_preferences = ["brief_announcements"]

    players: list[BackgammonPlayer] = field(default_factory=list)
    options: BackgammonOptions = field(default_factory=BackgammonOptions)
    game_state: BackgammonGameState = field(default_factory=BackgammonGameState)

    # Track which dice the must-use-both rule restricts to
    _forced_dice: list[int] | None = None
    # Queued bot actions from GNUBG (full turn planned at once)
    _bot_goals: list[tuple[int, int]] = field(default_factory=list)

    # Ctrl+Up/Down navigation cursor
    _nav_cursor: int | None = None
    _nav_selected_source: int | None = None
    _nav_skip_rebuild: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "Backgammon"

    @classmethod
    def get_type(cls) -> str:
        return "backgammon"

    @classmethod
    def get_category(cls) -> str:
        return "category-board-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 2

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> BackgammonPlayer:
        return BackgammonPlayer(id=player_id, name=name, is_bot=is_bot)

    def add_player(self, name: str, user: User) -> BackgammonPlayer:
        player = super().add_player(name, user)
        return player

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        if user:
            return user.locale
        return "en"

    def _get_player_by_color(self, color: str) -> BackgammonPlayer | None:
        for p in self.players:
            if isinstance(p, BackgammonPlayer) and p.color == color:
                return p
        return None

    def _current_bg_player(self) -> BackgammonPlayer | None:
        p = self.current_player
        return p if isinstance(p, BackgammonPlayer) else None

    # ==========================================================================
    # Action sets
    # ==========================================================================

    def create_turn_action_set(self, player: BackgammonPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        locale = self._player_locale(player)

        # 24 point actions in grid order: 2 rows x 12 cols
        # Top row (L→R): points 13-24 (indices 12-23)
        # Bottom row (L→R): points 12-1 (indices 11-0)
        for idx in self._grid_indices():
            action_set.add(
                Action(
                    id=f"point_{idx}",
                    label="",
                    handler="_action_point_click",
                    is_enabled="_is_point_enabled",
                    is_hidden="_is_point_hidden",
                    get_label="_get_point_label",
                    get_sound="_get_point_sound",
                    show_in_actions_menu=False,
                    show_disabled_label=False,
                )
            )

        # Offer double (keybind-triggered, hidden from menu)
        action_set.add(
            Action(
                id="offer_double",
                label=Localization.get(locale, "backgammon-label-double"),
                handler="_action_offer_double",
                is_enabled="_is_offer_double_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
            )
        )

        # Doubling response (shown as modal menu items when in doubling phase)
        action_set.add(
            Action(
                id="accept_double",
                label=Localization.get(locale, "backgammon-accept"),
                handler="_action_accept_double",
                is_enabled="_is_accept_double_enabled",
                is_hidden="_is_accept_double_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="drop_double",
                label=Localization.get(locale, "backgammon-drop"),
                handler="_action_drop_double",
                is_enabled="_is_drop_double_enabled",
                is_hidden="_is_drop_double_hidden",
                show_in_actions_menu=False,
            )
        )

        # Undo (keybind-triggered, hidden from menu)
        action_set.add(
            Action(
                id="undo_move",
                label=Localization.get(locale, "backgammon-label-undo"),
                handler="_action_undo_move",
                is_enabled="_is_undo_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
            )
        )

        # Hint (keybind-triggered, hidden from menu)
        action_set.add(
            Action(
                id="get_hint",
                label=Localization.get(locale, "backgammon-label-hint"),
                handler="_action_get_hint",
                is_enabled="_is_hint_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
            )
        )

        # Cube hint (keybind-triggered, hidden from menu)
        action_set.add(
            Action(
                id="get_cube_hint",
                label=Localization.get(locale, "backgammon-label-cube-hint"),
                handler="_action_get_cube_hint",
                is_enabled="_is_cube_hint_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
            )
        )

        # Navigation (ctrl+up/down, hidden from menu)
        action_set.add(
            Action(
                id="navigate_next",
                label="Next",
                handler="_action_navigate_next",
                is_enabled="_is_navigate_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="navigate_prev",
                label="Previous",
                handler="_action_navigate_prev",
                is_enabled="_is_navigate_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="deselect",
                label="Deselect",
                handler="_action_deselect",
                is_enabled="_is_deselect_enabled",
                is_hidden="_is_always_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        local_actions = [
            Action(
                id="check_status",
                label=Localization.get(locale, "backgammon-check-status"),
                handler="_action_check_status",
                is_enabled="_is_info_enabled",
                is_hidden="_is_always_hidden",
            ),
            Action(
                id="check_pip",
                label=Localization.get(locale, "backgammon-check-pip"),
                handler="_action_check_pip",
                is_enabled="_is_info_enabled",
                is_hidden="_is_always_hidden",
            ),
            Action(
                id="check_score",
                label=Localization.get(locale, "backgammon-check-score"),
                handler="_action_check_score",
                is_enabled="_is_info_enabled",
                is_hidden="_is_always_hidden",
            ),
            Action(
                id="check_cube",
                label=Localization.get(locale, "backgammon-check-cube"),
                handler="_action_check_cube",
                is_enabled="_is_info_enabled",
                is_hidden="_is_always_hidden",
            ),
            Action(
                id="check_dice",
                label=Localization.get(locale, "backgammon-check-dice"),
                handler="_action_check_dice",
                is_enabled="_is_info_enabled",
                is_hidden="_is_always_hidden",
            ),
        ]
        for action in reversed(local_actions):
            action_set.add(action)
            if action.id in action_set._order:
                action_set._order.remove(action.id)
            action_set._order.insert(0, action.id)

        # Hide base score actions — we use our own check_score
        for action_id in ("check_scores", "check_scores_detailed"):
            existing = action_set.get_action(action_id)
            if existing:
                existing.show_in_actions_menu = False

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()

        # Remove base class's score keybinds — we use our own
        if "s" in self._keybinds:
            self._keybinds["s"] = []
        if "shift+s" in self._keybinds:
            self._keybinds["shift+s"] = []

        # Rolling is done by pressing enter on any grid point (no dedicated key)
        self.define_keybind("shift+d", "Double", ["offer_double"], state=KeybindState.ACTIVE)
        self.define_keybind("y", "Accept double", ["accept_double"], state=KeybindState.ACTIVE)
        self.define_keybind("n", "Drop double", ["drop_double"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "e", "Status", ["check_status"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "d", "Cube", ["check_cube"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "p", "Pip count", ["check_pip"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind("u", "Undo", ["undo_move"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "s", "Score", ["check_score"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "c", "Dice", ["check_dice"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind("h", "Hint", ["get_hint"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+h", "Cube hint", ["get_cube_hint"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "ctrl+down", "Next destination", ["navigate_next"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "ctrl+right", "Next destination", ["navigate_next"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "ctrl+up", "Previous destination", ["navigate_prev"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "ctrl+left", "Previous destination", ["navigate_prev"], state=KeybindState.ACTIVE
        )
        self.define_keybind("ctrl+backspace", "Deselect", ["deselect"], state=KeybindState.ACTIVE)

    # ==========================================================================
    # Grid helpers
    # ==========================================================================

    def _grid_indices(self) -> list[int]:
        """Return point indices in grid order for Red's perspective.

        The board is a 1D track (points 1-24) folded into a U.
        Home board is on the RIGHT (like a physical board in front of you):
          Top row (L→R):  13 14 15 16 17 18 | 19 20 21 22 23 24
          Bottom row (L→R): 12 11 10  9  8  7 |  6  5  4  3  2  1

        Home board (1-6) is bottom-right. Opponent enters top-left.
        For White, rebuild_player_menu swaps the two halves so both
        players see their own home at bottom-right.
        """
        top = list(range(12, 24))  # indices 12,13,...,23 (pts 13→24)
        bottom = list(range(11, -1, -1))  # indices 11,10,...,0  (pts 12→1)
        return top + bottom

    # ==========================================================================
    # Ctrl+Up/Down navigation
    # ==========================================================================

    def _action_navigate_next(self, player: Player, action_id: str) -> None:
        if isinstance(player, BackgammonPlayer):
            self._navigate(player, direction=1)

    def _action_navigate_prev(self, player: Player, action_id: str) -> None:
        if isinstance(player, BackgammonPlayer):
            self._navigate(player, direction=-1)

    def _action_deselect(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state
        if gs.selected_source is not None:
            gs.selected_source = None
            self.play_sound("game_chess/setdown.ogg")
            self.rebuild_all_menus()

    def _navigate(self, player: BackgammonPlayer, direction: int) -> None:
        """Cycle through navigation targets with ctrl+up/down.

        With a piece selected: cycle destinations (blots first).
        Without selection: cycle source squares with legal moves,
        or bar entry destinations if on the bar.
        """
        gs = self.game_state
        if gs.turn_phase != "moving" or player.color != gs.current_color:
            return

        color = player.color
        selected = gs.selected_source

        # Reset cursor when selection state changes
        if selected != self._nav_selected_source:
            self._nav_cursor = None
            self._nav_selected_source = selected

        if selected is not None:
            targets = self._get_navigation_destinations(color, selected)
        elif bar_count(gs, color) > 0:
            targets = self._get_navigation_destinations(color, -1)
        else:
            targets = self._get_navigation_sources(color)

        if not targets:
            return

        if self._nav_cursor is not None and self._nav_cursor in targets:
            idx = targets.index(self._nav_cursor)
            idx = (idx + direction) % len(targets)
        else:
            idx = 0 if direction == 1 else len(targets) - 1

        self._nav_cursor = targets[idx]
        self._nav_skip_rebuild = True
        self.update_player_menu(
            player,
            selection_id=f"point_{targets[idx]}",
            play_selection_sound=True,
        )

    def _get_navigation_destinations(self, color: str, source: int) -> list[int]:
        """Destinations for source, ordered: opponent blots, own blots, other."""
        gs = self.game_state
        sign = color_sign(color)

        destinations: set[int] = set()
        for die_val in self._get_usable_dice():
            for m in generate_legal_moves(gs, color, die_val):
                if m.source == source and not m.is_bear_off:
                    destinations.add(m.destination)

        opponent_blots: list[int] = []
        own_blots: list[int] = []
        other: list[int] = []

        for dest in destinations:
            val = gs.board.points[dest]
            if val * sign < 0:
                opponent_blots.append(dest)
            elif val * sign > 0 and abs(val) == 1:
                own_blots.append(dest)
            else:
                other.append(dest)

        key = lambda idx: point_number_for_player(idx, color)
        opponent_blots.sort(key=key)
        own_blots.sort(key=key)
        other.sort(key=key)

        return opponent_blots + own_blots + other

    def _get_navigation_sources(self, color: str) -> list[int]:
        """Source points that have legal moves, sorted by point number."""
        gs = self.game_state
        sources: set[int] = set()
        for die_val in self._get_usable_dice():
            for m in generate_legal_moves(gs, color, die_val):
                if m.source >= 0:
                    sources.add(m.source)
        return sorted(sources, key=lambda idx: point_number_for_player(idx, color))

    # ==========================================================================
    # Menu overrides (grid mode)
    # ==========================================================================

    def update_player_menu(
        self,
        player: "Player",
        selection_id: str | None = None,
        play_selection_sound: bool = False,
    ) -> None:
        if self._destroyed or self.status == "finished":
            return
        if self._is_transient_display_open(player):
            return
        user = self.get_user(player)
        if not user:
            return

        point_items, other_items = self._build_menu_items(player, user)
        if isinstance(player, BackgammonPlayer) and player.color == "white":
            point_items = point_items[12:] + point_items[:12]

        user.update_menu(
            "turn_menu",
            point_items + other_items,
            selection_id=selection_id,
            play_selection_sound=play_selection_sound,
        )

    def _build_menu_items(self, player: "Player", user) -> tuple[list[MenuItem], list[MenuItem]]:
        """Build point items and other items for the turn menu."""
        point_items: list[MenuItem] = []
        other_items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            label = resolved.label
            if not resolved.enabled and resolved.action.show_disabled_label:
                unavailable = Localization.get(user.locale, "visibility-unavailable")
                label = f"{label}; {unavailable}"
            item = MenuItem(text=label, id=resolved.action.id, sound=resolved.sound)
            if resolved.action.id.startswith("point_"):
                point_items.append(item)
            else:
                other_items.append(item)
        return point_items, other_items

    def rebuild_player_menu(
        self,
        player: "Player",
        *,
        position: int | None = None,
        play_selection_sound: bool = False,
    ) -> None:
        if self._destroyed or self.status == "finished":
            return
        if self._is_transient_display_open(player):
            return
        user = self.get_user(player)
        if not user:
            return

        point_items, other_items = self._build_menu_items(player, user)
        use_grid = len(point_items) == 24

        # Flip for White: swap the two 12-item row halves so both
        # players see their own home board at bottom-left.
        if use_grid and isinstance(player, BackgammonPlayer) and player.color == "white":
            point_items = point_items[12:] + point_items[:12]

        user.show_menu(
            "turn_menu",
            point_items + other_items,
            multiletter=False,
            escape_behavior=EscapeBehavior.KEYBIND,
            position=position,
            grid_enabled=use_grid,
            grid_width=12 if use_grid else 1,
            play_selection_sound=play_selection_sound,
        )

    # ==========================================================================
    # Game flow
    # ==========================================================================

    def on_start(self) -> None:
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 1

        active_players = [p for p in self.players if not p.is_spectator]
        self.set_turn_players(active_players, reset_index=True)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Assign colors randomly
        if random.random() < 0.5:  # nosec B311
            active_players[0].color = "red"
            active_players[1].color = "white"
        else:
            active_players[0].color = "white"
            active_players[1].color = "red"

        self.game_state = build_initial_game_state(
            match_length=self.options.match_length,
        )

        red_player = self._get_player_by_color("red")
        white_player = self._get_player_by_color("white")
        self.broadcast_l(
            "backgammon-game-started",
            red=red_player.name if red_player else "?",
            white=white_player.name if white_player else "?",
        )

        # Opening roll
        self._do_opening_roll()
        BotHelper.jolt_bots(self, ticks=random.randint(4, 8))

    def _do_opening_roll(self) -> None:
        """Roll one die each for opening; higher goes first."""
        gs = self.game_state
        gs.opening_roll = True

        d1, d2 = roll_dice()
        while d1 == d2:
            self.broadcast_l("backgammon-opening-tie", die=d1)
            d1, d2 = roll_dice()

        gs.opening_die_red = d1
        gs.opening_die_white = d2

        red_player = self._get_player_by_color("red")
        white_player = self._get_player_by_color("white")

        self.broadcast_l(
            "backgammon-opening-roll",
            red=red_player.name if red_player else "Red",
            red_die=d1,
            white=white_player.name if white_player else "White",
            white_die=d2,
        )
        self._play_dice_sound()

        if d1 > d2:
            first_color = "red"
        else:
            first_color = "white"

        gs.current_color = first_color
        gs.dice = [d1, d2]
        gs.dice_used = [False, False]
        gs.opening_roll = False
        gs.turn_phase = "moving"

        first_player = self._get_player_by_color(first_color)
        if first_player:
            self.current_player = first_player

        winner_name = first_player.name if first_player else first_color
        self.broadcast_l(
            "backgammon-opening-winner",
            player=winner_name,
            die1=d1,
            die2=d2,
        )

        self._check_forced_dice()
        if not has_any_legal_move(gs, first_color):
            self.broadcast_l("backgammon-no-moves", player=winner_name)
            self._end_moving_phase()
        else:
            self.rebuild_all_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return
        self._check_pending_hint()

        # During doubling phase, the responder is the OPPONENT of current_player.
        # BotHelper.on_tick only processes current_player, so we handle this case
        # explicitly: find the opponent bot and run their think/execute cycle.
        gs = self.game_state
        if gs.turn_phase == "doubling":
            opp_color = opponent_color(gs.current_color)
            opp = self._get_player_by_color(opp_color)
            if opp and opp.is_bot:
                BotHelper.process_bot_action(
                    bot=opp,
                    think_fn=lambda: self.bot_think(opp),
                    execute_fn=lambda action_id: self.execute_action(opp, action_id),
                )
            return  # Don't run normal BotHelper — doubler shouldn't act now

        BotHelper.on_tick(self)

    def _check_pending_hint(self) -> None:
        """Check if an async hint query has completed."""
        future = getattr(self, "_hint_future", None)
        if future is None or not future.done():
            return
        self._hint_future = None
        try:
            result = future.result(timeout=0)
            if result:
                msg_key = result.pop("message_key")
                self.broadcast_l(msg_key, **result)
            else:
                self.broadcast_l("backgammon-hint-unavailable")
        except Exception:
            self.broadcast_l("backgammon-hint-unavailable")

    def bot_think(self, player: BackgammonPlayer) -> str | None:
        return bot_think(self, player)

    def execute_action(self, player, action_id, input_value=None, context=None):
        """Override to handle bot combined move format: point_{src}_{dst}."""
        if action_id and action_id.startswith("point_") and action_id.count("_") == 2:
            if isinstance(player, BackgammonPlayer):
                self._action_point_click(player, action_id)
                return
        super().execute_action(player, action_id, input_value=input_value, context=context)

    def _should_rebuild_after_keybind(self, player, executed_any: bool) -> bool:
        """Skip auto-rebuild when navigation already sent an update."""
        if self._nav_skip_rebuild:
            self._nav_skip_rebuild = False
            return False
        return super()._should_rebuild_after_keybind(player, executed_any)

    # ==========================================================================
    # Point click handler (roll + select + move)
    # ==========================================================================

    def _action_point_click(self, player: Player, action_id: str) -> None:
        """Handle point click — roll, select source, or select destination."""
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state

        # Pre-roll: pressing enter on any point rolls
        if gs.turn_phase == "pre_roll" and player.color == gs.current_color:
            self._do_roll(player)
            return

        if gs.turn_phase != "moving":
            return
        if player.color != gs.current_color:
            return

        parts = action_id.split("_")
        # Bot combined move: point_{src}_{dst}
        if len(parts) == 3:
            try:
                src = int(parts[1])
                dst = int(parts[2])
            except ValueError:
                return
            self._try_apply_move_direct(player, src, dst)
            return

        try:
            point_idx = int(parts[1])
        except (ValueError, IndexError):
            return

        color = player.color
        selected = gs.selected_source

        if selected is None:
            # First click: select source
            self._try_select_source(player, point_idx)
        else:
            # Second click: destination
            if selected == point_idx:
                # Double-click same point: try bear off, else deselect
                if not self._try_bear_off(player, point_idx):
                    gs.selected_source = None
                    self.play_sound("game_chess/setdown.ogg")
            else:
                self._try_move_to(player, selected, point_idx)

    def _try_select_source(self, player: BackgammonPlayer, point_idx: int) -> None:
        """Try to select a point as the move source."""
        gs = self.game_state
        color = player.color
        sign = color_sign(color)

        # Check if player has checkers on bar — directly attempt bar entry
        if bar_count(gs, color) > 0:
            self._try_apply_move_direct(player, -1, point_idx)
            return

        # Check the point has our checkers
        val = gs.board.points[point_idx]
        if val == 0:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-no-checkers-there")
            return
        if val * sign < 0:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-not-your-checkers")
            return

        # Check if any legal move originates from this point
        has_move = False
        for die_val in self._get_usable_dice():
            for m in generate_legal_moves(gs, color, die_val):
                if m.source == point_idx:
                    has_move = True
                    break
            if has_move:
                break

        if not has_move:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-no-moves-from-here")
            return

        gs.selected_source = point_idx
        self.play_sound("game_chess/pickup.ogg")

    def _try_move_to(self, player: BackgammonPlayer, source: int, dest_point: int) -> None:
        """Try to move from selected source to destination point."""
        self._try_apply_move_direct(player, source, dest_point)

    def _try_bear_off(self, player: BackgammonPlayer, point_idx: int) -> bool:
        """Try to bear off from point_idx (double-click). Returns True if handled."""
        gs = self.game_state
        color = player.color
        user = self.get_user(player)

        # Not in bearing-off position at all
        if not all_checkers_in_home(gs, color):
            return False

        # Check if any usable die produces a bear-off from this point
        for die_idx, (die_val, used) in enumerate(zip(gs.dice, gs.dice_used)):
            if used:
                continue
            if self._forced_dice is not None and die_val not in self._forced_dice:
                continue
            for m in generate_legal_moves(gs, color, die_val):
                if m.source == point_idx and m.is_bear_off:
                    # Found a legal bear-off — apply it
                    self._try_apply_move_direct(player, point_idx, 24)
                    return True

        # All checkers are home but can't bear off from this specific point.
        # Give a helpful error explaining why.
        pn = point_number_for_player(point_idx, color)
        usable_dice = [
            d
            for d, u in zip(gs.dice, gs.dice_used)
            if not u and (self._forced_dice is None or d in self._forced_dice)
        ]

        if not usable_dice:
            return False

        # The player's point number tells us the exact die needed
        exact_die = pn  # e.g. 5-point needs a 5 to bear off exactly

        # Which dice overshoot (could bear off if no higher checker)?
        overshooting = [d for d in usable_dice if d > exact_die]

        # Check: is there a higher checker blocking overshoot bear-off?
        sign = color_sign(color)
        higher_pn = None
        if color == "red":
            for i in range(point_idx + 1, 6):
                if gs.board.points[i] * sign > 0:
                    higher_pn = point_number_for_player(i, color)
                    break
        else:
            for i in range(18, point_idx):
                if gs.board.points[i] * sign > 0:
                    higher_pn = point_number_for_player(i, color)
                    break

        if overshooting and higher_pn is not None:
            # Has dice that overshoot but a higher checker blocks it
            die_str = ", ".join(str(d) for d in overshooting)
            if user:
                user.speak_l(
                    "backgammon-bearoff-blocked",
                    point=pn,
                    die=die_str,
                    blocking_point=higher_pn,
                )
        else:
            # No die is large enough (all undershoot)
            die_str = ", ".join(str(d) for d in usable_dice)
            if user:
                user.speak_l(
                    "backgammon-bearoff-no-die",
                    point=pn,
                    die=die_str,
                )

        gs.selected_source = None
        self.play_sound("game_chess/setdown.ogg")
        self.update_player_menu(player)
        return True

    def _try_apply_move_direct(self, player: BackgammonPlayer, source: int, dest: int) -> None:
        """Try to apply a move from source to dest, finding matching die."""
        gs = self.game_state
        color = player.color

        # Find a matching legal move
        matched_move: BackgammonMove | None = None
        matched_die_idx: int | None = None

        for die_idx, (die_val, used) in enumerate(zip(gs.dice, gs.dice_used)):
            if used:
                continue
            if self._forced_dice is not None and die_val not in self._forced_dice:
                continue
            for m in generate_legal_moves(gs, color, die_val):
                if m.source == source and m.destination == dest:
                    matched_move = m
                    matched_die_idx = die_idx
                    break
            if matched_move:
                break

        if matched_move is None or matched_die_idx is None:
            log.warning(
                "Illegal move: game=%s color=%s src=%s dst=%s dice=%s used=%s forced=%s",
                gs.game_number,
                color,
                source,
                dest,
                gs.dice,
                gs.dice_used,
                self._forced_dice,
            )
            gs.selected_source = None
            self._bot_goals.clear()  # Discard stale goals
            self.play_sound("game_chess/setdown.ogg")
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-illegal-move")
            return

        # Apply the move
        apply_move(gs, matched_move, color)
        gs.dice_used[matched_die_idx] = True
        gs.selected_source = None

        # Announce
        self._announce_sub_move(player, matched_move)

        # Play sound
        if matched_move.is_hit:
            self.play_sound(f"game_chess/capture{random.randint(1, 2)}.ogg")  # nosec B311
        elif matched_move.is_bear_off:
            self.play_sound("mention.ogg", volume=50)
        else:
            self.play_sound("game_squares/step1.ogg")

        # Check if game won
        if off_count(gs, color) == 15:
            self._win_game(player)
            return

        # Check for more moves
        self._check_forced_dice()
        if not has_any_legal_move(gs, color):
            remaining = remaining_dice(gs)
            if remaining:
                self.broadcast_l("backgammon-no-moves", player=player.name)
            self._end_moving_phase()
        elif not remaining_dice(gs):
            self._end_moving_phase()
        else:
            self.rebuild_all_menus()

    def _do_roll(self, player: BackgammonPlayer) -> None:
        """Roll dice and enter moving phase."""
        gs = self.game_state
        d1, d2 = roll_dice()
        if d1 == d2:
            gs.dice = [d1, d1, d1, d1]
            gs.dice_used = [False, False, False, False]
        else:
            gs.dice = [d1, d2]
            gs.dice_used = [False, False]

        gs.moves_this_turn = []
        gs.turn_phase = "moving"

        self._play_dice_sound()
        self.broadcast_l(
            "backgammon-roll",
            player=player.name,
            die1=d1,
            die2=d2,
        )

        self._check_forced_dice()
        if not has_any_legal_move(gs, player.color):
            self.broadcast_l("backgammon-no-moves", player=player.name)
            self._end_moving_phase()
        else:
            self.rebuild_all_menus()

    def _check_forced_dice(self) -> None:
        """Check and apply the must-use-both-dice rule."""
        gs = self.game_state
        unused = [d for d, u in zip(gs.dice, gs.dice_used) if not u]
        unique_unused = sorted(set(unused))
        if len(unique_unused) == 2:
            self._forced_dice = must_use_both_dice(gs, gs.current_color, unique_unused)
        else:
            self._forced_dice = None

    def _get_usable_dice(self) -> list[int]:
        """Get die values that can be used this sub-move."""
        gs = self.game_state
        unused = remaining_dice_unique(gs)
        if self._forced_dice is not None:
            return [d for d in unused if d in self._forced_dice]
        return unused

    def _end_moving_phase(self) -> None:
        """End the moving phase and advance turn."""
        gs = self.game_state
        gs.turn_phase = "pre_roll"
        gs.selected_source = None
        gs.moves_this_turn = []
        self._forced_dice = None
        self._bot_goals.clear()

        # Advance to other player
        opp_color = opponent_color(gs.current_color)
        gs.current_color = opp_color
        opp_player = self._get_player_by_color(opp_color)
        if opp_player:
            self.current_player = opp_player
            self.announce_turn()
            if opp_player.is_bot:
                BotHelper.jolt_bot(opp_player, ticks=random.randint(5, 10))  # nosec B311

        self.rebuild_all_menus()

    # ==========================================================================
    # Doubling cube
    # ==========================================================================

    def _can_double(self, player: BackgammonPlayer) -> bool:
        """Check if player can offer the doubling cube."""
        gs = self.game_state
        if gs.match_length <= 1:
            return False
        if gs.is_crawford:
            return False
        if gs.cube_owner and gs.cube_owner != player.color:
            return False
        if gs.turn_phase != "pre_roll":
            return False
        if player.color != gs.current_color:
            return False
        return True

    def _action_offer_double(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        if not self._can_double(player):
            return
        gs = self.game_state
        gs.turn_phase = "doubling"
        new_value = gs.cube_value * 2
        self.broadcast_l(
            "backgammon-doubles",
            player=player.name,
            value=new_value,
        )
        # Jolt the opponent bot so they pause before responding
        opp_color = opponent_color(player.color)
        opp = self._get_player_by_color(opp_color)
        if opp and opp.is_bot:
            BotHelper.jolt_bot(opp, ticks=random.randint(3, 6))
        self.rebuild_all_menus()

    def _action_accept_double(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state
        if gs.turn_phase != "doubling":
            return
        if player.color == gs.current_color:
            return  # Can't accept own double

        gs.cube_value *= 2
        gs.cube_owner = player.color
        gs.turn_phase = "pre_roll"
        self.broadcast_l("backgammon-accepts", player=player.name)
        self.rebuild_all_menus()

    def _action_drop_double(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state
        if gs.turn_phase != "doubling":
            return
        if player.color == gs.current_color:
            return

        self.broadcast_l("backgammon-drops", player=player.name)
        winner = self._get_player_by_color(gs.current_color)
        if winner:
            self._score_game(winner, gs.cube_value)

    # ==========================================================================
    # Undo
    # ==========================================================================

    def _action_undo_move(self, player: Player, action_id: str) -> None:
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state
        if gs.turn_phase != "moving":
            return
        if player.color != gs.current_color:
            return

        undone = undo_last_move(gs, player.color)
        if undone is None:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-nothing-to-undo")
            return

        # Unmark the die
        for i in range(len(gs.dice_used) - 1, -1, -1):
            if gs.dice_used[i] and gs.dice[i] == undone.die_value:
                gs.dice_used[i] = False
                break

        gs.selected_source = None
        self._check_forced_dice()
        self.play_sound("game_chess/setdown.ogg")
        user = self.get_user(player)
        if user:
            user.speak_l("backgammon-undone")
        self.rebuild_all_menus()

    # ==========================================================================
    # Info keybinds
    # ==========================================================================

    def _action_check_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        color = player.color if isinstance(player, BackgammonPlayer) else "red"
        bar_r = gs.board.bar_red
        bar_w = gs.board.bar_white
        off_r = gs.board.off_red
        off_w = gs.board.off_white
        user.speak_l(
            "backgammon-status",
            bar_red=bar_r,
            bar_white=bar_w,
            off_red=off_r,
            off_white=off_w,
        )

    def _action_check_pip(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        user.speak_l(
            "backgammon-pip-count",
            red_pip=pip_count(gs, "red"),
            white_pip=pip_count(gs, "white"),
        )

    def _action_check_score(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        red_p = self._get_player_by_color("red")
        white_p = self._get_player_by_color("white")
        user.speak_l(
            "backgammon-match-score",
            red=red_p.name if red_p else "Red",
            red_score=gs.score_red,
            white=white_p.name if white_p else "White",
            white_score=gs.score_white,
            match_length=gs.match_length,
            cube=gs.cube_value,
        )

    def _action_check_cube(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state

        if gs.match_length <= 1:
            user.speak_l("backgammon-cube-no-match")
            return

        # Who owns the cube?
        if not gs.cube_owner:
            owner_desc = "center"
        else:
            owner_p = self._get_player_by_color(gs.cube_owner)
            owner_desc = owner_p.name if owner_p else gs.cube_owner

        # Can the current player double right now?
        current_player = self._get_player_by_color(gs.current_color)
        if isinstance(current_player, BackgammonPlayer) and self._can_double(current_player):
            can_double = "yes"
        elif gs.is_crawford:
            can_double = "crawford"
        else:
            can_double = "no"

        user.speak_l(
            "backgammon-cube-status",
            value=gs.cube_value,
            owner=owner_desc,
            can_double=can_double,
        )

    def _action_check_dice(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        dice = remaining_dice(gs)
        if dice:
            user.speak_l("backgammon-dice", dice=" ".join(str(d) for d in dice))
        else:
            user.speak_l("backgammon-dice-none")

    def _get_hint_proc(self) -> GnubgProcess | None:
        """Get or create the hint GNUBG process."""
        from .gnubg import GnubgProcess, is_gnubg_available

        if not is_gnubg_available():
            return None
        proc = getattr(self, "_hint_proc", None)
        if proc is None:
            proc = GnubgProcess(ply=2)
            if not proc.start():
                return None
            self._hint_proc = proc
        return proc

    def _action_get_hint(self, player: Player, action_id: str) -> None:
        """Get a GNUBG hint and broadcast it to the table (async)."""
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state

        # Mid-turn (some dice used): list legal moves locally
        unused_dice = [d for d, u in zip(gs.dice, gs.dice_used) if not u]
        if len(unused_dice) < 2:
            self._show_local_hint(player, unused_dice)
            return

        if getattr(self, "_hint_future", None) is not None:
            return  # Already a hint in progress

        proc = self._get_hint_proc()
        if proc is None:
            self.broadcast_l("backgammon-hint-unavailable")
            return

        player_name = player.name
        color = player.color

        def _query():
            hints = proc.get_move_hint_text(gs, color, hint_count=3)
            if hints:
                hint_text = "; ".join(hints)
                return {"message_key": "backgammon-hint", "player": player_name, "hint": hint_text}
            return None

        from .bot import _gnubg_pool

        self._hint_future = _gnubg_pool.submit(_query)

    def _show_local_hint(self, player: BackgammonPlayer, unused_dice: list[int]) -> None:
        """Show legal moves locally when GNUBG can't be used (mid-turn)."""
        gs = self.game_state
        locale = self._player_locale(player)
        color = player.color
        viewer_color = color
        bar_str = Localization.get(locale, "backgammon-hint-bar")
        off_str = Localization.get(locale, "backgammon-hint-off")

        move_strs = []
        for die_val in set(unused_dice):
            for m in generate_legal_moves(gs, color, die_val):
                if m.source == -1:
                    src_str = bar_str
                else:
                    src_str = str(point_number_for_player(m.source, viewer_color))
                if m.is_bear_off:
                    dst_str = off_str
                else:
                    dst_str = str(point_number_for_player(m.destination, viewer_color))
                desc = f"{src_str}/{dst_str}"
                if m.is_hit:
                    desc += "*"
                if desc not in move_strs:
                    move_strs.append(desc)

        if move_strs:
            hint_text = ", ".join(move_strs)
            self.broadcast_l("backgammon-hint", player=player.name, hint=hint_text)
        else:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-no-moves-from-here")

    def _action_get_cube_hint(self, player: Player, action_id: str) -> None:
        """Get a GNUBG cube hint (async)."""
        if not isinstance(player, BackgammonPlayer):
            return
        gs = self.game_state

        if gs.match_length <= 1:
            user = self.get_user(player)
            if user:
                user.speak_l("backgammon-cube-no-match")
            return

        if getattr(self, "_hint_future", None) is not None:
            return  # Already a hint in progress

        proc = self._get_hint_proc()
        if proc is None:
            self.broadcast_l("backgammon-hint-unavailable")
            return

        player_name = player.name
        color = player.color
        # When facing a double, query from the doubler's perspective so cube
        # ownership is encoded correctly, then map to a clear take/drop answer.
        facing_double = gs.turn_phase == "doubling" and color != gs.current_color
        doubler_color = gs.current_color

        def _query():
            if facing_double:
                decision = proc.get_cube_decision(gs, doubler_color)
                if decision:
                    # "no-double" / "double-take" → take (double was bad or position is viable)
                    # "too-good" / "double-pass" → drop (position is lost)
                    advice = "take" if decision in ("double-take", "no-double") else "drop"
                    return {
                        "message_key": "backgammon-cube-hint-response",
                        "player": player_name,
                        "advice": advice,
                    }
            else:
                hint_text = proc.get_cube_hint_text(gs, color)
                if hint_text:
                    return {
                        "message_key": "backgammon-cube-hint",
                        "player": player_name,
                        "hint": hint_text,
                    }
            return None

        from .bot import _gnubg_pool

        self._hint_future = _gnubg_pool.submit(_query)

    # ==========================================================================
    # Scoring & game end
    # ==========================================================================

    def _win_game(self, winner: BackgammonPlayer) -> None:
        """Handle a player bearing off all checkers."""
        gs = self.game_state
        loser_color = opponent_color(winner.color)
        multiplier = game_multiplier(gs, loser_color)
        points = gs.cube_value * multiplier
        self._score_game(winner, points)

    def _score_game(self, winner: BackgammonPlayer, points: int) -> None:
        """Award points and check match end."""
        gs = self.game_state
        if winner.color == "red":
            gs.score_red += points
        else:
            gs.score_white += points

        self.broadcast_l(
            "backgammon-wins-game",
            player=winner.name,
            points=points,
        )

        # Check match end
        if gs.score_red >= gs.match_length:
            self._finish_match(self._get_player_by_color("red"))
        elif gs.score_white >= gs.match_length:
            self._finish_match(self._get_player_by_color("white"))
        else:
            # Crawford rule check
            if not gs.crawford_used:
                if gs.score_red == gs.match_length - 1 or gs.score_white == gs.match_length - 1:
                    gs.is_crawford = True
                    gs.crawford_used = True
                    self.broadcast_l("backgammon-crawford")
            elif gs.is_crawford:
                gs.is_crawford = False

            # Start new game
            gs.game_number += 1
            self._start_new_game()

    def _start_new_game(self) -> None:
        """Reset board for a new game within the match."""
        gs = self.game_state
        gs.board = BackgammonBoardState(points=list(INITIAL_BOARD))
        gs.dice = []
        gs.dice_used = []
        gs.turn_phase = "pre_roll"
        gs.selected_source = None
        gs.moves_this_turn = []
        gs.cube_value = 1
        gs.cube_owner = ""
        self._forced_dice = None

        self.broadcast_l("backgammon-new-game", number=gs.game_number)
        self._do_opening_roll()
        BotHelper.jolt_bots(self, ticks=random.randint(4, 8))

    def _finish_match(self, winner: BackgammonPlayer | None) -> None:
        """End the match."""
        cleanup_gnubg(self)
        self._match_winner = winner
        if winner:
            self.broadcast_l("backgammon-match-winner", player=winner.name)
        self.play_sound("game_pig/win.ogg")
        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result for the end screen."""
        from datetime import datetime

        gs = self.game_state
        winner = getattr(self, "_match_winner", None)
        red = self._get_player_by_color("red")
        white = self._get_player_by_color("white")

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot,
                    is_virtual_bot=getattr(p, "is_virtual_bot", False),
                )
                for p in self.players
                if not p.is_spectator
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "score_red": gs.score_red,
                "score_white": gs.score_white,
                "match_length": gs.match_length,
                "red_name": red.name if red else "Red",
                "white_name": white.name if white else "White",
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the match result for the end screen."""
        d = result.custom_data
        lines = []
        lines.append(
            Localization.get(
                locale,
                "backgammon-end-score",
                red=d.get("red_name", "Red"),
                red_score=d.get("score_red", 0),
                white=d.get("white_name", "White"),
                white_score=d.get("score_white", 0),
                match_length=d.get("match_length", 1),
            )
        )
        return lines

    # ==========================================================================
    # Leave handling
    # ==========================================================================

    def _perform_leave_game(self, player: Player) -> None:
        if self.status == "playing" and not player.is_bot:
            player.is_bot = True
            self._users.pop(player.id, None)
            bot_user = Bot(player.name, uuid=player.id)
            self.attach_user(player.id, bot_user)
            self.broadcast_l("player-replaced-by-bot", player=player.name)

            has_humans = any(not p.is_bot for p in self.players)
            if not has_humans:
                self.destroy()
                return

            self.rebuild_all_menus()
            return

        self.players = [p for p in self.players if p.id != player.id]
        self.player_action_sets.pop(player.id, None)
        self._users.pop(player.id, None)
        self.broadcast_l("table-left", player=player.name)

        has_humans = any(not p.is_bot for p in self.players)
        if not has_humans:
            self.destroy()
            return

        if self.status == "waiting":
            if player.name == self.host and self.players:
                for p in self.players:
                    if not p.is_bot:
                        self.host = p.name
                        self.broadcast_l("new-host", player=p.name)
                        break
            self.rebuild_all_menus()

    # ==========================================================================
    # Sound helpers
    # ==========================================================================

    def _play_dice_sound(self) -> None:
        self.play_sound(f"game_squares/diceroll{random.randint(1, 3)}.ogg")  # nosec B311

    # ==========================================================================
    # Commentary / announcements
    # ==========================================================================

    def _announce_sub_move(self, player: BackgammonPlayer, move: BackgammonMove) -> None:
        """Announce a sub-move to all players with reflected point numbers."""
        gs = self.game_state
        color = player.color

        for p in self.players:
            if not isinstance(p, BackgammonPlayer):
                continue
            user = self.get_user(p)
            if not user:
                continue
            viewer_color = p.color
            self._speak_move(user, move, color, viewer_color)

    def _speak_move(
        self, user: User, move: BackgammonMove, mover_color: str, viewer_color: str
    ) -> None:
        """Speak a single sub-move to a user with point numbers in their perspective."""
        brief = user.preferences.get_effective("brief_announcements", game_type=self.get_type())
        if not brief:
            self._speak_move_verbose(user, move, mover_color, viewer_color)
            return
        gs = self.game_state

        if move.source == -1:
            # Bar entry
            dest_pn = point_number_for_player(move.destination, viewer_color)
            dest_count = point_count(gs, move.destination)
            if move.is_hit:
                user.speak_l(
                    "backgammon-move-bar-hit",
                    dest=dest_pn,
                    count=dest_count,
                )
            else:
                user.speak_l(
                    "backgammon-move-bar",
                    dest=dest_pn,
                    count=dest_count,
                )
        elif move.is_bear_off:
            src_pn = point_number_for_player(move.source, viewer_color)
            remain = point_count(gs, move.source)
            user.speak_l(
                "backgammon-move-bearoff",
                src=src_pn,
                remain=remain,
            )
        elif move.is_hit:
            src_pn = point_number_for_player(move.source, viewer_color)
            dest_pn = point_number_for_player(move.destination, viewer_color)
            src_remain = point_count(gs, move.source)
            if src_remain == 0:
                user.speak_l(
                    "backgammon-move-emptying-hit",
                    src=src_pn,
                    dest=dest_pn,
                )
            else:
                user.speak_l(
                    "backgammon-move-hit",
                    src=src_pn,
                    dest=dest_pn,
                    remain=src_remain,
                )
        else:
            src_pn = point_number_for_player(move.source, viewer_color)
            dest_pn = point_number_for_player(move.destination, viewer_color)
            src_remain = point_count(gs, move.source)
            dest_count = point_count(gs, move.destination)
            if src_remain == 0:
                user.speak_l(
                    "backgammon-move-emptying",
                    src=src_pn,
                    dest=dest_pn,
                    count=dest_count,
                )
            else:
                user.speak_l(
                    "backgammon-move-normal",
                    src=src_pn,
                    dest=dest_pn,
                    remain=src_remain,
                    count=dest_count,
                )

    def _speak_move_verbose(
        self, user: User, move: BackgammonMove, mover_color: str, viewer_color: str
    ) -> None:
        """Speak a verbose sub-move: player name conjugation, captures, stack counts."""
        gs = self.game_state
        if mover_color == viewer_color:
            is_self = "yes"
        elif viewer_color == "":
            is_self = "spectator"
        else:
            is_self = "no"
        mover = self._get_player_by_color(mover_color)
        opp = self._get_player_by_color(opponent_color(mover_color))
        player_name = mover.name if mover else "?"
        opponent_name = opp.name if opp else "?"

        if move.source == -1:
            # Bar entry
            dest_pn = point_number_for_player(move.destination, viewer_color)
            dest_count = point_count(gs, move.destination)
            if move.is_hit:
                user.speak_l(
                    "backgammon-verbose-move-bar-hit",
                    is_self=is_self,
                    player=player_name,
                    opponent=opponent_name,
                    dest=dest_pn,
                )
            else:
                user.speak_l(
                    "backgammon-verbose-move-bar",
                    is_self=is_self,
                    player=player_name,
                    dest=dest_pn,
                    dest_count=dest_count,
                )
        elif move.is_bear_off:
            src_pn = point_number_for_player(move.source, viewer_color)
            src_count = point_count(gs, move.source)
            user.speak_l(
                "backgammon-verbose-move-bearoff",
                is_self=is_self,
                player=player_name,
                src=src_pn,
                src_count=src_count,
            )
        elif move.is_hit:
            src_pn = point_number_for_player(move.source, viewer_color)
            dest_pn = point_number_for_player(move.destination, viewer_color)
            src_count = point_count(gs, move.source)
            user.speak_l(
                "backgammon-verbose-move-hit",
                is_self=is_self,
                player=player_name,
                opponent=opponent_name,
                src=src_pn,
                dest=dest_pn,
                src_count=src_count,
            )
        else:
            src_pn = point_number_for_player(move.source, viewer_color)
            dest_pn = point_number_for_player(move.destination, viewer_color)
            src_count = point_count(gs, move.source)
            dest_count = point_count(gs, move.destination)
            user.speak_l(
                "backgammon-verbose-move-normal",
                is_self=is_self,
                player=player_name,
                src=src_pn,
                dest=dest_pn,
                src_count=src_count,
                dest_count=dest_count,
            )

    # ==========================================================================
    # Action visibility / enable callbacks
    # ==========================================================================

    def _is_point_enabled(self, player: Player, action_id: str) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "action-not-available"
        gs = self.game_state
        if gs.turn_phase == "doubling" and player.color != gs.current_color:
            return "action-not-available"
        if gs.turn_phase in ("pre_roll", "moving") and player.color != gs.current_color:
            return "action-not-your-turn"
        return None

    def _is_point_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        gs = self.game_state
        if gs.turn_phase == "doubling":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_point_label(self, player: Player, action_id: str) -> str:
        """Get label for a board point."""
        try:
            point_idx = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return ""

        gs = self.game_state
        locale = self._player_locale(player)
        color = player.color if isinstance(player, BackgammonPlayer) else "red"
        pn = point_number_for_player(point_idx, color)
        val = gs.board.points[point_idx]
        selected = gs.selected_source == point_idx

        if val == 0:
            key = "backgammon-point-empty-selected" if selected else "backgammon-point-empty"
            return Localization.get(locale, key, point=pn)

        cnt = abs(val)
        owner = "red" if val > 0 else "white"
        owner_name = Localization.get(locale, f"color-{owner}")
        key = "backgammon-point-occupied-selected" if selected else "backgammon-point-occupied"
        return Localization.get(locale, key, point=pn, color=owner_name, count=cnt)

    def _get_point_sound(self, player: Player, action_id: str) -> str | None:
        """Get navigation sound for a board point based on its contents.

        Sounds are perspective-relative: "mine" vs "theirs" rather than
        fixed colors, so Red and White each hear their own checkers as
        the same sound.
        """
        try:
            point_idx = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return None

        val = self.game_state.board.points[point_idx]
        if val == 0:
            return None

        # Determine if this point belongs to the viewing player
        is_own = (isinstance(player, BackgammonPlayer) and player.color == "red" and val > 0) or (
            isinstance(player, BackgammonPlayer) and player.color == "white" and val < 0
        )
        count = abs(val)

        if is_own:
            return "game_squares/token1.ogg" if count == 1 else "game_squares/token3.ogg"
        else:
            return "game_squares/token7.ogg" if count == 1 else "game_squares/token4.ogg"

    def _is_offer_double_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "backgammon-cannot-double"
        if not self._can_double(player):
            return "backgammon-cannot-double"
        return None

    def _is_undo_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "backgammon-cannot-undo"
        gs = self.game_state
        if gs.turn_phase != "moving":
            return "backgammon-cannot-undo"
        if player.color != gs.current_color:
            return "action-not-your-turn"
        if not gs.moves_this_turn:
            return "backgammon-cannot-undo"
        return None

    def _is_hint_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        gs = self.game_state
        if gs.turn_phase != "moving":
            return "backgammon-hint-not-now"
        if not self.options.hints_enabled:
            return "backgammon-hints-disabled"
        return None

    def _is_cube_hint_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        gs = self.game_state
        if gs.turn_phase not in ("pre_roll", "doubling"):
            return "backgammon-cube-hint-not-now"
        if not self.options.cube_hints_enabled:
            return "backgammon-cube-hints-disabled"
        return None

    def _is_accept_double_enabled(self, player: Player, action_id: str = "") -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        gs = self.game_state
        if gs.turn_phase != "doubling":
            return "backgammon-not-doubling-phase"
        if not isinstance(player, BackgammonPlayer):
            return "backgammon-not-doubling-phase"
        if player.is_spectator:
            return "backgammon-not-doubling-phase"
        if player.color == gs.current_color:
            return "backgammon-not-doubling-phase"
        return None

    def _is_accept_double_hidden(self, player: Player, action_id: str = "") -> Visibility:
        if self._is_accept_double_enabled(player) is not None:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_drop_double_enabled(self, player: Player, action_id: str = "") -> str | None:
        return self._is_accept_double_enabled(player)

    def _is_drop_double_hidden(self, player: Player, action_id: str = "") -> Visibility:
        return self._is_accept_double_hidden(player)

    def _is_navigate_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "action-not-available"
        gs = self.game_state
        if gs.turn_phase != "moving":
            return "action-not-available"
        if player.color != gs.current_color:
            return "action-not-your-turn"
        return None

    def _is_deselect_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, BackgammonPlayer):
            return "action-not-available"
        gs = self.game_state
        if gs.turn_phase != "moving":
            return "action-not-available"
        if player.color != gs.current_color:
            return "action-not-your-turn"
        if gs.selected_source is None:
            return "action-not-available"
        return None

    def _is_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_check_scores_detailed_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_always_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN
