"""Focused tests for Jurassic Park Monopoly board behavior."""

from server.core.users.test_user import MockUser
from server.games.monopoly.game import MonopolyGame, MonopolyOptions, MonopolyPlayer


def _start_jurassic_game() -> tuple[MonopolyGame, MonopolyPlayer, MonopolyPlayer]:
    game = MonopolyGame(
        options=MonopolyOptions(
            preset_id="classic_standard",
            board_id="jurassic_park",
            board_rules_mode="auto",
        )
    )
    alice = game.add_player("Alice", MockUser("Alice"))
    bob = game.add_player("Bob", MockUser("Bob"))
    game.on_start()
    assert isinstance(alice, MonopolyPlayer)
    assert isinstance(bob, MonopolyPlayer)
    assert game.active_board_id == "jurassic_park"
    assert game.active_board_effective_mode == "board_rules"
    return game, alice, bob


def test_jurassic_board_normalizes_special_space_types_and_costs() -> None:
    game, _, _ = _start_jurassic_game()

    paddock = game.active_space_by_id["compsognathus_pen"]
    park_road = game.active_space_by_id["park_road_1"]
    utility = game.active_space_by_id["control_room"]

    assert paddock.kind == "property"
    assert paddock.subtype == "dino_paddock"
    assert paddock.house_cost == 50

    assert park_road.kind == "railroad"
    assert utility.kind == "utility"
    assert not game._mortgages_enabled_for_active_board()


def test_jurassic_paddocks_use_fence_rent_and_deed_text() -> None:
    game, alice, _ = _start_jurassic_game()

    for space_id in ("compsognathus_pen", "dilophosaurus_paddock"):
        game.property_owners[space_id] = alice.id
        alice.owned_space_ids.append(space_id)

    paddock = game.active_space_by_id["compsognathus_pen"]

    assert game._calculate_rent_due(paddock, alice.id, None) == 2

    game._set_building_level(paddock.space_id, 1)
    assert game._calculate_rent_due(paddock, alice.id, None) == 10

    deed_text = "\n".join(game._deed_lines(paddock, "en")).lower()
    assert "with fence:" in deed_text
    assert "fence cost:" in deed_text
    assert "full color set" not in deed_text
    assert "hotel" not in deed_text
    assert "mortgage value" not in deed_text


def test_jurassic_build_and_mortgage_options_follow_fence_rules() -> None:
    game, alice, _ = _start_jurassic_game()

    for space_id in ("compsognathus_pen", "park_road_1", "control_room"):
        game.property_owners[space_id] = alice.id
        alice.owned_space_ids.append(space_id)

    buildable = game._build_house_space_ids(alice)
    assert buildable == ["compsognathus_pen"]

    build_options = game._options_for_build_house(alice)
    assert len(build_options) == 1
    assert "build fence" in build_options[0].lower()
    assert "$50" in build_options[0]

    assert game._options_for_mortgage_property(alice) == []

    game._set_building_level("compsognathus_pen", 1)
    assert game._build_house_space_ids(alice) == []

    sell_options = game._options_for_sell_house(alice)
    assert len(sell_options) == 1
    assert "sell fence" in sell_options[0].lower()
    assert "$25" in sell_options[0]


def test_jurassic_damaged_properties_require_repair_and_can_be_repaired() -> None:
    game, alice, _ = _start_jurassic_game()

    game.property_owners["compsognathus_pen"] = alice.id
    alice.owned_space_ids.append("compsognathus_pen")
    game.jurassic_park_engine.state.damaged_space_ids.add("compsognathus_pen")

    paddock = game.active_space_by_id["compsognathus_pen"]
    starting_cash = alice.cash

    assert game._calculate_rent_due(paddock, alice.id, None) == 0
    assert game._options_for_repair_property(alice)

    game._action_repair_property(alice, "compsognathus_pen", "repair_property")

    assert not game._jurassic_park_is_damaged("compsognathus_pen")
    assert alice.cash == starting_cash - 25


def test_jurassic_complete_sets_become_trex_immune_and_auto_repair() -> None:
    game, alice, _ = _start_jurassic_game()

    game.property_owners["compsognathus_pen"] = alice.id
    alice.owned_space_ids.append("compsognathus_pen")
    game.jurassic_park_engine.state.damaged_space_ids.add("compsognathus_pen")

    game.property_owners["dilophosaurus_paddock"] = alice.id
    alice.owned_space_ids.append("dilophosaurus_paddock")
    second = game.active_space_by_id["dilophosaurus_paddock"]
    game._announce_completed_collection_if_needed(alice, second, owned_before=False)

    assert "brown" in game.jurassic_park_engine.state.complete_set_groups
    assert not game._jurassic_park_is_damaged("compsognathus_pen")


def test_jurassic_trex_destroys_fences_and_then_damages_property() -> None:
    game, alice, bob = _start_jurassic_game()

    game.property_owners["compsognathus_pen"] = alice.id
    alice.owned_space_ids.append("compsognathus_pen")
    bob.position = 1
    game.jurassic_park_engine.state.trex_position = 0

    game._set_building_level("compsognathus_pen", 1)
    starting_bob_cash = bob.cash
    assert game._move_jurassic_park_trex(1)

    assert game._building_level("compsognathus_pen") == 0
    assert not game._jurassic_park_is_damaged("compsognathus_pen")
    assert bob.cash == starting_bob_cash - 50

    game.jurassic_park_engine.state.trex_position = 0
    assert game._move_jurassic_park_trex(1)
    assert game._jurassic_park_is_damaged("compsognathus_pen")


def test_jurassic_penalty_spaces_and_fenced_trades_follow_board_rules() -> None:
    game, alice, _ = _start_jurassic_game()

    security_breach = game.active_space_by_id["security_breach"]
    kitchen_attack = game.active_space_by_id["kitchen_attack"]
    starting_cash = alice.cash

    assert game._resolve_tax_space(alice, security_breach) == "resolved"
    assert alice.cash == starting_cash - 200
    assert game._resolve_tax_space(alice, kitchen_attack) == "resolved"
    assert alice.cash == starting_cash - 300

    game.property_owners["compsognathus_pen"] = alice.id
    alice.owned_space_ids.append("compsognathus_pen")
    game._set_building_level("compsognathus_pen", 1)

    assert game._is_property_tradable_for_trade("compsognathus_pen", alice.id)
