# Mensagens compartilhadas de jogos para PlayPalace (Português)
# Estas mensagens são comuns a vários jogos

# Nomes de jogos
game-name-ninetynine = Noventa e Nove

# Fluxo de rodadas e turnos
game-round-start = Rodada { $round }.
game-round-end = Rodada { $round } concluída.
game-turn-start = Vez de { $player }.
game-your-turn = Sua vez.
game-no-turn = Não é a vez de ninguém agora.

# Exibição de pontuação
game-scores-header = Pontuação Atual:
game-score-line = { $player }: { $score } pontos
game-final-scores-header = Pontuação Final:

# Vitória/derrota
game-winner = { $player } venceu!
game-winner-score = { $player } venceu com { $score } pontos!
game-tiebreaker = Empate! Rodada de desempate!
game-tiebreaker-players = Empate entre { $players }! Rodada de desempate!
game-eliminated = { $player } foi eliminado com { $score } pontos.

# Opções comuns
game-set-target-score = Pontuação alvo: { $score }
game-enter-target-score = Digite a pontuação alvo:
game-option-changed-target = Pontuação alvo definida para { $score }.

game-set-team-mode = Modo de equipe: { $mode }
game-select-team-mode = Selecione o modo de equipe
game-option-changed-team = Modo de equipe definido para { $mode }.
game-team-mode-individual = Individual
game-team-mode-x-teams-of-y = { $num_teams } equipes de { $team_size }

# Valores de opções booleanas
option-on = ligado
option-off = desligado

# Caixa de status

# Fim de jogo
game-leave = Sair do jogo

# Temporizador de rodada
round-timer-paused = { $player } pausou o jogo (pressione p para iniciar a próxima rodada).
round-timer-resumed = Temporizador retomado.
round-timer-countdown = Próxima rodada em { $seconds }...

# Jogos de dados - manter/soltar dados
dice-keeping = Mantendo { $value }.
dice-rerolling = Relançando { $value }.
dice-locked = Esse dado está bloqueado e não pode ser alterado.
dice-status-locked = locked
dice-status-kept = kept

# Distribuição (jogos de cartas)
game-deal-counter = Distribuição { $current }/{ $total }.
game-you-deal = Você distribui as cartas.
game-player-deals = { $player } distribui as cartas.

# Nomes de cartas
card-name = { $rank } de { $suit }
no-cards = Sem cartas

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = preto
color-black-m = preto
color-black-f = preta
color-blue = azul
color-blue-m = azul
color-blue-f = azul
color-brown = castanho
color-brown-m = castanho
color-brown-f = castanha
color-gray = cinzento
color-gray-m = cinzento
color-gray-f = cinzenta
color-green = verde
color-green-m = verde
color-green-f = verde
color-indigo = índigo
color-indigo-m = índigo
color-indigo-f = índigo
color-orange = laranja
color-orange-m = laranja
color-orange-f = laranja
color-pink = rosa
color-pink-m = rosa
color-pink-f = rosa
color-purple = roxo
color-purple-m = roxo
color-purple-f = roxa
color-red = vermelho
color-red-m = vermelho
color-red-f = vermelha
color-violet = violeta
color-violet-m = violeta
color-violet-f = violeta
color-white = branco
color-white-m = branco
color-white-f = branca
color-yellow = amarelo
color-yellow-m = amarelo
color-yellow-f = amarela

# Nomes dos naipes
suit-diamonds = ouros
suit-clubs = paus
suit-hearts = copas
suit-spades = espadas

# Nomes das cartas
rank-ace = ás
rank-ace-plural = áses
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
rank-jack = valete
rank-jack-plural = valetes
rank-queen = dama
rank-queen-plural = damas
rank-king = rei
rank-king-plural = reis

# Descrições de mãos de pôquer
poker-high-card-with = Carta alta, { $high }, com { $rest }
poker-high-card = Carta alta, { $high }
poker-pair-with = Par de { $pair }, com { $rest }
poker-pair = Par de { $pair }
poker-two-pair-with = Dois pares, { $high } e { $low }, com { $kicker }
poker-two-pair = Dois pares, { $high } e { $low }
poker-trips-with = Trinca de { $trips }, com { $rest }
poker-trips = Trinca de { $trips }
poker-straight-high = Sequência, { $high } alta
poker-flush-high-with = Flush, { $high } alto, com { $rest }
poker-full-house = Full house, { $trips } sobre { $pair }
poker-quads-with = Quadra de { $quads }, com { $kicker }
poker-quads = Quadra de { $quads }
poker-straight-flush-high = Straight flush, { $high } alto
poker-unknown-hand = Mão desconhecida
