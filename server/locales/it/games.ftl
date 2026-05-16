# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Novantanove

# Round and turn flow
game-round-start = Round { $round }.
game-round-end = Round { $round } completato.
game-turn-start = È il turno di { $player }.
game-your-turn = È il tuo turno.
game-no-turn = Nessuno sta giocando in questo momento.

# Score display
game-scores-header = Punteggi attuali:
game-score-line = { $player }: { $score } punti
game-final-scores-header = Punteggi finali:

# Win/loss
game-winner = { $player } vince!
game-winner-score = { $player } vince con { $score } punti!
game-tiebreaker = È un pareggio! Round di spareggio!
game-tiebreaker-players = È un pareggio tra { $players }! Round di spareggio!
game-eliminated = { $player } è stato/a eliminato/a con { $score } punti.

# Common options
game-set-target-score = Punteggio obiettivo: { $score }
game-enter-target-score = Inserisci il punteggio obiettivo:
game-option-changed-target = Punteggio obiettivo impostato a { $score }.

game-set-team-mode = Modalità squadra: { $mode }
game-select-team-mode = Seleziona modalità squadra
game-option-changed-team = Modalità squadra impostata a { $mode }.
game-team-mode-individual = Individuale
game-team-mode-x-teams-of-y = { $num_teams } squadre da { $team_size }

# Boolean option values
option-on = attivo
option-off = disattivo

# Status box

# Game end
game-leave = Abbandona partita

# Round timer
round-timer-paused = { $player } ha messo in pausa il gioco (premi p per iniziare il prossimo round).
round-timer-resumed = Timer del round ripreso.
round-timer-countdown = Prossimo round tra { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Tengo { $value }.
dice-rerolling = Rilancio { $value }.
dice-locked = Quel dado è bloccato e non può essere cambiato.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Distribuzione { $current }/{ $total }.
game-you-deal = Tu distribuisci le carte.
game-player-deals = { $player } distribuisce le carte.

# Card names
card-name = { $rank } di { $suit }
no-cards = Nessuna carta

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = nero
color-black-m = nero
color-black-f = nera
color-blue = blu
color-blue-m = blu
color-blue-f = blu
color-brown = marrone
color-brown-m = marrone
color-brown-f = marrone
color-gray = grigio
color-gray-m = grigio
color-gray-f = grigia
color-green = verde
color-green-m = verde
color-green-f = verde
color-indigo = indaco
color-indigo-m = indaco
color-indigo-f = indaco
color-orange = arancione
color-orange-m = arancione
color-orange-f = arancione
color-pink = rosa
color-pink-m = rosa
color-pink-f = rosa
color-purple = porpora
color-purple-m = porpora
color-purple-f = porpora
color-red = rosso
color-red-m = rosso
color-red-f = rossa
color-violet = viola
color-violet-m = viola
color-violet-f = viola
color-white = bianco
color-white-m = bianco
color-white-f = bianca
color-yellow = giallo
color-yellow-m = giallo
color-yellow-f = gialla

# Suit names
suit-diamonds = quadri
suit-clubs = fiori
suit-hearts = cuori
suit-spades = picche

# Rank names
rank-ace = asso
rank-ace-plural = assi
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
rank-jack = fante
rank-jack-plural = fanti
rank-queen = regina
rank-queen-plural = regine
rank-king = re
rank-king-plural = re

# Poker hand descriptions
poker-high-card-with = { $high } alto, con { $rest }
poker-high-card = { $high } alto
poker-pair-with = Coppia di { $pair }, con { $rest }
poker-pair = Coppia di { $pair }
poker-two-pair-with = Doppia coppia, { $high } e { $low }, con { $kicker }
poker-two-pair = Doppia coppia, { $high } e { $low }
poker-trips-with = Tris, { $trips }, con { $rest }
poker-trips = Tris, { $trips }
poker-straight-high = Scala con { $high } alto
poker-flush-high-with = Colore con { $high } alto, con { $rest }
poker-full-house = Full house, { $trips } su { $pair }
poker-quads-with = Poker, { $quads }, con { $kicker }
poker-quads = Poker, { $quads }
poker-straight-flush-high = Scala colore con { $high } alto
poker-unknown-hand = Mano sconosciuta

# Validation errors (common across games)
game-error-invalid-team-mode = La modalità squadra selezionata non è valida per il numero attuale di giocatori.
