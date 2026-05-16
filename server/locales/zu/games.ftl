# Shared game messages for PlayPalace (isiZulu)
# Imiyalezo ejwayelekile emidlalweni eminingi

# Game names
game-name-ninetynine = Ninety Nine

# Round and turn flow
game-round-start = Umjikelezo { $round }.
game-round-end = Umjikelezo { $round } uphelile.
game-turn-start = Ishintshi lika-{ $player }.
game-your-turn = Ishintshi lakho.
game-no-turn = Ayikho ishintshi lamuntu njengamanje.

# Score display
game-scores-header = Amaphuzu Amanje:
game-score-line = { $player }: { $score } amaphuzu
game-final-scores-header = Amaphuzu Okugcina:

# Win/loss
game-winner = U-{ $player } uyawina!
game-winner-score = U-{ $player } uyawina ngamaphuzu angu-{ $score }!
game-tiebreaker = Kuyalinganiswa! Umjikelezo wokuphula ukulinganiswa!
game-tiebreaker-players = Kuyalinganiswa phakathi kuka-{ $players }! Umjikelezo wokuphula ukulinganiswa!
game-eliminated = U-{ $player } ukhishiwe ngamaphuzu angu-{ $score }.

# Common options
game-set-target-score = Amaphuzu ahlosiwe: { $score }
game-enter-target-score = Faka amaphuzu ahlosiwe:
game-option-changed-target = Amaphuzu ahlosiwe asetelwe ku-{ $score }.

game-set-team-mode = Imodi yethimba: { $mode }
game-select-team-mode = Khetha imodi yethimba
game-option-changed-team = Imodi yethimba isetelwe ku-{ $mode }.
game-team-mode-individual = Ngamunye
game-team-mode-x-teams-of-y = Amathimba angu-{ $num_teams } obu-{ $team_size }

# Boolean option values
option-on = ivuliwe
option-off = ivaliwe

# Status box

# Game end
game-leave = Shiya umdlalo

# Round timer
round-timer-paused = U-{ $player } umise umdlalo (cindezela i-p ukuze uqale umjikelezo olandelayo).
round-timer-resumed = Isikhathi somjikelezo siqhubekile.
round-timer-countdown = Umjikelezo olandelayo kumasekhondi angu-{ $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Kugcinwa { $value }.
dice-rerolling = Kuphonswa kabusha { $value }.
dice-locked = Lelo dayisi livalwe futhi alikwazi ukushintshwa.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Ukwabela { $current }/{ $total }.
game-you-deal = Wena wabela amakhadi.
game-player-deals = U-{ $player } wabela amakhadi.

# Card names
card-name = { $rank } we-{ $suit }
no-cards = Awekho amakhadi

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = mnyama
color-black-m = mnyama
color-black-f = mnyama
color-blue = luhlaza okwesibhakabhaka
color-blue-m = luhlaza okwesibhakabhaka
color-blue-f = luhlaza okwesibhakabhaka
color-brown = nsundu
color-brown-m = nsundu
color-brown-f = nsundu
color-gray = mpunga
color-gray-m = mpunga
color-gray-f = mpunga
color-green = luhlaza
color-green-m = luhlaza
color-green-f = luhlaza
color-indigo = indigo
color-indigo-m = indigo
color-indigo-f = indigo
color-orange = orenji
color-orange-m = orenji
color-orange-f = orenji
color-pink = pinki
color-pink-m = pinki
color-pink-f = pinki
color-purple = mfusa
color-purple-m = mfusa
color-purple-f = mfusa
color-red = bomvu
color-red-m = bomvu
color-red-f = bomvu
color-violet = violethi
color-violet-m = violethi
color-violet-f = violethi
color-white = mhlophe
color-white-m = mhlophe
color-white-f = mhlophe
color-yellow = phuzi
color-yellow-m = phuzi
color-yellow-f = phuzi

# Suit names
suit-diamonds = amadayimane
suit-clubs = amaklabhu
suit-hearts = izinhliziyo
suit-spades = amaspeyidi

# Rank names
rank-ace = i-ace
rank-ace-plural = ama-aces
rank-two = u-2
rank-two-plural = ama-2
rank-three = u-3
rank-three-plural = ama-3
rank-four = u-4
rank-four-plural = ama-4
rank-five = u-5
rank-five-plural = ama-5
rank-six = u-6
rank-six-plural = ama-6
rank-seven = u-7
rank-seven-plural = ama-7
rank-eight = u-8
rank-eight-plural = ama-8
rank-nine = u-9
rank-nine-plural = ama-9
rank-ten = u-10
rank-ten-plural = ama-10
rank-jack = i-jack
rank-jack-plural = ama-jacks
rank-queen = i-queen
rank-queen-plural = ama-queens
rank-king = i-king
rank-king-plural = ama-kings

# Poker hand descriptions
poker-high-card-with = { $high } ephezulu, no-{ $rest }
poker-high-card = { $high } ephezulu
poker-pair-with = Ipheya le-{ $pair }, no-{ $rest }
poker-pair = Ipheya le-{ $pair }
poker-two-pair-with = Amapheya Amabili, { $high } no-{ $low }, no-{ $kicker }
poker-two-pair = Amapheya Amabili, { $high } no-{ $low }
poker-trips-with = Amathathu Ohlobo Olulodwa, { $trips }, no-{ $rest }
poker-trips = Amathathu Ohlobo Olulodwa, { $trips }
poker-straight-high = Ukulandelana okuphezulu kwe-{ $high }
poker-flush-high-with = Ukugcwala okuphezulu kwe-{ $high }, no-{ $rest }
poker-full-house = Indlu Egcwele, { $trips } phezu kwe-{ $pair }
poker-quads-with = Amane Ohlobo Olulodwa, { $quads }, no-{ $kicker }
poker-quads = Amane Ohlobo Olulodwa, { $quads }
poker-straight-flush-high = Ukugcwala Nokulandelana okuphezulu kwe-{ $high }
poker-unknown-hand = Isandla esingaziwa

# Validation errors (common across games)
game-error-invalid-team-mode = Imodi yethimba ekhethiwe ayivumelekile ngenani labadlali lamanje.
