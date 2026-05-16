# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Deväťdesiatdeväť

# Round and turn flow
game-round-start = Kolo { $round }.
game-round-end = Kolo { $round } dokončené.
game-turn-start = { $player } je na ťahu.
game-your-turn = Si na ťahu.
game-no-turn = Momentálne nie je nikto na ťahu.

# Score display
game-scores-header = Aktuálne skóre:
game-score-line = { $player }: { $score } bodov
game-final-scores-header = Konečné skóre:

# Win/loss
game-winner = { $player } vyhráva!
game-winner-score = { $player } vyhráva s { $score } bodmi!
game-tiebreaker = Je to remíza! Rozhodujúce kolo!
game-tiebreaker-players = Je to remíza medzi { $players }! Rozhodujúce kolo!
game-eliminated = { $player } bol/a vyradený/á s { $score } bodmi.

# Common options
game-set-target-score = Cieľové skóre: { $score }
game-enter-target-score = Zadajte cieľové skóre:
game-option-changed-target = Cieľové skóre nastavené na { $score }.

game-set-team-mode = Tímový režim: { $mode }
game-select-team-mode = Vyberte tímový režim
game-option-changed-team = Tímový režim nastavený na { $mode }.
game-team-mode-individual = Individuálny
game-team-mode-x-teams-of-y = { $num_teams } tímov po { $team_size }

# Boolean option values
option-on = zapnuté
option-off = vypnuté

# Status box

# Game end
game-leave = Opustiť hru

# Round timer
round-timer-paused = { $player } pozastavil/a hru (stlačte p pre spustenie ďalšieho kola).
round-timer-resumed = Časovač kola obnovený.
round-timer-countdown = Ďalšie kolo za { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Ponechávam { $value }.
dice-rerolling = Prehodím { $value }.
dice-locked = Táto kocka je uzamknutá a nemožno ju zmeniť.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Rozdávanie { $current }/{ $total }.
game-you-deal = Ty rozdávaš karty.
game-player-deals = { $player } rozdáva karty.

# Card names
card-name = { $rank } { $suit }
no-cards = Žiadne karty

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = čierna
color-black-m = čierny
color-black-f = čierna
color-blue = modrá
color-blue-m = modrý
color-blue-f = modrá
color-brown = hnedá
color-brown-m = hnedý
color-brown-f = hnedá
color-gray = šedá
color-gray-m = šedý
color-gray-f = šedá
color-green = zelená
color-green-m = zelený
color-green-f = zelená
color-indigo = indigo
color-indigo-m = indigo
color-indigo-f = indigo
color-orange = oranžová
color-orange-m = oranžový
color-orange-f = oranžová
color-pink = ružová
color-pink-m = ružový
color-pink-f = ružová
color-purple = purpurová
color-purple-m = purpurový
color-purple-f = purpurová
color-red = červená
color-red-m = červený
color-red-f = červená
color-violet = fialová
color-violet-m = fialový
color-violet-f = fialová
color-white = biela
color-white-m = biely
color-white-f = biela
color-yellow = žltá
color-yellow-m = žltý
color-yellow-f = žltá

# Suit names
suit-diamonds = káro
suit-clubs = krížiky
suit-hearts = srdcia
suit-spades = píky

# Rank names
rank-ace = eso
rank-ace-plural = esá
rank-two = 2
rank-two-plural = dvojky
rank-three = 3
rank-three-plural = trojky
rank-four = 4
rank-four-plural = štvorky
rank-five = 5
rank-five-plural = päťky
rank-six = 6
rank-six-plural = šestky
rank-seven = 7
rank-seven-plural = sedmičky
rank-eight = 8
rank-eight-plural = osmičky
rank-nine = 9
rank-nine-plural = deviatky
rank-ten = 10
rank-ten-plural = desiatky
rank-jack = dolník
rank-jack-plural = dolníky
rank-queen = dáma
rank-queen-plural = dámy
rank-king = kráľ
rank-king-plural = králi

# Poker hand descriptions
poker-high-card-with = { $high } vysoká, s { $rest }
poker-high-card = { $high } vysoká
poker-pair-with = Pár { $pair }, s { $rest }
poker-pair = Pár { $pair }
poker-two-pair-with = Dva páry, { $high } a { $low }, s { $kicker }
poker-two-pair = Dva páry, { $high } a { $low }
poker-trips-with = Trojica, { $trips }, s { $rest }
poker-trips = Trojica, { $trips }
poker-straight-high = { $high } vysoký pokerový postup
poker-flush-high-with = { $high } vysoký flush, s { $rest }
poker-full-house = Full house, { $trips } nad { $pair }
poker-quads-with = Štvorica, { $quads }, s { $kicker }
poker-quads = Štvorica, { $quads }
poker-straight-flush-high = { $high } vysoký pokerový postup v jednej farbe
poker-unknown-hand = Neznáme karty

# Validation errors (common across games)
game-error-invalid-team-mode = Vybraný tímový režim nie je platný pre aktuálny počet hráčov.
