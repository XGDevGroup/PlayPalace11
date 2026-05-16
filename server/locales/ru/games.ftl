# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = Девяносто девять

# Round and turn flow
game-round-start = Раунд { $round }.
game-round-end = Раунд { $round } завершён.
game-turn-start = Ход игрока { $player }.
game-your-turn = Ваш ход.
game-no-turn = Сейчас никто не ходит.

# Score display
game-scores-header = Текущий счёт:
game-score-line = { $player }: { $score } { $score ->
    [one] очко
    [few] очка
   *[other] очков
}
game-final-scores-header = Итоговый счёт:

# Win/loss
game-winner = { $player } побеждает!
game-winner-score = { $player } побеждает, набрав { $score } { $score ->
    [one] очко
    [few] очка
   *[other] очков
}!
game-tiebreaker = Ничья! Раунд для определения победителя!
game-tiebreaker-players = Ничья между игроками: { $players }! Раунд для определения победителя!
game-eliminated = Игрок { $player } выбывает из игры с результатом { $score } { $score ->
    [one] очко
    [few] очка
   *[other] очков
}.

# Common options
game-set-target-score = Конечный счёт: { $score }
game-enter-target-score = Введите конечный счёт:
game-option-changed-target = Конечный счёт установлен на { $score }.

game-set-team-mode = Командный режим: { $mode }
game-select-team-mode = Выберите командный режим
game-option-changed-team = Командный режим изменён на { $mode }.
game-team-mode-individual = Индивидуальный
game-team-mode-x-teams-of-y = { $num_teams } { $num_teams ->
    [one] команда
    [few] команды
   *[other] команд
} по { $team_size } { $team_size ->
    [one] игроку
    [few] игрока
   *[other] игроков
}

# Boolean option values
option-on = вкл.
option-off = выкл.
option-back = Назад
option-min-selected = Нужно выбрать как минимум { $count } { $count ->
    [one] вариант
    [few] варианта
   *[other] вариантов
}.
option-max-selected = Можно выбрать не более { $count } { $count ->
    [one] варианта
    [few] вариантов
   *[other] вариантов
}.

# Status box

# Game end
game-leave = Покинуть игру

# Round timer
round-timer-paused = Игрок { $player } поставил игру на паузу (нажмите «p», чтобы начать следующий раунд).
round-timer-resumed = Таймер раунда возобновлён.
round-timer-countdown = Следующий раунд через { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = Оставляем: { $value }.
dice-rerolling = Перебрасываем: { $value }.
dice-locked = Этот кубик заблокирован, его нельзя изменить.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = Раздача { $current }/{ $total }.
game-you-deal = Вы раздаёте карты.
game-player-deals = { $player } раздаёт карты.

# Card names
card-name = { $rank } { $suit }
no-cards = Нет карт

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = чёрный
color-black-m = чёрный
color-black-f = чёрная
color-blue = синий
color-blue-m = синий
color-blue-f = синяя
color-brown = коричневый
color-brown-m = коричневый
color-brown-f = коричневая
color-gray = серый
color-gray-m = серый
color-gray-f = серая
color-green = зелёный
color-green-m = зелёный
color-green-f = зелёная
color-indigo = индиго
color-indigo-m = индиго
color-indigo-f = индиго
color-orange = оранжевый
color-orange-m = оранжевый
color-orange-f = оранжевая
color-pink = розовый
color-pink-m = розовый
color-pink-f = розовая
color-purple = пурпурный
color-purple-m = пурпурный
color-purple-f = пурпурная
color-red = красный
color-red-m = красный
color-red-f = красная
color-violet = фиолетовый
color-violet-m = фиолетовый
color-violet-f = фиолетовая
color-white = белый
color-white-m = белый
color-white-f = белая
color-yellow = жёлтый
color-yellow-m = жёлтый
color-yellow-f = жёлтая

# Suit names (in genitive plural for phrases like "Ace of clubs" -> "Туз треф")
suit-diamonds = бубен
suit-clubs = треф
suit-hearts = червей
suit-spades = пик

# Rank names
rank-ace = Туз
rank-ace-plural = Тузов
rank-two = Двойка
rank-two-plural = Двоек
rank-three = Тройка
rank-three-plural = Троек
rank-four = Четвёрка
rank-four-plural = Четвёрок
rank-five = Пятёрка
rank-five-plural = Пятёрок
rank-six = Шестёрка
rank-six-plural = Шестёрок
rank-seven = Семёрка
rank-seven-plural = Семёрок
rank-eight = Восьмёрка
rank-eight-plural = Восьмёрок
rank-nine = Девятка
rank-nine-plural = Девяток
rank-ten = Десятка
rank-ten-plural = Десяток
rank-jack = Валет
rank-jack-plural = Валетов
rank-queen = Дама
rank-queen-plural = Дам
rank-king = Король
rank-king-plural = Королей

# Poker hand descriptions
poker-high-card-with = Старшая карта { $high }, кикер { $rest }
poker-high-card = Старшая карта { $high }
poker-pair-with = Пара { $pair }, кикер { $rest }
poker-pair = Пара { $pair }
poker-two-pair-with = Две пары: { $high } и { $low }, кикер { $kicker }
poker-two-pair = Две пары: { $high } и { $low }
poker-trips-with = Сет: { $trips }, кикер { $rest }
poker-trips = Сет: { $trips }
poker-straight-high = Стрит до { $high }
poker-flush-high-with = Флеш до { $high }, кикер { $rest }
poker-full-house = Фулл-хаус: { $trips } и { $pair }
poker-quads-with = Каре: { $quads }, кикер { $kicker }
poker-quads = Каре: { $quads }
poker-straight-flush-high = Стрит-флеш до { $high }
poker-unknown-hand = Неизвестная комбинация

# Validation errors (common across games)
game-error-invalid-team-mode = Выбранный командный режим недопустим для текущего количества игроков.
