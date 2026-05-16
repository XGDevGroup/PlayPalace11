from __future__ import annotations

from dataclasses import dataclass, field
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility, EditboxInput, MenuInput
from ...game_utils.game_result import GameResult, PlayerResult

from ...game_utils.options import MenuOption, BoolOption, option_field
from ...game_utils.bot_helper import BotHelper
from ...game_utils.poker_timer import PokerTurnTimer
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState
from server.core.users.bot import Bot
from server.core.users.base import User, MenuItem, EscapeBehavior
from .bot import bot_think

TURN_TIMER_CHOICES = ["15", "30", "45", "60", "90", "120", "180", "300", "0"]
TURN_TIMER_LABELS = {
    "15": "poker-timer-15",
    "30": "poker-timer-30",
    "45": "poker-timer-45",
    "60": "poker-timer-60",
    "90": "poker-timer-90",
    "120": "chess-timer-120",
    "180": "chess-timer-180",
    "300": "chess-timer-300",
    "0": "poker-timer-unlimited",
}

# File letters for notation
FILE_LETTERS = "abcdefgh"

# Piece display names (for localization keys)
PIECE_NAMES = {
    "pawn": "chess-piece-pawn",
    "knight": "chess-piece-knight",
    "bishop": "chess-piece-bishop",
    "rook": "chess-piece-rook",
    "queen": "chess-piece-queen",
    "king": "chess-piece-king",
}


def index_to_notation(index: int) -> str:
    """Convert board index (0-63) to chess notation (a1-h8)."""
    file = index % 8
    rank = index // 8 + 1
    return FILE_LETTERS[file] + str(rank)


def notation_to_index(notation: str) -> int | None:
    """Convert chess notation (a1-h8) to board index (0-63)."""
    if len(notation) != 2:
        return None
    file_letter = notation[0].lower()
    if file_letter not in FILE_LETTERS:
        return None
    try:
        rank = int(notation[1])
    except ValueError:
        return None
    if rank < 1 or rank > 8:
        return None
    return (rank - 1) * 8 + FILE_LETTERS.index(file_letter)


def piece_name(piece: str, locale: str) -> str:
    """Get localized piece name."""
    key = PIECE_NAMES.get(piece)
    if key:
        return Localization.get(locale, key)
    return piece


def piece_color_name(piece: str, color: str, locale: str) -> str:
    """Get the grammatically correct localized color word for a piece.

    Looks up the piece's gender from chess-piece-{piece}-gender, then
    returns color-{color}-m or color-{color}-f accordingly.
    """
    gender = Localization.get(locale, f"chess-piece-{piece}-gender")
    if gender not in ("m", "f"):
        gender = "m"
    return Localization.get(locale, f"color-{color}-{gender}")


@dataclass
class ChessOptions(GameOptions):
    """Options for Chess."""

    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            default="0",
            label="chess-set-turn-timer",
            prompt="chess-select-turn-timer",
            change_msg="chess-option-changed-turn-timer",
            choice_labels=TURN_TIMER_LABELS,
        )
    )
    auto_draw: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="chess-toggle-auto-draw",
            change_msg="chess-option-changed-auto-draw",
        )
    )
    show_coordinates: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="chess-toggle-show-coordinates",
            change_msg="chess-option-changed-show-coordinates",
        )
    )


@dataclass
class ChessPlayer(Player):
    color: str = ""  # "white" or "black"
    wins: int = 0


@register_game
@dataclass
class ChessGame(Game):
    """Chess game implementation."""

    players: list[ChessPlayer] = field(default_factory=list)
    options: ChessOptions = field(default_factory=ChessOptions)

    # Board: list of 64 entries, each None or {"piece": str, "color": str, "has_moved": bool}
    board: list[dict | None] = field(default_factory=lambda: [None] * 64)

    # Game state
    current_color: str = "white"
    selected_square: dict[str, int | None] = field(
        default_factory=dict
    )  # player_id -> selected square
    game_over: bool = False
    winner_color: str = ""
    draw_reason: str = ""

    # Castling rights
    castle_white_kingside: bool = True
    castle_white_queenside: bool = True
    castle_black_kingside: bool = True
    castle_black_queenside: bool = True

    # En passant target square (index or -1)
    en_passant_target: int = -1

    # Move tracking
    move_history: list[dict] = field(default_factory=list)
    position_history: list[str] = field(default_factory=list)
    halfmove_clock: int = 0

    # Promotion state
    promotion_pending: bool = False
    promotion_square: int = -1

    # Draw offer / undo request
    draw_offer_from: str = ""  # player_id who offered
    undo_request_from: str = ""  # player_id who requested

    # Timer
    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)
    timer_warning_played: bool = False

    # Board orientation: player_id -> True if board is flipped (rank 1 at top)
    board_flipped: dict[str, bool] = field(default_factory=dict)

    # Turn sound
    _turn_sound_player_id: str | None = None

    def __post_init__(self):
        super().__post_init__()

    # ==========================================================================
    # Metadata
    # ==========================================================================

    @classmethod
    def get_name(cls) -> str:
        return "Chess"

    @classmethod
    def get_type(cls) -> str:
        return "chess"

    @classmethod
    def get_category(cls) -> str:
        return "category-board-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 2

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> ChessPlayer:
        return ChessPlayer(id=player_id, name=name, is_bot=is_bot)

    def add_player(self, name: str, user: User) -> ChessPlayer:
        player = super().add_player(name, user)
        sound = "game_chess/botsit.ogg" if player.is_bot else "game_chess/personsit.ogg"
        self.play_sound(sound)
        return player

    def _perform_leave_game(self, player: Player) -> None:
        if self.status == "playing" and not player.is_bot:
            player.is_bot = True
            self._users.pop(player.id, None)
            bot_user = Bot(player.name, uuid=player.id)
            self.attach_user(player.id, bot_user)
            self.broadcast_l("player-replaced-by-bot", player=player.name)
            self.play_sound("game_chess/personleave.ogg")

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
        leave_sound = "game_chess/botleave.ogg" if player.is_bot else "game_chess/personleave.ogg"
        self.play_sound(leave_sound)

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
    # Action sets
    # ==========================================================================

    def create_turn_action_set(self, player: ChessPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        locale = self._player_locale(player)

        # 64 square actions in visual board order (rank 8 at top, rank 1 at bottom)
        # This ordering ensures the grid display shows the board correctly.
        for rank in range(7, -1, -1):
            for file in range(8):
                i = rank * 8 + file
                action_set.add(
                    Action(
                        id=f"square_{i}",
                        label="",
                        handler="_action_square_click",
                        is_enabled="_is_square_enabled",
                        is_hidden="_is_square_hidden",
                        get_label="_get_square_label",
                        show_in_actions_menu=False,
                        show_disabled_label=False,
                    )
                )

        # Promotion actions (only visible during promotion)
        for piece in ("queen", "rook", "bishop", "knight"):
            action_set.add(
                Action(
                    id=f"promote_{piece}",
                    label=Localization.get(locale, f"chess-piece-{piece}"),
                    handler="_action_promote",
                    is_enabled="_is_promote_enabled",
                    is_hidden="_is_promote_hidden",
                    show_in_actions_menu=False,
                )
            )

        # Draw offer/response
        action_set.add(
            Action(
                id="offer_draw",
                label=Localization.get(locale, "chess-offer-draw"),
                handler="_action_offer_draw",
                is_enabled="_is_offer_draw_enabled",
                is_hidden="_is_offer_draw_hidden",
                show_in_actions_menu=True,
            )
        )
        action_set.add(
            Action(
                id="accept_draw",
                label=Localization.get(locale, "chess-you-accept-draw"),
                handler="_action_accept_draw",
                is_enabled="_is_draw_response_enabled",
                is_hidden="_is_draw_response_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="decline_draw",
                label=Localization.get(locale, "chess-you-decline-draw"),
                handler="_action_decline_draw",
                is_enabled="_is_draw_response_enabled",
                is_hidden="_is_draw_response_hidden",
                show_in_actions_menu=False,
            )
        )

        # Undo
        action_set.add(
            Action(
                id="request_undo",
                label=Localization.get(locale, "chess-undo-request"),
                handler="_action_request_undo",
                is_enabled="_is_request_undo_enabled",
                is_hidden="_is_request_undo_hidden",
                show_in_actions_menu=True,
            )
        )
        action_set.add(
            Action(
                id="accept_undo",
                label=Localization.get(locale, "chess-you-accept-undo"),
                handler="_action_accept_undo",
                is_enabled="_is_undo_response_enabled",
                is_hidden="_is_undo_response_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="decline_undo",
                label=Localization.get(locale, "chess-you-decline-undo"),
                handler="_action_decline_undo",
                is_enabled="_is_undo_response_enabled",
                is_hidden="_is_undo_response_hidden",
                show_in_actions_menu=False,
            )
        )

        # Resign
        action_set.add(
            Action(
                id="resign",
                label=Localization.get(locale, "chess-resign"),
                handler="_action_resign",
                is_enabled="_is_resign_enabled",
                is_hidden="_is_resign_hidden",
                show_in_actions_menu=True,
                input_request=MenuInput(
                    prompt="chess-resign-confirm",
                    options="_resign_confirm_options",
                    include_cancel=False,
                ),
            )
        )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        local_actions = [
            Action(
                id="view_board",
                label=Localization.get(locale, "chess-view-board"),
                handler="_action_view_board",
                is_enabled="_is_check_enabled",
                is_hidden="_is_always_hidden",
            ),
            Action(
                id="flip_board",
                label=Localization.get(locale, "chess-flip-board"),
                handler="_action_flip_board",
                is_enabled="_is_check_enabled",
                is_hidden="_is_always_hidden",
            ),
            Action(
                id="check_status",
                label=Localization.get(locale, "chess-check-status"),
                handler="_action_check_status",
                is_enabled="_is_check_enabled",
                is_hidden="_is_always_hidden",
            ),
            Action(
                id="type_move",
                label=Localization.get(locale, "chess-type-move"),
                handler="_action_type_move",
                is_enabled="_is_type_move_enabled",
                is_hidden="_is_always_hidden",
                input_request=EditboxInput(prompt="chess-enter-move"),
            ),
            Action(
                id="import_fen",
                label=Localization.get(locale, "chess-import-fen"),
                handler="_action_import_fen",
                is_enabled="_is_check_enabled",
                is_hidden="_is_always_hidden",
                input_request=None,
            ),
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "chess-check-turn-timer"),
                handler="_action_check_turn_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_always_hidden",
            ),
        ]
        for action in reversed(local_actions):
            action_set.add(action)
            if action.id in action_set._order:
                action_set._order.remove(action.id)
            action_set._order.insert(0, action.id)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind(
            "b", "View board", ["view_board"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "s",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind("m", "Type a move", ["type_move"], state=KeybindState.ACTIVE)
        self.define_keybind("i", "Import FEN", ["import_fen"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "shift+t",
            "Turn timer",
            ["check_turn_timer"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "shift+f",
            "Flip board",
            ["flip_board"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind("shift+d", "Offer draw", ["offer_draw"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+u", "Request undo", ["request_undo"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+r", "Resign", ["resign"], state=KeybindState.ACTIVE)
        # Draw response
        self.define_keybind("y", "Accept draw", ["accept_draw"], state=KeybindState.ACTIVE)
        self.define_keybind("n", "Decline draw", ["decline_draw"], state=KeybindState.ACTIVE)
        # Undo response (reuse y/n)
        self.define_keybind("y", "Accept undo", ["accept_undo"], state=KeybindState.ACTIVE)
        self.define_keybind("n", "Decline undo", ["decline_undo"], state=KeybindState.ACTIVE)
        # Promotion
        self.define_keybind("q", "Promote queen", ["promote_queen"], state=KeybindState.ACTIVE)
        self.define_keybind("r", "Promote rook", ["promote_rook"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "shift+b", "Promote bishop", ["promote_bishop"], state=KeybindState.ACTIVE
        )
        self.define_keybind("k", "Promote knight", ["promote_knight"], state=KeybindState.ACTIVE)

    # ==========================================================================
    # Menu overrides (grid mode for chess board)
    # ==========================================================================

    def rebuild_player_menu(self, player: "Player", *, position: int | None = None) -> None:
        """Override to enable grid mode only when the board squares are shown."""
        if self._destroyed or self.status == "finished":
            return
        if self._is_transient_display_open(player):
            return
        user = self.get_user(player)
        if not user:
            return

        square_items: list[MenuItem] = []
        other_items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            label = resolved.label
            if not resolved.enabled and resolved.action.show_disabled_label:
                unavailable = Localization.get(user.locale, "visibility-unavailable")
                label = f"{label}; {unavailable}"
            item = MenuItem(text=label, id=resolved.action.id, sound=resolved.sound)
            if resolved.action.id.startswith("square_"):
                square_items.append(item)
            else:
                other_items.append(item)

        # Only enable grid mode when the 64 board squares are visible
        use_grid = len(square_items) == 64

        if use_grid and self.board_flipped.get(player.id, False):
            square_items.reverse()

        user.show_menu(
            "turn_menu",
            square_items + other_items,
            multiletter=False,
            escape_behavior=EscapeBehavior.KEYBIND,
            position=position,
            grid_enabled=use_grid,
            grid_width=8 if use_grid else 1,
        )

    # ==========================================================================
    # Game flow
    # ==========================================================================

    def on_start(self) -> None:
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 1

        self.play_music("game_chess/mus.ogg")

        active_players = [p for p in self.players if not p.is_spectator]
        self.set_turn_players(active_players, reset_index=True)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Assign colors randomly
        if random.random() < 0.5:  # nosec B311
            active_players[0].color = "white"
            active_players[1].color = "black"
        else:
            active_players[0].color = "black"
            active_players[1].color = "white"

        white_player = self._get_player_by_color("white")
        black_player = self._get_player_by_color("black")

        # Default orientation: black player views from black's side
        if black_player:
            self.board_flipped[black_player.id] = True

        # Initialize board
        self._init_board()

        self.broadcast_l(
            "chess-game-started",
            white=white_player.name if white_player else "?",
            black=black_player.name if black_player else "?",
        )
        self.play_sound("game_chess/intro.ogg")

        # Set turn to white
        if white_player:
            self.current_player = white_player

        self._start_turn()

    def on_tick(self) -> None:
        super().on_tick()
        if not self.game_active:
            return
        if self.timer.tick():
            self._handle_turn_timeout()
        self._maybe_play_timer_warning()
        BotHelper.on_tick(self)

    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, ChessPlayer):
            return

        self.current_color = player.color
        self.timer_warning_played = False

        # Clear selections
        self.selected_square = {}

        # Clear pending offers/requests
        self.draw_offer_from = ""
        self.undo_request_from = ""

        self._start_turn_timer()
        self.rebuild_all_menus()
        self.broadcast_personal_l(player, "game-your-turn", "game-turn-start")

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 60))  # nosec B311

    def _advance_turn(self) -> None:
        self.advance_turn(announce=False)
        self._start_turn()

    def _start_turn_timer(self) -> None:
        try:
            seconds = int(self.options.turn_timer)
        except ValueError:
            seconds = 0
        if seconds <= 0:
            self.timer.clear()
            return
        self.timer.start(seconds)
        self.timer_warning_played = False

    def _maybe_play_timer_warning(self) -> None:
        try:
            seconds = int(self.options.turn_timer)
        except ValueError:
            seconds = 0
        if seconds < 20:
            return
        if self.timer_warning_played:
            return
        if self.timer.seconds_remaining() == 5:
            self.timer_warning_played = True
            self.play_sound("game_chess/fivesec.ogg")

    def _handle_turn_timeout(self) -> None:
        player = self.current_player
        if not isinstance(player, ChessPlayer):
            return
        self.play_sound("game_chess/expired.ogg")
        # Force a bot move
        action_id = bot_think(self, player)
        if action_id:
            self.execute_action(player, action_id)

    def bot_think(self, player: ChessPlayer) -> str | None:
        return bot_think(self, player)

    def execute_action(self, player, action_id, input_value=None, context=None):
        """Override to handle bot combined move format: square_{from}_{to}."""
        if action_id and action_id.startswith("square_") and action_id.count("_") == 2:
            # Combined bot move - route to square click handler directly
            if isinstance(player, ChessPlayer):
                self._action_square_click(player, action_id)
                return
        # Speak the confirmation prompt before the resign menu appears
        if action_id == "resign" and input_value is None and not player.is_bot:
            user = self.get_user(player)
            if user:
                user.speak_l("chess-resign-confirm")
        super().execute_action(player, action_id, input_value=input_value, context=context)

    # ==========================================================================
    # Board initialization
    # ==========================================================================

    def _init_board(self) -> None:
        """Initialize board to standard starting position."""
        self.board = [None] * 64

        # White back rank (rank 1, indices 0-7)
        back_rank = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for i, piece in enumerate(back_rank):
            self.board[i] = {"piece": piece, "color": "white", "has_moved": False}

        # White pawns (rank 2, indices 8-15)
        for i in range(8, 16):
            self.board[i] = {"piece": "pawn", "color": "white", "has_moved": False}

        # Black pawns (rank 7, indices 48-55)
        for i in range(48, 56):
            self.board[i] = {"piece": "pawn", "color": "black", "has_moved": False}

        # Black back rank (rank 8, indices 56-63)
        for i, piece in enumerate(back_rank):
            self.board[56 + i] = {"piece": piece, "color": "black", "has_moved": False}

        # Reset state
        self.current_color = "white"
        self.selected_square = {}
        self.game_over = False
        self.winner_color = ""
        self.draw_reason = ""
        self.castle_white_kingside = True
        self.castle_white_queenside = True
        self.castle_black_kingside = True
        self.castle_black_queenside = True
        self.en_passant_target = -1
        self.move_history = []
        self.position_history = []
        self.halfmove_clock = 0
        self.promotion_pending = False
        self.promotion_square = -1
        self.draw_offer_from = ""
        self.undo_request_from = ""

    # ==========================================================================
    # Piece movement validation
    # ==========================================================================

    def _is_valid_piece_move(self, from_sq: int, to_sq: int, piece: dict) -> bool:
        """Check if move is valid for piece type (ignoring check)."""
        from_file = from_sq % 8
        from_rank = from_sq // 8
        to_file = to_sq % 8
        to_rank = to_sq // 8
        file_diff = abs(to_file - from_file)
        rank_diff = abs(to_rank - from_rank)

        p = piece["piece"]

        if p == "pawn":
            return self._is_valid_pawn_move(
                from_sq, to_sq, piece, from_file, from_rank, to_file, to_rank, file_diff, rank_diff
            )
        elif p == "knight":
            return (file_diff == 2 and rank_diff == 1) or (file_diff == 1 and rank_diff == 2)
        elif p == "bishop":
            return file_diff == rank_diff and file_diff > 0 and self._is_path_clear(from_sq, to_sq)
        elif p == "rook":
            return (
                (file_diff == 0 or rank_diff == 0)
                and (file_diff + rank_diff > 0)
                and self._is_path_clear(from_sq, to_sq)
            )
        elif p == "queen":
            if file_diff == rank_diff and file_diff > 0:
                return self._is_path_clear(from_sq, to_sq)
            if (file_diff == 0 or rank_diff == 0) and (file_diff + rank_diff > 0):
                return self._is_path_clear(from_sq, to_sq)
            return False
        elif p == "king":
            return file_diff <= 1 and rank_diff <= 1 and (file_diff + rank_diff > 0)

        return False

    def _is_valid_pawn_move(
        self,
        from_sq: int,
        to_sq: int,
        piece: dict,
        from_file: int,
        from_rank: int,
        to_file: int,
        to_rank: int,
        file_diff: int,
        rank_diff: int,
    ) -> bool:
        direction = 1 if piece["color"] == "white" else -1
        start_rank = 1 if piece["color"] == "white" else 6

        # Forward move
        if to_file == from_file:
            if to_rank == from_rank + direction and self.board[to_sq] is None:
                return True
            if from_rank == start_rank and to_rank == from_rank + 2 * direction:
                middle = from_sq + 8 * direction
                if self.board[middle] is None and self.board[to_sq] is None:
                    return True

        # Capture (including en passant)
        if file_diff == 1 and to_rank == from_rank + direction:
            if self.board[to_sq] is not None:
                return True
            if to_sq == self.en_passant_target:
                return True

        return False

    def _is_path_clear(self, from_sq: int, to_sq: int) -> bool:
        """Check if path between squares is clear (for sliding pieces)."""
        from_file = from_sq % 8
        from_rank = from_sq // 8
        to_file = to_sq % 8
        to_rank = to_sq // 8

        file_step = (1 if to_file > from_file else -1) if to_file != from_file else 0
        rank_step = (1 if to_rank > from_rank else -1) if to_rank != from_rank else 0

        current_file = from_file + file_step
        current_rank = from_rank + rank_step

        while current_file != to_file or current_rank != to_rank:
            index = current_rank * 8 + current_file
            if self.board[index] is not None:
                return False
            current_file += file_step
            current_rank += rank_step

        return True

    def _find_king(self, color: str) -> int | None:
        """Find king position for a color."""
        for i in range(64):
            sq = self.board[i]
            if sq and sq["piece"] == "king" and sq["color"] == color:
                return i
        return None

    def _can_piece_attack(self, from_sq: int, to_sq: int, piece: dict) -> bool:
        """Check if a piece can attack a square (ignoring check)."""
        if from_sq == to_sq:
            return False

        from_file = from_sq % 8
        from_rank = from_sq // 8
        to_file = to_sq % 8
        to_rank = to_sq // 8
        file_diff = abs(to_file - from_file)
        rank_diff = abs(to_rank - from_rank)
        p = piece["piece"]

        if p == "pawn":
            direction = 1 if piece["color"] == "white" else -1
            return file_diff == 1 and to_rank == from_rank + direction
        elif p == "knight":
            return (file_diff == 2 and rank_diff == 1) or (file_diff == 1 and rank_diff == 2)
        elif p == "bishop":
            return file_diff == rank_diff and file_diff > 0 and self._is_path_clear(from_sq, to_sq)
        elif p == "rook":
            return (
                (file_diff == 0 or rank_diff == 0)
                and (file_diff + rank_diff > 0)
                and self._is_path_clear(from_sq, to_sq)
            )
        elif p == "queen":
            if file_diff == rank_diff and file_diff > 0:
                return self._is_path_clear(from_sq, to_sq)
            if (file_diff == 0 or rank_diff == 0) and (file_diff + rank_diff > 0):
                return self._is_path_clear(from_sq, to_sq)
            return False
        elif p == "king":
            return file_diff <= 1 and rank_diff <= 1

        return False

    def _is_square_attacked(self, square: int, by_color: str) -> bool:
        """Check if a square is attacked by the given color."""
        for i in range(64):
            sq = self.board[i]
            if sq and sq["color"] == by_color:
                if self._can_piece_attack(i, square, sq):
                    return True
        return False

    def is_in_check(self, color: str) -> bool:
        """Check if a color's king is in check."""
        king_sq = self._find_king(color)
        if king_sq is None:
            return False
        opponent = "black" if color == "white" else "white"
        return self._is_square_attacked(king_sq, opponent)

    def _is_legal_move(self, from_sq: int, to_sq: int, color: str) -> tuple[bool, str]:
        """Check if a move is legal (including check validation)."""
        piece = self.board[from_sq]
        if not piece:
            return False, "No piece at source square"
        if piece["color"] != color:
            return False, "Not your piece"
        target = self.board[to_sq]
        if target and target["color"] == color:
            return False, "Cannot capture your own piece"

        # Check for castling
        if piece["piece"] == "king":
            is_castle, castle_type = self._is_castling_move(from_sq, to_sq, color)
            if is_castle:
                legal, reason = self._is_castling_legal(color, castle_type)
                return legal, reason

        # Check piece-specific movement
        if not self._is_valid_piece_move(from_sq, to_sq, piece):
            return False, "Invalid move for this piece"

        # Simulate move to check if it leaves king in check
        saved = self.save_position()
        self.execute_move_silent(from_sq, to_sq)
        king_in_check = self.is_in_check(color)
        self.restore_position(saved)

        if king_in_check:
            return False, "Move leaves king in check"

        return True, ""

    def get_legal_moves(self, color: str) -> list[dict]:
        """Generate all legal moves for a color."""
        moves = []
        for from_sq in range(64):
            piece = self.board[from_sq]
            if not piece or piece["color"] != color:
                continue
            candidates = self._get_candidate_squares(from_sq, piece)
            for to_sq in candidates:
                legal, _ = self._is_legal_move(from_sq, to_sq, color)
                if legal:
                    moves.append({"from": from_sq, "to": to_sq})
        return moves

    def _get_candidate_squares(self, from_sq: int, piece: dict) -> list[int]:
        """Get candidate destination squares for a piece (fast pre-filter)."""
        p = piece["piece"]
        from_file = from_sq % 8
        from_rank = from_sq // 8
        candidates = []

        if p == "pawn":
            direction = 1 if piece["color"] == "white" else -1
            start_rank = 1 if piece["color"] == "white" else 6
            # Forward
            fwd = from_sq + 8 * direction
            if 0 <= fwd < 64:
                candidates.append(fwd)
            # Double forward
            if from_rank == start_rank:
                dbl = from_sq + 16 * direction
                if 0 <= dbl < 64:
                    candidates.append(dbl)
            # Captures
            for df in (-1, 1):
                tf = from_file + df
                if 0 <= tf < 7 + 1:
                    cap = fwd + df if 0 <= fwd + df < 64 else -1
                    # Recalculate properly
                    tr = from_rank + direction
                    if 0 <= tr < 8:
                        cap = tr * 8 + tf
                        candidates.append(cap)

        elif p == "knight":
            for dr, df in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                tr, tf = from_rank + dr, from_file + df
                if 0 <= tr < 8 and 0 <= tf < 8:
                    candidates.append(tr * 8 + tf)

        elif p == "bishop":
            for dr, df in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                r, f = from_rank + dr, from_file + df
                while 0 <= r < 8 and 0 <= f < 8:
                    candidates.append(r * 8 + f)
                    if self.board[r * 8 + f] is not None:
                        break
                    r += dr
                    f += df

        elif p == "rook":
            for dr, df in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                r, f = from_rank + dr, from_file + df
                while 0 <= r < 8 and 0 <= f < 8:
                    candidates.append(r * 8 + f)
                    if self.board[r * 8 + f] is not None:
                        break
                    r += dr
                    f += df

        elif p == "queen":
            for dr, df in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                r, f = from_rank + dr, from_file + df
                while 0 <= r < 8 and 0 <= f < 8:
                    candidates.append(r * 8 + f)
                    if self.board[r * 8 + f] is not None:
                        break
                    r += dr
                    f += df

        elif p == "king":
            for dr in (-1, 0, 1):
                for df in (-1, 0, 1):
                    if dr == 0 and df == 0:
                        continue
                    tr, tf = from_rank + dr, from_file + df
                    if 0 <= tr < 8 and 0 <= tf < 8:
                        candidates.append(tr * 8 + tf)
            # Castling candidates
            candidates.append(from_sq + 2)  # Kingside
            candidates.append(from_sq - 2)  # Queenside

        return [sq for sq in candidates if 0 <= sq < 64]

    # ==========================================================================
    # Castling
    # ==========================================================================

    def _is_castling_move(self, from_sq: int, to_sq: int, color: str) -> tuple[bool, str]:
        """Check if a move is a castling attempt."""
        piece = self.board[from_sq]
        if not piece or piece["piece"] != "king":
            return False, ""
        file_diff = (to_sq % 8) - (from_sq % 8)
        if file_diff == 2:
            return True, "kingside"
        if file_diff == -2:
            return True, "queenside"
        return False, ""

    def _is_castling_legal(self, color: str, castle_type: str) -> tuple[bool, str]:
        """Check if castling is legal."""
        rank = 0 if color == "white" else 7
        king_sq = rank * 8 + 4

        king = self.board[king_sq]
        if not king or king["piece"] != "king" or king["color"] != color:
            return False, "King not on starting square"
        if king.get("has_moved", False):
            return False, "King has moved"

        if castle_type == "kingside":
            if color == "white" and not self.castle_white_kingside:
                return False, "No castling rights"
            if color == "black" and not self.castle_black_kingside:
                return False, "No castling rights"

            f_sq = rank * 8 + 5
            g_sq = rank * 8 + 6
            rook_sq = rank * 8 + 7

            if self.board[f_sq] or self.board[g_sq]:
                return False, "Squares not empty"

            rook = self.board[rook_sq]
            if not rook or rook["piece"] != "rook" or rook["color"] != color:
                return False, "Rook not present"
            if rook.get("has_moved", False):
                return False, "Rook has moved"

            if self.is_in_check(color):
                return False, "Cannot castle out of check"

            # Check intermediate square
            opponent = "black" if color == "white" else "white"
            if self._is_square_attacked(f_sq, opponent):
                return False, "Cannot castle through check"
            if self._is_square_attacked(g_sq, opponent):
                return False, "Cannot castle into check"

            return True, ""

        elif castle_type == "queenside":
            if color == "white" and not self.castle_white_queenside:
                return False, "No castling rights"
            if color == "black" and not self.castle_black_queenside:
                return False, "No castling rights"

            b_sq = rank * 8 + 1
            c_sq = rank * 8 + 2
            d_sq = rank * 8 + 3
            rook_sq = rank * 8

            if self.board[b_sq] or self.board[c_sq] or self.board[d_sq]:
                return False, "Squares not empty"

            rook = self.board[rook_sq]
            if not rook or rook["piece"] != "rook" or rook["color"] != color:
                return False, "Rook not present"
            if rook.get("has_moved", False):
                return False, "Rook has moved"

            if self.is_in_check(color):
                return False, "Cannot castle out of check"

            opponent = "black" if color == "white" else "white"
            if self._is_square_attacked(d_sq, opponent):
                return False, "Cannot castle through check"
            if self._is_square_attacked(c_sq, opponent):
                return False, "Cannot castle into check"

            return True, ""

        return False, "Invalid castle type"

    def _execute_castling(self, color: str, castle_type: str) -> None:
        """Execute a castling move."""
        rank = 0 if color == "white" else 7
        king_sq = rank * 8 + 4

        if castle_type == "kingside":
            new_king = rank * 8 + 6
            old_rook = rank * 8 + 7
            new_rook = rank * 8 + 5
        else:
            new_king = rank * 8 + 2
            old_rook = rank * 8
            new_rook = rank * 8 + 3

        self.board[new_king] = self.board[king_sq]
        self.board[king_sq] = None
        self.board[new_rook] = self.board[old_rook]
        self.board[old_rook] = None

        if self.board[new_king]:
            self.board[new_king]["has_moved"] = True
        if self.board[new_rook]:
            self.board[new_rook]["has_moved"] = True

        # Update castling rights
        if color == "white":
            self.castle_white_kingside = False
            self.castle_white_queenside = False
        else:
            self.castle_black_kingside = False
            self.castle_black_queenside = False

        self.halfmove_clock += 1
        self.en_passant_target = -1

    # ==========================================================================
    # Move execution
    # ==========================================================================

    def execute_move_silent(self, from_sq: int, to_sq: int) -> None:
        """Execute a move without sounds/broadcasts (for AI search)."""
        piece = self.board[from_sq]
        if not piece:
            return

        # Handle en passant capture
        if piece["piece"] == "pawn" and to_sq == self.en_passant_target:
            direction = -1 if piece["color"] == "white" else 1
            captured_sq = to_sq + 8 * direction
            self.board[captured_sq] = None

        # Handle castling
        is_castle, castle_type = self._is_castling_move(from_sq, to_sq, piece["color"])
        if is_castle:
            self._execute_castling(piece["color"], castle_type)
            return

        # Execute move
        self.board[to_sq] = piece
        self.board[from_sq] = None

        # Update en passant
        self.en_passant_target = -1
        if piece["piece"] == "pawn":
            from_rank = from_sq // 8
            to_rank = to_sq // 8
            if abs(to_rank - from_rank) == 2:
                direction = 1 if piece["color"] == "white" else -1
                self.en_passant_target = from_sq + 8 * direction

        # Update castling rights
        self._update_castling_rights(from_sq, piece)

        piece["has_moved"] = True

        # Auto-promote to queen in silent mode
        to_rank = to_sq // 8
        if piece["piece"] == "pawn":
            if (piece["color"] == "white" and to_rank == 7) or (
                piece["color"] == "black" and to_rank == 0
            ):
                self.board[to_sq] = {"piece": "queen", "color": piece["color"], "has_moved": True}

    def _execute_move_full(self, player: ChessPlayer, from_sq: int, to_sq: int) -> None:
        """Execute a move with full sound/broadcast support."""
        piece = self.board[from_sq]
        if not piece:
            return
        target = self.board[to_sq]
        from_notation = index_to_notation(from_sq)
        to_notation = index_to_notation(to_sq)

        # Check for castling
        is_castle, castle_type = self._is_castling_move(from_sq, to_sq, piece["color"])
        if is_castle:
            self._execute_castling(piece["color"], castle_type)
            self.play_sound("game_chess/moveking.ogg")
            if castle_type == "kingside":
                self.broadcast_personal_l(
                    player, "chess-you-castle-kingside", "chess-player-castles-kingside"
                )
            else:
                self.broadcast_personal_l(
                    player, "chess-you-castle-queenside", "chess-player-castles-queenside"
                )
            self._record_move(from_sq, to_sq, piece, target, castle_type)
            self._post_move_checks(player)
            return

        # Check for en passant
        en_passant = piece["piece"] == "pawn" and to_sq == self.en_passant_target
        if en_passant:
            direction = -1 if piece["color"] == "white" else 1
            captured_sq = to_sq + 8 * direction
            self.board[captured_sq] = None
            self.play_sound(f"game_chess/capture{random.randint(1, 2)}.ogg")  # nosec B311
            self.broadcast_personal_l(
                player,
                "chess-you-en-passant",
                "chess-player-en-passant",
                to=to_notation,
                **{"from": from_notation},
            )

        # Execute move
        self.board[to_sq] = piece
        self.board[from_sq] = None

        # Broadcast and play sounds
        if not en_passant:
            if target:
                self.play_sound(f"game_chess/capture{random.randint(1, 2)}.ogg")  # nosec B311
                self._broadcast_move(
                    player,
                    "chess-you-capture",
                    "chess-player-captures",
                    pieces={"piece": piece["piece"], "captured": target["piece"]},
                    to=to_notation,
                    **{"from": from_notation},
                )
            else:
                self._play_piece_sound(piece["piece"])
                self._broadcast_move(
                    player,
                    "chess-you-move",
                    "chess-player-moves",
                    pieces={"piece": piece["piece"]},
                    to=to_notation,
                    **{"from": from_notation},
                )

        # Mark as moved
        piece["has_moved"] = True

        # Update castling rights
        self._update_castling_rights(from_sq, piece)

        # Update en passant target
        self.en_passant_target = -1
        if piece["piece"] == "pawn":
            from_rank = from_sq // 8
            to_rank = to_sq // 8
            if abs(to_rank - from_rank) == 2:
                direction = 1 if piece["color"] == "white" else -1
                self.en_passant_target = from_sq + 8 * direction

        # Update halfmove clock
        if piece["piece"] == "pawn" or target:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Record move
        self._record_move(from_sq, to_sq, piece, target, "")

        # Check for promotion
        to_rank = to_sq // 8
        if piece["piece"] == "pawn":
            if (piece["color"] == "white" and to_rank == 7) or (
                piece["color"] == "black" and to_rank == 0
            ):
                self.promotion_pending = True
                self.promotion_square = to_sq
                self.rebuild_all_menus()
                if player.is_bot:
                    BotHelper.jolt_bot(player, ticks=random.randint(10, 20))  # nosec B311
                return

        self._post_move_checks(player)

    def _play_piece_sound(self, piece_type: str) -> None:
        """Play movement sound for a piece type."""
        sounds = {
            "pawn": f"game_chess/movepawn{random.randint(1, 3)}.ogg",  # nosec B311
            "knight": "game_chess/moveknight.ogg",
            "bishop": "game_chess/movebishop.ogg",
            "rook": "game_chess/moverook.ogg",
            "queen": "game_chess/movequeen.ogg",
            "king": "game_chess/moveking.ogg",
        }
        sound = sounds.get(piece_type, "game_chess/movepawn1.ogg")
        self.play_sound(sound)

    def _update_castling_rights(self, from_sq: int, piece: dict) -> None:
        """Update castling rights after a move."""
        if piece["piece"] == "king":
            if piece["color"] == "white":
                self.castle_white_kingside = False
                self.castle_white_queenside = False
            else:
                self.castle_black_kingside = False
                self.castle_black_queenside = False
        elif piece["piece"] == "rook":
            if from_sq == 0:
                self.castle_white_queenside = False
            elif from_sq == 7:
                self.castle_white_kingside = False
            elif from_sq == 56:
                self.castle_black_queenside = False
            elif from_sq == 63:
                self.castle_black_kingside = False

    def _record_move(
        self, from_sq: int, to_sq: int, piece: dict, target: dict | None, special: str
    ) -> None:
        """Record a move in history."""
        self.move_history.append(
            {
                "from": from_sq,
                "to": to_sq,
                "piece": piece["piece"],
                "color": piece["color"],
                "captured": target["piece"] if target else "",
                "special": special,
            }
        )
        self.position_history.append(self._get_position_hash())

    def _post_move_checks(self, player: ChessPlayer) -> None:
        """Check for checkmate, stalemate, draws after a move."""
        opponent_color = "black" if player.color == "white" else "white"
        opponent = self._get_player_by_color(opponent_color)

        # Check for check
        in_check = self.is_in_check(opponent_color)

        # Check for checkmate
        if self.is_checkmate(opponent_color):
            self.game_over = True
            self.winner_color = player.color
            self.play_sound("game_chess/checkmate.ogg")
            self.broadcast_personal_l(
                player, "chess-you-win-checkmate", "chess-checkmate", winner=player.name
            )
            self._end_game(player)
            return

        # Check for stalemate
        if self.is_stalemate(opponent_color):
            self.game_over = True
            self.draw_reason = "stalemate"
            self.play_sound("game_chess/draw.ogg")
            self.broadcast_l("chess-stalemate")
            self._end_game_draw()
            return

        # Check for draw conditions
        if self.options.auto_draw:
            draw = self._check_draw_conditions()
            if draw:
                return

        if in_check:
            self.schedule_sound("game_chess/check.ogg", delay_ticks=5)
            self.broadcast_l("chess-check")

        self._advance_turn()

    # ==========================================================================
    # Check/checkmate/stalemate
    # ==========================================================================

    def is_checkmate(self, color: str) -> bool:
        if not self.is_in_check(color):
            return False
        return len(self.get_legal_moves(color)) == 0

    def is_stalemate(self, color: str) -> bool:
        if self.is_in_check(color):
            return False
        return len(self.get_legal_moves(color)) == 0

    def _check_draw_conditions(self) -> bool:
        """Check automatic draw conditions. Returns True if draw."""
        # Fifty-move rule
        if self.halfmove_clock >= 100:
            self.game_over = True
            self.draw_reason = "fifty_move_rule"
            self.play_sound("game_chess/draw.ogg")
            self.broadcast_l("chess-draw-fifty")
            self._end_game_draw()
            return True

        # Threefold repetition
        if self.position_history:
            current = self.position_history[-1]
            count = sum(1 for p in self.position_history if p == current)
            if count >= 3:
                self.game_over = True
                self.draw_reason = "threefold_repetition"
                self.play_sound("game_chess/draw.ogg")
                self.broadcast_l("chess-draw-repetition")
                self._end_game_draw()
                return True

        # Insufficient material
        if self._is_insufficient_material():
            self.game_over = True
            self.draw_reason = "insufficient_material"
            self.play_sound("game_chess/draw.ogg")
            self.broadcast_l("chess-draw-material")
            self._end_game_draw()
            return True

        return False

    def _is_insufficient_material(self) -> bool:
        """Check if neither side can checkmate."""
        pieces = []
        for i in range(64):
            if self.board[i]:
                pieces.append(self.board[i])

        # King vs King
        if len(pieces) == 2:
            return True

        # King + minor piece vs King
        if len(pieces) == 3:
            for p in pieces:
                if p["piece"] in ("bishop", "knight"):
                    return True

        # King + Bishop vs King + Bishop (same color)
        if len(pieces) == 4:
            bishops = []
            for i in range(64):
                if self.board[i] and self.board[i]["piece"] == "bishop":
                    bishops.append(i)
            if len(bishops) == 2:
                # Check if bishops are on same color
                color1 = (bishops[0] // 8 + bishops[0] % 8) % 2
                color2 = (bishops[1] // 8 + bishops[1] % 8) % 2
                if color1 == color2:
                    return True

        return False

    # ==========================================================================
    # Position save/restore (for AI search)
    # ==========================================================================

    def save_position(self) -> dict:
        """Save current board state for rollback."""
        board_copy = []
        for sq in self.board:
            if sq is None:
                board_copy.append(None)
            else:
                board_copy.append(dict(sq))
        return {
            "board": board_copy,
            "en_passant": self.en_passant_target,
            "castle_wk": self.castle_white_kingside,
            "castle_wq": self.castle_white_queenside,
            "castle_bk": self.castle_black_kingside,
            "castle_bq": self.castle_black_queenside,
            "halfmove": self.halfmove_clock,
        }

    def restore_position(self, saved: dict) -> None:
        """Restore a saved board state."""
        self.board = saved["board"]
        self.en_passant_target = saved["en_passant"]
        self.castle_white_kingside = saved["castle_wk"]
        self.castle_white_queenside = saved["castle_wq"]
        self.castle_black_kingside = saved["castle_bk"]
        self.castle_black_queenside = saved["castle_bq"]
        self.halfmove_clock = saved["halfmove"]

    # ==========================================================================
    # Position hash
    # ==========================================================================

    def _get_position_hash(self) -> str:
        """Get a string hash of the current position for repetition detection."""
        parts = []
        for i in range(64):
            sq = self.board[i]
            if sq:
                parts.append(f"{i}:{sq['color'][0]}{sq['piece'][0]}")

        castling = ""
        if self.castle_white_kingside:
            castling += "K"
        if self.castle_white_queenside:
            castling += "Q"
        if self.castle_black_kingside:
            castling += "k"
        if self.castle_black_queenside:
            castling += "q"
        parts.append(f"c:{castling}")

        if self.en_passant_target >= 0:
            parts.append(f"ep:{self.en_passant_target}")

        parts.append(f"t:{self.current_color}")

        return "|".join(parts)

    # ==========================================================================
    # FEN import/export
    # ==========================================================================

    def _load_fen(self, fen_string: str) -> tuple[bool, str]:
        """Load board from FEN string."""
        parts = fen_string.strip().split()
        if len(parts) < 1:
            return False, "Invalid FEN"

        board_fen = parts[0]
        new_board: list[dict | None] = [None] * 64

        rank = 7
        file = 0

        for char in board_fen:
            if char == "/":
                rank -= 1
                file = 0
                if rank < 0:
                    return False, "Too many ranks"
            elif char.isdigit():
                file += int(char)
            else:
                if file > 7 or rank < 0:
                    return False, "Invalid position"
                index = rank * 8 + file
                color = "white" if char.isupper() else "black"
                piece_map = {
                    "p": "pawn",
                    "n": "knight",
                    "b": "bishop",
                    "r": "rook",
                    "q": "queen",
                    "k": "king",
                }
                piece = piece_map.get(char.lower())
                if not piece:
                    return False, f"Unknown piece: {char}"
                new_board[index] = {"piece": piece, "color": color, "has_moved": True}
                file += 1

        self.board = new_board

        if len(parts) > 1:
            self.current_color = "white" if parts[1] == "w" else "black"

        if len(parts) > 2:
            castling = parts[2]
            self.castle_white_kingside = "K" in castling
            self.castle_white_queenside = "Q" in castling
            self.castle_black_kingside = "k" in castling
            self.castle_black_queenside = "q" in castling

        if len(parts) > 3 and parts[3] != "-":
            ep = notation_to_index(parts[3])
            self.en_passant_target = ep if ep is not None else -1
        else:
            self.en_passant_target = -1

        if len(parts) > 4:
            try:
                self.halfmove_clock = int(parts[4])
            except ValueError:
                self.halfmove_clock = 0

        self.selected_square = {}
        self.promotion_pending = False
        self.promotion_square = -1
        self.position_history = [self._get_position_hash()]

        return True, ""

    def _get_fen(self) -> str:
        """Export board to FEN string."""
        rows = []
        for rank in range(7, -1, -1):
            row = ""
            empty = 0
            for file in range(8):
                index = rank * 8 + file
                sq = self.board[index]
                if sq:
                    if empty > 0:
                        row += str(empty)
                        empty = 0
                    piece_chars = {
                        "pawn": "p",
                        "knight": "n",
                        "bishop": "b",
                        "rook": "r",
                        "queen": "q",
                        "king": "k",
                    }
                    char = piece_chars.get(sq["piece"], "?")
                    if sq["color"] == "white":
                        char = char.upper()
                    row += char
                else:
                    empty += 1
            if empty > 0:
                row += str(empty)
            rows.append(row)

        board_str = "/".join(rows)
        active = "w" if self.current_color == "white" else "b"

        castling = ""
        if self.castle_white_kingside:
            castling += "K"
        if self.castle_white_queenside:
            castling += "Q"
        if self.castle_black_kingside:
            castling += "k"
        if self.castle_black_queenside:
            castling += "q"
        if not castling:
            castling = "-"

        ep = index_to_notation(self.en_passant_target) if self.en_passant_target >= 0 else "-"
        halfmove = str(self.halfmove_clock)
        fullmove = str(len(self.move_history) // 2 + 1)

        return f"{board_str} {active} {castling} {ep} {halfmove} {fullmove}"

    # ==========================================================================
    # Undo support
    # ==========================================================================

    def _undo_last_move(self) -> bool:
        """Undo the last move. Returns True if successful."""
        if not self.move_history:
            return False

        # We need at least the move data plus the previous board state.
        # For simplicity, we reload from move history by replaying from start.
        # This is safe since chess games are short enough.
        moves = self.move_history[:-1]  # All moves except last
        last = self.move_history[-1]

        # Reset board
        self._init_board()

        # Replay all moves except the last
        for move in moves:
            self.execute_move_silent(move["from"], move["to"])
            self.move_history.append(move)

        # Pop the position hash for the undone move
        if self.position_history:
            self.position_history.pop()

        return True

    # ==========================================================================
    # Actions
    # ==========================================================================

    def _action_square_click(self, player: Player, action_id: str) -> None:
        """Handle square click (two-click move system).

        Bots use combined format: square_{from}_{to} for direct moves.
        Humans use two clicks: square_{index} twice.
        """
        if not isinstance(player, ChessPlayer):
            return
        if self.game_over or self.promotion_pending:
            return
        if player.color != self.current_color:
            return

        parts = action_id.split("_")
        # Bot combined move: square_{from}_{to}
        if len(parts) == 3:
            try:
                from_sq = int(parts[1])
                to_sq = int(parts[2])
            except ValueError:
                return
            legal, _ = self._is_legal_move(from_sq, to_sq, player.color)
            if legal:
                self._execute_move_full(player, from_sq, to_sq)
            return

        try:
            sq_index = int(parts[1])
        except (ValueError, IndexError):
            return

        player_id = player.id
        selected = self.selected_square.get(player_id)
        locale = self._player_locale(player)

        if selected is None:
            # First click: select a piece
            piece = self.board[sq_index]
            if piece and piece["color"] == player.color:
                self.selected_square[player_id] = sq_index
                self.play_sound("game_chess/pickup.ogg")
                user = self.get_user(player)
                if user:
                    notation = index_to_notation(sq_index)
                    p_name = piece_name(piece["piece"], locale)
                    color_name = piece_color_name(piece["piece"], piece["color"], locale)
                    user.speak_l(
                        "chess-you-select", piece=f"{color_name} {p_name}", square=notation
                    )
                self.update_player_menu(player)
            else:
                user = self.get_user(player)
                if user:
                    user.speak_l("chess-no-piece")
        else:
            # Second click: move
            self.selected_square[player_id] = None

            if selected == sq_index:
                self.play_sound("game_chess/setdown.ogg")
                user = self.get_user(player)
                if user:
                    user.speak_l("chess-move-cancelled")
                self.update_player_menu(player)
                return

            legal, error_msg = self._is_legal_move(selected, sq_index, player.color)
            if legal:
                self._execute_move_full(player, selected, sq_index)
            else:
                self.play_sound("game_chess/setdown.ogg")
                user = self.get_user(player)
                if user:
                    user.speak_l("chess-illegal-move")
                self.update_player_menu(player)

    def _action_promote(self, player: Player, action_id: str) -> None:
        """Handle pawn promotion choice."""
        if not isinstance(player, ChessPlayer):
            return
        if not self.promotion_pending:
            return
        if player.color != self.current_color:
            return

        piece_type = action_id.replace("promote_", "")
        if piece_type not in ("queen", "rook", "bishop", "knight"):
            return

        sq = self.promotion_square
        if sq < 0 or not self.board[sq]:
            return

        self.board[sq] = {"piece": piece_type, "color": player.color, "has_moved": True}
        self.promotion_pending = False
        self.promotion_square = -1

        notation = index_to_notation(sq)
        self.play_sound("game_chess/promote.ogg")
        self._broadcast_move(
            player,
            "chess-you-promote",
            "chess-player-promotes",
            pieces={"piece": piece_type},
            square=notation,
        )

        self._post_move_checks(player)

    def _action_type_move(self, player: Player, input_value: str, action_id: str) -> None:
        """Execute a move typed by the player in text notation."""
        if not isinstance(player, ChessPlayer):
            return
        user = self.get_user(player)
        text = input_value.strip() if input_value else ""
        if not text:
            return
        from_sq, to_sq, promotion = self._parse_move_text(text, player.color)
        if from_sq is None or to_sq is None:
            if user:
                user.speak_l("chess-move-parse-error")
            return
        legal, _ = self._is_legal_move(from_sq, to_sq, player.color)
        if not legal:
            if user:
                user.speak_l("chess-illegal-move")
            return
        self._execute_move_full(player, from_sq, to_sq)
        if promotion and self.promotion_pending and player.color == self.current_color:
            self._action_promote(player, f"promote_{promotion}")

    def _parse_move_text(self, text: str, color: str) -> tuple[int | None, int | None, str]:
        """Parse typed move text into (from_sq, to_sq, promotion_piece).

        Accepted formats:
          - o-o / O-O / 0-0            kingside castle
          - o-o-o / O-O-O / 0-0-0      queenside castle
          - e2-e4  or  e2e4            coordinate move (hyphen optional)
          - pe2-e4 / Pe2-E4            piece-prefixed coordinate move (prefix ignored)
          - e2xe4                      capture notation (x treated like -)
          - e7-e8=q                    promotion, piece appended after =
          - e1-g1 / e1-h1             remapped to kingside castle for white (king must be on e1)
          - e1-c1 / e1-a1             remapped to queenside castle for white (king must be on e1)
          - e8-g8 / e8-h8             remapped to kingside castle for black (king must be on e8)
          - e8-c8 / e8-a8             remapped to queenside castle for black (king must be on e8)

        Returns (None, None, "") on parse failure.
        """
        s = text.strip().lower().rstrip("+#!")

        rank = 0 if color == "white" else 7

        # Castling symbolic notation
        if s in ("o-o-o", "0-0-0"):
            king_sq = rank * 8 + 4
            return king_sq, rank * 8 + 2, ""
        if s in ("o-o", "0-0"):
            king_sq = rank * 8 + 4
            return king_sq, rank * 8 + 6, ""

        # Strip optional piece prefix (p n b r q k).
        # Special case: "b" is ambiguous — strip it as a bishop prefix only when
        # the next character is a file letter (a-h), e.g. "bc1-e3". If the next
        # character is a digit it is the b-file coordinate, e.g. "b1-c3".
        if s and s[0] in "pnrqk":
            s = s[1:]
        elif len(s) >= 2 and s[0] == "b" and s[1] in "abcdefgh":
            s = s[1:]

        # Promotion suffix:  ...=q
        promotion = ""
        if "=" in s:
            s, promo_str = s.split("=", 1)
            piece_map = {"q": "queen", "r": "rook", "b": "bishop", "n": "knight"}
            promotion = piece_map.get(promo_str.strip()[:1], "")

        # Normalise separator: allow hyphen, x, or nothing
        # Expect exactly 4 chars after normalisation: e2e4
        s = s.replace("-", "").replace("x", "")

        if len(s) != 4:
            return None, None, ""

        from_str = s[0:2]
        to_str = s[2:4]

        from_sq = notation_to_index(from_str)
        to_sq = notation_to_index(to_str)

        if from_sq is None or to_sq is None:
            return None, None, ""

        # Remap castling shorthands where the player typed the rook square
        # instead of the king's destination.  Only applies when the king is
        # actually on e1/e8 — if it has moved, treat it as a normal move.
        # Accepted: e1/e8 -> g (kingside dest), h (kingside rook sq),
        #           e1/e8 -> c (queenside dest), a (queenside rook sq).
        # NOT remapped: d-file, so e1-d1 / e1-d2 work as plain king moves.
        king_file = 4  # e-file
        if from_sq % 8 == king_file and from_sq // 8 == rank:
            piece_on_sq = self.board[from_sq]
            if piece_on_sq and piece_on_sq["piece"] == "king" and piece_on_sq["color"] == color:
                to_file = to_sq % 8
                if to_file == 7:  # h-file -> kingside (g-file)
                    to_sq = rank * 8 + 6
                elif to_file == 0:  # a-file -> queenside (c-file)
                    to_sq = rank * 8 + 2

        return from_sq, to_sq, promotion

    def _is_type_move_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, ChessPlayer):
            return "action-not-available"
        if player.color != self.current_color:
            return "action-not-your-turn"
        if self.game_over or self.promotion_pending:
            return "action-not-available"
        return None

    def _action_offer_draw(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ChessPlayer):
            return
        if self.game_over:
            return
        if self.draw_offer_from:
            user = self.get_user(player)
            if user:
                user.speak_l("chess-already-offered")
            return

        self.draw_offer_from = player.id
        self.broadcast_personal_l(player, "chess-you-offer-draw", "chess-player-offers-draw")
        self.rebuild_all_menus()

    def _action_accept_draw(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ChessPlayer):
            return
        if not self.draw_offer_from or self.draw_offer_from == player.id:
            user = self.get_user(player)
            if user:
                user.speak_l("chess-no-draw-offer")
            return

        self.game_over = True
        self.draw_reason = "agreement"
        self.play_sound("game_chess/draw.ogg")
        self.broadcast_personal_l(player, "chess-you-accept-draw", "chess-player-accepts-draw")
        self.broadcast_l("chess-draw-agreement")
        self._end_game_draw()

    def _action_decline_draw(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ChessPlayer):
            return
        if not self.draw_offer_from or self.draw_offer_from == player.id:
            return

        self.draw_offer_from = ""
        self.broadcast_personal_l(player, "chess-you-decline-draw", "chess-player-declines-draw")
        self.rebuild_all_menus()

    def _action_request_undo(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ChessPlayer):
            return
        if self.game_over:
            return
        if not self.move_history:
            user = self.get_user(player)
            if user:
                user.speak_l("chess-no-moves-to-undo")
            return
        if self.undo_request_from:
            user = self.get_user(player)
            if user:
                user.speak_l("chess-already-requested-undo")
            return

        self.undo_request_from = player.id
        self.broadcast_personal_l(player, "chess-you-request-undo", "chess-player-requests-undo")
        self.rebuild_all_menus()

    def _action_accept_undo(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ChessPlayer):
            return
        if not self.undo_request_from or self.undo_request_from == player.id:
            user = self.get_user(player)
            if user:
                user.speak_l("chess-no-undo-request")
            return

        requester = self.get_player_by_id(self.undo_request_from)
        self.undo_request_from = ""

        if self._undo_last_move():
            # Set turn to appropriate player
            current_color_player = self._get_player_by_color(self.current_color)
            if current_color_player:
                self.current_player = current_color_player
            self.broadcast_personal_l(player, "chess-you-accept-undo", "chess-player-accepts-undo")
            self.broadcast_l("chess-undo-applied", player=self.current_color)
            self._start_turn()
        self.rebuild_all_menus()

    def _action_decline_undo(self, player: Player, action_id: str) -> None:
        if not isinstance(player, ChessPlayer):
            return
        if not self.undo_request_from or self.undo_request_from == player.id:
            return

        self.undo_request_from = ""
        self.broadcast_personal_l(player, "chess-you-decline-undo", "chess-player-declines-undo")
        self.rebuild_all_menus()

    def _resign_confirm_options(self, player: Player) -> list[str]:
        locale = self._player_locale(player)
        return [
            Localization.get(locale, "chess-resign-yes"),
            Localization.get(locale, "chess-resign-no"),
        ]

    def _action_resign(self, player: Player, input_value: str, action_id: str) -> None:
        if not isinstance(player, ChessPlayer):
            return
        if self.game_over:
            return

        locale = self._player_locale(player)
        if input_value != Localization.get(locale, "chess-resign-yes"):
            return

        opponent_color = "black" if player.color == "white" else "white"
        opponent = self._get_player_by_color(opponent_color)
        opponent_name = opponent.name if opponent else "?"

        self.game_over = True
        self.winner_color = opponent_color
        self.play_sound("game_chess/resign.ogg")
        self.broadcast_personal_l(
            player, "chess-you-resign", "chess-player-resigns", opponent=opponent_name
        )
        if opponent:
            self._end_game(opponent)
        else:
            self._end_game_draw()

    def _action_view_board(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        locale = user.locale
        lines = []
        for rank in range(7, -1, -1):
            rank_pieces = []
            for file in range(8):
                index = rank * 8 + file
                sq = self.board[index]
                if sq:
                    rank_pieces.append(
                        f"{sq['color'][0]}{piece_name(sq['piece'], locale)[0].upper()}"
                    )
                else:
                    rank_pieces.append(Localization.get(locale, "chess-empty"))
            line = Localization.get(
                locale, "chess-board-rank", rank=rank + 1, pieces=", ".join(rank_pieces)
            )
            lines.append(line)
        self.status_box(player, lines)

    def _action_flip_board(self, player: Player, action_id: str) -> None:
        flipped = self.board_flipped.get(player.id, False)
        self.board_flipped[player.id] = not flipped
        user = self.get_user(player)
        if user:
            locale = user.locale
            # Non-flipped = white's perspective, flipped = black's perspective
            viewing_color = "black" if not flipped else "white"
            color_name = Localization.get(locale, f"color-{viewing_color}")
            is_own = isinstance(player, ChessPlayer) and player.color == viewing_color
            viewer_key = "chess-viewer-own" if is_own else "chess-viewer-opponent"
            viewer = Localization.get(locale, viewer_key)
            user.speak_l("chess-board-flipped", viewer=viewer, color=color_name)
        self.rebuild_player_menu(player)

    def _action_check_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        locale = user.locale
        white = self._get_player_by_color("white")
        black = self._get_player_by_color("black")
        lines = [
            Localization.get(locale, "chess-status-white", player=white.name if white else "?"),
            Localization.get(locale, "chess-status-black", player=black.name if black else "?"),
            Localization.get(locale, "chess-status-turn", color=self.current_color),
            Localization.get(locale, "chess-status-move-count", count=len(self.move_history)),
        ]
        self.status_box(player, lines)

    def _action_import_fen(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        current_fen = self._get_fen()
        user.show_editbox(
            "fen_input", Localization.get(user.locale, "chess-enter-fen"), current_fen
        )
        self._pending_actions[player.id] = "import_fen"

    def on_editbox_submit(self, player: Player, editbox_id: str, value: str) -> None:
        """Handle editbox submission."""
        if editbox_id == "fen_input":
            self._pending_actions.pop(player.id, None)
            user = self.get_user(player)
            if value and value.strip():
                success, error = self._load_fen(value.strip())
                if success:
                    if user:
                        user.speak_l("chess-fen-loaded")
                    # Set current player based on loaded color
                    cp = self._get_player_by_color(self.current_color)
                    if cp:
                        self.current_player = cp
                    self.rebuild_all_menus()
                else:
                    if user:
                        user.speak_l("chess-fen-error")

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("poker-timer-disabled")
        else:
            user.speak_l("poker-timer-remaining", seconds=remaining)

    # ==========================================================================
    # Action state helpers
    # ==========================================================================

    def _is_square_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not isinstance(player, ChessPlayer):
            return "action-not-available"
        if player.color != self.current_color:
            return "action-not-your-turn"
        if self.game_over:
            return "action-not-available"
        if self.promotion_pending:
            return "action-not-available"
        return None

    def _is_square_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if not isinstance(player, ChessPlayer):
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_square_label(self, player: Player, action_id: str) -> str:
        """Get label for a board square."""
        try:
            sq_index = int(action_id.split("_")[1])
        except (ValueError, IndexError):
            return ""

        notation = index_to_notation(sq_index)
        sq = self.board[sq_index]
        locale = self._player_locale(player)

        # Show selection indicator
        if isinstance(player, ChessPlayer):
            selected = self.selected_square.get(player.id)
            if selected == sq_index:
                if sq:
                    p_name = piece_name(sq["piece"], locale)
                    color_name = piece_color_name(sq["piece"], sq["color"], locale)
                    return f"[{notation}: {color_name} {p_name}]"

        if sq:
            p_name = piece_name(sq["piece"], locale)
            color_name = piece_color_name(sq["piece"], sq["color"], locale)
            return f"{notation}: {color_name} {p_name}"
        return notation

    def _is_promote_enabled(self, player: Player) -> str | None:
        if not self.promotion_pending:
            return "action-not-available"
        if not isinstance(player, ChessPlayer):
            return "action-not-available"
        if player.color != self.current_color:
            return "action-not-your-turn"
        return None

    def _is_promote_hidden(self, player: Player) -> Visibility:
        if not self.promotion_pending:
            return Visibility.HIDDEN
        if not isinstance(player, ChessPlayer):
            return Visibility.HIDDEN
        if player.color != self.current_color:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_offer_draw_enabled(self, player: Player) -> str | None:
        if self.status != "playing" or self.game_over:
            return "action-not-available"
        if not isinstance(player, ChessPlayer):
            return "action-not-available"
        if self.draw_offer_from:
            return "action-not-available"
        return None

    def _is_offer_draw_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.game_over:
            return Visibility.HIDDEN
        if not isinstance(player, ChessPlayer) or player.is_spectator:
            return Visibility.HIDDEN
        if self.promotion_pending or self.draw_offer_from:
            return Visibility.HIDDEN
        return Visibility.HIDDEN  # Actions menu only

    def _is_draw_response_enabled(self, player: Player) -> str | None:
        if not self.draw_offer_from:
            return "action-not-available"
        if not isinstance(player, ChessPlayer):
            return "action-not-available"
        if self.draw_offer_from == player.id:
            return "action-not-available"
        return None

    def _is_draw_response_hidden(self, player: Player) -> Visibility:
        if not self.draw_offer_from:
            return Visibility.HIDDEN
        if not isinstance(player, ChessPlayer):
            return Visibility.HIDDEN
        if self.draw_offer_from == player.id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_request_undo_enabled(self, player: Player) -> str | None:
        if self.status != "playing" or self.game_over:
            return "action-not-available"
        if not isinstance(player, ChessPlayer):
            return "action-not-available"
        if not self.move_history:
            return "action-not-available"
        if self.undo_request_from:
            return "action-not-available"
        return None

    def _is_request_undo_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.game_over:
            return Visibility.HIDDEN
        if not isinstance(player, ChessPlayer) or player.is_spectator:
            return Visibility.HIDDEN
        if self.promotion_pending or self.undo_request_from:
            return Visibility.HIDDEN
        return Visibility.HIDDEN  # Actions menu only

    def _is_undo_response_enabled(self, player: Player) -> str | None:
        if not self.undo_request_from:
            return "action-not-available"
        if not isinstance(player, ChessPlayer):
            return "action-not-available"
        if self.undo_request_from == player.id:
            return "action-not-available"
        return None

    def _is_undo_response_hidden(self, player: Player) -> Visibility:
        if not self.undo_request_from:
            return Visibility.HIDDEN
        if not isinstance(player, ChessPlayer):
            return Visibility.HIDDEN
        if self.undo_request_from == player.id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_resign_enabled(self, player: Player) -> str | None:
        if self.status != "playing" or self.game_over:
            return "action-not-available"
        if not isinstance(player, ChessPlayer):
            return "action-not-available"
        return None

    def _is_resign_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.game_over:
            return Visibility.HIDDEN
        if not isinstance(player, ChessPlayer) or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.HIDDEN  # Actions menu only

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status == "waiting":
            return "action-not-playing"
        return None

    def _is_always_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        return "action-no-scores"

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        return "action-no-scores"

    # ==========================================================================
    # Game end
    # ==========================================================================

    def _end_game(self, winner: ChessPlayer) -> None:
        """End the game with a winner."""
        self._winner_id = winner.id
        self.timer.clear()
        self.finish_game()

    def _end_game_draw(self) -> None:
        """End the game as a draw."""
        self._winner_id = ""
        self.timer.clear()
        self.finish_game()

    def build_game_result(self) -> GameResult:
        from datetime import datetime

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot,
                    is_virtual_bot=p.is_virtual_bot,
                )
                for p in self.players
                if isinstance(p, ChessPlayer) and not p.is_spectator
            ],
            custom_data={
                "total_moves": len(self.move_history),
                "winner_color": self.winner_color,
                "winner_id": getattr(self, "_winner_id", ""),
                "draw_reason": self.draw_reason,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = []
        winner_color = result.custom_data.get("winner_color", "")
        draw_reason = result.custom_data.get("draw_reason", "")
        total_moves = result.custom_data.get("total_moves", 0)

        draw_keys = {
            "stalemate": "chess-stalemate",
            "fifty_move_rule": "chess-draw-fifty",
            "threefold_repetition": "chess-draw-repetition",
            "insufficient_material": "chess-draw-material",
            "agreement": "chess-draw-agreement",
        }

        if winner_color:
            winner_name = ""
            for p in result.player_results:
                player = self.get_player_by_id(p.player_id)
                if isinstance(player, ChessPlayer) and player.color == winner_color:
                    winner_name = p.player_name
                    break
            lines.append(Localization.get(locale, "chess-checkmate", winner=winner_name))
        elif draw_reason:
            key = draw_keys.get(draw_reason, "chess-stalemate")
            lines.append(Localization.get(locale, key))

        lines.append(Localization.get(locale, "chess-status-move-count", count=total_moves))
        return lines

    # ==========================================================================
    # Helpers
    # ==========================================================================

    def _get_player_by_color(self, color: str) -> ChessPlayer | None:
        for p in self.players:
            if isinstance(p, ChessPlayer) and p.color == color:
                return p
        return None

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _broadcast_move(
        self,
        player: Player,
        personal_msg: str,
        others_msg: str,
        pieces: dict[str, str] | None = None,
        **kwargs,
    ) -> None:
        """Like broadcast_personal_l but resolves piece names per-user locale.

        Args:
            player: The acting player.
            personal_msg: Message ID for the acting player.
            others_msg: Message ID for everyone else.
            pieces: Mapping of kwarg name to raw piece type (e.g. {"piece": "pawn"}).
                    Each value is resolved via piece_name() per recipient locale.
            **kwargs: Other arguments passed through unchanged.
        """
        pieces = pieces or {}
        for p in self.players:
            u = self.get_user(p)
            if not u:
                continue
            locale = u.locale
            resolved = {k: piece_name(v, locale) for k, v in pieces.items()}
            resolved.update(kwargs)
            if p is player:
                u.speak_l(personal_msg, **resolved)
            else:
                u.speak_l(others_msg, player=player.name, **resolved)
