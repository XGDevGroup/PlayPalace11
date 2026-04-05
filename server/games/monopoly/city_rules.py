"""Normalized anchor-backed data for Monopoly City preset."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CityRuleset:
    """Core normalized constants used by City runtime hooks."""

    anchor_edition_id: str
    source_policy: str = "anchor-first"
    win_rule_key: str = "richest_final_value"
    win_tiebreak: str = "turn_order_first"
    max_blocks_per_district: int = 8
    auction_timer_seconds: int = 50
    auction_min_opening_bid: int = 10_000
    planning_permission_cost: int = 0
    hazard_removal_cost_per_block: int = 500_000
    stadium_cost: int = 2_000_000
    stadium_pass_go_bonus: int = 1_000_000
    monopoly_tower_cost: int = 7_000_000
    jail_fine: int = 500_000
    jail_double_attempt_limit: int = 3
    rent_double_stacks: bool = False
    mortgage_value_basis: str = "current_rent_value"


CITY_RULESET = CityRuleset(anchor_edition_id="monopoly-1790")


CITY_SPACE_DEFINITIONS: tuple[dict[str, str], ...] = (
    {
        "kind": "district",
        "effect": "buy_or_auction_if_unowned_else_pay_rent",
        "anchor": "manual-lines-299-310",
    },
    {
        "kind": "auction",
        "effect": "auction_any_unowned_district",
        "anchor": "manual-lines-315-317",
    },
    {
        "kind": "industry_tax",
        "effect": "pay_printed_amount_if_player_has_industrial_buildings",
        "anchor": "manual-lines-319-321",
    },
    {
        "kind": "planning_permission",
        "effect": "build_bonus_or_hazard",
        "anchor": "manual-lines-323-325,397-415",
    },
    {
        "kind": "free_parking",
        "effect": "take_rent_dodge_card",
        "anchor": "manual-lines-327-329,517-523",
    },
    {
        "kind": "chance",
        "effect": "draw_and_resolve_chance_card",
        "anchor": "manual-line-333",
    },
    {
        "kind": "go_to_jail",
        "effect": "go_to_jail_no_pass_go_collect",
        "anchor": "manual-lines-335-337,543-547",
    },
)
