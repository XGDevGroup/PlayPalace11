"""Phase 10 evaluation: group validation, hit checking, scoring, card naming."""

from __future__ import annotations

from ...game_utils.cards import Card
from ...messages.localization import Localization
from .state import (
    PhaseRequirement,
    TableGroup,
    GROUP_SET,
    GROUP_RUN,
    GROUP_COLOR,
    P10_RANK_WILD,
    P10_RANK_SKIP,
    P10_COLOR_NAMES,
    PHASES,
    PHASE_DESC_KEYS,
    EVEN_PHASES,
)

# ---------------------------------------------------------------------------
# Card predicates
# ---------------------------------------------------------------------------


def is_wild(card: Card) -> bool:
    return card.rank == P10_RANK_WILD


def is_skip(card: Card) -> bool:
    return card.rank == P10_RANK_SKIP


def is_numbered(card: Card) -> bool:
    return 1 <= card.rank <= 12


# ---------------------------------------------------------------------------
# Card naming
# ---------------------------------------------------------------------------


def p10_card_name(card: Card, locale: str = "en") -> str:
    """Return the spoken name for a Phase 10 card."""
    if is_wild(card):
        return Localization.get(locale, "phase10-card-wild")
    if is_skip(card):
        return Localization.get(locale, "phase10-card-skip")
    color_key = P10_COLOR_NAMES.get(card.suit, "")
    color = Localization.get(locale, color_key) if color_key else str(card.suit)
    return Localization.get(locale, "phase10-card-numbered", number=card.rank, color=color)


def p10_cards_name(cards: list[Card], locale: str = "en") -> str:
    """Format a list of Phase 10 cards for speech output."""
    if not cards:
        return Localization.get(locale, "no-cards")
    names = [p10_card_name(c, locale) for c in cards]
    return Localization.format_list_and(locale, names)


def req_description(req: PhaseRequirement, locale: str = "en") -> str:
    """Short spoken description of a phase requirement, e.g. 'set of 3'."""
    if req.kind == GROUP_SET:
        return Localization.get(locale, "phase10-req-set", count=req.count)
    if req.kind == GROUP_RUN:
        return Localization.get(locale, "phase10-req-run", count=req.count)
    return Localization.get(locale, "phase10-req-color", count=req.count)


def phase_description(phase_num: int, locale: str = "en") -> str:
    """Full spoken description of a phase, e.g. 'Phase 1: 2 sets of 3'."""
    key = PHASE_DESC_KEYS.get(phase_num, "")
    return Localization.get(locale, key) if key else f"Phase {phase_num}"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_card(card: Card) -> int:
    """Penalty point value of a card remaining in hand at round end."""
    if is_wild(card):
        return 25
    if is_skip(card):
        return 15
    if card.rank >= 10:
        return 10
    return 5


def score_hand(cards: list[Card]) -> int:
    """Total penalty points for a list of cards."""
    return sum(score_card(c) for c in cards)


# ---------------------------------------------------------------------------
# Group validation
# ---------------------------------------------------------------------------


def _naturals(cards: list[Card]) -> list[Card]:
    return [c for c in cards if not is_wild(c)]


def _validate_set_cards(cards: list[Card], min_count: int) -> tuple[bool, str]:
    """Validate that cards form a valid set (same rank, at least 1 natural)."""
    if len(cards) < min_count:
        return False, "phase10-err-need-cards"
    nats = _naturals(cards)
    if not nats:
        return False, "phase10-err-need-natural"
    ref_rank = nats[0].rank
    if any(c.rank != ref_rank for c in nats):
        return False, "phase10-err-invalid-set"
    return True, ""


def _validate_run_cards(cards: list[Card], min_count: int) -> tuple[bool, str]:
    """Validate that cards form a valid run (consecutive numbers, at least 1 natural).

    Wilds fill internal gaps and may extend the run at either end.
    The combined span must be achievable with the available wilds.
    """
    if len(cards) < min_count:
        return False, "phase10-err-need-cards"
    nats = _naturals(cards)
    if not nats:
        return False, "phase10-err-need-natural"
    # Skips cannot appear in a run
    if any(is_skip(c) for c in nats):
        return False, "phase10-err-invalid-run"
    # Only numbered cards (1-12) may appear in a run
    if any(not is_numbered(c) for c in nats):
        return False, "phase10-err-invalid-run"

    wild_count = len(cards) - len(nats)
    nat_ranks = sorted(c.rank for c in nats)

    # Duplicate natural ranks are forbidden in a run
    if len(nat_ranks) != len(set(nat_ranks)):
        return False, "phase10-err-invalid-run"

    min_r, max_r = nat_ranks[0], nat_ranks[-1]
    internal_gaps = (max_r - min_r + 1) - len(nat_ranks)

    if internal_gaps > wild_count:
        return False, "phase10-err-invalid-run"

    return True, ""


def _validate_color_cards(cards: list[Card], min_count: int) -> tuple[bool, str]:
    """Validate that cards are all one color (at least 1 natural)."""
    if len(cards) < min_count:
        return False, "phase10-err-need-cards"
    nats = _naturals(cards)
    if not nats:
        return False, "phase10-err-need-natural"
    ref_color = nats[0].suit
    if any(c.suit != ref_color for c in nats):
        return False, "phase10-err-invalid-color"
    return True, ""


def validate_group(cards: list[Card], req: PhaseRequirement) -> tuple[bool, str]:
    """Validate a list of cards against a phase requirement.

    Returns:
        (True, "") on success or (False, error_ftl_key) on failure.
    """
    if req.kind == GROUP_SET:
        return _validate_set_cards(cards, req.count)
    if req.kind == GROUP_RUN:
        return _validate_run_cards(cards, req.count)
    return _validate_color_cards(cards, req.count)


# ---------------------------------------------------------------------------
# Hit validation
# ---------------------------------------------------------------------------


def can_hit_group(group: TableGroup, new_card: Card) -> tuple[bool, str]:
    """Check whether new_card can legally be added to an existing table group.

    Returns:
        (True, "") if valid, (False, reason_ftl_key) otherwise.
    """
    if is_skip(new_card):
        # Skips cannot be used as hits
        if group.requirement.kind == GROUP_SET:
            return False, "phase10-hit-invalid-set"
        if group.requirement.kind == GROUP_RUN:
            return False, "phase10-hit-invalid-run"
        return False, "phase10-hit-invalid-color"

    if is_wild(new_card):
        return True, ""

    if group.requirement.kind == GROUP_SET:
        nats = _naturals(group.cards)
        if nats and new_card.rank != nats[0].rank:
            return False, "phase10-hit-invalid-set"
        return True, ""

    if group.requirement.kind == GROUP_RUN:
        # Re-validate the whole group with the new card added.
        # This naturally checks for duplicate ranks and gap feasibility.
        test = group.cards + [new_card]
        ok, _ = _validate_run_cards(test, len(test))
        if not ok:
            return False, "phase10-hit-invalid-run"
        return True, ""

    # GROUP_COLOR
    nats = _naturals(group.cards)
    if nats and new_card.suit != nats[0].suit:
        return False, "phase10-hit-invalid-color"
    return True, ""


# ---------------------------------------------------------------------------
# Phase assignment helper (used by bot and lay-down validation)
# ---------------------------------------------------------------------------


def find_phase_assignment(
    hand: list[Card],
    phase_reqs: list[PhaseRequirement],
) -> list[list[Card]] | None:
    """Try to find a valid assignment of hand cards to phase requirements.

    Returns a list of card groups (one per requirement) if successful, else None.
    Only numbered cards and wilds are candidates; skips are excluded from phases.

    Uses a greedy approach: satisfy requirements in order, preferring naturals
    before committing wilds. Good enough for bot use; not exhaustive.
    """
    available = [c for c in hand if not is_skip(c)]
    groups: list[list[Card]] = []

    for req in phase_reqs:
        group = _pick_group(available, req)
        if group is None:
            return None
        groups.append(group)
        for c in group:
            available.remove(c)

    return groups


def _pick_group(available: list[Card], req: PhaseRequirement) -> list[Card] | None:
    """Greedily pick cards from available to satisfy req, or return None."""
    wilds = [c for c in available if is_wild(c)]
    nats = [c for c in available if not is_wild(c) and not is_skip(c)]

    if req.kind == GROUP_SET:
        return _pick_set(nats, wilds, req.count)
    if req.kind == GROUP_RUN:
        return _pick_run(nats, wilds, req.count)
    return _pick_color(nats, wilds, req.count)


def _pick_set(nats: list[Card], wilds: list[Card], count: int) -> list[Card] | None:
    from collections import Counter
    rank_groups: dict[int, list[Card]] = {}
    for c in nats:
        rank_groups.setdefault(c.rank, []).append(c)

    # Try to find a rank with enough naturals
    best: list[Card] | None = None
    best_nat_count = -1
    for rank, cards in rank_groups.items():
        nat_count = len(cards)
        needed_wilds = max(0, count - nat_count)
        if needed_wilds <= len(wilds) and nat_count > best_nat_count:
            best = cards[:count] + wilds[:needed_wilds]  # may be more than count if nat_count > count
            best = cards[:min(nat_count, count)] + wilds[:needed_wilds]
            # Also allow more than minimum (lay down extras)
            best = cards + wilds[:max(0, count - len(cards))]
            best_nat_count = nat_count

    if best is not None and len(best) >= count:
        # Return exactly count or more (extras of same rank)
        nat_for_rank = [c for c in nats if c.rank == best[0].rank if not is_wild(best[0])]
        needed_wilds = max(0, count - len(nat_for_rank))
        if needed_wilds <= len(wilds):
            return nat_for_rank + wilds[:needed_wilds]

    # Fall back: all wilds (invalid — needs at least 1 natural)
    return None


def _pick_run(nats: list[Card], wilds: list[Card], count: int) -> list[Card] | None:
    """Find a run of at least `count` among nats+wilds."""
    numbered = sorted((c for c in nats if is_numbered(c)), key=lambda c: c.rank)
    if not numbered:
        return None

    # Try each possible starting rank
    best: list[Card] | None = None
    seen_ranks = sorted(set(c.rank for c in numbered))

    for start_idx in range(len(seen_ranks)):
        # Build the longest run starting from seen_ranks[start_idx]
        run_nats: list[Card] = []
        wilds_used = 0
        prev_rank = seen_ranks[start_idx] - 1  # one before start

        for rank in range(seen_ranks[start_idx], 13):
            # Find a natural card with this rank (prefer first available)
            nat_for_rank = next((c for c in numbered if c.rank == rank and c not in run_nats), None)
            if nat_for_rank:
                prev_rank = rank
                run_nats.append(nat_for_rank)
            elif wilds_used < len(wilds):
                # Fill gap or extend with a wild
                wilds_used += 1
                prev_rank = rank
            else:
                break  # can't extend further

            total = len(run_nats) + wilds_used
            if total >= count:
                # Collect the actual wild objects
                used_wilds = wilds[:wilds_used]
                candidate = run_nats + used_wilds
                if best is None or len(candidate) > len(best):
                    best = candidate

        if best and len(best) >= count:
            return best

    return best if best and len(best) >= count else None


def _pick_color(nats: list[Card], wilds: list[Card], count: int) -> list[Card] | None:
    """Find a color group of at least `count`."""
    from collections import defaultdict
    color_groups: dict[int, list[Card]] = defaultdict(list)
    for c in nats:
        if is_numbered(c):
            color_groups[c.suit].append(c)

    for color, cards in color_groups.items():
        needed_wilds = max(0, count - len(cards))
        if needed_wilds <= len(wilds):
            return cards + wilds[:needed_wilds]

    return None


# ---------------------------------------------------------------------------
# Phase utility
# ---------------------------------------------------------------------------


def active_phases(even_only: bool) -> list[int]:
    """Return the ordered list of phase numbers used in this game variant."""
    return EVEN_PHASES if even_only else list(range(1, 11))


def next_phase(current: int, even_only: bool) -> int:
    """Return the next phase number, or 11 if the game is complete."""
    phases = active_phases(even_only)
    try:
        idx = phases.index(current)
        return phases[idx + 1] if idx + 1 < len(phases) else 11
    except ValueError:
        return 11


def starting_phase(even_only: bool) -> int:
    return active_phases(even_only)[0]
