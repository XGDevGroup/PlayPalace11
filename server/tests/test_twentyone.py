import random
from collections import defaultdict
from pathlib import Path

from server.core.users.bot import Bot
from server.core.users.test_user import MockUser
from server.game_utils.cards import Card, Deck
from server.games import twentyone as twentyone_module
from server.games.twentyone import (
    MODIFIER_LABELS,
    MODIFIER_GUARD,
    MODIFIER_LOCKDOWN,
    MODIFIER_REDRAFT,
    MODIFIER_TARGET_24,
    MODIFIER_RAISE_1,
    MODIFIER_RAISE_2,
    MODIFIER_PRECISION_DRAW,
    MODIFIER_AID_RIVAL,
    MODIFIER_RAISE_2_PLUS,
    MODIFIER_SCRAP,
    MODIFIER_RECYCLE,
    MODIFIER_SWAP_DRAW,
    TwentyOneGame,
    TwentyOneOptions,
)


def make_card(card_id: int, rank: int) -> Card:
    return Card(id=card_id, rank=rank, suit=0)


def setup_game() -> tuple[TwentyOneGame, object, object]:
    game = TwentyOneGame()
    user1 = MockUser("Host")
    user2 = MockUser("Guest")
    p1 = game.add_player("Host", user1)
    p2 = game.add_player("Guest", user2)
    game.host = "Host"
    return game, p1, p2


def test_twentyone_creation() -> None:
    game = TwentyOneGame()
    assert game.get_name() == "21 (Survival Rules)"
    assert game.get_name_key() == "21"
    assert game.get_type() == "twentyone"
    assert game.get_min_players() == 2
    assert game.get_max_players() == 2
    assert MODIFIER_LABELS[MODIFIER_RAISE_1] == "raise one"
    assert MODIFIER_LABELS[MODIFIER_RAISE_2_PLUS] == "withdraw and raise two"
    assert MODIFIER_LABELS[MODIFIER_GUARD] == "defend"
    assert MODIFIER_LABELS[MODIFIER_LOCKDOWN] == "delete double enhanced"


def test_twentyone_start_round_deals_number_cards() -> None:
    random.seed(22)
    game, p1, p2 = setup_game()
    game.on_start()

    assert game.status == "playing"
    assert game.phase == "turns"
    assert all(1 <= card.rank <= 11 for card in p1.hand)
    assert all(1 <= card.rank <= 11 for card in p2.hand)
    assert len(p1.modifiers) == 1
    assert len(p2.modifiers) == 1


def test_twentyone_hides_opponent_hole_card_on_round_start() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None

    def rigged_deck() -> None:
        game.deck = Deck(
            cards=[
                make_card(1, 11),  # Host hidden
                make_card(2, 3),   # Guest hidden
                make_card(3, 4),   # Host shown
                make_card(4, 5),   # Guest shown
            ]
        )

    game._build_round_deck = rigged_deck  # type: ignore[method-assign]
    game.on_start()

    host_text = " ".join(host_user.get_spoken_messages())
    guest_text = " ".join(guest_user.get_spoken_messages())

    assert "11" in host_text
    assert "11" not in guest_text
    assert "Host shows" in guest_text


def test_twentyone_modifier_gain_is_hidden_from_opponent() -> None:
    random.seed(7)
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None

    game._give_random_modifiers(p1, 1, announce=True)
    gained = MODIFIER_LABELS[p1.modifiers[-1]]

    host_text = " ".join(host_user.get_spoken_messages())
    guest_text = " ".join(guest_user.get_spoken_messages())

    assert gained in host_text
    assert gained not in guest_text
    assert "gains a change card" in guest_text


def test_twentyone_hit_card_is_visible_to_opponent() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    game.deck = Deck(cards=[make_card(99, 7)])

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "hit")

    guest_text = " ".join(guest_user.get_spoken_messages())
    assert "Host draws" in guest_text
    assert "(7)" in guest_text


def test_twentyone_hit_plays_draw_sound_for_both_players() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    game.deck = Deck(cards=[make_card(99, 7)])

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "hit")

    assert twentyone_module.SOUND_HIT in host_user.get_sounds_played()
    assert twentyone_module.SOUND_HIT in guest_user.get_sounds_played()


def test_twentyone_target_proximity_sound_only_on_exact_target_for_actor() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 10)]
    game.deck = Deck(cards=[make_card(99, 1)])

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "hit")

    assert twentyone_module.SOUND_NEAR_BUST in host_user.get_sounds_played()
    assert twentyone_module.SOUND_NEAR_BUST not in guest_user.get_sounds_played()


def test_twentyone_target_proximity_sound_not_played_when_below_target() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    assert host_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 9)]
    game.deck = Deck(cards=[make_card(99, 1)])

    host_user.clear_messages()
    game.execute_action(p1, "hit")

    assert twentyone_module.SOUND_NEAR_BUST not in host_user.get_sounds_played()


def test_twentyone_hit_empty_deck_plays_fail_sound_for_actor() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    assert host_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    game.deck = Deck(cards=[])

    host_user.clear_messages()
    game.execute_action(p1, "hit")

    assert twentyone_module.SOUND_ACTION_FAIL in host_user.get_sounds_played()


def test_twentyone_stand_plays_actor_and_opponent_stand_sounds() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.stand_pending = False
    p2.stand_pending = False

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "stand")

    assert twentyone_module.SOUND_STAND in host_user.get_sounds_played()
    assert twentyone_module.SOUND_OPPONENT_STAND in guest_user.get_sounds_played()


def test_twentyone_check_status_shows_only_opponent_face_up_cards() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    assert host_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 6)]
    p2.hand = [make_card(3, 11), make_card(4, 4), make_card(5, 5)]
    p2.modifiers = [MODIFIER_GUARD]

    host_user.clear_messages()
    game.execute_action(p1, "check_21_status")

    host_text = " ".join(host_user.get_spoken_messages())
    assert "shown cards [4, 5]" in host_text
    assert "hole card hidden" in host_text
    assert "shown cards [11, 4, 5]" not in host_text
    assert MODIFIER_LABELS[MODIFIER_GUARD] not in host_text


def test_twentyone_keybinds_use_numbers_and_remove_h_s_t_for_turn_actions() -> None:
    game = TwentyOneGame()
    game.setup_keybinds()

    def actions_for(key: str) -> list[str]:
        return [action for keybind in game._keybinds.get(key, []) for action in keybind.actions]

    assert "hit" in actions_for("1")
    assert "stand" in actions_for("2")
    assert "play_modifier" in actions_for("3")
    assert "check_21_status" in actions_for("4")
    assert "read_21_bets" in actions_for("b")
    assert "read_21_active_effects" in actions_for("e")
    assert "hit" not in actions_for("h")
    assert "stand" not in actions_for("s")
    assert "play_modifier" not in actions_for("t")


def test_twentyone_play_modifier_options_are_one_based() -> None:
    game, p1, _ = setup_game()
    p1.modifiers = [MODIFIER_GUARD, MODIFIER_SCRAP]

    options = game._options_for_play_modifier(p1)

    assert options[0].startswith("1:")
    assert options[1].startswith("2:")


def test_twentyone_action_input_menu_selection_index_fallback_plays_choice() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_GUARD]

    game.execute_action(p1, "play_modifier")
    assert p1.id in game._pending_actions

    game.handle_event(
        p1,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection": 1,
        },
    )

    assert p1.id not in game._pending_actions
    assert MODIFIER_GUARD in p1.table_modifiers


def test_twentyone_play_modifier_menu_open_plays_menu_sound() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    assert host_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_GUARD]

    host_user.clear_messages()
    game.execute_action(p1, "play_modifier")

    assert p1.id in game._pending_actions
    assert twentyone_module.SOUND_CHANGE_MENU_OPEN in host_user.get_sounds_played()


def test_twentyone_play_modifier_invalid_selection_plays_fail_sound() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    assert host_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_GUARD]

    host_user.clear_messages()
    game.execute_action(p1, "play_modifier", "bad input")

    assert twentyone_module.SOUND_ACTION_FAIL in host_user.get_sounds_played()


def test_twentyone_read_actions_no_opponent_play_fail_sound() -> None:
    game = TwentyOneGame()
    user = MockUser("Host")
    p1 = game.add_player("Host", user)
    host_user = game.get_user(p1)
    assert host_user is not None
    game.host = "Host"
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    p1.hp = 10

    host_user.clear_messages()
    game.execute_action(p1, "read_21_opponent_face_up")
    game.execute_action(p1, "read_21_bets")

    sounds = host_user.get_sounds_played()
    assert twentyone_module.SOUND_ACTION_FAIL in sounds


def test_twentyone_round_start_plays_deal_sound() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None

    host_user.clear_messages()
    guest_user.clear_messages()
    game.on_start()

    assert twentyone_module.SOUND_ROUND_DEAL in host_user.get_sounds_played()
    assert twentyone_module.SOUND_ROUND_DEAL in guest_user.get_sounds_played()


def test_twentyone_end_game_winner_plays_game_win_sound() -> None:
    game, p1, _ = setup_game()
    host_user = game.get_user(p1)
    assert host_user is not None
    p1.hp = 5

    host_user.clear_messages()
    game._end_game(p1)

    assert twentyone_module.SOUND_GAME_WIN in host_user.get_sounds_played()


def test_twentyone_end_game_no_winner_plays_no_win_sound() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None

    host_user.clear_messages()
    guest_user.clear_messages()
    game._end_game(None)

    assert twentyone_module.SOUND_GAME_NO_WIN in host_user.get_sounds_played()
    assert twentyone_module.SOUND_GAME_NO_WIN in guest_user.get_sounds_played()


def test_twentyone_read_keys_announce_current_and_opponent_visible_cards() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    assert host_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 6)]
    p2.hand = [make_card(3, 11), make_card(4, 4), make_card(5, 5)]
    p1.table_modifiers = [MODIFIER_GUARD]
    p2.table_modifiers = [MODIFIER_RAISE_1]

    host_user.clear_messages()
    game.execute_action(p1, "read_21_hand")
    game.execute_action(p1, "read_21_opponent_face_up")
    game.execute_action(p1, "read_21_bets")
    game.execute_action(p1, "read_21_active_effects")

    host_text = " ".join(host_user.get_spoken_messages())
    assert "Your hand [10, 6] total 16." in host_text
    assert "Guest face-up cards [4, 5] total 9." in host_text
    assert "Hole card is hidden." in host_text
    assert "Current bets. Host: 1. Guest: 1." in host_text
    assert "Active effects. Host: defend. Guest: raise one." in host_text
    assert "face-up cards [11, 4, 5]" not in host_text


def test_twentyone_raise_two_plus_returns_last_face_up_card() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    game.deck = Deck(cards=[make_card(100, 3)])

    p1.modifiers = [MODIFIER_RAISE_2_PLUS]
    p1.table_modifiers = []
    p2.hand = [make_card(1, 6), make_card(2, 9)]
    p2.last_drawn_card_id = 2

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_RAISE_2_PLUS]}")

    assert p2.last_drawn_card_id is None
    assert all(card.id != 2 for card in p2.hand)
    assert MODIFIER_RAISE_2_PLUS in p1.table_modifiers
    assert game.deck is not None
    assert game.deck.cards[0].id == 2
    assert game._current_bet(p2) >= 3


def test_twentyone_play_modifier_guard_plays_defend_sound_for_both_players() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_GUARD]

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_GUARD]}")

    assert twentyone_module.SOUND_MOD_DEFEND in host_user.get_sounds_played()
    assert twentyone_module.SOUND_MOD_DEFEND in guest_user.get_sounds_played()


def test_twentyone_play_modifier_raise_plays_raise_sound_for_both_players() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_RAISE_2]

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_RAISE_2]}")

    assert twentyone_module.SOUND_MOD_RAISE in host_user.get_sounds_played()
    assert twentyone_module.SOUND_MOD_RAISE in guest_user.get_sounds_played()


def test_twentyone_scrap_returns_opponent_last_face_up_card_to_top_of_deck() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    game.deck = Deck(cards=[make_card(100, 7)])

    p1.modifiers = [MODIFIER_SCRAP]
    p2.hand = [make_card(1, 6), make_card(2, 9)]
    p2.last_drawn_card_id = 2

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_SCRAP]}")

    assert all(card.id != 2 for card in p2.hand)
    assert game.deck is not None
    assert game.deck.cards[0].id == 2


def test_twentyone_undraw_returns_own_last_face_up_card_to_top_of_deck() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    game.deck = Deck(cards=[make_card(100, 7)])

    p1.modifiers = [MODIFIER_RECYCLE]
    p1.hand = [make_card(1, 6), make_card(2, 9)]
    p1.last_drawn_card_id = 2
    p2.hand = [make_card(3, 5), make_card(4, 8)]
    p2.last_drawn_card_id = 4

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_RECYCLE]}")

    assert all(card.id != 2 for card in p1.hand)
    assert any(card.id == 4 for card in p2.hand)
    assert game.deck is not None
    assert game.deck.cards[0].id == 2


def test_twentyone_swap_draw_exchanges_most_recent_face_up_cards() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    game.deck = Deck(cards=[make_card(100, 2), make_card(101, 3), make_card(102, 4)])

    p1.modifiers = [MODIFIER_SWAP_DRAW]
    p1.hand = [make_card(1, 6), make_card(2, 9)]
    p2.hand = [make_card(3, 5), make_card(4, 8)]
    p1.last_drawn_card_id = 2
    p2.last_drawn_card_id = 4

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_SWAP_DRAW]}")

    assert all(card.id != 2 for card in p1.hand)
    assert all(card.id != 4 for card in p2.hand)
    assert any(card.id == 4 for card in p1.hand)
    assert any(card.id == 2 for card in p2.hand)
    assert p1.last_drawn_card_id == 4
    assert p2.last_drawn_card_id == 2
    assert game.deck is not None
    assert [card.id for card in game.deck.cards[:3]] == [100, 101, 102]


def test_twentyone_lockdown_locks_opponent_modifiers() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10

    p1.modifiers = [MODIFIER_LOCKDOWN]
    p2.modifiers = [MODIFIER_RAISE_1]
    p2.table_modifiers = [MODIFIER_RAISE_1]

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_LOCKDOWN]}")

    assert MODIFIER_LOCKDOWN in p1.table_modifiers
    assert game._modifiers_locked_for(p2) is True


def test_twentyone_target_card_replaces_target() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10

    p1.modifiers = [MODIFIER_TARGET_24]
    p2.table_modifiers = []

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_TARGET_24]}")

    assert game._current_target() == 24


def test_twentyone_target_card_plays_target_specific_sound() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_TARGET_24]
    p2.table_modifiers = []

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_TARGET_24]}")

    assert twentyone_module.SOUND_TARGET_24 in host_user.get_sounds_played()
    assert twentyone_module.SOUND_TARGET_24 in guest_user.get_sounds_played()


def test_twentyone_target_card_matching_current_target_is_not_playable() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_TARGET_24]
    p2.table_modifiers = [MODIFIER_TARGET_24]

    assert game._current_target() == 24
    assert game._is_single_modifier_playable(p1, MODIFIER_TARGET_24) is False
    assert game._is_play_modifier_enabled(p1) == "action-not-available"


def test_twentyone_effect_expire_plays_expire_sound() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_TARGET_24]
    p1.table_modifiers = [MODIFIER_GUARD] * 5

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_TARGET_24]}")

    assert twentyone_module.SOUND_EFFECT_EXPIRE in host_user.get_sounds_played()
    assert twentyone_module.SOUND_EFFECT_EXPIRE in guest_user.get_sounds_played()


def test_twentyone_lockdown_expire_plays_end_sound() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_TARGET_24]
    p1.table_modifiers = [MODIFIER_LOCKDOWN, MODIFIER_GUARD, MODIFIER_GUARD, MODIFIER_GUARD, MODIFIER_GUARD]

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_TARGET_24]}")

    assert twentyone_module.SOUND_LOCKDOWN_END in host_user.get_sounds_played()
    assert twentyone_module.SOUND_LOCKDOWN_END in guest_user.get_sounds_played()


def test_twentyone_redraft_plays_change_card_gain_and_loss_sounds() -> None:
    random.seed(4)
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    assert host_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_REDRAFT, MODIFIER_GUARD, MODIFIER_RAISE_1, MODIFIER_RAISE_2]

    host_user.clear_messages()
    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_REDRAFT]}")

    sounds = host_user.get_sounds_played()
    assert twentyone_module.SOUND_LOSE_CHANGE_CARD in sounds
    assert twentyone_module.SOUND_GAIN_CHANGE_CARD in sounds


def test_twentyone_sound_constants_reference_existing_client_files() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    sounds_root = repo_root / "clients" / "desktop" / "sounds"
    sound_values = [
        value
        for name, value in vars(twentyone_module).items()
        if name.startswith("SOUND_") and isinstance(value, str)
    ]

    missing = [value for value in sound_values if not (sounds_root / value).is_file()]
    assert not missing, f"Missing sound files: {missing}"


def test_twentyone_sound_reuse_is_limited_to_logical_cases() -> None:
    sound_constants = {
        name: value
        for name, value in vars(twentyone_module).items()
        if name.startswith("SOUND_") and isinstance(value, str)
    }
    by_path: dict[str, list[str]] = defaultdict(list)
    for name, path in sound_constants.items():
        by_path[path].append(name)

    shared = {path: sorted(names) for path, names in by_path.items() if len(names) > 1}
    assert shared == {
        twentyone_module.SOUND_HIT: sorted(["SOUND_HIT", "SOUND_MOD_DRAW"]),
    }


def test_twentyone_precision_draw_picks_best_non_bust_card() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10

    p1.modifiers = [MODIFIER_PRECISION_DRAW]
    p1.hand = [make_card(1, 10), make_card(2, 6)]  # total 16, best non-bust is +5
    game.deck = Deck(cards=[make_card(10, 11), make_card(11, 5), make_card(12, 4)])

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_PRECISION_DRAW]}")

    assert any(card.rank == 5 for card in p1.hand)


def test_twentyone_precision_draw_uses_lowest_card_when_all_choices_bust() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10

    p1.modifiers = [MODIFIER_PRECISION_DRAW]
    p1.hand = [make_card(1, 10), make_card(2, 10)]  # total 20, all deck options bust
    game.deck = Deck(cards=[make_card(10, 11), make_card(11, 3), make_card(12, 2)])

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_PRECISION_DRAW]}")

    assert any(card.rank == 2 for card in p1.hand)


def test_twentyone_trojan_horse_uses_lowest_card_when_all_choices_bust() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10

    p1.modifiers = [MODIFIER_AID_RIVAL]
    p2.hand = [make_card(1, 10), make_card(2, 10)]  # total 20, all deck options bust
    game.deck = Deck(cards=[make_card(10, 11), make_card(11, 3), make_card(12, 2)])

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_AID_RIVAL]}")

    assert any(card.rank == 2 for card in p2.hand)


def test_twentyone_hit_keeps_turn_until_stand() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 7)]
    game.deck = Deck(cards=[make_card(3, 2)])

    game.execute_action(p1, "hit")

    assert game.current_player == p1
    assert game.phase == "turns"
    assert len(p1.hand) == 3


def test_twentyone_play_modifier_keeps_turn_until_stand() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_GUARD]

    game.execute_action(p1, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_GUARD]}")

    assert game.current_player == p1
    assert game.phase == "turns"
    assert MODIFIER_GUARD in p1.table_modifiers


def test_twentyone_round_settles_only_after_consecutive_stands() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 9)]
    p2.hand = [make_card(3, 8), make_card(4, 9)]
    game.deck = Deck(cards=[make_card(5, 1)])

    game.execute_action(p1, "stand")
    assert p1.stand_pending is True
    assert game.current_player == p2
    assert game.phase == "turns"

    game.execute_action(p2, "hit")
    assert p1.stand_pending is False
    assert p2.stand_pending is False
    assert game.current_player == p2
    assert game.phase == "turns"

    game.execute_action(p2, "stand")
    assert p2.stand_pending is True
    assert game.current_player == p1
    assert game.phase == "turns"

    game.execute_action(p1, "stand")
    assert game.phase == "between_rounds"


def test_twentyone_round_settle_transition_plays_resolve_sound() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 9)]
    p2.hand = [make_card(3, 8), make_card(4, 9)]
    game.deck = Deck(cards=[make_card(5, 1)])

    host_user.clear_messages()
    guest_user.clear_messages()
    game.execute_action(p1, "stand")
    game.execute_action(p2, "stand")

    assert twentyone_module.SOUND_ROUND_RESOLVE in host_user.get_sounds_played()
    assert twentyone_module.SOUND_ROUND_RESOLVE in guest_user.get_sounds_played()


def test_twentyone_modifier_play_between_stands_resets_pending_stands() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p2.modifiers = [MODIFIER_GUARD]

    game.execute_action(p1, "stand")
    assert p1.stand_pending is True
    assert game.current_player == p2

    game.execute_action(p2, "play_modifier", f"1:{MODIFIER_LABELS[MODIFIER_GUARD]}")

    assert p1.stand_pending is False
    assert p2.stand_pending is False
    assert game.current_player == p2
    assert game.phase == "turns"


def test_twentyone_both_bust_closer_to_target_wins() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 11), make_card(2, 11)]  # 22
    p2.hand = [make_card(3, 11), make_card(4, 11), make_card(5, 1)]  # 23

    game._settle_round()

    assert p1.hp == 10
    assert p2.hp == 9


def test_twentyone_round_outcome_plays_private_win_lose_sounds() -> None:
    game, p1, p2 = setup_game()
    host_user = game.get_user(p1)
    guest_user = game.get_user(p2)
    assert host_user is not None
    assert guest_user is not None
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 9)]  # 19
    p2.hand = [make_card(3, 8), make_card(4, 9)]  # 17

    host_user.clear_messages()
    guest_user.clear_messages()
    game._settle_round()

    assert twentyone_module.SOUND_ROUND_WIN in host_user.get_sounds_played()
    assert twentyone_module.SOUND_ROUND_LOSE in guest_user.get_sounds_played()


def test_twentyone_play_modifier_unavailable_when_no_playable_change_cards() -> None:
    game, p1, p2 = setup_game()
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p1, p2], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_GUARD]
    p1.table_modifiers = [MODIFIER_GUARD] * 5

    assert game._is_play_modifier_enabled(p1) == "action-not-available"


def test_twentyone_bot_select_play_modifier_returns_none_when_none_playable() -> None:
    game, p1, p2 = setup_game()
    p1.hp = 10
    p2.hp = 10
    p1.modifiers = [MODIFIER_GUARD]
    p1.table_modifiers = [MODIFIER_GUARD] * 5
    options = game._options_for_play_modifier(p1)

    assert game._bot_select_play_modifier(p1, options) is None


def test_twentyone_bot_think_stands_when_change_cards_exist_but_none_playable() -> None:
    game = TwentyOneGame()
    human = MockUser("Host")
    bot_user = Bot("GuestBot")
    p1 = game.add_player("Host", human)
    p2 = game.add_player("GuestBot", bot_user)
    game.host = "Host"
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p2, p1], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 10)]
    p2.hand = [make_card(3, 10), make_card(4, 9)]
    p2.modifiers = [MODIFIER_GUARD]
    p2.table_modifiers = [MODIFIER_GUARD] * 5

    assert game.bot_think(p2) == "stand"


def test_twentyone_bot_think_hits_when_change_cards_unplayable_and_below_target() -> None:
    game = TwentyOneGame()
    human = MockUser("Host")
    bot_user = Bot("GuestBot")
    p1 = game.add_player("Host", human)
    p2 = game.add_player("GuestBot", bot_user)
    game.host = "Host"
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p2, p1], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 7)]
    p2.hand = [make_card(3, 8), make_card(4, 7)]
    p2.modifiers = [MODIFIER_GUARD]
    p2.table_modifiers = [MODIFIER_GUARD] * 5

    assert game.bot_think(p2) == "hit"


def test_twentyone_bot_does_not_replay_same_target_card() -> None:
    game = TwentyOneGame()
    human = MockUser("Host")
    bot_user = Bot("GuestBot")
    p1 = game.add_player("Host", human)
    p2 = game.add_player("GuestBot", bot_user)
    game.host = "Host"
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p2, p1], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 7), make_card(2, 8)]
    p2.hand = [make_card(3, 8), make_card(4, 8)]
    p1.table_modifiers = [MODIFIER_TARGET_24]
    p2.modifiers = [MODIFIER_TARGET_24]

    assert game._current_target() == 24
    assert game._is_single_modifier_playable(p2, MODIFIER_TARGET_24) is False
    assert game.bot_think(p2) == "hit"


def test_twentyone_bot_turn_advances_when_change_cards_are_unplayable() -> None:
    game = TwentyOneGame()
    human = MockUser("Host")
    bot_user = Bot("GuestBot")
    p1 = game.add_player("Host", human)
    p2 = game.add_player("GuestBot", bot_user)
    game.host = "Host"
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p2, p1], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 10), make_card(2, 10)]
    p2.hand = [make_card(3, 10), make_card(4, 9)]
    p2.modifiers = [MODIFIER_GUARD]
    p2.table_modifiers = [MODIFIER_GUARD] * 5
    p2.bot_think_ticks = 0
    p2.bot_pending_action = None

    game.on_tick()
    game.on_tick()
    game.on_tick()

    assert game.current_player == p1
    assert p2.stand_pending is True
    assert game.phase == "turns"


def test_twentyone_bot_think_plays_change_card_when_high_priority_playable() -> None:
    game = TwentyOneGame()
    human = MockUser("Host")
    bot_user = Bot("GuestBot")
    p1 = game.add_player("Host", human)
    p2 = game.add_player("GuestBot", bot_user)
    game.host = "Host"
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p2, p1], reset_index=True)
    p1.hp = 10
    p2.hp = 9
    p1.hand = [make_card(1, 10), make_card(2, 11)]
    p2.hand = [make_card(3, 7), make_card(4, 6)]
    p2.modifiers = [MODIFIER_GUARD]
    p2.table_modifiers = []

    assert game.bot_think(p2) == "play_modifier"


def test_twentyone_bot_select_prefers_defend_when_likely_losing() -> None:
    game = TwentyOneGame()
    human = MockUser("Host")
    bot_user = Bot("GuestBot")
    p1 = game.add_player("Host", human)
    p2 = game.add_player("GuestBot", bot_user)
    game.host = "Host"
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p2, p1], reset_index=True)
    p1.hp = 10
    p2.hp = 9
    p1.hand = [make_card(1, 10), make_card(2, 11)]
    p2.hand = [make_card(3, 7), make_card(4, 6)]
    p2.modifiers = [MODIFIER_REDRAFT, MODIFIER_GUARD]
    p2.table_modifiers = []

    options = game._options_for_play_modifier(p2)
    chosen = game._bot_select_play_modifier(p2, options)

    assert chosen is not None
    assert chosen.startswith(f"2:{MODIFIER_LABELS[MODIFIER_GUARD]}")


def test_twentyone_bot_select_uses_raise_when_confident_winning() -> None:
    game = TwentyOneGame()
    human = MockUser("Host")
    bot_user = Bot("GuestBot")
    p1 = game.add_player("Host", human)
    p2 = game.add_player("GuestBot", bot_user)
    game.host = "Host"
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p2, p1], reset_index=True)
    p1.hp = 8
    p2.hp = 10
    p1.hand = [make_card(1, 2), make_card(2, 9)]
    p2.hand = [make_card(3, 10), make_card(4, 10)]
    p2.modifiers = [MODIFIER_RAISE_2]
    p2.table_modifiers = []

    assert game.bot_think(p2) == "play_modifier"
    options = game._options_for_play_modifier(p2)
    chosen = game._bot_select_play_modifier(p2, options)
    assert chosen is not None
    assert chosen.startswith(f"1:{MODIFIER_LABELS[MODIFIER_RAISE_2]}")


def test_twentyone_bot_decision_does_not_depend_on_opponent_hidden_card() -> None:
    def build_game(hidden_rank: int) -> tuple[TwentyOneGame, object, object]:
        game = TwentyOneGame()
        human = MockUser("Host")
        bot_user = Bot("GuestBot")
        p1 = game.add_player("Host", human)
        p2 = game.add_player("GuestBot", bot_user)
        game.host = "Host"
        game.status = "playing"
        game.game_active = True
        game.phase = "turns"
        game.set_turn_players([p2, p1], reset_index=True)
        p1.hp = 10
        p2.hp = 10
        p1.hand = [make_card(1, hidden_rank), make_card(2, 10)]
        p2.hand = [make_card(3, 10), make_card(4, 9)]
        p2.modifiers = [MODIFIER_RAISE_1]
        return game, p1, p2

    game_low, _, bot_low = build_game(1)
    game_high, _, bot_high = build_game(11)

    assert game_low.bot_think(bot_low) == game_high.bot_think(bot_high)


def test_twentyone_bot_holds_nonoptimal_playable_change_card_for_later() -> None:
    game = TwentyOneGame()
    human = MockUser("Host")
    bot_user = Bot("GuestBot")
    p1 = game.add_player("Host", human)
    p2 = game.add_player("GuestBot", bot_user)
    game.host = "Host"
    game.status = "playing"
    game.game_active = True
    game.phase = "turns"
    game.set_turn_players([p2, p1], reset_index=True)
    p1.hp = 10
    p2.hp = 10
    p1.hand = [make_card(1, 3), make_card(2, 9)]
    p2.hand = [make_card(3, 8), make_card(4, 7)]
    p2.modifiers = [MODIFIER_LOCKDOWN]
    p2.table_modifiers = []
    p1.modifiers = []

    assert game.bot_think(p2) == "hit"


def test_twentyone_bot_game_completes_and_reloads() -> None:
    random.seed(12345)
    game = TwentyOneGame(
        options=TwentyOneOptions(
            starting_health=4,
            base_bet=1,
            starting_modifiers_per_round=1,
            draw_modifier_chance_percent=25,
            deck_count=1,
            next_round_wait_ticks=5,
        )
    )
    bots = [Bot(f"Bot{i}") for i in range(2)]
    for bot in bots:
        game.add_player(bot.username, bot)
    game.on_start()

    for tick in range(80000):
        if game.status == "finished":
            break
        if tick > 0 and tick % 100 == 0:
            users = dict(game._users)
            keybinds = dict(game._keybinds)
            payload = game.to_json()
            game = TwentyOneGame.from_json(payload)
            game._users = users
            game._keybinds = keybinds
            game.rebuild_runtime_state()
            for player in game.players:
                if game.get_user(player):
                    game.setup_player_actions(player)
        game.on_tick()

    assert game.status == "finished"
