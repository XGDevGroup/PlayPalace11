"""Helpers for reading Monopoly playable preset artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path


DEFAULT_PRESET_ID = "classic_standard"
PRESETS_JSON_PATH = Path(__file__).resolve().parent / "catalog" / "playable_presets.json"


@dataclass(frozen=True)
class MonopolyPreset:
    """A playable Monopoly preset generated from the catalog pipeline."""

    preset_id: str
    family_key: str
    name: str
    description: str
    anchor_edition_id: str
    edition_ids: tuple[str, ...]

    @property
    def edition_count(self) -> int:
        """Number of catalog editions represented by this preset."""
        return len(self.edition_ids)


@dataclass(frozen=True)
class MonopolyPresetCatalog:
    """In-memory representation of playable preset artifacts."""

    generated_at: str
    preset_order: tuple[str, ...]
    presets: tuple[MonopolyPreset, ...]

    def get_preset(self, preset_id: str) -> MonopolyPreset | None:
        """Return a preset by id, if present."""
        for preset in self.presets:
            if preset.preset_id == preset_id:
                return preset
        return None


def _normalize_string_list(values: list[str]) -> tuple[str, ...]:
    """Return de-duplicated non-empty strings preserving first-seen order."""
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return tuple(normalized)


@lru_cache(maxsize=4)
def _load_preset_catalog(path_str: str) -> MonopolyPresetCatalog:
    """Load preset catalog from a JSON path (cached)."""
    path = Path(path_str)
    payload = json.loads(path.read_text(encoding="utf-8"))

    parsed_presets: dict[str, MonopolyPreset] = {}
    for row in payload.get("presets", []):
        preset_id = str(row.get("preset_id", "")).strip()
        if not preset_id or preset_id in parsed_presets:
            continue

        anchor_edition_id = str(row.get("anchor_edition_id", "")).strip()
        edition_ids = _normalize_string_list(row.get("edition_ids", []))
        if not edition_ids and anchor_edition_id:
            edition_ids = (anchor_edition_id,)

        parsed_presets[preset_id] = MonopolyPreset(
            preset_id=preset_id,
            family_key=str(row.get("family_key", "")).strip(),
            name=str(row.get("name", "")).strip() or preset_id,
            description=str(row.get("description", "")).strip(),
            anchor_edition_id=anchor_edition_id,
            edition_ids=edition_ids,
        )

    if not parsed_presets:
        parsed_presets[DEFAULT_PRESET_ID] = MonopolyPreset(
            preset_id=DEFAULT_PRESET_ID,
            family_key="classic_and_themed_standard",
            name="Classic and Themed Standard",
            description="Fallback preset when generated catalog artifacts are missing.",
            anchor_edition_id="",
            edition_ids=(),
        )

    raw_order = [str(value).strip() for value in payload.get("playable_roadmap_order", [])]
    ordered_ids: list[str] = [preset_id for preset_id in raw_order if preset_id in parsed_presets]
    for preset_id in sorted(parsed_presets):
        if preset_id not in ordered_ids:
            ordered_ids.append(preset_id)

    ordered_presets = tuple(parsed_presets[preset_id] for preset_id in ordered_ids)
    return MonopolyPresetCatalog(
        generated_at=str(payload.get("generated_at", "")).strip(),
        preset_order=tuple(ordered_ids),
        presets=ordered_presets,
    )


def load_preset_catalog(path: Path | None = None) -> MonopolyPresetCatalog:
    """Load playable presets from disk."""
    resolved_path = (path or PRESETS_JSON_PATH).resolve()
    return _load_preset_catalog(str(resolved_path))


def get_available_preset_ids(path: Path | None = None) -> list[str]:
    """Get preset ids in preferred selection order."""
    catalog = load_preset_catalog(path)
    return [preset.preset_id for preset in catalog.presets]


def get_default_preset_id(path: Path | None = None) -> str:
    """Get default preset id, preferring classic standard."""
    preset_ids = get_available_preset_ids(path)
    if DEFAULT_PRESET_ID in preset_ids:
        return DEFAULT_PRESET_ID
    return preset_ids[0]


def get_preset(preset_id: str, path: Path | None = None) -> MonopolyPreset | None:
    """Get a preset by id."""
    catalog = load_preset_catalog(path)
    return catalog.get_preset(preset_id)
