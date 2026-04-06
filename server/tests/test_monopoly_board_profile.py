from server.games.monopoly.board_profile import resolve_board_plan


def test_jurassic_park_allows_free_parking_jackpot():
    plan = resolve_board_plan(
        preset_id="free_parking_jackpot",
        board_id="jurassic_park",
        mode="auto",
    )

    assert plan.effective_preset_id == "free_parking_jackpot"
    assert plan.effective_board_id == "jurassic_park"
    assert plan.effective_mode == "board_rules"
    assert plan.auto_fixed_from_preset_id is None
