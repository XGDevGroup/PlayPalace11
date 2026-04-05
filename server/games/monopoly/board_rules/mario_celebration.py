"""Rule-pack constants for Mario Celebration board."""

RULE_PACK_ID = "mario_celebration"
ANCHOR_EDITION_ID = "monopoly-e9517"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
    "card_cash_override",
    "question_block_sound_unit",
)
CARD_ID_REMAPS = {
    ("chance", "poor_tax_15"): "bank_dividend_50",
}
CARD_CASH_OVERRIDES = {
    "income_tax_refund_20": 60,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
