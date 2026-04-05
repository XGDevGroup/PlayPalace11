"""Anchor-driven rules profile resolver for Monopoly electronic banking."""

from __future__ import annotations

from .banking_sim import ElectronicBankingProfile


DEFAULT_ELECTRONIC_BANKING_PROFILE = ElectronicBankingProfile(
    preset_id="electronic_banking",
    anchor_edition_id="monopoly-00114",
    source_policy="anchor-first",
    starting_balance=1500,
    pass_go_credit=200,
    allow_manual_transfers=True,
    overdraft_policy="no_overdraft",
    provenance_notes=(
        "Anchor manual: monopoly-00114",
        "Conflict policy: anchor-first",
        "Fallback policy: anchor-family -> consensus -> deterministic safe default",
    ),
)


def resolve_electronic_banking_profile(preset_id: str) -> ElectronicBankingProfile:
    """Return electronic banking rules profile for a preset id."""
    if preset_id == "electronic_banking":
        return DEFAULT_ELECTRONIC_BANKING_PROFILE
    return DEFAULT_ELECTRONIC_BANKING_PROFILE
