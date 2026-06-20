# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = ไมล์ต่อไมล์

# Game options
milebymile-set-distance = ระยะทางแข่ง: { $miles } ไมล์
milebymile-enter-distance = ใส่ระยะทางแข่ง (300-3000)
milebymile-set-winning-score = คะแนนชนะ: { $score } คะแนน
milebymile-enter-winning-score = ใส่คะแนนชนะ (1000-10000)
milebymile-toggle-perfect-crossing = ต้องการเข้าเส้นชัยแบบพอดี: { $enabled }
milebymile-toggle-stacking = อนุญาตการโจมตีซ้อน: { $enabled }
milebymile-toggle-reshuffle = สับกองทิ้งกลับเข้าสำรับ: { $enabled }
milebymile-toggle-karma = กฎกรรม: { $enabled }
milebymile-set-rig = การจัดสำรับ: { $rig }
milebymile-select-rig = เลือกตัวเลือกการจัดสำรับ

# Option change announcements
milebymile-option-changed-distance = ตั้งระยะทางแข่งเป็น { $miles } ไมล์
milebymile-option-changed-winning = ตั้งคะแนนชนะเป็น { $score } คะแนน
milebymile-option-changed-crossing = เข้าเส้นชัยแบบพอดี { $enabled }
milebymile-option-changed-stacking = อนุญาตการโจมตีซ้อน { $enabled }
milebymile-option-changed-reshuffle = สับกองทิ้งกลับเข้าสำรับ { $enabled }
milebymile-option-changed-karma = กฎกรรม { $enabled }
milebymile-option-changed-rig = ตั้งการจัดสำรับเป็น { $rig }

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points } คะแนน, { $miles } ไมล์, ปัญหา: { $problems }, ความปลอดภัย: { $safeties }

# Card actions
milebymile-no-matching-safety = คุณไม่มีไพ่ความปลอดภัยที่ตรงกัน!
milebymile-cant-play = คุณไม่สามารถเล่น { $card } เพราะ { $reason }
milebymile-no-card-selected = ไม่ได้เลือกไพ่ที่จะทิ้ง
milebymile-no-valid-targets = ไม่มีเป้าหมายที่ถูกต้องสำหรับอุปสรรคนี้!
milebymile-you-drew = คุณจั่ว: { $card }
milebymile-discards = { $player } ทิ้งไพ่
milebymile-select-target = เลือกเป้าหมาย

# Distance plays
milebymile-plays-distance-individual = { $player } เล่น { $distance } ไมล์ และตอนนี้อยู่ที่ { $total } ไมล์
milebymile-plays-distance-team = { $player } เล่น { $distance } ไมล์; ทีมของเขาตอนนี้อยู่ที่ { $total } ไมล์

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } เสร็จสิ้นการเดินทางด้วยการข้ามเส้นชัยที่สมบูรณ์แบบ!
milebymile-journey-complete-perfect-team = ทีม { $team } เสร็จสิ้นการเดินทางด้วยการข้ามเส้นชัยที่สมบูรณ์แบบ!
milebymile-journey-complete-individual = { $player } เสร็จสิ้นการเดินทาง!
milebymile-journey-complete-team = ทีม { $team } เสร็จสิ้นการเดินทาง!

# Hazard plays
milebymile-plays-hazard-individual = { $player } เล่น { $card } ใส่ { $target }
milebymile-plays-hazard-team = { $player } เล่น { $card } ใส่ทีม { $team }

# Remedy/Safety plays
milebymile-plays-card = { $player } เล่น { $card }
milebymile-plays-dirty-trick = { $player } เล่น { $card } เป็นกลเม็ดสกปรก!

# Deck
milebymile-deck-reshuffled = สับกองทิ้งกลับเข้าสำรับแล้ว

# Race
milebymile-new-race = การแข่งใหม่เริ่มต้น!
milebymile-race-complete = การแข่งเสร็จสิ้น! คำนวณคะแนน...
milebymile-earned-points = { $name } ได้ { $score } คะแนนในการแข่งนี้: { $breakdown }
milebymile-total-scores = คะแนนรวม:
milebymile-team-score = { $name }: { $score } คะแนน

# Scoring breakdown
milebymile-from-distance = { $miles } จากระยะทางที่เดินทาง
milebymile-from-trip = { $points } จากการเดินทางสำเร็จ
milebymile-from-perfect = { $points } จากการข้ามเส้นชัยที่สมบูรณ์แบบ
milebymile-from-safe = { $points } จากการเดินทางที่ปลอดภัย
milebymile-from-shutout = { $points } จากการชนะขาดลอย
milebymile-from-safeties = { $points } จาก { $count } ไพ่ความปลอดภัย
milebymile-from-all-safeties = { $points } จากความปลอดภัยทั้ง 4 แบบ
milebymile-from-dirty-tricks = { $points } จาก { $count } กลเม็ดสกปรก

# Game end
milebymile-wins-individual = { $player } ชนะเกม!
milebymile-wins-team = ทีม { $team } ชนะเกม! ({ $members })
milebymile-final-score = คะแนนสุดท้าย: { $score } คะแนน

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = คุณและเป้าหมายของคุณถูกขับไล่! การโจมตีถูกระงับ
milebymile-karma-clash-you-attacker = คุณและ { $attacker } ถูกขับไล่! การโจมตีถูกระงับ
milebymile-karma-clash-others = { $attacker } และ { $target } ถูกขับไล่! การโจมตีถูกระงับ
milebymile-karma-clash-your-team = ทีมของคุณและเป้าหมายของคุณถูกขับไล่! การโจมตีถูกระงับ
milebymile-karma-clash-target-team = คุณและทีม { $team } ถูกขับไล่! การโจมตีถูกระงับ
milebymile-karma-clash-other-teams = ทีม { $attacker } และทีม { $target } ถูกขับไล่! การโจมตีถูกระงับ

# Karma messages - attacker shunned
milebymile-karma-shunned-you = คุณถูกขับไล่เพราะความก้าวร้าว! กรรมของคุณสูญหายไป
milebymile-karma-shunned-other = { $player } ถูกขับไล่เพราะความก้าวร้าว!
milebymile-karma-shunned-your-team = ทีมของคุณถูกขับไล่เพราะความก้าวร้าว! กรรมของทีมสูญหายไป
milebymile-karma-shunned-other-team = ทีม { $team } ถูกขับไล่เพราะความก้าวร้าว!

# False Virtue
milebymile-false-virtue-you = คุณเล่นคุณธรรมปลอมและฟื้นกรรมของคุณ!
milebymile-false-virtue-other = { $player } เล่นคุณธรรมปลอมและฟื้นกรรมของเขา!
milebymile-false-virtue-your-team = ทีมของคุณเล่นคุณธรรมปลอมและฟื้นกรรมของทีม!
milebymile-false-virtue-other-team = ทีม { $team } เล่นคุณธรรมปลอมและฟื้นกรรมของทีม!

# Problems/Safeties (for status display)
milebymile-none = ไม่มี

# Unplayable card reasons
milebymile-reason-not-on-team = คุณไม่ได้อยู่ในทีม
milebymile-reason-stopped = คุณหยุดอยู่
milebymile-reason-has-problem = คุณมีปัญหาที่ป้องกันการขับ
milebymile-reason-speed-limit = ความเร็วจำกัดทำงานอยู่
milebymile-reason-exceeds-distance = มันจะเกิน { $miles } ไมล์
milebymile-reason-no-targets = ไม่มีเป้าหมายที่ถูกต้อง
milebymile-reason-no-speed-limit = คุณไม่อยู่ภายใต้ความเร็วจำกัด
milebymile-reason-has-right-of-way = สิทธิ์ในการผ่านทำให้คุณไปได้โดยไม่ต้องมีไฟเขียว
milebymile-reason-already-moving = คุณกำลังเคลื่อนที่อยู่แล้ว
milebymile-reason-must-fix-first = คุณต้องซ่อม { $problem } ก่อน
milebymile-reason-has-gas = รถของคุณมีน้ำมัน
milebymile-reason-tires-fine = ยางของคุณสบายดี
milebymile-reason-no-accident = รถของคุณไม่ได้ประสบอุบัติเหตุ
milebymile-reason-has-safety = คุณมีความปลอดภัยนั้นแล้ว
milebymile-reason-has-karma = คุณยังมีกรรมอยู่
milebymile-reason-generic = ไม่สามารถเล่นได้ตอนนี้

# Card names
milebymile-card-out-of-gas = น้ำมันหมด
milebymile-card-flat-tire = ยางแบน
milebymile-card-accident = อุบัติเหตุ
milebymile-card-speed-limit = ความเร็วจำกัด
milebymile-card-stop = หยุด
milebymile-card-gasoline = น้ำมันเบนซิน
milebymile-card-spare-tire = ยางอะไหล่
milebymile-card-repairs = ซ่อมแซม
milebymile-card-end-of-limit = สิ้นสุดความเร็วจำกัด
milebymile-card-green-light = ไฟเขียว
milebymile-card-extra-tank = ถังพิเศษ
milebymile-card-puncture-proof = ป้องกันการแทง
milebymile-card-driving-ace = เอซการขับ
milebymile-card-right-of-way = สิทธิ์ในการผ่าน
milebymile-card-false-virtue = คุณธรรมปลอม
milebymile-card-miles = { $miles } ไมล์

# Disabled action reasons
milebymile-no-dirty-trick-window = ไม่มีช่วงเวลากลเม็ดสกปรกทำงานอยู่
milebymile-not-your-dirty-trick = ไม่ใช่ช่วงเวลากลเม็ดสกปรกของทีมคุณ
milebymile-between-races = รอให้การแข่งถัดไปเริ่มต้น

# Validation errors
milebymile-error-karma-needs-three-teams = กฎกรรมต้องการอย่างน้อย 3 รถ/ทีมที่แตกต่างกัน

milebymile-you-play-safety-with-effect = คุณเล่น { $card } { $effect }
milebymile-player-plays-safety-with-effect = { $player } เล่น { $card } { $effect }
milebymile-you-play-dirty-trick-with-effect = คุณเล่น { $card } เป็นลูกเล่นสกปรก { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } เล่น { $card } เป็นลูกเล่นสกปรก { $effect }
milebymile-safety-effect-extra-tank = ตอนนี้ป้องกันจากน้ำมันหมดแล้ว
milebymile-safety-effect-puncture-proof = ตอนนี้ป้องกันจากยางแตกแล้ว
milebymile-safety-effect-driving-ace = ตอนนี้ป้องกันจากอุบัติเหตุแล้ว
milebymile-safety-effect-right-of-way = ตอนนี้ป้องกันจากหยุดและจำกัดความเร็วแล้ว
