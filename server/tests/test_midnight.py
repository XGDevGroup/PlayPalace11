"""
Tests for the 1-4-24 (Midnight) game.

Following the testing strategy:
- Unit tests for individual functions
- Play tests that run the game from start to finish with bots
- Persistence tests (save/reload at each tick)
"""

import pytest
import random
import json

from server.games.midnight.game import MidnightGame, MidnightOptions
from server.core.users.test_user import MockUser
from server.core.users.bot import Bot


def _play_human_turn(game: MidnightGame, player) -> None:
    """Execute a simple human turn strategy."""
    if not player.dice.has_rolled:
        game.execute_action(player, "roll")
        return
    if player.dice.kept_unlocked_count > 0:
        game.execute_action(player, "roll")
        return

    locked_values = [player.dice.values[i] for i in player.dice.locked]
    action = (
        _find_keep_action(player.dice, locked_values, 1)
        or _find_keep_action(player.dice, locked_values, 4)
        or _find_keep_highest_action(player.dice)
    )
    game.execute_action(player, action or "bank")


def _find_keep_action(dice, locked_values, target_value: int) -> str | None:
    """Find the action to keep a specific die value."""
    if target_value in locked_values:
        return None
    for i in range(6):
        if not dice.is_locked(i) and dice.values[i] == target_value:
            return f"toggle_die_{i}"
    return None


def _find_keep_highest_action(dice) -> str | None:
    """Find the action to keep the highest available die."""
    best_i = -1
    best_v = 0
    for i in range(6):
        if dice.is_locked(i) or dice.is_kept(i):
            continue
        if dice.values[i] > best_v:
            best_v = dice.values[i]
            best_i = i
    if best_i >= 0:
        return f"toggle_die_{best_i}"
    return None


class TestMidnightGameUnit:
    """Unit tests for Midnight game functions."""

    def test_game_creation(self):
        """Test creating a new Midnight game."""
        game = MidnightGame()
        assert game.get_name() == "1-4-24"
        assert game.get_type() == "midnight"
        assert game.get_category() == "category-dice-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 6

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = MidnightGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.round_score == 0
        assert player.round_wins == 0
        assert player.qualified is False
        assert player.dice.num_dice == 6
        assert player.dice.sides == 6
        assert player.is_bot is False

    def test_options_defaults(self):
        """Test default game options."""
        game = MidnightGame()
        assert game.options.rounds == 5

    def test_custom_options(self):
        """Test custom game options."""
        options = MidnightOptions(rounds=10)
        game = MidnightGame(options=options)
        assert game.options.rounds == 10

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = MidnightGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        game.players[0].round_score = 20
        game.players[0].round_wins = 2
        game.players[0].qualified = True
        game.players[0].dice.values = [1, 2, 3, 4, 5, 6]
        game.players[0].dice.locked = {0, 3}
        game.round = 3

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["round"] == 3
        assert len(data["players"]) == 2
        assert data["players"][0]["round_score"] == 20
        assert data["players"][0]["round_wins"] == 2
        assert data["players"][0]["qualified"] is True
        assert data["players"][0]["dice"]["values"] == [1, 2, 3, 4, 5, 6]
        assert data["players"][0]["dice"]["locked"] == [0, 3]

        # Deserialize
        loaded_game = MidnightGame.from_json(json_str)
        assert loaded_game.round == 3
        assert loaded_game.players[0].round_score == 20
        assert loaded_game.players[0].round_wins == 2
        assert loaded_game.players[0].qualified is True
        assert loaded_game.players[0].dice.values == [1, 2, 3, 4, 5, 6]
        assert loaded_game.players[0].dice.locked == {0, 3}


class TestMidnightGameActions:
    """Test individual game actions."""

    def setup_method(self):
        """Set up a game with two players for each test."""
        self.game = MidnightGame()
        self.user1 = MockUser("Alice")
        self.user2 = MockUser("Bob")
        self.player1 = self.game.add_player("Alice", self.user1)
        self.player2 = self.game.add_player("Bob", self.user2)
        self.game.on_start()
        self.game.reset_turn_order()

    def test_roll_initial(self):
        """Test rolling all 6 dice initially."""
        random.seed(42)

        assert not self.player1.dice.has_rolled
        self.game.execute_action(self.player1, "roll")

        assert self.player1.dice.has_rolled
        assert len(self.player1.dice.values) == 6
        assert all(1 <= v <= 6 for v in self.player1.dice.values)

    def test_keep_die(self):
        """Test keeping a die."""
        random.seed(42)
        self.game.execute_action(self.player1, "roll")

        # Keep first die
        initial_value = self.player1.dice.values[0]
        self.game.execute_action(self.player1, "toggle_die_0")

        assert 0 in self.player1.dice.kept
        assert self.player1.dice.values[0] == initial_value

    def test_unkeep_die(self):
        """Test unkeeping a kept die."""
        random.seed(42)
        self.game.execute_action(self.player1, "roll")

        # Keep first die
        self.game.execute_action(self.player1, "toggle_die_0")
        assert 0 in self.player1.dice.kept

        # Unkeep it
        self.game.execute_action(self.player1, "toggle_die_0")
        assert 0 not in self.player1.dice.kept

    def test_lock_kept_dice_on_roll(self):
        """Test that kept dice become locked on next roll."""
        random.seed(42)
        self.game.execute_action(self.player1, "roll")

        # Keep first die
        self.game.execute_action(self.player1, "toggle_die_0")
        assert 0 in self.player1.dice.kept
        assert 0 not in self.player1.dice.locked

        # Roll again - kept die should lock
        self.game.execute_action(self.player1, "roll")
        assert 0 in self.player1.dice.locked
        # After clear_kept=True, kept list contains locked indices
        assert 0 in self.player1.dice.kept

    def test_stop_action_ends_turn(self):
        """Test that bank action evaluates and ends turn."""
        random.seed(100)
        self.game.execute_action(self.player1, "roll")

        # Keep all dice by toggling them
        for i in range(6):
            self.game.execute_action(self.player1, f"toggle_die_{i}")

        # When all dice are kept, roll is hidden/disabled and bank ends turn.
        old_player = self.game.current_player
        self.game.execute_action(self.player1, "bank")

        # Turn should have ended due to banking
        assert self.game.current_player != old_player

    def test_qualification_with_1_and_4(self):
        """Test that having 1 and 4 qualifies the player."""
        # Manually set dice values to ensure we have 1 and 4
        self.player1.dice.values = [1, 4, 6, 6, 5, 3]
        self.player1.dice.locked = {0, 1, 2, 3, 4, 5}  # All locked

        self.game._score_turn(self.player1)

        assert self.player1.qualified is True
        # Score should be sum of other 4 dice: 6+6+5+3 = 20
        assert self.player1.round_score == 20

    def test_disqualification_without_1(self):
        """Test that not having 1 disqualifies."""
        self.player1.dice.values = [2, 4, 6, 6, 5, 3]
        self.player1.dice.locked = {0, 1, 2, 3, 4, 5}

        self.game._score_turn(self.player1)

        assert self.player1.qualified is False
        assert self.player1.round_score == 0

    def test_disqualification_without_4(self):
        """Test that not having 4 disqualifies."""
        self.player1.dice.values = [1, 2, 6, 6, 5, 3]
        self.player1.dice.locked = {0, 1, 2, 3, 4, 5}

        self.game._score_turn(self.player1)

        assert self.player1.qualified is False
        assert self.player1.round_score == 0

    def test_stop_hidden_before_roll(self):
        """Test that bank action is hidden before first roll."""
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "roll" in visible_ids
        assert "bank" not in visible_ids

    def test_stop_visible_after_roll(self):
        """Test that autobank triggers when rolling with 1 die left."""
        random.seed(42)
        self.game.execute_action(self.player1, "roll")

        # Keep and roll 5 times, locking 5 dice one at a time
        for i in range(5):
            # Find the first unlocked die
            for j in range(6):
                if not self.player1.dice.is_locked(j):
                    self.game.execute_action(self.player1, f"toggle_die_{j}")
                    break
            # After 5th keep, we have 1 die unlocked - rolling triggers autobank
            old_player = self.game.current_player
            self.game.execute_action(self.player1, "roll")
            if i == 4:  # After the 5th roll (6th total including first roll)
                # Turn should have ended due to autobank
                assert self.game.current_player != old_player
                return

        # Should not reach here
        assert False, "Autobank should have triggered"

    def test_dice_toggle_hidden_before_roll(self):
        """Test that dice toggle actions are hidden before first roll."""
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "toggle_die_0" not in visible_ids
        assert "toggle_die_1" not in visible_ids

    def test_dice_toggle_visible_after_roll(self):
        """Test that dice toggle actions are visible after roll."""
        random.seed(42)
        self.game.execute_action(self.player1, "roll")

        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        # At least some toggle actions should be visible (unlocked dice)
        toggle_actions = [id for id in visible_ids if id.startswith("toggle_die_")]
        assert len(toggle_actions) > 0

    def test_requires_turn(self):
        """Test that turn-required actions are only available on your turn."""
        p1_actions = self.game.get_all_enabled_actions(self.player1)
        p2_actions = self.game.get_all_enabled_actions(self.player2)

        p1_ids = [a.action.id for a in p1_actions]
        p2_ids = [a.action.id for a in p2_actions]

        assert "roll" in p1_ids
        assert "roll" not in p2_ids


class TestMidnightPlayTest:
    """
    Play tests that run complete games with bots.

    Following the testing strategy: games are ticked, saved and reloaded
    at each tick to verify persistence.
    """

    def test_two_player_game_completes(self):
        """Test that a 2-player game runs to completion."""
        random.seed(123)

        game = MidnightGame(options=MidnightOptions(rounds=2))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game with periodic save/reload to test persistence
        max_ticks = 2000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 50 ticks to verify persistence
            if tick % 50 == 0 and tick > 0:
                json_str = game.to_json()
                game = MidnightGame.from_json(json_str)
                game.attach_user("Bot1", bot1)
                game.attach_user("Bot2", bot2)
                game.rebuild_runtime_state()
                for player in game.players:
                    game.setup_player_actions(player)

            game.on_tick()

        assert not game.game_active, "Game should have ended"
        # At least one player should have won a round
        max_wins = max(p.round_wins for p in game.players)
        assert max_wins >= 1

    def test_four_player_game_completes(self):
        """Test that a 4-player game runs to completion."""
        random.seed(456)

        game = MidnightGame(options=MidnightOptions(rounds=2))
        bots = [Bot(f"Bot{i}") for i in range(1, 5)]
        for bot in bots:
            game.add_player(bot.username, bot)

        game.on_start()

        max_ticks = 3000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 100 ticks
            if tick % 100 == 0 and tick > 0:
                json_str = game.to_json()
                game = MidnightGame.from_json(json_str)
                for bot in bots:
                    game.attach_user(bot.username, bot)
                game.rebuild_runtime_state()
                for player in game.players:
                    game.setup_player_actions(player)

            game.on_tick()

        assert not game.game_active

    def test_human_and_bot_game(self):
        """Test a game with one human and one bot."""
        random.seed(789)

        game = MidnightGame(options=MidnightOptions(rounds=1))
        human = MockUser("Human")
        bot = Bot("Bot")
        game.add_player("Human", human)
        game.add_player("Bot", bot)

        game.on_start()

        max_ticks = 2000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            current = game.current_player
            if current and current.name == "Human":
                _play_human_turn(game, current)
            else:
                game.on_tick()

        assert not game.game_active

        # Check that we got game messages
        messages = human.get_spoken_messages()
        assert len(messages) > 0
        assert any("Round" in m for m in messages)

    def test_different_round_counts(self):
        """Test game with different round counts."""
        for rounds in [1, 3, 10]:
            random.seed(100 + rounds)

            game = MidnightGame(options=MidnightOptions(rounds=rounds))
            bot1 = Bot("Bot1")
            bot2 = Bot("Bot2")
            game.add_player("Bot1", bot1)
            game.add_player("Bot2", bot2)

            game.on_start()

            for _ in range(rounds * 1000 + 1000):
                if not game.game_active:
                    break
                game.on_tick()

            assert not game.game_active, f"Game with {rounds} rounds should complete"


class TestMidnightPersistence:
    """Specific tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that all game state is preserved through save/load."""
        game = MidnightGame(options=MidnightOptions(rounds=10))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Set various state
        game.round = 5
        game.turn_index = 1
        game.players[0].round_score = 18
        game.players[0].round_wins = 2
        game.players[0].qualified = True
        game.players[0].dice.values = [1, 4, 6, 5, 3, 2]
        game.players[0].dice.locked = {0, 1, 2}
        game.players[1].round_score = 0
        game.players[1].round_wins = 3
        game.players[1].qualified = False

        # Save
        json_str = game.to_json()

        # Load
        loaded = MidnightGame.from_json(json_str)

        # Verify all state
        assert loaded.game_active is True
        assert loaded.round == 5
        assert loaded.options.rounds == 10
        assert loaded.players[0].round_score == 18
        assert loaded.players[0].round_wins == 2
        assert loaded.players[0].qualified is True
        assert loaded.players[0].dice.values == [1, 4, 6, 5, 3, 2]
        assert loaded.players[0].dice.locked == {0, 1, 2}
        assert loaded.players[1].round_score == 0
        assert loaded.players[1].round_wins == 3
        assert loaded.players[1].qualified is False

    def test_actions_work_after_reload(self):
        """Test that actions work correctly after reloading."""
        game = MidnightGame()
        user = MockUser("Alice")
        bot = Bot("Bot")
        game.add_player("Alice", user)
        game.add_player("Bot", bot)
        game.on_start()

        # Do some actions
        game.execute_action(game.players[0], "roll")

        # Save and reload
        json_str = game.to_json()
        game = MidnightGame.from_json(json_str)
        game.attach_user("Alice", user)
        game.attach_user("Bot", bot)
        for player in game.players:
            game.setup_player_actions(player)

        # Actions should still work
        actions = game.get_all_enabled_actions(game.players[0])
        assert len(actions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
