"""Tests for Humanity Cards (Cards Against Humanity) game."""

from server.core.users.bot import Bot
from server.core.users.test_user import MockUser
from server.game_utils.actions import Visibility
from server.games.humanitycards.game import HumanityCardsGame, HumanityCardsOptions


# ==========================================================================
# Helpers
# ==========================================================================


def _make_white(count: int, start: int = 0) -> list[dict]:
    return [{"text": f"White card {i}", "pack": "Test", "id": i} for i in range(start, start + count)]


def _make_black(text: str = "Why is _ so funny?", pick: int = 1) -> dict:
    return {"text": text, "pick": pick, "pack": "Test"}


def _inject_decks(game: HumanityCardsGame, white_count: int = 200, black_count: int = 50) -> None:
    game.white_deck = _make_white(white_count)
    game.black_deck = [_make_black(f"Question {i} _") for i in range(black_count)]
    game.white_discard = []
    game.black_discard = []


def _setup_game(
    num_players: int = 3,
    options: HumanityCardsOptions | None = None,
) -> tuple[HumanityCardsGame, list[MockUser]]:
    opts = options or HumanityCardsOptions()
    game = HumanityCardsGame(options=opts)
    game._build_decks = lambda: _inject_decks(game)  # type: ignore[method-assign]
    users = []
    for i in range(num_players):
        name = f"Player{i}"
        user = MockUser(name)
        game.add_player(name, user)
        users.append(user)
    game.on_start()
    return game, users


def _get_to_judging(num_players: int = 3, options: HumanityCardsOptions | None = None):
    game, users = _setup_game(num_players=num_players, options=options)
    for p in game._get_submitters():
        game.execute_action(p, "toggle_card_0")
        game.execute_action(p, "submit_cards")
    assert game.phase == "judging"
    return game, users


def _setup_multi_judge(num_judges: int = 2, num_players: int = 4, judging_method: str = "Independent"):
    return _get_to_judging(
        num_players=num_players,
        options=HumanityCardsOptions(num_judges=num_judges, judging_method=judging_method),
    )


# ==========================================================================
# Metadata
# ==========================================================================


def test_game_metadata():
    game = HumanityCardsGame()
    assert game.get_name() == "Cards Against Humanity"
    assert game.get_type() == "humanitycards"
    assert game.get_min_players() == 3
    assert game.get_max_players() >= 6


# ==========================================================================
# Startup
# ==========================================================================


def test_game_starts_in_submitting_phase():
    game, _ = _setup_game()
    assert game.phase == "submitting"
    assert game.status == "playing"
    assert game.round == 1


def test_players_dealt_hands_on_start():
    game, _ = _setup_game(num_players=3)
    for p in game.get_active_players():
        assert len(p.hand) == game.options.hand_size  # type: ignore[union-attr]


def test_player_scores_zero_on_start():
    game, _ = _setup_game()
    for p in game.get_active_players():
        assert p.score == 0  # type: ignore[union-attr]


def test_black_card_dealt_on_start():
    game, _ = _setup_game()
    assert game.current_black_card is not None
    assert "text" in game.current_black_card


# ==========================================================================
# Judge selection
# ==========================================================================


def test_one_judge_on_start():
    game, _ = _setup_game()
    assert len(game._get_judges()) == 1


def test_rotating_judge_advances_each_round():
    game, _ = _setup_game(num_players=4)
    first_id = game._get_judges()[0].id
    game._start_round()
    assert game._get_judges()[0].id != first_id


def test_judge_count_capped_at_active_player_count():
    game, _ = _setup_game(num_players=3, options=HumanityCardsOptions(num_judges=5))
    assert game.options.num_judges == len(game.get_active_players())
    assert len(game._get_judges()) == len(game.get_active_players())


def test_random_judge_selection_picks_valid_player():
    game, _ = _setup_game(options=HumanityCardsOptions(czar_selection="Random"))
    active_ids = {p.id for p in game.get_active_players()}
    for j in game._get_judges():
        assert j.id in active_ids


def test_winner_judge_selection_uses_last_winner():
    game, _ = _setup_game(
        num_players=4, options=HumanityCardsOptions(czar_selection="Most Recent Winner")
    )
    active = game.get_active_players()
    game.last_winner_index = 2
    game._start_round()
    assert game._get_judges()[0].id == active[2].id


def test_judge_personal_announcement_spoken():
    game, users = _setup_game(num_players=3)
    judge = game._get_judges()[0]
    judge_user = next(u for u in users if u.username == judge.name)
    assert any("Card Czar" in m for m in judge_user.get_spoken_messages())


# ==========================================================================
# Utility
# ==========================================================================


def test_fill_in_blanks():
    game, _ = _setup_game()
    assert game._fill_in_blanks("I love _.", ["cats"]) == "I love cats."
    assert game._fill_in_blanks("_ meets _.", ["Alice", "Bob"]) == "Alice meets Bob."
    assert game._fill_in_blanks("Why?", ["Because"]) == "Why? Because"


def test_speech_friendly_black_replaces_underscore():
    game, _ = _setup_game()
    assert game._speech_friendly_black("I love _.") == "I love blank."


# ==========================================================================
# Deck reshuffle
# ==========================================================================


def test_white_deck_reshuffles_from_discard():
    game, _ = _setup_game()
    game.white_deck = []
    game.white_discard = _make_white(5, start=100)
    drawn = game._draw_white(3)
    assert len(drawn) == 3
    assert len(game.white_deck) + len(drawn) == 5


def test_white_deck_reshuffle_broadcasts():
    game, users = _setup_game()
    game.white_deck = []
    game.white_discard = _make_white(5, start=100)
    for u in users:
        u.clear_messages()
    game._draw_white(1)
    all_spoken = [m for u in users for m in u.get_spoken_messages()]
    assert any("reshuffled" in m.lower() for m in all_spoken)


def test_black_deck_reshuffles_from_discard():
    game, _ = _setup_game()
    game.black_deck = []
    game.black_discard = [_make_black("Test _ card") for _ in range(3)]
    assert game._draw_black() is not None


# ==========================================================================
# Card toggling
# ==========================================================================


def test_toggle_card_selects_and_deselects():
    game, _ = _setup_game()
    non_judge = game._get_non_judges()[0]
    game.execute_action(non_judge, "toggle_card_0")
    assert 0 in non_judge.selected_indices
    game.execute_action(non_judge, "toggle_card_0")
    assert 0 not in non_judge.selected_indices


def test_judge_cannot_toggle_cards():
    game, _ = _setup_game()
    judge = game._get_judges()[0]
    game.execute_action(judge, "toggle_card_0")
    assert 0 not in judge.selected_indices  # type: ignore[union-attr]


# ==========================================================================
# Submission
# ==========================================================================


def test_submit_removes_card_from_hand_and_records():
    game, _ = _setup_game()
    non_judge = game._get_non_judges()[0]
    expected_text = non_judge.hand[0]["text"]
    hand_size = len(non_judge.hand)
    game.execute_action(non_judge, "toggle_card_0")
    game.execute_action(non_judge, "submit_cards")
    assert non_judge.submitted_cards == [expected_text]
    assert len(non_judge.hand) == hand_size - 1


def test_submit_wrong_count_rejected():
    game, users = _setup_game()
    game.current_black_card = _make_black("_ loves _ forever.", pick=2)
    non_judge = game._get_non_judges()[0]
    non_judge_user = next(u for u in users if u.username == non_judge.name)
    game.execute_action(non_judge, "toggle_card_0")
    non_judge_user.clear_messages()
    game.execute_action(non_judge, "submit_cards")
    assert non_judge.submitted_cards is None
    assert any("2" in m for m in non_judge_user.get_spoken_messages())


def test_submit_already_submitted_rejected():
    game, _ = _setup_game()
    non_judge = game._get_non_judges()[0]
    game.execute_action(non_judge, "toggle_card_0")
    game.execute_action(non_judge, "submit_cards")
    first = list(non_judge.submitted_cards)  # type: ignore[arg-type]
    game.execute_action(non_judge, "submit_cards")
    assert non_judge.submitted_cards == first


def test_judge_cannot_submit():
    game, _ = _setup_game()
    judge = game._get_judges()[0]
    game.execute_action(judge, "toggle_card_0")
    game.execute_action(judge, "submit_cards")
    assert judge.submitted_cards is None  # type: ignore[union-attr]


def test_all_submit_triggers_judging_phase():
    game, _ = _setup_game(num_players=3)
    for p in game._get_non_judges():
        game.execute_action(p, "toggle_card_0")
        game.execute_action(p, "submit_cards")
    assert game.phase == "judging"


def test_pick_two_black_card_accepts_two_cards():
    game, _ = _setup_game()
    game.current_black_card = _make_black("_ with _ always.", pick=2)
    non_judge = game._get_non_judges()[0]
    game.execute_action(non_judge, "toggle_card_0")
    game.execute_action(non_judge, "toggle_card_1")
    game.execute_action(non_judge, "submit_cards")
    assert non_judge.submitted_cards is not None
    assert len(non_judge.submitted_cards) == 2


# ==========================================================================
# Judging
# ==========================================================================


def test_judge_pick_awards_point_and_ends_round():
    game, _ = _get_to_judging()
    judge = game._get_judges()[0]
    winner_id = game.submissions[game.submission_order[0]]["player_id"]
    game.execute_action(judge, "judge_pick_0")
    winner = game.get_player_by_id(winner_id)
    assert winner.score == 1  # type: ignore[union-attr]
    assert game.phase in ("round_end", "finished")


def test_winner_announcement_broadcast():
    game, users = _get_to_judging()
    for u in users:
        u.clear_messages()
    game.execute_action(game._get_judges()[0], "judge_pick_0")
    all_spoken = [m for u in users for m in u.get_spoken_messages()]
    assert any("gets" in m.lower() and "point" in m.lower() for m in all_spoken)


def test_non_judge_cannot_pick():
    game, _ = _get_to_judging()
    non_judge = game._get_non_judges()[0]
    game.execute_action(non_judge, "judge_pick_0")
    assert game.phase == "judging"


def test_no_losing_submissions_heading_when_all_are_winners():
    game, users = _setup_game(num_players=3)
    game.submissions = [
        {"player_id": "p1", "cards": ["foo"]},
        {"player_id": "p2", "cards": ["bar"]},
    ]
    game.current_black_card = _make_black("_ question", pick=1)
    for u in users:
        u.clear_messages()
    game._announce_losing_submissions({"p1", "p2"})
    all_spoken = [m for u in users for m in u.get_spoken_messages()]
    assert not any("other submissions" in m.lower() for m in all_spoken)


# ==========================================================================
# Win condition
# ==========================================================================


def test_game_ends_when_winning_score_reached():
    game, _ = _setup_game(options=HumanityCardsOptions(winning_score=1))
    for p in game._get_non_judges():
        game.execute_action(p, "toggle_card_0")
        game.execute_action(p, "submit_cards")
    game.execute_action(game._get_judges()[0], "judge_pick_0")
    assert game.status == "finished"


def test_round_continues_when_score_below_winning():
    game, _ = _setup_game(options=HumanityCardsOptions(winning_score=5))
    for p in game._get_non_judges():
        game.execute_action(p, "toggle_card_0")
        game.execute_action(p, "submit_cards")
    game.execute_action(game._get_judges()[0], "judge_pick_0")
    assert game.status == "playing"
    assert game.phase == "round_end"


# ==========================================================================
# Score display
# ==========================================================================


def test_check_scores_shows_all_players_and_values():
    game, users = _setup_game(num_players=3)
    player0 = game.get_active_players()[0]
    player0.score = 5  # type: ignore[union-attr]
    game._team_manager.add_to_team_score(player0.name, 5)
    user0 = next(u for u in users if u.username == player0.name)
    user0.clear_messages()
    game.execute_action(player0, "check_scores")
    all_text = " ".join(user0.get_spoken_messages())
    assert "5" in all_text
    for p in game.get_active_players():
        assert p.name in all_text


# ==========================================================================
# Round transition
# ==========================================================================


def test_round_end_ticks_advance_to_next_round():
    game, _ = _setup_game()
    for p in game._get_non_judges():
        game.execute_action(p, "toggle_card_0")
        game.execute_action(p, "submit_cards")
    game.execute_action(game._get_judges()[0], "judge_pick_0")
    assert game.phase == "round_end"
    game.round_end_ticks = 1
    game.on_tick()
    assert game.phase == "submitting"
    assert game.round == 2


def test_judge_announcement_fires_each_round():
    game, users = _setup_game(num_players=3)
    for p in game._get_non_judges():
        game.execute_action(p, "toggle_card_0")
        game.execute_action(p, "submit_cards")
    game.execute_action(game._get_judges()[0], "judge_pick_0")
    game.round_end_ticks = 1
    game.on_tick()
    new_judge = game._get_judges()[0]
    new_judge_user = next(u for u in users if u.username == new_judge.name)
    assert any("Card Czar" in m for m in new_judge_user.get_spoken_messages())


# ==========================================================================
# Multi-judge voting
# ==========================================================================


def test_multi_judge_waits_for_all_judges():
    game, _ = _setup_multi_judge(num_judges=2, num_players=4)
    judges = game._get_judges()
    game.execute_action(judges[0], "judge_pick_0")
    assert game.phase == "judging"
    assert len(game.judge_picks) == 1


def test_multi_judge_resolves_after_all_pick():
    game, _ = _setup_multi_judge(num_judges=2, num_players=4)
    judges = game._get_judges()
    game.execute_action(judges[0], "judge_pick_0")
    game.execute_action(judges[1], "judge_pick_0")
    assert game.phase in ("round_end", "finished")


def test_multi_judge_cannot_vote_twice():
    game, _ = _setup_multi_judge(num_judges=2, num_players=4)
    judges = game._get_judges()
    game.execute_action(judges[0], "judge_pick_0")
    first_picks = dict(game.judge_picks)
    game.execute_action(judges[0], "judge_pick_1")
    assert game.judge_picks == first_picks


def test_multi_judge_intermediate_vote_plays_sound_not_speech():
    game, users = _setup_multi_judge(num_judges=2, num_players=4)
    for u in users:
        u.clear_messages()
    game.execute_action(game._get_judges()[0], "judge_pick_0")
    all_spoken = [m for u in users for m in u.get_spoken_messages()]
    assert not any("made their choice" in m for m in all_spoken)
    all_sounds = [s for u in users for s in u.get_sounds_played()]
    assert any("judgechoice" in s for s in all_sounds)


# ==========================================================================
# Judging methods
# ==========================================================================


def test_single_judge_always_uses_independent():
    game, _ = _setup_game(options=HumanityCardsOptions(num_judges=1, judging_method="Jury"))
    for p in game._get_non_judges():
        game.execute_action(p, "toggle_card_0")
        game.execute_action(p, "submit_cards")
    assert game.active_judging_method == "Independent"


def test_independent_awards_one_point_per_vote():
    game, _ = _setup_multi_judge(num_judges=2, num_players=4, judging_method="Independent")
    judges = game._get_judges()
    sub0_id = game.submissions[game.submission_order[0]]["player_id"]
    game.execute_action(judges[0], "judge_pick_0")
    game.execute_action(judges[1], "judge_pick_0")
    assert game.get_player_by_id(sub0_id).score == 2  # type: ignore[union-attr]


def test_independent_split_vote_both_score():
    game, _ = _setup_multi_judge(num_judges=2, num_players=4, judging_method="Independent")
    judges = game._get_judges()
    sub0_id = game.submissions[game.submission_order[0]]["player_id"]
    sub1_id = game.submissions[game.submission_order[1]]["player_id"]
    game.execute_action(judges[0], "judge_pick_0")
    game.execute_action(judges[1], "judge_pick_1")
    assert game.get_player_by_id(sub0_id).score == 1  # type: ignore[union-attr]
    assert game.get_player_by_id(sub1_id).score == 1  # type: ignore[union-attr]


def test_jury_sole_winner_gets_one_point():
    game, _ = _setup_multi_judge(num_judges=2, num_players=4, judging_method="Jury")
    judges = game._get_judges()
    sub0_id = game.submissions[game.submission_order[0]]["player_id"]
    game.execute_action(judges[0], "judge_pick_0")
    game.execute_action(judges[1], "judge_pick_0")
    assert game.get_player_by_id(sub0_id).score == 1  # type: ignore[union-attr]


def test_jury_tie_both_score_one_point():
    game, _ = _setup_multi_judge(num_judges=2, num_players=4, judging_method="Jury")
    judges = game._get_judges()
    sub0_id = game.submissions[game.submission_order[0]]["player_id"]
    sub1_id = game.submissions[game.submission_order[1]]["player_id"]
    game.execute_action(judges[0], "judge_pick_0")
    game.execute_action(judges[1], "judge_pick_1")
    assert game.get_player_by_id(sub0_id).score == 1  # type: ignore[union-attr]
    assert game.get_player_by_id(sub1_id).score == 1  # type: ignore[union-attr]


def test_random_method_resolves_to_independent_or_jury():
    game, _ = _setup_multi_judge(num_judges=2, num_players=4, judging_method="Random")
    assert game.active_judging_method in ("Independent", "Jury")


# ==========================================================================
# Bot game
# ==========================================================================


def test_bot_game_completes():
    opts = HumanityCardsOptions(winning_score=3)
    game = HumanityCardsGame(options=opts)
    game._build_decks = lambda: _inject_decks(game, white_count=500, black_count=100)  # type: ignore[method-assign]
    for i in range(4):
        game.add_player(f"Bot{i}", Bot(f"Bot{i}"))
    game.on_start()
    for _ in range(100_000):
        if game.status == "finished":
            break
        game.on_tick()
    assert game.status == "finished"


# ==========================================================================
# All-judge mode
# ==========================================================================


def test_all_judge_mode_everyone_submits_and_judges():
    game, _ = _setup_game(num_players=3, options=HumanityCardsOptions(num_judges=3))
    assert game._all_players_are_judges()
    for p in game.get_active_players():
        game.execute_action(p, "toggle_card_0")
        game.execute_action(p, "submit_cards")
    assert game.phase == "judging"
    assert len(game.submissions) == 3


def test_all_judge_mode_self_vote_hidden():
    game, _ = _get_to_judging(options=HumanityCardsOptions(num_judges=3))
    for judge in game._get_judges():
        for i, sub_idx in enumerate(game.submission_order):
            if game.submissions[sub_idx]["player_id"] == judge.id:
                assert game._is_judge_pick_hidden(judge, f"judge_pick_{i}") == Visibility.HIDDEN


def test_all_judge_mode_self_vote_blocked():
    game, _ = _get_to_judging(options=HumanityCardsOptions(num_judges=3))
    for judge in game._get_judges():
        for i, sub_idx in enumerate(game.submission_order):
            if game.submissions[sub_idx]["player_id"] == judge.id:
                game._judge_pick(judge, i)
                assert judge.id not in game.judge_picks


def test_all_judge_mode_no_czar_announcement():
    game, users = _setup_game(num_players=3, options=HumanityCardsOptions(num_judges=3))
    all_spoken = [m for u in users for m in u.get_spoken_messages()]
    assert not any("Card Czar" in m for m in all_spoken)


def test_all_judge_bot_game_completes():
    opts = HumanityCardsOptions(winning_score=2, num_judges=3)
    game = HumanityCardsGame(options=opts)
    game._build_decks = lambda: _inject_decks(game, white_count=500, black_count=100)  # type: ignore[method-assign]
    for i in range(3):
        game.add_player(f"Bot{i}", Bot(f"Bot{i}"))
    game.on_start()
    for _ in range(200_000):
        if game.status == "finished":
            break
        game.on_tick()
    assert game.status == "finished"


# ==========================================================================
# Judge announcement grammar
# ==========================================================================


def test_judge_announcement_two_judges_grammar():
    game, users = _setup_game(num_players=4, options=HumanityCardsOptions(num_judges=2))
    all_spoken = [m for u in users for m in u.get_spoken_messages()]
    judge_names = [j.name for j in game._get_judges()]
    msgs = [m for m in all_spoken if "Card Czar" in m]
    assert msgs
    msg = msgs[0]
    assert all(n in msg for n in judge_names)
    assert msg.count("and") == 1


def test_judge_announcement_three_judges_oxford_comma():
    game, users = _setup_game(num_players=4, options=HumanityCardsOptions(num_judges=3))
    all_spoken = [m for u in users for m in u.get_spoken_messages()]
    judge_names = [j.name for j in game._get_judges()]
    msgs = [m for m in all_spoken if "Card Czar" in m]
    assert msgs
    assert all(n in msgs[0] for n in judge_names)
    assert ", and " in msgs[0]


def test_whose_turn_judging_lists_pending_judges():
    game, users = _setup_multi_judge(num_judges=2, num_players=4)
    judges = game._get_judges()
    game.execute_action(judges[0], "judge_pick_0")
    non_judge = game._get_non_judges()[0]
    non_judge_user = next(u for u in users if u.username == non_judge.name)
    non_judge_user.clear_messages()
    game._action_whose_turn(non_judge, "whose_turn")
    spoken = non_judge_user.get_spoken_messages()
    assert any(judges[1].name in m for m in spoken)
    assert not any("submitted" in m.lower() for m in spoken)
