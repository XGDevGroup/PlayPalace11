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
    """Return True if drawing the discard top card would help complete the phase."""
    if is_wild(card):
        return True
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
            return f"card_{card.id}"

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
        return f"card_{card.id}"
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
        if p.id not in game.skip_targets_this_hand
    ]
    if not eligible:
        return "cancel_skip"

    target = max(eligible, key=lambda p: (p.current_phase, int(p.phase_laid_down)))
    return f"skip_target_{target.id}"


# ---------------------------------------------------------------------------
# Discard
# ---------------------------------------------------------------------------


def _choose_discard(game: "Phase10Game", player: "Phase10Player") -> str | None:
    """Choose which card to discard."""
    if not player.hand:
        return None

    reqs = game._current_phase_reqs(player)

    # Identify which card IDs are "useful" for the phase
    useful_ids: set[int] = set()
    assignment = find_phase_assignment(player.hand, reqs)
    if assignment:
        for group in assignment:
            for c in group:
                useful_ids.add(c.id)

    # Dead cards sorted by descending penalty (shed most expensive first)
    dead = sorted(
        [c for c in player.hand if c.id not in useful_ids],
        key=lambda c: score_card(c),
        reverse=True,
    )

    if dead:
        # If the top dead card is a skip, play it on someone rather than just discarding
        top_dead = dead[0]
        if is_skip(top_dead):
            # Trigger the skip-discard flow via the card action
            return f"card_{top_dead.id}"
        return f"card_{top_dead.id}"

    # All cards are useful — discard the lowest-value card
    worst = min(player.hand, key=lambda c: score_card(c))
    return f"card_{worst.id}"
