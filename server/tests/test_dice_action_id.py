"""
Test that action_id parameter is passed correctly to is_enabled and is_hidden methods.

This verifies the enhancement to the action system that allows methods to optionally
receive the action_id as a keyword argument.
"""

import pytest

from server.games.threes.game import ThreesGame
from server.games.midnight.game import MidnightGame
from server.core.users.preferences import DiceKeepingStyle, UserPreferences
from server.core.users.test_user import MockUser


class PreferenceMockUser(MockUser):
    """Mock user with mutable preferences support."""

    def __init__(self, username: str):
        super().__init__(username)
        self._preferences = UserPreferences()

    @property
    def preferences(self) -> UserPreferences:
        return self._preferences


class TestActionIdPassing:
    """Test that action_id is passed to methods that accept it."""

    def test_threes_dice_toggle_with_5_dice(self):
        """Test Threes with 5 dice - all toggle actions should work."""
        game = ThreesGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()

        # Roll dice
        player.dice.roll()

        # Get all visible actions
        visible_actions = game.get_all_visible_actions(player)
        visible_ids = [a.action.id for a in visible_actions]

        # All 5 dice toggle actions should be visible
        assert "toggle_die_0" in visible_ids
        assert "toggle_die_1" in visible_ids
        assert "toggle_die_2" in visible_ids
        assert "toggle_die_3" in visible_ids
        assert "toggle_die_4" in visible_ids

        # All should be enabled (assuming more than 1 unlocked die)
        turn_set = game.get_action_set(player, "turn")
        resolved = turn_set.resolve_actions(game, player) if turn_set else []
        enabled_ids = [a.action.id for a in resolved if a.enabled]

        if player.dice.unlocked_count > 1:
            assert "toggle_die_0" in enabled_ids
            assert "toggle_die_1" in enabled_ids
            assert "toggle_die_2" in enabled_ids
            assert "toggle_die_3" in enabled_ids
            assert "toggle_die_4" in enabled_ids

    def test_midnight_dice_toggle_with_6_dice(self):
        """Test Midnight with 6 dice - all toggle actions should work."""
        game = MidnightGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()

        # Roll dice
        player.dice.roll()

        # Get all visible actions
        visible_actions = game.get_all_visible_actions(player)
        visible_ids = [a.action.id for a in visible_actions]

        # All 6 dice toggle actions should be visible
        assert "toggle_die_0" in visible_ids
        assert "toggle_die_1" in visible_ids
        assert "toggle_die_2" in visible_ids
        assert "toggle_die_3" in visible_ids
        assert "toggle_die_4" in visible_ids
        assert "toggle_die_5" in visible_ids  # This is the critical one

        # All should be enabled (no dice locked yet)
        turn_set = game.get_action_set(player, "turn")
        resolved = turn_set.resolve_actions(game, player) if turn_set else []
        enabled_ids = [a.action.id for a in resolved if a.enabled]

        assert "toggle_die_0" in enabled_ids
        assert "toggle_die_1" in enabled_ids
        assert "toggle_die_2" in enabled_ids
        assert "toggle_die_3" in enabled_ids
        assert "toggle_die_4" in enabled_ids
        assert "toggle_die_5" in enabled_ids

    def test_dice_toggles_hidden_before_roll(self):
        """Test that dice toggles are hidden before first roll."""
        game = MidnightGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()

        # Before roll
        visible_actions = game.get_all_visible_actions(player)
        visible_ids = [a.action.id for a in visible_actions]

        # No dice toggle actions should be visible
        assert "toggle_die_0" not in visible_ids
        assert "toggle_die_1" not in visible_ids
        assert "toggle_die_2" not in visible_ids
        assert "toggle_die_3" not in visible_ids
        assert "toggle_die_4" not in visible_ids
        assert "toggle_die_5" not in visible_ids

    def test_dice_toggle_index_extraction(self):
        """Test that die index is correctly extracted from action_id."""
        game = MidnightGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()

        # Roll dice
        player.dice.roll()
        original_values = player.dice.values.copy()

        # Keep die at index 2 using toggle_die_2 action
        game.execute_action(player, "toggle_die_2")

        # Die at index 2 should be kept
        assert 2 in player.dice.kept
        # Value should be preserved
        assert player.dice.values[2] == original_values[2]

    def test_backward_compatibility_without_action_id(self):
        """Test that methods without action_id parameter still work."""
        # This test verifies backward compatibility
        # Threes and Midnight both have _is_dice_toggle_enabled that doesn't use action_id
        # but the mixin delegate methods do use it

        game = ThreesGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()
        player.dice.roll()

        # These should work without errors
        visible = game.get_all_visible_actions(player)
        turn_set = game.get_action_set(player, "turn")
        enabled = turn_set.resolve_actions(game, player) if turn_set else []

        assert len(visible) > 0
        assert len(enabled) > 0

    def test_dice_values_mode_number_keeps_shift_rerolls(self):
        """Values mode: number keeps, shift+number rerolls."""
        game = ThreesGame()
        user = PreferenceMockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()
        user.preferences.dice_keeping_style = DiceKeepingStyle.QUENTIN_C

        player.dice.values = [1, 5, 2, 3, 6]
        player.dice.kept = set()
        player.dice.locked = set()

        game._handle_dice_key(player, 5)
        assert 1 in player.dice.kept

        game._handle_dice_unkeep(player, 5)
        assert 1 not in player.dice.kept

    def test_dice_values_mode_defaults_to_unkept_after_roll(self):
        """Values mode should not auto-keep all dice after rolling."""
        game = ThreesGame()
        user = PreferenceMockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()
        user.preferences.dice_keeping_style = DiceKeepingStyle.QUENTIN_C

        game.execute_action(player, "roll")
        assert player.dice.has_rolled
        assert player.dice.kept == set(player.dice.locked)

    def test_dice_values_mode_key_stays_enabled_when_first_die_locked(self):
        """Values mode key checks should not depend on die index 0."""
        game = ThreesGame()
        user = PreferenceMockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()
        user.preferences.dice_keeping_style = DiceKeepingStyle.QUENTIN_C

        # Die 0 is locked; only index 2 is an available 5.
        player.dice.values = [2, 3, 5, 4, 6]
        player.dice.locked = {0}
        player.dice.kept = {0}

        reason = game._is_dice_key_enabled(player, action_id="dice_key_5")
        assert reason is None

        game._handle_dice_key(player, 5)
        assert 2 in player.dice.kept


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
