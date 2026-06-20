# Mile by Mile game messages

# Game name
game-name-milebymile = ميل تلو الآخر

# Game options
milebymile-set-distance = مسافة السباق: { $miles } ميل
milebymile-enter-distance = أدخل مسافة السباق (300-3000)
milebymile-set-winning-score = نتيجة الفوز: { $score } نقطة
milebymile-enter-winning-score = أدخل نتيجة الفوز (1000-10000)
milebymile-toggle-perfect-crossing = يتطلب نهاية دقيقة: { $enabled }
milebymile-toggle-stacking = السماح بتكديس الهجمات: { $enabled }
milebymile-toggle-reshuffle = إعادة خلط كومة الإلقاء: { $enabled }
milebymile-toggle-karma = قاعدة الكارما: { $enabled }
milebymile-set-rig = تزوير المجموعة: { $rig }
milebymile-select-rig = اختر خيار تزوير المجموعة

# Option change announcements
milebymile-option-changed-distance = تم تعيين مسافة السباق إلى { $miles } ميل.
milebymile-option-changed-winning = تم تعيين نتيجة الفوز إلى { $score } نقطة.
milebymile-option-changed-crossing = يتطلب نهاية دقيقة { $enabled }.
milebymile-option-changed-stacking = السماح بتكديس الهجمات { $enabled }.
milebymile-option-changed-reshuffle = إعادة خلط كومة الإلقاء { $enabled }.
milebymile-option-changed-karma = قاعدة الكارما { $enabled }.
milebymile-option-changed-rig = تم تعيين تزوير المجموعة إلى { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } نقطة، { $miles } ميل، مشاكل: { $problems }، سلامات: { $safeties }

# Card actions
milebymile-no-matching-safety = ليس لديك ورقة السلامة المطابقة!
milebymile-cant-play = لا يمكنك لعب { $card } لأن { $reason }.
milebymile-no-card-selected = لم يتم اختيار ورقة للإلقاء.
milebymile-no-valid-targets = لا توجد أهداف صالحة لهذا الخطر!
milebymile-you-drew = سحبت: { $card }
milebymile-discards = { $player } يلقي ورقة.
milebymile-select-target = اختر هدفاً

# Distance plays
milebymile-plays-distance-individual = { $player } يلعب { $distance } ميل، والآن عند { $total } ميل.
milebymile-plays-distance-team = { $player } يلعب { $distance } ميل؛ فريقهم الآن عند { $total } ميل.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } أكمل الرحلة بعبور مثالي!
milebymile-journey-complete-perfect-team = الفريق { $team } أكمل الرحلة بعبور مثالي!
milebymile-journey-complete-individual = { $player } أكمل الرحلة!
milebymile-journey-complete-team = الفريق { $team } أكمل الرحلة!

# Hazard plays
milebymile-plays-hazard-individual = { $player } يلعب { $card } على { $target }.
milebymile-plays-hazard-team = { $player } يلعب { $card } على الفريق { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } يلعب { $card }.
milebymile-plays-dirty-trick = { $player } يلعب { $card } كخدعة قذرة!

# Deck
milebymile-deck-reshuffled = تم خلط كومة الإلقاء مرة أخرى في المجموعة.

# Race
milebymile-new-race = سباق جديد يبدأ!
milebymile-race-complete = اكتمل السباق! حساب النتائج...
milebymile-earned-points = { $name } كسب { $score } نقطة في هذا السباق: { $breakdown }.
milebymile-total-scores = النتائج الإجمالية:
milebymile-team-score = { $name }: { $score } نقطة

# Scoring breakdown
milebymile-from-distance = { $miles } من المسافة المقطوعة
milebymile-from-trip = { $points } من إكمال الرحلة
milebymile-from-perfect = { $points } من عبور مثالي
milebymile-from-safe = { $points } من رحلة آمنة
milebymile-from-shutout = { $points } من إقصاء كامل
milebymile-from-safeties = { $points } من { $count } { $safeties ->
    [zero] سلامة
    [one] سلامة
    [two] سلامتين
    [few] سلامات
    [many] سلامة
   *[other] سلامة
}
milebymile-from-all-safeties = { $points } من كل 4 سلامات
milebymile-from-dirty-tricks = { $points } من { $count } { $tricks ->
    [zero] خدعة قذرة
    [one] خدعة قذرة
    [two] خدعتين قذرتين
    [few] خدع قذرة
    [many] خدعة قذرة
   *[other] خدعة قذرة
}

# Game end
milebymile-wins-individual = { $player } يفوز باللعبة!
milebymile-wins-team = الفريق { $team } يفوز باللعبة! ({ $members })
milebymile-final-score = النتيجة النهائية: { $score } نقطة

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = أنت وهدفك كلاكما منبوذان! الهجوم محايد.
milebymile-karma-clash-you-attacker = أنت و { $attacker } كلاكما منبوذان! الهجوم محايد.
milebymile-karma-clash-others = { $attacker } و { $target } كلاهما منبوذان! الهجوم محايد.
milebymile-karma-clash-your-team = فريقك وهدفك كلاهما منبوذان! الهجوم محايد.
milebymile-karma-clash-target-team = أنت والفريق { $team } كلاكما منبوذان! الهجوم محايد.
milebymile-karma-clash-other-teams = الفريق { $attacker } والفريق { $target } كلاهما منبوذان! الهجوم محايد.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = لقد تم نبذك بسبب عدوانك! فقدت كارماك.
milebymile-karma-shunned-other = { $player } تم نبذه بسبب عدوانه!
milebymile-karma-shunned-your-team = تم نبذ فريقك بسبب عدوانه! فريقك فقد كارماه.
milebymile-karma-shunned-other-team = الفريق { $team } تم نبذه بسبب عدوانه!

# False Virtue
milebymile-false-virtue-you = تلعب الفضيلة الزائفة وتستعيد كارماك!
milebymile-false-virtue-other = { $player } يلعب الفضيلة الزائفة ويستعيد كارماه!
milebymile-false-virtue-your-team = فريقك يلعب الفضيلة الزائفة ويستعيد كارماه!
milebymile-false-virtue-other-team = الفريق { $team } يلعب الفضيلة الزائفة ويستعيد كارماه!

# Problems/Safeties (for status display)
milebymile-none = لا شيء

# Unplayable card reasons
milebymile-reason-not-on-team = لست في فريق
milebymile-reason-stopped = أنت متوقف
milebymile-reason-has-problem = لديك مشكلة تمنع القيادة
milebymile-reason-speed-limit = حد السرعة نشط
milebymile-reason-exceeds-distance = سيتجاوز { $miles } ميل
milebymile-reason-no-targets = لا توجد أهداف صالحة
milebymile-reason-no-speed-limit = لست تحت حد سرعة
milebymile-reason-has-right-of-way = حق الأولوية يتيح لك المضي بدون إشارات خضراء
milebymile-reason-already-moving = أنت بالفعل تتحرك
milebymile-reason-must-fix-first = يجب إصلاح { $problem } أولاً
milebymile-reason-has-gas = سيارتك بها وقود
milebymile-reason-tires-fine = إطاراتك بخير
milebymile-reason-no-accident = سيارتك لم تتعرض لحادث
milebymile-reason-has-safety = لديك بالفعل تلك السلامة
milebymile-reason-has-karma = ما زلت لديك كارماك
milebymile-reason-generic = لا يمكن لعبها الآن

# Card names
milebymile-card-out-of-gas = نفاد الوقود
milebymile-card-flat-tire = إطار مثقوب
milebymile-card-accident = حادث
milebymile-card-speed-limit = حد السرعة
milebymile-card-stop = توقف
milebymile-card-gasoline = وقود
milebymile-card-spare-tire = إطار احتياطي
milebymile-card-repairs = إصلاحات
milebymile-card-end-of-limit = نهاية الحد
milebymile-card-green-light = ضوء أخضر
milebymile-card-extra-tank = خزان إضافي
milebymile-card-puncture-proof = مضاد للثقب
milebymile-card-driving-ace = بطل القيادة
milebymile-card-right-of-way = حق الأولوية
milebymile-card-false-virtue = فضيلة زائفة
milebymile-card-miles = { $miles } ميل

# Disabled action reasons
milebymile-no-dirty-trick-window = لا توجد نافذة خدعة قذرة نشطة.
milebymile-not-your-dirty-trick = ليست نافذة خدعة قذرة لفريقك.
milebymile-between-races = انتظر بدء السباق التالي.

# Validation errors
milebymile-error-karma-needs-three-teams = تتطلب قاعدة الكارما 3 سيارات/فرق متميزة على الأقل.

milebymile-you-play-safety-with-effect = أنت تلعب { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } يلعب { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = أنت تلعب { $card } كخدعة قذرة. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } يلعب { $card } كخدعة قذرة. { $effect }
milebymile-safety-effect-extra-tank = محمي الآن من نفاد الوقود.
milebymile-safety-effect-puncture-proof = محمي الآن من ثقب الإطار.
milebymile-safety-effect-driving-ace = محمي الآن من الحوادث.
milebymile-safety-effect-right-of-way = محمي الآن من التوقف وحد السرعة.
