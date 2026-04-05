"""Rule-pack constants for lord_of_the_rings board."""

RULE_PACK_ID = "lord_of_the_rings"
ANCHOR_EDITION_ID = "monopoly-f1663"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
)
CARD_ID_REMAPS = {
    ("chance", "go_back_three"): "advance_to_go",
}
CARD_CASH_OVERRIDES: dict[str, int] = {}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
