"""Rule-pack constants for pokemon board."""

RULE_PACK_ID = "pokemon"
ANCHOR_EDITION_ID = "monopoly-g0716"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_id_remap",
)
CARD_ID_REMAPS = {
    ("chance", "bank_dividend_50"): "advance_to_go",
}
CARD_CASH_OVERRIDES: dict[str, int] = {}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
