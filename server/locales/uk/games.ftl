# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Дев'яносто дев'ять

# Round and turn flow
game-round-start = Раунд { $round }.
game-round-end = Раунд { $round } завершено.
game-turn-start = Хід { $player }.
game-your-turn = Ваш хід.
game-no-turn = Зараз нічий хід.

# Score display
game-scores-header = Поточні рахунки:
game-score-line = { $player }: { $score } очок
game-final-scores-header = Фінальні рахунки:

# Win/loss
game-winner = { $player } виграє!
game-winner-score = { $player } виграє з { $score } очками!
game-tiebreaker = Нічия! Додатковий раунд!
game-tiebreaker-players = Нічия між { $players }! Додатковий раунд!
game-eliminated = { $player } вибув з { $score } очками.

# Common options
game-set-target-score = Цільовий рахунок: { $score }
game-enter-target-score = Введіть цільовий рахунок:
game-option-changed-target = Цільовий рахунок встановлено на { $score }.

game-set-team-mode = Командний режим: { $mode }
game-select-team-mode = Виберіть командний режим
game-option-changed-team = Командний режим встановлено на { $mode }.
game-team-mode-individual = Індивідуальний
game-team-mode-x-teams-of-y = { $num_teams } команд по { $team_size }

# Boolean option values
option-on = увімкнено
option-off = вимкнено

# Status box

# Game end
game-leave = Покинути гру

# Round timer
round-timer-paused = { $player } призупинив гру (натисніть p, щоб почати наступний раунд).
round-timer-resumed = Таймер раунду відновлено.
round-timer-countdown = Наступний раунд через { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Зберігаємо { $value }.
dice-rerolling = Перекидаємо { $value }.
dice-locked = Цей кубик заблокований і не може бути змінений.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Роздача { $current }/{ $total }.
game-you-deal = Ви роздаєте карти.
game-player-deals = { $player } роздає карти.

# Card names
card-name = { $rank } { $suit }
no-cards = Немає карт

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = чорний
color-black-m = чорний
color-black-f = чорна
color-blue = синій
color-blue-m = синій
color-blue-f = синя
color-brown = коричневий
color-brown-m = коричневий
color-brown-f = коричнева
color-gray = сірий
color-gray-m = сірий
color-gray-f = сіра
color-green = зелений
color-green-m = зелений
color-green-f = зелена
color-indigo = індиго
color-indigo-m = індиго
color-indigo-f = індиго
color-orange = помаранчевий
color-orange-m = помаранчевий
color-orange-f = помаранчева
color-pink = рожевий
color-pink-m = рожевий
color-pink-f = рожева
color-purple = пурпурний
color-purple-m = пурпурний
color-purple-f = пурпурна
color-red = червоний
color-red-m = червоний
color-red-f = червона
color-violet = фіолетовий
color-violet-m = фіолетовий
color-violet-f = фіолетова
color-white = білий
color-white-m = білий
color-white-f = біла
color-yellow = жовтий
color-yellow-m = жовтий
color-yellow-f = жовта

# Suit names
suit-diamonds = бубни
suit-clubs = трефи
suit-hearts = черви
suit-spades = піки

# Rank names
rank-ace = туз
rank-ace-plural = тузи
rank-two = 2
rank-two-plural = двійки
rank-three = 3
rank-three-plural = трійки
rank-four = 4
rank-four-plural = четвірки
rank-five = 5
rank-five-plural = п'ятірки
rank-six = 6
rank-six-plural = шістки
rank-seven = 7
rank-seven-plural = сімки
rank-eight = 8
rank-eight-plural = вісімки
rank-nine = 9
rank-nine-plural = дев'ятки
rank-ten = 10
rank-ten-plural = десятки
rank-jack = валет
rank-jack-plural = валети
rank-queen = дама
rank-queen-plural = дами
rank-king = король
rank-king-plural = королі

# Poker hand descriptions
poker-high-card-with = Старша { $high }, з { $rest }
poker-high-card = Старша { $high }
poker-pair-with = Пара { $pair }, з { $rest }
poker-pair = Пара { $pair }
poker-two-pair-with = Дві пари, { $high } і { $low }, з { $kicker }
poker-two-pair = Дві пари, { $high } і { $low }
poker-trips-with = Трійка, { $trips }, з { $rest }
poker-trips = Трійка, { $trips }
poker-straight-high = Стріт до { $high }
poker-flush-high-with = Флеш до { $high }, з { $rest }
poker-full-house = Фул-хаус, { $trips } над { $pair }
poker-quads-with = Каре, { $quads }, з { $kicker }
poker-quads = Каре, { $quads }
poker-straight-flush-high = Стріт-флеш до { $high }
poker-unknown-hand = Невідома комбінація

# Validation errors (common across games)
game-error-invalid-team-mode = Вибраний командний режим недійсний для поточної кількості гравців.
