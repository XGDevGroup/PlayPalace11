"""Special-board parity manifest for staged fidelity rollout."""

from __future__ import annotations

from dataclasses import dataclass

from .board_profile import BOARD_PROFILES, DEFAULT_BOARD_ID
from .board_rules_registry import get_rule_pack
from .manual_rules.loader import load_manual_rule_set
from .manual_rules.validator import validate_manual_rule_set


@dataclass(frozen=True)
class BoardParityProfile:
    """Normalized parity metadata for one special board."""

    board_id: str
    rule_pack_id: str
    anchor_edition_id: str
    canonical_manual_edition_id: str
    fidelity_status: str
    deck_mode: str
    capability_ids: tuple[str, ...]
    hardware_capability_ids: tuple[str, ...]


_FIDELITY_OVERRIDES: dict[str, str] = {
    "mario_kart": "manual_core",
    "mario_movie": "manual_core",
    "mario_collectors": "manual_core",
    "mario_celebration": "manual_core",
    "junior_super_mario": "manual_core",
    "disney_star_wars_dark_side": "manual_core",
    "star_wars_40th": "manual_core",
    "star_wars_boba_fett": "manual_core",
    "star_wars_light_side": "manual_core",
    "star_wars_the_child": "manual_core",
    "star_wars_mandalorian": "manual_core",
    "star_wars_complete_saga": "manual_core",
    "star_wars_saga": "manual_core",
    "star_wars_legacy": "manual_core",
    "star_wars_classic_edition": "manual_core",
    "star_wars_solo": "manual_core",
    "star_wars_mandalorian_s2": "manual_core",
    "disney_animation": "manual_core",
    "disney_legacy": "manual_core",
    "disney_lightyear": "manual_core",
    "disney_lion_king": "manual_core",
    "disney_mickey_friends": "manual_core",
    "disney_princesses": "manual_core",
    "disney_the_edition": "manual_core",
    "disney_villains": "manual_core",
    "marvel_80_years": "manual_core",
    "marvel_avengers": "manual_core",
    "marvel_avengers_legacy": "manual_core",
    "marvel_black_panther_wf": "manual_core",
    "marvel_deadpool": "manual_core",
    "marvel_eternals": "manual_core",
    "marvel_falcon_winter_soldier": "manual_core",
    "marvel_flip": "manual_core",
    "marvel_spider_man": "manual_core",
    "marvel_super_villains": "manual_core",
    "harry_potter": "manual_core",
    "fortnite": "manual_core",
    "stranger_things": "manual_core",
    "animal_crossing": "manual_core",
    "barbie": "manual_core",
    "black_panther": "manual_core",
    "deadpool_collectors": "manual_core",
    "fortnite_collectors": "manual_core",
    "fortnite_flip": "manual_core",
    "game_of_thrones": "manual_core",
    "ghostbusters": "manual_core",
    "jurassic_park": "manual_core",
    "lord_of_the_rings": "manual_core",
    "lord_of_the_rings_trilogy": "manual_core",
    "pokemon": "manual_core",
    "stranger_things_collectors": "manual_core",
    "stranger_things_netflix": "manual_core",
    "toy_story": "manual_core",
    "transformers": "manual_core",
    "transformers_beast_wars": "manual_core",
}


def _resolve_fidelity_status(board_id: str) -> str:
    """Resolve current parity fidelity status for board."""
    return _FIDELITY_OVERRIDES.get(board_id, "partial")


def _resolve_deck_mode(capability_ids: tuple[str, ...]) -> str:
    """Resolve deck mode from declared card/manual capabilities."""
    deck_capabilities = {"card_id_remap", "card_cash_override", "junior_manual_core"}
    if any(capability_id in deck_capabilities for capability_id in capability_ids):
        return "board_specific"
    return "classic"


def _resolve_hardware_capability_ids(capability_ids: tuple[str, ...]) -> tuple[str, ...]:
    """Filter capability ids that represent hardware/audio paths."""
    hardware_ids = [
        capability_id
        for capability_id in capability_ids
        if (
            "hardware" in capability_id
            or "audio" in capability_id
            or "sound" in capability_id
        )
    ]
    return tuple(hardware_ids)


def _build_profiles() -> dict[str, BoardParityProfile]:
    """Build parity profiles for all special boards currently onboarded."""
    profiles: dict[str, BoardParityProfile] = {}
    for board_id, profile in BOARD_PROFILES.items():
        if board_id == DEFAULT_BOARD_ID:
            continue
        rule_pack_id = profile.rule_pack_id or board_id
        pack = get_rule_pack(rule_pack_id)
        capability_ids = pack.capability_ids if pack is not None else ()
        profiles[board_id] = BoardParityProfile(
            board_id=board_id,
            rule_pack_id=rule_pack_id,
            anchor_edition_id=profile.anchor_edition_id,
            canonical_manual_edition_id=profile.anchor_edition_id,
            fidelity_status=_resolve_fidelity_status(board_id),
            deck_mode=_resolve_deck_mode(capability_ids),
            capability_ids=capability_ids,
            hardware_capability_ids=_resolve_hardware_capability_ids(capability_ids),
        )
    return profiles


BOARD_PARITY_PROFILES: dict[str, BoardParityProfile] = _build_profiles()


def get_board_parity_profile(board_id: str) -> BoardParityProfile | None:
    """Return parity profile for a board when available."""
    return BOARD_PARITY_PROFILES.get(board_id)


def get_parity_board_ids() -> list[str]:
    """Return sorted board ids represented by parity manifest."""
    return sorted(BOARD_PARITY_PROFILES)


def can_promote_manual_core(board_id: str) -> bool:
    """Return True when a board has a citation-valid manual ruleset."""
    try:
        rule_set = load_manual_rule_set(board_id)
    except (FileNotFoundError, ValueError):
        return False
    return len(validate_manual_rule_set(rule_set)) == 0
