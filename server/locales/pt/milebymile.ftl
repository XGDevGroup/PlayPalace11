# Mensagens do jogo Mile by Mile
# Nota: Mensagens comuns como round-start, turn-start, team-mode estão em games.ftl

# Nome do jogo
game-name-milebymile = Mile by Mile

# Opções do jogo
milebymile-set-distance = Distância da corrida: { $miles } milhas
milebymile-enter-distance = Digite a distância da corrida (300-3000)
milebymile-set-winning-score = Pontuação para vencer: { $score } pontos
milebymile-enter-winning-score = Digite a pontuação para vencer (1000-10000)
milebymile-toggle-perfect-crossing = Exigir chegada exata: { $enabled }
milebymile-toggle-stacking = Permitir ataques acumulados: { $enabled }
milebymile-toggle-reshuffle = Embaralhar pilha de descarte: { $enabled }
milebymile-toggle-karma = Regra do karma: { $enabled }
milebymile-set-rig = Ajuste do baralho: { $rig }
milebymile-select-rig = Selecione opção de ajuste do baralho

# Anúncios de mudança de opções
milebymile-option-changed-distance = Distância da corrida definida para { $miles } milhas.
milebymile-option-changed-winning = Pontuação para vencer definida para { $score } pontos.
milebymile-option-changed-crossing = Exigir chegada exata { $enabled }.
milebymile-option-changed-stacking = Permitir ataques acumulados { $enabled }.
milebymile-option-changed-reshuffle = Embaralhar pilha de descarte { $enabled }.
milebymile-option-changed-karma = Regra do karma { $enabled }.
milebymile-option-changed-rig = Ajuste do baralho definido para { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $miles } milhas, Problemas: { $problems }, Seguranças: { $safeties }

# Ações de cartas
milebymile-no-matching-safety = Você não tem a carta de segurança correspondente!
milebymile-cant-play = Você não pode jogar { $card } porque { $reason }.
milebymile-no-card-selected = Nenhuma carta selecionada para descartar.
milebymile-no-valid-targets = Não há alvos válidos para este perigo!
milebymile-you-drew = Você comprou: { $card }
milebymile-discards = { $player } descarta uma carta.
milebymile-select-target = Selecione um alvo

# Jogadas de distância
milebymile-plays-distance-individual = { $player } joga { $distance } milhas, agora está com { $total } milhas.
milebymile-plays-distance-team = { $player } joga { $distance } milhas; sua equipe agora tem { $total } milhas.

# Viagem completa
milebymile-journey-complete-perfect-individual = { $player } completou a viagem com uma chegada perfeita!
milebymile-journey-complete-perfect-team = Equipe { $team } completou a viagem com uma chegada perfeita!
milebymile-journey-complete-individual = { $player } completou a viagem!
milebymile-journey-complete-team = Equipe { $team } completou a viagem!

# Jogadas de perigo
milebymile-plays-hazard-individual = { $player } joga { $card } em { $target }.
milebymile-plays-hazard-team = { $player } joga { $card } na Equipe { $team }.

# Jogadas de remédio/segurança
milebymile-plays-card = { $player } joga { $card }.
milebymile-plays-dirty-trick = { $player } joga { $card } como Golpe Sujo!

# Baralho
milebymile-deck-reshuffled = Pilha de descarte embaralhada de volta ao baralho.

# Corrida
milebymile-new-race = Nova corrida começa!
milebymile-race-complete = Corrida completa! Calculando pontuações...
milebymile-earned-points = { $name } ganhou { $score } pontos nesta corrida: { $breakdown }.
milebymile-total-scores = Pontuações totais:
milebymile-team-score = { $name }: { $score } pontos

# Detalhamento de pontuação
milebymile-from-distance = { $miles } da distância percorrida
milebymile-from-trip = { $points } por completar a viagem
milebymile-from-perfect = { $points } pela chegada perfeita
milebymile-from-safe = { $points } pela viagem segura
milebymile-from-shutout = { $points } por zerar adversários
milebymile-from-safeties = { $points } por { $count } carta(s) de segurança
milebymile-from-all-safeties = { $points } por todas as 4 cartas de segurança
milebymile-from-dirty-tricks = { $points } por { $count } golpe(s) sujo(s)

# Fim do jogo
milebymile-wins-individual = { $player } vence o jogo!
milebymile-wins-team = Equipe { $team } vence o jogo! ({ $members })
milebymile-final-score = Pontuação final: { $score } pontos

# Mensagens de karma - conflito (ambos perdem karma)
milebymile-karma-clash-you-target = Você e seu alvo foram ambos rejeitados! O ataque é neutralizado.
milebymile-karma-clash-you-attacker = Você e { $attacker } foram ambos rejeitados! O ataque é neutralizado.
milebymile-karma-clash-others = { $attacker } e { $target } foram ambos rejeitados! O ataque é neutralizado.
milebymile-karma-clash-your-team = Sua equipe e seu alvo foram ambos rejeitados! O ataque é neutralizado.
milebymile-karma-clash-target-team = Você e a Equipe { $team } foram ambos rejeitados! O ataque é neutralizado.
milebymile-karma-clash-other-teams = Equipe { $attacker } e Equipe { $target } foram ambos rejeitados! O ataque é neutralizado.

# Mensagens de karma - atacante rejeitado
milebymile-karma-shunned-you = Você foi rejeitado por sua agressão! Seu karma foi perdido.
milebymile-karma-shunned-other = { $player } foi rejeitado por sua agressão!
milebymile-karma-shunned-your-team = Sua equipe foi rejeitada por sua agressão! O karma da equipe foi perdido.
milebymile-karma-shunned-other-team = Equipe { $team } foi rejeitada por sua agressão!

# Falsa Virtude
milebymile-false-virtue-you = Você joga Falsa Virtude e recupera seu karma!
milebymile-false-virtue-other = { $player } joga Falsa Virtude e recupera seu karma!
milebymile-false-virtue-your-team = Sua equipe joga Falsa Virtude e recupera seu karma!
milebymile-false-virtue-other-team = Equipe { $team } joga Falsa Virtude e recupera seu karma!

# Problemas/Seguranças (para exibição de status)
milebymile-none = nenhum

# Razões para não poder jogar
milebymile-reason-not-on-team = você não está em uma equipe
milebymile-reason-stopped = você está parado
milebymile-reason-has-problem = você tem um problema que impede de dirigir
milebymile-reason-speed-limit = o limite de velocidade está ativo
milebymile-reason-exceeds-distance = excederia { $miles } milhas
milebymile-reason-no-targets = não há alvos válidos
milebymile-reason-no-speed-limit = você não está sob limite de velocidade
milebymile-reason-has-right-of-way = Direito de Passagem permite ir sem semáforo verde
milebymile-reason-already-moving = você já está em movimento
milebymile-reason-must-fix-first = você deve consertar o { $problem } primeiro
milebymile-reason-has-gas = seu carro tem combustível
milebymile-reason-tires-fine = seus pneus estão bem
milebymile-reason-no-accident = seu carro não sofreu um acidente
milebymile-reason-has-safety = você já tem essa carta de segurança
milebymile-reason-has-karma = você ainda tem seu karma
milebymile-reason-generic = não pode ser jogada agora

# Nomes das cartas
milebymile-card-out-of-gas = Sem Combustível
milebymile-card-flat-tire = Pneu Furado
milebymile-card-accident = Acidente
milebymile-card-speed-limit = Limite de Velocidade
milebymile-card-stop = Pare
milebymile-card-gasoline = Gasolina
milebymile-card-spare-tire = Pneu Reserva
milebymile-card-repairs = Reparos
milebymile-card-end-of-limit = Fim do Limite
milebymile-card-green-light = Sinal Verde
milebymile-card-extra-tank = Tanque Extra
milebymile-card-puncture-proof = À Prova de Furos
milebymile-card-driving-ace = Ás do Volante
milebymile-card-right-of-way = Direito de Passagem
milebymile-card-false-virtue = Falsa Virtude
milebymile-card-miles = { $miles } milhas

milebymile-you-play-safety-with-effect = Você joga { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } joga { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Você joga { $card } como um Truque Sujo. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } joga { $card } como um Truque Sujo. { $effect }
milebymile-safety-effect-extra-tank = Agora protegido contra Sem Combustível.
milebymile-safety-effect-puncture-proof = Agora protegido contra Pneu Furado.
milebymile-safety-effect-driving-ace = Agora protegido contra Acidente.
milebymile-safety-effect-right-of-way = Agora protegido contra Pare e Limite de Velocidade.
