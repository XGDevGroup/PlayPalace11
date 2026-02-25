import random

from server.core.users.bot import Bot
from server.core.users.test_user import MockUser
from server.game_utils.cards import Card, Deck
from server.games.twentyone import (
    MODIFIER_LABELS,
    MODIFIER_GUARD,
    MODIFIER_LOCKDOWN,
    MODIFIER_TARGET_24,
    MODIFIER_RAISE_1,
    MODIFIER_PRECISION_DRAW,
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

    assert "game_cards/draw3.ogg" in host_user.get_sounds_played()
    assert "game_cards/draw3.ogg" in guest_user.get_sounds_played()


def test_twentyone_stand_plays_stand_sound_for_both_players() -> None:
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

    assert "game_pig/bank.ogg" in host_user.get_sounds_played()
    assert "game_pig/bank.ogg" in guest_user.get_sounds_played()


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


def test_twentyone_play_modifier_plays_change_card_sound_for_both_players() -> None:
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

    assert "game_cards/play1.ogg" in host_user.get_sounds_played()
    assert "game_cards/play1.ogg" in guest_user.get_sounds_played()


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

    assert "game_pig/win.ogg" in host_user.get_sounds_played()
    assert "game_pig/lose.ogg" in guest_user.get_sounds_played()


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
