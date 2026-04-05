"""Rule-pack constants for jurassic_park board.

Jurassic Park Edition (Hasbro F1662) replaces standard Monopoly mechanics
with T. Rex movement, fences (instead of houses/hotels), property damage,
an electronic gate for GO resolution, and complete-set immunity.
"""

RULE_PACK_ID = "jurassic_park"
ANCHOR_EDITION_ID = "monopoly-f1662"
RULE_PACK_STATUS = "full"

PASS_GO_CREDIT_OVERRIDE = None  # GO is handled by the electronic gate (200 or 100)

CAPABILITY_IDS = (
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
)

# Impact Tremor (Chance) remaps - keep canonical cards where applicable
CARD_ID_REMAPS = {
    ("chance", "bank_dividend_50"): "go_back_three",
}

# No card cash overrides needed; amounts match canonical values
CARD_CASH_OVERRIDES: dict[str, int] = {}

# Penalty space amounts (Security Breach = Income Tax, Kitchen Attack = Luxury Tax)
PENALTY_SPACE_AMOUNTS = {
    "security_breach": 200,
    "kitchen_attack": 100,
}

# Deck label overrides for themed decks
DECK_LABELS = {
    "chance": "Impact Tremor",
    "community_chest": "Cold Storage",
}

# Property type labels for narration
PROPERTY_TYPE_LABELS = {
    "dino_paddock": "Dino Paddock",
    "park_road": "Park Road",
    "utility": "Utility",
}

SIMPLIFICATION_NOTE_KEY = None  # Full rules, no simplification needed
