"""Rule-pack constants for disney_lightyear board."""

RULE_PACK_ID = "disney_lightyear"
ANCHOR_EDITION_ID = "monopoly-f8046"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
    "card_cash_override",
)
CARD_ID_REMAPS = {
    ("chance", "poor_tax_15"): "bank_dividend_50",
}
CARD_CASH_OVERRIDES = {
    "bank_dividend_50": 88,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
