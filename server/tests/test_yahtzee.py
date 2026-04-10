"""
Tests for the Yahtzee game.
"""

import json

from server.games.yahtzee.game import (
    YahtzeeGame,
    YahtzeePlayer,
    YahtzeeOptions,
    calculate_score,
    is_yahtzee,
    count_dice,
    ALL_CATEGORIES,
    UPPER_CATEGORIES,
    LOWER_CATEGORIES,
)
from server.core.users.test_user import MockUser
from server.core.users.bot import Bot


class TestYahtzeeScoring:
    """Unit tests for Yahtzee scoring functions."""

    def test_count_dice(self):
        """Test dice counting."""
        counts = count_dice([1, 1, 2, 3, 3])
        assert counts[1] == 2
        assert counts[2] == 1
        assert counts[3] == 2
        assert counts[4] == 0
        assert counts[5] == 0
        assert counts[6] == 0

    def test_is_yahtzee(self):
        """Test Yahtzee detection."""
        assert is_yahtzee([5, 5, 5, 5, 5]) is True
        assert is_yahtzee([1, 1, 1, 1, 1]) is True
        assert is_yahtzee([5, 5, 5, 5, 4]) is False
        assert is_yahtzee([1, 2, 3, 4, 5]) is False
        assert is_yahtzee([]) is False
        assert is_yahtzee([5, 5, 5, 5]) is False

    def test_upper_section_scoring(self):
        """Test upper section category scoring."""
        dice = [1, 1, 2, 3, 6]
        assert calculate_score(dice, "ones") == 2  # 1+1
        assert calculate_score(dice, "twos") == 2  # 2
        assert calculate_score(dice, "threes") == 3  # 3
        assert calculate_score(dice, "fours") == 0  # no 4s
        assert calculate_score(dice, "fives") == 0  # no 5s
        assert calculate_score(dice, "sixes") == 6  # 6

    def test_three_of_a_kind(self):
        """Test three of a kind scoring."""
        assert calculate_score([3, 3, 3, 1, 2], "three_kind") == 12  # sum all
        assert calculate_score([5, 5, 5, 5, 1], "three_kind") == 21  # 4 of a kind counts
        assert calculate_score([1, 2, 3, 4, 5], "three_kind") == 0  # no three of a kind

    def test_four_of_a_kind(self):
        """Test four of a kind scoring."""
        assert calculate_score([4, 4, 4, 4, 2], "four_kind") == 18  # sum all
        assert calculate_score([6, 6, 6, 6, 6], "four_kind") == 30  # yahtzee counts
        assert calculate_score([3, 3, 3, 1, 2], "four_kind") == 0  # only three

    def test_full_house(self):
        """Test full house scoring."""
        assert calculate_score([2, 2, 3, 3, 3], "full_house") == 25
        assert calculate_score([5, 5, 5, 2, 2], "full_house") == 25
        assert calculate_score([1, 1, 1, 1, 1], "full_house") == 25  # yahtzee counts
        assert calculate_score([1, 1, 2, 3, 3], "full_house") == 0
        assert calculate_score([1, 2, 3, 4, 5], "full_house") == 0

    def test_small_straight(self):
        """Test small straight scoring."""
        assert calculate_score([1, 2, 3, 4, 6], "small_straight") == 30
        assert calculate_score([2, 3, 4, 5, 1], "small_straight") == 30
        assert calculate_score([3, 4, 5, 6, 1], "small_straight") == 30
        assert calculate_score([1, 2, 3, 5, 6], "small_straight") == 0

    def test_large_straight(self):
        """Test large straight scoring."""
        assert calculate_score([1, 2, 3, 4, 5], "large_straight") == 40
        assert calculate_score([2, 3, 4, 5, 6], "large_straight") == 40
        assert calculate_score([1, 2, 3, 4, 6], "large_straight") == 0

    def test_yahtzee_scoring(self):
        """Test Yahtzee category scoring."""
        assert calculate_score([6, 6, 6, 6, 6], "yahtzee") == 50
        assert calculate_score([1, 1, 1, 1, 1], "yahtzee") == 50
        assert calculate_score([5, 5, 5, 5, 4], "yahtzee") == 0

    def test_chance_scoring(self):
        """Test chance category scoring."""
        assert calculate_score([1, 2, 3, 4, 5], "chance") == 15
        assert calculate_score([6, 6, 6, 6, 6], "chance") == 30
        assert calculate_score([1, 1, 1, 1, 1], "chance") == 5


class TestYahtzeePlayer:
    """Tests for YahtzeePlayer."""

    def test_player_defaults(self):
        """Test player default values."""
        player = YahtzeePlayer(id="123", name="Test")
        assert player.dice.num_dice == 5
        assert player.dice.has_rolled is False
        assert player.dice.kept == set()
        assert player.rolls_left == 3
        assert all(player.scores.get(cat) is None for cat in ALL_CATEGORIES)
        assert player.yahtzee_bonus_count == 0
        assert player.upper_bonus_awarded is False

    def test_get_upper_total(self):
        """Test upper section total calculation."""
        player = YahtzeePlayer(id="123", name="Test")
        player.scores["ones"] = 3
        player.scores["twos"] = 6
        player.scores["threes"] = 9
        assert player.get_upper_total() == 18

    def test_get_total_score(self):
        """Test total score calculation with bonuses."""
        player = YahtzeePlayer(id="123", name="Test")
        # Fill upper section to get bonus
        player.scores["ones"] = 3
        player.scores["twos"] = 6
        player.scores["threes"] = 12
        player.scores["fours"] = 16
        player.scores["fives"] = 15
        player.scores["sixes"] = 18  # Total = 70 >= 63, bonus!
        player.upper_bonus_awarded = True

        # Add some lower section scores
        player.scores["yahtzee"] = 50
        player.scores["chance"] = 20

        # Add a yahtzee bonus
        player.yahtzee_bonus_count = 1

        total = player.get_total_score()
        # 70 (upper) + 35 (bonus) + 50 (yahtzee) + 20 (chance) + 100 (yahtzee bonus) = 275
        assert total == 275


class TestYahtzeeGameUnit:
    """Unit tests for Yahtzee game functions."""

    def test_game_creation(self):
        """Test creating a new Yahtzee game."""
        game = YahtzeeGame()
        assert game.get_name() == "Yahtzee"
        assert game.get_type() == "yahtzee"
        assert game.get_category() == "category-dice-games"
        assert game.get_min_players() == 1
        assert game.get_max_players() == 4

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, YahtzeePlayer)

    def test_options_defaults(self):
        """Test default game options."""
        game = YahtzeeGame()
        assert game.options.num_games == 1

    def test_custom_options(self):
        """Test custom game options."""
        options = YahtzeeOptions(num_games=3)
        game = YahtzeeGame(options=options)
        assert game.options.num_games == 3

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = YahtzeeGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert len(data["players"]) == 2
        assert "dice" in data["players"][0]
        assert "scores" in data["players"][0]

        # Deserialize
        loaded_game = YahtzeeGame.from_json(json_str)
        assert len(loaded_game.players) == 2

    def test_turn_action_order_has_roll_after_dice_keys(self):
        """Roll action should come after dice key actions in turn set order."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        action_set = game.create_turn_action_set(player)
        assert action_set._order.index("dice_key_1") < action_set._order.index("roll")

    def test_roll_hidden_when_all_dice_kept_then_reappears_on_unkeep(self):
        """Roll should disappear when all dice are kept and reappear after unkeep."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player: YahtzeePlayer = game.add_player("Alice", user)  # type: ignore
        game.on_start()

        player.dice.values = [1, 2, 3, 4, 5]
        player.rolls_left = 2
        player.dice.kept = {0, 1, 2, 3, 4}
        player.dice.locked = set()

        visible_ids = [ra.action.id for ra in game.get_all_visible_actions(player)]
        assert "roll" not in visible_ids

        player.dice.unkeep(4)
        visible_ids = [ra.action.id for ra in game.get_all_visible_actions(player)]
        assert "roll" in visible_ids

    def test_roll_focuses_first_dice_toggle(self):
        """After rolling, focus should move to first dice toggle item."""
        game = YahtzeeGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.on_start()

        game.execute_action(player, "roll")

        assert any(
            message.type == "update_menu"
            and message.data.get("menu_id") == "turn_menu"
            and message.data.get("selection_id") == "toggle_die_0"
            for message in user.messages
        )


class TestYahtzeePlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = YahtzeeGame()
        game.options.num_games = 1

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game for many ticks (13 categories * 2 players = 26 turns minimum)
        max_ticks = 5000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestYahtzeeBotStrategy:
    """Focused tests for Yahtzee bot decision flow."""

    def test_bot_rolls_before_first_roll(self):
        game = YahtzeeGame()
        bot = Bot("Bot1")
        player = game.add_player("Bot1", bot)
        game.on_start()
        game.current_player = player

        assert game.bot_think(player) == "roll"

    def test_bot_keeps_then_rolls_for_multiples(self):
        game = YahtzeeGame()
        bot = Bot("Bot1")
        player: YahtzeePlayer = game.add_player("Bot1", bot)  # type: ignore
        game.on_start()
        game.current_player = player

        player.dice.values = [6, 6, 6, 2, 3]
        player.rolls_left = 2
        player.dice.kept = set()
        player.dice.locked = set()

        first_action = game.bot_think(player)
        assert first_action == "toggle_die_0"

        player.dice.kept = {0, 1, 2}
        second_action = game.bot_think(player)
        assert second_action == "roll"

    def test_bot_scores_when_no_rolls_left(self):
        game = YahtzeeGame()
        bot = Bot("Bot1")
        player: YahtzeePlayer = game.add_player("Bot1", bot)  # type: ignore
        game.on_start()
        game.current_player = player

        player.dice.values = [6, 6, 6, 6, 2]
        player.rolls_left = 0
        action = game.bot_think(player)

        assert action is not None
        assert action.startswith("score_")

    def test_single_player_game_completes(self):
        """Test that a single-player bot game completes."""
        game = YahtzeeGame()

        bot = Bot("Bot1")
        game.add_player("Bot1", bot)

        game.on_start()

        max_ticks = 3000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_four_player_game_completes(self):
        """Test that a 4-player bot game completes."""
        game = YahtzeeGame()

        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        max_ticks = 10000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestYahtzeePersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = YahtzeeGame(options=YahtzeeOptions(num_games=2))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        alice: YahtzeePlayer = game.players[0]  # type: ignore
        alice.scores["ones"] = 3
        alice.scores["twos"] = 6
        alice.yahtzee_bonus_count = 1

        # Save
        json_str = game.to_json()

        # Load
        loaded = YahtzeeGame.from_json(json_str)
        loaded_alice: YahtzeePlayer = loaded.players[0]  # type: ignore

        # Verify state
        assert loaded.game_active is True
        assert loaded.options.num_games == 2
        assert loaded_alice.scores["ones"] == 3
        assert loaded_alice.scores["twos"] == 6
        assert loaded_alice.yahtzee_bonus_count == 1
