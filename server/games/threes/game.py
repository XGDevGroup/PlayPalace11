"""
Threes Game Implementation for PlayPalace v11.

Low-score dice game: Roll 5 dice, keep at least one each roll.
Threes = 0 points. Lowest score wins!
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.action_guard_mixin import ActionGuardMixin
from ...game_utils.round_based_game_mixin import RoundBasedGameMixin
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.dice import DiceSet
from ...game_utils.dice_game_mixin import DiceGameMixin
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field, GameOptions
from ...messages.localization import Localization
from server.core.ui.keybinds import KeybindState


@dataclass
class ThreesPlayer(Player):
    """Player state for Threes game."""

    dice: DiceSet = field(default_factory=lambda: DiceSet(num_dice=5, sides=6))
    turn_score: int = 0  # Score for current turn
    total_score: int = 0  # Total score across all rounds


@dataclass
class ThreesOptions(GameOptions):
    """Options for Threes game."""

    total_rounds: int = option_field(
        IntOption(
            default=10,
            min_val=1,
            max_val=20,
            value_key="rounds",
            label="threes-set-rounds",
            prompt="threes-enter-rounds",
            change_msg="threes-option-changed-rounds",
            description="threes-desc-rounds",
        )
    )


@dataclass
@register_game
class ThreesGame(ActionGuardMixin, RoundBasedGameMixin, Game, DiceGameMixin):
    """
    Threes dice game.

    Roll 5 dice, then keep at least one die each roll before rolling again.
    Kept dice become locked and can't be rerolled.
    Continue until all dice are locked or only 1 die remains.

    Scoring:
    - Threes = 0 points
    - All other dice = face value
    - Five sixes = "Shooting the moon" = -30 points

    Lowest score wins after all rounds.
    """

    relevant_preferences = ["dice_keeping_style"]

    players: list[ThreesPlayer] = field(default_factory=list)
    options: ThreesOptions = field(default_factory=ThreesOptions)

    round_start_sound = None

    @classmethod
    def get_name(cls) -> str:
        return "Threes"

    @classmethod
    def get_type(cls) -> str:
        return "threes"

    @classmethod
    def get_category(cls) -> str:
        return "category-dice-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> ThreesPlayer:
        """Create a new player with Threes-specific state."""
        return ThreesPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Declarative is_enabled / is_hidden / get_label for turn actions
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        """Check if roll action is enabled."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            # First roll is always allowed
            return None
        if threes_player.dice.unlocked_count <= 1:
            # Only 1 die left, can't roll (must bank)
            return "threes-must-bank"
        if threes_player.dice.all_decided:
            return "threes-must-bank"
        if threes_player.dice.kept_unlocked_count == 0:
            # Must keep at least one die
            return "threes-must-keep"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        """Roll is visible during play for current player."""
        threes_player: ThreesPlayer = player  # type: ignore
        return self.turn_action_visibility(
            player,
            extra_condition=not (threes_player.dice.has_rolled and threes_player.dice.all_decided),
        )

    def _is_bank_enabled(self, player: Player) -> str | None:
        """Check if bank action is enabled."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            return "threes-roll-first"
        if not threes_player.dice.all_decided:
            return "threes-keep-all-first"
        return None

    def _is_bank_hidden(self, player: Player) -> Visibility:
        """Bank is hidden until dice are rolled."""
        threes_player: ThreesPlayer = player  # type: ignore
        return self.turn_action_visibility(
            player,
            extra_condition=threes_player.dice.has_rolled,
        )

    def _is_check_hand_enabled(self, player: Player) -> str | None:
        """Check if check_hand action is enabled."""
        error = self.guard_game_active()
        if error:
            return error
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            return "threes-no-dice-yet"
        return None

    def _is_check_hand_hidden(self, player: Player) -> Visibility:
        """Check hand is always hidden (keybind only)."""
        return Visibility.HIDDEN

    # Override dice toggle methods from DiceGameMixin for Threes-specific logic
    def _is_dice_toggle_enabled(self, player: Player, die_index: int) -> str | None:
        """Check if toggling die at index is enabled in Threes."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        threes_player: ThreesPlayer = player  # type: ignore
        if not threes_player.dice.has_rolled:
            return "dice-not-rolled"
        if threes_player.dice.is_locked(die_index):
            return "dice-locked"
        if threes_player.dice.unlocked_count <= 1:
            # Only 1 unlocked die left - can't toggle
            return "threes-last-die"
        return None

    def _is_dice_toggle_hidden(self, player: Player, die_index: int) -> Visibility:
        """Check if die toggle action is hidden."""
        threes_player: ThreesPlayer = player  # type: ignore
        return self.turn_action_visibility(
            player,
            extra_condition=threes_player.dice.has_rolled,
        )

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: ThreesPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Dice keep/unkeep actions (1-5 keys) - from mixin
        self.add_dice_toggle_actions(action_set)

        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "threes-roll"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
            )
        )

        action_set.add(
            Action(
                id="bank",
                label=Localization.get(locale, "threes-bank"),
                handler="_action_bank",
                is_enabled="_is_bank_enabled",
                is_hidden="_is_bank_hidden",
            )
        )

        # Check hand action
        action_set.add(
            Action(
                id="check_hand",
                label=Localization.get(locale, "threes-check-hand"),
                handler="_action_check_hand",
                is_enabled="_is_check_hand_enabled",
                is_hidden="_is_check_hand_hidden",
            )
        )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Turn action keybinds - r/b like Pig
        self.define_keybind("r", "Roll dice", ["roll"], state=KeybindState.ACTIVE)
        self.define_keybind("b", "Bank and end turn", ["bank"], state=KeybindState.ACTIVE)

        # Dice toggle keybinds (1-5) - from DiceGameMixin
        self.setup_dice_keybinds()

        # Check hand
        self.define_keybind("h", "Check hand", ["check_hand"], state=KeybindState.ACTIVE)

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle rolling dice."""
        if not isinstance(player, ThreesPlayer):
            return

        # If not first roll, must keep at least one unlocked die
        if player.dice.has_rolled:
            if player.dice.kept_unlocked_count == 0:
                user = self.get_user(player)
                if user:
                    user.speak_l("threes-must-keep")
                return

        had_rolled = player.dice.has_rolled
        locked_before = set(player.dice.locked)
        kept_before = set(player.dice.kept)
        if had_rolled:
            rolled_indices = [
                i
                for i in range(player.dice.num_dice)
                if i not in locked_before and i not in kept_before
            ]
        else:
            rolled_indices = list(range(player.dice.num_dice))

        # Roll dice (locks kept dice and rerolls unlocked)
        self.play_sound("game_pig/roll.ogg")
        player.dice.roll()
        self._apply_dice_values_defaults(player)

        # Announce rerolled dice only (first roll announces all dice).
        dice_str = ", ".join(str(player.dice.values[i]) for i in rolled_indices)
        self.broadcast_personal_l(
            player, "threes-you-rolled", "threes-player-rolled", dice=dice_str
        )

        # Check if auto-score needed (all locked or only 1 unlocked)
        if player.dice.unlocked_count <= 1:
            self._score_turn(player)
            return

        # Give bot time to think about next action
        if player.is_bot:
            import random

            BotHelper.jolt_bot(player, ticks=random.randint(15, 30))  # nosec B311

        self.rebuild_all_menus()
        next_toggle = None
        for resolved in self.get_all_visible_actions(player):
            if resolved.action.id.startswith("toggle_die_"):
                next_toggle = resolved.action.id
                break
        if next_toggle:
            self.update_player_menu(player, selection_id=next_toggle)

    # Dice toggle handlers provided by DiceGameMixin

    def _action_bank(self, player: Player, action_id: str) -> None:
        """Bank score and end turn."""
        if not isinstance(player, ThreesPlayer):
            return
        self._score_turn(player)

    def _action_check_hand(self, player: Player, action_id: str) -> None:
        """Check current dice."""
        if not isinstance(player, ThreesPlayer):
            return

        user = self.get_user(player)
        if not user:
            return

        if not player.dice.has_rolled:
            user.speak_l("threes-no-dice-yet")
            return

        user.speak_l("threes-your-dice", dice=player.dice.format_all())

    def _score_turn(self, player: ThreesPlayer) -> None:
        """Calculate and apply turn score."""
        # Threes = 0 points, so sum all values excluding 3s
        score = player.dice.sum_values(exclude_value=3)
        six_count = player.dice.count_value(6)

        # Check for shooting the moon (5 sixes)
        if six_count == 5:
            score = -30
            self.play_sound("game_pig/win.ogg")
            self.broadcast_personal_l(player, "threes-you-shot-moon", "threes-shot-moon")
        else:
            self.play_sound("game_pig/bank.ogg")
            self.broadcast_personal_l(player, "threes-you-scored", "threes-scored", score=score)

        player.turn_score = score
        player.total_score += score
        self._team_manager.add_to_team_score(player.name, score)

        self._on_turn_end()

    # ==========================================================================
    # RoundBasedGameMixin hooks
    # ==========================================================================

    def should_reset_all_scores(self) -> bool:
        return True

    def _reset_player_for_game(self, player) -> None:
        if isinstance(player, ThreesPlayer):
            player.total_score = 0
            player.dice.reset()

    def _reset_player_for_turn(self, player) -> None:
        if isinstance(player, ThreesPlayer):
            player.dice.reset()
            player.turn_score = 0

    def _announce_turn_start(self, player) -> None:
        self.announce_turn(turn_sound="game_3cardpoker/turn.ogg")

    def _setup_bot_for_turn(self, player) -> None:
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))

    def _on_round_end(self) -> None:
        """End the current round."""
        # Announce round scores
        scores = [(p.name, p.total_score) for p in self.players if isinstance(p, ThreesPlayer)]
        scores.sort(key=lambda x: x[1])  # Sort by score (lowest first)
        scores_str = ", ".join(f"{name}: {score}" for name, score in scores)
        self.broadcast_l("threes-round-scores", round=self.round, scores=scores_str)

        # Check if game is over
        if self.round >= self.options.total_rounds:
            self._end_game()
        else:
            # Start next round
            self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1
        self.set_turn_players(self.get_active_players())
        self.broadcast_l(
            "threes-round-start",
            round=self.round,
            total=self.options.total_rounds,
        )
        self._start_turn()

    def _end_game(self) -> None:
        """End the game and announce winner."""
        # Only consider active (non-spectator) players when picking winners
        active_players = [
            p for p in self.players if isinstance(p, ThreesPlayer) and not p.is_spectator
        ]
        if not active_players:
            return

        # Find winner(s) (lowest score)
        players_with_scores = [(p, p.total_score) for p in active_players]
        players_with_scores.sort(key=lambda x: x[1])

        lowest_score = players_with_scores[0][1]
        winners = [p for p, s in players_with_scores if s == lowest_score]

        if len(winners) == 1:
            self.play_sound("game_pig/win.ogg")
            self.broadcast_l("threes-winner", player=winners[0].name, score=lowest_score)
        else:
            winner_names = " and ".join(w.name for w in winners)
            self.broadcast_l("threes-tie", players=winner_names, score=lowest_score)

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Threes-specific data."""
        # Sorted by score ascending (lowest wins)
        sorted_players = sorted(
            [p for p in self.players if isinstance(p, ThreesPlayer) and not p.is_spectator],
            key=lambda p: p.total_score,
        )

        # Build final scores
        final_scores = {}
        for p in sorted_players:
            final_scores[p.name] = p.total_score

        winner = sorted_players[0] if sorted_players else None

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
                for p in sorted_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": winner.total_score if winner else 0,
                "final_scores": final_scores,
                "rounds_played": self.round,
                "total_rounds": self.options.total_rounds,
                "scoring_mode": "lowest_wins",
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Threes game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(f"{i}. {name}: {points_str}")

        return lines

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI."""
        super().on_tick()

        if not self.game_active:
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        """Bot AI decision making."""
        if not isinstance(player, ThreesPlayer):
            return None

        # If no dice, roll
        if not player.dice.has_rolled:
            return "roll"

        # If only 1 unlocked die, we must bank (auto-handled)
        if player.dice.unlocked_count <= 1:
            return "bank"

        # Check if all dice are kept/locked - then bank
        if player.dice.all_decided:
            return "bank"

        # Decide what to keep using strategy
        self._bot_decide_keepers(player)

        # If we've kept something new, roll
        if player.dice.kept_unlocked_count > 0:
            return "roll"

        # Fallback: shouldn't reach here, but keep lowest if we do
        return None

    def _bot_decide_keepers(self, player: ThreesPlayer) -> None:
        """Bot AI to decide which dice to keep."""
        dice = player.dice

        # Clear current kept dice (except locked ones)
        dice.kept = set(dice.locked)

        # Group available dice by value
        available: dict[int, list[int]] = {}  # value -> list of indices
        for i in range(5):
            if not dice.is_locked(i):
                value = dice.get_value(i)
                if value is not None:
                    if value not in available:
                        available[value] = []
                    available[value].append(i)

        # Count locked sixes for moon shot check
        locked_sixes = sum(1 for i in dice.locked if dice.get_value(i) == 6)
        available_sixes = available.get(6, [])

        # Strategy 1: Go for moon shot if 3+ sixes locked or 4+ total sixes
        if locked_sixes >= 3 or (len(available_sixes) + locked_sixes >= 4):
            for i in available_sixes:
                dice.keep(i)
            if available_sixes:
                return

        # Strategy 2: Keep threes (0 points!)
        if 3 in available:
            for i in available[3]:
                dice.keep(i)
            return

        # Strategy 3: Keep ones (low value)
        if 1 in available:
            for i in available[1]:
                dice.keep(i)
            return

        # Strategy 4: Keep twos
        if 2 in available:
            for i in available[2]:
                dice.keep(i)
            return

        # Strategy 5: Keep lowest available
        for value in [4, 5, 6]:
            if value in available:
                dice.keep(available[value][0])
                return
