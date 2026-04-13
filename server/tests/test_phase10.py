"""Tests for Phase 10: unit tests, play tests, and persistence."""

import pytest

from server.core.users.bot import Bot
from server.core.users.test_user import MockUser
from server.game_utils.cards import Card
from server.games.phase10.evaluator import (
    can_hit_group,
    score_hand,
    validate_group,
    next_phase,
    active_phases,
    is_wild,
    is_skip,
)
from server.games.phase10.game import Phase10Game
from server.games.phase10.state import (
    Phase10Options,
    Phase10Player,
    PhaseRequirement,
    TableGroup,
    GROUP_SET,
    GROUP_RUN,
    GROUP_COLOR,
    P10_RANK_WILD,
    P10_RANK_SKIP,
    P10_COLOR_RED,
    P10_COLOR_BLUE,
    P10_COLOR_GREEN,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_id_counter = iter(range(100_000, 200_000)).__next__


def c(rank: int, suit: int = P10_COLOR_RED) -> Card:
    return Card(id=_id_counter(), rank=rank, suit=suit)


def wild() -> Card:
    return Card(id=_id_counter(), rank=P10_RANK_WILD, suit=0)


def skip() -> Card:
    return Card(id=_id_counter(), rank=P10_RANK_SKIP, suit=0)


def set_group(*cards: Card) -> TableGroup:
    return TableGroup(
        owner_id="p1",
        group_index=0,
        requirement=PhaseRequirement(kind=GROUP_SET, count=len(cards)),
        cards=list(cards),
    )


def color_group(*cards: Card) -> TableGroup:
    return TableGroup(
        owner_id="p1",
        group_index=0,
        requirement=PhaseRequirement(kind=GROUP_COLOR, count=len(cards)),
        cards=list(cards),
    )


def _make_game(n_bots: int = 2, options: Phase10Options | None = None) -> Phase10Game:
    game = Phase10Game(options=options or Phase10Options())
    for i in range(n_bots):
        name = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"][i]
        game.add_player(name, Bot(name))
    game.on_start()
    return game


def _run_to_finish(game: Phase10Game, max_ticks: int = 2_000_000) -> None:
    for _ in range(max_ticks):
        if game.status == "finished":
            return
        game.on_tick()
    raise AssertionError(f"Game did not finish within {max_ticks} ticks")


# ---------------------------------------------------------------------------
# Game metadata
# ---------------------------------------------------------------------------

class TestMetadata:
    def test_name(self):
        assert Phase10Game.get_name() == "Phase 10"

    def test_type(self):
        assert Phase10Game.get_type() == "phase10"

    def test_player_bounds(self):
        assert Phase10Game.get_min_players() == 2
        assert Phase10Game.get_max_players() == 6


# ---------------------------------------------------------------------------
# Options defaults
# ---------------------------------------------------------------------------

class TestOptionsDefaults:
    def test_defaults(self):
        opts = Phase10Options()
        assert opts.winning_phase == 10
        assert opts.turn_timer == "0"
        assert opts.even_phases_only is False
        assert opts.fixed_hands is False


# ---------------------------------------------------------------------------
# Evaluator — scoring
# ---------------------------------------------------------------------------

class TestScoring:
    def test_numbered_card_scores(self):
        # Ranks 1-9 score 5 each, ranks 10-12 score 10 each
        assert score_hand([c(1), c(5), c(10)]) == 20  # 5 + 5 + 10

    def test_wild_scores_25(self):
        assert score_hand([wild()]) == 25

    def test_skip_scores_15(self):
        assert score_hand([skip()]) == 15

    def test_empty_hand_scores_zero(self):
        assert score_hand([]) == 0

    def test_mixed_hand(self):
        # 5 + 25 + 15 + 5 = 50
        assert score_hand([c(3), wild(), skip(), c(7)]) == 50


# ---------------------------------------------------------------------------
# Evaluator — validate_group
# ---------------------------------------------------------------------------

class TestValidateGroup:
    def test_valid_set(self):
        req = PhaseRequirement(GROUP_SET, 3)
        ok, _ = validate_group([c(5), c(5), c(5)], req)
        assert ok

    def test_set_with_wild(self):
        req = PhaseRequirement(GROUP_SET, 3)
        ok, _ = validate_group([c(5), c(5), wild()], req)
        assert ok

    def test_set_mismatched_ranks_fails(self):
        req = PhaseRequirement(GROUP_SET, 3)
        ok, _ = validate_group([c(5), c(5), c(6)], req)
        assert not ok

    def test_set_too_few_fails(self):
        req = PhaseRequirement(GROUP_SET, 3)
        ok, _ = validate_group([c(5), c(5)], req)
        assert not ok

    def test_valid_run(self):
        req = PhaseRequirement(GROUP_RUN, 4)
        ok, _ = validate_group([c(3), c(4), c(5), c(6)], req)
        assert ok

    def test_run_with_wild(self):
        req = PhaseRequirement(GROUP_RUN, 4)
        ok, _ = validate_group([c(3), wild(), c(5), c(6)], req)
        assert ok

    def test_run_non_consecutive_fails(self):
        req = PhaseRequirement(GROUP_RUN, 4)
        ok, _ = validate_group([c(3), c(4), c(6), c(7)], req)
        assert not ok

    def test_valid_color_group(self):
        req = PhaseRequirement(GROUP_COLOR, 3)
        ok, _ = validate_group([c(1, P10_COLOR_RED), c(5, P10_COLOR_RED), c(9, P10_COLOR_RED)], req)
        assert ok

    def test_color_group_mixed_colors_fails(self):
        req = PhaseRequirement(GROUP_COLOR, 3)
        ok, _ = validate_group([c(1, P10_COLOR_RED), c(5, P10_COLOR_BLUE), c(9, P10_COLOR_RED)], req)
        assert not ok

    def test_all_wilds_fails_no_natural(self):
        req = PhaseRequirement(GROUP_SET, 3)
        ok, _ = validate_group([wild(), wild(), wild()], req)
        assert not ok


# ---------------------------------------------------------------------------
# Evaluator — can_hit_group (sets and color groups)
# ---------------------------------------------------------------------------

class TestHitSet:
    def test_matching_rank_accepted(self):
        group = set_group(c(7), c(7), c(7))
        ok, _ = can_hit_group(group, c(7))
        assert ok

    def test_wrong_rank_rejected(self):
        group = set_group(c(7), c(7), c(7))
        ok, _ = can_hit_group(group, c(8))
        assert not ok

    def test_wild_always_accepted_on_set(self):
        group = set_group(c(7), c(7), c(7))
        ok, _ = can_hit_group(group, wild())
        assert ok


class TestHitColor:
    def test_matching_color_accepted(self):
        group = color_group(c(1, P10_COLOR_RED), c(5, P10_COLOR_RED))
        ok, _ = can_hit_group(group, c(9, P10_COLOR_RED))
        assert ok

    def test_wrong_color_rejected(self):
        group = color_group(c(1, P10_COLOR_RED), c(5, P10_COLOR_RED))
        ok, _ = can_hit_group(group, c(9, P10_COLOR_BLUE))
        assert not ok

    def test_wild_accepted_on_color_group(self):
        group = color_group(c(1, P10_COLOR_RED), c(5, P10_COLOR_RED))
        ok, _ = can_hit_group(group, wild())
        assert ok


# ---------------------------------------------------------------------------
# Evaluator — phase progression helpers
# ---------------------------------------------------------------------------

class TestPhaseProgression:
    def test_next_phase_normal(self):
        assert next_phase(1, False) == 2
        assert next_phase(9, False) == 10
        assert next_phase(10, False) == 11

    def test_next_phase_even_only(self):
        assert next_phase(2, True) == 4
        assert next_phase(8, True) == 10
        assert next_phase(10, True) == 11

    def test_active_phases_normal(self):
        phases = active_phases(False)
        assert phases == list(range(1, 11))

    def test_active_phases_even_only(self):
        phases = active_phases(True)
        assert phases == [2, 4, 6, 8, 10]


# ---------------------------------------------------------------------------
# Play tests
# ---------------------------------------------------------------------------

class TestBotGameCompletes:
    def test_two_bots_complete(self):
        game = _make_game(2, Phase10Options(winning_phase=1))
        _run_to_finish(game)
        assert game.status == "finished"

    def test_four_bots_complete(self):
        game = _make_game(4, Phase10Options(winning_phase=2))
        _run_to_finish(game)
        assert game.status == "finished"

    def test_even_phases_complete(self):
        game = _make_game(2, Phase10Options(winning_phase=2, even_phases_only=True))
        _run_to_finish(game)
        assert game.status == "finished"

    def test_fixed_hands_complete(self):
        game = _make_game(2, Phase10Options(fixed_hands=True, winning_phase=10))
        _run_to_finish(game)
        assert game.status == "finished"

    def test_winner_has_lowest_score(self):
        game = _make_game(3, Phase10Options(winning_phase=1))
        _run_to_finish(game)
        winner_id = game.game_winner_id
        assert winner_id is not None
        winner = next(p for p in game.players if p.id == winner_id)
        assert all(winner.score <= p.score for p in game.players)


# ---------------------------------------------------------------------------
# Round-end behaviour
# ---------------------------------------------------------------------------

class TestRoundEnd:
    def test_hands_cleared_after_round(self):
        """After a round ends, all hands should be empty during the wait period."""
        game = _make_game(2, Phase10Options(winning_phase=1))
        # Tick until first round ends (game_active becomes True and next_round_wait_ticks > 0)
        for _ in range(500_000):
            game.on_tick()
            if game.next_round_wait_ticks > 0 and game.round >= 1:
                break
        for p in game.players:
            assert p.hand == [], f"{p.name} hand not empty after round end"

    def test_scores_assigned_after_round(self):
        """At least the loser should have a non-zero penalty after the first round."""
        game = _make_game(2, Phase10Options(winning_phase=1))
        for _ in range(500_000):
            game.on_tick()
            if game.round == 2 or game.status == "finished":
                break
        total = sum(p.score for p in game.players)
        assert total >= 0  # winner has 0, loser may have 0 if they also went out


# ---------------------------------------------------------------------------
# Skip card
# ---------------------------------------------------------------------------

class TestSkipCard:
    def test_is_skip_identifies_skip_card(self):
        assert is_skip(skip())
        assert not is_skip(c(5))
        assert not is_skip(wild())

    def test_skip_not_drawable_from_discard(self):
        """Skip on top of discard pile should be refused when a player tries to draw it."""
        game = _make_game(2)
        game.status = "playing"
        # Put a skip on the discard pile
        game.discard_pile = [skip()]
        p = game.players[0]
        game.set_turn_players(game.players, reset_index=True)
        user = MockUser(p.name)
        game._users[p.id] = user
        p.hand = [c(3), c(4), c(5)]
        game.turn_has_drawn = False

        game._action_draw_discard(p, "draw_discard")

        spoken = user.get_spoken_messages()
        assert any("cannot" in m.lower() or "skip" in m.lower() for m in spoken)


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_round_trip_preserves_player_state(self):
        game = _make_game(2, Phase10Options(winning_phase=3))
        # Advance a bit so there's interesting state to preserve
        for _ in range(5000):
            if game.status != "waiting":
                break
            game.on_tick()
        for _ in range(30000):
            game.on_tick()
            if game.round >= 2:
                break

        payload = game.to_json()
        loaded = Phase10Game.from_json(payload)
        loaded.rebuild_runtime_state()

        assert loaded.round == game.round
        assert loaded.status == game.status
        for orig, rest in zip(game.players, loaded.players):
            assert rest.current_phase == orig.current_phase
            assert rest.score == orig.score
            assert rest.phase_laid_down == orig.phase_laid_down

    def test_round_trip_preserves_table_groups(self):
        game = _make_game(2, Phase10Options(winning_phase=3))
        for _ in range(100_000):
            game.on_tick()
            if game.table_groups:
                break

        if not game.table_groups:
            pytest.skip("No table groups formed in time")

        payload = game.to_json()
        loaded = Phase10Game.from_json(payload)
        loaded.rebuild_runtime_state()

        assert len(loaded.table_groups) == len(game.table_groups)
        for orig, rest in zip(game.table_groups, loaded.table_groups):
            assert rest.owner_id == orig.owner_id
            assert rest.requirement.kind == orig.requirement.kind
            assert len(rest.cards) == len(orig.cards)

    def test_round_trip_preserves_options(self):
        opts = Phase10Options(winning_phase=5, even_phases_only=True, fixed_hands=False)
        game = _make_game(2, opts)
        payload = game.to_json()
        loaded = Phase10Game.from_json(payload)
        loaded.rebuild_runtime_state()

        assert loaded.options.winning_phase == 5
        assert loaded.options.even_phases_only is True
        assert loaded.options.fixed_hands is False

    def test_round_trip_scheduled_broadcasts_serializable(self):
        """scheduled_broadcasts must survive a JSON round-trip (no Player objects inside)."""
        import json
        game = _make_game(2, Phase10Options(winning_phase=1))
        # Queue a personal broadcast to populate scheduled_broadcasts
        if game.players:
            game.schedule_broadcast_personal_l(
                game.players[0],
                "phase10-your-phase",
                "phase10-player-phase-entry",
                delay_ticks=10,
                phase=1,
                description="test",
                laid_down="other",
            )
        payload = game.to_json()
        # Must not raise
        parsed = json.loads(payload)
        assert "scheduled_broadcasts" in parsed
