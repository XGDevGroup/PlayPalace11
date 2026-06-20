# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Миль бүрээр

# Game options
milebymile-set-distance = Уралдааны зай: { $miles } миль
milebymile-enter-distance = Уралдааны зай оруулах (300-3000)
milebymile-set-winning-score = Ялах оноо: { $score } оноо
milebymile-enter-winning-score = Ялах оноо оруулах (1000-10000)
milebymile-toggle-perfect-crossing = Яг таг төгсгөх шаардлага: { $enabled }
milebymile-toggle-stacking = Довтолгоо давхцуулах зөвшөөрөх: { $enabled }
milebymile-toggle-reshuffle = Хаясан хөзрийг холих: { $enabled }
milebymile-toggle-karma = Карма дүрэм: { $enabled }
milebymile-set-rig = Хөзөр залилах: { $rig }
milebymile-select-rig = Хөзөр залилах сонголт сонгох

# Option change announcements
milebymile-option-changed-distance = Уралдааны зай { $miles } миль болов.
milebymile-option-changed-winning = Ялах оноо { $score } оноо болов.
milebymile-option-changed-crossing = Яг таг төгсгөх шаардлага { $enabled }.
milebymile-option-changed-stacking = Довтолгоо давхцуулах зөвшөөрөх { $enabled }.
milebymile-option-changed-reshuffle = Хаясан хөзрийг холих { $enabled }.
milebymile-option-changed-karma = Карма дүрэм { $enabled }.
milebymile-option-changed-rig = Хөзөр залилах { $rig }-д тохируулагдлаа.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } оноо, { $miles } миль, Асуудал: { $problems }, Аюулгүй байдал: { $safeties }

# Card actions
milebymile-no-matching-safety = Танд тохирох аюулгүй байдлын хөзөр байхгүй!
milebymile-cant-play = { $card } тоглож чадахгүй учир нь { $reason }.
milebymile-no-card-selected = Хаях хөзөр сонгогдоогүй байна.
milebymile-no-valid-targets = Энэ аюулд зориулсан зохих бай байхгүй!
milebymile-you-drew = Та таталаа: { $card }
milebymile-discards = { $player } хөзөр хаяв.
milebymile-select-target = Бай сонгох

# Distance plays
milebymile-plays-distance-individual = { $player } { $distance } миль тоглож, одоо { $total } миль явав.
milebymile-plays-distance-team = { $player } { $distance } миль тоглов; багийнх нь { $total } миль явав.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } аяллаа төгс гаталаа!
milebymile-journey-complete-perfect-team = { $team } баг аяллаа төгс гаталаа!
milebymile-journey-complete-individual = { $player } аяллаа дуусгалаа!
milebymile-journey-complete-team = { $team } баг аяллаа дуусгалаа!

# Hazard plays
milebymile-plays-hazard-individual = { $player } { $target } дээр { $card } тоглов.
milebymile-plays-hazard-team = { $player } { $team } баг дээр { $card } тоглов.

# Remedy/Safety plays
milebymile-plays-card = { $player } { $card } тоглов.
milebymile-plays-dirty-trick = { $player } { $card }-г бохир мэх болгон тоглов!

# Deck
milebymile-deck-reshuffled = Хаясан хөзрийг буцаан хольж оруулав.

# Race
milebymile-new-race = Шинэ уралдаан эхэллээ!
milebymile-race-complete = Уралдаан дууслаа! Оноо тоолж байна...
milebymile-earned-points = { $name } энэ уралдаанд { $score } оноо олов: { $breakdown }.
milebymile-total-scores = Нийт оноо:
milebymile-team-score = { $name }: { $score } оноо

# Scoring breakdown
milebymile-from-distance = явсан зайнаас { $miles }
milebymile-from-trip = аяллыг дуусгасан { $points }
milebymile-from-perfect = төгс гаталаас { $points }
milebymile-from-safe = аюулгүй аяллаас { $points }
milebymile-from-shutout = бүрэн хааснаас { $points }
milebymile-from-safeties = { $count } { $safeties ->
    [one] аюулгүй байдлаас
    *[other] аюулгүй байдлуудаас
} { $points }
milebymile-from-all-safeties = 4 аюулгүй байдлаас { $points }
milebymile-from-dirty-tricks = { $count } { $tricks ->
    [one] бохир мэхээс
    *[other] бохир мэхнүүдээс
} { $points }

# Game end
milebymile-wins-individual = { $player } тоглоом хожлоо!
milebymile-wins-team = { $team } баг тоглоом хожлоо! ({ $members })
milebymile-final-score = Эцсийн оноо: { $score } оноо

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = Та болон таны бай хоёулаа няцаагдсан! Довтолгоо цуцлагдлаа.
milebymile-karma-clash-you-attacker = Та болон { $attacker } хоёулаа няцаагдсан! Довтолгоо цуцлагдлаа.
milebymile-karma-clash-others = { $attacker } болон { $target } хоёулаа няцаагдсан! Довтолгоо цуцлагдлаа.
milebymile-karma-clash-your-team = Таны баг болон таны бай хоёулаа няцаагдсан! Довтолгоо цуцлагдлаа.
milebymile-karma-clash-target-team = Та болон { $team } баг хоёулаа няцаагдсан! Довтолгоо цуцлагдлаа.
milebymile-karma-clash-other-teams = { $attacker } баг болон { $target } баг хоёулаа няцаагдсан! Довтолгоо цуцлагдлаа.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = Та түрэмгийлсний төлөө няцаагдлаа! Таны карма алдагдлаа.
milebymile-karma-shunned-other = { $player } түрэмгийлсний төлөө няцаагдлаа!
milebymile-karma-shunned-your-team = Таны баг түрэмгийлсний төлөө няцаагдлаа! Багийн карма алдагдлаа.
milebymile-karma-shunned-other-team = { $team } баг түрэмгийлсний төлөө няцаагдлаа!

# False Virtue
milebymile-false-virtue-you = Та Хуурмаг буян тоглож кармаа эргүүлэн авлаа!
milebymile-false-virtue-other = { $player } Хуурмаг буян тоглож кармаа эргүүлэн авлаа!
milebymile-false-virtue-your-team = Таны баг Хуурмаг буян тоглож кармаа эргүүлэн авлаа!
milebymile-false-virtue-other-team = { $team } баг Хуурмаг буян тоглож кармаа эргүүлэн авлаа!

# Problems/Safeties (for status display)
milebymile-none = байхгүй

# Unplayable card reasons
milebymile-reason-not-on-team = та багт байхгүй
milebymile-reason-stopped = та зогссон
milebymile-reason-has-problem = танд жолоодохоос сэргийлж буй асуудал байна
milebymile-reason-speed-limit = хурдны хязгаарлалт идэвхтэй
milebymile-reason-exceeds-distance = энэ нь { $miles } миль давна
milebymile-reason-no-targets = зохих бай байхгүй
milebymile-reason-no-speed-limit = та хурдны хязгаарлалтад байхгүй
milebymile-reason-has-right-of-way = Эрхийн зам ногоон гэрэлгүйгээр явах боломжтой
milebymile-reason-already-moving = та аль хэдийн хөдөлж байна
milebymile-reason-must-fix-first = эхлээд { $problem } засаж байх ёстой
milebymile-reason-has-gas = таны машинд бензин байна
milebymile-reason-tires-fine = таны дугуй сайхан байна
milebymile-reason-no-accident = таны машин ослоогүй
milebymile-reason-has-safety = танд тэр аюулгүй байдал аль хэдийн байна
milebymile-reason-has-karma = та хараахан кармаа алдаагүй
milebymile-reason-generic = яг одоо тоглож болохгүй

# Card names
milebymile-card-out-of-gas = Бензин дууссан
milebymile-card-flat-tire = Дугуй хагарсан
milebymile-card-accident = Осол
milebymile-card-speed-limit = Хурдны хязгаар
milebymile-card-stop = Зогс
milebymile-card-gasoline = Бензин
milebymile-card-spare-tire = Нөөц дугуй
milebymile-card-repairs = Засвар
milebymile-card-end-of-limit = Хязгаар дуусгавар
milebymile-card-green-light = Ногоон гэрэл
milebymile-card-extra-tank = Нэмэлт сав
milebymile-card-puncture-proof = Цоолох шахуу
milebymile-card-driving-ace = Жолоодлогын мастер
milebymile-card-right-of-way = Эрхийн зам
milebymile-card-false-virtue = Хуурмаг буян
milebymile-card-miles = { $miles } миль

# Disabled action reasons
milebymile-no-dirty-trick-window = Бохир мэхний цонх идэвхгүй байна.
milebymile-not-your-dirty-trick = Энэ таны багийн бохир мэхний цонх биш.
milebymile-between-races = Дараагийн уралдаан эхлэхийг хүлээнэ үү.

# Validation errors
milebymile-error-karma-needs-three-teams = Карма дүрэмд багадаа 3 өөр машин/баг хэрэгтэй.

milebymile-you-play-safety-with-effect = Та { $card }-г тоглолоо. { $effect }
milebymile-player-plays-safety-with-effect = { $player } { $card }-г тоглолоо. { $effect }
milebymile-you-play-dirty-trick-with-effect = Та { $card }-г бохир мэх болгон тоглолоо. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } { $card }-г бохир мэх болгон тоглолоо. { $effect }
milebymile-safety-effect-extra-tank = Одоо Шатахуун дуусахаас хамгаалагдсан.
milebymile-safety-effect-puncture-proof = Одоо Дугуй хагарахаас хамгаалагдсан.
milebymile-safety-effect-driving-ace = Одоо Ослоос хамгаалагдсан.
milebymile-safety-effect-right-of-way = Одоо Зогс болон Хурдны хязгаараас хамгаалагдсан.
