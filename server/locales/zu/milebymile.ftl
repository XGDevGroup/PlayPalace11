# Mile by Mile game messages (isiZulu)

# Game name
game-name-milebymile = Mile by Mile

# Game options
milebymile-set-distance = Ibanga lokugijima: { $miles } amamayela
milebymile-enter-distance = Faka ibanga lokugijima (300-3000)
milebymile-set-winning-score = Amaphuzu okunqoba: { $score } amaphuzu
milebymile-enter-winning-score = Faka amaphuzu okunqoba (1000-10000)
milebymile-toggle-perfect-crossing = Udinga ukuqeda ngokuqondile: { $enabled }
milebymile-toggle-stacking = Vumela ukuhlanganisa ukuhlasela: { $enabled }
milebymile-toggle-reshuffle = Xova kabusha inqwaba yokulahlwa: { $enabled }
milebymile-toggle-karma = Umthetho we-karma: { $enabled }
milebymile-set-rig = Ukutshela isigange: { $rig }
milebymile-select-rig = Khetha inketho yokutshela isigange

# Option change announcements
milebymile-option-changed-distance = Ibanga lokugijima lisetelwe kuma-{ $miles } mayela.
milebymile-option-changed-winning = Amaphuzu okunqoba asetelwe ku-{ $score }.
milebymile-option-changed-crossing = Udinga ukuqeda ngokuqondile { $enabled }.
milebymile-option-changed-stacking = Vumela ukuhlanganisa ukuhlasela { $enabled }.
milebymile-option-changed-reshuffle = Xova kabusha inqwaba yokulahlwa { $enabled }.
milebymile-option-changed-karma = Umthetho we-karma { $enabled }.
milebymile-option-changed-rig = Ukutshela isigange kusetelwe ku-{ $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } amaphuzu, { $miles } amamayela, Izinkinga: { $problems }, Ukuphepha: { $safeties }

# Card actions
milebymile-no-matching-safety = Awunayo ikhadi lokuphepha elifananayo!
milebymile-cant-play = Awukwazi ukudlala { $card } ngoba { $reason }.
milebymile-no-card-selected = Alikho ikhadi elikhethiwe lokukalahla.
milebymile-no-valid-targets = Azikho izinto ezihlosiwe ezivumelekile zalesi siyingozi!
milebymile-you-drew = Wena udonse: { $card }
milebymile-discards = U-{ $player } ukalahla ikhadi.
milebymile-select-target = Khetha okuhlosiwe

# Distance plays
milebymile-plays-distance-individual = U-{ $player } udlala { $distance } amamayela, futhi manje usekhona { $total } amamayela.
milebymile-plays-distance-team = U-{ $player } udlala { $distance } amamayela; ithimba labo manje lisekhona { $total } amamayela.

# Journey complete
milebymile-journey-complete-perfect-individual = U-{ $player } uqedile uhambo ngokudlula ngokuqondile!
milebymile-journey-complete-perfect-team = Ithimba { $team } liqedile uhambo ngokudlula ngokuqondile!
milebymile-journey-complete-individual = U-{ $player } uqedile uhambo!
milebymile-journey-complete-team = Ithimba { $team } liqedile uhambo!

# Hazard plays
milebymile-plays-hazard-individual = U-{ $player } udlala { $card } ku-{ $target }.
milebymile-plays-hazard-team = U-{ $player } udlala { $card } kuThimba { $team }.

# Remedy/Safety plays
milebymile-plays-card = U-{ $player } udlala { $card }.
milebymile-plays-dirty-trick = U-{ $player } udlala { $card } njenge-Dirty Trick!

# Deck
milebymile-deck-reshuffled = Inqwaba yokulahlwa ixovwe kabusha yaba sesigangeni.

# Race
milebymile-new-race = Ukugijima okusha kuyaqala!
milebymile-race-complete = Ukugijima kuphelile! Kubalwa amaphuzu...
milebymile-earned-points = { $name } uphumelele amaphuzu angu-{ $score } kulokhu kugijima: { $breakdown }.
milebymile-total-scores = Amaphuzu esamba:
milebymile-team-score = { $name }: { $score } amaphuzu

# Scoring breakdown
milebymile-from-distance = { $miles } kusuka ebangeni elithathiwe
milebymile-from-trip = { $points } kusuka ekuqedeni uhambo
milebymile-from-perfect = { $points } kusuka ekudluleni ngokuqondile
milebymile-from-safe = { $points } kusuka ohambweni oluphephile
milebymile-from-shutout = { $points } kusuka ekuvaleni
milebymile-from-safeties = { $points } kusuka ku-{ $count } { $safeties ->
    [one] ukuphepha
    *[other] ukuphepha
}
milebymile-from-all-safeties = { $points } kusuka kukho konke ukuphepha okungu-4
milebymile-from-dirty-tricks = { $points } kusuka ku-{ $count } { $tricks ->
    [one] dirty trick
    *[other] dirty tricks
}

# Game end
milebymile-wins-individual = U-{ $player } uwina umdlalo!
milebymile-wins-team = Ithimba { $team } liwina umdlalo! ({ $members })
milebymile-final-score = Amaphuzu okugcina: { $score } amaphuzu

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Wena nokuhlosiwe kwakho niyadelwa bobabili! Ukuhlasela kupheliswe.
milebymile-karma-clash-you-attacker = Wena no-{ $attacker } niyadelwa bobabili! Ukuhlasela kupheliswe.
milebymile-karma-clash-others = U-{ $attacker } no-{ $target } badelwa bobabili! Ukuhlasela kupheliswe.
milebymile-karma-clash-your-team = Ithimba lakho nokuhlosiwe kwenu niyadelwa bobabili! Ukuhlasela kupheliswe.
milebymile-karma-clash-target-team = Wena neThimba { $team } niyadelwa bobabili! Ukuhlasela kupheliswe.
milebymile-karma-clash-other-teams = Ithimba { $attacker } neThimba { $target } lidelwa bobabili! Ukuhlasela kupheliswe.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Wena udelwe ngenxa yokuhlasela kwakho! I-karma yakho ilahlekile.
milebymile-karma-shunned-other = U-{ $player } udelwe ngenxa yokuhlasela kwakhe!
milebymile-karma-shunned-your-team = Ithimba lakho lidelwe ngenxa yokuhlasela kwalo! I-karma yethimba lakho ilahlekile.
milebymile-karma-shunned-other-team = Ithimba { $team } lidelwe ngenxa yokuhlasela kwalo!

# False Virtue
milebymile-false-virtue-you = Wena udlala i-False Virtue futhi ubuyisela i-karma yakho!
milebymile-false-virtue-other = U-{ $player } udlala i-False Virtue futhi ubuyisela i-karma yakhe!
milebymile-false-virtue-your-team = Ithimba lakho lidlala i-False Virtue futhi libuyisela i-karma yalo!
milebymile-false-virtue-other-team = Ithimba { $team } lidlala i-False Virtue futhi libuyisela i-karma yalo!

# Problems/Safeties (for status display)
milebymile-none = lutho

# Unplayable card reasons
milebymile-reason-not-on-team = awukho ethimbeni
milebymile-reason-stopped = umile
milebymile-reason-has-problem = unenkinga evimbela ukushayela
milebymile-reason-speed-limit = umkhawulo wejubane uyasebenza
milebymile-reason-exceeds-distance = kungadlula { $miles } amamayela
milebymile-reason-no-targets = azikho izinto ezihlosiwe ezivumelekile
milebymile-reason-no-speed-limit = awukho ngaphansi komkhawulo wejubane
milebymile-reason-has-right-of-way = I-Right of Way ikuvumela ukuhamba ngaphandle kwezibani eziluhlaza
milebymile-reason-already-moving = usuvele uhamba
milebymile-reason-must-fix-first = kufanele ulungise { $problem } kuqala
milebymile-reason-has-gas = imoto yakho inegesi
milebymile-reason-tires-fine = amathayi akho alungile
milebymile-reason-no-accident = imoto yakho ayizange ibe nengozi
milebymile-reason-has-safety = usuvele unalokho kuphepha
milebymile-reason-has-karma = usanayo i-karma yakho
milebymile-reason-generic = ayikwazi ukudlalwa manje

# Card names
milebymile-card-out-of-gas = Awunayo Igesi
milebymile-card-flat-tire = Ithayi Eliphansi
milebymile-card-accident = Ingozi
milebymile-card-speed-limit = Umkhawulo Wejubane
milebymile-card-stop = Yima
milebymile-card-gasoline = Igesi
milebymile-card-spare-tire = Ithayi Elisesehlukileyo
milebymile-card-repairs = Ukulungisa
milebymile-card-end-of-limit = Ukuphela Komkhawulo
milebymile-card-green-light = Ukukhanya Okuluhlaza
milebymile-card-extra-tank = Ithangi Elengeziwe
milebymile-card-puncture-proof = Okuvikela Ukugqojwa
milebymile-card-driving-ace = Umshayeli Ociko
milebymile-card-right-of-way = Ilungelo Lokudlula
milebymile-card-false-virtue = Ubulungisa Obungamanga
milebymile-card-miles = { $miles } amamayela

# Disabled action reasons
milebymile-no-dirty-trick-window = Ayikho iwindi le-dirty trick elisebenzayo.
milebymile-not-your-dirty-trick = Akusiyona iwindi le-dirty trick lethimba lakho.
milebymile-between-races = Linda ukuqala kokugijima okulandelayo.

# Validation errors
milebymile-error-karma-needs-three-teams = Umthetho we-karma udinga okungenani izimoto/amathimba amathathu ahlukene.

milebymile-you-play-safety-with-effect = Udlala i-{ $card }. { $effect }
milebymile-player-plays-safety-with-effect = U-{ $player } udlala i-{ $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Udlala i-{ $card } njengeQhinga Elingcolile. { $effect }
milebymile-player-plays-dirty-trick-with-effect = U-{ $player } udlala i-{ $card } njengeQhinga Elingcolile. { $effect }
milebymile-safety-effect-extra-tank = Manje uvikelekile kuKuphele Uphethiloli.
milebymile-safety-effect-puncture-proof = Manje uvikelekile ekuPuncture.
milebymile-safety-effect-driving-ace = Manje uvikelekile engozini.
milebymile-safety-effect-right-of-way = Manje uvikelekile kuStop nakuMkhawulo Wejubane.
