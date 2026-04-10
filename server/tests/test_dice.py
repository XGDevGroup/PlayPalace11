"""Tests for DiceSet with set-based kept/locked."""
import json

from server.game_utils.dice import DiceSet


class TestDiceSetBasics:
    def test_creation(self):
        ds = DiceSet()
        assert ds.num_dice == 5
        assert ds.kept == set()
        assert ds.locked == set()

    def test_roll(self):
        ds = DiceSet()
        values = ds.roll()
        assert len(values) == 5
        assert all(1 <= v <= 6 for v in values)

    def test_reset(self):
        ds = DiceSet()
        ds.roll()
        ds.keep(0)
        ds.reset()
        assert ds.kept == set()
        assert ds.locked == set()
        assert ds.values == []


class TestDiceSetKeepLock:
    def test_keep_adds_to_set(self):
        ds = DiceSet()
        ds.roll()
        ds.keep(0)
        assert 0 in ds.kept
        # Keeping again is idempotent (set semantics)
        ds.keep(0)
        assert ds.kept == {0}

    def test_unkeep(self):
        ds = DiceSet()
        ds.roll()
        ds.keep(0)
        ds.unkeep(0)
        assert 0 not in ds.kept

    def test_toggle_keep(self):
        ds = DiceSet()
        ds.roll()
        result = ds.toggle_keep(0)
        assert result is True
        assert 0 in ds.kept
        result = ds.toggle_keep(0)
        assert result is False
        assert 0 not in ds.kept

    def test_locked_die_cannot_be_kept(self):
        ds = DiceSet()
        ds.roll()
        ds.keep(0)
        ds.roll()  # locks die 0 (lock_kept=True by default)
        assert 0 in ds.locked
        assert ds.keep(0) is False

    def test_locked_die_toggle_returns_none(self):
        ds = DiceSet()
        ds.roll()
        ds.keep(0)
        ds.roll()
        assert ds.toggle_keep(0) is None

    def test_no_duplicates(self):
        ds = DiceSet()
        ds.roll()
        ds.keep(0)
        ds.keep(0)
        ds.keep(0)
        assert ds.kept == {0}


class TestDiceSetSerialization:
    def test_to_dict_sorted(self):
        ds = DiceSet()
        ds.roll()
        ds.keep(3)
        ds.keep(1)
        d = ds.to_dict()
        assert d["kept"] == [1, 3]  # sorted
        assert d["locked"] == []

    def test_from_dict(self):
        d = {"num_dice": 5, "sides": 6, "values": [1, 2, 3, 4, 5], "kept": [0, 2], "locked": [4]}
        ds = DiceSet.from_dict(d)
        assert ds.kept == {0, 2}
        assert ds.locked == {4}

    def test_json_round_trip(self):
        ds = DiceSet()
        ds.roll()
        ds.keep(0)
        ds.keep(2)
        json_str = ds.to_json()
        loaded = DiceSet.from_json(json_str)
        assert loaded.kept == ds.kept
        assert loaded.locked == ds.locked
        assert loaded.values == ds.values
