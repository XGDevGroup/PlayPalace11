# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Mile by Mile

# Game options
milebymile-set-distance = Race afstand: { $miles } mijl
milebymile-enter-distance = Voer race afstand in (300-3000)
milebymile-set-winning-score = Winnende score: { $score } punten
milebymile-enter-winning-score = Voer winnende score in (1000-10000)
milebymile-toggle-perfect-crossing = Vereist exacte finish: { $enabled }
milebymile-toggle-stacking = Sta stapelen van aanvallen toe: { $enabled }
milebymile-toggle-reshuffle = Schud aflegstapel opnieuw: { $enabled }
milebymile-toggle-karma = Karmaregel: { $enabled }
milebymile-set-rig = Deck manipulatie: { $rig }
milebymile-select-rig = Selecteer deck manipulatie optie

# Option change announcements
milebymile-option-changed-distance = Race afstand ingesteld op { $miles } mijl.
milebymile-option-changed-winning = Winnende score ingesteld op { $score } punten.
milebymile-option-changed-crossing = Vereist exacte finish { $enabled }.
milebymile-option-changed-stacking = Sta stapelen van aanvallen toe { $enabled }.
milebymile-option-changed-reshuffle = Schud aflegstapel opnieuw { $enabled }.
milebymile-option-changed-karma = Karmaregel { $enabled }.
milebymile-option-changed-rig = Deck manipulatie ingesteld op { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } punten, { $miles } mijl, Problemen: { $problems }, Veiligheidskaarten: { $safeties }

# Card actions
milebymile-no-matching-safety = Je hebt de bijpassende veiligheidskaart niet!
milebymile-cant-play = Je kunt { $card } niet spelen omdat { $reason }.
milebymile-no-card-selected = Geen kaart geselecteerd om weg te gooien.
milebymile-no-valid-targets = Geen geldige doelen voor dit gevaar!
milebymile-you-drew = Je trok: { $card }
milebymile-discards = { $player } gooit een kaart weg.
milebymile-select-target = Selecteer een doel

# Distance plays
milebymile-plays-distance-individual = { $player } speelt { $distance } mijl, en is nu op { $total } mijl.
milebymile-plays-distance-team = { $player } speelt { $distance } mijl; hun team is nu op { $total } mijl.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } heeft de reis voltooid met een perfecte oversteek!
milebymile-journey-complete-perfect-team = Team { $team } heeft de reis voltooid met een perfecte oversteek!
milebymile-journey-complete-individual = { $player } heeft de reis voltooid!
milebymile-journey-complete-team = Team { $team } heeft de reis voltooid!

# Hazard plays
milebymile-plays-hazard-individual = { $player } speelt { $card } op { $target }.
milebymile-plays-hazard-team = { $player } speelt { $card } op Team { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } speelt { $card }.
milebymile-plays-dirty-trick = { $player } speelt { $card } als een Vieze Truc!

# Deck
milebymile-deck-reshuffled = Aflegstapel geschud terug in deck.

# Race
milebymile-new-race = Nieuwe race begint!
milebymile-race-complete = Race voltooid! Scores berekenen...
milebymile-earned-points = { $name } verdiende { $score } punten deze race: { $breakdown }.
milebymile-total-scores = Totale scores:
milebymile-team-score = { $name }: { $score } punten

# Scoring breakdown
milebymile-from-distance = { $miles } van afgelegde afstand
milebymile-from-trip = { $points } van het voltooien van de reis
milebymile-from-perfect = { $points } van een perfecte oversteek
milebymile-from-safe = { $points } van een veilige reis
milebymile-from-shutout = { $points } van een shut out
milebymile-from-safeties = { $points } van { $count } { $safeties ->
    [one] veiligheidskaart
    *[other] veiligheidskaarten
}
milebymile-from-all-safeties = { $points } van alle 4 veiligheidskaarten
milebymile-from-dirty-tricks = { $points } van { $count } { $tricks ->
    [one] vieze truc
    *[other] vieze trucs
}

# Game end
milebymile-wins-individual = { $player } wint het spel!
milebymile-wins-team = Team { $team } wint het spel! ({ $members })
milebymile-final-score = Eindscore: { $score } punten

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Jij en je doel worden beide gemeden! De aanval wordt geneutraliseerd.
milebymile-karma-clash-you-attacker = Jij en { $attacker } worden beide gemeden! De aanval wordt geneutraliseerd.
milebymile-karma-clash-others = { $attacker } en { $target } worden beide gemeden! De aanval wordt geneutraliseerd.
milebymile-karma-clash-your-team = Jouw team en je doel worden beide gemeden! De aanval wordt geneutraliseerd.
milebymile-karma-clash-target-team = Jij en Team { $team } worden beide gemeden! De aanval wordt geneutraliseerd.
milebymile-karma-clash-other-teams = Team { $attacker } en Team { $target } worden beide gemeden! De aanval wordt geneutraliseerd.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Je wordt gemeden voor je agressie! Je karma is verloren.
milebymile-karma-shunned-other = { $player } wordt gemeden voor hun agressie!
milebymile-karma-shunned-your-team = Jouw team wordt gemeden voor zijn agressie! Je team's karma is verloren.
milebymile-karma-shunned-other-team = Team { $team } wordt gemeden voor zijn agressie!

# False Virtue
milebymile-false-virtue-you = Je speelt False Virtue en herwinnt je karma!
milebymile-false-virtue-other = { $player } speelt False Virtue en herwinnt hun karma!
milebymile-false-virtue-your-team = Jouw team speelt False Virtue en herwinnt zijn karma!
milebymile-false-virtue-other-team = Team { $team } speelt False Virtue en herwinnt zijn karma!

# Problems/Safeties (for status display)
milebymile-none = geen

# Unplayable card reasons
milebymile-reason-not-on-team = je zit niet in een team
milebymile-reason-stopped = je bent gestopt
milebymile-reason-has-problem = je hebt een probleem dat rijden verhindert
milebymile-reason-speed-limit = de snelheidslimiet is actief
milebymile-reason-exceeds-distance = het zou { $miles } mijl overschrijden
milebymile-reason-no-targets = er zijn geen geldige doelen
milebymile-reason-no-speed-limit = je hebt geen snelheidslimiet
milebymile-reason-has-right-of-way = Right of Way laat je gaan zonder groene lichten
milebymile-reason-already-moving = je bent al in beweging
milebymile-reason-must-fix-first = je moet eerst { $problem } repareren
milebymile-reason-has-gas = je auto heeft benzine
milebymile-reason-tires-fine = je banden zijn in orde
milebymile-reason-no-accident = je auto heeft geen ongeluk gehad
milebymile-reason-has-safety = je hebt die veiligheidskaart al
milebymile-reason-has-karma = je hebt je karma nog
milebymile-reason-generic = het kan nu niet gespeeld worden

# Card names
milebymile-card-out-of-gas = Zonder Benzine
milebymile-card-flat-tire = Lekke Band
milebymile-card-accident = Ongeluk
milebymile-card-speed-limit = Snelheidslimiet
milebymile-card-stop = Stop
milebymile-card-gasoline = Benzine
milebymile-card-spare-tire = Reserveband
milebymile-card-repairs = Reparaties
milebymile-card-end-of-limit = Einde van Limiet
milebymile-card-green-light = Groen Licht
milebymile-card-extra-tank = Extra Tank
milebymile-card-puncture-proof = Lekbestendig
milebymile-card-driving-ace = Rij-aas
milebymile-card-right-of-way = Voorrang
milebymile-card-false-virtue = False Virtue
milebymile-card-miles = { $miles } mijl

# Disabled action reasons
milebymile-no-dirty-trick-window = Geen vieze truc venster is actief.
milebymile-not-your-dirty-trick = Het is niet jouw team's vieze truc venster.
milebymile-between-races = Wacht op de volgende race om te starten.

# Validation errors
milebymile-error-karma-needs-three-teams = Karmaregel vereist minstens 3 verschillende auto's/teams.

milebymile-you-play-safety-with-effect = Je speelt { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } speelt { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Je speelt { $card } als een Vuil Streekje. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } speelt { $card } als een Vuil Streekje. { $effect }
milebymile-safety-effect-extra-tank = Nu beschermd tegen Zonder Benzine.
milebymile-safety-effect-puncture-proof = Nu beschermd tegen Lekke Band.
milebymile-safety-effect-driving-ace = Nu beschermd tegen Ongeluk.
milebymile-safety-effect-right-of-way = Nu beschermd tegen Stop en Snelheidslimiet.
