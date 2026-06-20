# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Mérföld mérföld után

# Game options
milebymile-set-distance = Verseny távolság: { $miles } mérföld
milebymile-enter-distance = Adja meg a verseny távolságát (300-3000)
milebymile-set-winning-score = Győzelmi pontszám: { $score } pont
milebymile-enter-winning-score = Adja meg a győzelmi pontszámot (1000-10000)
milebymile-toggle-perfect-crossing = Pontos befejezés szükséges: { $enabled }
milebymile-toggle-stacking = Támadások halmozása: { $enabled }
milebymile-toggle-reshuffle = Dobópakli újrakeverése: { $enabled }
milebymile-toggle-karma = Karma szabály: { $enabled }
milebymile-set-rig = Pakli manipuláció: { $rig }
milebymile-select-rig = Válasszon pakli manipuláció opciót

# Option change announcements
milebymile-option-changed-distance = Verseny távolság beállítva { $miles } mérföldre.
milebymile-option-changed-winning = Győzelmi pontszám beállítva { $score } pontra.
milebymile-option-changed-crossing = Pontos befejezés szükséges { $enabled }.
milebymile-option-changed-stacking = Támadások halmozása { $enabled }.
milebymile-option-changed-reshuffle = Dobópakli újrakeverése { $enabled }.
milebymile-option-changed-karma = Karma szabály { $enabled }.
milebymile-option-changed-rig = Pakli manipuláció beállítva: { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } pont, { $miles } mérföld, Problémák: { $problems }, Védelem: { $safeties }

# Card actions
milebymile-no-matching-safety = Nincs megfelelő védelmi kártyája!
milebymile-cant-play = Nem játszhatja ki a következőt: { $card }, mert { $reason }.
milebymile-no-card-selected = Nincs kiválasztott kártya eldobásra.
milebymile-no-valid-targets = Nincsenek érvényes célpontok ehhez a veszélyhez!
milebymile-you-drew = Húzott: { $card }
milebymile-discards = { $player } eldob egy kártyát.
milebymile-select-target = Válasszon célpontot

# Distance plays
milebymile-plays-distance-individual = { $player } { $distance } mérföldet játszik, és most { $total } mérföldnél tart.
milebymile-plays-distance-team = { $player } { $distance } mérföldet játszik; csapatuk most { $total } mérföldnél tart.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } tökéletes átkeléssel befejezte az utat!
milebymile-journey-complete-perfect-team = A(z) { $team } csapat tökéletes átkeléssel befejezte az utat!
milebymile-journey-complete-individual = { $player } befejezte az utat!
milebymile-journey-complete-team = A(z) { $team } csapat befejezte az utat!

# Hazard plays
milebymile-plays-hazard-individual = { $player } kijátssza a következőt: { $card } erre: { $target }.
milebymile-plays-hazard-team = { $player } kijátssza a következőt: { $card } a(z) { $team } csapatra.

# Remedy/Safety plays
milebymile-plays-card = { $player } kijátssza: { $card }.
milebymile-plays-dirty-trick = { $player } kijátssza a következőt: { $card } piszkos trükkként!

# Deck
milebymile-deck-reshuffled = Dobópakli visszakeverve a pakliba.

# Race
milebymile-new-race = Új verseny kezdődik!
milebymile-race-complete = Verseny befejezve! Pontszámok számolása...
milebymile-earned-points = { $name } { $score } pontot szerzett ebben a versenyben: { $breakdown }.
milebymile-total-scores = Összes pontszám:
milebymile-team-score = { $name }: { $score } pont

# Scoring breakdown
milebymile-from-distance = { $miles } megtett távolságból
milebymile-from-trip = { $points } az út befejezéséért
milebymile-from-perfect = { $points } tökéletes átkelésért
milebymile-from-safe = { $points } biztonságos útért
milebymile-from-shutout = { $points } teljes kizárásért
milebymile-from-safeties = { $points } { $count } { $safeties ->
    [one] védelemből
    *[other] védelemből
}
milebymile-from-all-safeties = { $points } mind a 4 védelemből
milebymile-from-dirty-tricks = { $points } { $count } { $tricks ->
    [one] piszkos trükkből
    *[other] piszkos trükkből
}

# Game end
milebymile-wins-individual = { $player } megnyerte a játékot!
milebymile-wins-team = A(z) { $team } csapat megnyerte a játékot! ({ $members })
milebymile-final-score = Végső pontszám: { $score } pont

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Ön és a célpontja mindketten kiközösítve! A támadás semlegesítve.
milebymile-karma-clash-you-attacker = Ön és { $attacker } mindketten kiközösítve! A támadás semlegesítve.
milebymile-karma-clash-others = { $attacker } és { $target } mindketten kiközösítve! A támadás semlegesítve.
milebymile-karma-clash-your-team = Az Ön csapata és a célpontja mindketten kiközösítve! A támadás semlegesítve.
milebymile-karma-clash-target-team = Ön és a(z) { $team } csapat mindketten kiközösítve! A támadás semlegesítve.
milebymile-karma-clash-other-teams = A(z) { $attacker } és a(z) { $target } csapat mindketten kiközösítve! A támadás semlegesítve.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Kiközösítették agressziója miatt! Karmája elveszett.
milebymile-karma-shunned-other = { $player } kiközösítve lett agressziója miatt!
milebymile-karma-shunned-your-team = Csapata kiközösítve lett agressziója miatt! Csapata karmája elveszett.
milebymile-karma-shunned-other-team = A(z) { $team } csapat kiközösítve lett agressziója miatt!

# False Virtue
milebymile-false-virtue-you = Ön kijátssza a Hamis erényt és visszanyeri karmáját!
milebymile-false-virtue-other = { $player } kijátssza a Hamis erényt és visszanyeri karmáját!
milebymile-false-virtue-your-team = Csapata kijátssza a Hamis erényt és visszanyeri karmáját!
milebymile-false-virtue-other-team = A(z) { $team } csapat kijátssza a Hamis erényt és visszanyeri karmáját!

# Problems/Safeties (for status display)
milebymile-none = nincs

# Unplayable card reasons
milebymile-reason-not-on-team = nem tartozik csapathoz
milebymile-reason-stopped = megállt
milebymile-reason-has-problem = olyan problémája van, ami megakadályozza a vezetést
milebymile-reason-speed-limit = a sebességkorlátozás aktív
milebymile-reason-exceeds-distance = túllépné a { $miles } mérföldet
milebymile-reason-no-targets = nincsenek érvényes célpontok
milebymile-reason-no-speed-limit = nincs sebességkorlátozás alatt
milebymile-reason-has-right-of-way = Az elsőbbség lehetővé teszi a haladást zöld lámpa nélkül
milebymile-reason-already-moving = már mozgásban van
milebymile-reason-must-fix-first = először meg kell javítania a következőt: { $problem }
milebymile-reason-has-gas = autójában van benzin
milebymile-reason-tires-fine = gumiabroncsai rendben vannak
milebymile-reason-no-accident = autója nem volt balesetben
milebymile-reason-has-safety = már rendelkezik ezzel a védelemmel
milebymile-reason-has-karma = még mindig megvan a karmája
milebymile-reason-generic = most nem játszható ki

# Card names
milebymile-card-out-of-gas = Kifogyott a benzin
milebymile-card-flat-tire = Defekt
milebymile-card-accident = Baleset
milebymile-card-speed-limit = Sebességkorlátozás
milebymile-card-stop = Stop
milebymile-card-gasoline = Benzin
milebymile-card-spare-tire = Pótkerék
milebymile-card-repairs = Javítás
milebymile-card-end-of-limit = Korlátozás vége
milebymile-card-green-light = Zöld lámpa
milebymile-card-extra-tank = Extra tank
milebymile-card-puncture-proof = Defektbiztos
milebymile-card-driving-ace = Vezetési ász
milebymile-card-right-of-way = Elsőbbség
milebymile-card-false-virtue = Hamis erény
milebymile-card-miles = { $miles } mérföld

# Disabled action reasons
milebymile-no-dirty-trick-window = Nincs aktív piszkos trükk ablak.
milebymile-not-your-dirty-trick = Ez nem az Ön csapatának piszkos trükk ablaka.
milebymile-between-races = Várja meg a következő verseny kezdetét.

# Validation errors
milebymile-error-karma-needs-three-teams = A karma szabályhoz legalább 3 különböző autó/csapat szükséges.

milebymile-you-play-safety-with-effect = Kijátszod: { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } kijátssza: { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Kijátszod a { $card } lapot piszkos trükként. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } kijátssza a { $card } lapot piszkos trükkként. { $effect }
milebymile-safety-effect-extra-tank = Most védett az Üzemanyaghiány ellen.
milebymile-safety-effect-puncture-proof = Most védett a Defekt ellen.
milebymile-safety-effect-driving-ace = Most védett a Baleset ellen.
milebymile-safety-effect-right-of-way = Most védett a Stop és a Sebességkorlátozás ellen.
