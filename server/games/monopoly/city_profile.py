"""Anchor-driven rules profile resolver for Monopoly City preset."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CityProfile:
    """Preset-level configuration for Monopoly City runtime behavior."""

    preset_id: str
    anchor_edition_id: str
    source_policy: str = "anchor-first"
    win_rule_key: str = ""
    win_threshold: int = 0
    rule_flags: tuple[str, ...] = ()
    provenance_notes: tuple[str, ...] = ()


DEFAULT_CITY_PROFILE = CityProfile(
    preset_id="city",
    anchor_edition_id="monopoly-1790",
    source_policy="anchor-first",
    win_rule_key="richest_final_value",
    win_threshold=5_000_000,
    rule_flags=(
        "rent_dodge_card",
        "planning_permission",
        "railroad_jump",
        "stadium_income",
        "tower_or_skyscraper_double",
    ),
    provenance_notes=(
        "Anchor manual: monopoly-1790",
        "Conflict policy: anchor-first",
        "Fallback policy: anchor-family -> consensus -> deterministic safe default",
    ),
)


def resolve_city_profile(preset_id: str) -> CityProfile:
    """Return city profile for a preset id."""
    if preset_id == "city":
        return DEFAULT_CITY_PROFILE
    return DEFAULT_CITY_PROFILE
