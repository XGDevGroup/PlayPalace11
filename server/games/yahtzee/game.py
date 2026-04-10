"""
Yahtzee Game Implementation for PlayPalace v11.

Classic dice game: roll 5 dice up to 3 times per turn, then score in one of 13 categories.
Fill all categories to complete the game. Highest total score wins.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from .bot import bot_think as yahtzee_bot_think
from ...game_utils.action_guard_mixin import ActionGuardMixin
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.dice import (
    DiceSet,
    count_dice,
    has_consecutive_run,
    has_full_house,
    has_n_of_a_kind,
)
from ...game_utils.dice_game_mixin import DiceGameMixin
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState


# Scoring categories
UPPER_CATEGORIES = ["ones", "twos", "threes", "fours", "fives", "sixes"]
LOWER_CATEGORIES = [
    "three_kind",
    "four_kind",
    "full_house",
    "small_straight",
    "large_straight",
    "yahtzee",
    "chance",
]
ALL_CATEGORIES = UPPER_CATEGORIES + LOWER_CATEGORIES

# Category display names (for localization keys)
CATEGORY_NAMES = {
    "ones": "yahtzee-category-ones",
    "twos": "yahtzee-category-twos",
    "threes": "yahtzee-category-threes",
    "fours": "yahtzee-category-fours",
    "fives": "yahtzee-category-fives",
    "sixes": "yahtzee-category-sixes",
    "three_kind": "yahtzee-category-three-kind",
    "four_kind": "yahtzee-category-four-kind",
    "full_house": "yahtzee-category-full-house",
    "small_straight": "yahtzee-category-small-straight",
    "large_straight": "yahtzee-category-large-straight",
    "yahtzee": "yahtzee-category-yahtzee",
    "chance": "yahtzee-category-chance",
}

# Upper section target values
UPPER_VALUES = {
    "ones": 1,
    "twos": 2,
    "threes": 3,
    "fours": 4,
    "fives": 5,
    "sixes": 6,
}


def calculate_score(dice: list[int], category: str) -> int:
    """Calculate the score for a category given the dice."""
    if not dice or len(dice) != 5:
        return 0

    counts = count_dice(dice)
    dice_sum = sum(dice)

    # Upper section - sum of matching dice
    if category in UPPER_VALUES:
        target = UPPER_VALUES[category]
        return counts[target] * target

    # Three of a Kind - sum of all if 3+ of same
    if category == "three_kind":
        if has_n_of_a_kind(counts, 3):
            return dice_sum
        return 0

    # Four of a Kind - sum of all if 4+ of same
    if category == "four_kind":
        if has_n_of_a_kind(counts, 4):
            return dice_sum
        return 0

    # Full House - 3 of one kind + 2 of another = 25 points
    if category == "full_house":
        if has_full_house(counts, allow_five_kind=True):
            return 25
        return 0

    # Small Straight - 4 consecutive = 30 points
    if category == "small_straight":
        if has_consecutive_run(counts, length=4, min_value=1, max_value=6):
            return 30
        return 0

    # Large Straight - 5 consecutive = 40 points
    if category == "large_straight":
        if has_consecutive_run(counts, length=5, min_value=1, max_value=6, require_unique=True):
            return 40
        return 0

    # Yahtzee - 5 of a kind = 50 points
    if category == "yahtzee":
        if has_n_of_a_kind(counts, 5):
            return 50
        return 0

    # Chance - sum of all dice
    if category == "chance":
        return dice_sum

    return 0


def is_yahtzee(dice: list[int]) -> bool:
    """Check if dice are a Yahtzee (5 of a kind)."""
    if len(dice) != 5:
        return False
    return len(set(dice)) == 1


def _default_scores() -> dict[str, int | None]:
    """Create default scoresheet with all categories unfilled."""
    return {cat: None for cat in ALL_CATEGORIES}


@dataclass
class YahtzeePlayer(Player):
    """Player state for Yahtzee game."""

    # Dice state
    dice: DiceSet = field(default_factory=lambda: DiceSet(num_dice=5, sides=6))
    rolls_left: int = 3  # Rolls remaining this turn

    # Scoresheet - None means not filled, int is the score
    scores: dict[str, int | None] = field(default_factory=_default_scores)

    # Bonuses
    yahtzee_bonus_count: int = 0  # Number of Yahtzee bonuses earned
    upper_bonus_awarded: bool = False  # Whether upper section bonus was given

    def get_upper_total(self) -> int:
        """Get total of upper section scores."""
        return sum(
            self.scores.get(cat) or 0
            for cat in UPPER_CATEGORIES
            if self.scores.get(cat) is not None
        )

    def get_total_score(self) -> int:
        """Get total score including bonuses."""
        total = sum(s for s in self.scores.values() if s is not None)
        # Upper bonus
        if self.upper_bonus_awarded:
            total += 35
        # Yahtzee bonuses
        total += self.yahtzee_bonus_count * 100
        return total

    def get_open_categories(self) -> list[str]:
        """Get list of categories not yet filled."""
        return [cat for cat in ALL_CATEGORIES if self.scores.get(cat) is None]

    def is_scoresheet_complete(self) -> bool:
        """Check if all categories are filled."""
        return all(self.scores.get(cat) is not None for cat in ALL_CATEGORIES)


@dataclass
class YahtzeeOptions(GameOptions):
    """Options for Yahtzee game."""

    num_games: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=10,
            value_key="rounds",
            label="yahtzee-set-rounds",
            prompt="yahtzee-enter-rounds",
            change_msg="yahtzee-option-changed-rounds",
        )
    )


@dataclass
@register_game
class YahtzeeGame(ActionGuardMixin, Game, DiceGameMixin):
    """
    Yahtzee dice game.

    Players take turns rolling 5 dice up to 3 times, keeping dice between rolls.
    After rolling, they must score in one of 13 categories. Each category can
    only be used once. The game ends when all players have filled all categories.
    Highest total score wins.
    """

    relevant_preferences = ["clear_kept_on_roll", "dice_keeping_style"]

    players: list[YahtzeePlayer] = field(default_factory=list)
    options: YahtzeeOptions = field(default_factory=YahtzeeOptions)

    # Game tracking
    current_game: int = 0
    games_played: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Yahtzee"

    @classmethod
    def get_type(cls) -> str:
        return "yahtzee"

    @classmethod
    def get_category(cls) -> str:
        return "category-dice-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 1

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> YahtzeePlayer:
        """Create a new player with Yahtzee-specific state."""
        return YahtzeePlayer(id=player_id, name=name, is_bot=is_bot)

    def create_turn_action_set(self, player: YahtzeePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Dice toggle actions (1-5 keys) - shown after first roll
        self.add_dice_toggle_actions(action_set)

        # Roll action
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "yahtzee-roll-all"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
                get_label="_get_roll_label",
            )
        )

        # Scoring category actions
        for cat in ALL_CATEGORIES:
            cat_name = Localization.get(locale, CATEGORY_NAMES[cat])
            action_set.add(
                Action(
                    id=f"score_{cat}",
                    label=f"{cat_name} (- points)",
                    handler="_action_score",
                    is_enabled=f"_is_score_{cat}_enabled",
                    is_hidden=f"_is_score_{cat}_hidden",
                    get_label=f"_get_score_{cat}_label",
                    show_in_actions_menu=False,
                )
            )

        # View actions
        action_set.add(
            Action(
                id="view_dice",
                label=Localization.get(locale, "yahtzee-view-dice"),
                handler="_action_view_dice",
                is_enabled="_is_view_dice_enabled",
                is_hidden="_is_view_dice_hidden",
            )
        )
        action_set.add(
            Action(
                id="view_scoresheet",
                label=Localization.get(locale, "yahtzee-check-scoresheet"),
                handler="_action_view_scoresheet",
                is_enabled="_is_view_scoresheet_enabled",
                is_hidden="_is_view_scoresheet_hidden",
            )
        )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Roll
        self.define_keybind("r", "Roll dice", ["roll"], state=KeybindState.ACTIVE)

        # Toggle dice (1-5 keys) - from DiceGameMixin
        self.setup_dice_keybinds()

        # View actions
        self.define_keybind("d", "View dice", ["view_dice"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "View scoresheet", ["view_scoresheet"], state=KeybindState.ACTIVE)

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_roll_enabled(self, player: Player) -> str | None:
        """Check if roll action is enabled."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        ytz_player: YahtzeePlayer = player  # type: ignore
        if ytz_player.rolls_left <= 0:
            return "yahtzee-no-rolls-left"
        if ytz_player.dice.has_rolled and ytz_player.dice.all_decided:
            return "action-not-available"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        """Check if roll action is hidden."""
        ytz_player: YahtzeePlayer = player  # type: ignore
        can_reroll = not (ytz_player.dice.has_rolled and ytz_player.dice.all_decided)
        return self.turn_action_visibility(
            player, extra_condition=ytz_player.rolls_left > 0 and can_reroll
        )

    def _get_roll_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for roll action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        ytz_player: YahtzeePlayer = player  # type: ignore
        if ytz_player.dice.has_rolled:
            return Localization.get(locale, "yahtzee-roll", count=ytz_player.rolls_left)
        return Localization.get(locale, "yahtzee-roll-all")

    def _is_dice_toggle_enabled(self, player: Player, die_index: int) -> str | None:
        """Check if toggling die at index is enabled (override from DiceGameMixin)."""
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        ytz_player: YahtzeePlayer = player  # type: ignore
        if not ytz_player.dice.has_rolled:
            return "dice-not-rolled"
        if ytz_player.rolls_left <= 0:
            return "yahtzee-no-rolls-left"
        return None

    def _is_dice_toggle_hidden(self, player: Player, die_index: int) -> Visibility:
        """Check if die toggle action is hidden (override from DiceGameMixin)."""
        ytz_player: YahtzeePlayer = player  # type: ignore
        extra_condition = ytz_player.dice.has_rolled and ytz_player.rolls_left > 0
        return self.turn_action_visibility(player, extra_condition=extra_condition)

    def _is_view_dice_enabled(self, player: Player) -> str | None:
        """Check if view dice action is enabled."""
        return self.guard_game_active()

    def _is_view_dice_hidden(self, player: Player) -> Visibility:
        """View dice is always hidden from menu (keybind only)."""
        return Visibility.HIDDEN

    def _is_view_scoresheet_enabled(self, player: Player) -> str | None:
        """Check if view scoresheet action is enabled."""
        return self.guard_game_active()

    def _is_view_scoresheet_hidden(self, player: Player) -> Visibility:
        """View scoresheet is always hidden from menu (keybind only)."""
        return Visibility.HIDDEN

    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action."""
        ytz_player: YahtzeePlayer = player  # type: ignore

        if ytz_player.rolls_left <= 0:
            return

        had_rolled = ytz_player.dice.has_rolled
        locked_before = set(ytz_player.dice.locked)
        kept_before = set(ytz_player.dice.kept)
        if had_rolled:
            rolled_indices = [
                i
                for i in range(ytz_player.dice.num_dice)
                if i not in locked_before and i not in kept_before
            ]
        else:
            rolled_indices = list(range(ytz_player.dice.num_dice))

        # Play roll sound
        self.play_sound("game_pig/roll.ogg")

        # Roll the dice:
        # - lock_kept=False: kept dice don't become permanently locked
        # - clear_kept: controlled by user preference (default True)
        user = self.get_user(player)
        clear_kept = (
            user.preferences.get_effective("clear_kept_on_roll", game_type=self.get_type())
            if user
            else True
        )
        ytz_player.dice.roll(lock_kept=False, clear_kept=clear_kept)
        self._apply_dice_values_defaults(ytz_player)
        ytz_player.rolls_left -= 1

        # Announce rerolled dice only (first roll announces all dice).
        dice_str = ", ".join(str(ytz_player.dice.values[i]) for i in rolled_indices)
        self.broadcast_personal_l(
            player,
            "yahtzee-you-rolled",
            "yahtzee-player-rolled",
            dice=dice_str,
            remaining=ytz_player.rolls_left,
        )

        # If no rolls left, prompt to choose category
        if ytz_player.rolls_left == 0:
            user = self.get_user(player)
            if user:
                user.speak_l("yahtzee-choose-category")

        # Bot thinking time
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(15, 25))  # nosec B311

        self.rebuild_all_menus()
        if ytz_player.rolls_left > 0:
            self.update_player_menu(player, selection_id="toggle_die_0")

    def _action_score(self, player: Player, action_id: str) -> None:
        """Handle scoring in a category."""
        ytz_player: YahtzeePlayer = player  # type: ignore

        # Extract category from action_id
        category = action_id.replace("score_", "")
        if category not in ALL_CATEGORIES:
            return

        # Check category is open
        if ytz_player.scores.get(category) is not None:
            return

        # Calculate score
        points = calculate_score(ytz_player.dice.values, category)

        # Check for Yahtzee bonus
        yahtzee_bonus = False
        if is_yahtzee(ytz_player.dice.values):
            # If Yahtzee category already filled with 50, award bonus
            if ytz_player.scores.get("yahtzee") == 50:
                ytz_player.yahtzee_bonus_count += 1
                yahtzee_bonus = True

        # Record score
        ytz_player.scores[category] = points

        # Get localized category name
        user = self.get_user(player)
        locale = user.locale if user else "en"
        cat_name = Localization.get(locale, CATEGORY_NAMES[category])

        # Announce (v10 style: "You scored X points in Y.")
        self.play_sound("game_pig/bank.ogg")

        self.broadcast_personal_l(
            player,
            "yahtzee-you-scored",
            "yahtzee-player-scored",
            points=points,
            category=cat_name,
        )

        # Track points in TeamManager
        self._team_manager.add_to_team_round_score(player.name, points)

        if yahtzee_bonus:
            self.play_sound("game_farkle/6kind.ogg")
            self.broadcast_personal_l(player, "yahtzee-you-bonus", "yahtzee-player-bonus")
            self._team_manager.add_to_team_round_score(player.name, 100)

        # Check for upper bonus (first time upper section is complete)
        if not ytz_player.upper_bonus_awarded:
            upper_complete = all(ytz_player.scores.get(cat) is not None for cat in UPPER_CATEGORIES)
            if upper_complete:
                upper_total = ytz_player.get_upper_total()
                if upper_total >= 63:
                    ytz_player.upper_bonus_awarded = True
                    self.play_sound("game_pig/win.ogg")
                    self.broadcast_personal_l(
                        player,
                        "yahtzee-you-upper-bonus",
                        "yahtzee-player-upper-bonus",
                        total=upper_total,
                    )
                    self._team_manager.add_to_team_round_score(player.name, 35)
                else:
                    self.broadcast_personal_l(
                        player,
                        "yahtzee-you-upper-bonus-missed",
                        "yahtzee-player-upper-bonus-missed",
                        total=upper_total,
                    )

        # End turn
        self._end_turn()

    def _action_view_dice(self, player: Player, action_id: str) -> None:
        """View current dice state."""
        current = self.current_player
        if not current:
            return

        ytz_current: YahtzeePlayer = current  # type: ignore
        user = self.get_user(player)
        if not user:
            return

        if not ytz_current.dice.has_rolled:
            user.speak_l("yahtzee-not-rolled")
            return

        dice_str = ytz_current.dice.format_values_only()
        kept = [str(ytz_current.dice.get_value(i)) for i in range(5) if ytz_current.dice.is_kept(i)]
        if kept:
            kept_str = ", ".join(kept)
            user.speak_l("yahtzee-your-dice-kept", dice=dice_str, kept=kept_str)
        else:
            user.speak_l("yahtzee-your-dice", dice=dice_str)

    def _action_view_scoresheet(self, player: Player, action_id: str) -> None:
        """View scoresheet."""
        user = self.get_user(player)
        if not user:
            return

        # Show current player's scoresheet
        current = self.current_player
        if not current:
            return

        ytz_current: YahtzeePlayer = current  # type: ignore
        locale = user.locale

        lines = [Localization.get(locale, "yahtzee-scoresheet-header", player=current.name)]
        lines.append(Localization.get(locale, "yahtzee-scoresheet-upper"))

        for cat in UPPER_CATEGORIES:
            cat_name = Localization.get(locale, CATEGORY_NAMES[cat])
            score = ytz_current.scores.get(cat)
            if score is not None:
                lines.append(f"  {cat_name}: {score}")
            else:
                lines.append(f"  {cat_name}: -")

        upper_total = ytz_current.get_upper_total()
        if ytz_current.upper_bonus_awarded:
            lines.append(
                Localization.get(locale, "yahtzee-scoresheet-upper-total-bonus", total=upper_total)
            )
        else:
            needed = max(0, 63 - upper_total)
            lines.append(
                Localization.get(
                    locale,
                    "yahtzee-scoresheet-upper-total-needed",
                    total=upper_total,
                    needed=needed,
                )
            )

        lines.append(Localization.get(locale, "yahtzee-scoresheet-lower"))

        for cat in LOWER_CATEGORIES:
            cat_name = Localization.get(locale, CATEGORY_NAMES[cat])
            score = ytz_current.scores.get(cat)
            if score is not None:
                lines.append(f"  {cat_name}: {score}")
            else:
                lines.append(f"  {cat_name}: -")

        yahtzee_bonus = ytz_current.yahtzee_bonus_count * 100
        lines.append(
            Localization.get(
                locale,
                "yahtzee-scoresheet-yahtzee-bonus",
                count=ytz_current.yahtzee_bonus_count,
                total=yahtzee_bonus,
            )
        )

        lines.append(
            Localization.get(
                locale,
                "yahtzee-scoresheet-grand-total",
                total=ytz_current.get_total_score(),
            )
        )

        self.status_box(player, lines)

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.current_game = 0
        self.games_played = 0

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Set up TeamManager
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Reset all player state
        for p in active_players:
            self._reset_player(p)

        # Play music
        self.play_music("game_pig/mus.ogg")

        # Start first game
        self._start_game()

    def _reset_player(self, player: YahtzeePlayer) -> None:
        """Reset a player's state for a new game."""
        player.dice.reset()
        player.rolls_left = 3
        player.scores = {cat: None for cat in ALL_CATEGORIES}
        player.yahtzee_bonus_count = 0
        player.upper_bonus_awarded = False

    def _start_game(self) -> None:
        """Start a new game."""
        self.current_game += 1
        self.broadcast_l("game-round-start", round=self.current_game)

        # Reset turn order
        self.set_turn_players(self.get_active_players())

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        ytz_player: YahtzeePlayer = player  # type: ignore

        # Reset turn state
        ytz_player.dice.reset()
        ytz_player.rolls_left = 3

        # Announce turn
        self.announce_turn()

        # Bot setup
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(10, 20))  # nosec B311

        self.rebuild_all_menus()

    def _end_turn(self) -> None:
        """End current player's turn."""
        player = self.current_player
        if not player:
            return

        ytz_player: YahtzeePlayer = player  # type: ignore

        # Check if this player's scoresheet is complete
        if ytz_player.is_scoresheet_complete():
            # Check if all players have completed scoresheets
            all_complete = all(
                p.is_scoresheet_complete()
                for p in self.players
                if isinstance(p, YahtzeePlayer) and not p.is_spectator
            )

            if all_complete:
                self._end_game()
                return

        # Move to next player
        BotHelper.jolt_bots(self, ticks=random.randint(15, 25))  # nosec B311

        if self.turn_index >= len(self.turn_players) - 1:
            # Round complete, back to first player
            self.turn_index = 0
            self.set_turn_players(self.get_active_players())
        else:
            self.advance_turn(announce=False)

        self._start_turn()

    def _end_game(self) -> None:
        """End the current game."""
        self.games_played += 1

        # Find winner(s)
        active_players = [
            p for p in self.players if isinstance(p, YahtzeePlayer) and not p.is_spectator
        ]
        if not active_players:
            return

        high_score = max(p.get_total_score() for p in active_players)
        winners = [p for p in active_players if p.get_total_score() == high_score]

        self.play_sound("game_pig/win.ogg")

        if len(winners) == 1:
            self.broadcast_l("yahtzee-winner", player=winners[0].name, score=high_score)
        else:
            winner_names = [w.name for w in winners]
            for p in self.players:
                user = self.get_user(p)
                if user:
                    names_str = Localization.format_list_and(user.locale, winner_names)
                    user.speak_l(
                        "yahtzee-winners-tie", players=names_str, score=high_score, buffer="table"
                    )

        # Commit round scores to total
        self._team_manager.commit_round_scores()

        # Check if more games to play
        if self.games_played < self.options.num_games:
            # Reset for next game
            for p in active_players:
                self._reset_player(p)
            self._team_manager.reset_round_scores()
            self._start_game()
        else:
            # All games complete
            self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Yahtzee-specific data."""
        active_players = [
            p for p in self.players if isinstance(p, YahtzeePlayer) and not p.is_spectator
        ]

        sorted_players = sorted(
            active_players,
            key=lambda p: p.get_total_score(),
            reverse=True,
        )

        # Build final scores
        final_scores = {}
        for p in sorted_players:
            final_scores[p.name] = p.get_total_score()

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
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": winner.get_total_score() if winner else 0,
                "final_scores": final_scores,
                "games_played": self.games_played,
                "num_games": self.options.num_games,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Yahtzee game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(f"{i}. {name}: {points_str}")

        return lines

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()

        if not self.game_active:
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: YahtzeePlayer) -> str | None:
        """Bot AI decision making."""
        return yahtzee_bot_think(
            self,
            player,
            calculate_score=calculate_score,
            all_categories=ALL_CATEGORIES,
            upper_categories=UPPER_CATEGORIES,
        )


# =============================================================================
# Dynamic Scoring Category Methods
# =============================================================================
# Create is_enabled, is_hidden, and get_label methods for each scoring category
def _make_score_enabled(cat: str):
    """Create an is_enabled method for a scoring category."""

    def method(self, player: Player) -> str | None:
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        if not player.dice.has_rolled:
            return "yahtzee-roll-first"
        if cat not in player.get_open_categories():
            return "yahtzee-category-filled"
        return None

    return method


def _make_score_hidden(cat: str):
    """Create an is_hidden method for a scoring category."""

    def method(self, player: Player) -> Visibility:
        extra_condition = player.dice.has_rolled and cat in player.get_open_categories()
        return self.turn_action_visibility(player, extra_condition=extra_condition)

    return method


def _make_score_label(cat: str):
    """Create a get_label method for a scoring category."""

    def method(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        cat_name = Localization.get(locale, CATEGORY_NAMES[cat])
        if player.dice.has_rolled:
            points = calculate_score(player.dice.values, cat)
            return f"{cat_name} for {points} points"
        return cat_name

    return method


# Register the methods on YahtzeeGame
for _cat in ALL_CATEGORIES:
    setattr(YahtzeeGame, f"_is_score_{_cat}_enabled", _make_score_enabled(_cat))
    setattr(YahtzeeGame, f"_is_score_{_cat}_hidden", _make_score_hidden(_cat))
    setattr(YahtzeeGame, f"_get_score_{_cat}_label", _make_score_label(_cat))
