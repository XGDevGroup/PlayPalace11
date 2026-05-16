# Gemeinsame Spielnachrichten für PlayPalace
# Diese Nachrichten sind über mehrere Spiele hinweg gebräuchlich

# Spielnamen
game-name-ninetynine = Ninety Nine

# Runden- und Zugablauf
game-round-start = Runde { $round }.
game-round-end = Runde { $round } abgeschlossen.
game-turn-start = { $player } ist am Zug.
game-your-turn = Sie sind am Zug.
game-no-turn = Momentan ist niemand am Zug.

# Punkteanzeige
game-scores-header = Aktuelle Punktzahlen:
game-score-line = { $player }: { $score } Punkte
game-final-scores-header = Endpunktzahlen:

# Sieg/Niederlage
game-winner = { $player } gewinnt!
game-winner-score = { $player } gewinnt mit { $score } Punkten!
game-tiebreaker = Es ist ein Unentschieden! Entscheidungsrunde!
game-tiebreaker-players = Es ist ein Unentschieden zwischen { $players }! Entscheidungsrunde!
game-eliminated = { $player } wurde mit { $score } Punkten eliminiert.

# Gemeinsame Optionen
game-set-target-score = Zielpunktzahl: { $score }
game-enter-target-score = Zielpunktzahl eingeben:
game-option-changed-target = Zielpunktzahl auf { $score } gesetzt.

game-set-team-mode = Teammodus: { $mode }
game-select-team-mode = Teammodus auswählen
game-option-changed-team = Teammodus auf { $mode } gesetzt.
game-team-mode-individual = Einzelspieler
game-team-mode-x-teams-of-y = { $num_teams } Teams à { $team_size }

# Boolesche Optionswerte
option-on = an
option-off = aus

# Statusbox

# Spielende
game-leave = Spiel verlassen

# Rundenzeitmesser
round-timer-paused = { $player } hat das Spiel pausiert (drücken Sie P, um die nächste Runde zu starten).
round-timer-resumed = Rundenzeitmesser fortgesetzt.
round-timer-countdown = Nächste Runde in { $seconds }...

# Würfelspiele - Würfel behalten/neu werfen
dice-keeping = { $value } behalten.
dice-rerolling = { $value } neu würfeln.
dice-locked = Dieser Würfel ist gesperrt und kann nicht geändert werden.
dice-status-locked = locked
dice-status-kept = kept

# Austeilen (Kartenspiele)
game-deal-counter = Ausgabe { $current }/{ $total }.
game-you-deal = Sie teilen die Karten aus.
game-player-deals = { $player } teilt die Karten aus.

# Kartennamen
card-name = { $rank } { $suit }
no-cards = Keine Karten

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = schwarz
color-black-m = schwarzer
color-black-f = schwarze
color-blue = blau
color-blue-m = blauer
color-blue-f = blaue
color-brown = braun
color-brown-m = brauner
color-brown-f = braune
color-gray = grau
color-gray-m = grauer
color-gray-f = graue
color-green = grün
color-green-m = grüner
color-green-f = grüne
color-indigo = indigo
color-indigo-m = indigo
color-indigo-f = indigo
color-orange = orange
color-orange-m = orange
color-orange-f = orange
color-pink = pink
color-pink-m = pink
color-pink-f = pink
color-purple = lila
color-purple-m = lila
color-purple-f = lila
color-red = rot
color-red-m = roter
color-red-f = rote
color-violet = violett
color-violet-m = violetter
color-violet-f = violette
color-white = weiß
color-white-m = weißer
color-white-f = weiße
color-yellow = gelb
color-yellow-m = gelber
color-yellow-f = gelbe

# Farbennamen
suit-diamonds = Karo
suit-clubs = Kreuz
suit-hearts = Herz
suit-spades = Pik

# Rangbezeichnungen
rank-ace = Ass
rank-ace-plural = Asse
rank-two = 2
rank-two-plural = 2en
rank-three = 3
rank-three-plural = 3en
rank-four = 4
rank-four-plural = 4en
rank-five = 5
rank-five-plural = 5en
rank-six = 6
rank-six-plural = 6en
rank-seven = 7
rank-seven-plural = 7en
rank-eight = 8
rank-eight-plural = 8en
rank-nine = 9
rank-nine-plural = 9en
rank-ten = 10
rank-ten-plural = 10en
rank-jack = Bube
rank-jack-plural = Buben
rank-queen = Dame
rank-queen-plural = Damen
rank-king = König
rank-king-plural = Könige

# Poker-Blattbeschreibungen
poker-high-card-with = { $high } hoch, mit { $rest }
poker-high-card = { $high } hoch
poker-pair-with = Ein Paar { $pair }, mit { $rest }
poker-pair = Ein Paar { $pair }
poker-two-pair-with = Zwei Paare, { $high } und { $low }, mit { $kicker }
poker-two-pair = Zwei Paare, { $high } und { $low }
poker-trips-with = Drilling { $trips }, mit { $rest }
poker-trips = Drilling { $trips }
poker-straight-high = Straße bis { $high }
poker-flush-high-with = Flush bis { $high }, mit { $rest }
poker-full-house = Full House, { $trips } über { $pair }
poker-quads-with = Vierling { $quads }, mit { $kicker }
poker-quads = Vierling { $quads }
poker-straight-flush-high = Straight Flush bis { $high }
poker-unknown-hand = Unbekanntes Blatt

# Validierungsfehler (spielübergreifend)
game-error-invalid-team-mode = Der gewählte Teammodus ist für die aktuelle Spielerzahl nicht gültig.
