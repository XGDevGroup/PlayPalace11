"""
Tests for the Mile by Mile game.
"""

import json
import random

from server.messages.localization import Localization
from server.games.milebymile.game import (
    MileByMileGame,
    MileByMilePlayer,
    MileByMileOptions,
    RaceState,
)
from server.games.milebymile.cards import HazardType, SafetyType
from server.core.users.test_user import MockUser
from server.core.users.bot import Bot


class TestMileByMileGameUnit:
    """Unit tests for Mile by Mile game functions."""

    def test_game_creation(self):
        """Test creating a new Mile by Mile game."""
        game = MileByMileGame()
        assert game.get_name() == "Mile by Mile"
        assert game.get_type() == "milebymile"
        assert game.get_category() == "category-card-games"
        assert game.get_min_players() == 2
        assert game.get_max_players() == 9

    def test_player_creation(self):
        """Test creating a player with correct initial state."""
        game = MileByMileGame()
        user = MockUser("Alice")
        player = game.add_player("Alice", user)

        assert player.name == "Alice"
        assert player.is_bot is False
        assert isinstance(player, MileByMilePlayer)
        assert player.hand == []

    def test_options_defaults(self):
        """Test default game options."""
        game = MileByMileGame()
        assert game.options.round_distance == 1000
        assert game.options.winning_score == 5000

    def test_custom_options(self):
        """Test custom game options."""
        options = MileByMileOptions(round_distance=700, winning_score=3000)
        game = MileByMileGame(options=options)
        assert game.options.round_distance == 700
        assert game.options.winning_score == 3000

    def test_always_discard_option_localizes_in_english(self):
        """The always-discard option strings should resolve in English."""
        assert (
            Localization.get("en", "milebymile-toggle-always-discard", enabled="yes")
            == "Always allow discarding: yes"
        )
        assert (
            Localization.get("en", "milebymile-option-changed-always-discard", enabled="off")
            == "Always allow discarding off."
        )


class TestRightOfWayBehavior:
    """Tests for Right of Way safety card behavior."""

    def test_right_of_way_allows_driving_when_stopped(self):
        """Right of Way should allow playing distance when only STOP is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.STOP)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is True

    def test_right_of_way_allows_driving_with_speed_limit(self):
        """Right of Way should allow playing distance when SPEED_LIMIT is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.SPEED_LIMIT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is True

    def test_right_of_way_allows_driving_with_stop_and_speed_limit(self):
        """Right of Way should allow playing distance with both STOP and SPEED_LIMIT."""
        race_state = RaceState()
        race_state.add_problem(HazardType.STOP)
        race_state.add_problem(HazardType.SPEED_LIMIT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is True

    def test_right_of_way_does_not_protect_against_accident(self):
        """Right of Way should NOT allow playing distance when ACCIDENT is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.ACCIDENT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False

    def test_right_of_way_does_not_protect_against_flat_tire(self):
        """Right of Way should NOT allow playing distance when FLAT_TIRE is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.FLAT_TIRE)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False

    def test_right_of_way_does_not_protect_against_out_of_gas(self):
        """Right of Way should NOT allow playing distance when OUT_OF_GAS is active."""
        race_state = RaceState()
        race_state.add_problem(HazardType.OUT_OF_GAS)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False

    def test_right_of_way_with_accident_and_stop(self):
        """Right of Way should NOT allow distance with ACCIDENT even if STOP also present."""
        race_state = RaceState()
        race_state.add_problem(HazardType.STOP)
        race_state.add_problem(HazardType.ACCIDENT)
        race_state.add_safety(SafetyType.RIGHT_OF_WAY)

        assert race_state.can_play_distance() is False


class TestMileByMileSerialization:
    """Tests for game serialization."""

    def test_serialization(self):
        """Test that game state can be serialized and deserialized."""
        game = MileByMileGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Modify some state
        game.current_race = 1

        # Serialize
        json_str = game.to_json()
        data = json.loads(json_str)

        # Verify structure
        assert data["current_race"] == 1
        assert len(data["players"]) == 2

        # Deserialize
        loaded_game = MileByMileGame.from_json(json_str)
        assert loaded_game.current_race == 1


class TestMileByMilePlayTest:
    """Integration tests for complete game play."""

    def test_two_player_game_completes(self):
        """Test that a 2-player bot game completes."""
        game = MileByMileGame()
        game.options.round_distance = 300  # Lower target for faster test
        game.options.winning_score = 1000

        bot1 = Bot("Bot1")
        bot2 = Bot("Bot2")
        game.add_player("Bot1", bot1)
        game.add_player("Bot2", bot2)

        game.on_start()

        # Run game for many ticks
        max_ticks = 30000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"

    def test_four_player_team_game_completes(self):
        """Test that a 4-player team game completes."""
        random.seed(12345)
        game = MileByMileGame()
        game.options.round_distance = 500
        game.options.winning_score = 1000
        game.options.team_mode = "2v2"  # Internal format

        for i in range(4):
            bot = Bot(f"Bot{i}")
            game.add_player(f"Bot{i}", bot)

        game.on_start()

        # Verify teams are set up
        assert game.get_num_teams() == 2

        max_ticks = 100000
        for _ in range(max_ticks):
            if game.status == "finished":
                break
            game.on_tick()

        assert game.status == "finished"


class TestMileByMileDiscardConfirmation:
    """Tests for the discard confirmation prompt on tap of an unplayable card."""

    def _setup_unplayable_card(self):
        """Create a 2-player game where the current player has a STOP hazard
        and a distance card that therefore cannot be played."""
        from server.games.milebymile.cards import Card, CardType

        game = MileByMileGame()
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)
        game.on_start()

        player = game.current_player
        race_state = game.get_player_race_state(player)
        race_state.add_problem(HazardType.STOP)

        distance_card = Card(id=9999, card_type=CardType.DISTANCE, value="25")
        player.hand = [distance_card]
        return game, player

    def test_prompts_when_pref_enabled(self):
        game, player = self._setup_unplayable_card()
        user = game.get_user(player)
        user._preferences.confirm_destructive_actions = True

        before_hand_len = len(player.hand)
        game._action_play_card(player, "card_slot_1")

        # Card is still in hand; a discard_confirm menu was shown.
        assert len(player.hand) == before_hand_len
        assert "discard_confirm" in user.menus
        assert game._pending_actions.get(player.id) == "discard_confirm"
        assert game._pending_discard_slot.get(player.id) == 0

    def test_discards_immediately_when_pref_disabled(self):
        game, player = self._setup_unplayable_card()
        user = game.get_user(player)
        user._preferences.confirm_destructive_actions = False

        game._action_play_card(player, "card_slot_1")

        # Card was discarded; no confirmation menu was shown.
        assert len(player.hand) == 0
        assert "discard_confirm" not in user.menus
        assert player.id not in game._pending_actions

    def test_per_game_override_disables_prompt(self):
        game, player = self._setup_unplayable_card()
        user = game.get_user(player)
        # Global default is to confirm; override mile by mile specifically.
        user._preferences.confirm_destructive_actions = True
        user._preferences.game_overrides["milebymile"] = {
            "confirm_destructive_actions": False
        }

        game._action_play_card(player, "card_slot_1")

        assert len(player.hand) == 0
        assert "discard_confirm" not in user.menus

    def test_yes_confirmation_discards(self):
        game, player = self._setup_unplayable_card()
        user = game.get_user(player)
        user._preferences.confirm_destructive_actions = True

        game._action_play_card(player, "card_slot_1")
        assert "discard_confirm" in user.menus

        # Respond Yes
        game._handle_menu_event(
            player, {"menu_id": "discard_confirm", "selection_id": "yes"}
        )

        assert len(player.hand) == 0
        assert player.id not in game._pending_actions
        assert player.id not in game._pending_discard_slot

    def test_no_confirmation_keeps_card(self):
        game, player = self._setup_unplayable_card()
        user = game.get_user(player)
        user._preferences.confirm_destructive_actions = True

        game._action_play_card(player, "card_slot_1")

        game._handle_menu_event(
            player, {"menu_id": "discard_confirm", "selection_id": "no"}
        )

        assert len(player.hand) == 1
        assert player.id not in game._pending_actions
        assert player.id not in game._pending_discard_slot

    def test_bot_never_prompts(self):
        game, player = self._setup_unplayable_card()
        # Force the current player to be treated as a bot.
        player.is_bot = True

        game._action_play_card(player, "card_slot_1")

        assert len(player.hand) == 0
        assert player.id not in game._pending_actions

    def test_relevant_preference_registered(self):
        assert "confirm_destructive_actions" in MileByMileGame.relevant_preferences


class TestMileByMilePersistence:
    """Tests for game persistence."""

    def test_full_state_preserved(self):
        """Test that full game state is preserved through save/load."""
        game = MileByMileGame(options=MileByMileOptions(round_distance=500))
        user1 = MockUser("Alice")
        user2 = MockUser("Bob")
        game.add_player("Alice", user1)
        game.add_player("Bob", user2)

        game.on_start()

        # Set various state
        game.current_race = 1

        # Save
        json_str = game.to_json()

        # Load
        loaded = MileByMileGame.from_json(json_str)

        # Verify state
        assert loaded.game_active is True
        assert loaded.current_race == 1
        assert loaded.options.round_distance == 500
