"""Rule-pack constants for star_wars_complete_saga board."""

RULE_PACK_ID = "star_wars_complete_saga"
ANCHOR_EDITION_ID = "monopoly-e8066"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
    "card_cash_override",
)
CARD_ID_REMAPS = {
    ("community_chest", "bank_error_collect_200"): "income_tax_refund_20",
}
CARD_CASH_OVERRIDES = {
    "income_tax_refund_20": 80,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
