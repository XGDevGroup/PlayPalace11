"""Anchor-driven rules profile resolver for Jurassic Park Monopoly board."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class JurassicParkProfile:
    """Board-level rules and economy knobs for Jurassic Park edition."""

    board_id: str
    anchor_edition_id: str
    source_policy: str = "anchor-first"

    # T. Rex
    trex_start_position: int = 20  # Free Parking
    trex_fee: int = 50
    trex_no_fee_in_jail: bool = True

    # Fences
    total_fences: int = 24
    max_fences_per_paddock: int = 1
    fence_sell_back_rate: float = 0.5
    fences_require_full_set: bool = False
    fences_on_park_roads: bool = False
    fences_on_utilities: bool = False

    # Electronic gate (GO)
    gate_theme_payout: int = 200
    gate_roar_payout: int = 100
    gate_no_sound_fallback: str = "amber_die"
    gate_amber_theme_range: tuple[int, ...] = (1, 2, 3)
    gate_amber_roar_range: tuple[int, ...] = (4, 5, 6)

    # Complete sets
    complete_set_trex_immune: bool = True
    complete_set_auto_repair: bool = True
    complete_set_rent_bonus: bool = False

    # Mortgages
    mortgages_enabled: bool = False

    # Economy
    starting_cash: int = 1500
    jail_bail: int = 50
    auction_minimum: int = 10
    max_jail_turns: int = 3

    # Tokens
    tokens: tuple[str, ...] = (
        "Dr. Alan Grant",
        "Dr. Ian Malcolm",
        "Dr. Ellie Sattler",
        "John Hammond",
        "Lex Murphy",
        "Tim Murphy",
    )

    provenance_notes: tuple[str, ...] = ()


DEFAULT_JURASSIC_PARK_PROFILE = JurassicParkProfile(
    board_id="jurassic_park",
    anchor_edition_id="monopoly-f1662",
    source_policy="anchor-first",
    provenance_notes=(
        "Anchor manual: monopoly-f1662 (Hasbro F1662)",
        "Conflict policy: anchor-first",
        "Fence/repair costs are estimated from classic house costs; verify with Title Deed photos",
    ),
)


def resolve_jurassic_park_profile(board_id: str) -> JurassicParkProfile | None:
    """Return JP profile if board_id is jurassic_park, else None."""
    if board_id == "jurassic_park":
        return DEFAULT_JURASSIC_PARK_PROFILE
    return None


def is_jurassic_park_board(board_id: str) -> bool:
    """Return True when the active board is Jurassic Park."""
    return board_id == "jurassic_park"
