"""Rule-pack constants for fortnite board."""

RULE_PACK_ID = "fortnite"
ANCHOR_EDITION_ID = "monopoly-e6603"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
    "card_cash_override",
)
CARD_ID_REMAPS = {
    ("community_chest", "doctor_fee_pay_50"): "income_tax_refund_20",
}
CARD_CASH_OVERRIDES = {
    "income_tax_refund_20": 65,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
