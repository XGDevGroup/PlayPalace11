# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Devedeset devet

# Round and turn flow
game-round-start = Runda { $round }.
game-round-end = Runda { $round } završena.
game-turn-start = { $player } je na potezu.
game-your-turn = Vi ste na potezu.
game-no-turn = Nitko trenutno nije na potezu.

# Score display
game-scores-header = Trenutni rezultati:
game-score-line = { $player }: { $score } bodova
game-final-scores-header = Konačni rezultati:

# Win/loss
game-winner = { $player } pobjeđuje!
game-winner-score = { $player } pobjeđuje sa { $score } bodova!
game-tiebreaker = Neriješeno! Runda za prekid izjednačenja!
game-tiebreaker-players = Neriješeno između { $players }! Runda za prekid izjednačenja!
game-eliminated = { $player } je eliminiran/a sa { $score } bodova.

# Common options
game-set-target-score = Ciljni rezultat: { $score }
game-enter-target-score = Unesite ciljni rezultat:
game-option-changed-target = Ciljni rezultat postavljen na { $score }.

game-set-team-mode = Timski način: { $mode }
game-select-team-mode = Odaberite timski način
game-option-changed-team = Timski način postavljen na { $mode }.
game-team-mode-individual = Individualno
game-team-mode-x-teams-of-y = { $num_teams } timova od { $team_size }

# Boolean option values
option-on = uključeno
option-off = isključeno

# Status box

# Game end
game-leave = Napusti igru

# Round timer
round-timer-paused = { $player } je pauzirao/la igru (pritisnite p za početak sljedeće runde).
round-timer-resumed = Odbrojavanje runde nastavljeno.
round-timer-countdown = Sljedeća runda za { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Zadržavam { $value }.
dice-rerolling = Ponovno bacam { $value }.
dice-locked = Ta kocka je zaključana i ne može se promijeniti.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Dijeljenje { $current }/{ $total }.
game-you-deal = Vi dijelite karte.
game-player-deals = { $player } dijeli karte.

# Card names
card-name = { $rank } { $suit }
no-cards = Nema karata

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = crna
color-black-m = crni
color-black-f = crna
color-blue = plava
color-blue-m = plavi
color-blue-f = plava
color-brown = smeđa
color-brown-m = smeđi
color-brown-f = smeđa
color-gray = siva
color-gray-m = sivi
color-gray-f = siva
color-green = zelena
color-green-m = zeleni
color-green-f = zelena
color-indigo = indigo
color-indigo-m = indigo
color-indigo-f = indigo
color-orange = narančasta
color-orange-m = narančasti
color-orange-f = narančasta
color-pink = ružičasta
color-pink-m = ružičasti
color-pink-f = ružičasta
color-purple = ljubičasta
color-purple-m = ljubičasti
color-purple-f = ljubičasta
color-red = crvena
color-red-m = crveni
color-red-f = crvena
color-violet = ljubičasta
color-violet-m = ljubičasti
color-violet-f = ljubičasta
color-white = bijela
color-white-m = bijeli
color-white-f = bijela
color-yellow = žuta
color-yellow-m = žuti
color-yellow-f = žuta

# Suit names
suit-diamonds = karo
suit-clubs = tref
suit-hearts = herc
suit-spades = pik

# Rank names
rank-ace = as
rank-ace-plural = asevi
rank-two = 2
rank-two-plural = dvojke
rank-three = 3
rank-three-plural = trojke
rank-four = 4
rank-four-plural = četvorke
rank-five = 5
rank-five-plural = petice
rank-six = 6
rank-six-plural = šestice
rank-seven = 7
rank-seven-plural = sedmice
rank-eight = 8
rank-eight-plural = osmice
rank-nine = 9
rank-nine-plural = devetke
rank-ten = 10
rank-ten-plural = desetke
rank-jack = dečko
rank-jack-plural = dečki
rank-queen = dama
rank-queen-plural = dame
rank-king = kralj
rank-king-plural = kraljevi

# Poker hand descriptions
poker-high-card-with = { $high } visoko, sa { $rest }
poker-high-card = { $high } visoko
poker-pair-with = Par { $pair }, sa { $rest }
poker-pair = Par { $pair }
poker-two-pair-with = Dva para, { $high } i { $low }, sa { $kicker }
poker-two-pair = Dva para, { $high } i { $low }
poker-trips-with = Tri iste, { $trips }, sa { $rest }
poker-trips = Tri iste, { $trips }
poker-straight-high = { $high } visoko skala
poker-flush-high-with = { $high } visoko flush, sa { $rest }
poker-full-house = Full house, { $trips } preko { $pair }
poker-quads-with = Četiri iste, { $quads }, sa { $kicker }
poker-quads = Četiri iste, { $quads }
poker-straight-flush-high = { $high } visoko skala boja
poker-unknown-hand = Nepoznata ruka

# Validation errors (common across games)
game-error-invalid-team-mode = Odabrani timski način nije valjan za trenutni broj igrača.
