# Main UI messages for PlayPalace

# Game categories
category-card-games = Хөзрийн тоглоомууд
category-dice-games = Шоо тоглоомууд
category-rb-play-center = RB тоглоомын төв
category-poker = Покер
category-uncategorized = Ангилаагүй

# Menu titles
main-menu-title = Үндсэн цэс
play-menu-title = Тоглох
categories-menu-title = Тоглоомын ангиллууд
tables-menu-title = Боломжтой ширээнүүд

# Menu items
play = Тоглох
view-active-tables = Идэвхтэй ширээнүүдийг харах
options = Тохиргоо
logout = Гарах
back = Буцах
go-back = Буцах
context-menu = Контекст цэс.
no-actions-available = Үйлдэл боломжгүй.
create-table = Шинэ ширээ үүсгэх
join-as-player = Тоглогчоор нэгдэх
join-as-spectator = Үзэгчээр нэгдэх
leave-table = Ширээнээс гарах
start-game = Тоглоом эхлүүлэх
add-bot = Бот нэмэх
remove-bot = Бот устгах
actions-menu = Үйлдлийн цэс
save-table = Ширээг хадгалах
whose-turn = Хэний ээлж
whos-at-table = Ширээнд хэн байна
check-scores = Оноо шалгах
check-scores-detailed = Дэлгэрэнгүй оноо
check-game-options = Тоглоомын тохиргоог шалгах
no-game-options = Тоглоомын тохиргоо алга.

# Turn messages
game-player-skipped = { $player } алгасав.

# Table messages
table-created = { $host } шинэ { $game } ширээ үүсгэв.
table-joined = { $player } ширээнд нэгдэв.
table-left = { $player } ширээнээс гарав.
new-host = { $player } одоо хост болов.
waiting-for-players = Тоглогчдыг хүлээж байна. { $min } доод, { $max } дээд.
game-starting = Тоглоом эхэлж байна!
table-listing = { $host }-ын ширээ ({ $count } хэрэглэгч)
table-listing-one = { $host }-ын ширээ ({ $count } хэрэглэгч)
table-listing-with = { $host }-ын ширээ ({ $count } хэрэглэгч) { $members }-тай
table-listing-game = { $game }: { $host }-ын ширээ ({ $count } хэрэглэгч)
table-listing-game-one = { $game }: { $host }-ын ширээ ({ $count } хэрэглэгч)
table-listing-game-with = { $game }: { $host }-ын ширээ ({ $count } хэрэглэгч) { $members }-тай
table-not-exists = Ширээ байхгүй болсон.
table-full = Ширээ дүүрсэн.
player-replaced-by-bot = { $player } гарч, ботоор солигдов.
player-took-over = { $player } ботоос авав.
spectator-joined = { $host }-ын ширээнд үзэгчээр нэгдэв.

# Spectator mode
spectate = Үзэх
now-playing = { $player } одоо тоглож байна.
now-spectating = { $player } одоо үзэж байна.
spectator-left = { $player } үзэхээ больсон.

# General
welcome = PlayPalace-д тавтай морилно уу!
goodbye = Баяртай!

# User presence announcements
user-online = { $player } нэвтэрлээ.
user-offline = { $player } гарлаа.
user-is-admin = { $player } нь PlayPalace-ын админ юм.
user-is-server-owner = { $player } нь PlayPalace-ын серверийн эзэн юм.
online-users-none = Хэрэглэгч байхгүй байна.
online-users-one = 1 хэрэглэгч: { $users }
online-users-many = { $count } хэрэглэгч: { $users }
online-user-not-in-game = Тоглоомд ороогүй
online-user-waiting-approval = Зөвшөөрөл хүлээж байна

# Options
language = Хэл
language-option = Хэл: { $language }
language-changed = Хэл { $language } болгов.

# Boolean option states
option-on = Асаалттай
option-off = Унтраалттай

# Sound options
turn-sound-option = Ээлжийн дуу: { $status }

# Dice options
clear-kept-option = Шоо шидэхэд хадгалсныг цэвэрлэх: { $status }
dice-keeping-style-option = Шоо хадгалах арга: { $style }
dice-keeping-style-changed = Шоо хадгалах арга { $style } болгов.
dice-keeping-style-indexes = Шооны индекс
dice-keeping-style-values = Шооны утга

# Bot names
cancel = Цуцлах
no-bot-names-available = Ботын нэр байхгүй байна.
select-bot-name = Ботод нэр сонгох
enter-bot-name = Ботын нэр оруулах
no-options-available = Сонголт байхгүй байна.
no-scores-available = Оноо байхгүй байна.

# Duration estimation
estimate-duration = Үргэлжлэх хугацаа тооцох
estimate-computing = Тоглоомын үргэлжлэх хугацааг тооцож байна...
estimate-result = Ботын дундаж: { $bot_time } (± { $std_dev }). { $outlier_info }Хүний хугацаа: { $human_time }.
estimate-error = Үргэлжлэх хугацааг тооцож чадсангүй.
estimate-already-running = Үргэлжлэх хугацааг аль хэдийн тооцож байна.

# Save/Restore
saved-tables = Хадгалсан ширээнүүд
no-saved-tables = Танд хадгалсан ширээ байхгүй байна.
no-active-tables = Идэвхтэй ширээ байхгүй байна.
restore-table = Сэргээх
delete-saved-table = Устгах
saved-table-deleted = Хадгалсан ширээ устгагдав.
missing-players = Сэргээж чадахгүй: эдгээр тоглогчид байхгүй байна: { $players }
table-restored = Ширээ сэргээгдэв! Бүх тоглогчид шилжүүлэгдэв.
table-saved-destroying = Ширээ хадгалагдлаа! Үндсэн цэс рүү буцаж байна.
game-type-not-found = Тоглоомын төрөл байхгүй болсон.

# Action disabled reasons
action-not-your-turn = Таны ээлж биш байна.
action-not-playing = Тоглоом эхлээгүй байна.
action-spectator = Үзэгчид үүнийг хийж чадахгүй.
action-not-host = Зөвхөн хост үүнийг хийж болно.
action-game-in-progress = Тоглоом үргэлжилж байх үед үүнийг хийж болохгүй.
action-need-more-players = Эхлүүлэхэд илүү олон тоглогч хэрэгтэй.
action-table-full = Ширээ дүүрсэн байна.
action-no-bots = Устгах бот байхгүй байна.
action-bots-cannot = Ботууд үүнийг хийж чадахгүй.
action-no-scores = Оноо хараахан байхгүй байна.

# Dice actions
dice-not-rolled = Та хараахан шоо шидээгүй байна.
dice-locked = Энэ шоо түгжээтэй байна.
dice-no-dice = Шоо байхгүй байна.

# Game actions
game-turn-start = { $player }-ын ээлж.
game-no-turn = Одоо хэний ч ээлж биш байна.
table-no-players = Тоглогч байхгүй байна.
table-players-one = { $count } тоглогч: { $players }.
table-players-many = { $count } тоглогч: { $players }.
table-spectators = Үзэгчид: { $spectators }.
game-leave = Гарах
game-over = Тоглоом дууслаа
game-final-scores = Эцсийн оноо
game-points = { $count } { $count ->
    [one] оноо
   *[other] оноо
}
play = Тоглох

# Leaderboards
leaderboards = Тэргүүлэгчдийн самбар
leaderboards-menu-title = Тэргүүлэгчдийн самбар
leaderboards-select-game = Тэргүүлэгчдийн самбарыг харахын тулд тоглоом сонгох
leaderboard-no-data = Энэ тоглоомын тэргүүлэгчдийн самбарын өгөгдөл байхгүй байна.

# Leaderboard types
leaderboard-type-wins = Хожлын тэргүүн
leaderboard-type-rating = Чадварын үнэлгээ
leaderboard-type-total-score = Нийт оноо
leaderboard-type-high-score = Хамгийн өндөр оноо
leaderboard-type-games-played = Тоглосон тоглоомууд
leaderboard-type-avg-points-per-turn = Ээлж бүрийн дундаж оноо
leaderboard-type-best-single-turn = Хамгийн сайн ээлж
leaderboard-type-score-per-round = Тойрог бүрийн оноо

# Leaderboard headers
leaderboard-wins-header = { $game } - Хожлын тэргүүн
leaderboard-total-score-header = { $game } - Нийт оноо
leaderboard-high-score-header = { $game } - Хамгийн өндөр оноо
leaderboard-games-played-header = { $game } - Тоглосон тоглоомууд
leaderboard-rating-header = { $game } - Чадварын үнэлгээ
leaderboard-avg-points-header = { $game } - Ээлж бүрийн дундаж оноо
leaderboard-best-turn-header = { $game } - Хамгийн сайн ээлж
leaderboard-score-per-round-header = { $game } - Тойрог бүрийн оноо

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } { $wins ->
    [one] хожил
   *[other] хожил
} { $losses } { $losses ->
    [one] хожигдол
   *[other] хожигдол
}, { $percentage }% хожлын хувь
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } дундаж
leaderboard-games-entry = { $rank }. { $player }: { $value } тоглоом

# Player stats
leaderboard-player-stats = Таны статистик: { $wins } хожил, { $losses } хожигдол ({ $percentage }% хожлын хувь)
leaderboard-no-player-stats = Та энэ тоглоомыг хараахан тоглоогүй байна.

# Skill rating leaderboard
leaderboard-no-ratings = Энэ тоглоомын үнэлгээний өгөгдөл байхгүй байна.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } үнэлгээ ({ $mu } ± { $sigma })
leaderboard-player-rating = Таны үнэлгээ: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = Танд энэ тоглоомын үнэлгээ байхгүй байна.

# My Stats menu
my-stats = Миний статистик
my-stats-select-game = Статистикаа харахын тулд тоглоом сонгох
my-stats-no-data = Та энэ тоглоомыг хараахан тоглоогүй байна.
my-stats-no-games = Та ямар ч тоглоом тоглоогүй байна.
my-stats-header = { $game } - Таны статистик
my-stats-wins = Хожил: { $value }
my-stats-losses = Хожигдол: { $value }
my-stats-winrate = Хожлын хувь: { $value }%
my-stats-games-played = Тоглосон тоглоом: { $value }
my-stats-total-score = Нийт оноо: { $value }
my-stats-high-score = Хамгийн өндөр оноо: { $value }
my-stats-rating = Чадварын үнэлгээ: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = Чадварын үнэлгээ хараахан байхгүй
my-stats-avg-per-turn = Ээлж бүрийн дундаж оноо: { $value }
my-stats-best-turn = Хамгийн сайн ээлж: { $value }

# Prediction system
predict-outcomes = Үр дүнг таамаглах
predict-header = Таамагласан үр дүн (чадварын үнэлгээгээр)
predict-entry = { $rank }. { $player } (үнэлгээ: { $rating })
predict-entry-2p = { $rank }. { $player } (үнэлгээ: { $rating }, { $probability }% хожих магадлал)
predict-unavailable = Үнэлгээний таамаглал боломжгүй байна.
predict-need-players = Таамаглалд дор хаяж 2 хүний тоглогч хэрэгтэй.
action-need-more-humans = Илүү олон хүний тоглогч хэрэгтэй.
confirm-leave-game = Та ширээнээс гарахдаа итгэлтэй байна уу?
confirm-yes = Тийм
confirm-no = Үгүй

# Administration
administration = Администрац
admin-menu-title = Администрац

# Account approval
account-approval = Данс зөвшөөрөх
account-approval-menu-title = Данс зөвшөөрөх
no-pending-accounts = Хүлээгдэж буй данс байхгүй байна.
approve-account = Зөвшөөрөх
decline-account = Татгалзах
account-approved = { $player }-ын данс зөвшөөрөгдөв.
account-declined = { $player }-ын данс татгалзагдаж устгагдав.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = Таны данс админы зөвшөөрлийг хүлээж байна.
account-approved-welcome = Таны данс зөвшөөрөгдлөө! PlayPalace-д тавтай морилно уу!
account-declined-goodbye = Таны дансны хүсэлт татгалзагдав.
    Шалтгаан:
account-banned = Таны данс хориглогдсон бөгөөд хандаж болохгүй.

# Login errors
incorrect-username = Таны оруулсан хэрэглэгчийн нэр байхгүй байна.
incorrect-password = Таны оруулсан нууц үг буруу байна.
already-logged-in = Энэ данс аль хэдийн нэвтэрсэн байна.

# Нэвтрэх мэдээллийн баталгаажуулалт
credential-username-length = Хэрэглэгчийн нэр { $min }-аас { $max } тэмдэгтийн хооронд байх ёстой.
credential-password-length = Нууц үг { $min }-аас { $max } тэмдэгтийн хооронд байх ёстой.

# Хандалтын хязгаарлалт
rate-limit-login-ip = Энэ хаягаас хэт олон нэвтрэх оролдлого хийгдсэн. Хүлээгээд дахин оролдоно уу.
rate-limit-login-user = Энэ хэрэглэгчийн нэрээр хэт олон амжилтгүй нэвтрэх оролдлого хийгдсэн. Хүлээгээд дахин оролдоно уу.
rate-limit-registration = Энэ хаягаас хэт олон бүртгэлийн оролдлого хийгдсэн. Хүлээгээд дахин оролдоно уу.
rate-limit-refresh = Энэ хаягаас хэт олон шинэчлэлтийн оролдлого хийгдсэн. Хүлээгээд дахин оролдоно уу.

# Сесс/нэвтрэлтийн алдаа
account-not-found = Данс олдсонгүй.
session-expired = Сесс дууссан байна. Дахин нэвтэрнэ үү.
session-token-mismatch = Сессийн токен хэрэглэгчийн нэртэй таарахгүй байна.
refresh-token-expired = Шинэчлэлтийн токен дууссан байна. Дахин нэвтэрнэ үү.
refresh-token-mismatch = Шинэчлэлтийн токен хэрэглэгчийн нэртэй таарахгүй байна.

# Бүртгэл
registration-success = Бүртгэл амжилттай болсон! Таны данс зөвшөөрөлийг хүлээж байна.
registration-username-taken = Хэрэглэгчийн нэр аль хэдийн авагдсан байна. Өөр нэр сонгоно уу.

# Тохиргооны үндсэн утга
pref-invalid-value = Буруу сонголт, үндсэн утгыг ашиглана.

# Decline reason
decline-reason-prompt = Татгалзах шалтгааныг оруулах (эсвэл Escape дарж цуцлах):
account-action-empty-reason = Шалтгаан өгөөгүй.

# Admin notifications for account requests
account-request = дансны хүсэлт
account-action = дансны үйлдэл хийгдсэн

# Admin promotion/demotion
promote-admin = Админ болгох
demote-admin = Админаас буулгах
promote-admin-menu-title = Админ болгох
demote-admin-menu-title = Админаас буулгах
no-users-to-promote = Админ болгох хэрэглэгч байхгүй байна.
no-admins-to-demote = Буулгах админ байхгүй байна.
confirm-promote = Та { $player }-ыг админ болгохдоо итгэлтэй байна уу?
confirm-demote = Та { $player }-ыг админаас буулгахдаа итгэлтэй байна уу?
broadcast-to-all = Бүх хэрэглэгчид зарлах
broadcast-to-admins = Зөвхөн админуудад зарлах
broadcast-to-nobody = Чимээгүй (зарлахгүй)
promote-announcement = { $player } админ болсон!
promote-announcement-you = Та админ боллоо!
demote-announcement = { $player } админаас буугдсан.
demote-announcement-you = Та админаас буугдлаа.
not-admin-anymore = Та админ байхаа больсон тул энэ үйлдлийг хийж чадахгүй.
not-server-owner = Зөвхөн серверийн эзэн энэ үйлдлийг хийж чадна.

# Server ownership transfer
transfer-ownership = Эзэмшил шилжүүлэх
transfer-ownership-menu-title = Эзэмшил шилжүүлэх
no-admins-for-transfer = Эзэмшил шилжүүлэх админ байхгүй байна.
confirm-transfer-ownership = Та серверийн эзэмшлийг { $player } руу шилжүүлэхдээ итгэлтэй байна уу? Та админ болж буугдана.
transfer-ownership-announcement = { $player } одоо PlayPalace серверийн эзэн болов!
transfer-ownership-announcement-you = Та одоо PlayPalace серверийн эзэн боллоо!

# User banning
ban-user = Хэрэглэгч хориглох
unban-user = Хоригийг цуцлах
no-users-to-ban = Хориглох хэрэглэгч байхгүй байна.
no-users-to-unban = Хориг цуцлах хэрэглэгч байхгүй байна.
confirm-ban = Та { $player }-ыг хориглохдоо итгэлтэй байна уу?
confirm-unban = Та { $player }-ын хоригийг цуцлахдаа итгэлтэй байна уу?
ban-reason-prompt = Хоригийн шалтгааныг оруулах (сонголттой):
unban-reason-prompt = Хориг цуцлах шалтгааныг оруулах (сонголттой):
user-banned = { $player } хориглогдов.
user-unbanned = { $player }-ын хориг цуцлагдав.
you-have-been-banned = Та энэ серверээс хориглогдлоо.
    Шалтгаан:
you-have-been-unbanned = Таны хориг цуцлагдлаа.
    Шалтгаан:
ban-no-reason = Шалтгаан өгөөгүй.

# Virtual bots (server owner only)
virtual-bots = Виртуал ботууд
virtual-bots-fill = Серверийг дүүргэх
virtual-bots-clear = Бүх ботыг устгах
virtual-bots-status = Төлөв
virtual-bots-clear-confirm = Та бүх виртуал ботыг устгахдаа итгэлтэй байна уу? Энэ нь тэдний байгаа ширээнүүдийг бас устгана.
virtual-bots-not-available = Виртуал ботууд боломжгүй байна.
virtual-bots-filled = { $added } виртуал бот нэмэгдэв. { $online } одоо нэвтэрсэн байна.
virtual-bots-already-filled = Тохиргооны бүх виртуал ботууд аль хэдийн идэвхтэй байна.
virtual-bots-cleared = { $bots } виртуал бот устгагдаж { $tables } { $tables ->
    [one] ширээ
   *[other] ширээ
} устгагдлаа.
virtual-bot-table-closed = Ширээг админ хаасан.
virtual-bots-none-to-clear = Устгах виртуал бот байхгүй байна.
virtual-bots-status-report = Виртуал ботууд: { $total } нийт, { $online } нэвтэрсэн, { $offline } гарсан, { $in_game } тоглоомд байгаа.
virtual-bots-guided-overview = Удирдагдсан ширээнүүд
virtual-bots-groups-overview = Ботын бүлгүүд
virtual-bots-profiles-overview = Профайлууд
virtual-bots-guided-header = Удирдагдсан ширээнүүд: { $count } дүрэм. Хуваарилалт: { $allocation }, буцаах: { $fallback }, үндсэн профайл: { $default_profile }.
virtual-bots-guided-empty = Удирдагдсан ширээний дүрэм тохируулаагүй байна.
virtual-bots-guided-status-active = идэвхтэй
virtual-bots-guided-status-inactive = идэвхгүй
virtual-bots-guided-table-linked = ширээ { $table_id } холбогдсон (хост { $host }, тоглогчид { $players }, хүмүүс { $humans })
virtual-bots-guided-table-stale = ширээ { $table_id } серверт байхгүй байна
virtual-bots-guided-table-unassigned = одоогоор ширээ байхгүй байна
virtual-bots-guided-next-change = дараагийн өөрчлөлт { $ticks } тик-д
virtual-bots-guided-no-schedule = цагийн хүрээ байхгүй
virtual-bots-guided-warning = ⚠ дутуу
virtual-bots-guided-line = { $table }: тоглоом { $game }, давуу эрх { $priority }, ботууд { $assigned } (дор хаяж { $min_bots }, дээд { $max_bots }), хүлээж байгаа { $waiting }, боломжгүй { $unavailable }, төлөв { $status }, профайл { $profile }, бүлгүүд { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = Ботын бүлгүүд: { $count } шошго, { $bots } тохируулсан бот.
virtual-bots-groups-empty = Ботын бүлэг тодорхойлоогүй байна.
virtual-bots-groups-line = { $group }: профайл { $profile }, ботууд { $total } (нэвтэрсэн { $online }, хүлээж байгаа { $waiting }, тоглоомд байгаа { $in_game }, гарсан { $offline }), дүрмүүд { $rules }.
virtual-bots-groups-no-rules = байхгүй
virtual-bots-no-profile = үндсэн
virtual-bots-profile-inherit-default = үндсэн профайлаас өвлөнө
virtual-bots-profiles-header = Профайлууд: { $count } тодорхойлогдсон (үндсэн: { $default_profile }).
virtual-bots-profiles-empty = Профайл тодорхойлоогүй байна.
virtual-bots-profiles-line = { $profile } ({ $bot_count } бот) дарж бичих: { $overrides }.
virtual-bots-profiles-no-overrides = үндсэн тохиргооноос өвлөнө

localization-in-progress-try-again = Нутагшуулалт хийгдэж байна. Нэг минутын дараа дахин оролдоно уу.
