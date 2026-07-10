"""Tests for the classic Monopoly implementation."""

from server.core.users.bot import Bot
from server.core.users.test_user import MockUser
from server.games.registry import GameRegistry
from server.games.monopoly.board import CHANCE_CARD_IDS, COMMUNITY_CHEST_CARD_IDS, get_board
from server.games.monopoly.game import (
    UK_CLASSIC_RULESET,
    UK_SHORT_RULESET,
    UK_TIME_LIMIT_RULESET,
    US_SPEED_DIE_RULESET,
    MonopolyGame,
    MonopolyPlayer,
)


def make_game() -> tuple[MonopolyGame, MonopolyPlayer, MonopolyPlayer]:
    game = MonopolyGame()
    alice = game.add_player("Alice", MockUser("Alice"))
    bob = game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    game.reset_turn_order()
    return game, alice, bob  # type: ignore[return-value]


def test_classic_board_definition_has_expected_shape():
    board = get_board()

    assert board.name == "Classic Monopoly"
    assert len(board.spaces) == 40
    assert len(board.purchasable_spaces) == 28
    assert len(CHANCE_CARD_IDS) == 16
    assert len(COMMUNITY_CHEST_CARD_IDS) == 16
    assert board.get_space("boardwalk").price == 400
    assert board.get_space("boardwalk").rents == (50, 200, 600, 1400, 1700, 2000)


def test_ruleset_selection_switches_board_currency_and_speed_die_starting_cash():
    game = MonopolyGame()
    game.options.ruleset = UK_CLASSIC_RULESET
    game.add_player("Alice", MockUser("Alice"))
    game.add_player("Bob", MockUser("Bob"))
    game.on_start()

    assert game.board_id == "uk_classic"
    assert game.board.name == "Waddingtons Monopoly"
    assert game.board.get_space_at(1).name == "Old Kent Road"
    assert game._money(200) == "£200"

    speed_game = MonopolyGame()
    speed_game.options.ruleset = US_SPEED_DIE_RULESET
    alice = speed_game.add_player("Alice", MockUser("Alice"))
    speed_game.add_player("Bob", MockUser("Bob"))
    speed_game.on_start()

    assert speed_game.uses_speed_die is True
    assert speed_game.board_id == "classic"
    assert alice.cash == 2500


def test_uk_card_destinations_follow_waddingtons_board():
    game = MonopolyGame()
    game.options.ruleset = UK_CLASSIC_RULESET
    alice = game.add_player("Alice", MockUser("Alice"))
    game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    alice.position = 20

    game._apply_card(alice, "advance_to_st_charles_place", roll_total=7)

    assert alice.position == 39
    assert game._space_at(alice.position).name == "Mayfair"
    assert game._card_text("advance_to_st_charles_place") == "Advance to Mayfair. If you pass GO, collect £200."


def test_uk_short_game_deals_two_deeds_and_ends_after_second_bankruptcy():
    game = MonopolyGame()
    game.options.ruleset = UK_SHORT_RULESET
    alice = game.add_player("Alice", MockUser("Alice"))
    bob = game.add_player("Bob", MockUser("Bob"))
    game.add_player("Cara", MockUser("Cara"))
    game.on_start()
    assert len(game._owned_spaces(alice)) == 2
    assert len(game._owned_spaces(bob)) == 2
    bob.bankrupt = True
    game._check_for_winner()
    assert game.game_active is True
    game.players[2].bankrupt = True
    game._check_for_winner()
    assert game.game_active is False


def test_uk_auctions_allow_a_one_pound_opening_bid():
    game, alice, _bob = make_game()
    game.options.ruleset = UK_CLASSIC_RULESET
    game.ruleset_id = UK_CLASSIC_RULESET
    game.pending_purchase_property_id = "baltic_avenue"
    game.phase = "await_purchase"
    game.execute_action(alice, "auction_property")
    assert game._minimum_auction_bid() == 1


def test_uk_time_limit_uses_customizable_duration():
    game = MonopolyGame()
    game.options.ruleset = UK_TIME_LIMIT_RULESET
    game.options.time_limit_minutes = 5
    alice = game.add_player("Alice", MockUser("Alice"))
    game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    alice.cash = 2000
    game.sound_scheduler_tick = game.ruleset_started_tick + 5 * 60 * 20
    game.on_tick()
    assert game.game_active is False
    assert game.winner_id == alice.id


def test_speed_die_unlocks_after_passing_go():
    game = MonopolyGame()
    game.options.ruleset = US_SPEED_DIE_RULESET
    alice = game.add_player("Alice", MockUser("Alice"))
    game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    alice.position = 39

    game._move_steps(alice, 2)

    assert alice.speed_die_unlocked is True
    assert alice.cash == 2700


def test_speed_die_bus_offers_white_die_or_total(monkeypatch):
    game = MonopolyGame()
    game.options.ruleset = US_SPEED_DIE_RULESET
    alice = game.add_player("Alice", MockUser("Alice"))
    game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    game.reset_turn_order()
    alice.speed_die_unlocked = True
    dice = iter([1, 2, 4])  # white dice 1 + 2, then the Bus
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda *_: next(dice))

    game.execute_action(alice, "roll")

    assert game.phase == "await_speed_die_move"
    assert game.speed_die_action == "bus"
    assert game._speed_die_move_options(alice) == [
        "first|Move 1 spaces",
        "second|Move 2 spaces",
        "sum|Move 3 spaces",
    ]

    game.execute_action(alice, "speed_die_move", "sum|Move 3 spaces")

    assert alice.position == 3
    assert game.pending_purchase_property_id == "baltic_avenue"


def test_speed_die_three_of_a_kind_allows_any_destination(monkeypatch):
    game = MonopolyGame()
    game.options.ruleset = US_SPEED_DIE_RULESET
    alice = game.add_player("Alice", MockUser("Alice"))
    game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    game.reset_turn_order()
    alice.speed_die_unlocked = True
    dice = iter([2, 2, 2])
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda *_: next(dice))

    game.execute_action(alice, "roll")
    game.execute_action(alice, "speed_die_move", "39|Move to Boardwalk")

    assert alice.position == 39
    assert alice.cash == 2500
    assert game.pending_purchase_property_id == "boardwalk"


def test_mr_monopoly_advances_to_next_unowned_property(monkeypatch):
    game = MonopolyGame()
    game.options.ruleset = US_SPEED_DIE_RULESET
    alice = game.add_player("Alice", MockUser("Alice"))
    game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    game.reset_turn_order()
    alice.speed_die_unlocked = True
    game.property_states["baltic_avenue"].owner_id = alice.id
    dice = iter([1, 2, 5])  # white dice 1 + 2, then Mr. Monopoly
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda *_: next(dice))

    game.execute_action(alice, "roll")

    assert alice.position == 5
    assert game.pending_purchase_property_id == "reading_railroad"


def test_start_initializes_players_and_property_bank():
    game, alice, bob = make_game()

    assert game.get_name() == "Monopoly"
    assert game.get_type() == "monopoly"
    assert game.get_max_players() == 8
    assert alice.cash == 1500
    assert bob.cash == 1500
    assert len(game.property_states) == 28
    assert game.bank_houses == 32
    assert game.bank_hotels == 12


def test_monopoly_is_registered_in_board_games_category():
    board_games = GameRegistry.get_by_category()["category-board-games"]

    assert any(game_class.get_type() == "monopoly" for game_class in board_games)


def test_buy_property_assigns_deed_and_charges_cash():
    game, alice, _bob = make_game()
    game.pending_purchase_property_id = "mediterranean_avenue"
    game.phase = "await_purchase"

    game.execute_action(alice, "buy_property")

    assert game.property_states["mediterranean_avenue"].owner_id == alice.id
    assert alice.cash == 1440
    assert game.pending_purchase_property_id == ""
    assert game.current_player == _bob
    assert game.phase == "await_roll"


def test_unimproved_complete_color_set_doubles_rent():
    game, alice, bob = make_game()
    game.property_states["mediterranean_avenue"].owner_id = alice.id
    game.property_states["baltic_avenue"].owner_id = alice.id
    bob.position = 1

    complete = game._resolve_landing(bob, roll_total=7)

    assert complete is True
    assert bob.cash == 1496
    assert alice.cash == 1504


def test_building_uses_even_build_rule_and_increases_rent():
    game, alice, bob = make_game()
    game.property_states["mediterranean_avenue"].owner_id = alice.id
    game.property_states["baltic_avenue"].owner_id = alice.id

    game.execute_action(alice, "build_house", "mediterranean_avenue|Mediterranean Avenue")

    assert game.property_states["mediterranean_avenue"].houses == 1
    assert game.bank_houses == 31
    assert alice.cash == 1450

    bob.position = 1
    assert game._resolve_landing(bob, roll_total=5) is True
    assert bob.cash == 1490
    assert alice.cash == 1460


def test_auction_awards_property_to_high_bidder_after_others_pass():
    game, alice, bob = make_game()
    game.pending_purchase_property_id = "baltic_avenue"
    game.phase = "await_purchase"

    game.execute_action(alice, "auction_property")
    game.execute_action(bob, "auction_bid", "70")
    game.execute_action(alice, "auction_pass")

    assert game.auction is None
    assert game.property_states["baltic_avenue"].owner_id == bob.id
    assert bob.cash == 1430


def test_debt_can_be_resolved_by_mortgaging_property():
    game, alice, bob = make_game()
    game.property_states["boardwalk"].owner_id = alice.id
    bob.cash = 25
    bob.position = 39

    assert game._resolve_landing(bob, roll_total=8) is False
    assert game.pending_debt is not None
    assert game.pending_debt.amount == 50

    game.property_states["reading_railroad"].owner_id = bob.id
    game.execute_action(bob, "mortgage_property", "reading_railroad|Reading Railroad")
    game.execute_action(bob, "pay_debt")

    assert game.pending_debt is None
    assert bob.cash == 75
    assert alice.cash == 1550


def test_non_current_debt_payment_completes_current_turn():
    game, alice, bob = make_game()
    game._set_debt(bob, 10, alice, "birthday")

    game.execute_action(bob, "pay_debt")

    assert game.pending_debt is None
    assert alice.cash == 1510
    assert bob.cash == 1490
    assert game.current_player == bob
    assert game.phase == "await_roll"


def test_trade_sells_property_for_cash():
    game, alice, bob = make_game()
    game.property_states["mediterranean_avenue"].owner_id = alice.id

    game.execute_action(alice, "offer_trade", f"{bob.id}|Bob")
    game.execute_action(alice, "trade_give", "mediterranean_avenue|Mediterranean Avenue")
    game.execute_action(alice, "trade_cash", "-73")  # Bob pays Alice $73
    game.execute_action(alice, "trade_send")
    game.execute_action(bob, "accept_trade")

    assert game.pending_trade is None
    assert game.property_states["mediterranean_avenue"].owner_id == bob.id
    assert alice.cash == 1573
    assert bob.cash == 1427


def test_asset_actions_are_visible_on_main_turn_menu_when_available():
    game, alice, _bob = make_game()
    game.property_states["mediterranean_avenue"].owner_id = alice.id

    visible_ids = [resolved.action.id for resolved in game.get_all_visible_actions(alice)]

    assert "check_assets" in visible_ids
    assert "check_board" in visible_ids
    assert "mortgage_property" in visible_ids
    assert "offer_trade" in visible_ids


def test_trade_rejects_improved_color_group_properties():
    game, alice, bob = make_game()
    game.property_states["mediterranean_avenue"].owner_id = alice.id
    game.property_states["baltic_avenue"].owner_id = alice.id
    game.property_states["mediterranean_avenue"].houses = 1

    game.execute_action(alice, "offer_trade", f"{bob.id}|Bob")
    options = game._trade_give_options(alice)

    assert not any("Mediterranean Avenue" in option for option in options)
    assert not any("Baltic Avenue" in option for option in options)


def test_trade_mortgaged_property_charges_transfer_interest():
    game, alice, bob = make_game()
    game.property_states["reading_railroad"].owner_id = alice.id
    game.property_states["reading_railroad"].mortgaged = True

    game.execute_action(alice, "offer_trade", f"{bob.id}|Bob")
    game.execute_action(alice, "trade_give", "reading_railroad|Reading Railroad")
    game.execute_action(alice, "trade_cash", "-100")  # Bob pays Alice $100
    game.execute_action(alice, "trade_send")
    game.execute_action(bob, "accept_trade")

    assert game.property_states["reading_railroad"].owner_id == bob.id
    assert game.property_states["reading_railroad"].mortgaged is True
    assert alice.cash == 1600
    assert bob.cash == 1390


def test_trade_get_out_of_jail_card_for_cash():
    game, alice, bob = make_game()
    alice.jail_free_cards.append("get_out_of_jail_free_chance")

    game.execute_action(alice, "offer_trade", f"{bob.id}|Bob")
    game.execute_action(alice, "trade_jail", "give|Include your Get Out of Jail Free card")
    game.execute_action(alice, "trade_cash", "-50")  # Bob pays Alice $50
    game.execute_action(alice, "trade_send")
    game.execute_action(bob, "accept_trade")

    assert alice.jail_free_cards == []
    assert bob.jail_free_cards == ["get_out_of_jail_free_chance"]
    assert alice.cash == 1550
    assert bob.cash == 1450


def test_completed_non_double_turn_advances_automatically():
    game, alice, bob = make_game()

    game._complete_roll_resolution(alice)

    assert game.current_player == bob
    assert game.phase == "await_roll"


def test_doubles_keep_turn_for_extra_roll():
    game, alice, _bob = make_game()
    game.extra_roll_pending = True

    game._complete_roll_resolution(alice)

    assert game.current_player == alice
    assert game.phase == "await_roll"


def test_bankruptcy_transfers_assets_to_creditor_and_finishes_game():
    game, alice, bob = make_game()
    game.property_states["boardwalk"].owner_id = bob.id
    bob.cash = 0
    game._set_debt(bob, 100, alice, "rent")

    game.execute_action(bob, "declare_bankruptcy")

    assert bob.bankrupt is True
    assert game.property_states["boardwalk"].owner_id == alice.id
    assert game.game_active is False
    assert game.winner_id == alice.id


def test_serialization_preserves_monopoly_state():
    game, alice, _bob = make_game()
    game.property_states["park_place"].owner_id = alice.id
    game.property_states["park_place"].mortgaged = True
    alice.cash = 1234

    loaded = MonopolyGame.from_json(game.to_json())

    assert loaded.players[0].cash == 1234
    assert loaded.property_states["park_place"].owner_id == alice.id
    assert loaded.property_states["park_place"].mortgaged is True


def test_bot_game_progresses_without_crashing():
    game = MonopolyGame()
    bot1 = Bot("Bot1")
    bot2 = Bot("Bot2")
    game.add_player("Bot1", bot1)
    game.add_player("Bot2", bot2)
    game.on_start()

    for _ in range(400):
        game.on_tick()
        if not game.game_active:
            break

    assert game.status in {"playing", "finished"}


def test_starting_cash_option_sets_player_balances():
    game = MonopolyGame()
    game.options.starting_cash = 2500
    alice = game.add_player("Alice", MockUser("Alice"))
    bob = game.add_player("Bob", MockUser("Bob"))
    game.on_start()

    assert alice.cash == 2500
    assert bob.cash == 2500


def test_free_parking_does_nothing_by_default():
    game, alice, _bob = make_game()
    alice.position = 20  # Free Parking

    assert game._resolve_landing(alice, roll_total=6) is True
    assert alice.cash == 1500
    assert game.free_parking_pot == 0


def test_free_parking_jackpot_accumulates_taxes_and_pays_out():
    game = MonopolyGame()
    game.options.free_parking_jackpot = True
    alice = game.add_player("Alice", MockUser("Alice"))
    bob = game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    game.reset_turn_order()

    # Income Tax ($200) is paid to the bank and routed into the pot.
    alice.position = 4
    assert game._resolve_landing(alice, roll_total=4) is True
    assert alice.cash == 1300
    assert game.free_parking_pot == 200

    # Landing on Free Parking wins the pot, which then resets to the seed (0).
    bob.position = 20
    assert game._resolve_landing(bob, roll_total=6) is True
    assert bob.cash == 1700
    assert game.free_parking_pot == 0


def test_free_parking_pot_seeds_and_resets_to_seed():
    game = MonopolyGame()
    game.options.free_parking_jackpot = True
    game.options.free_parking_seed = 100
    alice = game.add_player("Alice", MockUser("Alice"))
    bob = game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    game.reset_turn_order()

    # The pot starts at the seed amount.
    assert game.free_parking_pot == 100

    # Luxury Tax ($100) accumulates on top of the seed.
    alice.position = 38
    assert game._resolve_landing(alice, roll_total=2) is True
    assert game.free_parking_pot == 200

    bob.position = 20
    assert game._resolve_landing(bob, roll_total=6) is True
    assert bob.cash == 1700
    assert game.free_parking_pot == 100  # reset to seed, not zero


def test_card_cash_message_uses_card_reason_not_literal_card():
    game, alice, _bob = make_game()
    user = game.get_user(alice)
    user.clear_messages()

    game.community_chest_deck = ["beauty_contest_collect_10"]

    assert game._draw_card(alice, "community_chest", roll_total=7) is True

    spoken = user.get_spoken_messages()
    assert any("collected $10 for beauty contest prize" in message for message in spoken)
    assert not any("for card" in message for message in spoken)


def test_non_current_player_has_no_turn_menu_but_escape_actions_still_work():
    game, alice, bob = make_game()
    other = bob if game.current_player == alice else alice
    other_user = game.get_user(other)

    game.rebuild_all_menus()

    assert "turn_menu" not in other_user.menus

    game.execute_action(other, "show_actions")

    action_menu = other_user.menus["actions_menu"]
    action_ids = [item.id for item in action_menu["items"]]
    assert "leave_game" in action_ids


def test_jackpot_deferred_bank_debt_feeds_pot_when_paid():
    game = MonopolyGame()
    game.options.free_parking_jackpot = True
    alice = game.add_player("Alice", MockUser("Alice"))
    _bob = game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    game.reset_turn_order()

    # Alice cannot afford the $200 Income Tax up front, so it becomes a debt.
    alice.cash = 50
    alice.position = 4
    assert game._resolve_landing(alice, roll_total=4) is False
    assert game.pending_debt is not None
    assert game.free_parking_pot == 0  # not collected yet

    # Once she raises funds and pays, the bank income still feeds the pot.
    alice.cash = 200
    game.execute_action(alice, "pay_debt")
    assert game.pending_debt is None
    assert game.free_parking_pot == 200


def test_trade_builder_bundles_multiple_properties_and_cash():
    game, alice, bob = make_game()
    game.property_states["boardwalk"].owner_id = alice.id
    game.property_states["park_place"].owner_id = alice.id
    game.property_states["baltic_avenue"].owner_id = bob.id

    game.execute_action(alice, "offer_trade", f"{bob.id}|Bob")
    game.execute_action(alice, "trade_give", "boardwalk|Boardwalk")
    game.execute_action(alice, "trade_give", "park_place|Park Place")
    game.execute_action(alice, "trade_request", "baltic_avenue|Baltic Avenue")
    game.execute_action(alice, "trade_cash", "200")  # Alice pays Bob $200
    game.execute_action(alice, "trade_send")

    assert game.pending_trade is not None
    assert set(game.pending_trade.give_property_ids) == {"boardwalk", "park_place"}
    assert game.pending_trade.receive_property_ids == ["baltic_avenue"]

    game.execute_action(bob, "accept_trade")

    assert game.property_states["boardwalk"].owner_id == bob.id
    assert game.property_states["park_place"].owner_id == bob.id
    assert game.property_states["baltic_avenue"].owner_id == alice.id
    assert alice.cash == 1300
    assert bob.cash == 1700


def test_trade_partner_menu_hides_encoded_ids():
    game, alice, bob = make_game()
    current = game._active_player(game.current_player)
    user = game.get_user(current)

    # No input value -> the framework presents the partner picker menu.
    game.execute_action(current, "offer_trade")

    menu = user.menus["action_input_menu"]
    texts = [item.text for item in menu["items"]]
    ids = [item.id for item in menu["items"]]

    # The shown label is the plain player name; the selection value still
    # carries the "playerid|name" encoding so resolution stays unambiguous.
    assert "Bob" in texts
    assert all("|" not in text for text in texts)
    assert any("|" in option_id for option_id in ids)


def test_property_menu_hides_encoded_ids():
    game, alice, _bob = make_game()
    game.property_states["reading_railroad"].owner_id = alice.id

    game.execute_action(alice, "mortgage_property")

    menu = game.get_user(alice).menus["action_input_menu"]
    texts = [item.text for item in menu["items"]]
    assert any(text.startswith("Reading Railroad") for text in texts)
    assert all("|" not in text for text in texts)


def test_trade_builder_toggle_removes_property():
    game, alice, bob = make_game()
    game.property_states["boardwalk"].owner_id = alice.id

    game.execute_action(alice, "offer_trade", f"{bob.id}|Bob")
    game.execute_action(alice, "trade_give", "boardwalk|Boardwalk")
    assert game.trade_draft_offers[alice.id].give_property_ids == ["boardwalk"]

    game.execute_action(alice, "trade_give", "boardwalk|Boardwalk")  # toggle off
    assert game.trade_draft_offers[alice.id].give_property_ids == []


def test_trade_builder_cancel_discards_draft():
    game, alice, bob = make_game()

    game.execute_action(alice, "offer_trade", f"{bob.id}|Bob")
    assert alice.id in game.trade_draft_offers

    game.execute_action(alice, "trade_cancel")
    assert alice.id not in game.trade_draft_offers


def test_turn_start_focuses_roll_not_check_assets():
    game, alice, bob = make_game()
    current = game._active_player(game.current_player)
    user = game.get_user(current)

    game._start_turn(rebuild_all=True)

    menu = user.menus["turn_menu"]
    assert menu["position"] == 1
    assert menu["items"][0].id == "roll"


def test_landing_on_unowned_property_focuses_buy(monkeypatch):
    game, alice, bob = make_game()
    current = game._active_player(game.current_player)
    user = game.get_user(current)

    dice = iter([1, 2])  # total 3 from GO -> Baltic Avenue (unowned), not a double

    def fake_randint(low, high):
        if (low, high) == (1, 6):
            return next(dice)
        return high

    monkeypatch.setattr("server.games.monopoly.game.random.randint", fake_randint)

    game.execute_action(current, "roll")

    assert game.pending_purchase_property_id == "baltic_avenue"
    menu = user.menus["turn_menu"]
    assert menu["position"] == 1
    assert menu["items"][0].id == "buy_property"


def test_trade_builder_focuses_menu_on_builder_actions():
    game, alice, bob = make_game()

    ids_before = {rv.action.id for rv in game.get_all_visible_actions(alice)}
    assert "offer_trade" in ids_before
    assert not any(action_id.startswith("trade_") for action_id in ids_before)

    game.execute_action(alice, "offer_trade", f"{bob.id}|Bob")

    ids_building = {rv.action.id for rv in game.get_all_visible_actions(alice)}
    assert ids_building
    assert all(action_id.startswith("trade_") for action_id in ids_building)
    assert {"trade_give", "trade_request", "trade_send", "trade_cancel"} <= ids_building
    assert "roll" not in ids_building
