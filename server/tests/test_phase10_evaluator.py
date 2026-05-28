"""Unit tests for Phase 10 evaluator: hit validation on runs."""

import pytest
from ..games.phase10.evaluator import can_hit_group, resolve_run_order
from ..games.phase10.state import TableGroup, PhaseRequirement, GROUP_RUN, GROUP_SET, P10_RANK_WILD
from ..game_utils.cards import Card


_next_id = iter(range(1, 10000)).__next__


def c(rank: int, suit: int = 1) -> Card:
    """Shorthand card constructor."""
    return Card(id=_next_id(), rank=rank, suit=suit)


def wild() -> Card:
    return Card(id=_next_id(), rank=P10_RANK_WILD, suit=0)


def run_group(*cards: Card) -> TableGroup:
    return TableGroup(
        owner_id="p1",
        group_index=0,
        requirement=PhaseRequirement(kind=GROUP_RUN, count=len(cards)),
        cards=list(cards),
    )


# ---------------------------------------------------------------------------
# resolve_run_order
# ---------------------------------------------------------------------------

class TestResolveRunOrder:
    def test_all_naturals(self):
        cards = [c(4), c(5), c(6), c(7)]
        ordered = resolve_run_order(cards)
        assert [v for _, v in ordered] == [4, 5, 6, 7]

    def test_wild_fills_internal_gap(self):
        # [4, Wild, 6, 7] — wild must fill position 5
        cards = [c(4), wild(), c(6), c(7)]
        ordered = resolve_run_order(cards)
        values = [v for _, v in ordered]
        assert values == [4, 5, 6, 7]

    def test_wild_extends_low_end(self):
        # [4, 5, Wild] — wild greedy extends to 3
        cards = [c(4), c(5), wild()]
        ordered = resolve_run_order(cards)
        values = [v for _, v in ordered]
        assert values == [3, 4, 5]

    def test_two_wilds_one_gap_one_low(self):
        # [4, Wild, 6, Wild] — one wild fills gap at 5, one extends to 3
        cards = [c(4), wild(), c(6), wild()]
        ordered = resolve_run_order(cards)
        values = [v for _, v in ordered]
        assert values == [3, 4, 5, 6]


# ---------------------------------------------------------------------------
# can_hit_group — run extension
# ---------------------------------------------------------------------------

class TestHitRun:
    def test_extend_high_end(self):
        # [4, Wild, 6, 7] span=4-7; can add 8
        group = run_group(c(4), wild(), c(6), c(7))
        ok, _ = can_hit_group(group, c(8))
        assert ok

    def test_extend_low_end(self):
        # [4, Wild, 6, 7] span=4-7; can add 3
        group = run_group(c(4), wild(), c(6), c(7))
        ok, _ = can_hit_group(group, c(3))
        assert ok

    def test_interior_natural_blocked(self):
        # [4, Wild, 6, 7] — wild covers 5; cannot add natural 5
        group = run_group(c(4), wild(), c(6), c(7))
        ok, reason = can_hit_group(group, c(5))
        assert not ok
        assert reason == "phase10-hit-invalid-run"

    def test_interior_natural_no_wild_blocked(self):
        # [4, 5, 6, 7] — no wilds; 6 is interior, blocked
        group = run_group(c(4), c(5), c(6), c(7))
        ok, _ = can_hit_group(group, c(6))
        assert not ok

    def test_non_adjacent_high_blocked(self):
        # [4, Wild, 6, 7] span=4-7; 9 is two steps above, blocked
        group = run_group(c(4), wild(), c(6), c(7))
        ok, _ = can_hit_group(group, c(9))
        assert not ok

    def test_non_adjacent_low_blocked(self):
        # [4, Wild, 6, 7] span=4-7; 2 is two steps below, blocked
        group = run_group(c(4), wild(), c(6), c(7))
        ok, _ = can_hit_group(group, c(2))
        assert not ok

    def test_wild_always_allowed(self):
        # Wild can be added regardless of span
        group = run_group(c(4), c(5), c(6), c(7))
        ok, _ = can_hit_group(group, wild())
        assert ok

    def test_wild_on_full_boundary_run(self):
        # Even a run at boundary accepts a wild
        group = run_group(c(10), c(11), c(12))
        ok, _ = can_hit_group(group, wild())
        assert ok

    def test_all_naturals_extend_high(self):
        # [4, 5, 6] — can add 7
        group = run_group(c(4), c(5), c(6))
        ok, _ = can_hit_group(group, c(7))
        assert ok

    def test_all_naturals_extend_low(self):
        # [4, 5, 6] — can add 3
        group = run_group(c(4), c(5), c(6))
        ok, _ = can_hit_group(group, c(3))
        assert ok

    def test_wild_at_low_end_blocks_same_position(self):
        # [4, 5, Wild] — resolve assigns wild to 3; can extend with 2 or 6, not 3
        group = run_group(c(4), c(5), wild())
        ok_2, _ = can_hit_group(group, c(2))
        ok_6, _ = can_hit_group(group, c(6))
        ok_3, _ = can_hit_group(group, c(3))
        assert ok_2
        assert ok_6
        assert not ok_3

    def test_duplicate_natural_blocked(self):
        # [4, 5, 6] — cannot add another 4 (it's interior to naturals range too)
        group = run_group(c(4), c(5), c(6))
        ok, _ = can_hit_group(group, c(4))
        assert not ok
