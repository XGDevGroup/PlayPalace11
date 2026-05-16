# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Nouăzeci și nouă

# Round and turn flow
game-round-start = Runda { $round }.
game-round-end = Runda { $round } completă.
game-turn-start = Este rândul lui { $player }.
game-your-turn = Este rândul tău.
game-no-turn = Nu este rândul nimănui acum.

# Score display
game-scores-header = Scoruri curente:
game-score-line = { $player }: { $score } puncte
game-final-scores-header = Scoruri finale:

# Win/loss
game-winner = { $player } câștigă!
game-winner-score = { $player } câștigă cu { $score } puncte!
game-tiebreaker = Este egalitate! Rundă de departajare!
game-tiebreaker-players = Este egalitate între { $players }! Rundă de departajare!
game-eliminated = { $player } a fost eliminat/ă cu { $score } puncte.

# Common options
game-set-target-score = Scor țintă: { $score }
game-enter-target-score = Introduceți scorul țintă:
game-option-changed-target = Scor țintă setat la { $score }.

game-set-team-mode = Mod echipă: { $mode }
game-select-team-mode = Selectați modul echipă
game-option-changed-team = Mod echipă setat la { $mode }.
game-team-mode-individual = Individual
game-team-mode-x-teams-of-y = { $num_teams } echipe de { $team_size }

# Boolean option values
option-on = activat
option-off = dezactivat

# Status box

# Game end
game-leave = Părăsește jocul

# Round timer
round-timer-paused = { $player } a pus jocul pe pauză (apăsați p pentru a începe următoarea rundă).
round-timer-resumed = Cronometrul rundei reluat.
round-timer-countdown = Următoarea rundă în { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Păstrez { $value }.
dice-rerolling = Relansez { $value }.
dice-locked = Acel zar este blocat și nu poate fi schimbat.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Împărțire { $current }/{ $total }.
game-you-deal = Tu împarți cărțile.
game-player-deals = { $player } împarte cărțile.

# Card names
card-name = { $rank } de { $suit }
no-cards = Fără cărți

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = negru
color-black-m = negru
color-black-f = neagră
color-blue = albastru
color-blue-m = albastru
color-blue-f = albastră
color-brown = maro
color-brown-m = maro
color-brown-f = maro
color-gray = gri
color-gray-m = gri
color-gray-f = gri
color-green = verde
color-green-m = verde
color-green-f = verde
color-indigo = indigo
color-indigo-m = indigo
color-indigo-f = indigo
color-orange = portocaliu
color-orange-m = portocaliu
color-orange-f = portocalie
color-pink = roz
color-pink-m = roz
color-pink-f = roz
color-purple = purpuriu
color-purple-m = purpuriu
color-purple-f = purpurie
color-red = roșu
color-red-m = roșu
color-red-f = roșie
color-violet = violet
color-violet-m = violet
color-violet-f = violetă
color-white = alb
color-white-m = alb
color-white-f = albă
color-yellow = galben
color-yellow-m = galben
color-yellow-f = galbenă

# Suit names
suit-diamonds = romburi
suit-clubs = treflă
suit-hearts = inimi
suit-spades = pică

# Rank names
rank-ace = as
rank-ace-plural = ași
rank-two = 2
rank-two-plural = 2
rank-three = 3
rank-three-plural = 3
rank-four = 4
rank-four-plural = 4
rank-five = 5
rank-five-plural = 5
rank-six = 6
rank-six-plural = 6
rank-seven = 7
rank-seven-plural = 7
rank-eight = 8
rank-eight-plural = 8
rank-nine = 9
rank-nine-plural = 9
rank-ten = 10
rank-ten-plural = 10
rank-jack = valet
rank-jack-plural = valeți
rank-queen = damă
rank-queen-plural = dame
rank-king = rege
rank-king-plural = regi

# Poker hand descriptions
poker-high-card-with = { $high } înalt, cu { $rest }
poker-high-card = { $high } înalt
poker-pair-with = Pereche de { $pair }, cu { $rest }
poker-pair = Pereche de { $pair }
poker-two-pair-with = Două perechi, { $high } și { $low }, cu { $kicker }
poker-two-pair = Două perechi, { $high } și { $low }
poker-trips-with = Trei de același fel, { $trips }, cu { $rest }
poker-trips = Trei de același fel, { $trips }
poker-straight-high = Chintă cu { $high } înalt
poker-flush-high-with = Culoare cu { $high } înalt, cu { $rest }
poker-full-house = Full house, { $trips } peste { $pair }
poker-quads-with = Careu, { $quads }, cu { $kicker }
poker-quads = Careu, { $quads }
poker-straight-flush-high = Chintă culoare cu { $high } înalt
poker-unknown-hand = Mână necunoscută

# Validation errors (common across games)
game-error-invalid-team-mode = Modul echipă selectat nu este valid pentru numărul curent de jucători.
