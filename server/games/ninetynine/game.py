"""
Ninety Nine Game Implementation for PlayPalace v11.

A card game where players try to avoid pushing the running total over 99.
Last player standing wins!

Rules match v10 implementation with Quentin C and RS Games variants.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.cards import (
    Card,
    Deck,
    DeckFactory,
    card_name,
    card_name_with_article,
    sort_cards,
    SUIT_NONE,
    RS_RANK_PLUS_10,
    RS_RANK_MINUS_10,
    RS_RANK_PASS,
    RS_RANK_REVERSE,
    RS_RANK_SKIP,
    RS_RANK_NINETY_NINE,
)
from ...game_utils.options import BoolOption, IntOption, MenuOption, option_field
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState
from .bot import bot_think as _bot_think, evaluate_count as _evaluate_count


# =============================================================================
# Game Constants
# =============================================================================

# Count thresholds
MAX_COUNT = 99
MILESTONE_33 = 33
MILESTONE_66 = 66
ACE_AUTO_THRESHOLD = 88  # Auto-choose +1 when count > this
TEN_AUTO_THRESHOLD = 90  # Auto-choose -10 when count >= this
TWO_DIVIDE_THRESHOLD = 49  # Divide by 2 when count > this and even

# Default options
DEFAULT_HAND_SIZE = 3
DEFAULT_TOKENS = 9

# Token penalties
PENALTY_BUST = 2  # Quentin C: going over 99
PENALTY_BUST_RS = 1  # RS Games: going over 99
PENALTY_MILESTONE_PASS = 1  # Passing through 33 or 66
PENALTY_MILESTONE_99 = 2  # Landing on 99 (others lose this)
PENALTY_MILESTONE_33_66 = 1  # Landing on 33/66 (others lose this)
PENALTY_NO_CARDS = 3  # Running out of cards

# Draw timeout (manual draw mode)
DRAW_TIMEOUT_TICKS = 200  # 10 seconds at 20 ticks/sec


@dataclass
class NinetyNinePlayer(Player):
    """Player state for Ninety Nine."""

    hand: list[Card] = field(default_factory=list)
    tokens: int = DEFAULT_TOKENS
    draw_timeout_ticks: int = 0  # Per-player manual draw countdown


@dataclass
class NinetyNineOptions(GameOptions):
    """Options for Ninety Nine game."""

    starting_tokens: int = option_field(
        IntOption(
            default=9,
            min_val=1,
            max_val=50,
            value_key="tokens",
            label="ninetynine-set-tokens",
            prompt="ninetynine-enter-tokens",
            change_msg="ninetynine-option-changed-tokens",
            description="ninetynine-desc-tokens",
        )
    )
    hand_size: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=13,
            value_key="size",
            label="ninetynine-set-hand-size",
            prompt="ninetynine-enter-hand-size",
            change_msg="ninetynine-option-changed-hand-size",
            description="ninetynine-desc-hand-size",
        )
    )
    rules_variant: str = option_field(
        MenuOption(
            default="quentin_c",
            value_key="rules",
            choices=["quentin_c", "rs_games"],
            choice_labels={
                "quentin_c": "ninetynine-rules-variant-quentin_c",
                "rs_games": "ninetynine-rules-variant-rs_games",
            },
            label="ninetynine-set-rules",
            prompt="ninetynine-select-rules",
            change_msg="ninetynine-option-changed-rules",
            description="ninetynine-desc-rules",
        )
    )
    autodraw: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="ninetynine-set-autodraw",
            change_msg="ninetynine-option-changed-autodraw",
            description="ninetynine-desc-autodraw",
        )
    )


@dataclass
@register_game
class NinetyNineGame(Game):
    """
    Ninety Nine - A card game where players try to avoid going over 99.

    Players take turns playing cards that modify a running count.
    Rules match v10 with Quentin C and RS Games variants.
    """

    players: list[NinetyNinePlayer] = field(default_factory=list)
    options: NinetyNineOptions = field(default_factory=NinetyNineOptions)

    # Game state
    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)
    count: int = 0  # Running count

    # Players still in the game (have tokens)
    alive_player_ids: list[str] = field(default_factory=list)

    @classmethod
    def get_name(cls) -> str:
        return "Ninety Nine"

    @classmethod
    def get_type(cls) -> str:
        return "ninetynine"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> NinetyNinePlayer:
        """Create a new player with Ninety Nine-specific state."""
        return NinetyNinePlayer(
            id=player_id,
            name=name,
            is_bot=is_bot,
            tokens=self.options.starting_tokens,
        )

    @property
    def alive_players(self) -> list[NinetyNinePlayer]:
        """Get players who still have tokens."""
        return [p for p in self.players if p.id in self.alive_player_ids and not p.is_spectator]

    @property
    def is_quentin_c(self) -> bool:
        """Check if using Quentin C rules."""
        return self.options.rules_variant == "quentin_c"

    def on_player_skipped(self, player: Player) -> None:
        """Announce when a player is skipped."""
        self.broadcast_l("ninetynine-player-skipped", player=player.name)

    def _play_sound_for_player(
        self, player: NinetyNinePlayer, sound_for_player: str, sound_for_others: str
    ) -> None:
        """Play different sounds for a specific player vs everyone else."""
        for p in self.players:
            user = self.get_user(p)
            if user:
                if p == player:
                    user.play_sound(sound_for_player)
                else:
                    user.play_sound(sound_for_others)

    def _sort_hand(self, player: NinetyNinePlayer) -> None:
        """Sort a player's hand by rank."""
        player.hand = sort_cards(player.hand, by_suit=False)

    # ==========================================================================
    # Card Value Calculation
    # ==========================================================================

    def calculate_card_value(self, card: Card, current_count: int) -> int | None:
        """
        Calculate the value a card adds to the count.
        Returns None if player choice is needed or special handling required.
        """
        rank = card.rank

        if self.is_quentin_c:
            return self._calculate_quentin_c_value(rank, current_count)
        else:
            return self._calculate_rs_games_value(rank)

    def _calculate_quentin_c_value(self, rank: int, current_count: int) -> int | None:
        """Calculate card value for Quentin C variant."""
        if rank == 1:  # Ace: +1 or +11
            if current_count > ACE_AUTO_THRESHOLD:
                return 1  # Auto +1 if would bust with +11
            return None  # Choice needed

        elif rank == 2:  # 2: multiply or divide (special handling)
            return None

        elif 3 <= rank <= 8:  # 3-8: face value
            return rank

        elif rank == 9:  # 9: pass
            return 0

        elif rank == 10:  # 10: +10 or -10
            if current_count >= TEN_AUTO_THRESHOLD:
                return -10  # Auto -10 at high counts
            return None  # Choice needed

        elif rank in (11, 12, 13):  # Jack, Queen, King: +10
            return 10

        return 0

    def _calculate_rs_games_value(self, rank: int) -> int | None:
        """Calculate card value for RS Games variant."""
        if 1 <= rank <= 9:  # Number cards: face value
            return rank
        elif rank == RS_RANK_PLUS_10:
            return 10
        elif rank == RS_RANK_MINUS_10:
            return -10
        elif rank in (RS_RANK_PASS, RS_RANK_REVERSE, RS_RANK_SKIP):
            return 0
        elif rank == RS_RANK_NINETY_NINE:
            return None  # Special handling - sets to exactly 99
        return 0

    def calculate_two_effect(self, current_count: int) -> int:
        """Calculate the new count after playing a 2 (Quentin C)."""
        if current_count % 2 == 0 and current_count > TWO_DIVIDE_THRESHOLD:
            return current_count // 2
        else:
            return current_count * 2

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: NinetyNinePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        action_set = ActionSet(name="turn")

        # Card slot actions will be dynamically created in _update_card_actions

        # Status actions (keybind only)
        action_set.add(
            Action(
                id="check_count",
                label="Check count",
                handler="_action_check_count",
                is_enabled="_is_check_count_enabled",
                is_hidden="_is_check_count_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_hand",
                label="Check hand",
                handler="_action_check_hand",
                is_enabled="_is_check_hand_enabled",
                is_hidden="_is_check_hand_hidden",
            )
        )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Number keybinds for card slots removed (menu/arrow selection only)

        # Draw card (Space or D)
        self.define_keybind("space", "Draw card", ["draw_card"], state=KeybindState.ACTIVE)
        self.define_keybind("d", "Draw card", ["draw_card"], state=KeybindState.ACTIVE)

        # Count check
        self.define_keybind(
            "c",
            "Check count",
            ["check_count"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Hand check
        self.define_keybind(
            "h",
            "Check hand",
            ["check_hand"],
            state=KeybindState.ACTIVE,
        )

    def _update_card_actions(self, player: NinetyNinePlayer) -> None:
        """Update card slot actions based on player's hand."""
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        user = self.get_user(player)
        locale = user.locale if user else "en"

        is_current = self.current_player == player
        is_playing = self.status == "playing"
        needs_to_draw = player.draw_timeout_ticks > 0

        # Remove old dynamic actions
        turn_set.remove_by_prefix("card_slot_")
        turn_set.remove("draw_card")

        # Add card slot actions for cards in hand
        for i, card in enumerate(player.hand, 1):
            action_id = f"card_slot_{i}"

            # Attach MenuInput for aces/tens that need a choice
            # (only for the current player, and only in Quentin C variant)
            input_request = None
            if is_current and self.is_quentin_c:
                if card.rank == 1 and self.count <= ACE_AUTO_THRESHOLD:
                    input_request = MenuInput(
                        prompt="ninetynine-ace-choice",
                        options="_card_choice_options",
                        bot_select="_bot_select_card_choice",
                    )
                elif card.rank == 10 and self.count < TEN_AUTO_THRESHOLD:
                    input_request = MenuInput(
                        prompt="ninetynine-ten-choice",
                        options="_card_choice_options",
                        bot_select="_bot_select_card_choice",
                    )

            turn_set.add(
                Action(
                    id=action_id,
                    label=card_name(card, locale),
                    handler="_action_play_card",
                    is_enabled="_is_card_slot_enabled",
                    is_hidden="_is_card_slot_hidden",
                    input_request=input_request,
                    show_in_actions_menu=False,
                )
            )

        # Add draw action if in manual draw mode
        if needs_to_draw and is_playing:
            turn_set.add(
                Action(
                    id="draw_card",
                    label=Localization.get(locale, "ninetynine-draw-card"),
                    handler="_action_draw_card",
                    is_enabled="_is_draw_enabled",
                    is_hidden="_is_draw_hidden",
                )
            )

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_check_count_enabled(self, player: Player) -> str | None:
        """Check if check count action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_count_hidden(self, player: Player) -> Visibility:
        """Check count is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_check_hand_enabled(self, player: Player) -> str | None:
        """Check if check hand action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hand_hidden(self, player: Player) -> Visibility:
        """Check hand is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_card_slot_enabled(self, player: Player) -> str | None:
        """Check if card slot actions are enabled."""
        if self.status != "playing":
            return "action-not-playing"
        # Turn check is done in handler to allow action to appear in menu
        return None

    def _is_card_slot_hidden(self, player: Player) -> Visibility:
        """Card slots are visible during play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_draw_enabled(self, player: Player) -> str | None:
        """Check if draw action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_draw_hidden(self, player: Player) -> Visibility:
        """Draw action is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _update_turn_actions(self, player: NinetyNinePlayer) -> None:
        """Update turn action availability for a player."""
        self._update_card_actions(player)

    def _update_all_turn_actions(self) -> None:
        """Update turn actions for all players."""
        for player in self.players:
            self._update_turn_actions(player)

    # ==========================================================================
    # MenuInput Callbacks (for Ace / Ten subchoices)
    # ==========================================================================

    def _card_choice_options(self, player: Player) -> list[str]:
        """Get choice options for ace or ten cards."""
        if not isinstance(player, NinetyNinePlayer):
            return []

        action_id = self._pending_actions.get(player.id)
        if not action_id:
            return []

        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return []

        if slot < 0 or slot >= len(player.hand):
            return []

        card = player.hand[slot]
        user = self.get_user(player)
        locale = user.locale if user else "en"

        if card.rank == 1:
            return [
                Localization.get(locale, "ninetynine-ace-add-eleven"),
                Localization.get(locale, "ninetynine-ace-add-one"),
            ]
        elif card.rank == 10:
            return [
                Localization.get(locale, "ninetynine-ten-add"),
                Localization.get(locale, "ninetynine-ten-subtract"),
            ]
        return []

    def _bot_select_card_choice(self, player: Player, options: list[str]) -> str | None:
        """Bot selects card choice for ace or ten."""
        if not isinstance(player, NinetyNinePlayer):
            return None

        action_id = self._pending_actions.get(player.id)
        if not action_id:
            return None

        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return None

        if slot < 0 or slot >= len(player.hand):
            return None

        card = player.hand[slot]

        if card.rank == 1:  # Ace: compare +11 vs +1
            score_11 = _evaluate_count(self, player, self.count + 11, 1)
            score_1 = _evaluate_count(self, player, self.count + 1, 1)
            return options[0] if score_11 > score_1 else options[1]
        elif card.rank == 10:  # Ten: compare +10 vs -10
            score_plus = _evaluate_count(self, player, self.count + 10, 10)
            score_minus = _evaluate_count(self, player, self.count - 10, 10)
            return options[0] if score_plus > score_minus else options[1]
        return None

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 0

        # Set up teams (individual mode)
        active_players = self.get_active_players()
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])

        # Initialize alive players
        self.alive_player_ids = [p.id for p in active_players]

        # Initialize player tokens
        for player in active_players:
            player.tokens = self.options.starting_tokens
        self._sync_team_scores()

        # Play music
        self.play_music("game_ninetynine/mus.ogg")

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1
        self.count = 0
        self.turn_direction = 1
        self.turn_skip_count = 0

        # Build and shuffle deck based on variant
        if self.is_quentin_c:
            self.deck, _ = DeckFactory.standard_deck()
        else:
            self.deck, _ = DeckFactory.rs_games_deck()
        self.discard_pile = []

        # Update alive players list
        self.alive_player_ids = [p.id for p in self.get_active_players() if p.tokens > 0]

        # Deal cards to alive players
        for player in self.alive_players:
            player.hand = []
            for _ in range(self.options.hand_size):
                card = self.deck.draw_one()
                if card:
                    player.hand.append(card)
            self._sort_hand(player)

        # Set turn order to alive players
        self.set_turn_players(self.alive_players)

        self.play_sound(f"game_cards/shuffle{random.randint(1, 3)}.ogg")  # nosec B311
        self.broadcast_l("ninetynine-round", round=self.round)

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        # Check if player has cards
        if not player.hand:
            self._player_out_of_cards(player)
            return

        # Announce turn
        self.broadcast_l("ninetynine-player-turn", player=player.name)

        # RS Games: Check if player has any safe cards
        if not self.is_quentin_c and not self._has_safe_card(player):
            self._rs_games_no_safe_cards(player)
            return

        # Set up bot thinking
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))  # nosec B311

        self._update_all_turn_actions()
        self.rebuild_all_menus()

    def _has_safe_card(self, player: NinetyNinePlayer) -> bool:
        """Check if player has any card that won't make them go over 99 (RS Games)."""
        for card in player.hand:
            if card.rank == RS_RANK_NINETY_NINE:
                return True

            value = self.calculate_card_value(card, self.count)
            if value is not None:
                new_count = self.count + value
                if new_count <= MAX_COUNT:
                    return True

        return False

    def _rs_games_no_safe_cards(self, player: NinetyNinePlayer) -> None:
        """Handle RS Games auto-lose when player has no safe cards."""
        self.broadcast_l("ninetynine-no-valid-cards", player=player.name)

        self._play_sound_for_player(player, "game_ninetynine/lose2.ogg", "game_pig/win.ogg")

        player.tokens = max(0, player.tokens - PENALTY_BUST_RS)
        self._announce_token_loss(player, PENALTY_BUST_RS)

        if player.tokens <= 0:
            self._eliminate_player(player)

        self._check_game_end()
        if self.game_active:
            self._start_round()

    def _advance_turn(self) -> None:
        """Advance to the next player's turn."""
        if not self.alive_players:
            return

        # Handle skip using base class mechanism
        while self.turn_skip_count > 0:
            self.turn_skip_count -= 1
            self.turn_index = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
            skipped = self.current_player
            if skipped:
                self.on_player_skipped(skipped)

        # Move to next player
        self.turn_index = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)

        # Make sure current player is still alive
        attempts = 0
        while attempts < len(self.turn_player_ids):
            player = self.current_player
            if player and player.tokens > 0:
                break
            self.turn_index = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
            attempts += 1

        BotHelper.jolt_bots(self, ticks=random.randint(15, 25))  # nosec B311
        self._start_turn()

    def _draw_card(self) -> Card | None:
        """Draw a card, reshuffling if needed (silently like v10)."""
        if self.deck.is_empty():
            if not self.discard_pile:
                return None
            # Reshuffle discard pile into deck
            self.deck.cards = self.discard_pile[:]
            self.discard_pile = []
            self.deck.shuffle()

        return self.deck.draw_one()

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_play_card(self, player: Player, *args) -> None:
        """Handle playing a card, or announce it if not playable.

        Can be called as:
        - _action_play_card(player, action_id) - no input
        - _action_play_card(player, input_value, action_id) - with menu input
        """
        if not isinstance(player, NinetyNinePlayer):
            return

        action_id, input_value = self._parse_play_args(args)
        if action_id is None:
            return

        slot = self._parse_card_slot(action_id)
        if slot is None:
            return

        if slot < 0 or slot >= len(player.hand):
            return

        card = player.hand[slot]
        user = self.get_user(player)
        locale = user.locale if user else "en"

        if not self._validate_card_play_turn(player, user):
            return

        old_count = self.count

        handled = self._apply_menu_choice_value(player, slot, card, old_count, input_value, locale)
        if handled:
            return

        new_count = self._calculate_new_count(card, old_count)
        if new_count is None:
            return
        self._play_card(player, slot, card, new_count)

    @staticmethod
    def _parse_play_args(args) -> tuple[str | None, str | None]:
        if len(args) == 1:
            return args[0], None
        if len(args) == 2:
            return args[1], args[0]
        return None, None

    @staticmethod
    def _parse_card_slot(action_id: str) -> int | None:
        try:
            return int(action_id.split("_")[-1]) - 1
        except (ValueError, IndexError):
            return None

    def _validate_card_play_turn(self, player: NinetyNinePlayer, user) -> bool:
        if self.current_player != player:
            if user:
                user.speak_l("action-not-your-turn")
            return False
        if player.draw_timeout_ticks > 0:
            if user:
                user.speak_l("ninetynine-draw-first")
            return False
        return True

    def _apply_menu_choice_value(
        self,
        player: NinetyNinePlayer,
        slot: int,
        card: Card,
        old_count: int,
        input_value: str | None,
        locale: str,
    ) -> bool:
        if input_value is None:
            return False
        if card.rank == 1:
            add_eleven = Localization.get(locale, "ninetynine-ace-add-eleven")
            value = 11 if input_value == add_eleven else 1
        elif card.rank == 10:
            add_ten = Localization.get(locale, "ninetynine-ten-add")
            value = 10 if input_value == add_ten else -10
        else:
            return True
        self._play_card(player, slot, card, old_count + value)
        return True

    def _calculate_new_count(self, card: Card, old_count: int) -> int | None:
        value = self.calculate_card_value(card, old_count)

        if card.rank == 2 and self.is_quentin_c:
            return self.calculate_two_effect(old_count)

        if card.rank == RS_RANK_NINETY_NINE and not self.is_quentin_c:
            return MAX_COUNT

        if value is None:
            value = 0
        return old_count + value

    def _play_card(
        self,
        player: NinetyNinePlayer,
        slot: int,
        card: Card,
        new_count: int,
    ) -> None:
        """Play a card with the calculated new count."""
        old_count = self.count
        value = new_count - old_count

        # Remove card from hand
        player.hand.pop(slot)
        self.discard_pile.append(card)

        # Play card sound
        self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg", 70)  # nosec B311

        # Announce the play
        self.broadcast_personal_l(
            player,
            "ninetynine-you-play",
            "ninetynine-player-plays",
            card=card_name_with_article(card),
            count=new_count,
        )

        # Update count
        self.count = new_count

        # Check milestones and handle effects
        round_ended = self._check_milestones(player, old_count, new_count, value, card.rank)

        # Always check if game should end (someone may have been eliminated)
        self._check_game_end()
        if not self.game_active:
            return

        if round_ended:
            self._start_round()
            return

        # Apply special card effects (reverse, skip)
        self._apply_special_effects(player, card)

        # Handle card drawing
        if self.options.autodraw:
            drawn = self._draw_card()
            if drawn:
                player.hand.append(drawn)
                self._sort_hand(player)
            self._update_all_turn_actions()
            self._advance_turn()
        else:
            # Manual draw mode - set per-player timeout
            # Bots draw after a short delay; humans get the full window
            if player.is_bot:
                player.draw_timeout_ticks = random.randint(15, 30)  # nosec B311
            else:
                player.draw_timeout_ticks = DRAW_TIMEOUT_TICKS
            self._advance_turn()
            self._update_all_turn_actions()
            self.rebuild_all_menus()

    def _check_milestones(
        self,
        player: NinetyNinePlayer,
        old_count: int,
        new_count: int,
        value: int,
        card_rank: int,
    ) -> bool:
        """
        Check for milestones (33, 66, 99) and apply penalties.
        Returns True if round should end.
        """
        # Check for going over 99
        if new_count > MAX_COUNT:
            self._player_busts(player)
            return True

        # Landing on 99
        if new_count == MAX_COUNT:
            if self.is_quentin_c and value > 0:
                self._others_lose_tokens(player, PENALTY_MILESTONE_99, "99")
                return True

        # Only check 33/66 milestones in Quentin C with positive value
        if self.is_quentin_c and value > 0:
            passed_33 = old_count < MILESTONE_33 < new_count
            landed_33 = new_count == MILESTONE_33
            passed_66 = old_count < MILESTONE_66 < new_count
            landed_66 = new_count == MILESTONE_66

            if landed_33:
                self._others_lose_tokens(player, PENALTY_MILESTONE_33_66, "33")
            elif passed_33:
                self._player_loses_tokens(player, PENALTY_MILESTONE_PASS, "passed_33")

            if landed_66:
                self._others_lose_tokens(player, PENALTY_MILESTONE_33_66, "66")
            elif passed_66:
                self._player_loses_tokens(player, PENALTY_MILESTONE_PASS, "passed_66")

        return False

    def _others_lose_tokens(self, player: NinetyNinePlayer, amount: int, milestone: str) -> None:
        """All other players lose tokens (milestone bonus for player)."""
        others = [p for p in self.alive_players if p != player]

        if milestone == "99":
            self._play_sound_for_player(player, "game_pig/win.ogg", "game_ninetynine/lose2.ogg")
        else:
            self._play_sound_for_player(
                player, "game_ninetynine/lose1_you.ogg", "game_ninetynine/lose1_other.ogg"
            )

        for other in others:
            other.tokens = max(0, other.tokens - amount)
            self._announce_token_loss(other, amount)

            if other.tokens <= 0:
                self._eliminate_player(other)

    def _player_loses_tokens(self, player: NinetyNinePlayer, amount: int, reason: str) -> None:
        """Player loses tokens (passing through milestone or busting)."""
        self._play_sound_for_player(
            player, "game_ninetynine/lose1_other.ogg", "game_ninetynine/lose1_you.ogg"
        )

        player.tokens = max(0, player.tokens - amount)
        self._announce_token_loss(player, amount)

        if player.tokens <= 0:
            self._eliminate_player(player)

    def _player_busts(self, player: NinetyNinePlayer) -> None:
        """Player went over 99."""
        self._play_sound_for_player(player, "game_ninetynine/lose2.ogg", "game_pig/win.ogg")

        amount = PENALTY_BUST if self.is_quentin_c else PENALTY_BUST_RS
        player.tokens = max(0, player.tokens - amount)
        self._announce_token_loss(player, amount)

        if player.tokens <= 0:
            self._eliminate_player(player)

    def _player_out_of_cards(self, player: NinetyNinePlayer) -> None:
        """Player has no cards on their turn."""
        self._play_sound_for_player(player, "game_ninetynine/lose2.ogg", "game_pig/win.ogg")

        player.tokens = max(0, player.tokens - PENALTY_NO_CARDS)
        self._announce_token_loss(player, PENALTY_NO_CARDS)

        if player.tokens <= 0:
            self._eliminate_player(player)

        self._check_game_end()
        if self.game_active:
            self._start_round()

    def _announce_token_loss(self, player: NinetyNinePlayer, amount: int) -> None:
        """Announce token loss."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            if listener == player:
                user.speak_l("ninetynine-you-lose-tokens", amount=amount, buffer="table")
            else:
                user.speak_l(
                    "ninetynine-player-loses-tokens",
                    player=player.name,
                    amount=amount,
                    buffer="table",
                )
        self._sync_team_scores()

    def _sync_team_scores(self) -> None:
        """Mirror player tokens into TeamManager totals for scoreboard output."""
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.players:
            team = self._team_manager.get_team(p.name)
            if team:
                team.total_score = p.tokens

    def _eliminate_player(self, player: NinetyNinePlayer) -> None:
        """Eliminate a player from the game."""
        self.broadcast_l("ninetynine-player-eliminated", player=player.name)

        if player.id in self.alive_player_ids:
            self.alive_player_ids.remove(player.id)

    def _apply_special_effects(self, player: NinetyNinePlayer, card: Card) -> None:
        """Apply special card effects (reverse, skip)."""
        rank = card.rank

        if self.is_quentin_c:
            if rank == 4 and len(self.alive_players) > 2:
                self.reverse_turn_direction()
                self.broadcast_l("ninetynine-direction-reverses")
            if rank == 11:  # Jack skips
                self.skip_next_players(1)
        else:
            if rank == RS_RANK_REVERSE and len(self.alive_players) > 2:
                self.reverse_turn_direction()
                self.broadcast_l("ninetynine-direction-reverses")
            if rank == RS_RANK_SKIP:
                self.skip_next_players(1)

    def _check_game_end(self) -> None:
        """Check if the game should end."""
        alive = [p for p in self.get_active_players() if p.tokens > 0]

        if len(alive) <= 1:
            self._end_game(alive[0] if alive else None)

    def _end_game(self, winner: NinetyNinePlayer | None) -> None:
        """End the game with a winner."""
        self.play_sound("game_pig/win.ogg")

        if winner:
            self.broadcast_l("ninetynine-player-wins", player=winner.name)

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with NinetyNine-specific data."""
        sorted_players = sorted(self.get_active_players(), key=lambda p: p.tokens, reverse=True)

        # Build final tokens
        final_tokens = {}
        for p in sorted_players:
            nn_p: NinetyNinePlayer = p  # type: ignore
            final_tokens[p.name] = nn_p.tokens

        winner = sorted_players[0] if sorted_players else None
        winner_nn: NinetyNinePlayer = winner  # type: ignore

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
                "winner_name": winner.name if winner else None,
                "winner_tokens": winner_nn.tokens if winner_nn else 0,
                "final_tokens": final_tokens,
                "rounds_played": self.round,
                "starting_tokens": self.options.starting_tokens,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for NinetyNine game."""
        from ...messages.localization import Localization

        lines = [Localization.get(locale, "game-final-scores")]

        final_tokens = result.custom_data.get("final_tokens", {})
        for i, (name, tokens) in enumerate(final_tokens.items(), 1):
            lines.append(f"{i}. {name}: {tokens} tokens")

        return lines

    def _action_draw_card(self, player: Player, action_id: str) -> None:
        """Handle manual card draw."""
        if not isinstance(player, NinetyNinePlayer):
            return

        # Note: We don't guard on draw_timeout_ticks here because:
        # - For humans: the draw action is only added to menu when timeout > 0
        # - For bots: on_tick calls this when timeout reaches 0 (countdown expired)
        # The callers are responsible for ensuring the draw is valid.

        drawn = self._draw_card()
        if drawn:
            player.hand.append(drawn)
            self._sort_hand(player)

            self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")  # nosec B311

            user = self.get_user(player)
            if user:
                user.speak_l("ninetynine-you-draw", card=card_name_with_article(drawn))
            # Announce to others that this player drew a card
            self.broadcast_l(
                "ninetynine-player-draws",
                exclude=player,
                player=player.name,
            )

        player.draw_timeout_ticks = 0
        self._update_all_turn_actions()
        self.rebuild_all_menus()

    def _action_check_count(self, player: Player, action_id: str) -> None:
        """Announce the current count."""
        user = self.get_user(player)
        if user:
            user.speak_l("ninetynine-current-count", count=self.count)

    def _action_check_hand(self, player: Player, action_id: str) -> None:
        """Announce the player's hand."""
        if not isinstance(player, NinetyNinePlayer):
            return
        user = self.get_user(player)
        if not user:
            return

        if not player.hand:
            user.speak_l("ninetynine-hand-empty")
            return

        locale = user.locale
        card_names = [card_name(card, locale) for card in player.hand]
        user.speak_l("ninetynine-hand-cards", cards=", ".join(card_names))

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()

        if not self.game_active:
            return

        # Handle per-player pending draws
        for player in self.alive_players:
            if player.draw_timeout_ticks <= 0:
                continue

            player.draw_timeout_ticks -= 1

            if player.is_bot:
                # Bots draw after a short delay (don't wait for their turn)
                if player.draw_timeout_ticks <= 0:
                    self._action_draw_card(player, "draw_card")
                    if not self.game_active:
                        return
                continue

            if player.draw_timeout_ticks <= 0:
                # Human timeout expired without drawing
                if len(player.hand) == 0:
                    self._player_out_of_cards(player)
                    if not self.game_active:
                        return
                else:
                    self._update_turn_actions(player)
                    self.rebuild_player_menu(player)

        BotHelper.on_tick(self)

    def bot_think(self, player: NinetyNinePlayer) -> str | None:
        """Bot AI decision making - delegates to bot module."""
        return _bot_think(self, player)
