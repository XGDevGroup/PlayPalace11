"""Hardware/sound emulation helpers for special board features."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

HARDWARE_EVENT_SOUND_PROFILES: dict[str, dict[str, str]] = {
    "play_theme": {
        "placeholder_asset": "game_monopoly_hardware/play_theme_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/play_theme.ogg",
    },
    "star_wars_theme": {
        "placeholder_asset": "game_monopoly_hardware/star_wars_theme_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/star_wars_theme.ogg",
    },
    "junior_coin_sound_powerup": {
        "placeholder_asset": "game_monopoly_hardware/junior_coin_sound_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/junior_coin_sound_powerup.ogg",
    },
    "mario_question_block_sound": {
        "placeholder_asset": "game_monopoly_hardware/mario_question_block_sound_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/mario_question_block_sound.ogg",
    },
    "jurassic_park_gate_theme": {
        "placeholder_asset": "game_monopoly_hardware/jurassic_park_gate_theme_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/jurassic_park_gate_theme.ogg",
    },
    "jurassic_park_gate_roar": {
        "placeholder_asset": "game_monopoly_hardware/jurassic_park_gate_roar_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/jurassic_park_gate_roar.ogg",
    },
    "mario_question_block_coin_ping": {
        "placeholder_asset": "game_monopoly_hardware/mario_question_block_coin_ping_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/mario_question_block_coin_ping.ogg",
    },
    "mario_question_block_power_up": {
        "placeholder_asset": "game_monopoly_hardware/mario_question_block_power_up_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/mario_question_block_power_up.ogg",
    },
    "mario_question_block_bowser": {
        "placeholder_asset": "game_monopoly_hardware/mario_question_block_bowser_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/mario_question_block_bowser.ogg",
    },
    "mario_question_block_game_over": {
        "placeholder_asset": "game_monopoly_hardware/mario_question_block_game_over_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/mario_question_block_game_over.ogg",
    },
    "pride_rock_celebration": {
        "placeholder_asset": "game_monopoly_hardware/pride_rock_celebration_placeholder.ogg",
        "original_asset": "game_monopoly_hardware/original/pride_rock_celebration.ogg",
    },
}
SUPPORTED_EVENT_IDS = set(HARDWARE_EVENT_SOUND_PROFILES)


@dataclass(frozen=True)
class HardwareEvent:
    """Normalized hardware event emitted by board runtime."""

    board_id: str
    event_id: str
    payload: dict[str, object]


@dataclass(frozen=True)
class HardwareResult:
    """Resolution result for one hardware event."""

    status: str
    details: str = ""
    sound_asset: str = ""
    sound_asset_source: str = ""


def _repo_root() -> Path:
    """Return repository root path from module location."""
    return Path(__file__).resolve().parents[3]


def _client_sound_path(relative_asset: str) -> Path:
    """Return absolute path to a client sound asset path."""
    return _repo_root() / "client" / "sounds" / relative_asset


def _sound_asset_exists(relative_asset: str) -> bool:
    """Return True when an asset exists in client/sounds."""
    return _client_sound_path(relative_asset).is_file()


def resolve_hardware_sound_asset(event_id: str) -> tuple[str, str]:
    """Resolve preferred sound asset path and source tag for one hardware event."""
    profile = HARDWARE_EVENT_SOUND_PROFILES.get(event_id)
    if profile is None:
        return ("", "none")

    original_asset = profile.get("original_asset", "")
    placeholder_asset = profile.get("placeholder_asset", "")
    if original_asset and _sound_asset_exists(original_asset):
        return (original_asset, "original")
    if placeholder_asset:
        return (placeholder_asset, "placeholder")
    return ("", "none")


def resolve_hardware_event(event: HardwareEvent, sound_mode: str) -> HardwareResult:
    """Resolve one hardware event according to active sound mode."""
    if sound_mode != "emulated":
        return HardwareResult(status="ignored", details="sound_mode_disabled", sound_asset_source="none")

    # Explicit product-scope exclusion: Pac-Man game-unit behavior is out-of-scope.
    if event.board_id == "pacman":
        return HardwareResult(status="ignored", details="pacman_excluded", sound_asset_source="none")

    if event.event_id not in SUPPORTED_EVENT_IDS:
        return HardwareResult(status="ignored", details="unsupported_event", sound_asset_source="none")

    sound_asset, sound_asset_source = resolve_hardware_sound_asset(event.event_id)

    return HardwareResult(
        status="emulated",
        details=event.event_id,
        sound_asset=sound_asset,
        sound_asset_source=sound_asset_source,
    )
