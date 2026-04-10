"""Tests for GameCommunicationMixin broadcast correctness, exclude logic, locale resolution."""

from dataclasses import dataclass, field

from server.games.base import Player
from server.game_utils.game_communication_mixin import GameCommunicationMixin
from server.messages.localization import Localization


class StubUser:
    """Minimal user stub that records speak and speak_l calls."""

    def __init__(self, locale: str = "en"):
        self.locale = locale
        self.spoken: list[tuple[str, str]] = []
        self.spoken_l: list[tuple[str, str, dict]] = []

    def speak(self, text: str, buffer: str = "misc") -> None:
        self.spoken.append((text, buffer))

    def speak_l(self, message_id: str, buffer: str = "misc", **kwargs) -> None:
        self.spoken_l.append((message_id, buffer, kwargs))


class DummyGame(GameCommunicationMixin):
    """Minimal game stub that provides players and get_user."""

    def __init__(self):
        self.players: list[Player] = []
        self._users: dict[str, StubUser] = {}
        self.transcript: list[tuple[str, str, str]] = []

    def get_user(self, player: Player) -> StubUser | None:
        return self._users.get(player.id)

    def record_transcript_event(self, player: Player, text: str, buffer: str = "table") -> None:
        self.transcript.append((player.id, text, buffer))

    def add_player(self, player_id: str, name: str, locale: str = "en") -> tuple[Player, StubUser]:
        player = Player(id=player_id, name=name)
        user = StubUser(locale=locale)
        self.players.append(player)
        self._users[player_id] = user
        return player, user


class TestBroadcast:
    def test_broadcast_sends_to_all(self):
        game = DummyGame()
        _, u1 = game.add_player("p1", "Alice")
        _, u2 = game.add_player("p2", "Bob")
        game.broadcast("Hello everyone", buffer="table")
        assert ("Hello everyone", "table") in u1.spoken
        assert ("Hello everyone", "table") in u2.spoken

    def test_broadcast_exclude(self):
        game = DummyGame()
        p1, u1 = game.add_player("p1", "Alice")
        _, u2 = game.add_player("p2", "Bob")
        game.broadcast("Secret", buffer="table", exclude=p1)
        assert len(u1.spoken) == 0
        assert ("Secret", "table") in u2.spoken

    def test_broadcast_records_transcript(self):
        game = DummyGame()
        game.add_player("p1", "Alice")
        game.add_player("p2", "Bob")
        game.broadcast("Log this", buffer="table")
        assert len(game.transcript) == 2
        assert game.transcript[0] == ("p1", "Log this", "table")
        assert game.transcript[1] == ("p2", "Log this", "table")


class TestBroadcastL:
    def test_broadcast_l_sends_to_all(self):
        game = DummyGame()
        _, u1 = game.add_player("p1", "Alice")
        _, u2 = game.add_player("p2", "Bob")
        game.broadcast_l("pig-rolled", buffer="table", value=3)
        assert len(u1.spoken_l) == 1
        assert u1.spoken_l[0][0] == "pig-rolled"
        assert u1.spoken_l[0][2] == {"value": 3}
        assert len(u2.spoken_l) == 1

    def test_broadcast_l_exclude(self):
        game = DummyGame()
        p1, u1 = game.add_player("p1", "Alice")
        _, u2 = game.add_player("p2", "Bob")
        game.broadcast_l("pig-rolled", buffer="table", exclude=p1, value=3)
        assert len(u1.spoken_l) == 0
        assert len(u2.spoken_l) == 1


class TestBroadcastPersonalL:
    def test_personal_and_others_messages(self):
        game = DummyGame()
        p1, u1 = game.add_player("p1", "Alice")
        _, u2 = game.add_player("p2", "Bob")
        game.broadcast_personal_l(
            p1,
            personal_message_id="pig-you-rolled",
            others_message_id="pig-player-rolled",
            buffer="table",
            value=5,
        )
        # Player 1 gets the personal message
        assert len(u1.spoken_l) == 1
        assert u1.spoken_l[0][0] == "pig-you-rolled"
        assert u1.spoken_l[0][2] == {"value": 5}
        # Player 2 gets the others message with player kwarg injected
        assert len(u2.spoken_l) == 1
        assert u2.spoken_l[0][0] == "pig-player-rolled"
        assert u2.spoken_l[0][2] == {"player": "Alice", "value": 5}

    def test_personal_records_transcript_for_all(self):
        game = DummyGame()
        p1, _ = game.add_player("p1", "Alice")
        game.add_player("p2", "Bob")
        game.broadcast_personal_l(
            p1,
            personal_message_id="pig-you-rolled",
            others_message_id="pig-player-rolled",
            buffer="table",
            value=5,
        )
        # Both players should have transcript entries
        player_ids = [t[0] for t in game.transcript]
        assert "p1" in player_ids
        assert "p2" in player_ids

    def test_single_player_only_personal(self):
        game = DummyGame()
        p1, u1 = game.add_player("p1", "Alice")
        game.broadcast_personal_l(
            p1,
            personal_message_id="pig-you-rolled",
            others_message_id="pig-player-rolled",
            buffer="table",
            value=5,
        )
        assert len(u1.spoken_l) == 1
        assert u1.spoken_l[0][0] == "pig-you-rolled"


class TestLabelL:
    def test_label_l_returns_callable(self):
        game = DummyGame()
        p1, _ = game.add_player("p1", "Alice")
        label_fn = game.label_l("pig-roll")
        result = label_fn(game, p1)
        assert isinstance(result, str)
        assert len(result) > 0  # should resolve to something from Fluent

    def test_label_l_uses_player_locale(self):
        game = DummyGame()
        p1, u1 = game.add_player("p1", "Alice", locale="en")
        label_fn = game.label_l("pig-roll")
        result = label_fn(game, p1)
        # Should be the English string
        expected = Localization.get("en", "pig-roll")
        assert result == expected


class TestNoUserHandling:
    def test_broadcast_skips_none_user(self):
        game = DummyGame()
        p1 = Player(id="ghost", name="Ghost")
        game.players.append(p1)
        # No user registered for this player
        game.broadcast("Hello")  # should not raise

    def test_broadcast_l_defaults_locale_for_none_user(self):
        game = DummyGame()
        p1 = Player(id="ghost", name="Ghost")
        game.players.append(p1)
        # Should not raise; locale defaults to "en" when user is None
        game.broadcast_l("pig-rolled", buffer="table", value=3)
        # Transcript should still be recorded
        assert len(game.transcript) == 1
