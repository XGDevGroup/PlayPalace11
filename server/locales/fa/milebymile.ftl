# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = مایل به مایل

# Game options
milebymile-set-distance = فاصله مسابقه: { $miles } مایل
milebymile-enter-distance = فاصله مسابقه را وارد کنید (۳۰۰-۳۰۰۰)
milebymile-set-winning-score = امتیاز برنده: { $score } امتیاز
milebymile-enter-winning-score = امتیاز برنده را وارد کنید (۱۰۰۰-۱۰۰۰۰)
milebymile-toggle-perfect-crossing = نیاز به پایان دقیق: { $enabled }
milebymile-toggle-stacking = اجازه انباشت حملات: { $enabled }
milebymile-toggle-reshuffle = مخلوط مجدد دور ریخته‌ها: { $enabled }
milebymile-toggle-karma = قانون کارما: { $enabled }
milebymile-set-rig = تقلب دسته: { $rig }
milebymile-select-rig = گزینه تقلب دسته را انتخاب کنید

# Option change announcements
milebymile-option-changed-distance = فاصله مسابقه به { $miles } مایل تنظیم شد.
milebymile-option-changed-winning = امتیاز برنده به { $score } امتیاز تنظیم شد.
milebymile-option-changed-crossing = نیاز به پایان دقیق { $enabled }.
milebymile-option-changed-stacking = اجازه انباشت حملات { $enabled }.
milebymile-option-changed-reshuffle = مخلوط مجدد دور ریخته‌ها { $enabled }.
milebymile-option-changed-karma = قانون کارما { $enabled }.
milebymile-option-changed-rig = تقلب دسته به { $rig } تنظیم شد.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } امتیاز، { $miles } مایل، مشکلات: { $problems }، ایمنی‌ها: { $safeties }

# Card actions
milebymile-no-matching-safety = شما کارت ایمنی مطابق ندارید!
milebymile-cant-play = شما نمی‌توانید { $card } بازی کنید چون { $reason }.
milebymile-no-card-selected = کارتی برای دور انداختن انتخاب نشده است.
milebymile-no-valid-targets = هدف معتبری برای این خطر نیست!
milebymile-you-drew = شما کشیدید: { $card }
milebymile-discards = { $player } کارتی دور می‌اندازد.
milebymile-select-target = هدفی انتخاب کنید

# Distance plays
milebymile-plays-distance-individual = { $player } { $distance } مایل بازی می‌کند و حالا در { $total } مایل است.
milebymile-plays-distance-team = { $player } { $distance } مایل بازی می‌کند؛ تیم آن‌ها حالا در { $total } مایل است.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } سفر را با یک عبور کامل به پایان رسانده است!
milebymile-journey-complete-perfect-team = تیم { $team } سفر را با یک عبور کامل به پایان رسانده است!
milebymile-journey-complete-individual = { $player } سفر را به پایان رسانده است!
milebymile-journey-complete-team = تیم { $team } سفر را به پایان رسانده است!

# Hazard plays
milebymile-plays-hazard-individual = { $player } { $card } را روی { $target } بازی می‌کند.
milebymile-plays-hazard-team = { $player } { $card } را روی تیم { $team } بازی می‌کند.

# Remedy/Safety plays
milebymile-plays-card = { $player } { $card } را بازی می‌کند.
milebymile-plays-dirty-trick = { $player } { $card } را به عنوان یک ترفند کثیف بازی می‌کند!

# Deck
milebymile-deck-reshuffled = دور ریخته‌ها دوباره در دسته مخلوط شدند.

# Race
milebymile-new-race = مسابقه جدید شروع می‌شود!
milebymile-race-complete = مسابقه تمام شد! در حال محاسبه امتیازها...
milebymile-earned-points = { $name } این مسابقه { $score } امتیاز به دست آورد: { $breakdown }.
milebymile-total-scores = امتیازهای کل:
milebymile-team-score = { $name }: { $score } امتیاز

# Scoring breakdown
milebymile-from-distance = { $miles } از فاصله طی شده
milebymile-from-trip = { $points } از تکمیل سفر
milebymile-from-perfect = { $points } از یک عبور کامل
milebymile-from-safe = { $points } از یک سفر ایمن
milebymile-from-shutout = { $points } از یک شات‌اوت
milebymile-from-safeties = { $points } از { $count } { $safeties ->
    [one] ایمنی
    *[other] ایمنی
}
milebymile-from-all-safeties = { $points } از تمام ۴ ایمنی
milebymile-from-dirty-tricks = { $points } از { $count } { $tricks ->
    [one] ترفند کثیف
    *[other] ترفند کثیف
}

# Game end
milebymile-wins-individual = { $player } بازی را برنده می‌شود!
milebymile-wins-team = تیم { $team } بازی را برنده می‌شود! ({ $members })
milebymile-final-score = امتیاز نهایی: { $score } امتیاز

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = شما و هدف شما هر دو طرد شدید! حمله خنثی می‌شود.
milebymile-karma-clash-you-attacker = شما و { $attacker } هر دو طرد شدید! حمله خنثی می‌شود.
milebymile-karma-clash-others = { $attacker } و { $target } هر دو طرد شدند! حمله خنثی می‌شود.
milebymile-karma-clash-your-team = تیم شما و هدف شما هر دو طرد شدند! حمله خنثی می‌شود.
milebymile-karma-clash-target-team = شما و تیم { $team } هر دو طرد شدید! حمله خنثی می‌شود.
milebymile-karma-clash-other-teams = تیم { $attacker } و تیم { $target } هر دو طرد شدند! حمله خنثی می‌شود.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = شما به خاطر پرخاشگری طرد شدید! کارما شما از دست رفت.
milebymile-karma-shunned-other = { $player } به خاطر پرخاشگری طرد شد!
milebymile-karma-shunned-your-team = تیم شما به خاطر پرخاشگری طرد شد! کارمای تیم شما از دست رفت.
milebymile-karma-shunned-other-team = تیم { $team } به خاطر پرخاشگری طرد شد!

# False Virtue
milebymile-false-virtue-you = شما فضیلت کاذب بازی می‌کنید و کارمای خود را به دست می‌آورید!
milebymile-false-virtue-other = { $player } فضیلت کاذب بازی می‌کند و کارمای خود را به دست می‌آورد!
milebymile-false-virtue-your-team = تیم شما فضیلت کاذب بازی می‌کند و کارمای خود را به دست می‌آورد!
milebymile-false-virtue-other-team = تیم { $team } فضیلت کاذب بازی می‌کند و کارمای خود را به دست می‌آورد!

# Problems/Safeties (for status display)
milebymile-none = هیچ

# Unplayable card reasons
milebymile-reason-not-on-team = شما در تیمی نیستید
milebymile-reason-stopped = شما متوقف شده‌اید
milebymile-reason-has-problem = شما مشکلی دارید که از رانندگی جلوگیری می‌کند
milebymile-reason-speed-limit = محدودیت سرعت فعال است
milebymile-reason-exceeds-distance = از { $miles } مایل بیشتر می‌شود
milebymile-reason-no-targets = هدف معتبری نیست
milebymile-reason-no-speed-limit = شما تحت محدودیت سرعت نیستید
milebymile-reason-has-right-of-way = حق تقدم به شما اجازه می‌دهد بدون چراغ سبز بروید
milebymile-reason-already-moving = شما از قبل در حال حرکت هستید
milebymile-reason-must-fix-first = شما باید ابتدا { $problem } را رفع کنید
milebymile-reason-has-gas = ماشین شما بنزین دارد
milebymile-reason-tires-fine = لاستیک‌های شما خوب است
milebymile-reason-no-accident = ماشین شما تصادف نکرده است
milebymile-reason-has-safety = شما از قبل آن ایمنی را دارید
milebymile-reason-has-karma = شما هنوز کارمای خود را دارید
milebymile-reason-generic = الان نمی‌توان آن را بازی کرد

# Card names
milebymile-card-out-of-gas = بنزین تمام شد
milebymile-card-flat-tire = پنچری
milebymile-card-accident = تصادف
milebymile-card-speed-limit = محدودیت سرعت
milebymile-card-stop = توقف
milebymile-card-gasoline = بنزین
milebymile-card-spare-tire = لاستیک یدکی
milebymile-card-repairs = تعمیرات
milebymile-card-end-of-limit = پایان محدودیت
milebymile-card-green-light = چراغ سبز
milebymile-card-extra-tank = باک اضافی
milebymile-card-puncture-proof = ضد پنچری
milebymile-card-driving-ace = استاد رانندگی
milebymile-card-right-of-way = حق تقدم
milebymile-card-false-virtue = فضیلت کاذب
milebymile-card-miles = { $miles } مایل

# Disabled action reasons
milebymile-no-dirty-trick-window = پنجره ترفند کثیف فعال نیست.
milebymile-not-your-dirty-trick = پنجره ترفند کثیف تیم شما نیست.
milebymile-between-races = منتظر شروع مسابقه بعدی بمانید.

# Validation errors
milebymile-error-karma-needs-three-teams = قانون کارما حداقل به ۳ ماشین/تیم متمایز نیاز دارد.

milebymile-you-play-safety-with-effect = شما { $card } بازی می‌کنید. { $effect }
milebymile-player-plays-safety-with-effect = { $player } { $card } بازی می‌کند. { $effect }
milebymile-you-play-dirty-trick-with-effect = شما { $card } را به عنوان یک ترفند کثیف بازی می‌کنید. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } { $card } را به عنوان یک ترفند کثیف بازی می‌کند. { $effect }
milebymile-safety-effect-extra-tank = اکنون در برابر اتمام سوخت محافظت می‌شوید.
milebymile-safety-effect-puncture-proof = اکنون در برابر پنچری محافظت می‌شوید.
milebymile-safety-effect-driving-ace = اکنون در برابر تصادف محافظت می‌شوید.
milebymile-safety-effect-right-of-way = اکنون در برابر توقف و محدودیت سرعت محافظت می‌شوید.
