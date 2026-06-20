# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Mile by Mile

# Game options
milebymile-set-distance = Distancia de carrera: { $miles } millas
milebymile-enter-distance = Ingresa la distancia de carrera (300-3000)
milebymile-set-winning-score = Puntuación ganadora: { $score } puntos
milebymile-enter-winning-score = Ingresa la puntuación ganadora (1000-10000)
milebymile-toggle-perfect-crossing = Requerir final exacto: { $enabled }
milebymile-toggle-stacking = Permitir ataques apilados: { $enabled }
milebymile-toggle-reshuffle = Barajar pila de descarte: { $enabled }
milebymile-toggle-karma = Regla de karma: { $enabled }
milebymile-set-rig = Manipulación del mazo: { $rig }
milebymile-select-rig = Selecciona la opción de manipulación del mazo

# Option change announcements
milebymile-option-changed-distance = Distancia de carrera establecida en { $miles } millas.
milebymile-option-changed-winning = Puntuación ganadora establecida en { $score } puntos.
milebymile-option-changed-crossing = Requerir final exacto { $enabled }.
milebymile-option-changed-stacking = Permitir ataques apilados { $enabled }.
milebymile-option-changed-reshuffle = Barajar pila de descarte { $enabled }.
milebymile-option-changed-karma = Regla de karma { $enabled }.
milebymile-option-changed-rig = Manipulación del mazo establecida en { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } puntos, { $miles } millas, Problemas: { $problems }, Seguros: { $safeties }

# Card actions
milebymile-no-matching-safety = ¡No tienes la carta de seguro correspondiente!
milebymile-cant-play = No puedes jugar { $card } porque { $reason }.
milebymile-no-card-selected = No se seleccionó ninguna carta para descartar.
milebymile-no-valid-targets = ¡No hay objetivos válidos para este peligro!
milebymile-you-drew = Robaste: { $card }
milebymile-discards = { $player } descarta una carta.
milebymile-select-target = Selecciona un objetivo

# Distance plays
milebymile-plays-distance-individual = { $player } juega { $distance } millas, y ahora está en { $total } millas.
milebymile-plays-distance-team = { $player } juega { $distance } millas; su equipo ahora está en { $total } millas.

# Journey complete
milebymile-journey-complete-perfect-individual = ¡{ $player } ha completado el viaje con un cruce perfecto!
milebymile-journey-complete-perfect-team = ¡El Equipo { $team } ha completado el viaje con un cruce perfecto!
milebymile-journey-complete-individual = ¡{ $player } ha completado el viaje!
milebymile-journey-complete-team = ¡El Equipo { $team } ha completado el viaje!

# Hazard plays
milebymile-plays-hazard-individual = { $player } juega { $card } en { $target }.
milebymile-plays-hazard-team = { $player } juega { $card } en el Equipo { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } juega { $card }.
milebymile-plays-dirty-trick = ¡{ $player } juega { $card } como un Truco Sucio!

# Deck
milebymile-deck-reshuffled = Pila de descarte barajada de vuelta al mazo.

# Race
milebymile-new-race = ¡Comienza nueva carrera!
milebymile-race-complete = ¡Carrera completa! Calculando puntuaciones...
milebymile-earned-points = { $name } ganó { $score } puntos esta carrera: { $breakdown }.
milebymile-total-scores = Puntuaciones totales:
milebymile-team-score = { $name }: { $score } puntos

# Scoring breakdown
milebymile-from-distance = { $miles } de distancia recorrida
milebymile-from-trip = { $points } por completar el viaje
milebymile-from-perfect = { $points } por un cruce perfecto
milebymile-from-safe = { $points } por un viaje seguro
milebymile-from-shutout = { $points } por una blanqueada
milebymile-from-safeties = { $points } de { $count } { $safeties ->
    [one] seguro
    *[other] seguros
}
milebymile-from-all-safeties = { $points } de los 4 seguros
milebymile-from-dirty-tricks = { $points } de { $count } { $tricks ->
    [one] truco sucio
    *[other] trucos sucios
}

# Game end
milebymile-wins-individual = ¡{ $player } gana el juego!
milebymile-wins-team = ¡El Equipo { $team } gana el juego! ({ $members })
milebymile-final-score = Puntuación final: { $score } puntos

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = ¡Tú y tu objetivo están siendo rechazados! El ataque es neutralizado.
milebymile-karma-clash-you-attacker = ¡Tú y { $attacker } están siendo rechazados! El ataque es neutralizado.
milebymile-karma-clash-others = ¡{ $attacker } y { $target } están siendo rechazados! El ataque es neutralizado.
milebymile-karma-clash-your-team = ¡Tu equipo y tu objetivo están siendo rechazados! El ataque es neutralizado.
milebymile-karma-clash-target-team = ¡Tú y el Equipo { $team } están siendo rechazados! El ataque es neutralizado.
milebymile-karma-clash-other-teams = ¡El Equipo { $attacker } y el Equipo { $target } están siendo rechazados! El ataque es neutralizado.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = ¡Has sido rechazado por tu agresión! Tu karma se pierde.
milebymile-karma-shunned-other = ¡{ $player } ha sido rechazado por su agresión!
milebymile-karma-shunned-your-team = ¡Tu equipo ha sido rechazado por su agresión! El karma de tu equipo se pierde.
milebymile-karma-shunned-other-team = ¡El Equipo { $team } ha sido rechazado por su agresión!

# False Virtue
milebymile-false-virtue-you = ¡Juegas Falsa Virtud y recuperas tu karma!
milebymile-false-virtue-other = ¡{ $player } juega Falsa Virtud y recupera su karma!
milebymile-false-virtue-your-team = ¡Tu equipo juega Falsa Virtud y recupera su karma!
milebymile-false-virtue-other-team = ¡El Equipo { $team } juega Falsa Virtud y recupera su karma!

# Problems/Safeties (for status display)
milebymile-none = ninguno

# Unplayable card reasons
milebymile-reason-not-on-team = no estás en un equipo
milebymile-reason-stopped = estás detenido
milebymile-reason-has-problem = tienes un problema que impide conducir
milebymile-reason-speed-limit = el límite de velocidad está activo
milebymile-reason-exceeds-distance = excedería { $miles } millas
milebymile-reason-no-targets = no hay objetivos válidos
milebymile-reason-no-speed-limit = no estás bajo un límite de velocidad
milebymile-reason-has-right-of-way = Derecho de Paso te permite avanzar sin luces verdes
milebymile-reason-already-moving = ya estás en movimiento
milebymile-reason-must-fix-first = debes arreglar el { $problem } primero
milebymile-reason-has-gas = tu auto tiene gasolina
milebymile-reason-tires-fine = tus llantas están bien
milebymile-reason-no-accident = tu auto no ha tenido un accidente
milebymile-reason-has-safety = ya tienes ese seguro
milebymile-reason-has-karma = todavía tienes tu karma
milebymile-reason-generic = no se puede jugar ahora mismo

# Card names
milebymile-card-out-of-gas = Sin Gasolina
milebymile-card-flat-tire = Llanta Pinchada
milebymile-card-accident = Accidente
milebymile-card-speed-limit = Límite de Velocidad
milebymile-card-stop = Alto
milebymile-card-gasoline = Gasolina
milebymile-card-spare-tire = Llanta de Repuesto
milebymile-card-repairs = Reparaciones
milebymile-card-end-of-limit = Fin de Límite
milebymile-card-green-light = Luz Verde
milebymile-card-extra-tank = Tanque Extra
milebymile-card-puncture-proof = Prueba de Pinchazos
milebymile-card-driving-ace = As del Volante
milebymile-card-right-of-way = Derecho de Paso
milebymile-card-false-virtue = Falsa Virtud
milebymile-card-miles = { $miles } millas

# Disabled action reasons
milebymile-no-dirty-trick-window = No hay ventana de truco sucio activa.
milebymile-not-your-dirty-trick = No es la ventana de truco sucio de tu equipo.
milebymile-between-races = Espera a que comience la siguiente carrera.

# Validation errors
milebymile-error-karma-needs-three-teams = La regla de karma requiere al menos 3 autos/equipos distintos.

milebymile-you-play-safety-with-effect = Juegas { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } juega { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Juegas { $card } como un Truco Sucio. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } juega { $card } como un Truco Sucio. { $effect }
milebymile-safety-effect-extra-tank = Ahora protegido contra Sin Combustible.
milebymile-safety-effect-puncture-proof = Ahora protegido contra Pinchazo.
milebymile-safety-effect-driving-ace = Ahora protegido contra Accidente.
milebymile-safety-effect-right-of-way = Ahora protegido contra Alto y Límite de Velocidad.
