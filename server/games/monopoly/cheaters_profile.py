"""Anchor-driven rules profile resolver for Monopoly cheaters preset."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CheatersProfile:
    """Preset-level rules and economy knobs for cheaters mode."""

    preset_id: str
    anchor_edition_id: str
    source_policy: str = "anchor-first"
    enabled_rules: tuple[str, ...] = ()
    penalty_amounts: dict[str, int] = field(default_factory=dict)
    reward_amounts: dict[str, int] = field(default_factory=dict)
    escalation_threshold: int = 2
    provenance_notes: tuple[str, ...] = ()


DEFAULT_CHEATERS_PROFILE = CheatersProfile(
    preset_id="cheaters",
    anchor_edition_id="monopoly-e4888",
    source_policy="anchor-first",
    enabled_rules=(
        "early_end_turn",
        "payment_avoidance",
        "reward_claim",
    ),
    penalty_amounts={
        "early_end_turn": 50,
        "payment_avoidance": 100,
        "escalated_repeat_violation": 150,
    },
    reward_amounts={
        "reward_claim": 100,
    },
    escalation_threshold=2,
    provenance_notes=(
        "Anchor manual: monopoly-e4888",
        "Conflict policy: anchor-first",
        "Fallback policy: anchor-family -> consensus -> deterministic safe default",
    ),
)


def resolve_cheaters_profile(preset_id: str) -> CheatersProfile:
    """Return cheaters profile for a preset id."""
    if preset_id == "cheaters":
        return DEFAULT_CHEATERS_PROFILE
    return DEFAULT_CHEATERS_PROFILE
