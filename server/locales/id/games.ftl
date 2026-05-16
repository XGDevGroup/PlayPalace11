# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Ninety Nine

# Round and turn flow
game-round-start = Ronde { $round }.
game-round-end = Ronde { $round } selesai.
game-turn-start = Giliran { $player }.
game-your-turn = Giliran Anda.
game-no-turn = Tidak ada giliran sekarang.

# Score display
game-scores-header = Skor Saat Ini:
game-score-line = { $player }: { $score } poin
game-final-scores-header = Skor Akhir:

# Win/loss
game-winner = { $player } menang!
game-winner-score = { $player } menang dengan { $score } poin!
game-tiebreaker = Seri! Ronde tiebreaker!
game-tiebreaker-players = Seri antara { $players }! Ronde tiebreaker!
game-eliminated = { $player } telah dieliminasi dengan { $score } poin.

# Common options
game-set-target-score = Skor target: { $score }
game-enter-target-score = Masukkan skor target:
game-option-changed-target = Skor target diatur ke { $score }.

game-set-team-mode = Mode tim: { $mode }
game-select-team-mode = Pilih mode tim
game-option-changed-team = Mode tim diatur ke { $mode }.
game-team-mode-individual = Individual
game-team-mode-x-teams-of-y = { $num_teams } tim dari { $team_size }

# Boolean option values
option-on = aktif
option-off = nonaktif

# Status box

# Game end
game-leave = Tinggalkan permainan

# Round timer
round-timer-paused = { $player } telah menjeda permainan (tekan p untuk memulai ronde berikutnya).
round-timer-resumed = Timer ronde dilanjutkan.
round-timer-countdown = Ronde berikutnya dalam { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Menyimpan { $value }.
dice-rerolling = Melempar ulang { $value }.
dice-locked = Dadu itu terkunci dan tidak dapat diubah.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Bagikan { $current }/{ $total }.
game-you-deal = Anda membagikan kartu.
game-player-deals = { $player } membagikan kartu.

# Card names
card-name = { $rank } { $suit }
no-cards = Tidak ada kartu

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = hitam
color-black-m = hitam
color-black-f = hitam
color-blue = biru
color-blue-m = biru
color-blue-f = biru
color-brown = cokelat
color-brown-m = cokelat
color-brown-f = cokelat
color-gray = abu-abu
color-gray-m = abu-abu
color-gray-f = abu-abu
color-green = hijau
color-green-m = hijau
color-green-f = hijau
color-indigo = nila
color-indigo-m = nila
color-indigo-f = nila
color-orange = oranye
color-orange-m = oranye
color-orange-f = oranye
color-pink = merah muda
color-pink-m = merah muda
color-pink-f = merah muda
color-purple = ungu
color-purple-m = ungu
color-purple-f = ungu
color-red = merah
color-red-m = merah
color-red-f = merah
color-violet = violet
color-violet-m = violet
color-violet-f = violet
color-white = putih
color-white-m = putih
color-white-f = putih
color-yellow = kuning
color-yellow-m = kuning
color-yellow-f = kuning

# Suit names
suit-diamonds = wajik
suit-clubs = keriting
suit-hearts = hati
suit-spades = sekop

# Rank names
rank-ace = as
rank-ace-plural = as
rank-two = 2
rank-two-plural = 2
rank-three = 3
rank-three-plural = 3
rank-four = 4
rank-four-plural = 4
rank-five = 5
rank-five-plural = 5
rank-six = 6
rank-six-plural = 6
rank-seven = 7
rank-seven-plural = 7
rank-eight = 8
rank-eight-plural = 8
rank-nine = 9
rank-nine-plural = 9
rank-ten = 10
rank-ten-plural = 10
rank-jack = jack
rank-jack-plural = jack
rank-queen = queen
rank-queen-plural = queen
rank-king = king
rank-king-plural = king

# Poker hand descriptions
poker-high-card-with = { $high } tinggi, dengan { $rest }
poker-high-card = { $high } tinggi
poker-pair-with = Pasangan { $pair }, dengan { $rest }
poker-pair = Pasangan { $pair }
poker-two-pair-with = Dua Pasangan, { $high } dan { $low }, dengan { $kicker }
poker-two-pair = Dua Pasangan, { $high } dan { $low }
poker-trips-with = Three of a Kind, { $trips }, dengan { $rest }
poker-trips = Three of a Kind, { $trips }
poker-straight-high = Straight { $high } tinggi
poker-flush-high-with = Flush { $high } tinggi, dengan { $rest }
poker-full-house = Full House, { $trips } over { $pair }
poker-quads-with = Four of a Kind, { $quads }, dengan { $kicker }
poker-quads = Four of a Kind, { $quads }
poker-straight-flush-high = Straight Flush { $high } tinggi
poker-unknown-hand = Tangan tidak diketahui

# Validation errors (common across games)
game-error-invalid-team-mode = Mode tim yang dipilih tidak valid untuk jumlah pemain saat ini.
