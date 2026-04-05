"""Rule-pack constants for star_wars_boba_fett board."""

RULE_PACK_ID = "star_wars_boba_fett"
ANCHOR_EDITION_ID = "monopoly-f5394"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
)
CARD_ID_REMAPS = {
    ("chance", "bank_dividend_50"): "go_back_three",
}
CARD_CASH_OVERRIDES: dict[str, int] = {}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
