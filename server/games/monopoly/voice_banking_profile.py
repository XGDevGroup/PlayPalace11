"""Anchor-driven rules profile resolver for Monopoly voice banking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceBankingProfile:
    """Preset-level configuration for voice banking behavior."""

    preset_id: str
    anchor_edition_id: str
    source_policy: str = "anchor-first"
    starting_balance: int = 1500
    pass_go_credit: int = 200
    command_prefix: str = "voice:"
    confirmation_required_for_transfers: bool = True
    provenance_notes: tuple[str, ...] = ()


DEFAULT_VOICE_BANKING_PROFILE = VoiceBankingProfile(
    preset_id="voice_banking",
    anchor_edition_id="monopoly-e4816",
    source_policy="anchor-first",
    starting_balance=1500,
    pass_go_credit=200,
    command_prefix="voice:",
    confirmation_required_for_transfers=True,
    provenance_notes=(
        "Anchor manual: monopoly-e4816",
        "Conflict policy: anchor-first",
        "Fallback policy: anchor-family -> consensus -> deterministic safe default",
    ),
)


def resolve_voice_banking_profile(preset_id: str) -> VoiceBankingProfile:
    """Return voice-banking profile for a preset id."""
    if preset_id == "voice_banking":
        return DEFAULT_VOICE_BANKING_PROFILE
    return DEFAULT_VOICE_BANKING_PROFILE
