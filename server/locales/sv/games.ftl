# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Nittionio

# Round and turn flow
game-round-start = Omgång { $round }.
game-round-end = Omgång { $round } slutförd.
game-turn-start = Det är { $player }s tur.
game-your-turn = Det är din tur.
game-no-turn = Det är ingen tur just nu.

# Score display
game-scores-header = Aktuella poäng:
game-score-line = { $player }: { $score } poäng
game-final-scores-header = Slutliga poäng:

# Win/loss
game-winner = { $player } vinner!
game-winner-score = { $player } vinner med { $score } poäng!
game-tiebreaker = Det är oavgjort! Utslagningsomgång!
game-tiebreaker-players = Det är oavgjort mellan { $players }! Utslagningsomgång!
game-eliminated = { $player } har blivit eliminerad med { $score } poäng.

# Common options
game-set-target-score = Målpoäng: { $score }
game-enter-target-score = Ange målpoäng:
game-option-changed-target = Målpoäng satt till { $score }.

game-set-team-mode = Lagläge: { $mode }
game-select-team-mode = Välj lagläge
game-option-changed-team = Lagläge satt till { $mode }.
game-team-mode-individual = Individuellt
game-team-mode-x-teams-of-y = { $num_teams } lag om { $team_size }

# Boolean option values
option-on = på
option-off = av

# Status box

# Game end
game-leave = Lämna spelet

# Round timer
round-timer-paused = { $player } har pausat spelet (tryck p för att starta nästa omgång).
round-timer-resumed = Omgångstimer återupptagen.
round-timer-countdown = Nästa omgång om { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Behåller { $value }.
dice-rerolling = Slår om { $value }.
dice-locked = Den tärningen är låst och kan inte ändras.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Ger { $current }/{ $total }.
game-you-deal = Du ger ut korten.
game-player-deals = { $player } ger ut korten.

# Card names
card-name = { $suit } { $rank }
no-cards = Inga kort

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = svart
color-black-m = svart
color-black-f = svart
color-blue = blå
color-blue-m = blå
color-blue-f = blå
color-brown = brun
color-brown-m = brun
color-brown-f = brun
color-gray = grå
color-gray-m = grå
color-gray-f = grå
color-green = grön
color-green-m = grön
color-green-f = grön
color-indigo = indigo
color-indigo-m = indigo
color-indigo-f = indigo
color-orange = orange
color-orange-m = orange
color-orange-f = orange
color-pink = rosa
color-pink-m = rosa
color-pink-f = rosa
color-purple = lila
color-purple-m = lila
color-purple-f = lila
color-red = röd
color-red-m = röd
color-red-f = röd
color-violet = violett
color-violet-m = violett
color-violet-f = violett
color-white = vit
color-white-m = vit
color-white-f = vit
color-yellow = gul
color-yellow-m = gul
color-yellow-f = gul

# Suit names
suit-diamonds = ruter
suit-clubs = klöver
suit-hearts = hjärter
suit-spades = spader

# Rank names
rank-ace = ess
rank-ace-plural = ess
rank-two = 2
rank-two-plural = 2:or
rank-three = 3
rank-three-plural = 3:or
rank-four = 4
rank-four-plural = 4:or
rank-five = 5
rank-five-plural = 5:or
rank-six = 6
rank-six-plural = 6:or
rank-seven = 7
rank-seven-plural = 7:or
rank-eight = 8
rank-eight-plural = 8:or
rank-nine = 9
rank-nine-plural = 9:or
rank-ten = 10
rank-ten-plural = 10:or
rank-jack = knekt
rank-jack-plural = knektar
rank-queen = dam
rank-queen-plural = damer
rank-king = kung
rank-king-plural = kungar

# Poker hand descriptions
poker-high-card-with = { $high } högt, med { $rest }
poker-high-card = { $high } högt
poker-pair-with = Par i { $pair }, med { $rest }
poker-pair = Par i { $pair }
poker-two-pair-with = Två par, { $high } och { $low }, med { $kicker }
poker-two-pair = Två par, { $high } och { $low }
poker-trips-with = Triss, { $trips }, med { $rest }
poker-trips = Triss, { $trips }
poker-straight-high = { $high } högt stege
poker-flush-high-with = { $high } högt färg, med { $rest }
poker-full-house = Kåk, { $trips } över { $pair }
poker-quads-with = Fyrtal, { $quads }, med { $kicker }
poker-quads = Fyrtal, { $quads }
poker-straight-flush-high = { $high } högt färgstege
poker-unknown-hand = Okänd hand

# Validation errors (common across games)
game-error-invalid-team-mode = Det valda lagläget är inte giltigt för det aktuella antalet spelare.
