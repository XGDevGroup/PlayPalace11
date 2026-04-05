"""Rule-pack constants for Mario Collector's board."""

RULE_PACK_ID = "mario_collectors"
ANCHOR_EDITION_ID = "monopoly-c4382"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
    "card_cash_override",
)
CARD_ID_REMAPS = {
    ("chance", "go_back_three"): "bank_dividend_50",
}
CARD_CASH_OVERRIDES = {
    "bank_error_collect_200": 250,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
