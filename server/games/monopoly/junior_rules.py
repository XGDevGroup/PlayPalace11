"""Anchor-driven Junior ruleset profiles for Monopoly presets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JuniorRuleset:
    """Normalized Junior gameplay configuration keyed by preset id."""

    preset_id: str
    anchor_edition_id: str
    source_policy: str
    starting_cash: int
    pass_go_cash: int
    bail_amount: int
    dice_count: int
    auto_auction_unowned_property: bool
    allow_trades: bool
    allow_mortgage: bool
    allow_buildings: bool
    rent_mode: str
    jail_mode: str
    cards_mode: str
    game_end_mode: str
    max_rounds: int
    provenance_notes: tuple[str, ...]


JUNIOR_RULESETS: dict[str, JuniorRuleset] = {
    "junior_modern": JuniorRuleset(
        preset_id="junior_modern",
        anchor_edition_id="monopoly-f8562",
        source_policy="anchor-first",
        starting_cash=31,
        pass_go_cash=2,
        bail_amount=1,
        dice_count=1,
        auto_auction_unowned_property=False,
        allow_trades=False,
        allow_mortgage=False,
        allow_buildings=False,
        rent_mode="modern_tier",
        jail_mode="pay_or_wait",
        cards_mode="modern_simplified",
        game_end_mode="property_pool_exhausted",
        max_rounds=120,
        provenance_notes=(
            "Anchor manual: monopoly-f8562",
            "Conflict policy: anchor-first",
            "Fallback policy: anchor-family -> consensus -> deterministic safe default",
        ),
    ),
    "junior_legacy": JuniorRuleset(
        preset_id="junior_legacy",
        anchor_edition_id="monopoly-00441",
        source_policy="anchor-first",
        starting_cash=20,
        pass_go_cash=2,
        bail_amount=1,
        dice_count=1,
        auto_auction_unowned_property=False,
        allow_trades=False,
        allow_mortgage=False,
        allow_buildings=False,
        rent_mode="legacy_tier",
        jail_mode="roll_or_pay",
        cards_mode="legacy_basic",
        game_end_mode="bankruptcy",
        max_rounds=160,
        provenance_notes=(
            "Anchor manual: monopoly-00441",
            "Conflict policy: anchor-first",
            "Fallback policy: anchor-family -> consensus -> deterministic safe default",
        ),
    ),
}


def get_junior_ruleset(preset_id: str) -> JuniorRuleset:
    """Return junior ruleset for preset id."""
    return JUNIOR_RULESETS[preset_id]


def is_junior_ruleset_preset(preset_id: str) -> bool:
    """Return True when preset id maps to a Junior ruleset."""
    return preset_id in JUNIOR_RULESETS

