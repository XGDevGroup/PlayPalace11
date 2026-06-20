# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Milja po Milja

# Game options
milebymile-set-distance = Udaljenost utrke: { $miles } milja
milebymile-enter-distance = Unesite udaljenost utrke (300-3000)
milebymile-set-winning-score = Pobjednički rezultat: { $score } bodova
milebymile-enter-winning-score = Unesite pobjednički rezultat (1000-10000)
milebymile-toggle-perfect-crossing = Zahtijevaj točan završetak: { $enabled }
milebymile-toggle-stacking = Dopusti gomilanje napada: { $enabled }
milebymile-toggle-reshuffle = Promiješaj odbačene karte: { $enabled }
milebymile-toggle-karma = Pravilo karme: { $enabled }
milebymile-set-rig = Namještanje špila: { $rig }
milebymile-select-rig = Odaberite opciju namještanja špila

# Option change announcements
milebymile-option-changed-distance = Udaljenost utrke postavljena na { $miles } milja.
milebymile-option-changed-winning = Pobjednički rezultat postavljen na { $score } bodova.
milebymile-option-changed-crossing = Zahtijevaj točan završetak { $enabled }.
milebymile-option-changed-stacking = Dopusti gomilanje napada { $enabled }.
milebymile-option-changed-reshuffle = Promiješaj odbačene karte { $enabled }.
milebymile-option-changed-karma = Pravilo karme { $enabled }.
milebymile-option-changed-rig = Namještanje špila postavljeno na { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } bodova, { $miles } milja, Problemi: { $problems }, Sigurnosti: { $safeties }

# Card actions
milebymile-no-matching-safety = Nemate odgovarajuću sigurnosnu kartu!
milebymile-cant-play = Ne možete odigrati { $card } jer { $reason }.
milebymile-no-card-selected = Nema odabrane karte za odbacivanje.
milebymile-no-valid-targets = Nema valjanih meta za ovu opasnost!
milebymile-you-drew = Izvukli ste: { $card }
milebymile-discards = { $player } odbacuje kartu.
milebymile-select-target = Odaberite metu

# Distance plays
milebymile-plays-distance-individual = { $player } odigrava { $distance } milja i sada je na { $total } milja.
milebymile-plays-distance-team = { $player } odigrava { $distance } milja; njihov tim je sada na { $total } milja.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } je završio putovanje sa savršenim prijelazom!
milebymile-journey-complete-perfect-team = Tim { $team } je završio putovanje sa savršenim prijelazom!
milebymile-journey-complete-individual = { $player } je završio putovanje!
milebymile-journey-complete-team = Tim { $team } je završio putovanje!

# Hazard plays
milebymile-plays-hazard-individual = { $player } odigrava { $card } na { $target }.
milebymile-plays-hazard-team = { $player } odigrava { $card } na Tim { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } odigrava { $card }.
milebymile-plays-dirty-trick = { $player } odigrava { $card } kao Prljavi trik!

# Deck
milebymile-deck-reshuffled = Odbačene karte vraćene u špil.

# Race
milebymile-new-race = Počinje nova utrka!
milebymile-race-complete = Utrka završena! Izračunavanje rezultata...
milebymile-earned-points = { $name } je zaradio { $score } bodova u ovoj utrci: { $breakdown }.
milebymile-total-scores = Ukupni rezultati:
milebymile-team-score = { $name }: { $score } bodova

# Scoring breakdown
milebymile-from-distance = { $miles } od prijeđene udaljenosti
milebymile-from-trip = { $points } od završetka putovanja
milebymile-from-perfect = { $points } od savršenog prijelaza
milebymile-from-safe = { $points } od sigurnog putovanja
milebymile-from-shutout = { $points } od potpunog zatvaranja
milebymile-from-safeties = { $points } od { $count } { $safeties ->
    [one] sigurnosti
    *[other] sigurnosti
}
milebymile-from-all-safeties = { $points } od sve 4 sigurnosti
milebymile-from-dirty-tricks = { $points } od { $count } { $tricks ->
    [one] prljavi trik
    *[other] prljavi trikovi
}

# Game end
milebymile-wins-individual = { $player } pobjeđuje u igri!
milebymile-wins-team = Tim { $team } pobjeđuje u igri! ({ $members })
milebymile-final-score = Konačan rezultat: { $score } bodova

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Vi i vaša meta ste oboje osuđeni! Napad je neutraliziran.
milebymile-karma-clash-you-attacker = Vi i { $attacker } ste oboje osuđeni! Napad je neutraliziran.
milebymile-karma-clash-others = { $attacker } i { $target } su oboje osuđeni! Napad je neutraliziran.
milebymile-karma-clash-your-team = Vaš tim i vaša meta su oboje osuđeni! Napad je neutraliziran.
milebymile-karma-clash-target-team = Vi i Tim { $team } ste oboje osuđeni! Napad je neutraliziran.
milebymile-karma-clash-other-teams = Tim { $attacker } i Tim { $target } su oboje osuđeni! Napad je neutraliziran.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Osuđeni ste zbog svoje agresije! Vaša karma je izgubljena.
milebymile-karma-shunned-other = { $player } je osuđen zbog svoje agresije!
milebymile-karma-shunned-your-team = Vaš tim je osuđen zbog svoje agresije! Karma vašeg tima je izgubljena.
milebymile-karma-shunned-other-team = Tim { $team } je osuđen zbog svoje agresije!

# False Virtue
milebymile-false-virtue-you = Odigravate Lažnu vrlinu i vraćate svoju karmu!
milebymile-false-virtue-other = { $player } odigrava Lažnu vrlinu i vraća svoju karmu!
milebymile-false-virtue-your-team = Vaš tim odigrava Lažnu vrlinu i vraća svoju karmu!
milebymile-false-virtue-other-team = Tim { $team } odigrava Lažnu vrlinu i vraća svoju karmu!

# Problems/Safeties (for status display)
milebymile-none = ništa

# Unplayable card reasons
milebymile-reason-not-on-team = niste u timu
milebymile-reason-stopped = stali ste
milebymile-reason-has-problem = imate problem koji sprječava vožnju
milebymile-reason-speed-limit = ograničenje brzine je aktivno
milebymile-reason-exceeds-distance = prekoračilo bi { $miles } milja
milebymile-reason-no-targets = nema valjanih meta
milebymile-reason-no-speed-limit = niste pod ograničenjem brzine
milebymile-reason-has-right-of-way = Prednost prolaza omogućava vožnju bez zelenih svjetala
milebymile-reason-already-moving = već se krećete
milebymile-reason-must-fix-first = prvo morate popraviti { $problem }
milebymile-reason-has-gas = vaš automobil ima benzin
milebymile-reason-tires-fine = vaše gume su u redu
milebymile-reason-no-accident = vaš automobil nije imao nesreću
milebymile-reason-has-safety = već imate tu sigurnost
milebymile-reason-has-karma = još uvijek imate svoju karmu
milebymile-reason-generic = ne može se odigrati sada

# Card names
milebymile-card-out-of-gas = Ostalo bez benzina
milebymile-card-flat-tire = Prazna guma
milebymile-card-accident = Nesreća
milebymile-card-speed-limit = Ograničenje brzine
milebymile-card-stop = Stop
milebymile-card-gasoline = Benzin
milebymile-card-spare-tire = Rezervna guma
milebymile-card-repairs = Popravak
milebymile-card-end-of-limit = Kraj ograničenja
milebymile-card-green-light = Zeleno svjetlo
milebymile-card-extra-tank = Dodatni rezervoar
milebymile-card-puncture-proof = Otporno na probijanje
milebymile-card-driving-ace = As vožnje
milebymile-card-right-of-way = Prednost prolaza
milebymile-card-false-virtue = Lažna vrlina
milebymile-card-miles = { $miles } milja

# Disabled action reasons
milebymile-no-dirty-trick-window = Nema aktivnog prozora za prljavi trik.
milebymile-not-your-dirty-trick = To nije prozor za prljavi trik vašeg tima.
milebymile-between-races = Pričekajte početak sljedeće utrke.

# Validation errors
milebymile-error-karma-needs-three-teams = Pravilo karme zahtijeva najmanje 3 različita automobila/tima.

milebymile-you-play-safety-with-effect = Igrate { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } igra { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Igrate { $card } kao Prljavi trik. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } igra { $card } kao Prljavi trik. { $effect }
milebymile-safety-effect-extra-tank = Sada zaštićeni od Nedostatka goriva.
milebymile-safety-effect-puncture-proof = Sada zaštićeni od Probušene gume.
milebymile-safety-effect-driving-ace = Sada zaštićeni od Nesreće.
milebymile-safety-effect-right-of-way = Sada zaštićeni od Stopa i Ograničenja brzine.
