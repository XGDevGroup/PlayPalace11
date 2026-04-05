"""Rule-pack constants for disney_princesses board."""

RULE_PACK_ID = "disney_princesses"
ANCHOR_EDITION_ID = "monopoly-b4644"
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
    "bank_dividend_50": 90,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
