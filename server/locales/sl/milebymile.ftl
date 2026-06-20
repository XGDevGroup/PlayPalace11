# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Milja za Miljo

# Game options
milebymile-set-distance = Razdalja dirke: { $miles } milj
milebymile-enter-distance = Vnesite razdaljo dirke (300-3000)
milebymile-set-winning-score = Zmagovalni rezultat: { $score } točk
milebymile-enter-winning-score = Vnesite zmagovalni rezultat (1000-10000)
milebymile-toggle-perfect-crossing = Zahtevaj natančen cilj: { $enabled }
milebymile-toggle-stacking = Dovoli kopičenje napadov: { $enabled }
milebymile-toggle-reshuffle = Premešaj zavržen kup: { $enabled }
milebymile-toggle-karma = Pravilo karme: { $enabled }
milebymile-set-rig = Manipulacija kupčka: { $rig }
milebymile-select-rig = Izberite možnost manipulacije kupčka

# Option change announcements
milebymile-option-changed-distance = Razdalja dirke nastavljena na { $miles } milj.
milebymile-option-changed-winning = Zmagovalni rezultat nastavljen na { $score } točk.
milebymile-option-changed-crossing = Zahtevaj natančen cilj { $enabled }.
milebymile-option-changed-stacking = Dovoli kopičenje napadov { $enabled }.
milebymile-option-changed-reshuffle = Premešaj zavržen kup { $enabled }.
milebymile-option-changed-karma = Pravilo karme { $enabled }.
milebymile-option-changed-rig = Manipulacija kupčka nastavljena na { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } točk, { $miles } milj, Težave: { $problems }, Zaščite: { $safeties }

# Card actions
milebymile-no-matching-safety = Nimate ustrezne varnostne karte!
milebymile-cant-play = Ne morete igrati { $card }, ker { $reason }.
milebymile-no-card-selected = Nobena karta ni izbrana za zavreči.
milebymile-no-valid-targets = Ni veljavnih ciljev za to nevarnost!
milebymile-you-drew = Potegnili ste: { $card }
milebymile-discards = { $player } zavrže karto.
milebymile-select-target = Izberite cilj

# Distance plays
milebymile-plays-distance-individual = { $player } igra { $distance } milj in je zdaj na { $total } miljah.
milebymile-plays-distance-team = { $player } igra { $distance } milj; njihova ekipa je zdaj na { $total } miljah.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } je dokončal potovanje s popolnim prehodom!
milebymile-journey-complete-perfect-team = Ekipa { $team } je dokončala potovanje s popolnim prehodom!
milebymile-journey-complete-individual = { $player } je dokončal potovanje!
milebymile-journey-complete-team = Ekipa { $team } je dokončala potovanje!

# Hazard plays
milebymile-plays-hazard-individual = { $player } igra { $card } na { $target }.
milebymile-plays-hazard-team = { $player } igra { $card } na Ekipo { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } igra { $card }.
milebymile-plays-dirty-trick = { $player } igra { $card } kot Umazano Trik!

# Deck
milebymile-deck-reshuffled = Zavržen kup premešan nazaj v kupček.

# Race
milebymile-new-race = Začne se nova dirka!
milebymile-race-complete = Dirka končana! Računanje rezultatov...
milebymile-earned-points = { $name } je zaslužil { $score } točk v tej dirki: { $breakdown }.
milebymile-total-scores = Skupni rezultati:
milebymile-team-score = { $name }: { $score } točk

# Scoring breakdown
milebymile-from-distance = { $miles } iz prepotovane razdalje
milebymile-from-trip = { $points } za dokončanje potovanja
milebymile-from-perfect = { $points } za popoln prehod
milebymile-from-safe = { $points } za varno potovanje
milebymile-from-shutout = { $points } za popolno izključitev
milebymile-from-safeties = { $points } iz { $count } { $safeties ->
    [one] zaščite
    *[other] zaščit
}
milebymile-from-all-safeties = { $points } iz vseh 4 zaščit
milebymile-from-dirty-tricks = { $points } iz { $count } { $tricks ->
    [one] umazanega trika
    *[other] umazanih trikov
}

# Game end
milebymile-wins-individual = { $player } zmaga igro!
milebymile-wins-team = Ekipa { $team } zmaga igro! ({ $members })
milebymile-final-score = Končni rezultat: { $score } točk

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Vi in vaš cilj sta oba izobčena! Napad je nevtraliziran.
milebymile-karma-clash-you-attacker = Vi in { $attacker } sta oba izobčena! Napad je nevtraliziran.
milebymile-karma-clash-others = { $attacker } in { $target } sta oba izobčena! Napad je nevtraliziran.
milebymile-karma-clash-your-team = Vaša ekipa in vaš cilj sta oba izobčena! Napad je nevtraliziran.
milebymile-karma-clash-target-team = Vi in Ekipa { $team } sta oba izobčena! Napad je nevtraliziran.
milebymile-karma-clash-other-teams = Ekipa { $attacker } in Ekipa { $target } sta obe izobčeni! Napad je nevtraliziran.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Izobčeni ste bili zaradi vaše agresije! Vaša karma je izgubljena.
milebymile-karma-shunned-other = { $player } je bil izobčen zaradi svoje agresije!
milebymile-karma-shunned-your-team = Vaša ekipa je bila izobčena zaradi svoje agresije! Karma vaše ekipe je izgubljena.
milebymile-karma-shunned-other-team = Ekipa { $team } je bila izobčena zaradi svoje agresije!

# False Virtue
milebymile-false-virtue-you = Igrate Lažno Krepost in povrnete svojo karmo!
milebymile-false-virtue-other = { $player } igra Lažno Krepost in povrne svojo karmo!
milebymile-false-virtue-your-team = Vaša ekipa igra Lažno Krepost in povrne svojo karmo!
milebymile-false-virtue-other-team = Ekipa { $team } igra Lažno Krepost in povrne svojo karmo!

# Problems/Safeties (for status display)
milebymile-none = nič

# Unplayable card reasons
milebymile-reason-not-on-team = niste v ekipi
milebymile-reason-stopped = ste ustavljeni
milebymile-reason-has-problem = imate težavo, ki preprečuje vožnjo
milebymile-reason-speed-limit = omejitev hitrosti je aktivna
milebymile-reason-exceeds-distance = bi preseglo { $miles } milj
milebymile-reason-no-targets = ni veljavnih ciljev
milebymile-reason-no-speed-limit = niste pod omejitvijo hitrosti
milebymile-reason-has-right-of-way = Prednost omogoča vožnjo brez zelenih luči
milebymile-reason-already-moving = že se premikate
milebymile-reason-must-fix-first = najprej morate popraviti { $problem }
milebymile-reason-has-gas = vaš avto ima gorivo
milebymile-reason-tires-fine = vaše pnevmatike so v redu
milebymile-reason-no-accident = vaš avto ni imel nesreče
milebymile-reason-has-safety = že imate to zaščito
milebymile-reason-has-karma = še vedno imate svojo karmo
milebymile-reason-generic = ne more biti odigrano zdaj

# Card names
milebymile-card-out-of-gas = Zmanjkalo Goriva
milebymile-card-flat-tire = Počena Pnevmatika
milebymile-card-accident = Nesreča
milebymile-card-speed-limit = Omejitev Hitrosti
milebymile-card-stop = Stop
milebymile-card-gasoline = Gorivo
milebymile-card-spare-tire = Nadomestna Pnevmatika
milebymile-card-repairs = Popravila
milebymile-card-end-of-limit = Konec Omejitve
milebymile-card-green-light = Zelena Luč
milebymile-card-extra-tank = Dodatni Rezervoar
milebymile-card-puncture-proof = Odporno na Preluknjanje
milebymile-card-driving-ace = As Vožnje
milebymile-card-right-of-way = Prednost
milebymile-card-false-virtue = Lažna Krepost
milebymile-card-miles = { $miles } milj

# Disabled action reasons
milebymile-no-dirty-trick-window = Ni aktivnega okna umazanega trika.
milebymile-not-your-dirty-trick = To ni okno umazanega trika vaše ekipe.
milebymile-between-races = Počakajte na začetek naslednje dirke.

# Validation errors
milebymile-error-karma-needs-three-teams = Pravilo karme zahteva vsaj 3 različne avte/ekipe.

milebymile-you-play-safety-with-effect = Igraš { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } igra { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Igraš { $card } kot Umazan trik. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } igra { $card } kot Umazan trik. { $effect }
milebymile-safety-effect-extra-tank = Zdaj zaščiteno pred Brez goriva.
milebymile-safety-effect-puncture-proof = Zdaj zaščiteno pred Počeno pnevmatiko.
milebymile-safety-effect-driving-ace = Zdaj zaščiteno pred Nesrečo.
milebymile-safety-effect-right-of-way = Zdaj zaščiteno pred Stop in Omejitvijo hitrosti.
