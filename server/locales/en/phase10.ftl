# Phase 10

game-name-phase10 = Phase 10

# Card colors
phase10-color-red = Red
phase10-color-blue = Blue
phase10-color-green = Green
phase10-color-yellow = Yellow

# Card names
phase10-card-numbered = { $number } { $color }
phase10-card-wild = Wild
phase10-card-skip = Skip
phase10-card-label-selected = { $card } (selected)
phase10-card-label-staged = { $card } (staged)
phase10-lay-down-card-already-staged = { $card } is already staged in a previous group.

# Phase requirement short descriptions (used in prompts)
phase10-req-set = set of { $count }
phase10-req-run = run of { $count }
phase10-req-color = { $count } of one color

# Phase long descriptions
phase10-phase-desc-1 = 2 sets of 3
phase10-phase-desc-2 = 1 set of 3 and 1 run of 4
phase10-phase-desc-3 = 1 set of 4 and 1 run of 4
phase10-phase-desc-4 = 1 run of 7
phase10-phase-desc-5 = 1 run of 8
phase10-phase-desc-6 = 1 run of 9
phase10-phase-desc-7 = 2 sets of 4
phase10-phase-desc-8 = 7 cards of one color
phase10-phase-desc-9 = 1 set of 5 and 1 set of 2
phase10-phase-desc-10 = 1 set of 4 and 1 set of 3

# Options
phase10-set-winning-phase = Winning phase: { $phase }
phase10-enter-winning-phase = Enter the phase number to reach in order to win (1-10)
phase10-option-changed-winning-phase = Winning phase set to { $phase }.

phase10-set-turn-timer = Turn timer: { $mode }
phase10-select-turn-timer = Select turn timer
phase10-option-changed-turn-timer = Turn timer set to { $mode }.
phase10-timer-5 = 5 seconds
phase10-timer-10 = 10 seconds
phase10-timer-15 = 15 seconds
phase10-timer-20 = 20 seconds
phase10-timer-30 = 30 seconds
phase10-timer-45 = 45 seconds
phase10-timer-60 = 1 minute
phase10-timer-90 = 90 seconds
phase10-timer-unlimited = No limit

phase10-toggle-even-phases = Even phases only: { $enabled }
phase10-option-changed-even-phases = Even phases only: { $enabled }.

phase10-toggle-fixed-hands = Fixed hands mode: { $enabled }
phase10-option-changed-fixed-hands = Fixed hands mode: { $enabled }.

# Game setup
phase10-new-hand = Hand { $round }. Each player is dealt 10 cards.
phase10-start-discard = { $card } starts the discard pile.
phase10-start-discard-skip = A Skip starts the discard pile. { $player }'s turn is automatically skipped.

# Draw
phase10-draw-deck-action = Draw from deck
phase10-draw-discard-action = Draw { $card } from discard pile
phase10-you-draw-deck = You draw { $card }.
phase10-player-draws-deck = { $player } draws from the deck.
phase10-you-draw-discard = You draw { $card } from the discard pile.
phase10-player-draws-discard = { $player } draws { $card } from the discard pile.
phase10-cannot-draw-skip = Skip cards cannot be taken from the discard pile.
phase10-deck-reshuffled = Discard pile reshuffled into the draw pile.
phase10-deck-truly-empty = No cards remain to draw. Hand ends.

# Lay down phase — action labels
phase10-lay-down-action = Lay down Phase { $phase }
phase10-confirm-group-action = Confirm group { $current } of { $total }
phase10-check-req-action = Check requirement
phase10-check-req-result = { $req }
phase10-cancel-lay-down-action = Cancel lay-down

# Lay down phase — flow messages
phase10-lay-down-start = Laying down Phase { $phase }: { $description }. Group { $current } of { $total }: { $req }.
phase10-lay-down-next-group = Group { $prev } confirmed. Group { $current } of { $total }: { $req }.
phase10-lay-down-add = { $card } added. Group { $current } selection: { $cards }.
phase10-lay-down-remove = { $card } removed. Group { $current } selection: { $cards }.
phase10-lay-down-selection-empty = Group { $current } selection is empty.
phase10-lay-down-confirmed-group = Group { $current } confirmed: { $cards }.
phase10-lay-down-success = You lay down Phase { $phase } ({ $description }): { $details }.
phase10-player-lays-down = { $player } lays down Phase { $phase } ({ $description }): { $details }.
phase10-lay-down-cancel = Phase lay-down cancelled.
phase10-hit-cancelled = Hit cancelled.

# Lay down phase — validation errors
phase10-err-need-cards = Need at least { $count } { $count ->
    [one] card
   *[other] cards
} for this group.
phase10-err-invalid-set = All cards in a set must share the same number.
phase10-err-invalid-run = Cards in a run must form a consecutive sequence.
phase10-err-invalid-color = All cards in a color group must share the same color.
phase10-err-need-natural = At least one non-Wild card is required per group.

# Lay down phase — guard messages
phase10-already-laid-down = You have already laid down your phase this hand.
phase10-must-draw-first = Draw a card before taking this action.

# Hit — action labels
phase10-hit-action = Hit
phase10-hit-cancel-action = Cancel hit

# Hit — flow messages
phase10-hit-mode-start = Select a card from your hand to hit with. Press Escape to cancel.
phase10-hit-choose-group = Hitting { $card }. Select a group to hit onto, or cancel.
phase10-hit-success = You hit { $card } onto { $target }'s group.
phase10-player-hits = { $player } hits { $card } onto { $target }'s group.
phase10-hit-invalid = { $card } does not fit that group: { $reason }.
phase10-hit-no-phase = Lay down your own phase before hitting.
phase10-hit-no-groups = No phases have been laid down yet.
phase10-hit-invalid-set = card does not match the group's number
phase10-hit-invalid-run = card does not extend the run
phase10-hit-invalid-color = card does not match the group's color
phase10-hit-wild-choose = Wild on a run. Choose which end to extend.
phase10-hit-wild-low = Extend low end to { $value }
phase10-hit-wild-high = Extend high end to { $value }

# Discard
phase10-discard-action = Discard
phase10-discard-confirm-action = Discard { $card }
phase10-no-card-selected = No card selected. Navigate to a card and press Enter to select it, then Delete to discard.
phase10-you-discard = You discard { $card }.
phase10-player-discards = { $player } discards { $card }.

# Skip — action labels
phase10-skip-target-label = { $player }, Phase { $phase }
phase10-skip-cancel-action = Cancel skip

# Skip — flow messages
phase10-skip-choose-target = You discarded a Skip. Choose a player to skip, or cancel.
phase10-skip-cancelled = Skip cancelled.
phase10-skip-played = You skip { $target }.
phase10-player-skips = { $player } plays a Skip on { $target }.
phase10-you-are-skipped = { $skipping_player } skips you. Your turn is lost.
phase10-skip-already-used = { $player } has already been skipped this round.
phase10-skip-self = You cannot skip yourself.
phase10-your-turn-skipped = Your turn has been skipped.

# Status / info — action labels
phase10-read-hand-action = Read hand
phase10-read-discard-action = Read top of discard pile
phase10-read-table-action = Read table groups
phase10-check-phase-action = Check phase status
phase10-read-counts-action = Read card counts
phase10-turn-timer-action = Check turn timer

# Status / info — messages
phase10-your-phase = You are on Phase { $phase }: { $description }.
phase10-your-phase-laid-down = Your Phase { $phase } is laid down. Waiting for end of hand.
phase10-phase-status-header = Phase status:
phase10-player-phase-entry = { $player }: Phase { $phase }{ $laid_down ->
    [true]  (laid down)
   *[other] }
phase10-top-discard = { $card }.
phase10-no-discard = The discard pile is empty.
phase10-draw-pile-size = { $count } { $count ->
    [one] card
   *[other] cards
} in the draw pile.
phase10-hand-contents = Your hand ({ $count } { $count ->
    [one] card
   *[other] cards
}): { $cards }.
phase10-player-hand-count = { $player }: { $count } { $count ->
    [one] card
   *[other] cards
}.
phase10-deck-count = Draw pile: { $count } { $count ->
    [one] card
   *[other] cards
} remaining.
phase10-group-summary-set = { $count } { $rank ->
    [1] ones
    [2] twos
    [3] threes
    [4] fours
    [5] fives
    [6] sixes
    [7] sevens
    [8] eights
    [9] nines
    [10] tens
    [11] elevens
    [12] twelves
   *[other] { $rank }s
}
phase10-group-summary-run = { $low } through { $high }
phase10-group-summary-color = { $count } { $color }s
phase10-no-table-groups = No phases have been laid down on the table yet.
phase10-table-group-header = Table groups:
phase10-table-group-entry = { $owner }: { $cards }.

# Round end
phase10-you-go-out = You go out! Hand { $round } over.
phase10-player-goes-out = { $player } goes out. Hand { $round } over.
phase10-round-scoring-header = Scoring:
phase10-you-score-zero = You went out. No penalty points this hand.
phase10-you-score = You score { $points } penalty { $points ->
    [one] point
   *[other] points
}. Running total: { $total }.
phase10-player-scores-zero = { $player } went out. No penalty.
phase10-player-scores = { $player } scores { $points } penalty { $points ->
    [one] point
   *[other] points
}. Total: { $total }.
phase10-you-advance = You advance to Phase { $next }.
phase10-you-stay = You stay on Phase { $phase }.
phase10-player-advances = { $player } advances to Phase { $next }.
phase10-player-stays = { $player } stays on Phase { $phase }.
phase10-fixed-hands-advance = { $player } advances to Phase { $next } (fixed hands).
phase10-you-fixed-hands-advance = You advance to Phase { $next } (fixed hands).

# Game end
phase10-phase-completed = { $player } completes Phase { $phase }!
phase10-you-completed-phase = You complete Phase { $phase }!
phase10-game-winner = { $player } wins with { $score } penalty { $score ->
    [one] point
   *[other] points
}!
phase10-you-win = You win with { $score } penalty { $score ->
    [one] point
   *[other] points
}!
phase10-tiebreaker = Scores are tied between { $players }! Replaying Phase { $phase }.
phase10-tiebreaker-you = It's a tie! You replay Phase { $phase }.
phase10-fixed-hands-over = 10 hands complete.

# Hand sort
phase10-sort-by-color-action = Sort hand by color
phase10-sort-by-number-action = Sort hand by number
phase10-sorted-by-color = Hand sorted by color.
phase10-sorted-by-number-asc = Hand sorted by number, ascending.
phase10-sorted-by-number-desc = Hand sorted by number, descending.

# Score display (S key)
phase10-score-header = Scores (lower is better):
phase10-score-entry = { $player }: Phase { $phase }, { $score }
