"""Tests for the Battleship game."""

from pathlib import Path

import pytest

from ..game_utils.actions import Visibility
from ..games.battleship.game import (
    BattleshipGame,
    BattleshipOptions,
    BattleshipPlayer,
    Ship,
    FLEET,
    CELL_EMPTY,
    CELL_SHIP,
    CELL_MISS,
    CELL_HIT,
    _can_place_ship,
    _place_ship_on_board,
    _random_place_fleet,
    _make_board,
    _get_opponent,
)
from ..games.registry import GameRegistry
from ..messages.localization import Localization
from server.core.users.bot import Bot
from server.core.users.test_user import MockUser


_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #


def make_game(
    start: bool = False,
    **option_overrides,
) -> BattleshipGame:
    game = BattleshipGame(options=BattleshipOptions(**option_overrides))
    game.setup_keybinds()
    game.add_player("Alice", MockUser("Alice", uuid="p1"))
    game.add_player("Bob", MockUser("Bob", uuid="p2"))
    game.host = "Alice"
    if start:
        game.on_start()
    return game


def make_game_with_bot(
    start: bool = False,
    **option_overrides,
) -> BattleshipGame:
    game = BattleshipGame(options=BattleshipOptions(**option_overrides))
    game.setup_keybinds()
    game.add_player("Alice", MockUser("Alice", uuid="p1"))
    game.add_player("Bot1", Bot("Bot1", uuid="p2"))
    game.host = "Alice"
    if start:
        game.on_start()
    return game


def set_web_client(game: BattleshipGame, *players) -> None:
    targets = players or game.players
    for player in targets:
        user = game.get_user(player)
        if user is not None:
            user.set_client_type("web")


def advance_until(game: BattleshipGame, condition, max_ticks: int = 500) -> bool:
    for _ in range(max_ticks):
        if condition():
            return True
        game.on_tick()
    return condition()


def fire_and_resolve(game: BattleshipGame, bp: BattleshipPlayer, row: int, col: int) -> None:
    """Fire a shot and immediately resolve the delay (skip the 0.5s wait)."""
    game._fire_shot(bp, row, col)
    if game.shot_pending_ticks > 0:
        game.shot_pending_ticks = 0
        game._resolve_shot()


def choose_orientation(game: BattleshipGame, player: BattleshipPlayer, horizontal: bool) -> None:
    """Simulate selecting orientation from the orient sub-menu."""
    selection = "horizontal" if horizontal else "vertical"
    game._handle_menu_event(
        player,
        {
            "menu_id": "orient_menu",
            "selection_id": selection,
        },
    )


def get_bp(game: BattleshipGame, name: str) -> BattleshipPlayer:
    player = game.get_player_by_name(name)
    assert player is not None
    bp = game._as_bp(player)
    assert bp is not None
    return bp


# ------------------------------------------------------------------ #
# Registration & defaults                                              #
# ------------------------------------------------------------------ #


class TestRegistration:
    def test_game_registered(self) -> None:
        game_class = GameRegistry.get("battleship")
        assert game_class is BattleshipGame

    def test_class_methods(self) -> None:
        assert BattleshipGame.get_name() == "Battleship"
        assert BattleshipGame.get_type() == "battleship"
        assert BattleshipGame.get_category() == "category-playaural"
        assert BattleshipGame.get_min_players() == 2
        assert BattleshipGame.get_max_players() == 2
        assert BattleshipGame.get_name_key() == "game-name-battleship"

    def test_default_options(self) -> None:
        opts = BattleshipOptions()
        assert opts.grid_size == "10"
        assert opts.placement_mode == "auto"
        assert opts.replay_on_hit is False
        assert opts.turn_timer == "0"

    def test_leaderboards(self) -> None:
        assert "wins" in BattleshipGame.get_supported_leaderboards()
        assert "rating" in BattleshipGame.get_supported_leaderboards()


# ------------------------------------------------------------------ #
# Ship data class                                                      #
# ------------------------------------------------------------------ #


class TestShip:
    def test_cells_horizontal(self) -> None:
        ship = Ship(type_key="destroyer", size=3, row=2, col=4, horizontal=True)
        assert ship.cells() == [(2, 4), (2, 5), (2, 6)]

    def test_cells_vertical(self) -> None:
        ship = Ship(type_key="submarine", size=3, row=1, col=5, horizontal=False)
        assert ship.cells() == [(1, 5), (2, 5), (3, 5)]

    def test_sunk(self) -> None:
        ship = Ship(type_key="patrol", size=2, hits=1)
        assert not ship.sunk
        ship.hits = 2
        assert ship.sunk

    def test_sunk_at_zero_hits(self) -> None:
        ship = Ship(type_key="carrier", size=5, hits=0)
        assert not ship.sunk


# ------------------------------------------------------------------ #
# Board helpers                                                        #
# ------------------------------------------------------------------ #


class TestBoardHelpers:
    def test_make_board(self) -> None:
        board = _make_board(6)
        assert len(board) == 6
        assert all(len(row) == 6 for row in board)
        assert all(cell == CELL_EMPTY for row in board for cell in row)

    def test_can_place_ship_valid(self) -> None:
        board = _make_board(10)
        assert _can_place_ship(board, 5, 0, 0, True, 10)
        assert _can_place_ship(board, 5, 0, 0, False, 10)

    def test_can_place_ship_out_of_bounds(self) -> None:
        board = _make_board(10)
        # Horizontal overflow
        assert not _can_place_ship(board, 5, 0, 7, True, 10)
        # Vertical overflow
        assert not _can_place_ship(board, 5, 7, 0, False, 10)

    def test_can_place_ship_overlap(self) -> None:
        board = _make_board(10)
        board[0][2] = CELL_SHIP
        assert not _can_place_ship(board, 5, 0, 0, True, 10)

    def test_place_ship_marks_cells(self) -> None:
        board = _make_board(10)
        ship = Ship(type_key="patrol", size=2, row=3, col=4, horizontal=True)
        _place_ship_on_board(board, ship)
        assert board[3][4] == CELL_SHIP
        assert board[3][5] == CELL_SHIP
        assert board[3][3] == CELL_EMPTY

    def test_random_place_fleet(self) -> None:
        board = _make_board(10)
        ships = _random_place_fleet(board, 10, FLEET)
        assert len(ships) == 5
        # Verify total ship cells
        ship_cells = sum(board[r][c] == CELL_SHIP for r in range(10) for c in range(10))
        expected = sum(size for _, size in FLEET)
        assert ship_cells == expected

    def test_random_place_fleet_no_overlap(self) -> None:
        board = _make_board(10)
        ships = _random_place_fleet(board, 10, FLEET)
        all_cells = []
        for ship in ships:
            all_cells.extend(ship.cells())
        assert len(all_cells) == len(set(all_cells))  # no duplicates

    def test_random_place_fleet_small_board(self) -> None:
        """6x6 board should still fit the fleet."""
        board = _make_board(6)
        ships = _random_place_fleet(board, 6, FLEET)
        assert len(ships) == 5


# ------------------------------------------------------------------ #
# Game initialization                                                  #
# ------------------------------------------------------------------ #


class TestGameInit:
    def test_auto_deploy_starts_battle(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        assert game.phase == "battling"
        assert game.status == "playing"
        alice = get_bp(game, "Alice")
        bob = get_bp(game, "Bob")
        assert len(alice.ships) == 5
        assert len(bob.ships) == 5
        assert alice.deploy_ready
        assert bob.deploy_ready

    def test_manual_deploy_stays_deploying(self) -> None:
        game = make_game(start=True, placement_mode="manual")
        assert game.phase == "deploying"
        alice = get_bp(game, "Alice")
        assert not alice.deploy_ready
        assert alice.ships_placed == 0

    def test_grid_size_from_options(self) -> None:
        game = make_game(start=True, grid_size="8")
        assert game.grid_rows == 8
        assert game.grid_cols == 8

    def test_boards_initialized(self) -> None:
        game = make_game(start=True, grid_size="6")
        alice = get_bp(game, "Alice")
        assert len(alice.own_board) == 6
        assert len(alice.shot_board) == 6

    def test_players_view_shots_after_auto_deploy(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        assert not alice.viewing_own  # battle starts on shot view


# ------------------------------------------------------------------ #
# Manual deployment                                                    #
# ------------------------------------------------------------------ #


class TestManualDeployment:
    def test_place_first_ship(self) -> None:
        game = make_game(start=True, placement_mode="manual")
        alice = get_bp(game, "Alice")

        # Select cell
        game.on_grid_select(alice, 0, 0)
        assert game.placing_orientation_pending.get(alice.id) is True

        # Choose horizontal
        choose_orientation(game, alice, horizontal=True)
        assert alice.ships_placed == 1
        assert alice.ships[0].type_key == "carrier"
        assert alice.ships[0].horizontal is True
        assert alice.ships[0].row == 0
        assert alice.ships[0].col == 0

    def test_place_vertical(self) -> None:
        game = make_game(start=True, placement_mode="manual")
        alice = get_bp(game, "Alice")

        game.on_grid_select(alice, 0, 0)
        choose_orientation(game, alice, horizontal=False)
        assert alice.ships[0].horizontal is False

    def test_reject_overlapping_placement(self) -> None:
        game = make_game(start=True, placement_mode="manual")
        alice = get_bp(game, "Alice")

        # Place carrier at (0,0) horizontal
        game.on_grid_select(alice, 0, 0)
        choose_orientation(game, alice, horizontal=True)
        assert alice.ships_placed == 1

        # Try to place battleship overlapping
        game.on_grid_select(alice, 0, 2)
        choose_orientation(game, alice, horizontal=True)
        # Should fail — still 1 ship placed
        assert alice.ships_placed == 1
        # Orientation pending should be reset
        assert not game.placing_orientation_pending.get(alice.id, False)

    def test_reject_out_of_bounds(self) -> None:
        game = make_game(start=True, placement_mode="manual", grid_size="10")
        alice = get_bp(game, "Alice")

        # Try to place carrier at col 8 horizontal (needs 5 cells: 8,9,10,11,12 — out of bounds)
        game.on_grid_select(alice, 0, 8)
        choose_orientation(game, alice, horizontal=True)
        assert alice.ships_placed == 0

    def test_all_ships_placed_triggers_ready(self) -> None:
        game = make_game(start=True, placement_mode="manual")
        alice = get_bp(game, "Alice")

        # Place all 5 ships manually
        col = 0
        for idx, (type_key, size) in enumerate(FLEET):
            game.on_grid_select(alice, idx, 0)
            choose_orientation(game, alice, horizontal=True)

        assert alice.ships_placed == 5
        assert alice.deploy_ready

    def test_both_deployed_starts_battle(self) -> None:
        game = make_game(start=True, placement_mode="auto")

        # Auto placement mode deploys both immediately
        assert game.phase == "battling"


# ------------------------------------------------------------------ #
# Battle phase                                                         #
# ------------------------------------------------------------------ #


class TestBattle:
    def _setup_battle(self, **opts) -> BattleshipGame:
        game = make_game(start=True, placement_mode="auto", **opts)
        assert game.phase == "battling"
        return game

    def test_miss(self) -> None:
        game = self._setup_battle()
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)

        # Find an empty cell on opponent's board
        size = int(game.options.grid_size)
        for r in range(size):
            for c in range(size):
                if opponent.own_board[r][c] == CELL_EMPTY:
                    current.viewing_own = False
                    fire_and_resolve(game, current, r, c)
                    assert current.shot_board[r][c] == CELL_MISS
                    assert current.total_shots == 1
                    assert current.total_hits == 0
                    return
        pytest.fail("No empty cell found on opponent board")

    def test_hit(self) -> None:
        game = self._setup_battle()
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)

        # Find a ship cell on opponent's board
        ship = opponent.ships[0]
        r, c = ship.cells()[0]
        current.viewing_own = False
        old_turn = game.current_player
        fire_and_resolve(game, current, r, c)
        assert current.shot_board[r][c] == CELL_HIT
        assert current.total_hits == 1
        assert ship.hits == 1

    def test_cannot_fire_same_cell_twice(self) -> None:
        game = self._setup_battle()
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)

        # Fire at empty cell (miss advances turn)
        size = int(game.options.grid_size)
        for r in range(size):
            for c in range(size):
                if opponent.own_board[r][c] == CELL_EMPTY:
                    current.viewing_own = False
                    fire_and_resolve(game, current, r, c)
                    assert current.shot_board[r][c] == CELL_MISS
                    # Cell stays enabled (visible in grid) but selecting it
                    # gives feedback — no state change
                    game.current_player = current  # force back for testing
                    reason = game.is_grid_cell_enabled(current, r, c)
                    assert reason is None  # cell stays visible
                    old_board = [row[:] for row in current.shot_board]
                    game._on_battle_select(current, r, c)
                    assert current.shot_board == old_board  # no change
                    return

    def test_sunk_ship(self) -> None:
        game = self._setup_battle()
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)

        # Find the patrol boat (size 2) for easiest sinking
        patrol = None
        for ship in opponent.ships:
            if ship.type_key == "patrol":
                patrol = ship
                break
        assert patrol is not None

        # Sink it
        current.viewing_own = False
        for r, c in patrol.cells():
            if game.current_player != current:
                # Turn may have advanced on miss; force current back
                game.current_player = current
            fire_and_resolve(game, current, r, c)
        assert patrol.sunk

    def test_victory(self) -> None:
        game = self._setup_battle()
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)

        # Sink all ships
        current.viewing_own = False
        for ship in opponent.ships:
            for r, c in ship.cells():
                if game.status == "finished":
                    break
                if game.current_player != current:
                    game.current_player = current
                fire_and_resolve(game, current, r, c)

        assert game.status == "finished"

    def test_replay_on_hit(self) -> None:
        game = self._setup_battle(replay_on_hit=True)
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)

        # Hit a ship — should keep same player's turn
        ship = opponent.ships[0]
        r, c = ship.cells()[0]
        current.viewing_own = False
        fire_and_resolve(game, current, r, c)
        # Player should still be current (replay on hit)
        assert game.current_player == current

    def test_miss_advances_turn(self) -> None:
        game = self._setup_battle()
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)

        # Miss
        size = int(game.options.grid_size)
        for r in range(size):
            for c in range(size):
                if opponent.own_board[r][c] == CELL_EMPTY:
                    current.viewing_own = False
                    fire_and_resolve(game, current, r, c)
                    assert game.current_player != current
                    return

    def test_cannot_fire_while_viewing_own_board(self) -> None:
        game = self._setup_battle()
        current = game._as_bp(game.current_player)
        current.viewing_own = True
        # Cell stays enabled in grid, but _on_battle_select blocks firing
        reason = game.is_grid_cell_enabled(current, 0, 0)
        assert reason is None
        old_board = [row[:] for row in current.shot_board]
        game._on_battle_select(current, 0, 0)
        assert current.shot_board == old_board  # no shot fired


# ------------------------------------------------------------------ #
# Grid cell labels                                                     #
# ------------------------------------------------------------------ #


class TestCellLabels:
    def test_deploy_empty(self) -> None:
        game = make_game(start=True, placement_mode="manual")
        alice = get_bp(game, "Alice")
        label = game.get_cell_label(0, 0, alice, "en")
        assert "open water" in label.lower()

    def test_deploy_ship_placed(self) -> None:
        game = make_game(start=True, placement_mode="manual")
        alice = get_bp(game, "Alice")
        alice.own_board[0][0] = CELL_SHIP
        label = game.get_cell_label(0, 0, alice, "en")
        assert "vessel" in label.lower()

    def test_battle_unknown(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        alice.viewing_own = False
        label = game.get_cell_label(5, 5, alice, "en")
        assert "uncharted" in label.lower()

    def test_battle_hit(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        alice.viewing_own = False
        alice.shot_board[3][3] = CELL_HIT
        label = game.get_cell_label(3, 3, alice, "en")
        assert "hit" in label.lower()

    def test_battle_miss(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        alice.viewing_own = False
        alice.shot_board[3][3] = CELL_MISS
        label = game.get_cell_label(3, 3, alice, "en")
        assert "miss" in label.lower()

    def test_own_board_shows_ship(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        alice.viewing_own = True
        # Find a ship cell — label should include the ship's name
        ship = alice.ships[0]
        r, c = ship.cells()[0]
        label = game.get_cell_label(r, c, alice, "en")
        ship_name = Localization.get("en", f"battleship-ship-{ship.type_key}")
        assert ship_name.lower() in label.lower()


# ------------------------------------------------------------------ #
# Toggle view                                                          #
# ------------------------------------------------------------------ #


class TestToggleView:
    def test_toggle_switches_view(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        initial = alice.viewing_own
        game._action_toggle_view(alice, "toggle_view")
        assert alice.viewing_own != initial

    def test_toggle_blocked_during_deploy(self) -> None:
        game = make_game(start=True, placement_mode="manual")
        alice = get_bp(game, "Alice")
        reason = game._is_toggle_view_enabled(alice)
        assert reason is not None

    def test_toggle_visible_for_web(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        set_web_client(game, alice)
        vis = game._is_toggle_view_hidden(alice)
        assert vis == Visibility.VISIBLE


# ------------------------------------------------------------------ #
# Fleet status                                                         #
# ------------------------------------------------------------------ #


class TestFleetStatus:
    def test_read_fleet_shows_all_ships(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        game._action_read_fleet(alice, "read_fleet")
        user = game.get_user(alice)
        # Status box should be open
        assert game._get_transient_display_state(alice) is not None

    def test_read_enemy_fleet(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        game._action_read_enemy_fleet(alice, "read_enemy_fleet")
        assert game._get_transient_display_state(alice) is not None


# ------------------------------------------------------------------ #
# Turn timer                                                           #
# ------------------------------------------------------------------ #


class TestTurnTimer:
    def test_timer_disabled_by_default(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        assert game.timer.ticks_remaining == 0

    def test_timer_starts_when_configured(self) -> None:
        game = make_game(start=True, placement_mode="auto", turn_timer="30")
        assert game.timer.ticks_remaining > 0

    def test_timeout_auto_fires(self) -> None:
        game = make_game(start=True, placement_mode="auto", turn_timer="30")
        current = game._as_bp(game.current_player)
        initial_shots = current.total_shots

        # Simulate timeout — fires and queues pending shot
        game._on_turn_timeout()
        assert current.total_shots == initial_shots + 1
        # Resolve the pending shot
        assert game.shot_pending_ticks > 0
        game.shot_pending_ticks = 0
        game._resolve_shot()


# ------------------------------------------------------------------ #
# Sound timing                                                         #
# ------------------------------------------------------------------ #


class TestSoundTiming:
    def test_fire_sound_plays_immediately(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)
        current.viewing_own = False

        # Find empty cell
        size = int(game.options.grid_size)
        for r in range(size):
            for c in range(size):
                if opponent.own_board[r][c] == CELL_EMPTY:
                    game._fire_shot(current, r, c)
                    # Shot board NOT yet updated (deferred)
                    assert current.shot_board[r][c] == CELL_EMPTY
                    assert game.shot_pending_ticks > 0
                    return

    def test_result_deferred_by_10_ticks(self) -> None:
        from ..games.battleship.game import FIRE_DELAY_TICKS

        game = make_game(start=True, placement_mode="auto")
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)
        current.viewing_own = False

        size = int(game.options.grid_size)
        for r in range(size):
            for c in range(size):
                if opponent.own_board[r][c] == CELL_EMPTY:
                    game._fire_shot(current, r, c)
                    assert game.shot_pending_ticks == FIRE_DELAY_TICKS

                    # Advance 9 ticks — still pending
                    for _ in range(FIRE_DELAY_TICKS - 1):
                        game.on_tick()
                    assert game.shot_pending_ticks == 1

                    # One more tick resolves
                    game.on_tick()
                    assert game.shot_pending_ticks == 0
                    assert current.shot_board[r][c] == CELL_MISS
                    return

    def test_input_blocked_during_pending_shot(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)
        current.viewing_own = False

        size = int(game.options.grid_size)
        for r in range(size):
            for c in range(size):
                if opponent.own_board[r][c] == CELL_EMPTY:
                    game._fire_shot(current, r, c)
                    # While pending, _on_battle_select silently ignores input
                    assert game.shot_pending_ticks > 0
                    old_board = [row[:] for row in current.shot_board]
                    game._on_battle_select(current, 0, 0)
                    assert current.shot_board == old_board  # blocked
                    # Resolve
                    game.shot_pending_ticks = 0
                    game._resolve_shot()
                    return

    def test_sunk_sound_is_scheduled(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)
        current.viewing_own = False

        # Find patrol boat (size 2) and sink it
        patrol = next(s for s in opponent.ships if s.type_key == "patrol")
        cells = patrol.cells()

        # Hit first cell
        fire_and_resolve(game, current, cells[0][0], cells[0][1])
        if game.current_player != current:
            game.current_player = current

        # Hit second cell — should sink and schedule sunk sound
        scheduled_before = len(game.scheduled_sounds)
        fire_and_resolve(game, current, cells[1][0], cells[1][1])
        # A sunk sound should have been scheduled (with delay_ticks=2)
        assert len(game.scheduled_sounds) > scheduled_before
        assert patrol.sunk


# ------------------------------------------------------------------ #
# Bot AI                                                               #
# ------------------------------------------------------------------ #


class TestBotAI:
    def test_bot_auto_deploys(self) -> None:
        game = make_game_with_bot(start=True, placement_mode="manual")
        bot = get_bp(game, "Bot1")
        advance_until(game, lambda: bot.deploy_ready, max_ticks=50)
        assert bot.deploy_ready
        assert len(bot.ships) == 5

    def test_bot_fires_during_battle(self) -> None:
        game = make_game_with_bot(start=True, placement_mode="auto")
        bot = get_bp(game, "Bot1")

        # Advance until bot gets a turn and fires
        if game.current_player == bot:
            initial_shots = bot.total_shots
            advance_until(
                game,
                lambda: bot.total_shots > initial_shots or game.status == "finished",
                max_ticks=200,
            )
            if game.status != "finished":
                assert bot.total_shots > initial_shots

    def test_bot_game_completes(self) -> None:
        """A full bot vs bot game should complete."""
        game = BattleshipGame(options=BattleshipOptions(placement_mode="auto"))
        game.setup_keybinds()
        game.add_player("Bot1", Bot("Bot1", uuid="p1"))
        game.add_player("Bot2", Bot("Bot2", uuid="p2"))
        game.host = "Bot1"
        game.on_start()

        completed = advance_until(
            game,
            lambda: game.status == "finished",
            max_ticks=30000,
        )
        assert completed, "Bot vs bot game did not complete within 10000 ticks"


# ------------------------------------------------------------------ #
# Game result                                                          #
# ------------------------------------------------------------------ #


class TestGameResult:
    def test_build_result_has_winner(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)

        # Sink all opponent ships
        for ship in opponent.ships:
            for r, c in ship.cells():
                if game.status == "finished":
                    break
                if game.current_player != current:
                    game.current_player = current
                current.viewing_own = False
                fire_and_resolve(game, current, r, c)

        assert game.status == "finished"
        result = game._last_game_result
        assert result is not None
        assert current.id in result.custom_data["winner_ids"]

    def test_end_screen_format(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        current = game._as_bp(game.current_player)
        opponent = _get_opponent(game, current)

        for ship in opponent.ships:
            for r, c in ship.cells():
                if game.status == "finished":
                    break
                if game.current_player != current:
                    game.current_player = current
                current.viewing_own = False
                fire_and_resolve(game, current, r, c)

        result = game._last_game_result
        lines = game.format_end_screen(result, "en")
        assert len(lines) >= 2  # winner line + at least one stats line


# ------------------------------------------------------------------ #
# Grid mixin integration                                               #
# ------------------------------------------------------------------ #


class TestGridIntegration:
    def test_grid_enabled_in_battle(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        kwargs = game._build_grid_menu_kwargs()
        assert kwargs["grid_enabled"] is True
        assert kwargs["grid_width"] == 10

    def test_grid_size_matches_option(self) -> None:
        game = make_game(start=True, grid_size="8")
        kwargs = game._build_grid_menu_kwargs()
        assert kwargs["grid_width"] == 8

    def test_cursors_initialized(self) -> None:
        game = make_game(start=True)
        alice = get_bp(game, "Alice")
        cursor = game._get_cursor(alice)
        assert cursor.row == 0
        assert cursor.col == 0


# ------------------------------------------------------------------ #
# Edge cases                                                           #
# ------------------------------------------------------------------ #


class TestEdgeCases:
    def test_spectator_cannot_fire(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        alice = get_bp(game, "Alice")
        alice.is_spectator = True
        reason = game.is_grid_cell_enabled(alice, 0, 0)
        assert reason == "action-spectator"

    def test_not_your_turn(self) -> None:
        game = make_game(start=True, placement_mode="auto")
        current = game.current_player
        other = None
        for p in game.get_active_players():
            if p != current:
                other = p
                break
        assert other is not None
        other_bp = game._as_bp(other)
        other_bp.viewing_own = False
        # Cell stays enabled in grid, but _on_battle_select blocks non-current player
        reason = game.is_grid_cell_enabled(other, 0, 0)
        assert reason is None
        old_board = [row[:] for row in other_bp.shot_board]
        game._on_battle_select(other_bp, 0, 0)
        assert other_bp.shot_board == old_board  # no shot fired

    def test_small_grid_works(self) -> None:
        game = make_game(start=True, grid_size="6", placement_mode="auto")
        assert game.phase == "battling"
        alice = get_bp(game, "Alice")
        assert len(alice.ships) == 5

    def test_large_grid_works(self) -> None:
        game = make_game(start=True, grid_size="12", placement_mode="auto")
        assert game.phase == "battling"
        assert game.grid_rows == 12
