# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Miglio per Miglio

# Game options
milebymile-set-distance = Distanza gara: { $miles } miglia
milebymile-enter-distance = Inserisci distanza gara (300-3000)
milebymile-set-winning-score = Punteggio vittoria: { $score } punti
milebymile-enter-winning-score = Inserisci punteggio vittoria (1000-10000)
milebymile-toggle-perfect-crossing = Richiedi arrivo esatto: { $enabled }
milebymile-toggle-stacking = Permetti accumulazione attacchi: { $enabled }
milebymile-toggle-reshuffle = Rimescola mazzo scarti: { $enabled }
milebymile-toggle-karma = Regola karma: { $enabled }
milebymile-set-rig = Truccatura mazzo: { $rig }
milebymile-select-rig = Seleziona opzione truccatura mazzo

# Option change announcements
milebymile-option-changed-distance = Distanza gara impostata a { $miles } miglia.
milebymile-option-changed-winning = Punteggio vittoria impostato a { $score } punti.
milebymile-option-changed-crossing = Richiedi arrivo esatto { $enabled }.
milebymile-option-changed-stacking = Permetti accumulazione attacchi { $enabled }.
milebymile-option-changed-reshuffle = Rimescola mazzo scarti { $enabled }.
milebymile-option-changed-karma = Regola karma { $enabled }.
milebymile-option-changed-rig = Truccatura mazzo impostata su { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } punti, { $miles } miglia, Problemi: { $problems }, Sicurezze: { $safeties }

# Card actions
milebymile-no-matching-safety = Non hai la carta sicurezza corrispondente!
milebymile-cant-play = Non puoi giocare { $card } perché { $reason }.
milebymile-no-card-selected = Nessuna carta selezionata da scartare.
milebymile-no-valid-targets = Nessun bersaglio valido per questo pericolo!
milebymile-you-drew = Hai pescato: { $card }
milebymile-discards = { $player } scarta una carta.
milebymile-select-target = Seleziona un bersaglio

# Distance plays
milebymile-plays-distance-individual = { $player } gioca { $distance } miglia ed è ora a { $total } miglia.
milebymile-plays-distance-team = { $player } gioca { $distance } miglia; la loro squadra è ora a { $total } miglia.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } ha completato il viaggio con un arrivo perfetto!
milebymile-journey-complete-perfect-team = Squadra { $team } ha completato il viaggio con un arrivo perfetto!
milebymile-journey-complete-individual = { $player } ha completato il viaggio!
milebymile-journey-complete-team = Squadra { $team } ha completato il viaggio!

# Hazard plays
milebymile-plays-hazard-individual = { $player } gioca { $card } su { $target }.
milebymile-plays-hazard-team = { $player } gioca { $card } sulla Squadra { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } gioca { $card }.
milebymile-plays-dirty-trick = { $player } gioca { $card } come un Trucco Sporco!

# Deck
milebymile-deck-reshuffled = Mazzo scarti rimescolato nel mazzo.

# Race
milebymile-new-race = Inizia nuova gara!
milebymile-race-complete = Gara completata! Calcolo punteggi...
milebymile-earned-points = { $name } ha guadagnato { $score } punti in questa gara: { $breakdown }.
milebymile-total-scores = Punteggi totali:
milebymile-team-score = { $name }: { $score } punti

# Scoring breakdown
milebymile-from-distance = { $miles } dalla distanza percorsa
milebymile-from-trip = { $points } dal completamento viaggio
milebymile-from-perfect = { $points } da un arrivo perfetto
milebymile-from-safe = { $points } da un viaggio sicuro
milebymile-from-shutout = { $points } da uno shut out
milebymile-from-safeties = { $points } da { $count } { $safeties ->
    [one] sicurezza
    *[other] sicurezze
}
milebymile-from-all-safeties = { $points } da tutte le 4 sicurezze
milebymile-from-dirty-tricks = { $points } da { $count } { $tricks ->
    [one] trucco sporco
    *[other] trucchi sporchi
}

# Game end
milebymile-wins-individual = { $player } vince la partita!
milebymile-wins-team = Squadra { $team } vince la partita! ({ $members })
milebymile-final-score = Punteggio finale: { $score } punti

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Tu e il tuo bersaglio siete entrambi evitati! L'attacco è neutralizzato.
milebymile-karma-clash-you-attacker = Tu e { $attacker } siete entrambi evitati! L'attacco è neutralizzato.
milebymile-karma-clash-others = { $attacker } e { $target } sono entrambi evitati! L'attacco è neutralizzato.
milebymile-karma-clash-your-team = La tua squadra e il tuo bersaglio sono entrambi evitati! L'attacco è neutralizzato.
milebymile-karma-clash-target-team = Tu e Squadra { $team } siete entrambi evitati! L'attacco è neutralizzato.
milebymile-karma-clash-other-teams = Squadra { $attacker } e Squadra { $target } sono entrambe evitate! L'attacco è neutralizzato.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Sei stato evitato per la tua aggressione! Il tuo karma è perso.
milebymile-karma-shunned-other = { $player } è stato evitato per la sua aggressione!
milebymile-karma-shunned-your-team = La tua squadra è stata evitata per la sua aggressione! Il karma della tua squadra è perso.
milebymile-karma-shunned-other-team = Squadra { $team } è stata evitata per la sua aggressione!

# False Virtue
milebymile-false-virtue-you = Giochi Falsa Virtù e recuperi il tuo karma!
milebymile-false-virtue-other = { $player } gioca Falsa Virtù e recupera il suo karma!
milebymile-false-virtue-your-team = La tua squadra gioca Falsa Virtù e recupera il suo karma!
milebymile-false-virtue-other-team = Squadra { $team } gioca Falsa Virtù e recupera il suo karma!

# Problems/Safeties (for status display)
milebymile-none = nessuno

# Unplayable card reasons
milebymile-reason-not-on-team = non sei in una squadra
milebymile-reason-stopped = sei fermo
milebymile-reason-has-problem = hai un problema che impedisce di guidare
milebymile-reason-speed-limit = il limite di velocità è attivo
milebymile-reason-exceeds-distance = supererebbe { $miles } miglia
milebymile-reason-no-targets = non ci sono bersagli validi
milebymile-reason-no-speed-limit = non sei sotto un limite di velocità
milebymile-reason-has-right-of-way = Diritto di Precedenza ti permette di andare senza semafori verdi
milebymile-reason-already-moving = ti stai già muovendo
milebymile-reason-must-fix-first = devi prima riparare { $problem }
milebymile-reason-has-gas = la tua auto ha benzina
milebymile-reason-tires-fine = le tue gomme sono a posto
milebymile-reason-no-accident = la tua auto non ha avuto incidenti
milebymile-reason-has-safety = hai già quella sicurezza
milebymile-reason-has-karma = hai ancora il tuo karma
milebymile-reason-generic = non può essere giocata adesso

# Card names
milebymile-card-out-of-gas = Senza Benzina
milebymile-card-flat-tire = Gomma a Terra
milebymile-card-accident = Incidente
milebymile-card-speed-limit = Limite di Velocità
milebymile-card-stop = Stop
milebymile-card-gasoline = Benzina
milebymile-card-spare-tire = Ruota di Scorta
milebymile-card-repairs = Riparazioni
milebymile-card-end-of-limit = Fine del Limite
milebymile-card-green-light = Luce Verde
milebymile-card-extra-tank = Tanica Extra
milebymile-card-puncture-proof = Antigomma
milebymile-card-driving-ace = Asso della Guida
milebymile-card-right-of-way = Diritto di Precedenza
milebymile-card-false-virtue = Falsa Virtù
milebymile-card-miles = { $miles } miglia

# Disabled action reasons
milebymile-no-dirty-trick-window = Nessuna finestra trucco sporco attiva.
milebymile-not-your-dirty-trick = Non è la finestra trucco sporco della tua squadra.
milebymile-between-races = Attendi l'inizio della prossima gara.

# Validation errors
milebymile-error-karma-needs-three-teams = La regola karma richiede almeno 3 auto/squadre distinte.

milebymile-you-play-safety-with-effect = Giochi { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } gioca { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Giochi { $card } come un Trucco Sporco. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } gioca { $card } come un Trucco Sporco. { $effect }
milebymile-safety-effect-extra-tank = Ora protetto da Senza Benzina.
milebymile-safety-effect-puncture-proof = Ora protetto da Foratura.
milebymile-safety-effect-driving-ace = Ora protetto da Incidente.
milebymile-safety-effect-right-of-way = Ora protetto da Stop e Limite di Velocità.
