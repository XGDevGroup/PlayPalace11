"""
Tests for the Rolling Balls game.

Following the testing strategy:
- Unit tests for individual functions
- Play tests that run the game from start to finish with bots
- Persistence tests (save/reload at each tick)
"""

import pytest
import random
import json

from server.games.rollingballs.game import (
    RollingBallsGame,
    RollingBallsOptions,
    RollingBallsPlayer,
    load_ball_packs,
    get_pack_names,
)
from server.core.users.test_user import MockUser
from server.core.users.bot import Bot


class TestRollingBallsUnit:
    """Unit tests for Rolling Balls game functions."""

    def test_game_creation(self):
        """Test creating a new Rolling Balls game."""
        game = RollingBallsGame()
        assert game.get_name() == "Rolling Balls"
        assert game.get_type() == "rollingballs"
        assert game.get_category() == "category-uncategorized"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 4

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = RollingBallsGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.score == 0
        assert player.has_reshuffled is False
        assert player.view_pipe_uses == 0
        assert player.reshuffle_uses == 0
        assert player.is_bot is False

    def test_options_defaults(self):
        """Test default game options."""
        game = RollingBallsGame()
        assert game.options.min_take == 1
        assert game.options.max_take == 3
        assert game.options.view_pipe_limit == 5
        assert game.options.reshuffle_limit == 3
        assert game.options.reshuffle_penalty == 1

    def test_custom_options(self):
        """Test custom game options."""
        options = RollingBallsOptions(
            view_pipe_limit=10,
            reshuffle_limit=0,
            reshuffle_penalty=3,
        )
        game = RollingBallsGame(options=options)
        assert game.options.view_pipe_limit == 10
        assert game.options.reshuffle_limit == 0
        assert game.options.reshuffle_penalty == 3

    def test_ball_packs_load(self):
        """Test that ball packs load correctly from JSON."""
        packs = load_ball_packs()
        assert len(packs) >= 2
        assert "Rory's Pack" in packs
        assert "Pizza" in packs
        for pack_id, pack in packs.items():
            assert len(pack) > 0
            for desc, value in pack.items():
                assert isinstance(desc, str)
                assert isinstance(value, int)

    def test_get_pack_names(self):
        """Test getting available pack names."""
        names = get_pack_names()
        assert "Rory's Pack" in names
        assert "Pizza" in names

    def test_default_ball_pack_option(self):
        """Test default ball pack option is the first available pack."""
        game = RollingBallsGame()
        assert game.options.ball_packs == [get_pack_names()[0]]

    def test_fill_pipe_2_players(self):
        """Test pipe filling with 2 players."""
        game = RollingBallsGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()

        assert len(game.pipe) == 25

    def test_fill_pipe_3_players(self):
        """Test pipe filling with 3 players."""
        game = RollingBallsGame()
        for name in ["Alice", "Bob", "Charlie"]:
            game.add_player(name, MockUser(name))
        game.on_start()

        assert len(game.pipe) == 35

    def test_fill_pipe_4_players(self):
        """Test pipe filling with 4 players."""
        game = RollingBallsGame()
        for name in ["Alice", "Bob", "Charlie", "Dave"]:
            game.add_player(name, MockUser(name))
        game.on_start()

        assert len(game.pipe) == 50

    def test_pipe_balls_from_pack(self):
        """Test that pipe balls come from the selected packs."""
        random.seed(42)
        game = RollingBallsGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()

        packs = load_ball_packs()
        combined_pack: dict[str, int] = {}
        for pack_name in game.options.ball_packs:
            combined_pack.update(packs[pack_name])
        for ball in game.pipe:
            assert isinstance(ball["description"], str)
            assert len(ball["description"]) > 0
            assert ball["description"] in combined_pack
            assert ball["value"] == combined_pack[ball["description"]]

    def test_pipe_balls_from_different_pack(self):
        """Test that pipe balls come from a different pack when selected."""
        random.seed(42)
        game = RollingBallsGame(options=RollingBallsOptions(ball_packs=["Pizza"]))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()

        packs = load_ball_packs()
        pack = packs["Pizza"]
        for ball in game.pipe:
            assert ball["description"] in pack
            assert ball["value"] == pack[ball["description"]]

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = RollingBallsGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()

        # Modify some state
        game.players[0].score = 15
        game.players[0].view_pipe_uses = 2
        game.players[0].reshuffle_uses = 1
        game.round = 3

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["round"] == 3
        assert len(data["players"]) == 2
        assert data["players"][0]["score"] == 15
        assert data["players"][0]["view_pipe_uses"] == 2
        assert data["players"][0]["reshuffle_uses"] == 1

        # Deserialize
        loaded_game = RollingBallsGame.from_json(json_str)
        assert loaded_game.round == 3
        assert loaded_game.players[0].score == 15
        assert loaded_game.players[0].view_pipe_uses == 2
        assert loaded_game.players[0].reshuffle_uses == 1
        assert len(loaded_game.pipe) == len(game.pipe)


class TestRollingBallsActions:
    """Test individual game actions."""

    def setup_method(self):
        """Set up a game with two players for each test."""
        random.seed(42)
        self.game = RollingBallsGame()
        self.user1 = MockUser("Alice")
        self.user2 = MockUser("Bob")
        self.player1 = self.game.add_player("Alice", self.user1)
        self.player2 = self.game.add_player("Bob", self.user2)
        self.game.on_start()
        self.game.reset_turn_order()

    def test_take_1_ball(self):
        """Test taking 1 ball from the pipe."""
        initial_pipe_len = len(self.game.pipe)
        initial_score = self.player1.score
        first_ball_value = self.game.pipe[0]["value"]

        self.game.execute_action(self.player1, "take_1")

        assert len(self.game.pipe) == initial_pipe_len - 1
        assert self.player1.score == initial_score + first_ball_value

    def test_take_2_balls(self):
        """Test taking 2 balls from the pipe."""
        initial_pipe_len = len(self.game.pipe)
        expected_score = self.game.pipe[0]["value"] + self.game.pipe[1]["value"]

        self.game.execute_action(self.player1, "take_2")

        assert len(self.game.pipe) == initial_pipe_len - 2
        assert self.player1.score == expected_score

    def test_take_3_balls(self):
        """Test taking 3 balls from the pipe."""
        initial_pipe_len = len(self.game.pipe)
        expected_score = sum(self.game.pipe[i]["value"] for i in range(3))

        self.game.execute_action(self.player1, "take_3")

        assert len(self.game.pipe) == initial_pipe_len - 3
        assert self.player1.score == expected_score

    def test_take_2_hidden_when_only_1_ball(self):
        """Test that take 2 is hidden when only 1 ball in pipe."""
        self.game.pipe = [{"value": 1, "description": "test"}]
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "take_1" in visible_ids
        assert "take_2" not in visible_ids
        assert "take_3" not in visible_ids

    def test_reshuffle(self):
        """Test reshuffling the pipe."""
        # Save original pipe order
        original_pipe = [b["value"] for b in self.game.pipe[:15]]

        self.game.execute_action(self.player1, "reshuffle")

        # Pipe should still have the same number of balls
        assert len(self.game.pipe) == 25
        assert self.player1.has_reshuffled is True
        assert self.player1.reshuffle_uses == 1

        # Penalty should be applied
        assert self.player1.score == -self.game.options.reshuffle_penalty

    def test_reshuffle_hidden_when_limit_0(self):
        """Test reshuffle action hidden when limit is 0."""
        self.game.options.reshuffle_limit = 0
        # Need to rebuild action sets for the option change to take effect
        self.game.setup_player_actions(self.player1)
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "reshuffle" not in visible_ids

    def test_reshuffle_hidden_when_uses_exhausted(self):
        """Test reshuffle hidden when all uses consumed."""
        self.player1.reshuffle_uses = self.game.options.reshuffle_limit
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "reshuffle" not in visible_ids

    def test_reshuffle_hidden_after_reshuffling_this_turn(self):
        """Test reshuffle hidden after already reshuffling this turn."""
        self.game.execute_action(self.player1, "reshuffle")

        # Should not be able to reshuffle again this turn
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "reshuffle" not in visible_ids

    def test_reshuffle_hidden_when_pipe_too_small(self):
        """Test reshuffle hidden when pipe has fewer than 6 balls."""
        self.game.pipe = [{"value": 1, "description": "test"}] * 5
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "reshuffle" not in visible_ids

    def test_reshuffle_no_penalty_when_0(self):
        """Test that no penalty when reshuffle_penalty is 0."""
        self.game.options.reshuffle_penalty = 0
        self.game.execute_action(self.player1, "reshuffle")

        assert self.player1.score == 0

    def test_view_pipe(self):
        """Test viewing the pipe."""
        self.game.execute_action(self.player1, "view_pipe")

        assert self.player1.view_pipe_uses == 1
        # Check that the user received a status box with pipe information
        assert "transient_display" in self.user1.menus

    def test_view_pipe_visible_when_uses_remain(self):
        """Test view pipe is visible when uses remain."""
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "view_pipe" in visible_ids

    def test_view_pipe_hidden_when_limit_0(self):
        """Test view pipe hidden when limit is 0."""
        self.game.options.view_pipe_limit = 0
        self.game.setup_player_actions(self.player1)
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "view_pipe" not in visible_ids

    def test_view_pipe_hidden_when_uses_exhausted(self):
        """Test view pipe hidden when all uses consumed."""
        self.player1.view_pipe_uses = self.game.options.view_pipe_limit
        visible_actions = self.game.get_all_visible_actions(self.player1)
        visible_ids = [a.action.id for a in visible_actions]

        assert "view_pipe" not in visible_ids

    def test_view_pipe_no_charge_when_unchanged(self):
        """Test that viewing the pipe again without changes doesn't use a charge."""
        self.game.execute_action(self.player1, "view_pipe")
        assert self.player1.view_pipe_uses == 1

        # View again without any pipe changes
        self.game.execute_action(self.player1, "view_pipe")
        assert self.player1.view_pipe_uses == 1

    def test_view_pipe_charges_after_change(self):
        """Test that viewing the pipe after a change uses a charge."""
        self.game.execute_action(self.player1, "view_pipe")
        assert self.player1.view_pipe_uses == 1

        # Take a ball to change the pipe
        self.game.execute_action(self.player1, "take_1")

        # View again - pipe changed, should cost a use
        self.game.execute_action(self.player1, "view_pipe")
        assert self.player1.view_pipe_uses == 2

    def test_requires_turn(self):
        """Test that turn-required actions are only available on your turn."""
        p1_actions = self.game.get_all_enabled_actions(self.player1)
        p2_actions = self.game.get_all_enabled_actions(self.player2)

        p1_ids = [a.action.id for a in p1_actions]
        p2_ids = [a.action.id for a in p2_actions]

        assert "take_1" in p1_ids
        assert "take_1" not in p2_ids

    def test_reshuffle_resets_each_turn(self):
        """Test that has_reshuffled resets at the start of each turn."""
        self.player1.has_reshuffled = True
        # Simulate turn end and new turn
        self.game._start_turn()

        current = self.game.current_player
        assert current is not None
        rb_current: RollingBallsPlayer = current  # type: ignore
        assert rb_current.has_reshuffled is False

    def test_option_change_rebuilds_take_actions(self):
        """Test that changing min/max take rebuilds the take actions."""
        # Start with defaults (min=1, max=3)
        visible_actions = self.game.get_all_visible_actions(self.player1)
        take_ids = [a.action.id for a in visible_actions if a.action.id.startswith("take_")]
        assert take_ids == ["take_1", "take_2", "take_3"]

        # Change max_take to 5 via the option system
        self.game._handle_option_change("max_take", "5")

        visible_actions = self.game.get_all_visible_actions(self.player1)
        take_ids = [a.action.id for a in visible_actions if a.action.id.startswith("take_")]
        assert take_ids == ["take_1", "take_2", "take_3", "take_4", "take_5"]

    def test_option_change_clamps_min_max(self):
        """Test that min_take is clamped when max_take is lowered below it."""
        self.game._handle_option_change("min_take", "3")
        assert self.game.options.min_take == 3

        # Lower max_take below min_take - min should be clamped
        self.game._handle_option_change("max_take", "2")
        assert self.game.options.max_take == 2
        assert self.game.options.min_take == 2

    def test_min_take_hides_lower_actions(self):
        """Test that take actions below min_take are not created."""
        game = RollingBallsGame(options=RollingBallsOptions(min_take=2, max_take=4))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()
        game.reset_turn_order()

        visible_actions = game.get_all_visible_actions(game.players[0])
        visible_ids = [a.action.id for a in visible_actions]

        assert "take_1" not in visible_ids
        assert "take_2" in visible_ids
        assert "take_3" in visible_ids
        assert "take_4" in visible_ids
        assert "take_5" not in visible_ids

    def test_max_take_limits_actions(self):
        """Test that take actions above max_take are not created."""
        game = RollingBallsGame(options=RollingBallsOptions(min_take=1, max_take=5))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()
        game.reset_turn_order()

        visible_actions = game.get_all_visible_actions(game.players[0])
        visible_ids = [a.action.id for a in visible_actions]

        assert "take_1" in visible_ids
        assert "take_2" in visible_ids
        assert "take_3" in visible_ids
        assert "take_4" in visible_ids
        assert "take_5" in visible_ids

    def test_single_take_option(self):
        """Test that min_take == max_take creates only one take action."""
        game = RollingBallsGame(options=RollingBallsOptions(min_take=2, max_take=2))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()
        game.reset_turn_order()

        visible_actions = game.get_all_visible_actions(game.players[0])
        take_ids = [a.action.id for a in visible_actions if a.action.id.startswith("take_")]

        assert take_ids == ["take_2"]


class TestRollingBallsPlayTest:
    """Play tests that run complete games with bots."""

    def test_two_player_game_completes(self):
        """Test that a 2-player game runs to completion."""
        random.seed(123)

        game = RollingBallsGame()
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        max_ticks = 5000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            # Save and reload every 50 ticks
            if tick % 50 == 0 and tick > 0:
                json_str = game.to_json()
                game = RollingBallsGame.from_json(json_str)
                game.attach_user("Bot1", bot1)
                game.attach_user("Bot2", bot2)
                game.rebuild_runtime_state()
                for player in game.players:
                    game.setup_player_actions(player)

            game.on_tick()

        assert not game.game_active, "Game should have ended"
        assert len(game.pipe) == 0

    def test_four_player_game_completes(self):
        """Test that a 4-player game runs to completion."""
        random.seed(456)

        game = RollingBallsGame()
        bots = [Bot(f"Bot{i}") for i in range(1, 5)]
        for bot in bots:
            game.add_player(bot.username, bot)

        game.on_start()

        max_ticks = 10000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            if tick % 50 == 0 and tick > 0:
                json_str = game.to_json()
                game = RollingBallsGame.from_json(json_str)
                for bot in bots:
                    game.attach_user(bot.username, bot)
                game.rebuild_runtime_state()
                for player in game.players:
                    game.setup_player_actions(player)

            game.on_tick()

        assert not game.game_active

    def test_game_with_no_reshuffles(self):
        """Test game with reshuffle limit set to 0."""
        random.seed(789)

        game = RollingBallsGame(options=RollingBallsOptions(reshuffle_limit=0))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        for tick in range(5000):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active

    def test_game_with_no_view_pipe(self):
        """Test game with view pipe limit set to 0."""
        random.seed(101)

        game = RollingBallsGame(options=RollingBallsOptions(view_pipe_limit=0))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        for tick in range(5000):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active

    def test_game_with_high_penalty(self):
        """Test game with maximum reshuffle penalty."""
        random.seed(202)

        game = RollingBallsGame(options=RollingBallsOptions(reshuffle_penalty=5))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        for tick in range(5000):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active

    def test_bot_acts_after_reshuffle(self):
        """Test that a bot takes balls after reshuffling (doesn't freeze)."""
        random.seed(42)

        game = RollingBallsGame(
            options=RollingBallsOptions(reshuffle_limit=100, reshuffle_penalty=0)
        )
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        for tick in range(5000):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active

    def test_game_with_custom_take_range(self):
        """Test game with min_take=2 and max_take=5."""
        random.seed(404)

        game = RollingBallsGame(options=RollingBallsOptions(min_take=2, max_take=5))
        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        for tick in range(5000):
            if not game.game_active:
                break
            game.on_tick()

        assert not game.game_active

    def test_human_and_bot_game(self):
        """Test a game with one human and one bot."""
        random.seed(303)

        game = RollingBallsGame()
        human = MockUser("Human")
        bot = Bot("Bot")
        game.add_player("Human", human)
        game.add_player("Bot", bot)

        game.on_start()

        max_ticks = 5000
        for tick in range(max_ticks):
            if not game.game_active:
                break

            game.on_tick()

            # Human always takes 1 ball on their turn (when not revealing)
            current = game.current_player
            if current and current.name == "Human" and not game._ball_reveal_player_id:
                game.execute_action(current, "take_1")

        assert not game.game_active
        messages = human.get_spoken_messages()
        assert len(messages) > 0


class TestRollingBallsPersistence:
    """Specific tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that all game state is preserved through save/load."""
        random.seed(42)
        game = RollingBallsGame(
            options=RollingBallsOptions(
                view_pipe_limit=10,
                reshuffle_limit=5,
                reshuffle_penalty=2,
            )
        )
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()

        # Modify state
        game.round = 5
        game.players[0].score = 15
        game.players[0].view_pipe_uses = 3
        game.players[0].reshuffle_uses = 2
        game.players[0].has_reshuffled = True
        game.players[1].score = -5

        # Save
        json_str = game.to_json()

        # Load
        loaded = RollingBallsGame.from_json(json_str)

        # Verify all state
        assert loaded.game_active is True
        assert loaded.round == 5
        assert loaded.options.view_pipe_limit == 10
        assert loaded.options.reshuffle_limit == 5
        assert loaded.options.reshuffle_penalty == 2
        assert loaded.players[0].score == 15
        assert loaded.players[0].view_pipe_uses == 3
        assert loaded.players[0].reshuffle_uses == 2
        assert loaded.players[0].has_reshuffled is True
        assert loaded.players[1].score == -5
        assert len(loaded.pipe) == len(game.pipe)

    def test_pipe_preserved(self):
        """Test that pipe contents are preserved through save/load."""
        random.seed(42)
        game = RollingBallsGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()

        original_pipe = [b.copy() for b in game.pipe]

        json_str = game.to_json()
        loaded = RollingBallsGame.from_json(json_str)

        assert len(loaded.pipe) == len(original_pipe)
        for i, ball in enumerate(loaded.pipe):
            assert ball["value"] == original_pipe[i]["value"]
            assert ball["description"] == original_pipe[i]["description"]

    def test_actions_work_after_reload(self):
        """Test that actions work correctly after reloading."""
        random.seed(42)
        game = RollingBallsGame()
        user = MockUser("Alice")
        bot = Bot("Bot")
        game.add_player("Alice", user)
        game.add_player("Bot", bot)
        game.on_start()

        # Save and reload
        json_str = game.to_json()
        game = RollingBallsGame.from_json(json_str)
        game.attach_user("Alice", user)
        game.attach_user("Bot", bot)
        for player in game.players:
            game.setup_player_actions(player)

        # Actions should still work
        actions = game.get_all_enabled_actions(game.players[0])
        assert len(actions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
