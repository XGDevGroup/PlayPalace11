# Main UI messages for PlayPalace

# Game categories
category-card-games = Карткові ігри
category-dice-games = Ігри з кубиками
category-rb-play-center = Центр ігор RB
category-poker = Покер
category-uncategorized = Без категорії

# Menu titles
main-menu-title = Головне меню
play-menu-title = Грати
categories-menu-title = Категорії ігор
tables-menu-title = Доступні столи

# Menu items
play = Грати
view-active-tables = Переглянути активні столи
options = Налаштування
logout = Вийти
back = Назад
go-back = Повернутися
context-menu = Контекстне меню.
no-actions-available = Немає доступних дій.
create-table = Створити новий стіл
join-as-player = Приєднатись як гравець
join-as-spectator = Приєднатись як глядач
leave-table = Покинути стіл
start-game = Почати гру
add-bot = Додати бота
remove-bot = Видалити бота
actions-menu = Меню дій
save-table = Зберегти стіл
whose-turn = Чий хід
whos-at-table = Хто за столом
check-scores = Перевірити рахунок
check-scores-detailed = Детальний рахунок
check-game-options = Перевірити параметри гри
no-game-options = Немає параметрів гри.

# Turn messages
game-player-skipped = { $player } пропущений.

# Table messages
table-created = { $host } створив новий стіл { $game }.
table-joined = { $player } приєднався до столу.
table-left = { $player } покинув стіл.
new-host = { $player } тепер господар.
waiting-for-players = Очікуємо гравців. {$min} мін, { $max } макс.
game-starting = Гра починається!
table-listing = Стіл { $host } ({ $count } користувачів)
table-listing-one = Стіл { $host } ({ $count } користувач)
table-listing-with = Стіл { $host } ({ $count } користувачів) з { $members }
table-listing-game = { $game }: стіл { $host } ({ $count } користувачів)
table-listing-game-one = { $game }: стіл { $host } ({ $count } користувач)
table-listing-game-with = { $game }: стіл { $host } ({ $count } користувачів) з { $members }
table-not-exists = Стіл більше не існує.
table-full = Стіл заповнений.
player-replaced-by-bot = { $player } вийшов і був замінений ботом.
player-took-over = { $player } перейняв керування від бота.
spectator-joined = Приєднався до столу { $host } як глядач.

# Spectator mode
spectate = Спостерігати
now-playing = { $player } тепер грає.
now-spectating = { $player } тепер спостерігає.
spectator-left = { $player } припинив спостереження.

# General
welcome = Ласкаво просимо до PlayPalace!
goodbye = До побачення!

# User presence announcements
user-online = { $player } з'явився в мережі.
user-offline = { $player } вийшов з мережі.
user-is-admin = { $player } є адміністратором PlayPalace.
user-is-server-owner = { $player } є власником сервера PlayPalace.
online-users-none = Немає користувачів в мережі.
online-users-one = 1 користувач: { $users }
online-users-many = { $count } користувачів: { $users }
online-user-not-in-game = Не в грі
online-user-waiting-approval = Очікує схвалення

# Options
language = Мова
language-option = Мова: { $language }
language-changed = Мову встановлено на { $language }.

# Boolean option states
option-on = Увімкнено
option-off = Вимкнено

# Sound options
turn-sound-option = Звук ходу: { $status }

# Dice options
clear-kept-option = Очищати збережені кубики при киданні: { $status }
dice-keeping-style-option = Стиль збереження кубиків: { $style }
dice-keeping-style-changed = Стиль збереження кубиків встановлено на { $style }.
dice-keeping-style-indexes = Індекси кубиків
dice-keeping-style-values = Значення кубиків

# Bot names
cancel = Скасувати
no-bot-names-available = Немає доступних імен ботів.
select-bot-name = Виберіть ім'я для бота
enter-bot-name = Введіть ім'я бота
no-options-available = Немає доступних опцій.
no-scores-available = Немає доступних рахунків.

# Duration estimation
estimate-duration = Оцінити тривалість
estimate-computing = Обчислюємо оцінку тривалості гри...
estimate-result = Середнє для бота: { $bot_time } (± { $std_dev }). { $outlier_info }Оцінка часу для людини: { $human_time }.
estimate-error = Не вдалося оцінити тривалість.
estimate-already-running = Оцінка тривалості вже виконується.

# Save/Restore
saved-tables = Збережені столи
no-saved-tables = У вас немає збережених столів.
no-active-tables = Немає активних столів.
restore-table = Відновити
delete-saved-table = Видалити
saved-table-deleted = Збережений стіл видалено.
missing-players = Не вдалося відновити: ці гравці недоступні: { $players }
table-restored = Стіл відновлено! Всі гравці переведені.
table-saved-destroying = Стіл збережено! Повертаємось до головного меню.
game-type-not-found = Тип гри більше не існує.

# Action disabled reasons
action-not-your-turn = Зараз не ваш хід.
action-not-playing = Гра ще не почалася.
action-spectator = Глядачі не можуть це робити.
action-not-host = Тільки господар може це робити.
action-game-in-progress = Не можна це зробити під час гри.
action-need-more-players = Потрібно більше гравців для початку.
action-table-full = Стіл заповнений.
action-no-bots = Немає ботів для видалення.
action-bots-cannot = Боти не можуть це робити.
action-no-scores = Рахунки ще недоступні.

# Dice actions
dice-not-rolled = Ви ще не кидали кубики.
dice-locked = Цей кубик заблокований.
dice-no-dice = Немає доступних кубиків.

# Game actions
game-turn-start = Хід { $player }.
game-no-turn = Зараз нічий хід.
table-no-players = Немає гравців.
table-players-one = { $count } гравець: { $players }.
table-players-many = { $count } гравців: { $players }.
table-spectators = Глядачі: { $spectators }.
game-leave = Вийти
game-over = Гра закінчена
game-final-scores = Фінальні рахунки
game-points = { $count } { $count ->
    [one] очко
   *[other] очок
}
play = Грати

# Leaderboards
leaderboards = Таблиці лідерів
leaderboards-menu-title = Таблиці лідерів
leaderboards-select-game = Виберіть гру для перегляду таблиці лідерів
leaderboard-no-data = Поки немає даних таблиці лідерів для цієї гри.

# Leaderboard types
leaderboard-type-wins = Лідери за перемогами
leaderboard-type-rating = Рейтинг майстерності
leaderboard-type-total-score = Загальний рахунок
leaderboard-type-high-score = Найкращий рахунок
leaderboard-type-games-played = Зіграних ігор
leaderboard-type-avg-points-per-turn = Середні очки за хід
leaderboard-type-best-single-turn = Найкращий хід
leaderboard-type-score-per-round = Рахунок за раунд

# Leaderboard headers
leaderboard-wins-header = { $game } - Лідери за перемогами
leaderboard-total-score-header = { $game } - Загальний рахунок
leaderboard-high-score-header = { $game } - Найкращий рахунок
leaderboard-games-played-header = { $game } - Зіграних ігор
leaderboard-rating-header = { $game } - Рейтинги майстерності
leaderboard-avg-points-header = { $game } - Середні очки за хід
leaderboard-best-turn-header = { $game } - Найкращий хід
leaderboard-score-per-round-header = { $game } - Рахунок за раунд

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] перемога
   *[other] перемог
} { $losses } { $losses ->
    [one] поразка
   *[other] поразок
}, { $percentage }% перемог
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } сер.
leaderboard-games-entry = { $rank }. { $player }: { $value } ігор

# Player stats
leaderboard-player-stats = Ваша статистика: { $wins } перемог, { $losses } поразок ({ $percentage }% перемог)
leaderboard-no-player-stats = Ви ще не грали в цю гру.

# Skill rating leaderboard
leaderboard-no-ratings = Поки немає даних рейтингу для цієї гри.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } рейтинг ({ $mu } ± { $sigma })
leaderboard-player-rating = Ваш рейтинг: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = У вас ще немає рейтингу для цієї гри.

# My Stats menu
my-stats = Моя статистика
my-stats-select-game = Виберіть гру для перегляду статистики
my-stats-no-data = Ви ще не грали в цю гру.
my-stats-no-games = Ви ще не грали в жодну гру.
my-stats-header = { $game } - Ваша статистика
my-stats-wins = Перемоги: { $value }
my-stats-losses = Поразки: { $value }
my-stats-winrate = Відсоток перемог: { $value }%
my-stats-games-played = Зіграно ігор: { $value }
my-stats-total-score = Загальний рахунок: { $value }
my-stats-high-score = Найкращий рахунок: { $value }
my-stats-rating = Рейтинг майстерності: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Рейтинг майстерності ще немає
my-stats-avg-per-turn = Середні очки за хід: { $value }
my-stats-best-turn = Найкращий хід: { $value }

# Prediction system
predict-outcomes = Передбачити результати
predict-header = Передбачені результати (за рейтингом майстерності)
predict-entry = { $rank }. { $player } (рейтинг: { $rating })
predict-entry-2p = { $rank }. { $player } (рейтинг: { $rating }, { $probability }% шанс перемоги)
predict-unavailable = Передбачення за рейтингом недоступні.
predict-need-players = Потрібно принаймні 2 гравці-люди для передбачень.
action-need-more-humans = Потрібно більше гравців-людей.
confirm-leave-game = Ви впевнені, що хочете покинути стіл?
confirm-yes = Так
confirm-no = Ні

# Administration
administration = Адміністрування
admin-menu-title = Адміністрування

# Account approval
account-approval = Схвалення облікових записів
account-approval-menu-title = Схвалення облікових записів
no-pending-accounts = Немає облікових записів, що очікують.
approve-account = Схвалити
decline-account = Відхилити
account-approved = Обліковий запис { $player } схвалено.
account-declined = Обліковий запис { $player } відхилено та видалено.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Ваш обліковий запис очікує схвалення адміністратором.
account-approved-welcome = Ваш обліковий запис схвалено! Ласкаво просимо до PlayPalace!
account-declined-goodbye = Ваш запит на обліковий запис відхилено.
    Причина:
account-banned = Ваш обліковий запис заблоковано і не може бути доступний.

# Login errors
incorrect-username = Введене вами ім'я користувача не існує.
incorrect-password = Введений вами пароль неправильний.
already-logged-in = Цей обліковий запис вже увійшов в систему.

# Credential validation
credential-username-length = Ім'я користувача повинно містити від { $min } до { $max } символів.
credential-password-length = Пароль повинен містити від { $min } до { $max } символів.

# Rate limiting
rate-limit-login-ip = Забагато спроб входу з цієї адреси. Будь ласка, зачекайте і спробуйте знову.
rate-limit-login-user = Забагато невдалих спроб входу для цього імені користувача. Будь ласка, зачекайте і спробуйте знову.
rate-limit-registration = Забагато спроб реєстрації з цієї адреси. Будь ласка, зачекайте і спробуйте знову.
rate-limit-refresh = Забагато спроб оновлення з цієї адреси. Будь ласка, зачекайте і спробуйте знову.

# Session/auth errors
account-not-found = Обліковий запис не знайдено.
session-expired = Сесія закінчилась. Будь ласка, увійдіть знову.
session-token-mismatch = Токен сесії не відповідає імені користувача.
refresh-token-expired = Токен оновлення закінчився. Будь ласка, увійдіть знову.
refresh-token-mismatch = Токен оновлення не відповідає імені користувача.

# Registration
registration-success = Реєстрація успішна! Ваш обліковий запис очікує схвалення.
registration-username-taken = Це ім'я користувача вже зайняте. Будь ласка, оберіть інше.

# Preference fallback
pref-invalid-value = Невірний вибір, використовується стандартне значення.

# Decline reason
decline-reason-prompt = Введіть причину відхилення (або натисніть Escape для скасування):
account-action-empty-reason = Причину не вказано.

# Admin notifications for account requests
account-request = запит на обліковий запис
account-action = дію з обліковим записом виконано

# Admin promotion/demotion
promote-admin = Призначити адміністратором
demote-admin = Зняти адміністратора
promote-admin-menu-title = Призначити адміністратором
demote-admin-menu-title = Зняти адміністратора
no-users-to-promote = Немає користувачів для призначення.
no-admins-to-demote = Немає адміністраторів для зняття.
confirm-promote = Ви впевнені, що хочете призначити { $player } адміністратором?
confirm-demote = Ви впевнені, що хочете зняти { $player } з адміністратора?
broadcast-to-all = Оголосити всім користувачам
broadcast-to-admins = Оголосити тільки адміністраторам
broadcast-to-nobody = Тихо (без оголошення)
promote-announcement = { $player } призначений адміністратором!
promote-announcement-you = Вас призначено адміністратором!
demote-announcement = { $player } знято з адміністратора.
demote-announcement-you = Вас знято з адміністратора.
not-admin-anymore = Ви більше не адміністратор і не можете виконати цю дію.
not-server-owner = Тільки власник сервера може виконати цю дію.

# Server ownership transfer
transfer-ownership = Передати володіння
transfer-ownership-menu-title = Передати володіння
no-admins-for-transfer = Немає адміністраторів для передачі володіння.
confirm-transfer-ownership = Ви впевнені, що хочете передати володіння сервером { $player }? Ви будете знижені до адміністратора.
transfer-ownership-announcement = { $player } тепер власник сервера Play Palace!
transfer-ownership-announcement-you = Тепер ви власник сервера Play palace!

# User banning
ban-user = Заблокувати користувача
unban-user = Розблокувати користувача
no-users-to-ban = Немає користувачів для блокування.
no-users-to-unban = Немає заблокованих користувачів для розблокування.
confirm-ban = Ви впевнені, що хочете заблокувати { $player }?
confirm-unban = Ви впевнені, що хочете розблокувати { $player }?
ban-reason-prompt = Введіть причину блокування (необов'язково):
unban-reason-prompt = Введіть причину розблокування (необов'язково):
user-banned = { $player } заблоковано.
user-unbanned = { $player } розблоковано.
you-have-been-banned = Вас заблоковано на цьому сервері.
    Причина:
you-have-been-unbanned = Вас розблоковано на цьому сервері.
    Причина:
ban-no-reason = Причину не вказано.

# Virtual bots (server owner only)
virtual-bots = Віртуальні боти
virtual-bots-fill = Заповнити сервер
virtual-bots-clear = Очистити всіх ботів
virtual-bots-status = Статус
virtual-bots-clear-confirm = Ви впевнені, що хочете очистити всіх віртуальних ботів? Це також знищить будь-які столи, в яких вони знаходяться.
virtual-bots-not-available = Віртуальні боти недоступні.
virtual-bots-filled = Додано { $added } віртуальних ботів. { $online } зараз онлайн.
virtual-bots-already-filled = Усі віртуальні боти з конфігурації вже активні.
virtual-bots-cleared = Очищено { $bots } віртуальних ботів і знищено { $tables } { $tables ->
    [one] стіл
   *[other] столів
}.
virtual-bot-table-closed = Стіл закрито адміністратором.
virtual-bots-none-to-clear = Немає віртуальних ботів для очищення.
virtual-bots-status-report = Віртуальні боти: { $total } всього, { $online } онлайн, { $offline } офлайн, { $in_game } в грі.
virtual-bots-guided-overview = Керовані столи
virtual-bots-groups-overview = Групи ботів
virtual-bots-profiles-overview = Профілі
virtual-bots-guided-header = Керовані столи: { $count } правил(о). Розподіл: { $allocation }, резерв: { $fallback }, профіль за замовчуванням: { $default_profile }.
virtual-bots-guided-empty = Не налаштовано правил керованих столів.
virtual-bots-guided-status-active = активний
virtual-bots-guided-status-inactive = неактивний
virtual-bots-guided-table-linked = прив'язаний до столу { $table_id } (господар { $host }, гравців { $players }, людей { $humans })
virtual-bots-guided-table-stale = стіл { $table_id } відсутній на сервері
virtual-bots-guided-table-unassigned = наразі стіл не відстежується
virtual-bots-guided-next-change = наступна зміна через { $ticks } тиків
virtual-bots-guided-no-schedule = немає вікна планування
virtual-bots-guided-warning = ⚠ недозаповнений
virtual-bots-guided-line = { $table }: гра { $game }, пріоритет { $priority }, ботів { $assigned } (мін { $min_bots }, макс { $max_bots }), очікує { $waiting }, недоступні { $unavailable }, статус { $status }, профіль { $profile }, групи { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Групи ботів: { $count } тегів, { $bots } налаштованих ботів.
virtual-bots-groups-empty = Не визначено груп ботів.
virtual-bots-groups-line = { $group }: профіль { $profile }, ботів { $total } (онлайн { $online }, очікує { $waiting }, в грі { $in_game }, офлайн { $offline }), правил { $rules }.
virtual-bots-groups-no-rules = немає
virtual-bots-no-profile = за замовчуванням
virtual-bots-profile-inherit-default = успадковує профіль за замовчуванням
virtual-bots-profiles-header = Профілі: { $count } визначено (за замовчуванням: { $default_profile }).
virtual-bots-profiles-empty = Не визначено профілів.
virtual-bots-profiles-line = { $profile } ({ $bot_count } ботів) перевизначення: { $overrides }.
virtual-bots-profiles-no-overrides = успадковує базову конфігурацію

localization-in-progress-try-again = Локалізація ще завантажується. Будь ласка, спробуйте знову за хвилину.
