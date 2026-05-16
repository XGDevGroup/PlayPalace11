# Main UI messages for PlayPalace

# Game categories
category-card-games = بازی‌های ورق
category-dice-games = بازی‌های تاس
category-rb-play-center = مرکز بازی RB
category-poker = پوکر
category-uncategorized = دسته‌بندی نشده

# Menu titles
main-menu-title = منوی اصلی
play-menu-title = بازی
categories-menu-title = دسته‌های بازی
tables-menu-title = میزهای موجود

# Menu items
play = بازی
view-active-tables = مشاهده میزهای فعال
options = تنظیمات
logout = خروج
back = بازگشت
go-back = بازگشت
context-menu = منوی زمینه.
no-actions-available = هیچ اقدامی در دسترس نیست.
create-table = ایجاد میز جدید
join-as-player = پیوستن به عنوان بازیکن
join-as-spectator = پیوستن به عنوان تماشاگر
leave-table = ترک میز
start-game = شروع بازی
add-bot = افزودن ربات
remove-bot = حذف ربات
actions-menu = منوی اقدامات
save-table = ذخیره میز
whose-turn = نوبت کیست
whos-at-table = چه کسانی پشت میز هستند
check-scores = بررسی امتیازها
check-scores-detailed = امتیازهای تفصیلی
check-game-options = بررسی گزینه‌های بازی
no-game-options = هیچ گزینه‌ای برای بازی وجود ندارد.

# Turn messages
game-player-skipped = { $player } رد شد.

# Table messages
table-created = { $host } یک میز { $game } جدید ایجاد کرد.
table-joined = { $player } به میز پیوست.
table-left = { $player } میز را ترک کرد.
new-host = { $player } اکنون میزبان است.
waiting-for-players = در انتظار بازیکنان. حداقل { $min }، حداکثر { $max }.
game-starting = بازی شروع می‌شود!
table-listing = میز { $host } ({ $count } کاربر)
table-listing-one = میز { $host } ({ $count } کاربر)
table-listing-with = میز { $host } ({ $count } کاربر) با { $members }
table-listing-game = { $game }: میز { $host } ({ $count } کاربر)
table-listing-game-one = { $game }: میز { $host } ({ $count } کاربر)
table-listing-game-with = { $game }: میز { $host } ({ $count } کاربر) با { $members }
table-not-exists = میز دیگر وجود ندارد.
table-full = میز پر است.
player-replaced-by-bot = { $player } میز را ترک کرد و با ربات جایگزین شد.
player-took-over = { $player } جای ربات را گرفت.
spectator-joined = به میز { $host } به عنوان تماشاگر پیوستید.

# Spectator mode
spectate = تماشا
now-playing = { $player } اکنون در حال بازی است.
now-spectating = { $player } اکنون تماشاگر است.
spectator-left = { $player } تماشا را متوقف کرد.

# General
welcome = به PlayPalace خوش آمدید!
goodbye = خداحافظ!

# User presence announcements
user-online = { $player } آنلاین شد.
user-offline = { $player } آفلاین شد.
user-is-admin = { $player } مدیر PlayPalace است.
user-is-server-owner = { $player } مالک سرور PlayPalace است.
online-users-none = هیچ کاربری آنلاین نیست.
online-users-one = ۱ کاربر: { $users }
online-users-many = { $count } کاربر: { $users }
online-user-not-in-game = در بازی نیست
online-user-waiting-approval = در انتظار تأیید

# Options
language = زبان
language-option = زبان: { $language }
language-changed = زبان به { $language } تغییر کرد.

# Boolean option states
option-on = روشن
option-off = خاموش

# Sound options
turn-sound-option = صدای نوبت: { $status }

# Dice options
clear-kept-option = پاک کردن تاس‌های نگه‌داشته شده هنگام پرتاب: { $status }
dice-keeping-style-option = سبک نگهداری تاس: { $style }
dice-keeping-style-changed = سبک نگهداری تاس به { $style } تغییر کرد.
dice-keeping-style-indexes = شاخص‌های تاس
dice-keeping-style-values = مقادیر تاس

# Bot names
cancel = لغو
no-bot-names-available = هیچ نام رباتی موجود نیست.
select-bot-name = یک نام برای ربات انتخاب کنید
enter-bot-name = نام ربات را وارد کنید
no-options-available = هیچ گزینه‌ای موجود نیست.
no-scores-available = هیچ امتیازی موجود نیست.

# Duration estimation
estimate-duration = تخمین مدت زمان
estimate-computing = در حال محاسبه مدت زمان تخمینی بازی...
estimate-result = میانگین ربات: { $bot_time } (± { $std_dev }). { $outlier_info }زمان تخمینی انسان: { $human_time }.
estimate-error = نتوانست مدت زمان را تخمین بزند.
estimate-already-running = تخمین مدت زمان در حال اجرا است.

# Save/Restore
saved-tables = میزهای ذخیره شده
no-saved-tables = شما هیچ میز ذخیره‌شده‌ای ندارید.
no-active-tables = هیچ میز فعالی وجود ندارد.
restore-table = بازیابی
delete-saved-table = حذف
saved-table-deleted = میز ذخیره‌شده حذف شد.
missing-players = نمی‌توان بازیابی کرد: این بازیکنان در دسترس نیستند: { $players }
table-restored = میز بازیابی شد! همه بازیکنان منتقل شدند.
table-saved-destroying = میز ذخیره شد! بازگشت به منوی اصلی.
game-type-not-found = نوع بازی دیگر وجود ندارد.

# Action disabled reasons
action-not-your-turn = نوبت شما نیست.
action-not-playing = بازی شروع نشده است.
action-spectator = تماشاگران نمی‌توانند این کار را انجام دهند.
action-not-host = فقط میزبان می‌تواند این کار را انجام دهد.
action-game-in-progress = نمی‌توان این کار را در حین بازی انجام داد.
action-need-more-players = برای شروع به بازیکنان بیشتری نیاز است.
action-table-full = میز پر است.
action-no-bots = هیچ رباتی برای حذف وجود ندارد.
action-bots-cannot = ربات‌ها نمی‌توانند این کار را انجام دهند.
action-no-scores = هنوز امتیازی موجود نیست.

# Dice actions
dice-not-rolled = شما هنوز تاس نریخته‌اید.
dice-locked = این تاس قفل شده است.
dice-no-dice = هیچ تاسی موجود نیست.

# Game actions
game-turn-start = نوبت { $player }.
game-no-turn = در حال حاضر نوبت کسی نیست.
table-no-players = بازیکنی وجود ندارد.
table-players-one = { $count } بازیکن: { $players }.
table-players-many = { $count } بازیکن: { $players }.
table-spectators = تماشاگران: { $spectators }.
game-leave = ترک
game-over = بازی تمام شد
game-final-scores = امتیازهای نهایی
game-points = { $count } { $count ->
    [one] امتیاز
   *[other] امتیاز
}
play = بازی

# Leaderboards
leaderboards = جداول برتر
leaderboards-menu-title = جداول برتر
leaderboards-select-game = یک بازی را برای مشاهده جدول برترش انتخاب کنید
leaderboard-no-data = هنوز داده‌ای برای جدول برتر این بازی وجود ندارد.

# Leaderboard types
leaderboard-type-wins = برترین‌های برنده
leaderboard-type-rating = رتبه‌بندی مهارت
leaderboard-type-total-score = امتیاز کل
leaderboard-type-high-score = بالاترین امتیاز
leaderboard-type-games-played = بازی‌های انجام شده
leaderboard-type-avg-points-per-turn = میانگین امتیاز هر نوبت
leaderboard-type-best-single-turn = بهترین نوبت تکی
leaderboard-type-score-per-round = امتیاز هر دور

# Leaderboard headers
leaderboard-wins-header = { $game } - برترین‌های برنده
leaderboard-total-score-header = { $game } - امتیاز کل
leaderboard-high-score-header = { $game } - بالاترین امتیاز
leaderboard-games-played-header = { $game } - بازی‌های انجام شده
leaderboard-rating-header = { $game } - رتبه‌بندی مهارت
leaderboard-avg-points-header = { $game } - میانگین امتیاز هر نوبت
leaderboard-best-turn-header = { $game } - بهترین نوبت تکی
leaderboard-score-per-round-header = { $game } - امتیاز هر دور

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }، { $wins } { $wins ->
    [one] برد
   *[other] برد
} { $losses } { $losses ->
    [one] باخت
   *[other] باخت
}، { $percentage }٪ نرخ برد
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } میانگین
leaderboard-games-entry = { $rank }. { $player }: { $value } بازی

# Player stats
leaderboard-player-stats = آمار شما: { $wins } برد، { $losses } باخت ({ $percentage }٪ نرخ برد)
leaderboard-no-player-stats = شما هنوز این بازی را انجام نداده‌اید.

# Skill rating leaderboard
leaderboard-no-ratings = هنوز داده‌ای برای رتبه‌بندی این بازی وجود ندارد.
leaderboard-rating-entry = { $rank }. { $player }: { $rating } رتبه ({ $mu } ± { $sigma })
leaderboard-player-rating = رتبه شما: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = شما هنوز رتبه‌ای برای این بازی ندارید.

# My Stats menu
my-stats = آمار من
my-stats-select-game = یک بازی را برای مشاهده آمار خود انتخاب کنید
my-stats-no-data = شما هنوز این بازی را انجام نداده‌اید.
my-stats-no-games = شما هنوز هیچ بازی‌ای انجام نداده‌اید.
my-stats-header = { $game } - آمار شما
my-stats-wins = برد: { $value }
my-stats-losses = باخت: { $value }
my-stats-winrate = نرخ برد: { $value }٪
my-stats-games-played = بازی‌های انجام شده: { $value }
my-stats-total-score = امتیاز کل: { $value }
my-stats-high-score = بالاترین امتیاز: { $value }
my-stats-rating = رتبه‌بندی مهارت: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = هنوز رتبه‌بندی مهارتی وجود ندارد
my-stats-avg-per-turn = میانگین امتیاز هر نوبت: { $value }
my-stats-best-turn = بهترین نوبت تکی: { $value }

# Prediction system
predict-outcomes = پیش‌بینی نتایج
predict-header = نتایج پیش‌بینی‌شده (بر اساس رتبه‌بندی مهارت)
predict-entry = { $rank }. { $player } (رتبه: { $rating })
predict-entry-2p = { $rank }. { $player } (رتبه: { $rating }، { $probability }٪ احتمال برد)
predict-unavailable = پیش‌بینی رتبه‌بندی در دسترس نیست.
predict-need-players = برای پیش‌بینی به حداقل ۲ بازیکن انسانی نیاز است.
action-need-more-humans = به بازیکنان انسانی بیشتری نیاز است.
confirm-leave-game = آیا مطمئن هستید که می‌خواهید میز را ترک کنید؟
confirm-yes = بله
confirm-no = خیر

# Administration
administration = مدیریت
admin-menu-title = مدیریت

# Account approval
account-approval = تأیید حساب
account-approval-menu-title = تأیید حساب
no-pending-accounts = هیچ حساب در انتظاری وجود ندارد.
approve-account = تأیید
decline-account = رد
account-approved = حساب { $player } تأیید شد.
account-declined = حساب { $player } رد و حذف شد.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = حساب شما در انتظار تأیید توسط مدیر است.
account-approved-welcome = حساب شما تأیید شد! به PlayPalace خوش آمدید!
account-declined-goodbye = درخواست حساب شما رد شد.
    دلیل:
account-banned = حساب شما مسدود شده و قابل دسترسی نیست.

# Login errors
incorrect-username = نام کاربری وارد شده وجود ندارد.
incorrect-password = رمز عبور وارد شده نادرست است.
already-logged-in = این حساب قبلاً وارد شده است.

# اعتبارسنجی اطلاعات ورود
credential-username-length = نام کاربری باید بین { $min } تا { $max } کاراکتر باشد.
credential-password-length = رمز عبور باید بین { $min } تا { $max } کاراکتر باشد.

# محدودیت نرخ درخواست
rate-limit-login-ip = تعداد زیادی تلاش برای ورود از این آدرس. لطفاً صبر کنید و دوباره امتحان کنید.
rate-limit-login-user = تعداد زیادی تلاش ناموفق برای ورود با این نام کاربری. لطفاً صبر کنید و دوباره امتحان کنید.
rate-limit-registration = تعداد زیادی تلاش برای ثبت‌نام از این آدرس. لطفاً صبر کنید و دوباره امتحان کنید.
rate-limit-refresh = تعداد زیادی تلاش برای بازآوری از این آدرس. لطفاً صبر کنید و دوباره امتحان کنید.

# خطاهای جلسه و احراز هویت
account-not-found = حساب یافت نشد.
session-expired = جلسه منقضی شده است. لطفاً دوباره وارد شوید.
session-token-mismatch = توکن جلسه با نام کاربری مطابقت ندارد.
refresh-token-expired = توکن بازآوری منقضی شده است. لطفاً دوباره وارد شوید.
refresh-token-mismatch = توکن بازآوری با نام کاربری مطابقت ندارد.

# ثبت‌نام
registration-success = ثبت‌نام موفقیت‌آمیز بود! حساب شما در انتظار تأیید است.
registration-username-taken = این نام کاربری قبلاً گرفته شده است. لطفاً نام کاربری دیگری انتخاب کنید.

# مقدار پیش‌فرض تنظیمات
pref-invalid-value = انتخاب نامعتبر است، از مقدار پیش‌فرض استفاده می‌شود.

# Decline reason
decline-reason-prompt = دلیل رد را وارد کنید (یا Escape را فشار دهید تا لغو شود):
account-action-empty-reason = دلیلی ارائه نشد.

# Admin notifications for account requests
account-request = درخواست حساب
account-action = اقدام روی حساب انجام شد

# Admin promotion/demotion
promote-admin = ارتقا به مدیر
demote-admin = کاهش رتبه مدیر
promote-admin-menu-title = ارتقا به مدیر
demote-admin-menu-title = کاهش رتبه مدیر
no-users-to-promote = هیچ کاربری برای ارتقا موجود نیست.
no-admins-to-demote = هیچ مدیری برای کاهش رتبه موجود نیست.
confirm-promote = آیا مطمئن هستید که می‌خواهید { $player } را به مدیر ارتقا دهید؟
confirm-demote = آیا مطمئن هستید که می‌خواهید { $player } را از مدیر کاهش دهید؟
broadcast-to-all = اعلام به همه کاربران
broadcast-to-admins = اعلام فقط به مدیران
broadcast-to-nobody = بی‌صدا (بدون اعلام)
promote-announcement = { $player } به مدیر ارتقا یافت!
promote-announcement-you = شما به مدیر ارتقا یافتید!
demote-announcement = { $player } از مدیر کاهش یافت.
demote-announcement-you = شما از مدیر کاهش یافتید.
not-admin-anymore = شما دیگر مدیر نیستید و نمی‌توانید این اقدام را انجام دهید.
not-server-owner = فقط مالک سرور می‌تواند این اقدام را انجام دهد.

# Server ownership transfer
transfer-ownership = انتقال مالکیت
transfer-ownership-menu-title = انتقال مالکیت
no-admins-for-transfer = هیچ مدیری برای انتقال مالکیت موجود نیست.
confirm-transfer-ownership = آیا مطمئن هستید که می‌خواهید مالکیت سرور را به { $player } منتقل کنید؟ شما به مدیر کاهش می‌یابید.
transfer-ownership-announcement = { $player } اکنون مالک سرور Play Palace است!
transfer-ownership-announcement-you = شما اکنون مالک سرور Play Palace هستید!

# User banning
ban-user = مسدود کردن کاربر
unban-user = رفع مسدودیت کاربر
no-users-to-ban = هیچ کاربری برای مسدود کردن موجود نیست.
no-users-to-unban = هیچ کاربر مسدودی برای رفع مسدودیت وجود ندارد.
confirm-ban = آیا مطمئن هستید که می‌خواهید { $player } را مسدود کنید؟
confirm-unban = آیا مطمئن هستید که می‌خواهید مسدودیت { $player } را رفع کنید؟
ban-reason-prompt = دلیل مسدودیت را وارد کنید (اختیاری):
unban-reason-prompt = دلیل رفع مسدودیت را وارد کنید (اختیاری):
user-banned = { $player } مسدود شد.
user-unbanned = مسدودیت { $player } رفع شد.
you-have-been-banned = شما از این سرور مسدود شده‌اید.
    دلیل:
you-have-been-unbanned = مسدودیت شما از این سرور رفع شد.
    دلیل:
ban-no-reason = دلیلی ارائه نشد.

# Virtual bots (server owner only)
virtual-bots = ربات‌های مجازی
virtual-bots-fill = پر کردن سرور
virtual-bots-clear = پاک کردن همه ربات‌ها
virtual-bots-status = وضعیت
virtual-bots-clear-confirm = آیا مطمئن هستید که می‌خواهید همه ربات‌های مجازی را پاک کنید؟ این کار میزهایی که آن‌ها در آن هستند را نیز از بین می‌برد.
virtual-bots-not-available = ربات‌های مجازی در دسترس نیستند.
virtual-bots-filled = { $added } ربات مجازی اضافه شد. { $online } اکنون آنلاین هستند.
virtual-bots-already-filled = همه ربات‌های مجازی از پیکربندی قبلاً فعال هستند.
virtual-bots-cleared = { $bots } ربات مجازی پاک شد و { $tables } { $tables ->
    [one] میز
   *[other] میز
} از بین رفت.
virtual-bot-table-closed = میز توسط مدیر بسته شد.
virtual-bots-none-to-clear = هیچ ربات مجازی برای پاک کردن وجود ندارد.
virtual-bots-status-report = ربات‌های مجازی: { $total } مجموع، { $online } آنلاین، { $offline } آفلاین، { $in_game } در بازی.
virtual-bots-guided-overview = میزهای راهنمایی‌شده
virtual-bots-groups-overview = گروه‌های ربات
virtual-bots-profiles-overview = پروفایل‌ها
virtual-bots-guided-header = میزهای راهنمایی‌شده: { $count } قانون. تخصیص: { $allocation }، پیش‌فرض: { $fallback }، پروفایل پیش‌فرض: { $default_profile }.
virtual-bots-guided-empty = هیچ قانون میز راهنمایی‌شده‌ای پیکربندی نشده است.
virtual-bots-guided-status-active = فعال
virtual-bots-guided-status-inactive = غیرفعال
virtual-bots-guided-table-linked = پیوند به میز { $table_id } (میزبان { $host }، بازیکنان { $players }، انسان‌ها { $humans })
virtual-bots-guided-table-stale = میز { $table_id } در سرور موجود نیست
virtual-bots-guided-table-unassigned = در حال حاضر هیچ میزی ردیابی نمی‌شود
virtual-bots-guided-next-change = تغییر بعدی در { $ticks } تیک
virtual-bots-guided-no-schedule = هیچ بازه زمانبندی‌ای وجود ندارد
virtual-bots-guided-warning = ⚠ ناقص پر شده
virtual-bots-guided-line = { $table }: بازی { $game }، اولویت { $priority }، ربات‌ها { $assigned } (حداقل { $min_bots }، حداکثر { $max_bots })، در انتظار { $waiting }، در دسترس نیست { $unavailable }، وضعیت { $status }، پروفایل { $profile }، گروه‌ها { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = گروه‌های ربات: { $count } برچسب، { $bots } ربات پیکربندی‌شده.
virtual-bots-groups-empty = هیچ گروه رباتی تعریف نشده است.
virtual-bots-groups-line = { $group }: پروفایل { $profile }، ربات‌ها { $total } (آنلاین { $online }، در انتظار { $waiting }، در بازی { $in_game }، آفلاین { $offline })، قوانین { $rules }.
virtual-bots-groups-no-rules = هیچ‌کدام
virtual-bots-no-profile = پیش‌فرض
virtual-bots-profile-inherit-default = ارث‌بری پروفایل پیش‌فرض
virtual-bots-profiles-header = پروفایل‌ها: { $count } تعریف‌شده (پیش‌فرض: { $default_profile }).
virtual-bots-profiles-empty = هیچ پروفایلی تعریف نشده است.
virtual-bots-profiles-line = { $profile } ({ $bot_count } ربات) بازنویسی‌ها: { $overrides }.
virtual-bots-profiles-no-overrides = ارث‌بری پیکربندی پایه

localization-in-progress-try-again = بومی‌سازی در حال انجام است. لطفاً یک دقیقه دیگر دوباره تلاش کنید.
