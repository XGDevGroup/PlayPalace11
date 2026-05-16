# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = نود و نه

# Round and turn flow
game-round-start = دور { $round }.
game-round-end = دور { $round } تمام شد.
game-turn-start = نوبت { $player }.
game-your-turn = نوبت شماست.
game-no-turn = الان نوبت کسی نیست.

# Score display
game-scores-header = امتیازات فعلی:
game-score-line = { $player }: { $score } امتیاز
game-final-scores-header = امتیازات نهایی:

# Win/loss
game-winner = { $player } برنده می‌شود!
game-winner-score = { $player } با { $score } امتیاز برنده می‌شود!
game-tiebreaker = مساوی! دور تعیین‌کننده!
game-tiebreaker-players = مساوی بین { $players }! دور تعیین‌کننده!
game-eliminated = { $player } با { $score } امتیاز حذف شد.

# Common options
game-set-target-score = امتیاز هدف: { $score }
game-enter-target-score = امتیاز هدف را وارد کنید:
game-option-changed-target = امتیاز هدف به { $score } تنظیم شد.

game-set-team-mode = حالت تیمی: { $mode }
game-select-team-mode = حالت تیمی را انتخاب کنید
game-option-changed-team = حالت تیمی به { $mode } تنظیم شد.
game-team-mode-individual = انفرادی
game-team-mode-x-teams-of-y = { $num_teams } تیم { $team_size } نفره

# Boolean option values
option-on = روشن
option-off = خاموش

# Status box

# Game end
game-leave = خروج از بازی

# Round timer
round-timer-paused = { $player } بازی را متوقف کرده است (برای شروع دور بعدی p را فشار دهید).
round-timer-resumed = تایمر دور از سر گرفته شد.
round-timer-countdown = دور بعدی در { $seconds }...

# Dice games - keeping/releasing dice
dice-keeping = نگه‌داری { $value }.
dice-rerolling = انداختن دوباره { $value }.
dice-locked = آن تاس قفل است و نمی‌توان تغییر داد.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = پخش { $current }/{ $total }.
game-you-deal = شما کارت‌ها را پخش می‌کنید.
game-player-deals = { $player } کارت‌ها را پخش می‌کند.

# Card names
card-name = { $rank } { $suit }
no-cards = بدون کارت

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = سیاه
color-black-m = سیاه
color-black-f = سیاه
color-blue = آبی
color-blue-m = آبی
color-blue-f = آبی
color-brown = قهوه‌ای
color-brown-m = قهوه‌ای
color-brown-f = قهوه‌ای
color-gray = خاکستری
color-gray-m = خاکستری
color-gray-f = خاکستری
color-green = سبز
color-green-m = سبز
color-green-f = سبز
color-indigo = نیلی
color-indigo-m = نیلی
color-indigo-f = نیلی
color-orange = نارنجی
color-orange-m = نارنجی
color-orange-f = نارنجی
color-pink = صورتی
color-pink-m = صورتی
color-pink-f = صورتی
color-purple = بنفش
color-purple-m = بنفش
color-purple-f = بنفش
color-red = قرمز
color-red-m = قرمز
color-red-f = قرمز
color-violet = بنفش
color-violet-m = بنفش
color-violet-f = بنفش
color-white = سفید
color-white-m = سفید
color-white-f = سفید
color-yellow = زرد
color-yellow-m = زرد
color-yellow-f = زرد

# Suit names
suit-diamonds = خشت
suit-clubs = گشنیز
suit-hearts = دل
suit-spades = پیک

# Rank names
rank-ace = اُس
rank-ace-plural = اُس‌ها
rank-two = ۲
rank-two-plural = ۲ها
rank-three = ۳
rank-three-plural = ۳ها
rank-four = ۴
rank-four-plural = ۴ها
rank-five = ۵
rank-five-plural = ۵ها
rank-six = ۶
rank-six-plural = ۶ها
rank-seven = ۷
rank-seven-plural = ۷ها
rank-eight = ۸
rank-eight-plural = ۸ها
rank-nine = ۹
rank-nine-plural = ۹ها
rank-ten = ۱۰
rank-ten-plural = ۱۰ها
rank-jack = سرباز
rank-jack-plural = سربازها
rank-queen = بی‌بی
rank-queen-plural = بی‌بی‌ها
rank-king = شاه
rank-king-plural = شاه‌ها

# Poker hand descriptions
poker-high-card-with = { $high } بالا، با { $rest }
poker-high-card = { $high } بالا
poker-pair-with = یک جفت { $pair }، با { $rest }
poker-pair = یک جفت { $pair }
poker-two-pair-with = دو جفت، { $high } و { $low }، با { $kicker }
poker-two-pair = دو جفت، { $high } و { $low }
poker-trips-with = سه‌تا یکی، { $trips }، با { $rest }
poker-trips = سه‌تا یکی، { $trips }
poker-straight-high = ترتیب { $high } بالا
poker-flush-high-with = فلاش { $high } بالا، با { $rest }
poker-full-house = فول هاوس، { $trips } روی { $pair }
poker-quads-with = چهارتا یکی، { $quads }، با { $kicker }
poker-quads = چهارتا یکی، { $quads }
poker-straight-flush-high = استریت فلاش { $high } بالا
poker-unknown-hand = دست ناشناخته

# Validation errors (common across games)
game-error-invalid-team-mode = حالت تیمی انتخاب شده برای تعداد بازیکنان فعلی معتبر نیست.
