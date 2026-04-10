"""Ludo game implementation for PlayPalace v11."""

from dataclasses import dataclass, field
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import GameOptions, IntOption, option_field, BoolOption
from ...game_utils.teams import TeamResultBuilder
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState
from .bot import bot_think


@dataclass
class LudoToken:
    """Token state for Ludo."""

    state: str  # yard | track | home_column | finished
    position: int
    token_number: int


@dataclass
class LudoPlayer(Player):
    """Player state for Ludo."""

    color: str | None = None
    tokens: list[LudoToken] = field(default_factory=list)
    finished_count: int = 0
    move_options: dict[int, str] = field(default_factory=dict)


@dataclass
class LudoOptions(GameOptions):
    """Options for Ludo."""

    max_consecutive_sixes: int = option_field(
        IntOption(
            default=3,
            min_val=0,
            max_val=5,
            value_key="max_consecutive_sixes",
            label="ludo-set-max-sixes",
            prompt="ludo-enter-max-sixes",
            change_msg="ludo-option-changed-max-sixes",
            description="ludo-desc-max-sixes",
        )
    )
    safe_start_squares: bool = option_field(
        BoolOption(
            default=True,
            value_key="safe_start_squares",
            label="ludo-set-safe-start-squares",
            change_msg="ludo-option-changed-safe-start-squares",
            description="ludo-desc-safe-start-squares",
        )
    )


@dataclass
@register_game
class LudoGame(Game):
    """Classic Ludo: race four tokens around the board and into home."""

    players: list[LudoPlayer] = field(default_factory=list)
    options: LudoOptions = field(default_factory=LudoOptions)

    player_colors: list[str] = field(default_factory=lambda: ["Red", "Blue", "Green", "Yellow"])

    last_roll: int = 0
    consecutive_sixes: int = 0
    extra_turn: bool = False
    turn_start_state: dict[str, dict] | None = None

    track_length: int = 52
    home_column_length: int = 6
    safe_squares: list[int] = field(default_factory=lambda: [9, 22, 35, 48])

    @classmethod
    def get_name(cls) -> str:
        return "Ludo"

    @classmethod
    def get_type(cls) -> str:
        return "ludo"

    @classmethod
    def get_category(cls) -> str:
        return "category-board-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> LudoPlayer:
        """Create a new player."""
        return LudoPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Action sets
    # ==========================================================================

    def create_turn_action_set(self, player: LudoPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        action_set.add(
            Action(
                id="roll_dice",
                label=Localization.get(locale, "ludo-roll-die"),
                handler="_action_roll_dice",
                is_enabled="_is_roll_dice_enabled",
                is_hidden="_is_roll_dice_hidden",
            )
        )
        for token_number in range(1, 5):
            action_set.add(
                Action(
                    id=f"move_token_{token_number}",
                    label=Localization.get(locale, "ludo-move-token"),
                    handler="_action_move_token",
                    is_enabled=f"_is_move_token_{token_number}_enabled",
                    is_hidden=f"_is_move_token_{token_number}_hidden",
                    get_label="_get_move_token_label",
                )
            )
        return action_set

    def setup_keybinds(self) -> None:
        """Define keybinds for Ludo."""
        super().setup_keybinds()

        self.define_keybind(
            "r",
            "Roll die",
            ["roll_dice"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "v",
            "View board status",
            ["check_board"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        for token_number in range(1, 5):
            self.define_keybind(
                str(token_number),
                f"Move token {token_number}",
                [f"move_token_{token_number}"],
                state=KeybindState.ACTIVE,
            )

    def create_standard_action_set(self, player: LudoPlayer) -> ActionSet:
        """Create the standard action set with Ludo actions."""
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action = Action(
            id="check_board",
            label=Localization.get(locale, "ludo-check-board"),
            handler="_action_check_board",
            is_enabled="_is_check_board_enabled",
            is_hidden="_is_check_board_hidden",
        )
        action_set.add(action)
        if action.id in action_set._order:
            action_set._order.remove(action.id)
        action_set._order.insert(0, action.id)
        return action_set

    # ==========================================================================
    # Game lifecycle
    # ==========================================================================

    def on_start(self) -> None:
        """Start the game."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.last_roll = 0

        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Set up TeamManager for finished-count scores
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])
        self._team_manager.reset_all_scores()

        # Assign colors and initialize tokens
        for i, player in enumerate(active_players):
            player.color = self.player_colors[i]
            player.tokens = [
                LudoToken(state="yard", position=0, token_number=j + 1) for j in range(4)
            ]
            player.finished_count = 0
            player.move_options = {}

        # Play music
        self.play_music("game_pig/mus.ogg")

        self._start_turn(new_turn=True)

    def on_tick(self) -> None:
        """Run per-tick logic (bots)."""
        super().on_tick()
        if not self.game_active:
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        """Bot logic."""
        return bot_think(self, player)  # type: ignore[arg-type]

    # ==========================================================================
    # Helpers
    # ==========================================================================

    def _start_turn(self, new_turn: bool) -> None:
        """Start a player's turn."""
        player = self.current_player
        if isinstance(player, LudoPlayer):
            player.move_options = {}
        if new_turn:
            self.consecutive_sixes = 0
            self.turn_start_state = self._save_turn_state()
        self.extra_turn = False
        if player and player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 40))  # nosec B311
        self.announce_turn()
        self.rebuild_all_menus()

    def _end_turn(self) -> None:
        """End turn or grant extra turn."""
        if self.extra_turn:
            self._start_turn(new_turn=False)
            return
        self.turn_start_state = None
        self.advance_turn(announce=False)
        self._start_turn(new_turn=True)

    def _save_turn_state(self) -> dict[str, dict]:
        """Deep copy player token states for rollback."""
        state: dict[str, dict] = {}
        for player in self.players:
            state[player.id] = {
                "finished_count": player.finished_count,
                "tokens": [
                    {
                        "state": t.state,
                        "position": t.position,
                        "token_number": t.token_number,
                    }
                    for t in player.tokens
                ],
            }
        return state

    def _restore_turn_state(self, state: dict[str, dict]) -> None:
        """Restore player token states from rollback."""
        for player in self.players:
            saved = state.get(player.id)
            if not saved:
                continue
            player.finished_count = saved["finished_count"]
            for i, saved_token in enumerate(saved["tokens"]):
                token = player.tokens[i]
                token.state = saved_token["state"]
                token.position = saved_token["position"]
                token.token_number = saved_token["token_number"]
        self._sync_team_scores()

    def _sync_team_scores(self) -> None:
        """Sync TeamManager scores from finished counts."""
        self._team_manager.reset_all_scores()
        for player in self.players:
            if isinstance(player, LudoPlayer):
                self._team_manager.add_to_team_score(player.name, player.finished_count)

    def _get_start_position(self, player: LudoPlayer) -> int:
        color_starts = {"Red": 1, "Blue": 14, "Green": 27, "Yellow": 40}
        return color_starts[player.color]

    def _get_home_entry_position(self, player: LudoPlayer) -> int:
        color_entries = {"Red": 51, "Blue": 12, "Green": 25, "Yellow": 38}
        return color_entries[player.color]

    def _is_safe_square(self, position: int, player: LudoPlayer) -> bool:
        if position in self.safe_squares:
            return True
        if self.options.safe_start_squares and position == self._get_start_position(player):
            return True
        return False

    def _get_token_at_position(
        self, position: int, exclude_player: LudoPlayer
    ) -> tuple[LudoToken | None, LudoPlayer | None]:
        for player in self.players:
            if player == exclude_player:
                continue
            for token in player.tokens:
                if token.state == "track" and token.position == position:
                    return token, player
        return None, None

    def _check_capture(self, player: LudoPlayer, token: LudoToken) -> None:
        if token.state != "track":
            return
        if self._is_safe_square(token.position, player):
            return
        captured_token, captured_player = self._get_token_at_position(token.position, player)
        if captured_token and captured_player:
            captured_token.state = "yard"
            captured_token.position = 0
            self.broadcast_l(
                "ludo-captures",
                player=player.name,
                color=player.color,
                captured_player=captured_player.name,
                captured_color=captured_player.color,
                token=captured_token.token_number,
            )
            self.play_sound("game_pig/lose.ogg")

    def _can_token_move(self, token: LudoToken, roll: int) -> bool:
        if token.state == "finished":
            return False
        if token.state == "yard":
            return roll == 6
        if token.state == "track":
            return True
        if token.state == "home_column":
            return token.position + roll <= self.home_column_length
        return False

    def _get_moveable_tokens(self, player: LudoPlayer, roll: int) -> list[tuple[int, LudoToken]]:
        moveable = []
        for i, token in enumerate(player.tokens):
            if self._can_token_move(token, roll):
                moveable.append((i, token))
        return moveable

    def _describe_token(self, token: LudoToken, locale: str) -> str:
        if token.state == "yard":
            return Localization.get(locale, "ludo-token-yard", token=token.token_number)
        if token.state == "track":
            return Localization.get(
                locale,
                "ludo-token-track",
                token=token.token_number,
                position=token.position,
            )
        if token.state == "home_column":
            return Localization.get(
                locale,
                "ludo-token-home",
                token=token.token_number,
                position=token.position,
                total=self.home_column_length,
            )
        return Localization.get(locale, "ludo-token-finished", token=token.token_number)

    # ==========================================================================
    # Actions
    # ==========================================================================

    def _is_roll_dice_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        ludo_player: LudoPlayer = player  # type: ignore
        if ludo_player.move_options:
            return "action-not-available"
        return None

    def _is_roll_dice_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        ludo_player: LudoPlayer = player  # type: ignore
        if ludo_player.move_options:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_token_enabled(self, player: Player, token_index: int) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        ludo_player: LudoPlayer = player  # type: ignore
        if token_index not in ludo_player.move_options:
            return "action-not-available"
        return None

    def _is_move_token_1_enabled(self, player: Player) -> str | None:
        return self._is_move_token_enabled(player, 0)

    def _is_move_token_2_enabled(self, player: Player) -> str | None:
        return self._is_move_token_enabled(player, 1)

    def _is_move_token_3_enabled(self, player: Player) -> str | None:
        return self._is_move_token_enabled(player, 2)

    def _is_move_token_4_enabled(self, player: Player) -> str | None:
        return self._is_move_token_enabled(player, 3)

    def _is_check_board_enabled(self, player: Player) -> str | None:
        return None

    def _is_check_board_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_move_token_hidden(self, player: Player, token_index: int) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        ludo_player: LudoPlayer = player  # type: ignore
        if token_index not in ludo_player.move_options:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_token_1_hidden(self, player: Player) -> Visibility:
        return self._is_move_token_hidden(player, 0)

    def _is_move_token_2_hidden(self, player: Player) -> Visibility:
        return self._is_move_token_hidden(player, 1)

    def _is_move_token_3_hidden(self, player: Player) -> Visibility:
        return self._is_move_token_hidden(player, 2)

    def _is_move_token_4_hidden(self, player: Player) -> Visibility:
        return self._is_move_token_hidden(player, 3)

    def _get_move_token_label(self, player: Player, action_id: str) -> str:
        ludo_player: LudoPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        token_index = self._token_index_from_action(action_id)
        if token_index is None:
            return Localization.get(locale, "ludo-move-token")
        label = ludo_player.move_options.get(token_index)
        if label:
            return label
        return Localization.get(locale, "ludo-move-token")

    def _action_roll_dice(self, player: Player, action_id: str) -> None:
        ludo_player: LudoPlayer = player  # type: ignore

        self.last_roll = random.randint(1, 6)  # nosec B311
        self.play_sound("game_pig/roll.ogg")
        self.broadcast_personal_l(
            player,
            "ludo-you-roll",
            "ludo-roll",
            roll=self.last_roll,
        )

        moveable = self._get_moveable_tokens(ludo_player, self.last_roll)
        if not moveable:
            self.broadcast_personal_l(
                player,
                "ludo-you-no-moves",
                "ludo-no-moves",
            )
            self._end_turn()
            return

        if len(moveable) == 1:
            self._move_token(ludo_player, moveable[0][1], self.last_roll)
            self._after_move(ludo_player)
            return

        user = self.get_user(ludo_player)
        locale = user.locale if user else "en"
        ludo_player.move_options = {
            idx: self._describe_token(token, locale) for idx, token in moveable
        }
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 40))  # nosec B311
        self.update_all_menus()
        return

    def _action_move_token(self, player: Player, action_id: str) -> None:
        ludo_player: LudoPlayer = player  # type: ignore
        token_index = self._token_index_from_action(action_id)
        if token_index is None or token_index not in ludo_player.move_options:
            return
        ludo_player.move_options = {}
        token = ludo_player.tokens[token_index]
        self._move_token(ludo_player, token, self.last_roll)
        self._after_move(ludo_player)

    def _token_index_from_action(self, action_id: str) -> int | None:
        if action_id.startswith("move_token_"):
            try:
                token_number = int(action_id.split("_")[-1])
            except ValueError:
                return None
            if 1 <= token_number <= 4:
                return token_number - 1
        return None

    def _action_check_board(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        locale = user.locale

        lines: list[str] = []
        for p in self.players:
            if not isinstance(p, LudoPlayer):
                continue
            lines.append(
                Localization.get(
                    locale,
                    "ludo-board-player",
                    player=p.name,
                    color=p.color,
                    finished=p.finished_count,
                )
            )
            for token in p.tokens:
                lines.append(self._describe_token(token, locale))
        if self.last_roll > 0:
            lines.append(Localization.get(locale, "ludo-last-roll", roll=self.last_roll))

        self.status_box(player, lines)

    def format_end_screen(self, result, locale: str) -> list[str]:
        """Format end screen with finished token counts."""
        lines = [Localization.get(locale, "game-final-scores")]
        if not self._team_manager:
            return lines
        for index, team in enumerate(
            self._team_manager.get_sorted_teams(by_score=True, descending=True), 1
        ):
            name = self._team_manager.get_team_name(team, locale)
            points = Localization.get(locale, "game-points", count=team.total_score)
            lines.append(f"{index}. {name}: {points}")
        return lines

    def build_game_result(self) -> GameResult:
        """Build game result with winner information."""
        from datetime import datetime

        sorted_teams, winner, final_scores = TeamResultBuilder.summarize(self._team_manager)

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
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": self._team_manager.get_team_name(winner) if winner else None,
                "final_scores": final_scores,
            },
        )

    # ==========================================================================
    # Movement / resolution
    # ==========================================================================

    def _move_token(self, player: LudoPlayer, token: LudoToken, spaces: int) -> None:
        user = self.get_user(player)
        locale = user.locale if user else "en"

        if token.state == "yard":
            token.state = "track"
            token.position = self._get_start_position(player)
            self.broadcast_l(
                "ludo-enter-board",
                player=player.name,
                color=player.color,
                token=token.token_number,
            )
            self.play_sound("game_dominos/play.ogg")
            self._check_capture(player, token)
            return

        if token.state == "track":
            home_entry = self._get_home_entry_position(player)
            new_pos = token.position + spaces
            if token.position <= home_entry and new_pos > home_entry:
                overshoot = new_pos - home_entry
                if overshoot >= self.home_column_length:
                    token.state = "finished"
                    token.position = self.home_column_length
                    player.finished_count += 1
                    self._team_manager.add_to_team_score(player.name, 1)
                    self.broadcast_l(
                        "ludo-home-finish",
                        player=player.name,
                        color=player.color,
                        token=token.token_number,
                        finished=player.finished_count,
                    )
                    self.play_sound("game_pig/win.ogg")
                else:
                    token.state = "home_column"
                    token.position = overshoot
                    self.broadcast_l(
                        "ludo-enter-home",
                        player=player.name,
                        color=player.color,
                        token=token.token_number,
                    )
                    self.play_sound("game_dominos/draw.ogg")
                return

            token.position = ((new_pos - 1) % self.track_length) + 1
            self.broadcast_l(
                "ludo-move-track",
                player=player.name,
                color=player.color,
                token=token.token_number,
                position=token.position,
            )
            self.play_sound("game_dominos/play.ogg")
            self._check_capture(player, token)
            return

        if token.state == "home_column":
            token.position += spaces
            if token.position >= self.home_column_length:
                token.state = "finished"
                token.position = self.home_column_length
                player.finished_count += 1
                self._team_manager.add_to_team_score(player.name, 1)
                self.broadcast_l(
                    "ludo-home-finish",
                    player=player.name,
                    color=player.color,
                    token=token.token_number,
                    finished=player.finished_count,
                )
                self.play_sound("game_pig/win.ogg")
            else:
                self.broadcast_l(
                    "ludo-move-home",
                    player=player.name,
                    color=player.color,
                    token=token.token_number,
                    position=token.position,
                    total=self.home_column_length,
                )
                self.play_sound("game_dominos/draw.ogg")

    def _after_move(self, player: LudoPlayer) -> None:
        if player.finished_count >= 4:
            self.play_sound("game_pig/win.ogg")
            self.broadcast_l("ludo-winner", player=player.name, color=player.color)
            self.finish_game()
            return

        if self.last_roll == 6:
            self.consecutive_sixes += 1
            max_sixes = self.options.max_consecutive_sixes
            if max_sixes > 0 and self.consecutive_sixes >= max_sixes:
                self.broadcast_l(
                    "ludo-too-many-sixes",
                    player=player.name,
                    count=self.consecutive_sixes,
                )
                if self.turn_start_state:
                    self._restore_turn_state(self.turn_start_state)
                    self.play_sound("game_pig/lose.ogg")
                self.consecutive_sixes = 0
                self._end_turn()
                return

            self.broadcast_personal_l(
                player,
                "ludo-you-extra-turn",
                "ludo-extra-turn",
            )
            self.extra_turn = True
            self._end_turn()
            return

        self._end_turn()
