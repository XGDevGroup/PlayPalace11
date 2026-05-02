# Humanity Cards - English localization

# Options
hc-set-winning-score = Winning score: { $score }
hc-desc-winning-score = Points needed to win
hc-enter-winning-score = Enter winning score:
hc-option-changed-winning-score = Winning score set to { $score }.

hc-set-hand-size = Hand size: { $count }
hc-desc-hand-size = Number of cards in hand
hc-enter-hand-size = Enter hand size:
hc-option-changed-hand-size = Hand size set to { $count }.

hc-set-card-packs = Card packs ({ $count } of { $total } selected)
hc-desc-card-packs = Which card packs to use
hc-option-changed-card-packs = Card pack selection changed.

hc-set-judging-method = Judging method: { $mode }
hc-select-judging-method = Select judging method
hc-desc-judging-method = How winning submissions are chosen. Independent: each judge picks a winner, one point per vote. Jury: majority wins; ties award all tied players one point. Random: method chosen randomly each round.
hc-option-changed-judging-method = Judging method set to { $mode }.
hc-judging-method-independent = Independent
hc-judging-method-jury = Jury
hc-judging-method-random = Random

hc-set-czar-selection = Card Czar selection: { $mode }
hc-select-czar-selection = Select Card Czar selection mode
hc-option-changed-czar-selection = Card Czar selection set to { $mode }.

hc-set-num-judges = Number of judges: { $count }
hc-enter-num-judges = Enter number of judges:
hc-option-changed-num-judges = Number of judges set to { $count }.

hc-czar-rotating = Rotating
hc-czar-random = Random
hc-czar-winner = Most Recent Winner

# Game flow
hc-game-starting = Shuffling the decks...
hc-dealing-cards = Dealing { $count } cards to each player.
hc-round-start = Round { $round }.

# Judge announcement
hc-judge-is = { $count ->
    [one] { $names } is the Card Czar.
   *[other] { $names } are the Card Czars.
}
hc-you-are-judge = You are the Card Czar this round.

hc-waiting-for-judges = Waiting for { $names } to judge.

# Black card
hc-black-card = The prompt is: { $text }
hc-black-card-pick = Pick { $count }.
hc-view-black-card = View the question card

# Submission phase
hc-select-cards = Select { $count } { $count ->
    [one] card
   *[other] cards
} from your hand.
hc-card-selected = { $text }, selected
hc-card-not-selected = { $text }
hc-card-fallback = Card { $index }
hc-submit-cards = Submit ({ $selected } of { $required } selected)
hc-submitted = You submitted your cards.
hc-already-submitted = You already submitted your cards.
hc-wrong-card-count = You need to select exactly { $count } { $count ->
    [one] card
   *[other] cards
}.

# Judging phase
hc-judging-start = All cards are in! Time to judge.
hc-judge-prompt-header = Choose the best card that matches: { $prompt }
hc-judge-prompt-header-empty = Choose the best card

# Results
hc-submission-fallback = Submission { $index }

hc-winner-announcement = { $player } gets { $points } { $points ->
    [one] point
   *[other] points
} for { $text }.
hc-all-submissions = Other submissions:
hc-submission-reveal = { $player }: { $text }

# View
hc-preview-submission = Preview your submission
hc-view-submission = View your submission
hc-preview-submission-text = Preview: { $text }
hc-your-submission = Your submission: { $text }
hc-select-cards-first = Select at least 1 card first.

# Win
hc-game-winner = { $player } wins with { $score } points!
hc-you-win = You win with { $score } points!

# Deck management
hc-deck-reshuffled = White card discard pile reshuffled into the deck.
hc-black-deck-reshuffled = Black card discard pile reshuffled into the deck.
hc-not-enough-cards = Not enough cards. Try enabling more packs.

# Hand management

# Scores
# Whose turn / whose judge
hc-whose-judge = Who is judging
hc-waiting-for = Waiting for { $names } to submit.
hc-all-submitted-waiting-judge = All players have submitted. Waiting for { $judge } to judge.
