"""Rule-pack constants for disney_legacy board."""

RULE_PACK_ID = "disney_legacy"
ANCHOR_EDITION_ID = "monopoly-19643"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
    "card_cash_override",
)
CARD_ID_REMAPS = {
    ("community_chest", "doctor_fee_pay_50"): "bank_error_collect_200",
}
CARD_CASH_OVERRIDES = {
    "bank_error_collect_200": 210,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
