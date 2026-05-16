"""Senet game for PlayPalace."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field

log = logging.getLogger(__name__)

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.options import MenuOption, option_field
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState
from server.core.users.bot import Bot
from server.core.users.base import User, MenuItem, EscapeBehavior
from .bot import bot_think
from .moves import generate_legal_moves, apply_move, has_any_legal_move
from .state import (
    SenetGameState,
    PIECES_PER_PLAYER,
    SPECIAL_SQUARE_NAMES,
    HOUSE_WATER,
    HOUSE_HAPPINESS,
    build_initial_state,
    opponent_num,
    pieces_remaining,
    throw_sticks,
)


BOT_DIFFICULTY_CHOICES = ["random", "simple"]
BOT_DIFFICULTY_LABELS = {
    "random": "senet-difficulty-random",
    "simple": "senet-difficulty-simple",
}


@dataclass
class SenetOptions(GameOptions):
    bot_difficulty: str = option_field(
        MenuOption(
            default="simple",
            choices=BOT_DIFFICULTY_CHOICES,
            choice_labels=BOT_DIFFICULTY_LABELS,
            value_key="bot_difficulty",
            label="senet-option-bot-difficulty",
            prompt="senet-option-select-bot-difficulty",
            change_msg="senet-option-changed-bot-difficulty",
        )
    )


@dataclass
class SenetPlayer(Player):
    player_num: int = 0  # 1 or 2


@register_game
@dataclass
class SenetGame(Game):
    """Senet — ancient Egyptian board game."""

    players: list[SenetPlayer] = field(default_factory=list)
    options: SenetOptions = field(default_factory=SenetOptions)
    game_state: SenetGameState = field(default_factory=SenetGameState)

    _nav_cursor: int | None = None
    _nav_skip_rebuild: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "Senet"

    @classmethod
    def get_type(cls) -> str:
        return "senet"

    @classmethod
    def get_category(cls) -> str:
        return "category-board-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 2

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> SenetPlayer:
        return SenetPlayer(id=player_id, name=name, is_bot=is_bot)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _get_player_by_num(self, num: int) -> SenetPlayer | None:
        for p in self.players:
            if isinstance(p, SenetPlayer) and p.player_num == num:
                return p
        return None

    def _current_senet_player(self) -> SenetPlayer | None:
        return self._get_player_by_num(self.game_state.current_player_num)

    # ======================================================================
    # Action sets
    # ======================================================================

    def create_turn_action_set(self, player: SenetPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        locale = self._player_locale(player)

        for idx in self._grid_indices():
            action_set.add(
                Action(
                    id=f"sq_{idx}",
                    label="",
                    handler="_action_square_click",
                    is_enabled="_is_square_enabled",
                    is_hidden="_is_square_hidden",
                    get_label="_get_square_label",
                    get_sound="_get_square_sound",
                    show_in_actions_menu=False,
                    show_disabled_label=False,
                )
            )

        # Navigation (keybind-only)
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

        # Info actions
        local_actions = [
            Action(
                id="check_status",
                label=Localization.get(locale, "senet-check-status"),
                handler="_action_check_status",
                is_enabled="_is_info_enabled",
                is_hidden="_is_always_hidden",
            ),
            Action(
                id="check_sticks",
                label=Localization.get(locale, "senet-check-sticks"),
                handler="_action_check_sticks",
                is_enabled="_is_info_enabled",
                is_hidden="_is_always_hidden",
            ),
            Action(
                id="check_score",
                label=Localization.get(locale, "senet-check-score"),
                handler="_action_check_score",
                is_enabled="_is_info_enabled",
                is_hidden="_is_always_hidden",
            ),
        ]
        for action in reversed(local_actions):
            action_set.add(action)
            if action.id in action_set._order:
                action_set._order.remove(action.id)
            action_set._order.insert(0, action.id)

        # Hide base score actions — we use our own
        for action_id in ("check_scores", "check_scores_detailed"):
            existing = action_set.get_action(action_id)
            if existing:
                existing.show_in_actions_menu = False

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()

        if "s" in self._keybinds:
            self._keybinds["s"] = []
        if "shift+s" in self._keybinds:
            self._keybinds["shift+s"] = []

        self.define_keybind(
            "e", "Status", ["check_status"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "c", "Sticks", ["check_sticks"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "s", "Score", ["check_score"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "ctrl+down", "Next piece", ["navigate_next"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "ctrl+right", "Next piece", ["navigate_next"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "ctrl+up", "Previous piece", ["navigate_prev"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "ctrl+left", "Previous piece", ["navigate_prev"], state=KeybindState.ACTIVE
        )

    # ======================================================================
    # Grid helpers
    # ======================================================================

    def _grid_indices(self) -> list[int]:
        """Return square indices in physical grid order (3 rows x 10 cols).

        Row 1: squares 1-10  (indices 0-9, L to R)
        Row 2: squares 20-11 (indices 19-10, L to R visually = R to L on path)
        Row 3: squares 21-30 (indices 20-29, L to R)
        """
        row1 = list(range(0, 10))
        row2 = list(range(19, 9, -1))
        row3 = list(range(20, 30))
        return row1 + row2 + row3

    # ======================================================================
    # Navigation (ctrl+up/down)
    # ======================================================================

    def _action_navigate_next(self, player: Player, action_id: str) -> None:
        if isinstance(player, SenetPlayer):
            self._navigate(player, direction=1)

    def _action_navigate_prev(self, player: Player, action_id: str) -> None:
        if isinstance(player, SenetPlayer):
            self._navigate(player, direction=-1)

    def _navigate(self, player: SenetPlayer, direction: int) -> None:
        """Cycle through squares with movable pieces."""
        gs = self.game_state
        if gs.turn_phase != "moving" or gs.current_player_num != player.player_num:
            return

        targets = self._get_movable_squares(player.player_num)
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
            selection_id=f"sq_{targets[idx]}",
            play_selection_sound=True,
        )

    def _get_movable_squares(self, player_num: int) -> list[int]:
        gs = self.game_state
        sources: set[int] = set()
        for move in generate_legal_moves(gs, player_num, gs.current_roll):
            sources.add(move.source)
        return sorted(sources)

    # ======================================================================
    # Menu overrides (grid mode)
    # ======================================================================

    def rebuild_player_menu(
        self,
        player: Player,
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

        grid_items, other_items = self._build_menu_items(player, user)
        use_grid = len(grid_items) == 30

        user.show_menu(
            "turn_menu",
            grid_items + other_items,
            multiletter=False,
            escape_behavior=EscapeBehavior.KEYBIND,
            position=position,
            grid_enabled=use_grid,
            grid_width=10 if use_grid else 1,
            play_selection_sound=play_selection_sound,
        )

    def update_player_menu(
        self,
        player: Player,
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

        grid_items, other_items = self._build_menu_items(player, user)

        user.update_menu(
            "turn_menu",
            grid_items + other_items,
            selection_id=selection_id,
            play_selection_sound=play_selection_sound,
        )

    def _build_menu_items(
        self, player: Player, user
    ) -> tuple[list[MenuItem], list[MenuItem]]:
        grid_items: list[MenuItem] = []
        other_items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            label = resolved.label
            if not resolved.enabled and resolved.action.show_disabled_label:
                unavailable = Localization.get(user.locale, "visibility-unavailable")
                label = f"{label}; {unavailable}"
            item = MenuItem(text=label, id=resolved.action.id, sound=resolved.sound)
            if resolved.action.id.startswith("sq_"):
                grid_items.append(item)
            else:
                other_items.append(item)
        return grid_items, other_items

    def _should_rebuild_after_keybind(self, player, executed_any: bool) -> bool:
        if self._nav_skip_rebuild:
            self._nav_skip_rebuild = False
            return False
        return super()._should_rebuild_after_keybind(player, executed_any)

    # ======================================================================
    # Game flow
    # ======================================================================

    def on_start(self) -> None:
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 1

        active_players = [p for p in self.players if not p.is_spectator]
        self.set_turn_players(active_players, reset_index=True)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Assign player numbers randomly
        if random.random() < 0.5:  # nosec B311
            active_players[0].player_num = 1
            active_players[1].player_num = 2
        else:
            active_players[0].player_num = 2
            active_players[1].player_num = 1

        self.game_state = build_initial_state()

        p1 = self._get_player_by_num(1)
        p2 = self._get_player_by_num(2)
        first = p1  # Player 1 always goes first
        self.current_player = first

        self.broadcast_l(
            "senet-game-started",
            p1=p1.name if p1 else "?",
            p2=p2.name if p2 else "?",
            first=first.name if first else "?",
        )

        self.play_music("game_pig/mus.ogg")
        BotHelper.jolt_bots(self, ticks=random.randint(4, 8))
        self.rebuild_all_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: SenetPlayer) -> str | None:
        return bot_think(self, player)

    # ======================================================================
    # Square click handler
    # ======================================================================

    def _action_square_click(self, player: Player, action_id: str) -> None:
        if not isinstance(player, SenetPlayer):
            return
        gs = self.game_state
        if gs.current_player_num != player.player_num:
            return

        # Throwing phase: any click throws sticks
        if gs.turn_phase == "throwing":
            self._do_throw(player)
            return

        if gs.turn_phase != "moving":
            return

        try:
            sq_idx = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return

        board = gs.board
        user = self.get_user(player)

        if board[sq_idx] == 0:
            if user:
                user.speak_l("senet-no-piece-there")
            return

        if board[sq_idx] != player.player_num:
            if user:
                user.speak_l("senet-not-your-piece")
            return

        # Auto-move: find the legal move from this square and apply it
        moves = [
            m
            for m in generate_legal_moves(gs, player.player_num, gs.current_roll)
            if m.source == sq_idx
        ]

        if not moves:
            if user:
                user.speak_l("senet-no-moves-from-here")
            return

        self._apply_and_announce(player, moves[0])

    # ======================================================================
    # Throwing sticks
    # ======================================================================

    def _do_throw(self, player: SenetPlayer) -> None:
        gs = self.game_state
        value, bonus = throw_sticks()
        gs.current_roll = value
        gs.bonus_turn = bonus
        gs.throws_this_turn += 1

        self._play_dice_sound()
        self.broadcast_l(
            "senet-throw",
            player=player.name,
            result=value,
            bonus="yes" if bonus else "no",
        )

        gs.turn_phase = "moving"

        if not has_any_legal_move(gs, player.player_num, value):
            self.broadcast_personal_l(
                player, "senet-no-moves-you", "senet-no-moves-other",
            )
            self._after_move_or_skip(player)
            return

        self.rebuild_all_menus()

    def _play_dice_sound(self) -> None:
        self.broadcast_sound(f"game_squares/diceroll{random.randint(1, 3)}.ogg")

    # ======================================================================
    # Move application and announcements
    # ======================================================================

    def _apply_and_announce(self, player: SenetPlayer, move) -> None:
        gs = self.game_state
        pnum = player.player_num
        opp_num = opponent_num(pnum)
        opp_player = self._get_player_by_num(opp_num)
        opp_name = opp_player.name if opp_player else "?"

        # Square numbers are 1-indexed for display
        from_sq = move.source + 1

        apply_move(gs, move, pnum)

        if move.is_bear_off:
            remaining = pieces_remaining(gs, pnum)
            self.broadcast_personal_l(
                player,
                "senet-bearoff-you",
                "senet-bearoff-other",
                **{"from": from_sq, "remaining": remaining},
            )
            self.broadcast_sound("mention.ogg", volume=50)
        elif move.is_swap:
            to_sq = move.destination + 1
            self.broadcast_personal_l(
                player,
                "senet-swap-you",
                "senet-swap-other",
                opponent=opp_name,
                **{"from": from_sq, "to": to_sq},
            )
            self.broadcast_sound("game_chess/capture1.ogg")
            if move.water_dest is not None:
                dest_sq = move.water_dest + 1
                self.broadcast_personal_l(
                    player, "senet-water-you", "senet-water-other", dest=dest_sq,
                )
                self.broadcast_sound("game_squares/step1.ogg")
        elif move.water_dest is not None:
            to_sq = move.destination + 1
            self.broadcast_personal_l(
                player,
                "senet-move-you",
                "senet-move-other",
                **{"from": from_sq, "to": to_sq},
            )
            dest_sq = move.water_dest + 1
            self.broadcast_personal_l(
                player, "senet-water-you", "senet-water-other", dest=dest_sq,
            )
            self.broadcast_sound("game_squares/step1.ogg")
        else:
            to_sq = move.destination + 1
            self.broadcast_personal_l(
                player,
                "senet-move-you",
                "senet-move-other",
                **{"from": from_sq, "to": to_sq},
            )
            self.broadcast_sound("game_squares/step1.ogg")

            # Announce reaching House of Happiness
            if move.destination == HOUSE_HAPPINESS:
                self.broadcast_personal_l(
                    player, "senet-happiness-you", "senet-happiness-other",
                )

        # Check win
        if gs.off[pnum] >= PIECES_PER_PLAYER:
            self._handle_win(player)
            return

        self._after_move_or_skip(player)

    def _after_move_or_skip(self, player: SenetPlayer) -> None:
        """Handle post-move: bonus throw or switch turns."""
        gs = self.game_state

        if gs.bonus_turn:
            gs.turn_phase = "throwing"
            gs.current_roll = 0
            gs.bonus_turn = False
            BotHelper.jolt_bots(self, ticks=random.randint(3, 6))
            self.rebuild_all_menus()
        else:
            self._end_turn()

    def _end_turn(self) -> None:
        gs = self.game_state
        opp = opponent_num(gs.current_player_num)
        gs.current_player_num = opp
        gs.turn_phase = "throwing"
        gs.current_roll = 0
        gs.bonus_turn = False
        gs.throws_this_turn = 0

        opp_player = self._get_player_by_num(opp)
        if opp_player:
            self.current_player = opp_player
        self.announce_turn()
        BotHelper.jolt_bots(self, ticks=random.randint(3, 6))
        self.rebuild_all_menus()

    # ======================================================================
    # Win
    # ======================================================================

    def _handle_win(self, winner: SenetPlayer) -> None:
        self.broadcast_l("senet-wins", player=winner.name)
        self.broadcast_sound("game_pig/win.ogg")
        self._winner = winner
        self.finish_game()

    def build_game_result(self) -> GameResult:
        from datetime import datetime

        gs = self.game_state
        winner = getattr(self, "_winner", None)
        p1 = self._get_player_by_num(1)
        p2 = self._get_player_by_num(2)

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
                "p1_name": p1.name if p1 else "?",
                "p2_name": p2.name if p2 else "?",
                "p1_off": gs.off[1],
                "p2_off": gs.off[2],
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        d = result.custom_data
        return [
            Localization.get(
                locale,
                "senet-score",
                p1=d.get("p1_name", "?"),
                off1=d.get("p1_off", 0),
                p2=d.get("p2_name", "?"),
                off2=d.get("p2_off", 0),
            )
        ]

    # ======================================================================
    # Info actions
    # ======================================================================

    def _action_check_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        p1 = self._get_player_by_num(1)
        p2 = self._get_player_by_num(2)
        user.speak_l(
            "senet-status",
            p1=p1.name if p1 else "?",
            off1=gs.off[1],
            p2=p2.name if p2 else "?",
            off2=gs.off[2],
            phase=gs.turn_phase,
            roll=gs.current_roll,
        )

    def _action_check_sticks(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        if gs.current_roll > 0:
            user.speak_l("senet-sticks", result=gs.current_roll)
        else:
            user.speak_l("senet-sticks-none")

    def _action_check_score(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        gs = self.game_state
        p1 = self._get_player_by_num(1)
        p2 = self._get_player_by_num(2)
        user.speak_l(
            "senet-score",
            p1=p1.name if p1 else "?",
            off1=gs.off[1],
            p2=p2.name if p2 else "?",
            off2=gs.off[2],
        )

    # ======================================================================
    # Leave handling
    # ======================================================================

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

    # ======================================================================
    # Visibility / enabled / label / sound callbacks
    # ======================================================================

    def _is_square_enabled(self, player: Player, action_id: str) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, SenetPlayer):
            return "action-not-available"
        gs = self.game_state
        if gs.current_player_num != player.player_num:
            return "action-not-your-turn"
        return None

    def _is_square_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_square_label(self, player: Player, action_id: str) -> str:
        try:
            sq_idx = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return ""

        gs = self.game_state
        locale = self._player_locale(player)
        sq_num = sq_idx + 1
        occupant = gs.board[sq_idx]
        special_key = SPECIAL_SQUARE_NAMES.get(sq_idx)

        if special_key:
            special_name = Localization.get(locale, special_key)
            if occupant == 0:
                return Localization.get(locale, "senet-sq-empty-special", sq=sq_num, name=special_name)
            elif isinstance(player, SenetPlayer) and occupant == player.player_num:
                return Localization.get(locale, "senet-sq-own-special", sq=sq_num, name=special_name)
            else:
                owner = self._get_player_by_num(occupant)
                return Localization.get(
                    locale, "senet-sq-opponent-special",
                    sq=sq_num, name=special_name, owner=owner.name if owner else "?",
                )
        else:
            if occupant == 0:
                return Localization.get(locale, "senet-sq-empty", sq=sq_num)
            elif isinstance(player, SenetPlayer) and occupant == player.player_num:
                return Localization.get(locale, "senet-sq-own", sq=sq_num)
            else:
                owner = self._get_player_by_num(occupant)
                return Localization.get(
                    locale, "senet-sq-opponent", sq=sq_num, owner=owner.name if owner else "?",
                )

    def _get_square_sound(self, player: Player, action_id: str) -> str | None:
        try:
            sq_idx = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return None

        occupant = self.game_state.board[sq_idx]
        if occupant == 0:
            return None

        is_own = isinstance(player, SenetPlayer) and occupant == player.player_num
        if is_own:
            return "game_squares/token1.ogg"
        else:
            return "game_squares/token7.ogg"

    def _is_navigate_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, SenetPlayer):
            return "action-not-available"
        gs = self.game_state
        if gs.turn_phase != "moving" or gs.current_player_num != player.player_num:
            return "action-not-your-turn"
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
