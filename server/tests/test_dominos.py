"""Tests for the Dominos game."""

from pathlib import Path

import pytest

from ..games.dominos.game import (
    BRANCH_ORDER,
    DominosGame,
    DominosOptions,
    DominoTile,
)
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from server.core.users.bot import Bot
from server.core.users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def make_game(player_count: int = 2, start: bool = False, **option_overrides) -> DominosGame:
    game = DominosGame(options=DominosOptions(**option_overrides))
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        game.add_player(name, MockUser(name, uuid=f"p{index + 1}"))
    game.host = "Player1"
    if start:
        game.on_start()
    return game


def make_game_with_bot(start: bool = False, **option_overrides) -> DominosGame:
    game = DominosGame(options=DominosOptions(**option_overrides))
    game.setup_keybinds()
    game.add_player("Alice", MockUser("Alice", uuid="p1"))
    game.add_player("Bot1", Bot("Bot1", uuid="p2"))
    game.host = "Alice"
    if start:
        game.on_start()
    return game


def set_web_client(game: DominosGame, *players) -> None:
    targets = players or game.players
    for player in targets:
        user = game.get_user(player)
        if user is not None:
            user.set_client_type("web")


def advance_until(game: DominosGame, condition, max_ticks: int = 400) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def set_linear_chain(game: DominosGame, left: int, right: int) -> None:
    game.center_tile = DominoTile(id=1000, left=left, right=right)
    game.spinner_active = False
    game.branches = {branch: [] for branch in BRANCH_ORDER}
    game.open_ends = {"left": left, "right": right}


def test_dominos_game_registration_and_defaults() -> None:
    game_class = GameRegistry.get("dominos")
    assert game_class is DominosGame
    assert game_class.get_name() == "Dominos"
    assert game_class.get_name_key() == "game-name-dominos"
    assert game_class.get_type() == "dominos"
    assert game_class.get_category() == "category-playaural"
    assert game_class.get_min_players() == 2
    assert game_class.get_max_players() == 4

    options = DominosOptions()
    assert options.target_score == 100
    assert options.draw_mode == "draw"
    assert options.domino_set == "double6"
    assert options.spinner_enabled is True
    assert options.opening_rule == "highest_double"
    assert options.team_mode == "individual"


def test_prestart_validation_rejects_invalid_team_mode() -> None:
    game = make_game(player_count=3, team_mode="2v2")
    assert "game-error-invalid-team-mode" in game.prestart_validate()


@pytest.mark.parametrize(
    ("domino_set", "player_count", "expected_hand_size"),
    [
        ("double6", 2, 7),
        ("double6", 4, 5),
        ("double9", 2, 10),
        ("double9", 4, 7),
    ],
)
def test_round_start_deals_expected_hand_sizes(
    domino_set: str, player_count: int, expected_hand_size: int
) -> None:
    game = make_game(player_count=player_count, start=True, domino_set=domino_set)
    hand_sizes = sorted(len(player.hand) for player in game.get_active_players())
    assert hand_sizes == [expected_hand_size - 1] + [expected_hand_size] * (player_count - 1)


def test_spinner_opening_creates_four_open_ends() -> None:
    game = make_game()
    game.options.spinner_enabled = True
    opening = DominoTile(id=1, left=4, right=4)
    game._place_opening_tile(opening)

    assert game.spinner_active is True
    assert game.center_tile == opening
    assert game.open_ends == {branch: 4 for branch in BRANCH_ORDER}


def test_round_winner_opening_rule_uses_previous_round_winner() -> None:
    game = make_game(player_count=2, opening_rule="round_winner")
    player1, player2 = game.get_active_players()
    player1.hand = [DominoTile(id=1, left=1, right=1), DominoTile(id=2, left=6, right=5)]
    player2.hand = [DominoTile(id=3, left=6, right=6)]
    game.previous_round_winner_id = player1.id

    opener, tile = game._select_opening_play([player1, player2], 6)

    assert opener == player1
    assert tile.id == 2


def test_option_labels_localize_choice_values() -> None:
    options = DominosOptions(
        domino_set="double9", opening_rule="set_max_double", spinner_enabled=True
    )
    summary = options.format_options_summary("en")

    # Summary should contain localized labels, not raw field names
    assert len(summary) > 0
    assert not any("domino_set" in line or "opening_rule" in line for line in summary)


def test_draw_mode_draws_until_playable_and_auto_plays() -> None:
    game = make_game(start=True, draw_mode="draw")
    player1, player2 = game.get_active_players()
    game.current_player = player1
    set_linear_chain(game, 1, 2)
    player1.hand = [DominoTile(id=1, left=6, right=6)]
    player2.hand = [DominoTile(id=2, left=0, right=0)]
    game.boneyard = [
        DominoTile(id=3, left=2, right=5),
        DominoTile(id=4, left=0, right=0),
    ]
    game._update_all_turn_actions()

    game._action_draw(player1, "draw")

    assert [tile.id for tile in player1.hand] == [1, 4]
    assert game.open_ends["right"] == 5
    assert game.current_player == player2
    assert len(game.branches["right"]) == 1


def test_draw_mode_empty_boneyard_enables_knock_instead() -> None:
    game = make_game(start=True, draw_mode="draw")
    player1, _player2 = game.get_active_players()
    game.current_player = player1
    set_linear_chain(game, 1, 2)
    player1.hand = [DominoTile(id=1, left=6, right=6)]
    game.boneyard = []

    assert game._is_draw_enabled(player1) == "dominos-boneyard-empty"
    assert game._is_knock_enabled(player1) is None


def test_draw_button_does_not_remove_hand_tiles_from_turn_menu() -> None:
    game = make_game(start=True, draw_mode="draw")
    player1, _player2 = game.get_active_players()
    game.current_player = player1
    set_linear_chain(game, 1, 2)
    player1.hand = [
        DominoTile(id=1, left=6, right=6),
        DominoTile(id=2, left=4, right=4),
    ]
    game.boneyard = [DominoTile(id=3, left=0, right=0)]
    game.rebuild_player_menu(player1)

    menu_ids = [item.id for item in game.get_user(player1).menus["turn_menu"]["items"]]

    assert "draw" in menu_ids
    assert "play_tile_1" in menu_ids
    assert "play_tile_2" in menu_ids


def test_draw_mode_auto_knocks_after_exhausting_boneyard() -> None:
    game = make_game(start=True, draw_mode="draw")
    player1, player2 = game.get_active_players()
    game.current_player = player1
    set_linear_chain(game, 1, 2)
    player1.hand = [DominoTile(id=1, left=6, right=6)]
    player2.hand = [DominoTile(id=2, left=2, right=4)]
    game.boneyard = [DominoTile(id=3, left=0, right=0)]
    game.consecutive_passes = 0

    game._action_draw(player1, "draw")

    assert game.current_player == player2
    assert game.consecutive_passes == 1
    assert [tile.id for tile in player1.hand] == [1, 3]


def test_empty_boneyard_no_playable_tiles_resolves_blocked_round_immediately() -> None:
    game = make_game(start=True, draw_mode="draw", target_score=200)
    player1, player2 = game.get_active_players()
    game.current_player = player1
    set_linear_chain(game, 1, 2)
    player1.hand = [DominoTile(id=1, left=6, right=6)]
    player2.hand = [DominoTile(id=2, left=5, right=5)]
    game.boneyard = [DominoTile(id=3, left=0, right=0)]

    game._action_draw(player1, "draw")

    assert game.team_manager.get_team(player2.name).total_score == 12
    assert game.round_wait_ticks == 100


def test_block_mode_knock_advances_turn() -> None:
    game = make_game(start=True, draw_mode="block")
    player1, player2 = game.get_active_players()
    game.current_player = player1
    set_linear_chain(game, 1, 2)
    player1.hand = [DominoTile(id=1, left=6, right=6)]
    player2.hand = [DominoTile(id=2, left=2, right=4)]
    game.consecutive_passes = 0

    game._action_knock(player1, "knock")

    assert game.current_player == player2
    assert game.consecutive_passes == 1


def test_blocked_round_scores_lowest_pips(monkeypatch: pytest.MonkeyPatch) -> None:
    game = make_game(start=True, draw_mode="block", target_score=200)
    player1, player2 = game.get_active_players()
    game.current_player = player1
    set_linear_chain(game, 1, 2)
    player1.hand = [DominoTile(id=1, left=3, right=3)]
    player2.hand = [DominoTile(id=2, left=5, right=6)]
    game.consecutive_passes = 1
    game._action_knock(player1, "knock")

    assert game.team_manager.get_team(player1.name).total_score == 11
    assert game.previous_round_winner_id == player1.id
    assert game.round_wait_ticks == 100


def test_blocked_round_tie_scores_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    game = make_game(start=True, draw_mode="block", target_score=200)
    player1, player2 = game.get_active_players()
    game.current_player = player1
    set_linear_chain(game, 1, 2)
    player1.hand = [DominoTile(id=1, left=3, right=3)]
    player2.hand = [DominoTile(id=2, left=0, right=6)]
    game.consecutive_passes = 1
    game._action_knock(player1, "knock")

    assert game.team_manager.get_team(player1.name).total_score == 0
    assert game.team_manager.get_team(player2.name).total_score == 0
    assert game.previous_round_winner_id is None


def test_team_mode_round_scoring_uses_opponents_only(monkeypatch: pytest.MonkeyPatch) -> None:
    game = make_game(player_count=4, start=True, team_mode="2v2", target_score=200)
    player1, player2, player3, player4 = game.get_active_players()
    player1.hand = []
    player2.hand = [DominoTile(id=1, left=6, right=6)]
    player3.hand = [DominoTile(id=2, left=1, right=1)]
    player4.hand = [DominoTile(id=3, left=4, right=5)]
    game._finish_round_from_empty_hand(player1)

    assert game.team_manager.get_team(player1.name).total_score == 21
    assert game.team_manager.get_team(player2.name).total_score == 0
    assert game.round_wait_ticks == 100


def test_custom_dominos_keybinds_avoid_reserved_keys() -> None:
    game = make_game()
    custom_actions = {
        "draw",
        "knock",
        "view_chain",
        "read_ends",
        "read_hand",
        "read_counts",
    }
    custom_keys = {
        key
        for key, binds in game._keybinds.items()
        for bind in binds
        if any(action in custom_actions for action in bind.actions)
    }

    assert custom_keys == {"space", "p", "v", "c", "e", "w"}
    assert custom_keys.isdisjoint({"s", "t", "escape", "enter"})


def test_tile_actions_are_hidden_from_global_action_menu_and_info_actions_are_last() -> None:
    game = make_game(start=True)
    player1, _player2 = game.get_active_players()
    set_linear_chain(game, 1, 2)
    player1.hand = [
        DominoTile(id=1, left=1, right=4),
        DominoTile(id=2, left=6, right=6),
    ]
    game.rebuild_player_menu(player1)

    enabled_action_ids = [action.action.id for action in game.get_all_enabled_actions(player1)]

    assert "play_tile_1" not in enabled_action_ids
    assert "play_tile_2" not in enabled_action_ids
    assert enabled_action_ids[-4:] == ["view_chain", "read_ends", "read_hand", "read_counts"]


def test_information_actions_use_direct_tts_not_status_box() -> None:
    game = make_game(start=True)
    player1, _player2 = game.get_active_players()
    user = game.get_user(player1)
    assert user is not None
    user.clear_messages()

    game._action_read_hand(player1, "read_hand")

    assert "transient_display" not in user.menus
    assert any(message.type == "speak" for message in user.messages)


def test_view_chain_uses_status_box() -> None:
    game = make_game(start=True)
    player1, _player2 = game.get_active_players()
    user = game.get_user(player1)
    assert user is not None

    game._action_view_chain(player1, "view_chain")

    assert "transient_display" in user.menus


def test_read_ends_uses_direct_tts() -> None:
    game = make_game(start=True)
    player1, _player2 = game.get_active_players()
    user = game.get_user(player1)
    assert user is not None
    set_linear_chain(game, 3, 5)
    user.clear_messages()

    game._action_read_ends(player1, "read_ends")

    assert "transient_display" not in user.menus
    spoken = user.get_last_spoken()
    assert spoken is not None
    assert "3" in spoken
    assert "5" in spoken


def test_hand_tiles_remain_visible_when_not_players_turn() -> None:
    game = make_game(start=True)
    player1, player2 = game.get_active_players()
    game.current_player = player2
    player1.hand = [
        DominoTile(id=1, left=1, right=4),
        DominoTile(id=2, left=6, right=6),
    ]
    game.rebuild_player_menu(player1)

    menu_ids = [item.id for item in game.get_user(player1).menus["turn_menu"]["items"]]

    assert "play_tile_1" in menu_ids
    assert "play_tile_2" in menu_ids


def test_knock_and_blocked_sounds_broadcast_to_all_players() -> None:
    game = make_game(start=True, draw_mode="block", target_score=200)
    player1, player2 = game.get_active_players()
    user1 = game.get_user(player1)
    user2 = game.get_user(player2)
    assert user1 is not None and user2 is not None
    user1.clear_messages()
    user2.clear_messages()
    game.current_player = player1
    set_linear_chain(game, 1, 2)
    player1.hand = [DominoTile(id=1, left=6, right=6)]
    player2.hand = [DominoTile(id=2, left=5, right=6)]

    game._action_knock(player1, "knock")

    assert "game_dominos/knock.ogg" in user1.get_sounds_played()
    assert "game_dominos/knock.ogg" in user2.get_sounds_played()

    user1.clear_messages()
    user2.clear_messages()
    game.current_player = player2
    game.consecutive_passes = 1
    player2.hand = [DominoTile(id=2, left=5, right=6)]

    game._action_knock(player2, "knock")

    assert "game_dominos/blocked.ogg" in user1.get_sounds_played()
    assert "game_dominos/blocked.ogg" in user2.get_sounds_played()


def test_web_turn_menu_shows_info_actions_and_orders_score_above_turn_and_table() -> None:
    game = make_game(start=False)
    player1, _player2 = game.get_active_players()
    set_web_client(game, player1)
    game.on_start()
    game.rebuild_player_menu(player1)

    menu_ids = [item.id for item in game.get_user(player1).menus["turn_menu"]["items"]]

    for action_id in ["read_ends", "read_hand", "view_chain", "read_counts"]:
        assert action_id in menu_ids

    assert menu_ids.index("check_scores") < menu_ids.index("whose_turn")
    assert menu_ids.index("check_scores") < menu_ids.index("whos_at_table")


def test_read_counts_speaks_other_players_tile_counts() -> None:
    game = make_game(player_count=3, start=True)
    player1, player2, player3 = game.get_active_players()
    player1.hand = [DominoTile(id=1, left=1, right=1)]
    player2.hand = [DominoTile(id=2, left=2, right=2), DominoTile(id=3, left=3, right=3)]
    player3.hand = [DominoTile(id=4, left=4, right=4)]
    user = game.get_user(player1)
    assert user is not None
    user.clear_messages()

    game._action_read_counts(player1, "read_counts")

    spoken = user.get_last_spoken()
    assert spoken is not None
    assert "Player2" in spoken
    assert "Player3" in spoken


def test_round_wait_advances_to_next_round_after_five_seconds() -> None:
    game = make_game(start=True, target_score=200)
    player1, player2 = game.get_active_players()
    player1.hand = []
    player2.hand = [DominoTile(id=2, left=6, right=6)]

    current_round = game.round
    game._finish_round_from_empty_hand(player1)

    assert game.round_wait_ticks == 100
    reached = advance_until(
        game, lambda: game.round == current_round + 1 and game.round_wait_ticks == 0, max_ticks=120
    )
    assert reached is True


def test_round_and_match_victory_sounds_broadcast() -> None:
    game = make_game(start=True, target_score=5)
    player1, player2 = game.get_active_players()
    user1 = game.get_user(player1)
    user2 = game.get_user(player2)
    assert user1 is not None and user2 is not None
    user1.clear_messages()
    user2.clear_messages()

    player1.hand = []
    player2.hand = [DominoTile(id=2, left=3, right=3)]
    game._finish_round_from_empty_hand(player1)

    sounds1 = user1.get_sounds_played()
    sounds2 = user2.get_sounds_played()
    assert "game_pig/win.ogg" in sounds1
    assert "game_pig/win.ogg" in sounds2
    assert "game_pig/wingame.ogg" in sounds1
    assert "game_pig/wingame.ogg" in sounds2


def test_bot_turn_uses_advance_until_to_act() -> None:
    game = make_game_with_bot(start=True, draw_mode="block")
    human, bot = game.get_active_players()
    game.current_player = bot
    set_linear_chain(game, 1, 2)
    bot.hand = [DominoTile(id=1, left=2, right=4), DominoTile(id=3, left=6, right=6)]
    human.hand = [DominoTile(id=2, left=6, right=6)]
    bot.bot_think_ticks = 0
    bot.bot_pending_action = None
    game._update_all_turn_actions()

    reached = advance_until(
        game, lambda: game.current_player == human and game.open_ends["right"] == 4
    )

    assert reached is True
