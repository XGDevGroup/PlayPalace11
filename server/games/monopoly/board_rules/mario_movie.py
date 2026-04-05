"""Rule-pack constants for Super Mario Bros. Movie board."""

RULE_PACK_ID = "mario_movie"
ANCHOR_EDITION_ID = "monopoly-f6818"
RULE_PACK_STATUS = "partial"
PASS_GO_CREDIT_OVERRIDE = 200
CAPABILITY_IDS = (
    "pass_go_credit_override",
    "startup_board_announcement",
    "card_cash_override",
)
CARD_ID_REMAPS: dict[tuple[str, str], str] = {}
CARD_CASH_OVERRIDES = {
    "bank_dividend_50": 120,
}
SIMPLIFICATION_NOTE_KEY = "monopoly-board-rules-simplified"
