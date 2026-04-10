"""
Tests for the Threes game.
"""

import json

from server.games.threes.game import ThreesGame, ThreesPlayer, ThreesOptions
from server.core.users.test_user import MockUser
from server.core.users.bot import Bot


class TestThreesGameUnit:
    """Unit tests for Threes game functions."""

    def test_game_creation(self):
        """Test creating a new Threes game."""
        game = ThreesGame()
        assert game.get_name() == "Threes"
        assert game.get_type() == "threes"
        assert game.get_category() == "category-dice-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 8

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = ThreesGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, ThreesPlayer)

    def test_options_defaults(self):
        """Test default game options."""
        game = ThreesGame()
        assert game.options.total_rounds == 10

    def test_custom_options(self):
        """Test custom game options."""
        options = ThreesOptions(total_rounds=10)
        game = ThreesGame(options=options)
        assert game.options.total_rounds == 10

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = ThreesGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        game.round = 3

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["round"] == 3
        assert len(data["players"]) == 2

        # Deserialize
        loaded_game = ThreesGame.from_json(json_str)
        assert loaded_game.round == 3

    def test_roll_focuses_first_dice_toggle(self):
        """After rolling, focus should move to first dice toggle item."""
        game = ThreesGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.add_player("Bob", MockUser("Bob"))
        game.on_start()

        game.execute_action(player, "roll")

        assert any(
            message.type == "update_menu"
            and message.data.get("menu_id") == "turn_menu"
            and message.data.get("selection_id") == "toggle_die_0"
            for message in user.messages
        )

    def test_second_roll_focuses_first_toggle(self):
        """After locking die 0, focus should land on a toggle die action."""
        game = ThreesGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.add_player("Bob", MockUser("Bob"))
        game.on_start()

        player.dice.values = [1, 2, 3, 4, 5]
        player.dice.kept = {0}
        player.dice.locked = set()
        user.clear_messages()

        game.execute_action(player, "roll")

        updates = [
            message
            for message in user.messages
            if message.type == "update_menu"
            and message.data.get("menu_id") == "turn_menu"
            and message.data.get("selection_id")
        ]
        assert updates
        selected = updates[-1].data.get("selection_id")
        assert selected is not None
        assert selected.startswith("toggle_die_")

    def test_roll_hidden_when_all_dice_kept_then_reappears(self):
        """Roll should hide when all dice are kept and reappear after unkeep."""
        game = ThreesGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)
        game.add_player("Bob", MockUser("Bob"))
        game.on_start()

        player.dice.values = [1, 2, 3, 4, 5]
        player.dice.kept = {0, 1, 2, 3, 4}
        player.dice.locked = set()

        visible_ids = [ra.action.id for ra in game.get_all_visible_actions(player)]
        assert "roll" not in visible_ids

        player.dice.unkeep(4)
        visible_ids = [ra.action.id for ra in game.get_all_visible_actions(player)]
        assert "roll" in visible_ids


class TestThreesPlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = ThreesGame()
        game.options.total_rounds = 3  # Fewer rounds for faster test

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game for many ticks
        max_ticks = 5000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_four_player_game_completes(self):
        """Test that a 4-player bot game completes."""
        game = ThreesGame()
        game.options.total_rounds = 3

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


class TestThreesPersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = ThreesGame(options=ThreesOptions(total_rounds=5))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Set various state
        game.round = 3

        # Save
        json_str = game.to_json()

        # Load
        loaded = ThreesGame.from_json(json_str)

        # Verify state
        assert loaded.game_active is True
        assert loaded.round == 3
        assert loaded.options.total_rounds == 5
