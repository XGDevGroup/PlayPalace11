# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Миля за милей

# Game options
milebymile-set-distance = Дистанция гонки: { $miles } миль
milebymile-enter-distance = Введите дистанцию гонки (300–3000)
milebymile-set-winning-score = Победный счёт: { $score } очков
milebymile-enter-winning-score = Введите победный счёт (1000–10000)
milebymile-toggle-perfect-crossing = Требовать точный финиш: { $enabled }
milebymile-toggle-stacking = Разрешить накопление проблем: { $enabled }
milebymile-toggle-reshuffle = Перемешивать стопку сброса: { $enabled }
milebymile-toggle-karma = Правило кармы: { $enabled }
milebymile-set-rig = Подтасовка колоды: { $rig }
milebymile-select-rig = Выберите вариант подтасовки колоды

# Option change announcements
milebymile-option-changed-distance = Дистанция гонки установлена на { $miles } миль.
milebymile-option-changed-winning = Победный счёт установлен на { $score } очков.
milebymile-option-changed-crossing = Требование точного финиша: { $enabled }.
milebymile-option-changed-stacking = Накопление проблем: { $enabled }.
milebymile-option-changed-reshuffle = Перемешивание стопки сброса: { $enabled }.
milebymile-option-changed-karma = Правило кармы: { $enabled }.
milebymile-option-changed-rig = Подтасовка колоды: { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } очков, { $miles } миль. Проблемы: { $problems }, защиты: { $safeties }

# Card actions
milebymile-no-matching-safety = У вас нет подходящей карты защиты!
milebymile-cant-play = Вы не можете разыграть карту «{ $card }», так как { $reason }.
milebymile-no-card-selected = Не выбрана карта для сброса.
milebymile-no-valid-targets = Нет подходящих целей для этой проблемы!
milebymile-you-drew = Вы взяли карту: { $card }
milebymile-discards = { $player } сбрасывает карту.
milebymile-select-target = Выберите цель

# Distance plays
milebymile-plays-distance-individual = { $player } проезжает { $distance } миль и теперь находится на отметке { $total } миль.
milebymile-plays-distance-team = { $player } проезжает { $distance } миль; его команда теперь на отметке { $total } миль.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } завершает путь с точным финишем!
milebymile-journey-complete-perfect-team = Команда { $team } завершает путь с точным финишем!
milebymile-journey-complete-individual = { $player } завершает путь!
milebymile-journey-complete-team = Команда { $team } завершает путь!

# Hazard plays
milebymile-plays-hazard-individual = { $player } разыгрывает «{ $card }» против игрока { $target }.
milebymile-plays-hazard-team = { $player } разыгрывает «{ $card }» против команды { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } разыгрывает карту «{ $card }».
milebymile-plays-dirty-trick = { $player } разыгрывает карту «{ $card }» как подлый трюк!

# Deck
milebymile-deck-reshuffled = Стопка сброса перемешана и возвращена в колоду.

# Race
milebymile-new-race = Начинается новая гонка!
milebymile-race-complete = Гонка завершена! Подсчёт очков...
milebymile-earned-points = { $name } получает { $score } очков за эту гонку: { $breakdown }.
milebymile-total-scores = Общий счёт:
milebymile-team-score = { $name }: { $score } очков

# Scoring breakdown
milebymile-from-distance = { $miles } за пройденную дистанцию
milebymile-from-trip = { $points } за завершение пути
milebymile-from-perfect = { $points } за точный финиш
milebymile-from-safe = { $points } за безопасную поездку (без аварий)
milebymile-from-shutout = { $points } за «сухую» победу (соперник не сдвинулся с места)
milebymile-from-safeties = { $points } за { $count } { $safeties ->
    [one] карту защиты
    [few] карты защиты
   *[other] карт защиты
}
milebymile-from-all-safeties = { $points } за все 4 карты защиты
milebymile-from-dirty-tricks = { $points } за { $count } { $tricks ->
    [one] подлый трюк
    [few] подлых трюка
   *[other] подлых трюков
}

# Game end
milebymile-wins-individual = { $player } побеждает в игре!
milebymile-wins-team = Команда { $team } побеждает в игре! ({ $members })
milebymile-final-score = Итоговый счёт: { $score } очков

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = И вы, и ваша цель отвергнуты! Атака нейтрализована.
milebymile-karma-clash-you-attacker = И вы, и { $attacker } отвергнуты! Атака нейтрализована.
milebymile-karma-clash-others = { $attacker } и { $target } отвергнуты! Атака нейтрализована.
milebymile-karma-clash-your-team = Ваша команда и ваша цель отвергнуты! Атака нейтрализована.
milebymile-karma-clash-target-team = Вы и команда { $team } отвергнуты! Атака нейтрализована.
milebymile-karma-clash-other-teams = Команда { $attacker } и команда { $target } отвергнуты! Атака нейтрализована.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Вы были отвергнуты за свою агрессию! Ваша карма потеряна.
milebymile-karma-shunned-other = { $player } был отвергнут за свою агрессию!
milebymile-karma-shunned-your-team = Ваша команда была отвергнута за агрессию! Карма команды потеряна.
milebymile-karma-shunned-other-team = Команда { $team } была отвергнута за свою агрессию!

# False Virtue
milebymile-false-virtue-you = Вы разыгрываете «Ложную добродетель» и восстанавливаете свою карму!
milebymile-false-virtue-other = { $player } разыгрывает «Ложную добродетель» и восстанавливает свою карму!
milebymile-false-virtue-your-team = Ваша команда разыгрывает «Ложную добродетель» и восстанавливает свою карму!
milebymile-false-virtue-other-team = Команда { $team } разыгрывает «Ложную добродетель» и восстанавливает свою карму!

# Problems/Safeties (for status display)
milebymile-none = нет

# Unplayable card reasons
milebymile-reason-not-on-team = вы не в команде
milebymile-reason-stopped = вы стоите на месте
milebymile-reason-has-problem = у вас есть проблема, мешающая движению
milebymile-reason-speed-limit = действует ограничение скорости
milebymile-reason-exceeds-distance = это превысит дистанцию в { $miles } миль
milebymile-reason-no-targets = нет подходящих целей
milebymile-reason-no-speed-limit = на вас не действует ограничение скорости
milebymile-reason-has-right-of-way = «Приоритет» позволяет ехать без зелёного света
milebymile-reason-already-moving = вы уже в движении
milebymile-reason-must-fix-first = сначала нужно устранить проблему: { $problem }
milebymile-reason-has-gas = в вашей машине есть бензин
milebymile-reason-tires-fine = ваши шины в порядке
milebymile-reason-no-accident = ваша машина не попадала в аварию
milebymile-reason-has-safety = у вас уже есть эта карта защиты
milebymile-reason-has-karma = у вас всё ещё есть карма
milebymile-reason-generic = карту нельзя разыграть сейчас

# Card names
milebymile-card-out-of-gas = Без бензина
milebymile-card-flat-tire = Спущенное колесо
milebymile-card-accident = Авария
milebymile-card-speed-limit = Ограничение скорости
milebymile-card-stop = Стоп
milebymile-card-gasoline = Бензин
milebymile-card-spare-tire = Запасное колесо
milebymile-card-repairs = Ремонт
milebymile-card-end-of-limit = Конец ограничения скорости
milebymile-card-green-light = Зелёный свет
milebymile-card-extra-tank = Бензобак
milebymile-card-puncture-proof = Непробиваемые шины
milebymile-card-driving-ace = Водитель-ас
milebymile-card-right-of-way = Приоритет
milebymile-card-false-virtue = Ложная добродетель
milebymile-card-miles = { $miles } миль

# Disabled action reasons
milebymile-no-dirty-trick-window = Окно для подлого трюка сейчас не активно.
milebymile-not-your-dirty-trick = Сейчас не окно подлого трюка вашей команды.
milebymile-between-races = Дождитесь начала следующей гонки.

# Validation errors
milebymile-error-karma-needs-three-teams = Для правила кармы требуется как минимум 3 отдельных машины или команды.

milebymile-you-play-safety-with-effect = Вы играете { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } играет { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Вы играете { $card } как подлый трюк. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } играет { $card } как подлый трюк. { $effect }
milebymile-safety-effect-extra-tank = Теперь вы защищены от слива бензина.
milebymile-safety-effect-puncture-proof = Теперь вы защищены от прокола колёс.
milebymile-safety-effect-driving-ace = Теперь вы защищены от аварий.
milebymile-safety-effect-right-of-way = Теперь вы защищены от остановки и ограничения скорости.
