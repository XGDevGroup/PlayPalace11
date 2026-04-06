"""Board profile and resolver utilities for Monopoly themed boards."""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_BOARD_ID = "classic_default"
DEFAULT_BOARD_RULES_MODE = "auto"
BOARD_RULES_MODES: tuple[str, ...] = ("auto", "skin_only")


@dataclass(frozen=True)
class BoardProfile:
    """Static metadata for one selectable Monopoly board profile."""

    board_id: str
    label_key: str
    anchor_edition_id: str
    compatible_preset_ids: tuple[str, ...]
    fallback_preset_id: str
    rule_pack_id: str | None = None
    rule_pack_status: str = "none"


@dataclass(frozen=True)
class ResolvedBoardPlan:
    """Normalized board selection plan for runtime startup."""

    requested_preset_id: str
    requested_board_id: str
    requested_mode: str
    effective_preset_id: str
    effective_board_id: str
    effective_mode: str
    rule_pack_id: str | None
    rule_pack_status: str
    auto_fixed_from_preset_id: str | None = None


BOARD_PROFILES: dict[str, BoardProfile] = {
    DEFAULT_BOARD_ID: BoardProfile(
        board_id=DEFAULT_BOARD_ID,
        label_key="monopoly-board-classic-default",
        anchor_edition_id="monopoly-00009",
        compatible_preset_ids=(
            "classic_standard",
            "junior",
            "junior_modern",
            "junior_legacy",
            "cheaters",
            "electronic_banking",
            "voice_banking",
            "speed",
            "builder",
            "sore_losers",
            "free_parking_jackpot",
            "city",
            "bid_card_game",
            "deal_card_game",
            "knockout",
        ),
        fallback_preset_id="classic_standard",
        rule_pack_id=None,
        rule_pack_status="none",
    ),
    "mario_collectors": BoardProfile(
        board_id="mario_collectors",
        label_key="monopoly-board-mario-collectors",
        anchor_edition_id="monopoly-c4382",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="mario_collectors",
        rule_pack_status="partial",
    ),
    "mario_kart": BoardProfile(
        board_id="mario_kart",
        label_key="monopoly-board-mario-kart",
        anchor_edition_id="monopoly-e1870",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="mario_kart",
        rule_pack_status="partial",
    ),
    "mario_celebration": BoardProfile(
        board_id="mario_celebration",
        label_key="monopoly-board-mario-celebration",
        anchor_edition_id="monopoly-e9517",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="mario_celebration",
        rule_pack_status="partial",
    ),
    "mario_movie": BoardProfile(
        board_id="mario_movie",
        label_key="monopoly-board-mario-movie",
        anchor_edition_id="monopoly-f6818",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="mario_movie",
        rule_pack_status="partial",
    ),
    "junior_super_mario": BoardProfile(
        board_id="junior_super_mario",
        label_key="monopoly-board-junior-super-mario",
        anchor_edition_id="monopoly-f4817",
        compatible_preset_ids=("junior", "junior_modern", "junior_legacy"),
        fallback_preset_id="junior_modern",
        rule_pack_id="junior_super_mario",
        rule_pack_status="partial",
    ),
    "disney_princesses": BoardProfile(
        board_id="disney_princesses",
        label_key="monopoly-board-disney-princesses",
        anchor_edition_id="monopoly-b4644",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="disney_princesses",
        rule_pack_status="partial",
    ),
    "disney_animation": BoardProfile(
        board_id="disney_animation",
        label_key="monopoly-board-disney-animation",
        anchor_edition_id="monopoly-c2116",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="disney_animation",
        rule_pack_status="partial",
    ),
    "disney_lion_king": BoardProfile(
        board_id="disney_lion_king",
        label_key="monopoly-board-disney-lion-king",
        anchor_edition_id="monopoly-e6707",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="disney_lion_king",
        rule_pack_status="partial",
    ),
    "disney_mickey_friends": BoardProfile(
        board_id="disney_mickey_friends",
        label_key="monopoly-board-disney-mickey-friends",
        anchor_edition_id="monopoly-f5267",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="disney_mickey_friends",
        rule_pack_status="partial",
    ),
    "disney_villains": BoardProfile(
        board_id="disney_villains",
        label_key="monopoly-board-disney-villains",
        anchor_edition_id="monopoly-f0091",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="disney_villains",
        rule_pack_status="partial",
    ),
    "disney_lightyear": BoardProfile(
        board_id="disney_lightyear",
        label_key="monopoly-board-disney-lightyear",
        anchor_edition_id="monopoly-f8046",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="disney_lightyear",
        rule_pack_status="partial",
    ),
    "marvel_80_years": BoardProfile(
        board_id="marvel_80_years",
        label_key="monopoly-board-marvel-80-years",
        anchor_edition_id="monopoly-e7866",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_80_years",
        rule_pack_status="partial",
    ),
    "marvel_avengers": BoardProfile(
        board_id="marvel_avengers",
        label_key="monopoly-board-marvel-avengers",
        anchor_edition_id="monopoly-e6504",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_avengers",
        rule_pack_status="partial",
    ),
    "marvel_spider_man": BoardProfile(
        board_id="marvel_spider_man",
        label_key="monopoly-board-marvel-spider-man",
        anchor_edition_id="monopoly-f3968",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_spider_man",
        rule_pack_status="partial",
    ),
    "marvel_black_panther_wf": BoardProfile(
        board_id="marvel_black_panther_wf",
        label_key="monopoly-board-marvel-black-panther-wf",
        anchor_edition_id="monopoly-f5405",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_black_panther_wf",
        rule_pack_status="partial",
    ),
    "marvel_super_villains": BoardProfile(
        board_id="marvel_super_villains",
        label_key="monopoly-board-marvel-super-villains",
        anchor_edition_id="monopoly-f5270",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_super_villains",
        rule_pack_status="partial",
    ),
    "marvel_deadpool": BoardProfile(
        board_id="marvel_deadpool",
        label_key="monopoly-board-marvel-deadpool",
        anchor_edition_id="monopoly-e2033",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_deadpool",
        rule_pack_status="partial",
    ),
    "star_wars_40th": BoardProfile(
        board_id="star_wars_40th",
        label_key="monopoly-board-star-wars-40th",
        anchor_edition_id="monopoly-c1990",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_40th",
        rule_pack_status="partial",
    ),
    "star_wars_boba_fett": BoardProfile(
        board_id="star_wars_boba_fett",
        label_key="monopoly-board-star-wars-boba-fett",
        anchor_edition_id="monopoly-f5394",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_boba_fett",
        rule_pack_status="partial",
    ),
    "star_wars_light_side": BoardProfile(
        board_id="star_wars_light_side",
        label_key="monopoly-board-star-wars-light-side",
        anchor_edition_id="monopoly-f8383",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_light_side",
        rule_pack_status="partial",
    ),
    "star_wars_the_child": BoardProfile(
        board_id="star_wars_the_child",
        label_key="monopoly-board-star-wars-the-child",
        anchor_edition_id="monopoly-f2013",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_the_child",
        rule_pack_status="partial",
    ),
    "star_wars_mandalorian": BoardProfile(
        board_id="star_wars_mandalorian",
        label_key="monopoly-board-star-wars-mandalorian",
        anchor_edition_id="monopoly-f1276",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_mandalorian",
        rule_pack_status="partial",
    ),
    "star_wars_complete_saga": BoardProfile(
        board_id="star_wars_complete_saga",
        label_key="monopoly-board-star-wars-complete-saga",
        anchor_edition_id="monopoly-e8066",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_complete_saga",
        rule_pack_status="partial",
    ),
    "harry_potter": BoardProfile(
        board_id="harry_potter",
        label_key="monopoly-board-harry-potter",
        anchor_edition_id="monopoly-f9422",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="harry_potter",
        rule_pack_status="partial",
    ),
    "fortnite": BoardProfile(
        board_id="fortnite",
        label_key="monopoly-board-fortnite",
        anchor_edition_id="monopoly-e6603",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="fortnite",
        rule_pack_status="partial",
    ),
    "stranger_things": BoardProfile(
        board_id="stranger_things",
        label_key="monopoly-board-stranger-things",
        anchor_edition_id="monopoly-c4550",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="stranger_things",
        rule_pack_status="partial",
    ),
    "jurassic_park": BoardProfile(
        board_id="jurassic_park",
        label_key="monopoly-board-jurassic-park",
        anchor_edition_id="monopoly-f1662",
        compatible_preset_ids=("classic_standard", "free_parking_jackpot"),
        fallback_preset_id="classic_standard",
        rule_pack_id="jurassic_park",
        rule_pack_status="full",
    ),
    "lord_of_the_rings": BoardProfile(
        board_id="lord_of_the_rings",
        label_key="monopoly-board-lord-of-the-rings",
        anchor_edition_id="monopoly-f1663",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="lord_of_the_rings",
        rule_pack_status="partial",
    ),
    "animal_crossing": BoardProfile(
        board_id="animal_crossing",
        label_key="monopoly-board-animal-crossing",
        anchor_edition_id="monopoly-f1661",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="animal_crossing",
        rule_pack_status="partial",
    ),
    "barbie": BoardProfile(
        board_id="barbie",
        label_key="monopoly-board-barbie",
        anchor_edition_id="monopoly-g0038",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="barbie",
        rule_pack_status="partial",
    ),
    "disney_star_wars_dark_side": BoardProfile(
        board_id="disney_star_wars_dark_side",
        label_key="monopoly-board-disney-star-wars-dark-side",
        anchor_edition_id="monopoly-f6167",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="disney_star_wars_dark_side",
        rule_pack_status="partial",
    ),
    "disney_legacy": BoardProfile(
        board_id="disney_legacy",
        label_key="monopoly-board-disney-legacy",
        anchor_edition_id="monopoly-19643",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="disney_legacy",
        rule_pack_status="partial",
    ),
    "disney_the_edition": BoardProfile(
        board_id="disney_the_edition",
        label_key="monopoly-board-disney-the-edition",
        anchor_edition_id="monopoly-40224",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="disney_the_edition",
        rule_pack_status="partial",
    ),
    "lord_of_the_rings_trilogy": BoardProfile(
        board_id="lord_of_the_rings_trilogy",
        label_key="monopoly-board-lord-of-the-rings-trilogy",
        anchor_edition_id="monopoly-41603",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="lord_of_the_rings_trilogy",
        rule_pack_status="partial",
    ),
    "star_wars_saga": BoardProfile(
        board_id="star_wars_saga",
        label_key="monopoly-board-star-wars-saga",
        anchor_edition_id="monopoly-42452",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_saga",
        rule_pack_status="partial",
    ),
    "marvel_avengers_legacy": BoardProfile(
        board_id="marvel_avengers_legacy",
        label_key="monopoly-board-marvel-avengers-legacy",
        anchor_edition_id="monopoly-b0323",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_avengers_legacy",
        rule_pack_status="partial",
    ),
    "star_wars_legacy": BoardProfile(
        board_id="star_wars_legacy",
        label_key="monopoly-board-star-wars-legacy",
        anchor_edition_id="monopoly-b0324",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_legacy",
        rule_pack_status="partial",
    ),
    "star_wars_classic_edition": BoardProfile(
        board_id="star_wars_classic_edition",
        label_key="monopoly-board-star-wars-classic-edition",
        anchor_edition_id="monopoly-b8613",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_classic_edition",
        rule_pack_status="partial",
    ),
    "star_wars_solo": BoardProfile(
        board_id="star_wars_solo",
        label_key="monopoly-board-star-wars-solo",
        anchor_edition_id="monopoly-e1702",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_solo",
        rule_pack_status="partial",
    ),
    "game_of_thrones": BoardProfile(
        board_id="game_of_thrones",
        label_key="monopoly-board-game-of-thrones",
        anchor_edition_id="monopoly-e3278",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="game_of_thrones",
        rule_pack_status="partial",
    ),
    "deadpool_collectors": BoardProfile(
        board_id="deadpool_collectors",
        label_key="monopoly-board-deadpool-collectors",
        anchor_edition_id="monopoly-e4833",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="deadpool_collectors",
        rule_pack_status="partial",
    ),
    "toy_story": BoardProfile(
        board_id="toy_story",
        label_key="monopoly-board-toy-story",
        anchor_edition_id="monopoly-e5065",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="toy_story",
        rule_pack_status="partial",
    ),
    "black_panther": BoardProfile(
        board_id="black_panther",
        label_key="monopoly-board-black-panther",
        anchor_edition_id="monopoly-e5797",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="black_panther",
        rule_pack_status="partial",
    ),
    "stranger_things_collectors": BoardProfile(
        board_id="stranger_things_collectors",
        label_key="monopoly-board-stranger-things-collectors",
        anchor_edition_id="monopoly-e8194",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="stranger_things_collectors",
        rule_pack_status="partial",
    ),
    "ghostbusters": BoardProfile(
        board_id="ghostbusters",
        label_key="monopoly-board-ghostbusters",
        anchor_edition_id="monopoly-e9479",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="ghostbusters",
        rule_pack_status="partial",
    ),
    "marvel_eternals": BoardProfile(
        board_id="marvel_eternals",
        label_key="monopoly-board-marvel-eternals",
        anchor_edition_id="monopoly-f1659",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_eternals",
        rule_pack_status="partial",
    ),
    "transformers": BoardProfile(
        board_id="transformers",
        label_key="monopoly-board-transformers",
        anchor_edition_id="monopoly-f1660",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="transformers",
        rule_pack_status="partial",
    ),
    "stranger_things_netflix": BoardProfile(
        board_id="stranger_things_netflix",
        label_key="monopoly-board-stranger-things-netflix",
        anchor_edition_id="monopoly-f2544",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="stranger_things_netflix",
        rule_pack_status="partial",
    ),
    "fortnite_collectors": BoardProfile(
        board_id="fortnite_collectors",
        label_key="monopoly-board-fortnite-collectors",
        anchor_edition_id="monopoly-f2546",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="fortnite_collectors",
        rule_pack_status="partial",
    ),
    "star_wars_mandalorian_s2": BoardProfile(
        board_id="star_wars_mandalorian_s2",
        label_key="monopoly-board-star-wars-mandalorian-s2",
        anchor_edition_id="monopoly-f4257",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="star_wars_mandalorian_s2",
        rule_pack_status="partial",
    ),
    "transformers_beast_wars": BoardProfile(
        board_id="transformers_beast_wars",
        label_key="monopoly-board-transformers-beast-wars",
        anchor_edition_id="monopoly-f5269",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="transformers_beast_wars",
        rule_pack_status="partial",
    ),
    "marvel_falcon_winter_soldier": BoardProfile(
        board_id="marvel_falcon_winter_soldier",
        label_key="monopoly-board-marvel-falcon-winter-soldier",
        anchor_edition_id="monopoly-f5851",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_falcon_winter_soldier",
        rule_pack_status="partial",
    ),
    "fortnite_flip": BoardProfile(
        board_id="fortnite_flip",
        label_key="monopoly-board-fortnite-flip",
        anchor_edition_id="monopoly-f7774",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="fortnite_flip",
        rule_pack_status="partial",
    ),
    "marvel_flip": BoardProfile(
        board_id="marvel_flip",
        label_key="monopoly-board-marvel-flip",
        anchor_edition_id="monopoly-f9931",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="marvel_flip",
        rule_pack_status="partial",
    ),
    "pokemon": BoardProfile(
        board_id="pokemon",
        label_key="monopoly-board-pokemon",
        anchor_edition_id="monopoly-g0716",
        compatible_preset_ids=("classic_standard",),
        fallback_preset_id="classic_standard",
        rule_pack_id="pokemon",
        rule_pack_status="partial",
    ),
}


def get_board_profile(board_id: str) -> BoardProfile:
    """Return board profile, falling back to default board profile."""
    return BOARD_PROFILES.get(board_id, BOARD_PROFILES[DEFAULT_BOARD_ID])


def get_available_board_ids() -> list[str]:
    """Return selectable board ids with default board first."""
    ids = [DEFAULT_BOARD_ID]
    ids.extend(board_id for board_id in sorted(BOARD_PROFILES) if board_id != DEFAULT_BOARD_ID)
    return ids


def get_board_label_keys() -> dict[str, str]:
    """Return mapping of board ids to localization label keys."""
    return {board_id: profile.label_key for board_id, profile in BOARD_PROFILES.items()}


def get_available_board_rules_modes() -> list[str]:
    """Return selectable board rules mode ids."""
    return list(BOARD_RULES_MODES)


def resolve_board_plan(
    preset_id: str,
    board_id: str,
    mode: str,
) -> ResolvedBoardPlan:
    """Resolve a deterministic runtime board plan.

    The resolver enforces board compatibility and normalizes mode handling:
    - unknown board id -> default board profile
    - incompatible preset -> fallback preset with auto-fix metadata
    - `skin_only` forces skin-only behavior
    - `auto` enables board-rules only when a rule pack exists
    """
    profile = get_board_profile(board_id)

    requested_mode = mode if mode in BOARD_RULES_MODES else DEFAULT_BOARD_RULES_MODE
    effective_preset_id = preset_id
    auto_fixed_from: str | None = None
    if effective_preset_id not in profile.compatible_preset_ids:
        auto_fixed_from = effective_preset_id
        effective_preset_id = profile.fallback_preset_id

    if requested_mode == "skin_only":
        effective_mode = "skin_only"
    elif profile.rule_pack_id and profile.rule_pack_status in {"partial", "full"}:
        effective_mode = "board_rules"
    else:
        effective_mode = "skin_only"

    return ResolvedBoardPlan(
        requested_preset_id=preset_id,
        requested_board_id=board_id,
        requested_mode=requested_mode,
        effective_preset_id=effective_preset_id,
        effective_board_id=profile.board_id,
        effective_mode=effective_mode,
        rule_pack_id=profile.rule_pack_id,
        rule_pack_status=profile.rule_pack_status,
        auto_fixed_from_preset_id=auto_fixed_from,
    )
