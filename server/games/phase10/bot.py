"""Phase 10 bot AI.

Strategy:
  1. Draw: prefer discard pile if top card helps current phase; else draw from deck.
  2. Lay down: attempt to complete phase whenever hand contains enough cards.
  3. Hit: after laying down, hit any cards that extend table groups, prioritising
     high-penalty cards first (Wilds 25 pts, Skips 15 pts).
  4. Skip: play a Skip card on the opponent closest to finishing (highest phase
     or already laid down), but only if we cannot use the Skip turn productively
     (i.e. we already want to discard it anyway).
  5. Discard: the card least useful to the current phase, prioritising high-penalty
     dead weight (Wild > Skip > 10-12 > 1-9).
"""

from __future__ import annotations

import random
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Phase10Game
    from .state import Phase10Player

from ...game_utils.cards import Card
from .state import P10_RANK_WILD, P10_RANK_SKIP, PHASES, GROUP_SET, GROUP_RUN, GROUP_COLOR
from .evaluator import (
    is_wild,
    is_skip,
    is_numbered,
    score_card,
    find_phase_assignment,
    can_hit_group,
    p10_card_name,
)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def bot_think(game: "Phase10Game", player: "Phase10Player") -> str | None:  # noqa: C901
    """Return the next action ID for the bot to execute, or None."""

    # ---- draw phase ---------------------------------------------------------
    if not game.turn_has_drawn:
        return _choose_draw(game, player)

    # ---- lay-down mode (bot is mid-group-selection) -------------------------
    if game.lay_down_active:
        return _handle_lay_down_mode(game, player)

    # ---- wild placement choice ----------------------------------------------
    if game.hit_wild_group_idx is not None:
        from .evaluator import resolve_run_order
        group = game.table_groups[game.hit_wild_group_idx]
        ordered = resolve_run_order(group.cards)
        if ordered and ordered[0][1] > 1:
            return "hit_wild_low"
        return "hit_wild_high"

    # ---- hit mode -----------------------------------------------------------
    if game.hit_active:
        return _handle_hit_mode(game, player)

    # ---- skip target selection ----------------------------------------------
    if game.skip_discard_active:
        return _choose_skip_target(game, player)

    # ---- try to lay down phase ----------------------------------------------
    if not player.phase_laid_down:
        reqs = game._current_phase_reqs(player)
        assignment = find_phase_assignment(player.hand, reqs)
        if assignment is not None:
            # Start the lay-down flow
            return "lay_down_phase"

    # ---- hit on table groups ------------------------------------------------
    if player.phase_laid_down and game.table_groups:
        hit_target = _find_hit(game, player)
        if hit_target:
            return "hit"

    # ---- discard ------------------------------------------------------------
    return _choose_discard(game, player)


# ---------------------------------------------------------------------------
# Draw
# ---------------------------------------------------------------------------


def _choose_draw(game: "Phase10Game", player: "Phase10Player") -> str:
    """Choose draw_deck or draw_discard."""
    if not game.discard_pile:
        return "draw_deck"
    top = game.discard_pile[-1]
    if is_skip(top):
        return "draw_deck"
    if _discard_helps_phase(top, player.hand, game._current_phase_reqs(player)):
        return "draw_discard"
    return "draw_deck"


def _discard_helps_phase(card: Card, hand: list[Card], reqs) -> bool:
    """Return True if drawing the discard top card would help complete the phase.

    Wilds: always helpful (we keep them), but only draw from discard if the
    phase assignment isn't already complete without it — otherwise taking it
    just wastes a Wild slot and creates ping-pong loops.
    """
    if is_wild(card):
        # Only take the Wild if we can't already lay down without it
        already_done = find_phase_assignment(hand, reqs) is not None
        return not already_done
    test_hand = hand + [card]
    return find_phase_assignment(test_hand, reqs) is not None


# ---------------------------------------------------------------------------
# Lay-down group filling
# ---------------------------------------------------------------------------


def _handle_lay_down_mode(game: "Phase10Game", player: "Phase10Player") -> str | None:
    """During lay-down mode, toggle the right cards then confirm."""
    reqs = game._current_phase_reqs(player)
    req = reqs[game.lay_down_group_index]

    # Work out which card IDs to place in this group.
    # Re-run the assignment from scratch to stay deterministic.
    already_staged: set[int] = set()
    for group_ids in game.lay_down_staged:
        already_staged.update(group_ids)

    available = [c for c in player.hand if c.id not in already_staged]
    assignment = find_phase_assignment(available, reqs[game.lay_down_group_index:])
    if assignment is None:
        # Can't complete — cancel
        return "cancel_lay_down"

    target_ids = set(c.id for c in assignment[0])
    current_ids = set(game.lay_down_current)

    # Toggle cards that differ from target
    for card in player.hand:
        if card.id in already_staged:
            continue
        in_target = card.id in target_ids
        in_current = card.id in current_ids
        if in_target != in_current:
            return game._card_action_id(player, card) or "card_1"

    # Selection matches target — confirm
    return "confirm_group"


# ---------------------------------------------------------------------------
# Hit
# ---------------------------------------------------------------------------


def _handle_hit_mode(game: "Phase10Game", player: "Phase10Player") -> str | None:
    """During hit mode, select the card and group."""
    if game.hit_card_id is None:
        # Choose the best card to hit with
        hit_pair = _find_hit(game, player)
        if not hit_pair:
            return "cancel_hit"
        card, _group_idx = hit_pair
        return game._card_action_id(player, card) or "card_1"
    else:
        # Card chosen; find the matching group
        card = next((c for c in player.hand if c.id == game.hit_card_id), None)
        if not card:
            return "cancel_hit"
        for i, group in enumerate(game.table_groups):
            ok, _ = can_hit_group(group, card)
            if ok:
                return f"hit_group_{i}"
        return "cancel_hit"


def _find_hit(game: "Phase10Game", player: "Phase10Player") -> tuple[Card, int] | None:
    """Return (card, group_index) for the best hit, or None."""
    # Sort hand by descending penalty so we shed high-value dead cards first
    candidates = sorted(
        [c for c in player.hand if not is_skip(c)],
        key=lambda c: score_card(c),
        reverse=True,
    )
    for card in candidates:
        for i, group in enumerate(game.table_groups):
            ok, _ = can_hit_group(group, card)
            if ok:
                # Make sure this card isn't needed for the phase (if not laid down yet)
                if not player.phase_laid_down:
                    continue
                return card, i
    return None


# ---------------------------------------------------------------------------
# Skip target
# ---------------------------------------------------------------------------


def _choose_skip_target(game: "Phase10Game", player: "Phase10Player") -> str:
    """Choose which player to skip — target the one closest to winning."""
    active = [p for p in game._active_players() if p.id != player.id]
    if not active:
        return "cancel_skip"

    # Target whoever is on the highest phase (and not already skipped this hand)
    eligible = [
        p for p in active
        if p.id not in game.skip_targets_this_round
    ]
    if not eligible:
        return "cancel_skip"

    target = max(eligible, key=lambda p: (p.current_phase, int(p.phase_laid_down)))
    return f"skip_target_{target.id}"


# ---------------------------------------------------------------------------
# Discard
# ---------------------------------------------------------------------------


def _choose_discard(game: "Phase10Game", player: "Phase10Player") -> str | None:
    """Choose which card to discard and queue it via discard_pending_card_id."""
    if not player.hand:
        return None

    reqs = game._current_phase_reqs(player)

    # Identify which card IDs are "useful" for the phase.
    # If the phase is completable now, keep exactly the assigned cards.
    # Otherwise, keep cards that contribute to the best partial progress per
    # requirement so we don't throw away the run/set we're building toward.
    useful_ids: set[int] = set()
    assignment = find_phase_assignment(player.hand, reqs)
    if assignment:
        for group in assignment:
            for c in group:
                useful_ids.add(c.id)
    else:
        useful_ids = _partial_useful_ids(player.hand, reqs)

    # Wilds are always considered useful — never discard them if alternatives exist
    for c in player.hand:
        if is_wild(c):
            useful_ids.add(c.id)

    # Prefer to discard dead cards (highest penalty first; selecting a Skip
    # triggers the skip-discard target-selection flow automatically).
    # However, avoid feeding table groups — deprioritize cards that an opponent
    # could immediately draw and hit onto an existing group.
    dead = sorted(
        [c for c in player.hand if c.id not in useful_ids],
        key=lambda c: score_card(c),
        reverse=True,
    )
    card = None
    if dead:
        if game.table_groups:
            safe = [c for c in dead if not any(can_hit_group(g, c)[0] for g in game.table_groups)]
            if safe:
                card = safe[0]
        if card is None:
            card = dead[0]

    if card is None:
        # All cards are useful — discard the lowest-value non-Wild if possible, else Wild
        non_wilds = [c for c in player.hand if not is_wild(c)]
        if non_wilds:
            card = min(non_wilds, key=lambda c: score_card(c))
        else:
            card = min(player.hand, key=lambda c: score_card(c))

    # Set the pending card directly so do_discard can find it without needing
    # a menu focus context (bots don't navigate the UI the way humans do).
    game.discard_pending_card_id = card.id
    return "do_discard"


def _partial_useful_ids(hand: list[Card], reqs) -> set[int]:
    """Return card IDs worth keeping when the full phase can't yet be assembled.

    For each requirement we keep the cards that best contribute to that group:
    - SET: all naturals of the most common rank
    - RUN: all naturals that form the longest consecutive chain
    - COLOR: all naturals of the most common color
    """
    nats = [c for c in hand if not is_wild(c) and not is_skip(c) and is_numbered(c)]
    useful: set[int] = set()

    for req in reqs:
        if req.kind == GROUP_SET:
            if nats:
                best_rank = Counter(c.rank for c in nats).most_common(1)[0][0]
                useful.update(c.id for c in nats if c.rank == best_rank)

        elif req.kind == GROUP_RUN:
            seen_ranks = sorted(set(c.rank for c in nats))
            if not seen_ranks:
                continue
            # Find the longest chain of consecutive ranks
            best: list[int] = []
            current: list[int] = [seen_ranks[0]]
            for r in seen_ranks[1:]:
                if r == current[-1] + 1:
                    current.append(r)
                else:
                    if len(current) > len(best):
                        best = current
                    current = [r]
            if len(current) > len(best):
                best = current
            best_set = set(best)
            useful.update(c.id for c in nats if c.rank in best_set)

        elif req.kind == GROUP_COLOR:
            if nats:
                best_color = Counter(c.suit for c in nats).most_common(1)[0][0]
                useful.update(c.id for c in nats if c.suit == best_color)

    return useful
