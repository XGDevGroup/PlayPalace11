# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Mile by Mile

# Game options
milebymile-set-distance = Jarak balapan: { $miles } mil
milebymile-enter-distance = Masukkan jarak balapan (300-3000)
milebymile-set-winning-score = Skor kemenangan: { $score } poin
milebymile-enter-winning-score = Masukkan skor kemenangan (1000-10000)
milebymile-toggle-perfect-crossing = Memerlukan finish tepat: { $enabled }
milebymile-toggle-stacking = Izinkan serangan bertumpuk: { $enabled }
milebymile-toggle-reshuffle = Kocok ulang tumpukan buangan: { $enabled }
milebymile-toggle-karma = Aturan karma: { $enabled }
milebymile-set-rig = Kecurangan dek: { $rig }
milebymile-select-rig = Pilih opsi kecurangan dek

# Option change announcements
milebymile-option-changed-distance = Jarak balapan diatur ke { $miles } mil.
milebymile-option-changed-winning = Skor kemenangan diatur ke { $score } poin.
milebymile-option-changed-crossing = Memerlukan finish tepat { $enabled }.
milebymile-option-changed-stacking = Izinkan serangan bertumpuk { $enabled }.
milebymile-option-changed-reshuffle = Kocok ulang tumpukan buangan { $enabled }.
milebymile-option-changed-karma = Aturan karma { $enabled }.
milebymile-option-changed-rig = Kecurangan dek diatur ke { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } poin, { $miles } mil, Masalah: { $problems }, Keselamatan: { $safeties }

# Card actions
milebymile-no-matching-safety = Anda tidak memiliki kartu keselamatan yang sesuai!
milebymile-cant-play = Anda tidak dapat memainkan { $card } karena { $reason }.
milebymile-no-card-selected = Tidak ada kartu yang dipilih untuk dibuang.
milebymile-no-valid-targets = Tidak ada target yang valid untuk bahaya ini!
milebymile-you-drew = Anda mengambil: { $card }
milebymile-discards = { $player } membuang kartu.
milebymile-select-target = Pilih target

# Distance plays
milebymile-plays-distance-individual = { $player } memainkan { $distance } mil, dan sekarang di { $total } mil.
milebymile-plays-distance-team = { $player } memainkan { $distance } mil; tim mereka sekarang di { $total } mil.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } telah menyelesaikan perjalanan dengan penyeberangan sempurna!
milebymile-journey-complete-perfect-team = Tim { $team } telah menyelesaikan perjalanan dengan penyeberangan sempurna!
milebymile-journey-complete-individual = { $player } telah menyelesaikan perjalanan!
milebymile-journey-complete-team = Tim { $team } telah menyelesaikan perjalanan!

# Hazard plays
milebymile-plays-hazard-individual = { $player } memainkan { $card } pada { $target }.
milebymile-plays-hazard-team = { $player } memainkan { $card } pada Tim { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } memainkan { $card }.
milebymile-plays-dirty-trick = { $player } memainkan { $card } sebagai Trik Kotor!

# Deck
milebymile-deck-reshuffled = Tumpukan buangan dikocok kembali ke dek.

# Race
milebymile-new-race = Balapan baru dimulai!
milebymile-race-complete = Balapan selesai! Menghitung skor...
milebymile-earned-points = { $name } mendapat { $score } poin di balapan ini: { $breakdown }.
milebymile-total-scores = Total skor:
milebymile-team-score = { $name }: { $score } poin

# Scoring breakdown
milebymile-from-distance = { $miles } dari jarak yang ditempuh
milebymile-from-trip = { $points } dari menyelesaikan perjalanan
milebymile-from-perfect = { $points } dari penyeberangan sempurna
milebymile-from-safe = { $points } dari perjalanan aman
milebymile-from-shutout = { $points } dari shut out
milebymile-from-safeties = { $points } dari { $count } { $safeties ->
    [one] keselamatan
    *[other] keselamatan
}
milebymile-from-all-safeties = { $points } dari semua 4 keselamatan
milebymile-from-dirty-tricks = { $points } dari { $count } { $tricks ->
    [one] trik kotor
    *[other] trik kotor
}

# Game end
milebymile-wins-individual = { $player } memenangkan permainan!
milebymile-wins-team = Tim { $team } memenangkan permainan! ({ $members })
milebymile-final-score = Skor akhir: { $score } poin

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Anda dan target Anda sama-sama dicemooh! Serangan dinetralkan.
milebymile-karma-clash-you-attacker = Anda dan { $attacker } sama-sama dicemooh! Serangan dinetralkan.
milebymile-karma-clash-others = { $attacker } dan { $target } sama-sama dicemooh! Serangan dinetralkan.
milebymile-karma-clash-your-team = Tim Anda dan target Anda sama-sama dicemooh! Serangan dinetralkan.
milebymile-karma-clash-target-team = Anda dan Tim { $team } sama-sama dicemooh! Serangan dinetralkan.
milebymile-karma-clash-other-teams = Tim { $attacker } dan Tim { $target } sama-sama dicemooh! Serangan dinetralkan.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Anda telah dicemooh karena agresi Anda! Karma Anda hilang.
milebymile-karma-shunned-other = { $player } telah dicemooh karena agresi mereka!
milebymile-karma-shunned-your-team = Tim Anda telah dicemooh karena agresinya! Karma tim Anda hilang.
milebymile-karma-shunned-other-team = Tim { $team } telah dicemooh karena agresinya!

# False Virtue
milebymile-false-virtue-you = Anda memainkan False Virtue dan mendapatkan kembali karma Anda!
milebymile-false-virtue-other = { $player } memainkan False Virtue dan mendapatkan kembali karma mereka!
milebymile-false-virtue-your-team = Tim Anda memainkan False Virtue dan mendapatkan kembali karmanya!
milebymile-false-virtue-other-team = Tim { $team } memainkan False Virtue dan mendapatkan kembali karmanya!

# Problems/Safeties (for status display)
milebymile-none = tidak ada

# Unplayable card reasons
milebymile-reason-not-on-team = Anda tidak dalam tim
milebymile-reason-stopped = Anda berhenti
milebymile-reason-has-problem = Anda memiliki masalah yang mencegah mengemudi
milebymile-reason-speed-limit = batas kecepatan aktif
milebymile-reason-exceeds-distance = akan melebihi { $miles } mil
milebymile-reason-no-targets = tidak ada target yang valid
milebymile-reason-no-speed-limit = Anda tidak di bawah batas kecepatan
milebymile-reason-has-right-of-way = Right of Way memungkinkan Anda pergi tanpa lampu hijau
milebymile-reason-already-moving = Anda sudah bergerak
milebymile-reason-must-fix-first = Anda harus memperbaiki { $problem } terlebih dahulu
milebymile-reason-has-gas = mobil Anda memiliki bensin
milebymile-reason-tires-fine = ban Anda baik-baik saja
milebymile-reason-no-accident = mobil Anda tidak mengalami kecelakaan
milebymile-reason-has-safety = Anda sudah memiliki keselamatan itu
milebymile-reason-has-karma = Anda masih memiliki karma Anda
milebymile-reason-generic = tidak dapat dimainkan sekarang

# Card names
milebymile-card-out-of-gas = Out of Gas
milebymile-card-flat-tire = Flat Tire
milebymile-card-accident = Accident
milebymile-card-speed-limit = Speed Limit
milebymile-card-stop = Stop
milebymile-card-gasoline = Gasoline
milebymile-card-spare-tire = Spare Tire
milebymile-card-repairs = Repairs
milebymile-card-end-of-limit = End of Limit
milebymile-card-green-light = Green Light
milebymile-card-extra-tank = Extra Tank
milebymile-card-puncture-proof = Puncture Proof
milebymile-card-driving-ace = Driving Ace
milebymile-card-right-of-way = Right of Way
milebymile-card-false-virtue = False Virtue
milebymile-card-miles = { $miles } mil

# Disabled action reasons
milebymile-no-dirty-trick-window = Tidak ada jendela trik kotor yang aktif.
milebymile-not-your-dirty-trick = Bukan jendela trik kotor tim Anda.
milebymile-between-races = Tunggu balapan berikutnya untuk dimulai.

# Validation errors
milebymile-error-karma-needs-three-teams = Aturan karma memerlukan setidaknya 3 mobil/tim yang berbeda.

milebymile-you-play-safety-with-effect = Kamu memainkan { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } memainkan { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Kamu memainkan { $card } sebagai Trik Kotor. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } memainkan { $card } sebagai Trik Kotor. { $effect }
milebymile-safety-effect-extra-tank = Sekarang terlindungi dari Kehabisan Bensin.
milebymile-safety-effect-puncture-proof = Sekarang terlindungi dari Ban Kempis.
milebymile-safety-effect-driving-ace = Sekarang terlindungi dari Kecelakaan.
milebymile-safety-effect-right-of-way = Sekarang terlindungi dari Berhenti dan Batas Kecepatan.
