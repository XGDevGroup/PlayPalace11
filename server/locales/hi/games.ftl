# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = नाइंटी नाइन

# Round and turn flow
game-round-start = राउंड { $round }।
game-round-end = राउंड { $round } पूरा।
game-turn-start = { $player } की बारी।
game-your-turn = आपकी बारी।
game-no-turn = अभी किसी की बारी नहीं।

# Score display
game-scores-header = वर्तमान स्कोर:
game-score-line = { $player }: { $score } अंक
game-final-scores-header = अंतिम स्कोर:

# Win/loss
game-winner = { $player } जीतते हैं!
game-winner-score = { $player } { $score } अंकों के साथ जीतते हैं!
game-tiebreaker = बराबरी है! टाइब्रेकर राउंड!
game-tiebreaker-players = { $players } के बीच बराबरी है! टाइब्रेकर राउंड!
game-eliminated = { $player } { $score } अंकों के साथ बाहर हो गए हैं।

# Common options
game-set-target-score = लक्ष्य स्कोर: { $score }
game-enter-target-score = लक्ष्य स्कोर दर्ज करें:
game-option-changed-target = लक्ष्य स्कोर { $score } पर सेट किया गया।

game-set-team-mode = टीम मोड: { $mode }
game-select-team-mode = टीम मोड चुनें
game-option-changed-team = टीम मोड { $mode } पर सेट किया गया।
game-team-mode-individual = व्यक्तिगत
game-team-mode-x-teams-of-y = { $team_size } की { $num_teams } टीमें

# Boolean option values
option-on = चालू
option-off = बंद

# Status box

# Game end
game-leave = खेल छोड़ें

# Round timer
round-timer-paused = { $player } ने खेल को रोक दिया है (अगला राउंड शुरू करने के लिए p दबाएं)।
round-timer-resumed = राउंड टाइमर फिर से शुरू हुआ।
round-timer-countdown = अगला राउंड { $seconds } में...

# Dice games - keeping/releasing dice
dice-keeping = { $value } को रख रहे हैं।
dice-rerolling = { $value } को फिर से रोल कर रहे हैं।
dice-locked = वह पासा बंद है और बदला नहीं जा सकता।
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = बांटें { $current }/{ $total }।
game-you-deal = आप पत्ते बांटते हैं।
game-player-deals = { $player } पत्ते बांटते हैं।

# Card names
card-name = { $suit } का { $rank }
no-cards = कोई पत्ते नहीं

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = काला
color-black-m = काला
color-black-f = काली
color-blue = नीला
color-blue-m = नीला
color-blue-f = नीली
color-brown = भूरा
color-brown-m = भूरा
color-brown-f = भूरी
color-gray = धूसर
color-gray-m = धूसर
color-gray-f = धूसर
color-green = हरा
color-green-m = हरा
color-green-f = हरी
color-indigo = नील
color-indigo-m = नील
color-indigo-f = नील
color-orange = नारंगी
color-orange-m = नारंगी
color-orange-f = नारंगी
color-pink = गुलाबी
color-pink-m = गुलाबी
color-pink-f = गुलाबी
color-purple = बैंगनी
color-purple-m = बैंगनी
color-purple-f = बैंगनी
color-red = लाल
color-red-m = लाल
color-red-f = लाल
color-violet = बैंगनी
color-violet-m = बैंगनी
color-violet-f = बैंगनी
color-white = सफ़ेद
color-white-m = सफ़ेद
color-white-f = सफ़ेद
color-yellow = पीला
color-yellow-m = पीला
color-yellow-f = पीली

# Suit names
suit-diamonds = हीरा
suit-clubs = चिड़ी
suit-hearts = पान
suit-spades = हुकुम

# Rank names
rank-ace = इक्का
rank-ace-plural = इक्के
rank-two = 2
rank-two-plural = 2s
rank-three = 3
rank-three-plural = 3s
rank-four = 4
rank-four-plural = 4s
rank-five = 5
rank-five-plural = 5s
rank-six = 6
rank-six-plural = 6s
rank-seven = 7
rank-seven-plural = 7s
rank-eight = 8
rank-eight-plural = 8s
rank-nine = 9
rank-nine-plural = 9s
rank-ten = 10
rank-ten-plural = 10s
rank-jack = गुलाम
rank-jack-plural = गुलाम
rank-queen = बेगम
rank-queen-plural = बेगम
rank-king = बादशाह
rank-king-plural = बादशाह

# Poker hand descriptions
poker-high-card-with = { $high } हाई, { $rest } के साथ
poker-high-card = { $high } हाई
poker-pair-with = { $pair } की जोड़ी, { $rest } के साथ
poker-pair = { $pair } की जोड़ी
poker-two-pair-with = दो जोड़ी, { $high } और { $low }, { $kicker } के साथ
poker-two-pair = दो जोड़ी, { $high } और { $low }
poker-trips-with = तीन एक तरह के, { $trips }, { $rest } के साथ
poker-trips = तीन एक तरह के, { $trips }
poker-straight-high = { $high } हाई स्ट्रेट
poker-flush-high-with = { $high } हाई फ्लश, { $rest } के साथ
poker-full-house = फुल हाउस, { $trips } { $pair } के ऊपर
poker-quads-with = चार एक तरह के, { $quads }, { $kicker } के साथ
poker-quads = चार एक तरह के, { $quads }
poker-straight-flush-high = { $high } हाई स्ट्रेट फ्लश
poker-unknown-hand = अज्ञात हाथ

# Validation errors (common across games)
game-error-invalid-team-mode = चयनित टीम मोड वर्तमान खिलाड़ियों की संख्या के लिए मान्य नहीं है।
