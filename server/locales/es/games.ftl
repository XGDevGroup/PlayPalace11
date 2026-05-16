# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Ninety Nine

# Round and turn flow
game-round-start = Ronda { $round }.
game-round-end = Ronda { $round } completa.
game-turn-start = Turno de { $player }.
game-your-turn = Tu turno.
game-no-turn = No es el turno de nadie ahora mismo.

# Score display
game-scores-header = Puntuaciones Actuales:
game-score-line = { $player }: { $score } puntos
game-final-scores-header = Puntuaciones Finales:

# Win/loss
game-winner = ¡{ $player } gana!
game-winner-score = ¡{ $player } gana con { $score } puntos!
game-tiebreaker = ¡Es un empate! ¡Ronda de desempate!
game-tiebreaker-players = ¡Es un empate entre { $players }! ¡Ronda de desempate!
game-eliminated = { $player } ha sido eliminado con { $score } puntos.

# Common options
game-set-target-score = Puntuación objetivo: { $score }
game-enter-target-score = Ingresa la puntuación objetivo:
game-option-changed-target = Puntuación objetivo establecida en { $score }.

game-set-team-mode = Modo de equipos: { $mode }
game-select-team-mode = Selecciona el modo de equipos
game-option-changed-team = Modo de equipos establecido en { $mode }.
game-team-mode-individual = Individual
game-team-mode-x-teams-of-y = { $num_teams } equipos de { $team_size }

# Boolean option values
option-on = activado
option-off = desactivado

# Status box

# Game end
game-leave = Salir del juego

# Round timer
round-timer-paused = { $player } ha pausado el juego (presiona p para iniciar la siguiente ronda).
round-timer-resumed = Temporizador de ronda reanudado.
round-timer-countdown = Siguiente ronda en { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Manteniendo { $value }.
dice-rerolling = Volviendo a tirar { $value }.
dice-locked = Ese dado está bloqueado y no puede ser cambiado.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Reparto { $current }/{ $total }.
game-you-deal = Repartes las cartas.
game-player-deals = { $player } reparte las cartas.

# Card names
card-name = { $rank } de { $suit }
no-cards = Sin cartas

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = negro
color-black-m = negro
color-black-f = negra
color-blue = azul
color-blue-m = azul
color-blue-f = azul
color-brown = marrón
color-brown-m = marrón
color-brown-f = marrón
color-gray = gris
color-gray-m = gris
color-gray-f = gris
color-green = verde
color-green-m = verde
color-green-f = verde
color-indigo = índigo
color-indigo-m = índigo
color-indigo-f = índigo
color-orange = naranja
color-orange-m = naranja
color-orange-f = naranja
color-pink = rosa
color-pink-m = rosa
color-pink-f = rosa
color-purple = púrpura
color-purple-m = púrpura
color-purple-f = púrpura
color-red = rojo
color-red-m = rojo
color-red-f = roja
color-violet = violeta
color-violet-m = violeta
color-violet-f = violeta
color-white = blanco
color-white-m = blanco
color-white-f = blanca
color-yellow = amarillo
color-yellow-m = amarillo
color-yellow-f = amarilla

# Suit names
suit-diamonds = diamantes
suit-clubs = tréboles
suit-hearts = corazones
suit-spades = picas

# Rank names
rank-ace = as
rank-ace-plural = ases
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
rank-jack = sota
rank-jack-plural = sotas
rank-queen = reina
rank-queen-plural = reinas
rank-king = rey
rank-king-plural = reyes

# Poker hand descriptions
poker-high-card-with = { $high } alta, con { $rest }
poker-high-card = { $high } alta
poker-pair-with = Par de { $pair }, con { $rest }
poker-pair = Par de { $pair }
poker-two-pair-with = Doble Par, { $high } y { $low }, con { $kicker }
poker-two-pair = Doble Par, { $high } y { $low }
poker-trips-with = Trío, { $trips }, con { $rest }
poker-trips = Trío, { $trips }
poker-straight-high = Escalera alta de { $high }
poker-flush-high-with = Color alta de { $high }, con { $rest }
poker-full-house = Full House, { $trips } sobre { $pair }
poker-quads-with = Póker, { $quads }, con { $kicker }
poker-quads = Póker, { $quads }
poker-straight-flush-high = Escalera de Color alta de { $high }
poker-unknown-hand = Mano desconocida

# Validation errors (common across games)
game-error-invalid-team-mode = El modo de equipos seleccionado no es válido para el número actual de jugadores.
