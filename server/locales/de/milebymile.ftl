# Mile by Mile-Spielnachrichten
# Hinweis: Gemeinsame Nachrichten wie round-start, turn-start, team-mode sind in games.ftl

# Spielname
game-name-milebymile = Mile by Mile

# Spieloptionen
milebymile-set-distance = Renndistanz: { $miles } Meilen
milebymile-enter-distance = Renndistanz eingeben (300-3000)
milebymile-set-winning-score = Gewinnpunktzahl: { $score } Punkte
milebymile-enter-winning-score = Gewinnpunktzahl eingeben (1000-10000)
milebymile-toggle-perfect-crossing = Exaktes Ziel erforderlich: { $enabled }
milebymile-toggle-stacking = Stapeln von Angriffen erlauben: { $enabled }
milebymile-toggle-reshuffle = Ablagestapel neu mischen: { $enabled }
milebymile-toggle-karma = Karma-Regel: { $enabled }
milebymile-set-rig = Deck-Manipulation: { $rig }
milebymile-select-rig = Deck-Manipulationsoption auswählen

# Optionsänderungsankündigungen
milebymile-option-changed-distance = Renndistanz auf { $miles } Meilen gesetzt.
milebymile-option-changed-winning = Gewinnpunktzahl auf { $score } gesetzt.
milebymile-option-changed-crossing = Exaktes Ziel erforderlich { $enabled }.
milebymile-option-changed-stacking = Stapeln von Angriffen erlauben { $enabled }.
milebymile-option-changed-reshuffle = Ablagestapel neu mischen { $enabled }.
milebymile-option-changed-karma = Karma-Regel { $enabled }.
milebymile-option-changed-rig = Deck-Manipulation auf { $rig } gesetzt.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } Punkte, { $miles } Meilen, Probleme: { $problems }, Sicherheiten: { $safeties }

# Kartenaktionen
milebymile-no-matching-safety = Sie haben nicht die passende Sicherheitskarte!
milebymile-cant-play = Sie können { $card } nicht spielen, weil { $reason }.
milebymile-no-card-selected = Keine Karte zum Ablegen ausgewählt.
milebymile-no-valid-targets = Keine gültigen Ziele für dieses Hindernis!
milebymile-you-drew = Sie zogen: { $card }
milebymile-discards = { $player } legt eine Karte ab.
milebymile-select-target = Wählen Sie ein Ziel

# Distanzspiele
milebymile-plays-distance-individual = { $player } spielt { $distance } Meilen und ist jetzt bei { $total } Meilen.
milebymile-plays-distance-team = { $player } spielt { $distance } Meilen; ihr Team ist jetzt bei { $total } Meilen.

# Reise abgeschlossen
milebymile-journey-complete-perfect-individual = { $player } hat die Reise mit einer perfekten Überquerung abgeschlossen!
milebymile-journey-complete-perfect-team = Team { $team } hat die Reise mit einer perfekten Überquerung abgeschlossen!
milebymile-journey-complete-individual = { $player } hat die Reise abgeschlossen!
milebymile-journey-complete-team = Team { $team } hat die Reise abgeschlossen!

# Hindernisspiele
milebymile-plays-hazard-individual = { $player } spielt { $card } auf { $target }.
milebymile-plays-hazard-team = { $player } spielt { $card } auf Team { $team }.

# Abhilfe-/Sicherheitsspiele
milebymile-plays-card = { $player } spielt { $card }.
milebymile-plays-dirty-trick = { $player } spielt { $card } als Dreckigen Trick!

# Deck
milebymile-deck-reshuffled = Ablagestapel zurück ins Deck gemischt.

# Rennen
milebymile-new-race = Neues Rennen beginnt!
milebymile-race-complete = Rennen abgeschlossen! Berechne Punktzahlen...
milebymile-earned-points = { $name } erhielt { $score } Punkte in diesem Rennen: { $breakdown }.
milebymile-total-scores = Gesamtpunktzahlen:
milebymile-team-score = { $name }: { $score } Punkte

# Punkteaufschlüsselung
milebymile-from-distance = { $miles } von zurückgelegter Distanz
milebymile-from-trip = { $points } für Abschluss der Reise
milebymile-from-perfect = { $points } für eine perfekte Überquerung
milebymile-from-safe = { $points } für eine sichere Reise
milebymile-from-shutout = { $points } für eine Abfuhr
milebymile-from-safeties = { $points } von { $count } { $safeties ->
    [one] Sicherheit
   *[other] Sicherheiten
}
milebymile-from-all-safeties = { $points } von allen 4 Sicherheiten
milebymile-from-dirty-tricks = { $points } von { $count } { $tricks ->
    [one] dreckigem Trick
   *[other] dreckigen Tricks
}

# Spielende
milebymile-wins-individual = { $player } gewinnt das Spiel!
milebymile-wins-team = Team { $team } gewinnt das Spiel! ({ $members })
milebymile-final-score = Endpunktzahl: { $score } Punkte

# Karma-Nachrichten - Zusammenstoß (beide verlieren Karma)
milebymile-karma-clash-you-target = Sie und Ihr Ziel werden beide gemieden! Der Angriff wird neutralisiert.
milebymile-karma-clash-you-attacker = Sie und { $attacker } werden beide gemieden! Der Angriff wird neutralisiert.
milebymile-karma-clash-others = { $attacker } und { $target } werden beide gemieden! Der Angriff wird neutralisiert.
milebymile-karma-clash-your-team = Ihr Team und Ihr Ziel werden beide gemieden! Der Angriff wird neutralisiert.
milebymile-karma-clash-target-team = Sie und Team { $team } werden beide gemieden! Der Angriff wird neutralisiert.
milebymile-karma-clash-other-teams = Team { $attacker } und Team { $target } werden beide gemieden! Der Angriff wird neutralisiert.

# Karma-Nachrichten - Angreifer gemieden
milebymile-karma-shunned-you = Sie wurden für Ihre Aggression gemieden! Ihr Karma ist verloren.
milebymile-karma-shunned-other = { $player } wurde für seine Aggression gemieden!
milebymile-karma-shunned-your-team = Ihr Team wurde für seine Aggression gemieden! Das Karma Ihres Teams ist verloren.
milebymile-karma-shunned-other-team = Team { $team } wurde für seine Aggression gemieden!

# False Virtue
milebymile-false-virtue-you = Sie spielen False Virtue und gewinnen Ihr Karma zurück!
milebymile-false-virtue-other = { $player } spielt False Virtue und gewinnt sein Karma zurück!
milebymile-false-virtue-your-team = Ihr Team spielt False Virtue und gewinnt sein Karma zurück!
milebymile-false-virtue-other-team = Team { $team } spielt False Virtue und gewinnt sein Karma zurück!

# Probleme/Sicherheiten (für Statusanzeige)
milebymile-none = keine

# Gründe für nicht spielbare Karten
milebymile-reason-not-on-team = Sie sind nicht in einem Team
milebymile-reason-stopped = Sie sind gestoppt
milebymile-reason-has-problem = Sie haben ein Problem, das das Fahren verhindert
milebymile-reason-speed-limit = das Tempolimit ist aktiv
milebymile-reason-exceeds-distance = es würde { $miles } Meilen überschreiten
milebymile-reason-no-targets = es gibt keine gültigen Ziele
milebymile-reason-no-speed-limit = Sie stehen nicht unter Tempolimit
milebymile-reason-has-right-of-way = Right of Way lässt Sie ohne grüne Ampeln fahren
milebymile-reason-already-moving = Sie bewegen sich bereits
milebymile-reason-must-fix-first = Sie müssen zuerst das { $problem } beheben
milebymile-reason-has-gas = Ihr Auto hat Benzin
milebymile-reason-tires-fine = Ihre Reifen sind in Ordnung
milebymile-reason-no-accident = Ihr Auto hatte keinen Unfall
milebymile-reason-has-safety = Sie haben diese Sicherheit bereits
milebymile-reason-has-karma = Sie haben noch Ihr Karma
milebymile-reason-generic = es kann momentan nicht gespielt werden

# Kartennamen
milebymile-card-out-of-gas = Kein Benzin
milebymile-card-flat-tire = Platter Reifen
milebymile-card-accident = Unfall
milebymile-card-speed-limit = Tempolimit
milebymile-card-stop = Stopp
milebymile-card-gasoline = Benzin
milebymile-card-spare-tire = Ersatzreifen
milebymile-card-repairs = Reparaturen
milebymile-card-end-of-limit = Ende des Limits
milebymile-card-green-light = Grüne Ampel
milebymile-card-extra-tank = Extra Tank
milebymile-card-puncture-proof = Pannensicher
milebymile-card-driving-ace = Fahrkünstler
milebymile-card-right-of-way = Vorfahrt
milebymile-card-false-virtue = Falsche Tugend
milebymile-card-miles = { $miles } Meilen

# Gründe für deaktivierte Aktionen
milebymile-no-dirty-trick-window = Kein Dreckiger-Trick-Fenster ist aktiv.
milebymile-not-your-dirty-trick = Es ist nicht das Dreckige-Trick-Fenster Ihres Teams.
milebymile-between-races = Warten Sie, bis das nächste Rennen beginnt.

# Validierungsfehler
milebymile-error-karma-needs-three-teams = Karma-Regel benötigt mindestens 3 verschiedene Autos/Teams.

milebymile-you-play-safety-with-effect = Du spielst { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } spielt { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Du spielst { $card } als Schmutzigen Trick. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } spielt { $card } als Schmutzigen Trick. { $effect }
milebymile-safety-effect-extra-tank = Jetzt vor Liegengeblieben geschützt.
milebymile-safety-effect-puncture-proof = Jetzt vor Reifenpanne geschützt.
milebymile-safety-effect-driving-ace = Jetzt vor Unfall geschützt.
milebymile-safety-effect-right-of-way = Jetzt vor Stopp und Tempolimit geschützt.
