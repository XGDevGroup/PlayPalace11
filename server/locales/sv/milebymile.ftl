# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Mil för Mil

# Game options
milebymile-set-distance = Racedistans: { $miles } miles
milebymile-enter-distance = Ange racedistans (300-3000)
milebymile-set-winning-score = Vinstpoäng: { $score } poäng
milebymile-enter-winning-score = Ange vinstpoäng (1000-10000)
milebymile-toggle-perfect-crossing = Kräv exakt målgång: { $enabled }
milebymile-toggle-stacking = Tillåt staplade attacker: { $enabled }
milebymile-toggle-reshuffle = Blanda om slänga-högen: { $enabled }
milebymile-toggle-karma = Karmaregel: { $enabled }
milebymile-set-rig = Kortleksriggning: { $rig }
milebymile-select-rig = Välj kortleksriggningsalternativ

# Option change announcements
milebymile-option-changed-distance = Racedistans inställd på { $miles } miles.
milebymile-option-changed-winning = Vinstpoäng inställd på { $score } poäng.
milebymile-option-changed-crossing = Kräv exakt målgång { $enabled }.
milebymile-option-changed-stacking = Tillåt staplade attacker { $enabled }.
milebymile-option-changed-reshuffle = Blanda om slänga-högen { $enabled }.
milebymile-option-changed-karma = Karmaregel { $enabled }.
milebymile-option-changed-rig = Kortleksriggning inställd på { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } poäng, { $miles } miles, Problem: { $problems }, Säkerheter: { $safeties }

# Card actions
milebymile-no-matching-safety = Du har inte det matchande säkerhetskortet!
milebymile-cant-play = Du kan inte spela { $card } eftersom { $reason }.
milebymile-no-card-selected = Inget kort valt att slänga.
milebymile-no-valid-targets = Inga giltiga mål för denna fara!
milebymile-you-drew = Du drog: { $card }
milebymile-discards = { $player } slänger ett kort.
milebymile-select-target = Välj ett mål

# Distance plays
milebymile-plays-distance-individual = { $player } spelar { $distance } miles och är nu på { $total } miles.
milebymile-plays-distance-team = { $player } spelar { $distance } miles; deras lag är nu på { $total } miles.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } har slutfört resan med en perfekt korsning!
milebymile-journey-complete-perfect-team = Lag { $team } har slutfört resan med en perfekt korsning!
milebymile-journey-complete-individual = { $player } har slutfört resan!
milebymile-journey-complete-team = Lag { $team } har slutfört resan!

# Hazard plays
milebymile-plays-hazard-individual = { $player } spelar { $card } på { $target }.
milebymile-plays-hazard-team = { $player } spelar { $card } på Lag { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } spelar { $card }.
milebymile-plays-dirty-trick = { $player } spelar { $card } som ett Smutsigt Trick!

# Deck
milebymile-deck-reshuffled = Slänga-högen blandad tillbaka i kortleken.

# Race
milebymile-new-race = Nytt race börjar!
milebymile-race-complete = Race slutfört! Beräknar poäng...
milebymile-earned-points = { $name } fick { $score } poäng i detta race: { $breakdown }.
milebymile-total-scores = Totala poäng:
milebymile-team-score = { $name }: { $score } poäng

# Scoring breakdown
milebymile-from-distance = { $miles } från tillryggalagd distans
milebymile-from-trip = { $points } från att slutföra resan
milebymile-from-perfect = { $points } från en perfekt korsning
milebymile-from-safe = { $points } från en säker resa
milebymile-from-shutout = { $points } från en shut out
milebymile-from-safeties = { $points } från { $count } { $safeties ->
    [one] säkerhet
    *[other] säkerheter
}
milebymile-from-all-safeties = { $points } från alla 4 säkerheter
milebymile-from-dirty-tricks = { $points } från { $count } { $tricks ->
    [one] smutsigt trick
    *[other] smutsiga trick
}

# Game end
milebymile-wins-individual = { $player } vinner spelet!
milebymile-wins-team = Lag { $team } vinner spelet! ({ $members })
milebymile-final-score = Slutpoäng: { $score } poäng

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Du och ditt mål är båda utfrysta! Attacken neutraliseras.
milebymile-karma-clash-you-attacker = Du och { $attacker } är båda utfrysta! Attacken neutraliseras.
milebymile-karma-clash-others = { $attacker } och { $target } är båda utfrysta! Attacken neutraliseras.
milebymile-karma-clash-your-team = Ditt lag och ditt mål är båda utfrysta! Attacken neutraliseras.
milebymile-karma-clash-target-team = Du och Lag { $team } är båda utfrysta! Attacken neutraliseras.
milebymile-karma-clash-other-teams = Lag { $attacker } och Lag { $target } är båda utfrysta! Attacken neutraliseras.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Du har blivit utfryst för din aggression! Din karma är förlorad.
milebymile-karma-shunned-other = { $player } har blivit utfryst för sin aggression!
milebymile-karma-shunned-your-team = Ditt lag har blivit utfryst för sin aggression! Ditt lags karma är förlorad.
milebymile-karma-shunned-other-team = Lag { $team } har blivit utfryst för sin aggression!

# False Virtue
milebymile-false-virtue-you = Du spelar Falsk Dygd och återfår din karma!
milebymile-false-virtue-other = { $player } spelar Falsk Dygd och återfår sin karma!
milebymile-false-virtue-your-team = Ditt lag spelar Falsk Dygd och återfår sin karma!
milebymile-false-virtue-other-team = Lag { $team } spelar Falsk Dygd och återfår sin karma!

# Problems/Safeties (for status display)
milebymile-none = inga

# Unplayable card reasons
milebymile-reason-not-on-team = du är inte i ett lag
milebymile-reason-stopped = du är stoppad
milebymile-reason-has-problem = du har ett problem som hindrar körning
milebymile-reason-speed-limit = hastighetsgränsen är aktiv
milebymile-reason-exceeds-distance = det skulle överstiga { $miles } miles
milebymile-reason-no-targets = det finns inga giltiga mål
milebymile-reason-no-speed-limit = du är inte under en hastighetsgräns
milebymile-reason-has-right-of-way = Företräde låter dig köra utan grönt ljus
milebymile-reason-already-moving = du rör dig redan
milebymile-reason-must-fix-first = du måste först reparera { $problem }
milebymile-reason-has-gas = din bil har bensin
milebymile-reason-tires-fine = dina däck är okej
milebymile-reason-no-accident = din bil har inte varit med om en olycka
milebymile-reason-has-safety = du har redan den säkerheten
milebymile-reason-has-karma = du har fortfarande din karma
milebymile-reason-generic = det kan inte spelas just nu

# Card names
milebymile-card-out-of-gas = Slut på Bensin
milebymile-card-flat-tire = Punktering
milebymile-card-accident = Olycka
milebymile-card-speed-limit = Hastighetsgräns
milebymile-card-stop = Stopp
milebymile-card-gasoline = Bensin
milebymile-card-spare-tire = Reservdäck
milebymile-card-repairs = Reparationer
milebymile-card-end-of-limit = Slut på Gräns
milebymile-card-green-light = Grönt Ljus
milebymile-card-extra-tank = Extra Tank
milebymile-card-puncture-proof = Punkteringssäker
milebymile-card-driving-ace = Körässä
milebymile-card-right-of-way = Företräde
milebymile-card-false-virtue = Falsk Dygd
milebymile-card-miles = { $miles } miles

# Disabled action reasons
milebymile-no-dirty-trick-window = Inget smutsigt trick-fönster aktivt.
milebymile-not-your-dirty-trick = Det är inte ditt lags smutsiga trick-fönster.
milebymile-between-races = Vänta på att nästa race ska börja.

# Validation errors
milebymile-error-karma-needs-three-teams = Karmaregeln kräver minst 3 distinkta bilar/lag.

milebymile-you-play-safety-with-effect = Du spelar { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } spelar { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Du spelar { $card } som ett Smutsigt Trick. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } spelar { $card } som ett Smutsigt Trick. { $effect }
milebymile-safety-effect-extra-tank = Nu skyddad mot Slut på bensin.
milebymile-safety-effect-puncture-proof = Nu skyddad mot Punktering.
milebymile-safety-effect-driving-ace = Nu skyddad mot Olycka.
milebymile-safety-effect-right-of-way = Nu skyddad mot Stopp och Hastighetsgräns.
