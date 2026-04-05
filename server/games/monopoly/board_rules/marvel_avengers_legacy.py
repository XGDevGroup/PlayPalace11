"""Rule-pack constants for marvel_avengers_legacy board."""

RULE_PACK_ID = "marvel_avengers_legacy"
ANCHOR_EDITION_ID = "monopoly-b0323"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
    "card_cash_override",
)
CARD_ID_REMAPS = {
    ("chance", "advance_to_go"): "shield_advance_to_go",
    ("chance", "bank_dividend_50"): "shield_bank_dividend_50",
    ("chance", "go_back_three"): "shield_go_back_three",
    ("chance", "go_to_jail"): "shield_go_to_jail",
    ("chance", "poor_tax_15"): "shield_poor_tax_15",
    ("community_chest", "bank_error_collect_200"): "villains_bank_error_collect_215",
    ("community_chest", "doctor_fee_pay_50"): "villains_doctor_fee_pay_50",
    ("community_chest", "income_tax_refund_20"): "villains_income_tax_refund_20",
    ("community_chest", "go_to_jail"): "villains_go_to_jail",
    ("community_chest", "get_out_of_jail_free"): "villains_jail_release_options",
}
CARD_CASH_OVERRIDES = {
    "bank_error_collect_200": 215,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
