"""Capability registry for Monopoly board-specific rule packs."""

from __future__ import annotations

from dataclasses import dataclass

from .board_rules import (
    animal_crossing,
    barbie,
    black_panther,
    deadpool_collectors,
    disney_animation,
    disney_legacy,
    disney_lightyear,
    disney_lion_king,
    disney_mickey_friends,
    disney_princesses,
    disney_star_wars_dark_side,
    disney_the_edition,
    disney_villains,
    fortnite,
    fortnite_collectors,
    fortnite_flip,
    game_of_thrones,
    ghostbusters,
    harry_potter,
    junior_super_mario,
    jurassic_park,
    lord_of_the_rings,
    lord_of_the_rings_trilogy,
    mario_celebration,
    mario_collectors,
    mario_kart,
    mario_movie,
    marvel_80_years,
    marvel_avengers,
    marvel_avengers_legacy,
    marvel_black_panther_wf,
    marvel_deadpool,
    marvel_eternals,
    marvel_falcon_winter_soldier,
    marvel_flip,
    marvel_spider_man,
    marvel_super_villains,
    pokemon,
    star_wars_40th,
    star_wars_boba_fett,
    star_wars_classic_edition,
    star_wars_complete_saga,
    star_wars_legacy,
    star_wars_light_side,
    star_wars_mandalorian,
    star_wars_mandalorian_s2,
    star_wars_saga,
    star_wars_solo,
    star_wars_the_child,
    stranger_things,
    stranger_things_collectors,
    stranger_things_netflix,
    toy_story,
    transformers,
    transformers_beast_wars,
)

@dataclass(frozen=True)
class BoardRulePack:
    """Declarative capabilities for one board rule-pack."""

    rule_pack_id: str
    status: str
    capability_ids: tuple[str, ...]


RULE_PACKS: dict[str, BoardRulePack] = {
    "mario_collectors": BoardRulePack(
        rule_pack_id="mario_collectors",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "mario_kart": BoardRulePack(
        rule_pack_id="mario_kart",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "mario_celebration": BoardRulePack(
        rule_pack_id="mario_celebration",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
            "question_block_sound_unit",
        ),
    ),
    "mario_movie": BoardRulePack(
        rule_pack_id="mario_movie",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_cash_override",
        ),
    ),
    "junior_super_mario": BoardRulePack(
        rule_pack_id="junior_super_mario",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "junior_manual_core",
            "junior_powerup_sound_ready",
        ),
    ),
    "disney_princesses": BoardRulePack(
        rule_pack_id="disney_princesses",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "disney_animation": BoardRulePack(
        rule_pack_id="disney_animation",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "disney_lion_king": BoardRulePack(
        rule_pack_id="disney_lion_king",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
            "pride_rock_sound_unit",
        ),
    ),
    "disney_mickey_friends": BoardRulePack(
        rule_pack_id="disney_mickey_friends",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "disney_villains": BoardRulePack(
        rule_pack_id="disney_villains",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "disney_lightyear": BoardRulePack(
        rule_pack_id="disney_lightyear",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "marvel_80_years": BoardRulePack(
        rule_pack_id="marvel_80_years",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "marvel_avengers": BoardRulePack(
        rule_pack_id="marvel_avengers",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "marvel_spider_man": BoardRulePack(
        rule_pack_id="marvel_spider_man",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "marvel_black_panther_wf": BoardRulePack(
        rule_pack_id="marvel_black_panther_wf",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "marvel_super_villains": BoardRulePack(
        rule_pack_id="marvel_super_villains",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "marvel_deadpool": BoardRulePack(
        rule_pack_id="marvel_deadpool",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "star_wars_40th": BoardRulePack(
        rule_pack_id="star_wars_40th",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "star_wars_boba_fett": BoardRulePack(
        rule_pack_id="star_wars_boba_fett",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "star_wars_light_side": BoardRulePack(
        rule_pack_id="star_wars_light_side",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "star_wars_the_child": BoardRulePack(
        rule_pack_id="star_wars_the_child",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "star_wars_mandalorian": BoardRulePack(
        rule_pack_id="star_wars_mandalorian",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "audio_theme_event",
        ),
    ),
    "star_wars_complete_saga": BoardRulePack(
        rule_pack_id="star_wars_complete_saga",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "harry_potter": BoardRulePack(
        rule_pack_id="harry_potter",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "fortnite": BoardRulePack(
        rule_pack_id="fortnite",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "stranger_things": BoardRulePack(
        rule_pack_id="stranger_things",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "jurassic_park": BoardRulePack(
        rule_pack_id="jurassic_park",
        status="full",
        capability_ids=(
            "startup_board_announcement",
            "card_id_remap",
            "electronic_gate_sound_unit",
            "trex_roaming",
            "fence_building",
            "property_damage",
            "electronic_gate_go",
            "complete_set_immunity",
            "penalty_spaces",
            "no_mortgages",
            "no_houses",
            "park_road_rent",
            "jp_utility_rent",
            "jp_turn_order",
        ),
    ),
    "lord_of_the_rings": BoardRulePack(
        rule_pack_id="lord_of_the_rings",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "animal_crossing": BoardRulePack(
        rule_pack_id="animal_crossing",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "barbie": BoardRulePack(
        rule_pack_id="barbie",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "disney_star_wars_dark_side": BoardRulePack(
        rule_pack_id="disney_star_wars_dark_side",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "disney_legacy": BoardRulePack(
        rule_pack_id="disney_legacy",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "disney_the_edition": BoardRulePack(
        rule_pack_id="disney_the_edition",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "lord_of_the_rings_trilogy": BoardRulePack(
        rule_pack_id="lord_of_the_rings_trilogy",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "star_wars_saga": BoardRulePack(
        rule_pack_id="star_wars_saga",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "marvel_avengers_legacy": BoardRulePack(
        rule_pack_id="marvel_avengers_legacy",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "star_wars_legacy": BoardRulePack(
        rule_pack_id="star_wars_legacy",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "star_wars_classic_edition": BoardRulePack(
        rule_pack_id="star_wars_classic_edition",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "star_wars_solo": BoardRulePack(
        rule_pack_id="star_wars_solo",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "game_of_thrones": BoardRulePack(
        rule_pack_id="game_of_thrones",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "deadpool_collectors": BoardRulePack(
        rule_pack_id="deadpool_collectors",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "toy_story": BoardRulePack(
        rule_pack_id="toy_story",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "black_panther": BoardRulePack(
        rule_pack_id="black_panther",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "stranger_things_collectors": BoardRulePack(
        rule_pack_id="stranger_things_collectors",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "ghostbusters": BoardRulePack(
        rule_pack_id="ghostbusters",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "marvel_eternals": BoardRulePack(
        rule_pack_id="marvel_eternals",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "transformers": BoardRulePack(
        rule_pack_id="transformers",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "stranger_things_netflix": BoardRulePack(
        rule_pack_id="stranger_things_netflix",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "fortnite_collectors": BoardRulePack(
        rule_pack_id="fortnite_collectors",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "star_wars_mandalorian_s2": BoardRulePack(
        rule_pack_id="star_wars_mandalorian_s2",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
            "card_cash_override",
        ),
    ),
    "transformers_beast_wars": BoardRulePack(
        rule_pack_id="transformers_beast_wars",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "marvel_falcon_winter_soldier": BoardRulePack(
        rule_pack_id="marvel_falcon_winter_soldier",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "fortnite_flip": BoardRulePack(
        rule_pack_id="fortnite_flip",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "marvel_flip": BoardRulePack(
        rule_pack_id="marvel_flip",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
    "pokemon": BoardRulePack(
        rule_pack_id="pokemon",
        status="partial",
        capability_ids=(
            "pass_go_credit_override",
            "startup_board_announcement",
            "card_id_remap",
        ),
    ),
}
RULE_PACK_MODULES = {
    "mario_collectors": mario_collectors,
    "mario_kart": mario_kart,
    "mario_celebration": mario_celebration,
    "mario_movie": mario_movie,
    "junior_super_mario": junior_super_mario,
    "disney_princesses": disney_princesses,
    "disney_animation": disney_animation,
    "disney_lion_king": disney_lion_king,
    "disney_mickey_friends": disney_mickey_friends,
    "disney_villains": disney_villains,
    "disney_lightyear": disney_lightyear,
    "marvel_80_years": marvel_80_years,
    "marvel_avengers": marvel_avengers,
    "marvel_spider_man": marvel_spider_man,
    "marvel_black_panther_wf": marvel_black_panther_wf,
    "marvel_super_villains": marvel_super_villains,
    "marvel_deadpool": marvel_deadpool,
    "star_wars_40th": star_wars_40th,
    "star_wars_boba_fett": star_wars_boba_fett,
    "star_wars_light_side": star_wars_light_side,
    "star_wars_the_child": star_wars_the_child,
    "star_wars_mandalorian": star_wars_mandalorian,
    "star_wars_complete_saga": star_wars_complete_saga,
    "harry_potter": harry_potter,
    "fortnite": fortnite,
    "stranger_things": stranger_things,
    "jurassic_park": jurassic_park,
    "lord_of_the_rings": lord_of_the_rings,
    "animal_crossing": animal_crossing,
    "barbie": barbie,
    "disney_star_wars_dark_side": disney_star_wars_dark_side,
    "disney_legacy": disney_legacy,
    "disney_the_edition": disney_the_edition,
    "lord_of_the_rings_trilogy": lord_of_the_rings_trilogy,
    "star_wars_saga": star_wars_saga,
    "marvel_avengers_legacy": marvel_avengers_legacy,
    "star_wars_legacy": star_wars_legacy,
    "star_wars_classic_edition": star_wars_classic_edition,
    "star_wars_solo": star_wars_solo,
    "game_of_thrones": game_of_thrones,
    "deadpool_collectors": deadpool_collectors,
    "toy_story": toy_story,
    "black_panther": black_panther,
    "stranger_things_collectors": stranger_things_collectors,
    "ghostbusters": ghostbusters,
    "marvel_eternals": marvel_eternals,
    "transformers": transformers,
    "stranger_things_netflix": stranger_things_netflix,
    "fortnite_collectors": fortnite_collectors,
    "star_wars_mandalorian_s2": star_wars_mandalorian_s2,
    "transformers_beast_wars": transformers_beast_wars,
    "marvel_falcon_winter_soldier": marvel_falcon_winter_soldier,
    "fortnite_flip": fortnite_flip,
    "marvel_flip": marvel_flip,
    "pokemon": pokemon,
}


def get_rule_pack(rule_pack_id: str) -> BoardRulePack | None:
    """Return one board rule-pack by id."""
    return RULE_PACKS.get(rule_pack_id)


def supports_capability(rule_pack_id: str, capability_id: str) -> bool:
    """Return True when a rule-pack advertises one capability id."""
    pack = get_rule_pack(rule_pack_id)
    return bool(pack and capability_id in pack.capability_ids)


def get_pass_go_credit_override(rule_pack_id: str) -> int | None:
    """Return pass-GO override for one rule-pack when declared."""
    module = RULE_PACK_MODULES.get(rule_pack_id)
    if module is None:
        return None
    value = getattr(module, "PASS_GO_CREDIT_OVERRIDE", None)
    if isinstance(value, int):
        return value
    return None


def get_card_id_remap(rule_pack_id: str, deck_type: str, card_id: str) -> str:
    """Return remapped card id for a board pack when declared."""
    module = RULE_PACK_MODULES.get(rule_pack_id)
    if module is None:
        return card_id
    remaps = getattr(module, "CARD_ID_REMAPS", None)
    if not isinstance(remaps, dict):
        return card_id
    value = remaps.get((deck_type, card_id))
    if isinstance(value, str) and value:
        return value
    return card_id


def get_card_cash_override(rule_pack_id: str, card_id: str) -> int | None:
    """Return card cash override for a board pack when declared."""
    module = RULE_PACK_MODULES.get(rule_pack_id)
    if module is None:
        return None
    overrides = getattr(module, "CARD_CASH_OVERRIDES", None)
    if not isinstance(overrides, dict):
        return None
    value = overrides.get(card_id)
    if isinstance(value, int):
        return max(0, value)
    return None
