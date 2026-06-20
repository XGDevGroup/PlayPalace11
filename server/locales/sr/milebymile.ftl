# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Kilometar po kilometar

# Game options
milebymile-set-distance = Udaljenost do kraja trke: { $miles } kilometara
milebymile-enter-distance = Upišite udaljenost do kraja trke (300-3000)
milebymile-set-winning-score = Rezultat za pobedu: { $score } poena
milebymile-enter-winning-score = Upišite rezultat za pobedu (1000-10000)
milebymile-toggle-perfect-crossing = Zahtevaj precizan dolazak do cilja: { $enabled }
milebymile-toggle-stacking = Dozvoli nizanje napada: { $enabled }
milebymile-toggle-reshuffle = Ponovo promešaj odbačene karte u špil: { $enabled }
milebymile-toggle-karma = Pravilo karme: { $enabled }
milebymile-set-rig = Štelovanje špila: { $rig }
milebymile-select-rig = Izaberite opciju štelovanja špila

# Option change announcements
milebymile-option-changed-distance = Udaljenost do kraja trke podešena na { $miles } kilometara.
milebymile-option-changed-winning = Rezultat za pobedu podešen na { $score } poena.
milebymile-option-changed-crossing = Zahtevanje preciznog dolaska do cilja { $enabled }.
milebymile-option-changed-stacking = Nizanje napada { $enabled }.
milebymile-option-changed-reshuffle = Mešanje odbačenih karata u špil { $enabled }.
milebymile-option-changed-karma = Pravilo karme { $enabled }.
milebymile-option-changed-rig = Štelovanje špila podešeno na { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } poena, { $miles } kilometara, Problemi: { $problems }, Zaštite: { $safeties }

# Card actions
milebymile-no-matching-safety = Nemate odgovarajuću zaštitu!
milebymile-cant-play = Ne možete da igrate { $card }  { $reason }.
milebymile-no-card-selected = Nijedna karta nije izabrana za odbacivanje.
milebymile-no-valid-targets = Nema mogućih protivnika za ovaj napad!
milebymile-you-drew = Vučete: { $card }
milebymile-discards = { $player } odbacuje kartu.
milebymile-select-target = Izaberite protivnika

# Distance plays
milebymile-plays-distance-individual = { $player } igra { $distance } kilometara, sada je na { $total } kilometara.
milebymile-plays-distance-team = { $player } igra { $distance } kilometara; tim je sada na { $total } kilometara.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } je završio putovanje savršenim dolaskom do cilja!
milebymile-journey-complete-perfect-team = Tim { $team } je završio putovanje savršenim dolaskom do cilja!
milebymile-journey-complete-individual = { $player } je završio putovanje!
milebymile-journey-complete-team = Tim { $team } je završio putovanje!

# Hazard plays
milebymile-plays-hazard-individual = { $player } igra { $card } protiv igrača { $target }.
milebymile-plays-hazard-team = { $player } igra { $card } protiv tima  { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } igra { $card }.
milebymile-plays-dirty-trick = { $player } igra { $card } kao prljav trik!

# Deck
milebymile-deck-reshuffled = Odbačene karte su promešane nazad u špil.

# Race
milebymile-new-race = Nova trka počinje!
milebymile-race-complete = Trka završena! Računanje rezultata...
milebymile-earned-points = { $name } dobija { $score } poena za ovu trku: { $breakdown }.
milebymile-total-scores = Ukupan rezultat:
milebymile-team-score = { $name }: { $score } poena

# Scoring breakdown
milebymile-from-distance = { $miles } za pređen put
milebymile-from-trip = { $points } za završeno putovanje
milebymile-from-perfect = { $points } za savršen dolazak do cilja
milebymile-from-safe = { $points } za bezbedno putovanje
milebymile-from-shutout = { $points } za zatvaranje
milebymile-from-safeties = { $points } za { $count } { $safeties ->
    [one] zaštitu
    *[other] zaštite
}
milebymile-from-all-safeties = { $points } za sve četiri zaštite
milebymile-from-dirty-tricks = { $points } za { $count } { $tricks ->
    [one] prljav trik
    *[other] prljava trika
}

# Game end
milebymile-wins-individual = { $player } pobeđuje!
milebymile-wins-team = Tim { $team } pobeđuje! ({ $members })
milebymile-final-score = Konačni rezultat: { $score } poena

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Vi i vaš protivnik ste prokleti! Napad se neutrališe.
milebymile-karma-clash-you-attacker = Vi i { $attacker } ste prokleti! Napad se neutrališe.
milebymile-karma-clash-others = { $attacker } i { $target } su prokleti! Napad se neutrališe.
milebymile-karma-clash-your-team = Vaš tim i vaši protivnici su prokleti! Napad se neutrališe.
milebymile-karma-clash-target-team = Vi i tim { $team } ste prokleti! Napad se neutrališe.
milebymile-karma-clash-other-teams = Tim { $attacker } i tim { $target } su prokleti! Napad se neutrališe.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Prokleti ste zbog vaše agresije! Vaša karma je izgubljena.
milebymile-karma-shunned-other = { $player } dobija prokletstvo zbog svoje agresije!
milebymile-karma-shunned-your-team = Vaš tim je proklet zbog svoje agresije! Karma vašeg tima je izgubljena.
milebymile-karma-shunned-other-team = Tim { $team } je proklet zbog svoje agresije!

# False Virtue
milebymile-false-virtue-you = Igrate lažnu skromnost i vraćate vašu karmu!
milebymile-false-virtue-other = { $player } igra lažnu skromnost i vraća svoju karmu!
milebymile-false-virtue-your-team = Vaš tim igra lažnu skromnost i vraća svoju karmu!
milebymile-false-virtue-other-team = Tim { $team } igra lažnu skromnost i vraća svoju karmu!

# Problems/Safeties (for status display)
milebymile-none = Nema

# Unplayable card reasons
milebymile-reason-not-on-team = Niste u timu
milebymile-reason-stopped = Zaustavljeni ste
milebymile-reason-has-problem = Imate problem koji sprečava vožnju
milebymile-reason-speed-limit = Ograničenje brzine je aktivno
milebymile-reason-exceeds-distance = Prešlo bi { $miles } kilometara
milebymile-reason-no-targets = Nema ispravnih protivnika
milebymile-reason-no-speed-limit = Niste pod ograničenjem brzine
milebymile-reason-has-right-of-way = Prvenstvo prolaza vam dozvoljava da se krećete bez zelenog svetla
milebymile-reason-already-moving = Već se krećete
milebymile-reason-must-fix-first = Prvo morate da rešite problem { $problem }
milebymile-reason-has-gas = Vaš automobil ima gorivo
milebymile-reason-tires-fine = Vaše gume su ispravne
milebymile-reason-no-accident = Vaš automobil nije slupan
milebymile-reason-has-safety = Već imate tu zaštitu
milebymile-reason-has-karma = Još uvek imate vašu karmu
milebymile-reason-generic = Ne može se igrati sada

# Card names
milebymile-card-out-of-gas = Bez goriva
milebymile-card-flat-tire = Bušenje gume
milebymile-card-accident = Udes
milebymile-card-speed-limit = Ograničenje brzine
milebymile-card-stop = Stop
milebymile-card-gasoline = Punjenje goriva
milebymile-card-spare-tire = Rezervna guma
milebymile-card-repairs = Popravke
milebymile-card-end-of-limit = Uklanjanje ograničenja
milebymile-card-green-light = Zeleno svetlo
milebymile-card-extra-tank = Dodatni rezervoar
milebymile-card-puncture-proof = Otporna guma
milebymile-card-driving-ace = Majstor vožnje
milebymile-card-right-of-way = Prvenstvo prolaza
milebymile-card-false-virtue = Lažna skromnost
milebymile-card-miles = { $miles } kilometara

# Disabled action reasons
milebymile-no-dirty-trick-window = Sada nije trenutan za prljav trik.
milebymile-not-your-dirty-trick = Nije trenutak za prljav trik vašeg  tima.
milebymile-between-races = Sačekajte da sledeća trka krene.

# Validation errors
milebymile-error-karma-needs-three-teams = Pravilo karme zahteva bar tri automobila/tima.

milebymile-you-play-safety-with-effect = Igrate { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } igra { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Igrate { $card } kao prljav trik. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } igra { $card } kao prljav trik. { $effect }
milebymile-safety-effect-extra-tank = Sada zaštićen od pražnjenja goriva.
milebymile-safety-effect-puncture-proof = Sada zaštićen od bušenja gume.
milebymile-safety-effect-driving-ace = Sada zaštićen od udesa.
milebymile-safety-effect-right-of-way = Sada zaštićen od zaustavljanja i ograničenja brzine.
