"""
Left Right Center (LRC) Game Implementation for PlayPalace v11.

Players roll up to 3 dice (limited by chips they hold). Each die result
passes a chip left/right/center or keeps it. Center chips are removed
from play. Last player holding chips wins.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.action_guard_mixin import ActionGuardMixin
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState


DICE_FACES = ["left", "right", "center", "dot", "dot", "dot"]


@dataclass
class LeftRightCenterPlayer(Player):
    """Player state for Left Right Center."""

    chips: int = 0


@dataclass
class LeftRightCenterOptions(GameOptions):
    """Options for Left Right Center."""

    starting_chips: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=10,
            value_key="count",
            label="lrc-set-starting-chips",
            prompt="lrc-enter-starting-chips",
            change_msg="lrc-option-changed-starting-chips",
        )
    )


@dataclass
@register_game
class LeftRightCenterGame(ActionGuardMixin, Game):
    """Left Right Center dice game."""

    players: list[LeftRightCenterPlayer] = field(default_factory=list)
    options: LeftRightCenterOptions = field(default_factory=LeftRightCenterOptions)
    center_pot: int = 0
    turn_delay_ticks: int = 0

    def __post_init__(self):
        super().__post_init__()
        self._pending_turn_advance = False
        self._pending_roll = None
        self._roll_delay_ticks = 0

    @classmethod
    def get_name(cls) -> str:
        return "Left Right Center"

    @classmethod
    def get_type(cls) -> str:
        return "leftrightcenter"

    @classmethod
    def get_category(cls) -> str:
        return "category-dice-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 20

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> LeftRightCenterPlayer:
        return LeftRightCenterPlayer(id=player_id, name=name, is_bot=is_bot, chips=0)

    # ==========================================================================
    # Turn action availability
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        return self.guard_turn_action_enabled(player)

    def _is_roll_hidden(self, player: Player) -> Visibility:
        has_chips = not isinstance(player, LeftRightCenterPlayer) or player.chips > 0
        return self.turn_action_visibility(player, extra_condition=has_chips)

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: LeftRightCenterPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "lrc-roll", count=0),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                get_label="_get_roll_label",
            )
        )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("r", "Roll dice", ["roll"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "c",
            "Center pot",
            ["check_center"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action = Action(
            id="check_center",
            label=Localization.get(locale, "lrc-center-pot"),
            handler="_action_check_center",
            is_enabled="_is_check_center_enabled",
            is_hidden="_is_check_center_hidden",
        )
        action_set.add(action)
        if action.id in action_set._order:
            action_set._order.remove(action.id)
        action_set._order.insert(0, action.id)
        return action_set

    # ==========================================================================
    # Game flow
    # ==========================================================================

    def on_start(self) -> None:
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 0
        self.center_pot = 0
        self.turn_delay_ticks = 0
        self._pending_turn_advance = False
        self._pending_roll = None
        self._roll_delay_ticks = 0

        for player in self.players:
            player.chips = self.options.starting_chips

        # Set up individual team scores so the default scoreboard works
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in self.players])
        self._sync_team_scores()

        # Initialize turn order with all active players
        self.set_turn_players(self.get_active_players())
        self.play_music("game_pig/mus.ogg")
        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not player:
            return

        if self._check_for_winner():
            return

        self.announce_turn()
        if isinstance(player, LeftRightCenterPlayer) and player.chips == 0:
            self.broadcast_l("lrc-no-chips", player=player.name)
            self.end_turn()
            return
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(5, 10))  # nosec B311

        self.rebuild_all_menus()

    def _end_turn(self) -> None:
        if self._check_for_winner():
            return
        self.advance_turn(announce=False)
        self._start_turn()

    def _get_turn_order(self) -> list[LeftRightCenterPlayer]:
        return [p for p in self.players if not p.is_spectator]

    def _get_left_right(
        self, player: LeftRightCenterPlayer
    ) -> tuple[LeftRightCenterPlayer, LeftRightCenterPlayer]:
        order = self._get_turn_order()
        if not order:
            return (player, player)
        idx = order.index(player)
        left_player = order[(idx - 1) % len(order)]
        right_player = order[(idx + 1) % len(order)]
        return left_player, right_player

    def _broadcast_roll_results(self, player: LeftRightCenterPlayer, faces: list[str]) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            locale = user.locale
            localized_faces = [Localization.get(locale, f"lrc-face-{face}") for face in faces]
            results_text = Localization.format_list_and(locale, localized_faces)
            user.speak_l("lrc-roll-results", player=player.name, results=results_text)

    def _action_roll(self, player: Player, action_id: str) -> None:
        lrc_player: LeftRightCenterPlayer = player  # type: ignore

        roll_count = min(3, lrc_player.chips)

        if roll_count == 0:
            # No chips: skip roll output entirely and move on
            self.end_turn()
            return
        self.play_sound("game_pig/roll.ogg")

        faces = [random.choice(DICE_FACES) for _ in range(roll_count)]  # nosec B311
        self._broadcast_roll_results(lrc_player, faces)

        # Delay the chip movements slightly for pacing
        self._pending_roll = {
            "player_id": lrc_player.id,
            "faces": faces,
        }
        self._roll_delay_ticks = 10
        return

    def _resolve_pending_roll(self) -> None:
        if not self._pending_roll:
            return
        player = self.get_player_by_id(self._pending_roll["player_id"])
        if not player:
            self._pending_roll = None
            return
        lrc_player: LeftRightCenterPlayer = player  # type: ignore
        faces = list(self._pending_roll["faces"])
        self._pending_roll = None

        left_player, right_player = self._get_left_right(lrc_player)

        sound_delay = 0
        left_count = faces.count("left")
        right_count = faces.count("right")
        center_count = faces.count("center")

        if left_count:
            lrc_player.chips -= left_count
            left_player.chips += left_count
            self.broadcast_l(
                "lrc-pass-left",
                player=lrc_player.name,
                target=left_player.name,
                count=left_count,
            )
            for _ in range(left_count):
                self.schedule_sound(
                    "game_ninetynine/lose1_you.ogg", delay_ticks=sound_delay, pan=-50
                )
                sound_delay += 10

        if right_count:
            lrc_player.chips -= right_count
            right_player.chips += right_count
            self.broadcast_l(
                "lrc-pass-right",
                player=lrc_player.name,
                target=right_player.name,
                count=right_count,
            )
            for _ in range(right_count):
                self.schedule_sound(
                    "game_ninetynine/lose1_you.ogg", delay_ticks=sound_delay, pan=50
                )
                sound_delay += 10

        if center_count:
            lrc_player.chips -= center_count
            self.center_pot += center_count
            self.broadcast_l(
                "lrc-pass-center",
                player=lrc_player.name,
                count=center_count,
            )
            for _ in range(center_count):
                self.schedule_sound("game_ninetynine/lose1_other.ogg", delay_ticks=sound_delay)
                sound_delay += 10

        self._sync_team_scores()
        self.end_turn(delay_ticks=sound_delay)

    def _check_for_winner(self) -> bool:
        active = self.get_active_players()
        players_with_chips = [p for p in active if p.chips > 0]
        if len(players_with_chips) == 1:
            winner = players_with_chips[0]
            self.broadcast_l("lrc-winner", player=winner.name, count=winner.chips)
            self.play_sound("game_pig/win.ogg")
            self.finish_game()
            return True
        return False

    def on_tick(self) -> None:
        super().on_tick()
        if self._roll_delay_ticks > 0:
            self._roll_delay_ticks -= 1
            if self._roll_delay_ticks == 0:
                self._resolve_pending_roll()
            return
        if self.turn_delay_ticks > 0:
            self.turn_delay_ticks -= 1
            return
        if self._pending_turn_advance:
            self._pending_turn_advance = False
            self._end_turn()
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: LeftRightCenterPlayer) -> str | None:
        return "roll"

    def _is_check_center_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_center_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _action_check_center(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak_l("lrc-center-pot", count=self.center_pot)

    def end_turn(self, delay_ticks: int = 0) -> None:
        """End the current turn with optional delay for turn resolution."""
        current = self.current_player
        if current and current.is_bot:
            BotHelper.jolt_bot(current, ticks=random.randint(10, 15))  # nosec B311
        if delay_ticks > 0:
            self.turn_delay_ticks = delay_ticks
            self._pending_turn_advance = True
            return
        self._end_turn()

    def _sync_team_scores(self) -> None:
        """Mirror player chips into TeamManager totals for scoreboard output."""
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.players:
            team = self._team_manager.get_team(p.name)
            if team:
                team.total_score = p.chips

    def _get_roll_label(self, player: Player, action_id: str) -> str:
        lrc_player: LeftRightCenterPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        count = min(3, max(0, lrc_player.chips))
        return Localization.get(locale, "lrc-roll", count=count)

    # Use default announce_turn() (includes per-user turn sound preference)

    def build_game_result(self) -> GameResult:
        active_players = self.get_active_players()
        players_with_chips = [p for p in active_players if p.chips > 0]
        winner = players_with_chips[0] if len(players_with_chips) == 1 else None
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
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "center_pot": self.center_pot,
                "final_chips": {p.name: p.chips for p in active_players},
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores-header")]
        final_chips = result.custom_data.get("final_chips", {})
        for name, chips in final_chips.items():
            lines.append(f"{name}: {chips}")
        lines.append(
            Localization.get(
                locale, "lrc-center-pot", count=result.custom_data.get("center_pot", 0)
            )
        )
        return lines
