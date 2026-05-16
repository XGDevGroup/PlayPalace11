# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Devedeset devet
game-name-humanitycards = Karte protiv čovečanstva

# Game categories (shared)
category-party-games = Društvene igre

# Round and turn flow
game-round-start = Runda { $round }.
game-round-end = Runda { $round } završena.
game-turn-start = { $player } je na potezu.
game-your-turn = Vi ste na potezu.
game-no-turn = Niko trenutno nije na potezu.

# Score display
game-scores-header = Trenutni rezultat:
game-score-line = { $player }: { $score } poena
game-final-scores-header = Krajnji rezultat:

# Win/loss
game-winner = { $player } pobeđuje!
game-winner-score = { $player } pobeđuje sa { $score } poena!
game-tiebreaker = Izjednačeno! Odlučujuća runda!
game-tiebreaker-players = Izjednačeno je između igrača { $players }! Odlučujuća runda!
game-eliminated = { $player } ispada sa { $score } poena.

# Common options
game-set-target-score = Krajnji rezultat: { $score }
game-enter-target-score = Upišite krajnji rezultat:
game-option-changed-target = Krajnji rezultat podešen na { $score }.

game-set-team-mode = Režim timova: { $mode }
game-select-team-mode = Izaberite režim timova
game-option-changed-team = Režim timova podešen na { $mode }.
game-team-mode-individual = Individualni
game-team-mode-x-teams-of-y = { $num_teams } timova sa po { $team_size }

# Boolean option values
option-on = Uključeno
option-off = Isključeno

# Option navigation
option-back = Nazad
option-min-selected = Bar { $count } { $count ->
    [one] stavka mora biti izabrana
    [few] stavke moraju biti izabrane
   *[other] stavki mora biti izabrano
}.
option-max-selected = Najviše { $count } { $count ->
    [one] stavka može biti izabrana
    [few] stavke mogu biti izabrane
   *[other] stavki može biti izabrano
}.
option-select-all = Izaberi sve
option-deselect-all = Opozovi izbor svih opcija
option-selected-count = { $count } { $count ->
    [one] stavka izabrana
    [few] stavke izabrane
    *[other] stavki izabrano
}.
option-deselected-count = { $count } { $count ->
    [one] stavka nije izabrana
    [few] stavke nisu izabrane
    *[other] stavki nije izabrano
}.

# Status box

# Game end
game-leave = Napusti igru

# Round timer
round-timer-paused = { $player } pauzira igru (pritisnite P da započnete sledeću rundu).
round-timer-resumed = Tajmer runde nastavljen.
round-timer-countdown = Sledeća runda za { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Zadržava se { $value }.
dice-rerolling = Ponovo se baca { $value }.
dice-locked = Ova kockica je zaključana i ne može se promeniti.
dice-status-locked = Zaključana
dice-status-kept = Zadržana

# Dealing (card games)
game-deal-counter = Deljenje { $current }/{ $total }.
game-you-deal = Delite karte.
game-player-deals = { $player } deli karte.

# Card names
card-name = { $rank }  { $suit }
no-cards = Nema karata

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = Crna
color-black-m = crni
color-black-f = crna
color-blue = Plava
color-blue-m = plavi
color-blue-f = plava
color-brown = Braon
color-brown-m = braon
color-brown-f = braon
color-gray = Siva
color-gray-m = sivi
color-gray-f = siva
color-green = Zelena
color-green-m = zeleni
color-green-f = zelena
color-indigo = indigo
color-indigo-m = indigo
color-indigo-f = indigo
color-orange = Narandžasta
color-orange-m = narandžasti
color-orange-f = narandžasta
color-pink = Ružičasta
color-pink-m = ružičasti
color-pink-f = ružičasta
color-purple = Ljubičasta
color-purple-m = ljubičasti
color-purple-f = ljubičasta
color-red = Crvena
color-red-m = crveni
color-red-f = crvena
color-violet = Ljubičasta
color-violet-m = ljubičasti
color-violet-f = ljubičasta
color-white = Bela
color-white-m = beli
color-white-f = bela
color-yellow = Žuta
color-yellow-m = žuti
color-yellow-f = žuta

# Suit names
suit-diamonds = Karo
suit-clubs = Tref
suit-hearts = Herc
suit-spades = Pik

# Rank names
rank-ace = Kec
rank-ace-plural = Kečevi
rank-two = 2
rank-two-plural = Dvojke
rank-three = 3
rank-three-plural = Trojke
rank-four = 4
rank-four-plural = Četvorke
rank-five = 5
rank-five-plural = Petice
rank-six = 6
rank-six-plural = Šestice
rank-seven = 7
rank-seven-plural = Sedmice
rank-eight = 8
rank-eight-plural = Osmice
rank-nine = 9
rank-nine-plural = Devetke
rank-ten = 10
rank-ten-plural = Desetke
rank-jack = Žandar
rank-jack-plural = Žandari
rank-queen = Dama
rank-queen-plural = Dame
rank-king = Kralj
rank-king-plural = Kraljevi
rank-joker = Džoker
rank-joker-plural = Džokeri

# Shapes
shape-circle = Krug
shape-cone = Konus
shape-cylinder = Cilindar
shape-hexagon = heksagon
shape-oval = Ovalni
shape-pentagon = pentagon
shape-prism = Prizma
shape-rectangle = Pravougaonik
shape-square = Kvadrat
shape-triangle = Trougao

# Poker hand descriptions
poker-high-card-with = { $high } najjača, sa { $rest }
poker-high-card = { $high } najjača
poker-pair-with = { $pair } par, uz { $rest }
poker-pair = { $pair } par
poker-two-pair-with = Dva para, { $high } i { $low }, uz { $kicker }
poker-two-pair = Dva para, { $high } i { $low }
poker-trips-with = Tri iste, { $trips }, uz { $rest }
poker-trips = Tri iste, { $trips }
poker-straight-high = { $high } kenta
poker-flush-high-with = { $high } boja, uz { $rest }
poker-full-house = Ful haus, { $trips } i { $pair }
poker-quads-with = Četiri iste, { $quads }, uz { $kicker }
poker-quads = Četiri iste, { $quads }
poker-straight-flush-high = { $high } kenta boje
poker-unknown-hand = Nepoznata ruka

# Validation errors (common across games)
game-error-invalid-team-mode = Izabran režim timova nije ispravan sa trenutnim brojem igrača.
