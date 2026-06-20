# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Milă cu Milă

# Game options
milebymile-set-distance = Distanța cursei: { $miles } mile
milebymile-enter-distance = Introduceți distanța cursei (300-3000)
milebymile-set-winning-score = Scor de victorie: { $score } puncte
milebymile-enter-winning-score = Introduceți scorul de victorie (1000-10000)
milebymile-toggle-perfect-crossing = Necesită sosire exactă: { $enabled }
milebymile-toggle-stacking = Permite acumularea atacurilor: { $enabled }
milebymile-toggle-reshuffle = Amestecă pachetul de descărcare: { $enabled }
milebymile-toggle-karma = Regula karmei: { $enabled }
milebymile-set-rig = Trucarea pachetului: { $rig }
milebymile-select-rig = Selectați opțiunea de trucare a pachetului

# Option change announcements
milebymile-option-changed-distance = Distanța cursei setată la { $miles } mile.
milebymile-option-changed-winning = Scorul de victorie setat la { $score } puncte.
milebymile-option-changed-crossing = Necesită sosire exactă { $enabled }.
milebymile-option-changed-stacking = Permite acumularea atacurilor { $enabled }.
milebymile-option-changed-reshuffle = Amestecă pachetul de descărcare { $enabled }.
milebymile-option-changed-karma = Regula karmei { $enabled }.
milebymile-option-changed-rig = Trucarea pachetului setată la { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } puncte, { $miles } mile, Probleme: { $problems }, Siguranțe: { $safeties }

# Card actions
milebymile-no-matching-safety = Nu aveți cartea de siguranță corespunzătoare!
milebymile-cant-play = Nu puteți juca { $card } pentru că { $reason }.
milebymile-no-card-selected = Nicio carte selectată pentru a fi aruncată.
milebymile-no-valid-targets = Nicio țintă validă pentru acest pericol!
milebymile-you-drew = Ați tras: { $card }
milebymile-discards = { $player } aruncă o carte.
milebymile-select-target = Selectați o țintă

# Distance plays
milebymile-plays-distance-individual = { $player } joacă { $distance } mile și este acum la { $total } mile.
milebymile-plays-distance-team = { $player } joacă { $distance } mile; echipa lor este acum la { $total } mile.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } a completat călătoria cu o trecere perfectă!
milebymile-journey-complete-perfect-team = Echipa { $team } a completat călătoria cu o trecere perfectă!
milebymile-journey-complete-individual = { $player } a completat călătoria!
milebymile-journey-complete-team = Echipa { $team } a completat călătoria!

# Hazard plays
milebymile-plays-hazard-individual = { $player } joacă { $card } pe { $target }.
milebymile-plays-hazard-team = { $player } joacă { $card } pe Echipa { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } joacă { $card }.
milebymile-plays-dirty-trick = { $player } joacă { $card } ca un Truc Murdar!

# Deck
milebymile-deck-reshuffled = Pachetul de descărcare amestecat înapoi în pachet.

# Race
milebymile-new-race = Începe o cursă nouă!
milebymile-race-complete = Cursă completă! Calcularea scorurilor...
milebymile-earned-points = { $name } a câștigat { $score } puncte în această cursă: { $breakdown }.
milebymile-total-scores = Scoruri totale:
milebymile-team-score = { $name }: { $score } puncte

# Scoring breakdown
milebymile-from-distance = { $miles } din distanța parcursă
milebymile-from-trip = { $points } pentru completarea călătoriei
milebymile-from-perfect = { $points } pentru o trecere perfectă
milebymile-from-safe = { $points } pentru o călătorie sigură
milebymile-from-shutout = { $points } pentru un shut out
milebymile-from-safeties = { $points } din { $count } { $safeties ->
    [one] siguranță
    [few] siguranțe
    *[other] de siguranțe
}
milebymile-from-all-safeties = { $points } din toate cele 4 siguranțe
milebymile-from-dirty-tricks = { $points } din { $count } { $tricks ->
    [one] truc murdar
    [few] trucuri murdare
    *[other] de trucuri murdare
}

# Game end
milebymile-wins-individual = { $player } câștigă jocul!
milebymile-wins-team = Echipa { $team } câștigă jocul! ({ $members })
milebymile-final-score = Scor final: { $score } puncte

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Tu și ținta ta sunteți ambii evitați! Atacul este neutralizat.
milebymile-karma-clash-you-attacker = Tu și { $attacker } sunteți ambii evitați! Atacul este neutralizat.
milebymile-karma-clash-others = { $attacker } și { $target } sunt ambii evitați! Atacul este neutralizat.
milebymile-karma-clash-your-team = Echipa ta și ținta ta sunt ambele evitate! Atacul este neutralizat.
milebymile-karma-clash-target-team = Tu și Echipa { $team } sunteți ambii evitați! Atacul este neutralizat.
milebymile-karma-clash-other-teams = Echipa { $attacker } și Echipa { $target } sunt ambele evitate! Atacul este neutralizat.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Ai fost evitat pentru agresiunea ta! Karma ta este pierdută.
milebymile-karma-shunned-other = { $player } a fost evitat pentru agresiunea sa!
milebymile-karma-shunned-your-team = Echipa ta a fost evitată pentru agresiunea ei! Karma echipei tale este pierdută.
milebymile-karma-shunned-other-team = Echipa { $team } a fost evitată pentru agresiunea ei!

# False Virtue
milebymile-false-virtue-you = Joci Falsă Virtute și îți recapeți karma!
milebymile-false-virtue-other = { $player } joacă Falsă Virtute și își recapătă karma!
milebymile-false-virtue-your-team = Echipa ta joacă Falsă Virtute și își recapătă karma!
milebymile-false-virtue-other-team = Echipa { $team } joacă Falsă Virtute și își recapătă karma!

# Problems/Safeties (for status display)
milebymile-none = niciuna

# Unplayable card reasons
milebymile-reason-not-on-team = nu ești într-o echipă
milebymile-reason-stopped = ești oprit
milebymile-reason-has-problem = ai o problemă care împiedică conducerea
milebymile-reason-speed-limit = limita de vitez este activă
milebymile-reason-exceeds-distance = ar depăși { $miles } mile
milebymile-reason-no-targets = nu există ținte valide
milebymile-reason-no-speed-limit = nu ești sub o limită de viteză
milebymile-reason-has-right-of-way = Prioritate te lasă să mergi fără semafoare verzi
milebymile-reason-already-moving = te miști deja
milebymile-reason-must-fix-first = trebuie să repari { $problem } mai întâi
milebymile-reason-has-gas = mașina ta are benzină
milebymile-reason-tires-fine = cauciucurile tale sunt în regulă
milebymile-reason-no-accident = mașina ta nu a avut un accident
milebymile-reason-has-safety = ai deja acea siguranță
milebymile-reason-has-karma = încă ai karma ta
milebymile-reason-generic = nu poate fi jucată acum

# Card names
milebymile-card-out-of-gas = Fără Benzină
milebymile-card-flat-tire = Cauciuc Dezumflat
milebymile-card-accident = Accident
milebymile-card-speed-limit = Limită de Viteză
milebymile-card-stop = Stop
milebymile-card-gasoline = Benzină
milebymile-card-spare-tire = Cauciuc de Rezervă
milebymile-card-repairs = Reparații
milebymile-card-end-of-limit = Sfârșitul Limitei
milebymile-card-green-light = Lumină Verde
milebymile-card-extra-tank = Rezervor Extra
milebymile-card-puncture-proof = Rezistent la Puncție
milebymile-card-driving-ace = As la Conducere
milebymile-card-right-of-way = Prioritate
milebymile-card-false-virtue = Falsă Virtute
milebymile-card-miles = { $miles } mile

# Disabled action reasons
milebymile-no-dirty-trick-window = Nicio fereastră de truc murdar activă.
milebymile-not-your-dirty-trick = Nu este fereastra de truc murdar a echipei tale.
milebymile-between-races = Așteaptă următoarea cursă să înceapă.

# Validation errors
milebymile-error-karma-needs-three-teams = Regula karmei necesită cel puțin 3 mașini/echipe distincte.

milebymile-you-play-safety-with-effect = Joci { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } joacă { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Joci { $card } ca un Truc Murdar. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } joacă { $card } ca un Truc Murdar. { $effect }
milebymile-safety-effect-extra-tank = Acum protejat împotriva Fără Combustibil.
milebymile-safety-effect-puncture-proof = Acum protejat împotriva Pană.
milebymile-safety-effect-driving-ace = Acum protejat împotriva Accident.
milebymile-safety-effect-right-of-way = Acum protejat împotriva Stop și Limită de viteză.
