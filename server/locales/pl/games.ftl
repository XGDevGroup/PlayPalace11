# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Ninety Nine
game-name-humanitycards = Karty przeciwko ludzkości

# Game categories (shared)
category-party-games = Gry imprezowe

# Round and turn flow
game-round-start = Runda { $round }.
game-round-end = Runda { $round } zakończona.
game-turn-start = Kolej { $player }.
game-your-turn = Twoja kolej.
game-no-turn = Obecnie brak czyjejkolwiek tury.

# Score display
game-scores-header = Obecne statystyki:
game-score-line = { $player }: { $score } points
game-final-scores-header = Finalne statystyki:

# Win/loss
game-winner = Wygrał { $player }!
game-winner-score = { $player } wygrał osiągając { $score } punktów!
game-tiebreaker = It's a tie! Tiebreaker round!
game-tiebreaker-players = It's a tie between { $players }! Tiebreaker round!
game-eliminated = { $player } został wyeliminowany z liczbą { $score } punktów.

# Common options
game-set-target-score = Maksymalna liczba punktów: { $score }
game-enter-target-score = Podaj maksymalną liczbę punktów:
game-option-changed-target = Maksymalna liczba punktów została ustawiona na { $score }.

game-set-team-mode = Team mode: { $mode }
game-select-team-mode = Wybierz tryb gry
game-option-changed-team = Tryb gry został ustawiony na { $mode }.
game-team-mode-individual = Indywidualna
game-team-mode-x-teams-of-y = { $num_teams } drużyn po { $team_size } graczy

# Boolean option values
option-on = Wł
option-off = Wył

# Option navigation
option-back = Wróć
option-min-selected = Wybierz co najmniej { $count } { $count ->
    [one] element
   *[other] elementów
}.
option-max-selected = Wybierz maksymalnie { $count } { $count ->
    [one] element
   *[other] elementów
}.
option-select-all = Zaznacz wszystko
option-deselect-all = Odznacz wszystko
option-selected-count = Wybrano { $count } { $count ->
    [one] element
   *[other] elementów
}.
option-deselected-count = Wybrano { $count } { $count ->
    [one] element
   *[other] elementów
}.

# Status box

# Game end
game-leave = Opuść grę

# Round timer
round-timer-paused = { $player } wstrzymał grę. Naciśnij P, aby rozpocząć następną rundę.
round-timer-resumed = Licznik rund wznowiony
round-timer-countdown = Następna runda za { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Keeping { $value }.
dice-rerolling = Rerolling { $value }.
dice-locked = That die is locked and cannot be changed.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Deal { $current }/{ $total }.
game-you-deal = You deal out the cards.
game-player-deals = { $player } deals out the cards.

# Card names
card-name = { $rank } of { $suit }
no-cards = No cards

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = czarny
color-black-m = czarny
color-black-f = czarna
color-blue = niebieski
color-blue-m = niebieski
color-blue-f = niebieska
color-brown = brązowy
color-brown-m = brązowy
color-brown-f = brązowa
color-gray = szary
color-gray-m = szary
color-gray-f = szara
color-green = zielony
color-green-m = zielony
color-green-f = zielona
color-indigo = indygo
color-indigo-m = indygo
color-indigo-f = indygo
color-orange = pomarańczowy
color-orange-m = pomarańczowy
color-orange-f = pomarańczowa
color-pink = różowy
color-pink-m = różowy
color-pink-f = różowa
color-purple = purpurowy
color-purple-m = purpurowy
color-purple-f = purpurowa
color-red = czerwony
color-red-m = czerwony
color-red-f = czerwona
color-violet = fioletowy
color-violet-m = fioletowy
color-violet-f = fioletowa
color-white = biały
color-white-m = biały
color-white-f = biała
color-yellow = żółty
color-yellow-m = żółty
color-yellow-f = żółta

# Suit names
suit-diamonds = diamonds
suit-clubs = clubs
suit-hearts = hearts
suit-spades = spades

# Rank names
rank-ace = ace
rank-ace-plural = aces
rank-two = 2
rank-two-plural = 2s
rank-three = 3
rank-three-plural = 3s
rank-four = 4
rank-four-plural = 4s
rank-five = 5
rank-five-plural = 5s
rank-six = 6
rank-six-plural = 6s
rank-seven = 7
rank-seven-plural = 7s
rank-eight = 8
rank-eight-plural = 8s
rank-nine = 9
rank-nine-plural = 9s
rank-ten = 10
rank-ten-plural = 10s
rank-jack = jack
rank-jack-plural = jacks
rank-queen = queen
rank-queen-plural = queens
rank-king = king
rank-king-plural = kings
rank-joker = joker
rank-joker-plural = jokers

# Shapes
shape-circle = circle
shape-cone = cone
shape-cylinder = cylinder
shape-hexagon = hexagon
shape-oval = oval
shape-pentagon = pentagon
shape-prism = prism
shape-rectangle = rectangle
shape-square = square
shape-triangle = triangle

# Poker hand descriptions
poker-high-card-with = { $high } high, with { $rest }
poker-high-card = { $high } high
poker-pair-with = Pair of { $pair }, with { $rest }
poker-pair = Pair of { $pair }
poker-two-pair-with = Two Pair, { $high } and { $low }, with { $kicker }
poker-two-pair = Two Pair, { $high } and { $low }
poker-trips-with = Three of a Kind, { $trips }, with { $rest }
poker-trips = Three of a Kind, { $trips }
poker-straight-high = { $high } high Straight
poker-flush-high-with = { $high } high Flush, with { $rest }
poker-full-house = Full House, { $trips } over { $pair }
poker-quads-with = Four of a Kind, { $quads }, with { $kicker }
poker-quads = Four of a Kind, { $quads }
poker-straight-flush-high = { $high } high Straight Flush
poker-unknown-hand = Unknown hand

# Validation errors (common across games)
game-error-invalid-team-mode = Wybrany tryb gry drużynowej nie jest dostępny w przypadku tej liczby graczy.
