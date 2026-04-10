from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import Optional

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from ...core.ui.keybinds import KeybindState
from ...game_utils.cards import (
    Card,
    Deck,
    SUIT_CLUBS,
    SUIT_DIAMONDS,
    SUIT_HEARTS,
    SUIT_SPADES,
)

from .player import NinePlayer
from .state import NineState, SequenceState


# Card Ranks for Nine: 6, 7, 8, 9, 10, J, Q, K, A
# Using standard ranks 1-13, but mapping 1 (Ace) to a higher internal value for comparison.
RANK_SIX = 6
RANK_SEVEN = 7
RANK_EIGHT = 8
RANK_NINE = 9
RANK_TEN = 10
RANK_JACK = 11
RANK_QUEEN = 12
RANK_KING = 13
RANK_ACE = 1  # Standard Ace rank

# Internal mapping for comparison (Ace is highest)
NINE_RANK_ORDER = {
    RANK_SIX: 6,
    RANK_SEVEN: 7,
    RANK_EIGHT: 8,
    RANK_NINE: 9,
    RANK_TEN: 10,
    RANK_JACK: 11,
    RANK_QUEEN: 12,
    RANK_KING: 13,
    RANK_ACE: 14,  # Ace is highest in Nine
}

# Ordered list of ranks for easy iteration and checking adjacency
NINE_RANKS_IN_ORDER = [
    RANK_SIX,
    RANK_SEVEN,
    RANK_EIGHT,
    RANK_NINE,
    RANK_TEN,
    RANK_JACK,
    RANK_QUEEN,
    RANK_KING,
    RANK_ACE,
]

# Map standard ranks to localization keys
NINE_RANK_KEYS = {
    RANK_SIX: "rank-six",
    RANK_SEVEN: "rank-seven",
    RANK_EIGHT: "rank-eight",
    RANK_NINE: "rank-nine",
    RANK_TEN: "rank-ten",
    RANK_JACK: "rank-jack",
    RANK_QUEEN: "rank-queen",
    RANK_KING: "rank-king",
    RANK_ACE: "rank-ace",
}

# Suit localization keys (from game_utils.cards)
SUIT_KEYS = {
    SUIT_DIAMONDS: "suit-diamonds",
    SUIT_CLUBS: "suit-clubs",
    SUIT_HEARTS: "suit-hearts",
    SUIT_SPADES: "suit-spades",
}


@dataclass
@register_game
class NineGame(Game):
    "nine-description"

    #    Nine - A card game where players form sequences.

    players: list[NinePlayer] = field(default_factory=list)
    nine_state: NineState = field(default_factory=NineState)

    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)

    # Game state variables
    game_active: bool = False
    first_turn_player_id: Optional[str] = None  # Player who has the nine of clubs

    def __post_init__(self):
        """Initialize runtime state."""
        super().__post_init__()

    def rebuild_runtime_state(self) -> None:
        """Rebuild non-serialized state after deserialization."""
        super().rebuild_runtime_state()

    @classmethod
    def get_name(cls) -> str:
        return "Nine"

    @classmethod
    def get_type(cls) -> str:
        return "nine"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> NinePlayer:
        """Create a new player."""
        return NinePlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Deck and Card Utilities
    # ==========================================================================

    def _build_nine_deck(self) -> Deck:
        """
        Create a 36-card deck for Nine (6s through Aces).
        """
        cards = []
        card_id_counter = 0
        for suit in [SUIT_CLUBS, SUIT_DIAMONDS, SUIT_HEARTS, SUIT_SPADES]:
            for rank in NINE_RANKS_IN_ORDER:
                card = Card(id=card_id_counter, rank=rank, suit=suit)
                cards.append(card)
                card_id_counter += 1
        return Deck(cards=cards)

    def _get_card_nine_value(self, card: Card) -> int:
        """Get the internal value of a card for Nine game logic (Ace is highest)."""
        return NINE_RANK_ORDER.get(card.rank, 0)  # Default to 0 for unknown ranks

    def _get_localized_rank_name(self, rank: int, locale: str = "en") -> str:
        """Get localized name for a card rank specific to Nine."""
        key = NINE_RANK_KEYS.get(rank)
        if key:
            return Localization.get(locale, key)
        return str(rank)  # Fallback to number if not found

    def _get_localized_suit_name(self, suit: int, locale: str = "en") -> str:
        """Get localized name for a card suit."""
        key = SUIT_KEYS.get(suit)
        if key:
            return Localization.get(locale, key)
        return str(suit)  # Fallback to number if not found

    def _get_localized_card_name(self, card: Card, locale: str = "en") -> str:
        """Get localized full card name (e.g., 'Nine of Clubs')."""
        rank_name = self._get_localized_rank_name(card.rank, locale)
        suit_name = self._get_localized_suit_name(card.suit, locale)
        return Localization.get(locale, "card-name", rank=rank_name, suit=suit_name)

    def _get_localized_check_sequences_label(self, player: Player, action_id: str) -> str:
        """Get localized label for the 'Check Sequences' action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "nine-action-check-sequences")

    def _sort_player_hand(self, hand: list[Card]) -> list[Card]:
        """Sorts a player's hand according to Nine's rules (rank ascending, then suit)."""
        # Sort by rank using NINE_RANK_ORDER for custom Ace value, then by suit
        return sorted(hand, key=lambda card: (self._get_card_nine_value(card), card.suit))

    def _draw_card(self, player: NinePlayer) -> Card | None:
        """Draw a card for a player."""
        if self.deck.is_empty():
            # In Nine, the game typically ends when deck is empty and players empty hands,
            # so no reshuffling of discard pile is needed.
            return None
        return self.deck.draw_one()

    def _broadcast_nine_message(
        self, message_key: str, sending_player: NinePlayer | None = None, **kwargs
    ) -> None:
        """Broadcasts a localized message to all players, personalizing 'you' vs 'player',
        with fallback for 'you' messages to 'player' messages if 'you' version is not defined."""
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue

            target_locale = user.locale

            final_message_key = f"nine-player-{message_key}"  # Default to player version

            if sending_player and p == sending_player:
                # Check if a specific "you" version exists for this message key
                you_version_key = f"nine-you-{message_key}"
                if Localization.get(target_locale, you_version_key, silent=True):
                    final_message_key = you_version_key

            # Make a mutable copy of kwargs for localization per recipient
            msg_kwargs = dict(kwargs)

            # Localize card object if present in kwargs before speaking
            if "card" in msg_kwargs and isinstance(msg_kwargs["card"], Card):
                msg_kwargs["card"] = self._get_localized_card_name(
                    msg_kwargs["card"], target_locale
                )

            # Localize suit if present in kwargs before speaking (expecting int suit ID)
            if "suit" in msg_kwargs and isinstance(msg_kwargs["suit"], int):
                msg_kwargs["suit"] = self._get_localized_suit_name(
                    msg_kwargs["suit"], target_locale
                )

            user.speak_l(final_message_key, **msg_kwargs)

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def prestart_validate(self) -> list[str]:
        """Validate game configuration before starting."""
        errors = super().prestart_validate()

        num_players = len(self.get_active_players())
        if num_players == 5:  # Only 5 players is specifically invalid for Nine
            errors.append(Localization.get("en", "nine-error-invalid-player-count"))

        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.nine_state = NineState()  # Reset game state for new game

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Build and shuffle deck
        self.deck = self._build_nine_deck()
        self.deck.shuffle()
        self.discard_pile = []

        # Deal hands and find who has the nine of clubs
        self._deal_initial_hands()
        self.first_turn_player_id = self._find_nine_of_clubs_player()

        if self.first_turn_player_id:
            # Set the current player to the one with the nine of clubs
            # Find the player object by ID
            first_player_obj = None
            for p in self.get_active_players():
                if p.id == self.first_turn_player_id:
                    first_player_obj = p
                    break

            if first_player_obj:
                self.current_player = first_player_obj
                self._broadcast_nine_message(
                    "start-player-announcement",
                    player=first_player_obj.name,
                    sending_player=first_player_obj,
                )
        else:
            # This should ideally not happen if deck is built correctly
            self.broadcast("Error: Nine of Clubs not found in any hand. Aborting game.")
            self.finish_game()
            return

        self.play_sound(
            random.choice(
                ["game_cards/shuffle1.ogg", "game_cards/shuffle2.ogg", "game_cards/shuffle3.ogg"]
            )
        )

        self._start_turn()

    def _deal_initial_hands(self) -> None:
        """Deal initial hands to all players based on player count."""
        active_players = self.get_active_players()
        num_players = len(active_players)
        cards_to_deal_per_player = 0

        if num_players == 2:
            cards_to_deal_per_player = 18
        elif num_players == 3:
            cards_to_deal_per_player = 12
        elif num_players == 4:
            cards_to_deal_per_player = 9
        elif num_players == 6:
            cards_to_deal_per_player = 6
        else:
            # Should be caught by prestart_validate
            return
        self._broadcast_nine_message("nine-deal", cards=cards_to_deal_per_player)

        for player in active_players:
            player.hand = []
            for _ in range(cards_to_deal_per_player):
                card = self._draw_card(player)
                if card:
                    player.hand.append(card)
            # Sort hand after dealing all cards
            player.hand = self._sort_player_hand(player.hand)

        self.play_sound(
            random.choice(
                [
                    "game_cards/draw1.ogg",
                    "game_cards/draw2.ogg",
                    "game_cards/draw3.ogg",
                    "game_cards/draw4.ogg",
                ]
            )
        )

    def _find_nine_of_clubs_player(self) -> Optional[str]:
        """Find the player who has the Nine of Clubs."""
        for player in self.get_active_players():
            for card in player.hand:
                if card.rank == RANK_NINE and card.suit == SUIT_CLUBS:
                    return player.id
        return None

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player or not isinstance(player, NinePlayer):
            return

        self.announce_turn()

        # Check for automatic skip
        if not self._has_valid_move(player):
            self._auto_skip_current_player_turn(player)
            return

        # Jolt bot to think about next play
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 50))

        self._update_all_turn_actions()
        self.rebuild_all_menus()

    def _auto_skip_current_player_turn(self, player: NinePlayer) -> None:
        """Execute the logic for automatically skipping a player's turn."""
        self._broadcast_nine_message("skips-turn", sending_player=player, player=player.name)
        # To do: Add skip sound.         self.play_sound("sound.ogg")
        self._end_turn()

    def _end_turn(self) -> None:
        """End current player's turn."""
        # Check for game winner
        winning_player_id = self._check_game_winner()
        if winning_player_id:
            self._end_game(winning_player_id)
            return

        # Advance to next player
        BotHelper.jolt_bots(self, ticks=random.randint(15, 25))
        self.advance_turn(announce=False)
        self._start_turn()

    def _check_game_winner(self) -> Optional[str]:
        """Check if any player has won the game (empty hand)."""
        for player in self.get_active_players():
            if not player.hand:
                return player.id
        return None

    def _end_game(self, winner_id: str) -> None:
        """End the game with a winner."""
        winner_obj = None
        for p in self.get_active_players():
            if p.id == winner_id:
                winner_obj = p
                break

        if winner_obj:
            self._broadcast_nine_message(
                "wins-game", sending_player=winner_obj, player=winner_obj.name
            )
            self._broadcast_nine_message("game-ended")

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Nine-specific data."""
        # Sort players by cards remaining (ascending)
        player_results = []
        for p in self.get_active_players():
            player_results.append(
                (p.id, p.name, len(p.hand), p.is_bot, getattr(p, "is_virtual_bot", False))
            )
        sorted_player_results = sorted(player_results, key=lambda x: x[2])  # Sort by cards left

        final_scores = {}
        for p_id, p_name, cards_left, _, _ in sorted_player_results:
            final_scores[p_name] = cards_left

        winner_name = sorted_player_results[0][1] if sorted_player_results else "N/A"

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p_id,
                    player_name=p_name,
                    is_bot=is_bot,
                    is_virtual_bot=is_virtual_bot,
                )
                for p_id, p_name, _, is_bot, is_virtual_bot in player_results
            ],
            custom_data={
                "winner_name": winner_name,
                "final_scores": final_scores,
                "rounds_played": 1,  # Nine is usually one round
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Nine game."""
        lines = [Localization.get(locale, "game-final-scores-header")]

        final_scores = result.custom_data.get("final_scores", {})
        winner_name = result.custom_data.get("winner_name")

        if not final_scores:
            return lines

        # Sort players by score (cards left) for a consistent display order
        sorted_players = sorted(final_scores.items(), key=lambda item: item[1])

        for name, cards_left in sorted_players:
            if name == winner_name:
                # Announce the winner by name
                lines.append(Localization.get(locale, "game-winner", player=name))
                lines.append(Localization.get(locale, "nine-final-score", score=cards_left))
            else:
                # Announce other players' scores
                lines.append(
                    Localization.get(locale, "game-eliminated", player=name, score=cards_left)
                )

        return lines

    # ==========================================================================
    # Action Sets and Keybinds
    # ==========================================================================

    def create_turn_action_set(self, player: NinePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        action_set = ActionSet(name="turn")

        # Actions for playing cards dynamically added based on hand
        # This will be updated by _update_card_actions
        return action_set

    def create_standard_action_set(self, player: NinePlayer) -> ActionSet:
        """Create the standard action set for Nine."""
        action_set = super().create_standard_action_set(player)

        # Add a custom status action
        action_set.add(
            Action(
                id="check_sequences_status",
                label="",
                handler="_action_check_sequences_status",
                is_enabled="_is_check_sequences_status_enabled",
                is_hidden="_is_check_sequences_status_hidden",
                get_label="_get_localized_check_sequences_label",  # Use get_label for dynamic localization
                show_in_actions_menu=True,  # Set to True to make visible in general menu
            )
        )

        action_set.add(
            Action(
                id="check_hand_counts_status",
                label="",
                handler="_action_check_hand_counts_status",
                is_enabled="_is_check_hand_counts_status_enabled",
                is_hidden="_is_check_hand_counts_status_hidden",
                get_label="_get_localized_check_hand_counts_label",
                show_in_actions_menu=True,
            )
        )

        # Reorder to put check_sequences_status first, then check_hand_counts_status
        if "check_sequences_status" in action_set._order:
            action_set._order.remove("check_sequences_status")
        action_set._order.insert(0, "check_sequences_status")

        if "check_hand_counts_status" in action_set._order:
            action_set._order.remove("check_hand_counts_status")
        action_set._order.insert(1, "check_hand_counts_status")

        # Hide generic score actions as they don't apply directly
        for action_id in ("check_scores", "check_scores_detailed"):
            existing = action_set.get_action(action_id)
            if existing:
                existing.show_in_actions_menu = False

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Remove unneeded 's' keybind
        if "s" in self._keybinds:
            self._keybinds["s"] = []

        # Custom keybind for status (check sequences)
        self.define_keybind(
            "c",
            Localization.get("en", "nine-action-check-sequences"),
            ["check_sequences_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Custom keybind for status (check hand counts)
        self.define_keybind(
            "e",
            Localization.get("en", "nine-action-check-hand-counts"),
            ["check_hand_counts_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _update_card_actions(self, player: NinePlayer) -> None:
        """Update card slot actions based on player's hand."""
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        # Clear existing card actions
        for i in range(1, len(player.hand) + 2):  # Account for potential new cards
            action_id = f"play_card_slot_{i}"
            if turn_set.get_action(action_id):
                turn_set.remove(action_id)
            if action_id in turn_set._order:
                turn_set._order.remove(action_id)

        # Add actions for cards in hand
        for i, card in enumerate(player.hand, 1):
            action_id = f"play_card_slot_{i}"

            # Check if card is playable
            is_playable, _ = self._can_play_card(player, card, check_only=True)

            turn_set.add(
                Action(
                    id=action_id,
                    label="",  # Dynamic label will be set
                    handler="_action_play_card",
                    is_enabled=(None if is_playable else "nine-reason-generic"),
                    is_hidden=Visibility.VISIBLE,
                    get_label="_get_card_slot_label",
                    show_in_actions_menu=False,
                )
            )

    def _get_card_slot_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for a card slot action."""
        if not isinstance(player, NinePlayer):
            return ""
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except (ValueError, IndexError):
            return ""
        if slot < 0 or slot >= len(player.hand):
            return ""
        card = player.hand[slot]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return self._get_localized_card_name(card, locale)

    def _update_turn_actions(self, player: NinePlayer) -> None:
        """Update dynamic card actions for a player."""
        self._update_card_actions(player)

    def _update_all_turn_actions(self) -> None:
        """Update card actions for all players."""
        for player in self.players:
            self._update_turn_actions(player)

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_check_sequences_status_enabled(self, player: Player) -> str | None:
        """Check if check sequences status action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_sequences_status_hidden(self, player: Player) -> Visibility:
        """Check sequences status is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_skip_turn_enabled(self, player: Player) -> str | None:
        """Skip turn action is never enabled for direct player interaction."""
        return "action-disabled"

    def _is_skip_turn_hidden(self, player: Player) -> Visibility:
        """Skip turn action is always hidden from the UI."""
        return Visibility.HIDDEN

    def _has_valid_move(self, player: NinePlayer) -> bool:
        """Check if the player has any valid moves."""
        for card in player.hand:
            if self._can_play_card(player, card, check_only=True)[0]:
                return True
        return False

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_check_sequences_status(self, player: Player, action_id: str) -> None:
        """Show game sequences status to player."""
        user = self.get_user(player)
        if not user:
            return

        locale = user.locale
        none_str = Localization.get(locale, "nine-none")
        lines = []

        # Only Sequences on the table
        for suit in [SUIT_CLUBS, SUIT_DIAMONDS, SUIT_HEARTS, SUIT_SPADES]:
            suit_name = self._get_localized_suit_name(suit, locale)
            sequence_state = self.nine_state.sequences.get(suit)
            if sequence_state and sequence_state.low_card and sequence_state.high_card:
                low_card_name = self._get_localized_rank_name(sequence_state.low_card.rank, locale)
                high_card_name = self._get_localized_rank_name(
                    sequence_state.high_card.rank, locale
                )
                sequence_str = f"{low_card_name} - {high_card_name}"
                lines.append(
                    Localization.get(
                        locale, "nine-status-sequence", suit=suit_name, sequence=sequence_str
                    )
                )
            else:
                lines.append(Localization.get(locale, "nine-status-no-sequence", suit=suit_name))

        self.status_box(player, lines)

    def _get_localized_check_hand_counts_label(self, player: Player, action_id: str) -> str:
        """Get localized label for the 'Check Hand Counts' action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "nine-action-check-hand-counts")

    def _is_check_hand_counts_status_enabled(self, player: Player) -> str | None:
        """Check if check hand counts action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hand_counts_status_hidden(self, player: Player) -> Visibility:
        """Check hand counts is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _action_check_hand_counts_status(self, player: Player, action_id: str) -> None:
        """Announce the number of cards in each player's hand to the player."""
        user = self.get_user(player)
        if not user:
            return

        locale = user.locale

        for p in self.get_active_players():
            user.speak_l("nine-status-player-hand-count", player=p.name, count=len(p.hand))

    def _action_skip_turn(self, player: Player, action_id: str) -> None:
        """Handle skipping a turn."""
        if not isinstance(player, NinePlayer):
            return

        # All checks should have happened before this point, if this action is still callable,
        # it means a player wants to skip when they legitimately have no moves.
        self._auto_skip_current_player_turn(player)

    def _action_play_card(self, player: Player, action_id: str) -> None:
        """Handle playing a card from hand."""
        if not isinstance(player, NinePlayer):
            return

        if self.current_player != player:
            user = self.get_user(player)
            if user:
                user.speak_l("nine-reason-not-your-turn")
            return

        # Extract slot number from action_id (e.g., "play_card_slot_1" -> 0)
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return

        if slot < 0 or slot >= len(player.hand):
            return

        card_to_play = player.hand[slot]

        can_play, reason = self._can_play_card(player, card_to_play)

        if can_play:
            self._play_card(player, slot, card_to_play)
        else:
            user = self.get_user(player)
            if user:
                card_name = self._get_localized_card_name(card_to_play, user.locale)
                user.speak_l(reason, card=card_name)  # reason contains localized message key

    # ==========================================================================
    # Card Play Logic
    # ==========================================================================

    def _can_play_card(
        self, player: NinePlayer, card: Card, check_only: bool = False
    ) -> tuple[bool, str]:
        """
        Check if a card can be played.
        Returns (bool, reason_message_key)
        """
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Rule 1: First card must be Nine of Clubs
        if not self.nine_state.nine_of_clubs_played:
            if not (card.rank == RANK_NINE and card.suit == SUIT_CLUBS):
                return False, Localization.get(locale, "nine-reason-must-play-nine-clubs")
            return True, ""  # Nine of Clubs is always playable as first card

        # Rule 2: Play any nine to start forming the sequence of that suit.
        if card.rank == RANK_NINE:
            if card.suit not in self.nine_state.sequences:
                return True, ""  # Can start a new sequence with this nine
            else:
                pass

        # Rule 3: Extend an already existing sequence.
        # Check if the suit has a sequence
        if card.suit in self.nine_state.sequences:
            sequence = self.nine_state.sequences[card.suit]
            if sequence.low_card and sequence.high_card:
                card_nine_value = self._get_card_nine_value(card)
                low_nine_value = self._get_card_nine_value(sequence.low_card)
                high_nine_value = self._get_card_nine_value(sequence.high_card)

                # Check if card is one lower than current low or one higher than current high

                is_one_lower = card_nine_value == low_nine_value - 1
                is_one_higher = card_nine_value == high_nine_value + 1
                if is_one_lower or is_one_higher:
                    return True, ""

        # If none of the above, it's not a valid move (unless skipping is an option)
        if not check_only:  # If this is a real play attempt, return reason
            # Determine a more specific reason if possible
            if not self._has_valid_move(player):
                return False, Localization.get(locale, "nine-reason-must-skip")
            elif card.rank == RANK_NINE and card.suit in self.nine_state.sequences:
                # Trying to play a nine, but sequence already exists, and it's not a direct extension
                return False, Localization.get(
                    locale,
                    "nine-reason-cannot-extend",
                    suit=self._get_localized_suit_name(card.suit, locale),
                )
            elif card.suit in self.nine_state.sequences:
                return False, Localization.get(
                    locale,
                    "nine-reason-cannot-extend",
                    suit=self._get_localized_suit_name(card.suit, locale),
                )
            else:
                return False, Localization.get(locale, "nine-reason-generic")
        return False, ""  # For check_only, if not playable, return False with empty reason

    def _play_card(self, player: NinePlayer, slot: int, card: Card) -> None:
        """Execute playing a card."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        player.hand.pop(slot)
        player.hand = self._sort_player_hand(player.hand)  # Sort hand after card is played

        if not self.nine_state.nine_of_clubs_played:
            # Must be Nine of Clubs
            self.nine_state.nine_of_clubs_played = True
            self.nine_state.sequences[card.suit] = SequenceState(low_card=card, high_card=card)
            self._broadcast_nine_message(
                "plays-nine-clubs", sending_player=player, player=player.name
            )
        elif card.rank == RANK_NINE:
            # Playing a nine to start a new sequence
            self.nine_state.sequences[card.suit] = SequenceState(low_card=card, high_card=card)
            self._broadcast_nine_message(
                "plays-nine-suit",
                sending_player=player,
                player=player.name,
                card=card,  # Pass raw Card object
                suit=card.suit,  # Pass raw suit integer
            )
        else:
            # Extending an existing sequence
            sequence = self.nine_state.sequences[card.suit]
            card_nine_value = self._get_card_nine_value(card)

            if (
                sequence.low_card
                and self._get_card_nine_value(sequence.low_card) == card_nine_value + 1
            ):
                sequence.low_card = card
            elif (
                sequence.high_card
                and self._get_card_nine_value(sequence.high_card) == card_nine_value - 1
            ):
                sequence.high_card = card

            self._broadcast_nine_message(
                "extend-sequence",
                sending_player=player,
                player=player.name,
                card=card,  # Pass raw Card object
                suit=card.suit,  # Pass raw suit integer
            )

        self.discard_pile.append(card)
        self.play_sound(
            random.choice(
                [
                    "game_cards/play1.ogg",
                    "game_cards/play2.ogg",
                    "game_cards/play3.ogg",
                    "game_cards/play4.ogg",
                ]
            )
        )
        self._end_turn()

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()

        if not self.game_active:
            return

        BotHelper.on_tick(self)

    def bot_think(self, player: NinePlayer) -> str | None:
        """Bot AI decision making."""
        if self.current_player != player:
            return None

        # Try to play Nine of Clubs if it's the first card
        if not self.nine_state.nine_of_clubs_played:
            for i, card in enumerate(player.hand):
                if card.rank == RANK_NINE and card.suit == SUIT_CLUBS:
                    return f"play_card_slot_{i + 1}"

        # Try to play a Nine to start a new sequence
        for i, card in enumerate(player.hand):
            if card.rank == RANK_NINE and card.suit not in self.nine_state.sequences:
                return f"play_card_slot_{i + 1}"

        # Try to extend an existing sequence
        for i, card in enumerate(player.hand):
            if card.suit in self.nine_state.sequences:
                sequence = self.nine_state.sequences[card.suit]
                card_nine_value = self._get_card_nine_value(card)

                if (
                    sequence.low_card
                    and self._get_card_nine_value(sequence.low_card) == card_nine_value + 1
                ):
                    return f"play_card_slot_{i + 1}"
                elif (
                    sequence.high_card
                    and self._get_card_nine_value(sequence.high_card) == card_nine_value - 1
                ):
                    return f"play_card_slot_{i + 1}"

        # If no valid moves, skip turn
        if not self._has_valid_move(player):
            return "skip_turn"

        return None  # No move decided, wait for next tick or user input
