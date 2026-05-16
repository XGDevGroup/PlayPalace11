# Main UI messages for PlayPalace

# Game categories
category-card-games = Карточные игры
category-dice-games = Игры в кости
category-board-games = Настольные игры
category-rb-play-center = RB Play Center
category-poker = Покер
category-uncategorized = Без категории

# Menu titles
main-menu-title = Главное меню
play-menu-title = Играть
categories-menu-title = Категории игр
tables-menu-title = Доступные столы

# Menu items
play = Играть
view-active-tables = Список активных столов
options = Настройки
logout = Выйти
back = Назад
context-menu = Контекстное меню.
no-actions-available = Нет доступных действий.
create-table = Создать новый стол
join-as-player = Присоединиться как игрок
join-as-spectator = Присоединиться как зритель
leave-table = Покинуть стол
start-game = Начать игру
add-bot = Добавить бота
remove-bot = Удалить бота
actions-menu = Меню действий
save-table = Сохранить стол
whose-turn = Чей ход
whos-at-table = Кто за столом
check-scores = Проверить счёт
check-scores-detailed = Подробный счёт
check-game-options = Проверить настройки игры
no-game-options = Нет настроек игры.

# Turn messages
game-player-skipped = { $player } пропускает ход.

# Table messages
table-created = { $host } создаёт новый стол для игры «{ $game }».
table-joined = { $player } присоединяется к столу.
table-left = { $player } покидает стол.
new-host = { $player } теперь организатор.
waiting-for-players = Ожидание игроков. Минимум: {$min}, максимум: { $max }.
game-starting = Игра начинается!
table-listing = Стол игрока { $host } ({ $count } { $count ->
    [one] участник
    [few] участника
   *[other] участников
})
table-listing-one = Стол игрока { $host } ({ $count } участник)
table-listing-with = Стол игрока { $host } ({ $count } { $count ->
    [one] участник
    [few] участника
   *[other] участников
}), играют: { $members }
table-listing-game = { $game }: стол игрока { $host } ({ $count } { $count ->
    [one] участник
    [few] участника
   *[other] участников
})
table-listing-game-one = { $game }: стол игрока { $host } ({ $count } участник)
table-listing-game-with = { $game }: стол игрока { $host } ({ $count } { $count ->
    [one] участник
    [few] участника
   *[other] участников
}), играют: { $members }
table-not-exists = Стол больше не существует.
table-full = Стол заполнен.
player-replaced-by-bot = { $player } уходит, его место занимает бот.
player-took-over = { $player } заменяет бота.
spectator-joined = Вы присоединились к столу игрока { $host } как зритель.

# Spectator mode
spectate = Наблюдать
now-playing = { $player } теперь играет.
now-spectating = { $player } теперь наблюдает.
spectator-left = { $player } прекращает наблюдение.

# General
welcome = Добро пожаловать в PlayPalace!
goodbye = До свидания!

# User presence announcements
user-online = { $player } в сети.
user-offline = { $player } не в сети.
user-is-admin = { $player } является администратором PlayPalace.
user-is-server-owner = { $player } является владельцем сервера PlayPalace.
online-users-none = Нет пользователей в сети.
online-users-one = 1 пользователь: { $users }
online-users-many = { $count } { $count ->
    [one] пользователь
    [few] пользователя
   *[other] пользователей
}: { $users }
online-user-not-in-game = Вне игры
online-user-waiting-approval = Ожидает одобрения

# Options
language = Язык
language-option = Язык: { $language }
language-changed = Выбран язык: { $language }.

# Boolean option states
option-on = Вкл.
option-off = Выкл.

# Sound options
turn-sound-option = Звук хода: { $status }

# Dice options
clear-kept-option = Сбрасывать отложенные кубики при броске: { $status }
dice-keeping-style-option = Стиль удержания кубиков: { $style }
dice-keeping-style-changed = Стиль удержания кубиков изменён на: { $style }.
dice-keeping-style-indexes = По индексам
dice-keeping-style-values = По значениям

# Bot names
cancel = Отмена
no-bot-names-available = Нет доступных имён для ботов.
select-bot-name = Выберите имя для бота
enter-bot-name = Введите имя бота
no-options-available = Нет доступных настроек.
no-scores-available = Нет данных о счёте.

# Duration estimation
estimate-duration = Оценить длительность
estimate-computing = Расчёт примерной длительности игры...
estimate-result = Среднее время ботов: { $bot_time } (± { $std_dev }). { $outlier_info }Примерное время людей: { $human_time }.
estimate-error = Не удалось оценить длительность.
estimate-already-running = Расчёт длительности уже запущен.

# Save/Restore
saved-tables = Сохранённые столы
no-saved-tables = У вас нет сохранённых столов.
no-active-tables = Нет активных столов.
restore-table = Восстановить
delete-saved-table = Удалить
saved-table-deleted = Сохранённый стол удалён.
missing-players = Не удалось восстановить: следующие игроки недоступны: { $players }
table-restored = Стол восстановлен! Все игроки перенесены.
table-saved-destroying = Стол сохранён! Возврат в главное меню.
game-type-not-found = Тип игры больше не существует.

# Action disabled reasons
action-not-your-turn = Сейчас не ваш ход.
action-not-playing = Игра ещё не началась.
action-spectator = Зрители не могут этого делать.
action-not-host = Только организатор может это делать.
action-game-in-progress = Нельзя сделать это во время игры.
action-need-more-players = Нужно минимум { $min_players } игроков для начала.
action-table-full = Стол заполнен.
action-no-bots = Нет ботов для удаления.
action-bots-cannot = Боты не могут этого делать.
action-no-scores = Данные о счёте пока отсутствуют.

# Dice actions
dice-not-rolled = Вы ещё не бросали кубики.
dice-locked = Этот кубик заблокирован.
dice-no-dice = Нет доступных кубиков.

# Game actions
game-turn-start = Ход игрока { $player }.
game-no-turn = Сейчас никто не ходит.
table-no-players = Нет игроков.
table-players-one = { $count } игрок: { $players }.
table-players-many = { $count } { $count ->
    [one] игрок
    [few] игрока
   *[other] игроков
}: { $players }.
table-spectators = Зрители: { $spectators }.
game-leave = Покинуть
game-over = Игра окончена
game-final-scores = Итоговый счёт
game-points = { $count } { $count ->
    [one] очко
    [few] очка
   *[other] очков
}
play = Играть

# Leaderboards
leaderboards = Таблицы лидеров
leaderboards-menu-title = Таблицы лидеров
leaderboards-select-game = Выберите игру, чтобы посмотреть таблицу лидеров
leaderboard-no-data = Для этой игры пока нет данных в таблице лидеров.

# Leaderboard types
leaderboard-type-wins = Лидеры по победам
leaderboard-type-rating = Рейтинг мастерства
leaderboard-type-total-score = Общий счёт
leaderboard-type-high-score = Рекорды
leaderboard-type-games-played = Игр сыграно
leaderboard-type-avg-points-per-turn = Среднее очков за ход
leaderboard-type-best-single-turn = Лучший ход
leaderboard-type-score-per-round = Очков за раунд

# Leaderboard headers
leaderboard-wins-header = { $game } — Лидеры по победам
leaderboard-total-score-header = { $game } — Общий счёт
leaderboard-high-score-header = { $game } — Рекорды
leaderboard-games-played-header = { $game } — Игр сыграно
leaderboard-rating-header = { $game } — Рейтинг мастерства
leaderboard-avg-points-header = { $game } — Среднее очков за ход
leaderboard-best-turn-header = { $game } — Лучший ход
leaderboard-score-per-round-header = { $game } — Очков за раунд

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] победа
    [few] победы
   *[other] побед
}, { $losses } { $losses ->
    [one] поражение
    [few] поражения
   *[other] поражений
}, { $percentage }% побед
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } в ср.
leaderboard-games-entry = { $rank }. { $player }: { $value } { $value ->
    [one] игра
    [few] игры
   *[other] игр
}

# Player stats
leaderboard-player-stats = Ваша статистика: { $wins } { $wins ->
    [one] победа
    [few] победы
   *[other] побед
}, { $losses } { $losses ->
    [one] поражение
    [few] поражения
   *[other] поражений
} ({ $percentage }% побед)
leaderboard-no-player-stats = Вы ещё не играли в эту игру.

# Skill rating leaderboard
leaderboard-no-ratings = Для этой игры пока нет данных о рейтинге.
leaderboard-rating-entry = { $rank }. { $player }: рейтинг { $rating } ({ $mu } ± { $sigma })
leaderboard-player-rating = Ваш рейтинг: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = У вас пока нет рейтинга в этой игре.

# My Stats menu
my-stats = Моя статистика
my-stats-select-game = Выберите игру, чтобы посмотреть свою статистику
my-stats-no-data = Вы ещё не играли в эту игру.
my-stats-no-games = Вы ещё не сыграли ни одной игры.
my-stats-header = { $game } — Ваша статистика
my-stats-wins = Побед: { $value }
my-stats-losses = Поражений: { $value }
my-stats-winrate = Процент побед: { $value }%
my-stats-games-played = Игр сыграно: { $value }
my-stats-total-score = Общий счёт: { $value }
my-stats-high-score = Лучший результат: { $value }
my-stats-rating = Рейтинг мастерства: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Рейтинг пока не определён
my-stats-avg-per-turn = Среднее очков за ход: { $value }
my-stats-best-turn = Лучший ход: { $value }

# Prediction system
predict-outcomes = Прогноз исхода
predict-header = Прогноз результатов (на основе рейтинга)
predict-entry = { $rank }. { $player } (рейтинг: { $rating })
predict-entry-2p = { $rank }. { $player } (рейтинг: { $rating }, вероятность победы: { $probability }%)
predict-unavailable = Прогнозы рейтинга недоступны.
predict-need-players = Для прогноза нужно как минимум 2 игрока-человека.
action-need-more-humans = Нужно больше игроков-людей.
confirm-leave-game = Вы уверены, что хотите покинуть стол?
confirm-yes = Да
confirm-no = Нет

# Administration
administration = Администрирование
admin-menu-title = Администрирование

# Account approval
account-approval = Одобрение аккаунтов
account-approval-menu-title = Одобрение аккаунтов
no-pending-accounts = Нет аккаунтов, ожидающих подтверждения.
approve-account = Одобрить
decline-account = Отклонить
account-approved = Аккаунт игрока { $player } одобрен.
account-declined = Запрос игрока { $player } отклонён, аккаунт удалён.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Ваш аккаунт ожидает подтверждения администратором.
account-approved-welcome = Ваш аккаунт одобрен! Добро пожаловать в PlayPalace!
account-declined-goodbye = Ваш запрос на создание аккаунта был отклонён.
    Причина:
account-banned = Ваш аккаунт заблокирован и недоступен.

# Ошибки входа
incorrect-username = Введённое имя пользователя не существует.
incorrect-password = Введённый пароль неверен.
already-logged-in = Этот аккаунт уже выполнен вход.

# Проверка учётных данных
credential-username-length = Имя пользователя должно содержать от { $min } до { $max } символов.
credential-password-length = Пароль должен содержать от { $min } до { $max } символов.

# Ограничение количества попыток
rate-limit-login-ip = Слишком много попыток входа с этого адреса. Подождите и попробуйте снова.
rate-limit-login-user = Слишком много неудачных попыток входа для этого имени пользователя. Подождите и попробуйте снова.
rate-limit-registration = Слишком много попыток регистрации с этого адреса. Подождите и попробуйте снова.
rate-limit-refresh = Слишком много попыток обновления с этого адреса. Подождите и попробуйте снова.

# Ошибки сессии и авторизации
account-not-found = Аккаунт не найден.
session-expired = Сессия истекла. Пожалуйста, войдите снова.
session-token-mismatch = Токен сессии не соответствует имени пользователя.
refresh-token-expired = Токен обновления истёк. Пожалуйста, войдите снова.
refresh-token-mismatch = Токен обновления не соответствует имени пользователя.

# Регистрация
registration-success = Регистрация прошла успешно! Ваш аккаунт ожидает подтверждения.
registration-username-taken = Это имя пользователя уже занято. Пожалуйста, выберите другое имя пользователя.

# Настройки по умолчанию
pref-invalid-value = Недопустимый выбор, используется значение по умолчанию.

# Причина отклонения
decline-reason-prompt = Введите причину отклонения (или нажмите Escape для отмены):
account-action-empty-reason = Причина не указана.

# Admin notifications for account requests
account-request = запрос аккаунта
account-action = действие с аккаунтом выполнено

# Admin promotion/demotion
promote-admin = Назначить администратором
demote-admin = Снять права администратора
promote-admin-menu-title = Назначение администратора
demote-admin-menu-title = Снятие прав администратора
no-users-to-promote = Нет пользователей для назначения.
no-admins-to-demote = Нет администраторов для снятия прав.
confirm-promote = Вы уверены, что хотите назначить игрока { $player } администратором?
confirm-demote = Вы уверены, что хотите снять права администратора с игрока { $player }?
broadcast-to-all = Объявить всем пользователям
broadcast-to-admins = Объявить только администраторам
broadcast-to-nobody = Без объявления
promote-announcement = { $player } назначается администратором!
promote-announcement-you = Вы назначены администратором!
demote-announcement = { $player } больше не является администратором.
demote-announcement-you = С вас сняты права администратора.
not-admin-anymore = Вы больше не являетесь администратором и не можете выполнить это действие.
not-server-owner = Только владелец сервера может выполнить это действие.

# Server ownership transfer
transfer-ownership = Передать владение
transfer-ownership-menu-title = Передача владения
no-admins-for-transfer = Нет администраторов для передачи владения.
confirm-transfer-ownership = Вы уверены, что хотите передать владение сервером игроку { $player }? Вы станете администратором.
transfer-ownership-announcement = { $player } теперь владелец сервера Play Palace!
transfer-ownership-announcement-you = Вы теперь владелец сервера Play Palace!

# User banning
ban-user = Забанить пользователя
unban-user = Разбанить пользователя
no-users-to-ban = Нет пользователей для бана.
no-users-to-unban = Нет забаненных пользователей для разбана.
confirm-ban = Вы уверены, что хотите забанить { $player }?
confirm-unban = Вы уверены, что хотите разбанить { $player }?
ban-reason-prompt = Введите причину бана (необязательно):
unban-reason-prompt = Введите причину разбана (необязательно):
user-banned = { $player } был забанен.
user-unbanned = { $player } был разбанен.
you-have-been-banned = Вы были забанены на этом сервере.
    Причина:
you-have-been-unbanned = Вы были разбанены на этом сервере.
    Причина:
ban-no-reason = Причина не указана.

# Virtual bots (server owner only)
virtual-bots = Виртуальные боты
virtual-bots-fill = Заполнить сервер
virtual-bots-clear = Очистить всех ботов
virtual-bots-status = Статус
virtual-bots-clear-confirm = Вы уверены, что хотите удалить всех виртуальных ботов? Это также закроет все столы, за которыми они находятся.
virtual-bots-not-available = Виртуальные боты недоступны.
virtual-bots-filled = Добавлено { $added } виртуальных ботов. Сейчас в сети: { $online }.
virtual-bots-already-filled = Все виртуальные боты из конфигурации уже активны.
virtual-bots-cleared = Удалено { $bots } виртуальных ботов и закрыто { $tables } { $tables ->
    [one] стол
    [few] стола
   *[other] столов
}.
virtual-bot-table-closed = Стол закрыт администратором.
virtual-bots-none-to-clear = Нет виртуальных ботов для удаления.
virtual-bots-status-report = Виртуальные боты: всего { $total }, в сети { $online }, не в сети { $offline }, в игре { $in_game }.
virtual-bots-guided-overview = Управляемые столы
virtual-bots-groups-overview = Группы ботов
virtual-bots-profiles-overview = Профили
virtual-bots-guided-header = Управляемые столы: правил — { $count }. Распределение: { $allocation }, резерв: { $fallback }, профиль по умолчанию: { $default_profile }.
virtual-bots-guided-empty = Правила управляемых столов не настроены.
virtual-bots-guided-status-active = активен
virtual-bots-guided-status-inactive = неактивен
virtual-bots-guided-table-linked = привязан к столу { $table_id } (организатор: { $host }, игроков { $players }, людей { $humans })
virtual-bots-guided-table-stale = стол { $table_id } отсутствует на сервере
virtual-bots-guided-table-unassigned = стол в данный момент не отслеживается
virtual-bots-guided-next-change = следующее изменение через { $ticks } тиков
virtual-bots-guided-no-schedule = расписание не задано
virtual-bots-guided-warning = ⚠ недобор
virtual-bots-guided-line = { $table }: игра { $game }, приоритет { $priority }, ботов { $assigned } (мин { $min_bots }, макс { $max_bots }), в ожидании { $waiting }, недоступно { $unavailable }, статус { $status }, профиль { $profile }, группы { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Группы ботов: тегов — { $count }, настроено ботов — { $bots }.
virtual-bots-groups-empty = Группы ботов не определены.
virtual-bots-groups-line = { $group }: профиль { $profile }, ботов { $total } (в сети { $online }, ожидают { $waiting }, в игре { $in_game }, не в сети { $offline }), правила { $rules }.
virtual-bots-groups-no-rules = нет
virtual-bots-no-profile = по умолчанию
virtual-bots-profile-inherit-default = наследует профиль по умолчанию
virtual-bots-profiles-header = Профили: определено { $count } (по умолчанию: { $default_profile }).
virtual-bots-profiles-empty = Профили не определены.
virtual-bots-profiles-line = { $profile } (ботов: { $bot_count }) переопределения: { $overrides }.
virtual-bots-profiles-no-overrides = наследует базовую конфигурацию

localization-in-progress-try-again = Локализация ещё загружается. Пожалуйста, попробуйте снова через минуту.
