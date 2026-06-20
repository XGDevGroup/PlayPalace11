# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Миля за милею

# Game options
milebymile-set-distance = Дистанція гонки: { $miles } миль
milebymile-enter-distance = Введіть дистанцію гонки (300-3000)
milebymile-set-winning-score = Переможний рахунок: { $score } очок
milebymile-enter-winning-score = Введіть переможний рахунок (1000-10000)
milebymile-toggle-perfect-crossing = Вимагати точного фінішу: { $enabled }
milebymile-toggle-stacking = Дозволити накопичення атак: { $enabled }
milebymile-toggle-reshuffle = Перетасувати скинуту колоду: { $enabled }
milebymile-toggle-karma = Правило карми: { $enabled }
milebymile-set-rig = Підтасовка колоди: { $rig }
milebymile-select-rig = Виберіть опцію підтасовки колоди

# Option change announcements
milebymile-option-changed-distance = Дистанцію гонки встановлено на { $miles } миль.
milebymile-option-changed-winning = Переможний рахунок встановлено на { $score } очок.
milebymile-option-changed-crossing = Вимагати точного фінішу { $enabled }.
milebymile-option-changed-stacking = Дозволити накопичення атак { $enabled }.
milebymile-option-changed-reshuffle = Перетасувати скинуту колоду { $enabled }.
milebymile-option-changed-karma = Правило карми { $enabled }.
milebymile-option-changed-rig = Підтасовку колоди встановлено на { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } очок, { $miles } миль, Проблеми: { $problems }, Безпека: { $safeties }

# Card actions
milebymile-no-matching-safety = У вас немає відповідної карти безпеки!
milebymile-cant-play = Ви не можете зіграти { $card }, тому що { $reason }.
milebymile-no-card-selected = Не вибрано карту для скидання.
milebymile-no-valid-targets = Немає дійсних цілей для цієї небезпеки!
milebymile-you-drew = Ви взяли: { $card }
milebymile-discards = { $player } скидає карту.
milebymile-select-target = Виберіть ціль

# Distance plays
milebymile-plays-distance-individual = { $player } грає { $distance } миль, і тепер на { $total } милях.
milebymile-plays-distance-team = { $player } грає { $distance } миль; їхня команда тепер на { $total } милях.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } завершив подорож з ідеальним перетином!
milebymile-journey-complete-perfect-team = Команда { $team } завершила подорож з ідеальним перетином!
milebymile-journey-complete-individual = { $player } завершив подорож!
milebymile-journey-complete-team = Команда { $team } завершила подорож!

# Hazard plays
milebymile-plays-hazard-individual = { $player } грає { $card } на { $target }.
milebymile-plays-hazard-team = { $player } грає { $card } на Команду { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } грає { $card }.
milebymile-plays-dirty-trick = { $player } грає { $card } як Брудний трюк!

# Deck
milebymile-deck-reshuffled = Скинуту колоду перетасовано назад в колоду.

# Race
milebymile-new-race = Нова гонка починається!
milebymile-race-complete = Гонка завершена! Підрахунок очок...
milebymile-earned-points = { $name } заробив { $score } очок цієї гонки: { $breakdown }.
milebymile-total-scores = Загальні рахунки:
milebymile-team-score = { $name }: { $score } очок

# Scoring breakdown
milebymile-from-distance = { $miles } за пройдену відстань
milebymile-from-trip = { $points } за завершення поїздки
milebymile-from-perfect = { $points } за ідеальний перетин
milebymile-from-safe = { $points } за безпечну поїздку
milebymile-from-shutout = { $points } за нуль
milebymile-from-safeties = { $points } від { $count } { $safeties ->
    [one] безпеки
    *[other] безпек
}
milebymile-from-all-safeties = { $points } за всі 4 безпеки
milebymile-from-dirty-tricks = { $points } від { $count } { $tricks ->
    [one] брудного трюку
    *[other] брудних трюків
}

# Game end
milebymile-wins-individual = { $player } виграє гру!
milebymile-wins-team = Команда { $team } виграє гру! ({ $members })
milebymile-final-score = Фінальний рахунок: { $score } очок

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Вас і вашу ціль обох відторгають! Атака нейтралізована.
milebymile-karma-clash-you-attacker = Вас і { $attacker } обох відторгають! Атака нейтралізована.
milebymile-karma-clash-others = { $attacker } і { $target } обох відторгають! Атака нейтралізована.
milebymile-karma-clash-your-team = Вашу команду і вашу ціль обох відторгають! Атака нейтралізована.
milebymile-karma-clash-target-team = Вас і Команду { $team } обох відторгають! Атака нейтралізована.
milebymile-karma-clash-other-teams = Команду { $attacker } і Команду { $target } обох відторгають! Атака нейтралізована.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Вас відторгли за вашу агресію! Ваша карма втрачена.
milebymile-karma-shunned-other = { $player } відторгнутий за їхню агресію!
milebymile-karma-shunned-your-team = Вашу команду відторгли за її агресію! Карма вашої команди втрачена.
milebymile-karma-shunned-other-team = Команду { $team } відторгли за її агресію!

# False Virtue
milebymile-false-virtue-you = Ви граєте Фальшива чеснота і повертаєте свою карму!
milebymile-false-virtue-other = { $player } грає Фальшива чеснота і повертає свою карму!
milebymile-false-virtue-your-team = Ваша команда грає Фальшива чеснота і повертає свою карму!
milebymile-false-virtue-other-team = Команда { $team } грає Фальшива чеснота і повертає свою карму!

# Problems/Safeties (for status display)
milebymile-none = немає

# Unplayable card reasons
milebymile-reason-not-on-team = ви не в команді
milebymile-reason-stopped = ви зупинені
milebymile-reason-has-problem = у вас проблема, що перешкоджає їзді
milebymile-reason-speed-limit = обмеження швидкості активне
milebymile-reason-exceeds-distance = це перевищить { $miles } миль
milebymile-reason-no-targets = немає дійсних цілей
milebymile-reason-no-speed-limit = ви не під обмеженням швидкості
milebymile-reason-has-right-of-way = Право проїзду дозволяє їхати без зелених світлофорів
milebymile-reason-already-moving = ви вже рухаєтесь
milebymile-reason-must-fix-first = спочатку потрібно виправити { $problem }
milebymile-reason-has-gas = у вашій машині є бензин
milebymile-reason-tires-fine = ваші шини в порядку
milebymile-reason-no-accident = ваша машина не була в аварії
milebymile-reason-has-safety = у вас вже є ця безпека
milebymile-reason-has-karma = у вас ще є карма
milebymile-reason-generic = зараз не можна зіграти

# Card names
milebymile-card-out-of-gas = Без бензину
milebymile-card-flat-tire = Проколота шина
milebymile-card-accident = Аварія
milebymile-card-speed-limit = Обмеження швидкості
milebymile-card-stop = Стоп
milebymile-card-gasoline = Бензин
milebymile-card-spare-tire = Запасна шина
milebymile-card-repairs = Ремонт
milebymile-card-end-of-limit = Кінець обмеження
milebymile-card-green-light = Зелене світло
milebymile-card-extra-tank = Додатковий бак
milebymile-card-puncture-proof = Протипрокольна
milebymile-card-driving-ace = Ас водіння
milebymile-card-right-of-way = Право проїзду
milebymile-card-false-virtue = Фальшива чеснота
milebymile-card-miles = { $miles } миль

# Disabled action reasons
milebymile-no-dirty-trick-window = Немає активного вікна брудного трюку.
milebymile-not-your-dirty-trick = Це не вікно брудного трюку вашої команди.
milebymile-between-races = Почекайте початку наступної гонки.

# Validation errors
milebymile-error-karma-needs-three-teams = Правило карми вимагає принаймні 3 різних автомобілів/команд.

milebymile-you-play-safety-with-effect = Ви граєте { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } грає { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Ви граєте { $card } як Брудний трюк. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } грає { $card } як Брудний трюк. { $effect }
milebymile-safety-effect-extra-tank = Тепер захищено від Без пального.
milebymile-safety-effect-puncture-proof = Тепер захищено від Проколу шини.
milebymile-safety-effect-driving-ace = Тепер захищено від Аварії.
milebymile-safety-effect-right-of-way = Тепер захищено від Стопа та Обмеження швидкості.
