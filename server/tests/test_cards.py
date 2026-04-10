"""Tests for card utilities and IntEnum types."""
import json

from server.game_utils.cards import (
    Suit, SpecialRank, Card, Deck, DeckFactory,
    SUIT_NONE, SUIT_DIAMONDS, SUIT_CLUBS, SUIT_HEARTS, SUIT_SPADES,
    RS_RANK_PLUS_10, RS_RANK_MINUS_10, RS_RANK_PASS,
    RS_RANK_REVERSE, RS_RANK_SKIP, RS_RANK_NINETY_NINE,
)


class TestSuitEnum:
    def test_int_values(self):
        assert Suit.NONE == 0
        assert Suit.DIAMONDS == 1
        assert Suit.CLUBS == 2
        assert Suit.HEARTS == 3
        assert Suit.SPADES == 4

    def test_arithmetic(self):
        assert Suit.DIAMONDS + 1 == 2
        assert Suit.SPADES - Suit.DIAMONDS == 3

    def test_backward_compat_aliases(self):
        assert SUIT_NONE == Suit.NONE
        assert SUIT_DIAMONDS == Suit.DIAMONDS
        assert SUIT_CLUBS == Suit.CLUBS
        assert SUIT_HEARTS == Suit.HEARTS
        assert SUIT_SPADES == Suit.SPADES

    def test_comparison_with_int(self):
        assert Suit.HEARTS == 3
        assert 4 == Suit.SPADES


class TestSpecialRankEnum:
    def test_int_values(self):
        assert SpecialRank.PLUS_10 == 14
        assert SpecialRank.NINETY_NINE == 19

    def test_backward_compat_aliases(self):
        assert RS_RANK_PLUS_10 == SpecialRank.PLUS_10
        assert RS_RANK_MINUS_10 == SpecialRank.MINUS_10
        assert RS_RANK_PASS == SpecialRank.PASS
        assert RS_RANK_REVERSE == SpecialRank.REVERSE
        assert RS_RANK_SKIP == SpecialRank.SKIP
        assert RS_RANK_NINETY_NINE == SpecialRank.NINETY_NINE


class TestCardSerialization:
    def test_card_round_trip(self):
        card = Card(id=0, rank=1, suit=Suit.DIAMONDS)
        data = json.loads(card.to_json())
        assert data["suit"] == 1
        loaded = Card.from_json(json.dumps(data))
        assert loaded.id == card.id
        assert loaded.rank == card.rank
        assert loaded.suit == card.suit

    def test_deck_round_trip(self):
        deck = Deck(cards=[Card(id=i, rank=i % 13 + 1, suit=i % 4 + 1) for i in range(52)])
        json_str = deck.to_json()
        loaded = Deck.from_json(json_str)
        assert len(loaded.cards) == 52
        assert loaded.cards[0].id == 0


class TestDeckFactory:
    def test_standard_52(self):
        deck, lookup = DeckFactory.standard_deck()
        assert len(deck.cards) == 52
        assert len(lookup) == 52

    def test_italian_40(self):
        deck, lookup = DeckFactory.italian_deck()
        assert len(deck.cards) == 40
        assert len(lookup) == 40

    def test_rs_games_60(self):
        deck, lookup = DeckFactory.rs_games_deck()
        assert len(deck.cards) == 60
        assert len(lookup) == 60
