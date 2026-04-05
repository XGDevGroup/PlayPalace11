"""Rule-pack constants for star_wars_saga board."""

RULE_PACK_ID = "star_wars_saga"
ANCHOR_EDITION_ID = "monopoly-42452"
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
    "bank_error_collect_200": 205,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
