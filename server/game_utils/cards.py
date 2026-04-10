"""
Reusable card and deck utilities for card games.

Provides Card, Deck, and DeckFactory classes that can be used by any card game.
"""

from dataclasses import dataclass, field
from enum import IntEnum
import random

from mashumaro.mixins.json import DataClassJSONMixin

from ..messages.localization import Localization


class Suit(IntEnum):
    """Card suit constants.

    IntEnum preserves arithmetic and comparison with bare ints.
    """

    NONE = 0
    DIAMONDS = 1
    CLUBS = 2
    HEARTS = 3
    SPADES = 4


class SpecialRank(IntEnum):
    """RS Games special card ranks (for Ninety-Nine RS Games variant)."""

    PLUS_10 = 14
    MINUS_10 = 15
    PASS = 16
    REVERSE = 17
    SKIP = 18
    NINETY_NINE = 19


# Backward-compatible aliases
SUIT_NONE = Suit.NONE
SUIT_DIAMONDS = Suit.DIAMONDS
SUIT_CLUBS = Suit.CLUBS
SUIT_HEARTS = Suit.HEARTS
SUIT_SPADES = Suit.SPADES

RS_RANK_PLUS_10 = SpecialRank.PLUS_10
RS_RANK_MINUS_10 = SpecialRank.MINUS_10
RS_RANK_PASS = SpecialRank.PASS
RS_RANK_REVERSE = SpecialRank.REVERSE
RS_RANK_SKIP = SpecialRank.SKIP
RS_RANK_NINETY_NINE = SpecialRank.NINETY_NINE


@dataclass
class Card(DataClassJSONMixin):
    """Playing card model.

    Attributes:
        id: Unique identifier.
        rank: Card rank (1-13 standard, 1-10 Italian, 14-19 RS Games special).
        suit: Suit number (0=none, 1=diamonds, 2=clubs, 3=hearts, 4=spades).
    """

    id: int  # Unique identifier
    rank: int  # Card rank (1-13 for standard, 1-10 for Italian, 14-19 for RS Games special)
    suit: int  # Suit number (0=none, 1=diamonds, 2=clubs, 3=hearts, 4=spades)

    def __hash__(self) -> int:
        """Hash cards by stable id for set/dict usage."""
        return self.id

    def __eq__(self, other: object) -> bool:
        """Compare cards by id equality."""
        if not isinstance(other, Card):
            return False
        return self.id == other.id


@dataclass
class Deck(DataClassJSONMixin):
    """Deck of cards with draw/shuffle operations.

    Attributes:
        cards: Ordered list of cards in the deck.
    """

    cards: list[Card] = field(default_factory=list)

    def shuffle(self) -> None:
        """Shuffle the deck in place."""
        random.shuffle(self.cards)

    def draw(self, count: int = 1) -> list[Card]:
        """Draw cards from the top of the deck."""
        drawn = self.cards[:count]
        self.cards = self.cards[count:]
        return drawn

    def draw_one(self) -> Card | None:
        """Draw a single card from the top of the deck."""
        if self.cards:
            return self.cards.pop(0)
        return None

    def add(self, cards: list[Card]) -> None:
        """Add cards to the bottom of the deck."""
        self.cards.extend(cards)

    def add_top(self, cards: list[Card]) -> None:
        """Add cards to the top of the deck."""
        self.cards = cards + self.cards

    def size(self) -> int:
        """Return the number of cards in the deck."""
        return len(self.cards)

    def is_empty(self) -> bool:
        """Check if the deck is empty."""
        return len(self.cards) == 0

    def clear(self) -> list[Card]:
        """Remove and return all cards from the deck."""
        cards = self.cards
        self.cards = []
        return cards


class DeckFactory:
    """Factory for creating common deck types."""

    @staticmethod
    def italian_deck(num_decks: int = 1) -> tuple[Deck, dict[int, Card]]:
        """
        Create Italian 40-card deck (4 suits x 10 ranks).

        Args:
            num_decks: Number of decks to combine.

        Returns:
            Tuple of (shuffled deck, card lookup dict mapping id -> Card)
        """
        cards = []
        card_lookup: dict[int, Card] = {}
        card_id = 0
        for _ in range(num_decks):
            for suit in range(1, 5):  # 1=diamonds, 2=clubs, 3=hearts, 4=spades
                for rank in range(1, 11):  # 1-10
                    card = Card(id=card_id, rank=rank, suit=suit)
                    cards.append(card)
                    card_lookup[card_id] = card
                    card_id += 1
        deck = Deck(cards=cards)
        deck.shuffle()
        return deck, card_lookup

    @staticmethod
    def standard_deck(num_decks: int = 1) -> tuple[Deck, dict[int, Card]]:
        """
        Create standard 52-card deck (4 suits x 13 ranks).

        Args:
            num_decks: Number of decks to combine.

        Returns:
            Tuple of (shuffled deck, card lookup dict mapping id -> Card)
        """
        cards = []
        card_lookup: dict[int, Card] = {}
        card_id = 0
        for _ in range(num_decks):
            for suit in range(1, 5):  # 1=diamonds, 2=clubs, 3=hearts, 4=spades
                for rank in range(1, 14):  # 1-13 (Ace through King)
                    card = Card(id=card_id, rank=rank, suit=suit)
                    cards.append(card)
                    card_lookup[card_id] = card
                    card_id += 1
        deck = Deck(cards=cards)
        deck.shuffle()
        return deck, card_lookup

    @staticmethod
    def rs_games_deck() -> tuple[Deck, dict[int, Card]]:
        """
        Create RS Games 60-card deck for Ninety-Nine variant.

        Contains:
        - Number cards 1-9: 4 of each (36 cards)
        - Special cards: +10, -10, Pass, Reverse, Skip, Ninety-Nine (4 of each, 24 cards)

        Returns:
            Tuple of (shuffled deck, card lookup dict mapping id -> Card)
        """
        cards = []
        card_lookup: dict[int, Card] = {}
        card_id = 0

        # Number cards 1-9 (4 of each = 36 cards)
        for rank in range(1, 10):
            for _ in range(4):
                card = Card(id=card_id, rank=rank, suit=SUIT_NONE)
                cards.append(card)
                card_lookup[card_id] = card
                card_id += 1

        # Special cards (4 of each = 24 cards)
        # 14=+10, 15=-10, 16=Pass, 17=Reverse, 18=Skip, 19=Ninety Nine
        for rank in [
            RS_RANK_PLUS_10,
            RS_RANK_MINUS_10,
            RS_RANK_PASS,
            RS_RANK_REVERSE,
            RS_RANK_SKIP,
            RS_RANK_NINETY_NINE,
        ]:
            for _ in range(4):
                card = Card(id=card_id, rank=rank, suit=SUIT_NONE)
                cards.append(card)
                card_lookup[card_id] = card
                card_id += 1

        deck = Deck(cards=cards)
        deck.shuffle()
        return deck, card_lookup


# Suit localization keys
SUIT_KEYS = {
    1: "suit-diamonds",
    2: "suit-clubs",
    3: "suit-hearts",
    4: "suit-spades",
}

# Rank localization keys (1-13 for standard decks)
RANK_KEYS = {
    1: "rank-ace",
    2: "rank-two",
    3: "rank-three",
    4: "rank-four",
    5: "rank-five",
    6: "rank-six",
    7: "rank-seven",
    8: "rank-eight",
    9: "rank-nine",
    10: "rank-ten",
    11: "rank-jack",
    12: "rank-queen",
    13: "rank-king",
}

# RS Games special card names (not localized - they're game-specific terms)
RS_GAMES_RANK_NAMES = {
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    RS_RANK_PLUS_10: "10",
    RS_RANK_MINUS_10: "-10",
    RS_RANK_PASS: "Pass",
    RS_RANK_REVERSE: "Reverse",
    RS_RANK_SKIP: "Skip",
    RS_RANK_NINETY_NINE: "Ninety Nine",
}


def card_name(card: Card, locale: str = "en") -> str:
    """
    Get localized card name (e.g., 'Seven of Diamonds').

    For RS Games cards (suit == SUIT_NONE), returns the special card name directly.

    Args:
        card: The card to name.
        locale: Locale for localization.

    Returns:
        Localized card name string.
    """
    # RS Games cards have no suit and use special naming
    if card.suit == SUIT_NONE:
        return RS_GAMES_RANK_NAMES.get(card.rank, str(card.rank))

    rank_key = RANK_KEYS.get(card.rank)
    suit_key = SUIT_KEYS.get(card.suit)

    rank_name = Localization.get(locale, rank_key) if rank_key else str(card.rank)
    suit_name = Localization.get(locale, suit_key) if suit_key else str(card.suit)

    return Localization.get(locale, "card-name", rank=rank_name, suit=suit_name)


def card_name_with_article(card: Card, locale: str = "en") -> str:
    """
    Get card name with article (a/an).

    Args:
        card: The card to name.
        locale: Locale for localization.

    Returns:
        Card name with appropriate article (e.g., 'an Ace of Hearts').
    """
    name = card_name(card, locale)
    # Words starting with vowel sounds use 'an' (8 sounds like "eight")
    if name[0].lower() in "aeiou8":
        return f"an {name}"
    return f"a {name}"


def card_name_short(card: Card) -> str:
    """
    Get short card name (e.g., '7D' for Seven of Diamonds).

    Args:
        card: The card to name.

    Returns:
        Short card name string.
    """
    # RS Games cards have no suit
    if card.suit == SUIT_NONE:
        return RS_GAMES_RANK_NAMES.get(card.rank, str(card.rank))

    suit_chars = {1: "D", 2: "C", 3: "H", 4: "S"}
    rank_chars = {1: "A", 11: "J", 12: "Q", 13: "K"}
    rank_str = rank_chars.get(card.rank, str(card.rank))
    suit_str = suit_chars.get(card.suit, "?")
    return f"{rank_str}{suit_str}"


def read_cards(cards: list[Card], locale: str = "en") -> str:
    """
    Format a list of cards for speech output.

    Args:
        cards: List of cards to read.
        locale: Locale for localization.

    Returns:
        Formatted string with card names joined by 'and'.
    """
    if not cards:
        return Localization.get(locale, "no-cards")
    names = [card_name(c, locale) for c in cards]
    return Localization.format_list_and(locale, names)


def sort_cards(cards: list[Card], by_suit: bool = True) -> list[Card]:
    """
    Sort cards by suit then rank, or by rank then suit.

    Args:
        cards: List of cards to sort.
        by_suit: If True, sort by suit first. Otherwise by rank first.

    Returns:
        New sorted list of cards.
    """
    if by_suit:
        return sorted(cards, key=lambda c: (c.suit, c.rank))
    else:
        return sorted(cards, key=lambda c: (c.rank, c.suit))
