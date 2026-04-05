"""Rule-pack constants for marvel_flip board."""

RULE_PACK_ID = "marvel_flip"
ANCHOR_EDITION_ID = "monopoly-f9931"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
)
CARD_ID_REMAPS = {
    ("chance", "advance_to_go"): "event_advance_to_go",
    ("chance", "bank_dividend_50"): "event_go_to_jail_primary",
    ("chance", "go_back_three"): "event_go_back_three",
    ("chance", "go_to_jail"): "event_go_to_jail_secondary",
    ("chance", "poor_tax_15"): "event_poor_tax_15",
    ("community_chest", "bank_error_collect_200"): "team_up_bank_error_collect_200",
    ("community_chest", "doctor_fee_pay_50"): "team_up_doctor_fee_pay_50",
    ("community_chest", "income_tax_refund_20"): "team_up_income_tax_refund_20",
    ("community_chest", "go_to_jail"): "team_up_go_to_jail",
    ("community_chest", "get_out_of_jail_free"): "team_up_jail_release_options",
}
CARD_CASH_OVERRIDES: dict[str, int] = {}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
