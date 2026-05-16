# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Ninety Nine

# Round and turn flow
game-round-start = Ronde { $round }.
game-round-end = Ronde { $round } voltooid.
game-turn-start = { $player } is aan de beurt.
game-your-turn = Jij bent aan de beurt.
game-no-turn = Niemand is nu aan de beurt.

# Score display
game-scores-header = Huidige Scores:
game-score-line = { $player }: { $score } punten
game-final-scores-header = Eindscores:

# Win/loss
game-winner = { $player } wint!
game-winner-score = { $player } wint met { $score } punten!
game-tiebreaker = Het is gelijk! Tie-breaker ronde!
game-tiebreaker-players = Het is gelijk tussen { $players }! Tie-breaker ronde!
game-eliminated = { $player } is geëlimineerd met { $score } punten.

# Common options
game-set-target-score = Doelscore: { $score }
game-enter-target-score = Voer doelscore in:
game-option-changed-target = Doelscore ingesteld op { $score }.

game-set-team-mode = Teammodus: { $mode }
game-select-team-mode = Selecteer teammodus
game-option-changed-team = Teammodus ingesteld op { $mode }.
game-team-mode-individual = Individueel
game-team-mode-x-teams-of-y = { $num_teams } teams van { $team_size }

# Boolean option values
option-on = aan
option-off = uit

# Status box

# Game end
game-leave = Verlaat spel

# Round timer
round-timer-paused = { $player } heeft het spel gepauzeerd (druk op p om de volgende ronde te starten).
round-timer-resumed = Rondetimer hervat.
round-timer-countdown = Volgende ronde over { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = { $value } bewaren.
dice-rerolling = { $value } opnieuw gooien.
dice-locked = Die dobbelsteen is vergrendeld en kan niet worden gewijzigd.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Deel { $current }/{ $total }.
game-you-deal = Jij deelt de kaarten uit.
game-player-deals = { $player } deelt de kaarten uit.

# Card names
card-name = { $rank } van { $suit }
no-cards = Geen kaarten

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = zwart
color-black-m = zwart
color-black-f = zwart
color-blue = blauw
color-blue-m = blauw
color-blue-f = blauw
color-brown = bruin
color-brown-m = bruin
color-brown-f = bruin
color-gray = grijs
color-gray-m = grijs
color-gray-f = grijs
color-green = groen
color-green-m = groen
color-green-f = groen
color-indigo = indigo
color-indigo-m = indigo
color-indigo-f = indigo
color-orange = oranje
color-orange-m = oranje
color-orange-f = oranje
color-pink = roze
color-pink-m = roze
color-pink-f = roze
color-purple = paars
color-purple-m = paars
color-purple-f = paars
color-red = rood
color-red-m = rood
color-red-f = rood
color-violet = violet
color-violet-m = violet
color-violet-f = violet
color-white = wit
color-white-m = wit
color-white-f = wit
color-yellow = geel
color-yellow-m = geel
color-yellow-f = geel

# Suit names
suit-diamonds = ruiten
suit-clubs = klaveren
suit-hearts = harten
suit-spades = schoppen

# Rank names
rank-ace = aas
rank-ace-plural = azen
rank-two = 2
rank-two-plural = 2's
rank-three = 3
rank-three-plural = 3's
rank-four = 4
rank-four-plural = 4's
rank-five = 5
rank-five-plural = 5's
rank-six = 6
rank-six-plural = 6's
rank-seven = 7
rank-seven-plural = 7's
rank-eight = 8
rank-eight-plural = 8's
rank-nine = 9
rank-nine-plural = 9's
rank-ten = 10
rank-ten-plural = 10's
rank-jack = boer
rank-jack-plural = boeren
rank-queen = vrouw
rank-queen-plural = vrouwen
rank-king = heer
rank-king-plural = heren

# Poker hand descriptions
poker-high-card-with = { $high } hoog, met { $rest }
poker-high-card = { $high } hoog
poker-pair-with = Paar { $pair }, met { $rest }
poker-pair = Paar { $pair }
poker-two-pair-with = Twee Paar, { $high } en { $low }, met { $kicker }
poker-two-pair = Twee Paar, { $high } en { $low }
poker-trips-with = Three of a Kind, { $trips }, met { $rest }
poker-trips = Three of a Kind, { $trips }
poker-straight-high = { $high } hoog Straat
poker-flush-high-with = { $high } hoog Flush, met { $rest }
poker-full-house = Full House, { $trips } over { $pair }
poker-quads-with = Four of a Kind, { $quads }, met { $kicker }
poker-quads = Four of a Kind, { $quads }
poker-straight-flush-high = { $high } hoog Straight Flush
poker-unknown-hand = Onbekende hand

# Validation errors (common across games)
game-error-invalid-team-mode = De geselecteerde teammodus is niet geldig voor het huidige aantal spelers.
