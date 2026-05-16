# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = เก้าสิบเก้า

# Round and turn flow
game-round-start = รอบที่ { $round }
game-round-end = รอบที่ { $round } เสร็จสิ้น
game-turn-start = ตาของ { $player }
game-your-turn = ตาของคุณ
game-no-turn = ไม่มีตาใครตอนนี้

# Score display
game-scores-header = คะแนนปัจจุบัน:
game-score-line = { $player }: { $score } คะแนน
game-final-scores-header = คะแนนสุดท้าย:

# Win/loss
game-winner = { $player } ชนะ!
game-winner-score = { $player } ชนะด้วย { $score } คะแนน!
game-tiebreaker = เสมอ! รอบตัดสินชนะ!
game-tiebreaker-players = เสมอระหว่าง { $players }! รอบตัดสินชนะ!
game-eliminated = { $player } ถูกคัดออกด้วย { $score } คะแนน

# Common options
game-set-target-score = คะแนนเป้าหมาย: { $score }
game-enter-target-score = ป้อนคะแนนเป้าหมาย:
game-option-changed-target = ตั้งคะแนนเป้าหมายเป็น { $score } แล้ว

game-set-team-mode = โหมดทีม: { $mode }
game-select-team-mode = เลือกโหมดทีม
game-option-changed-team = ตั้งโหมดทีมเป็น { $mode } แล้ว
game-team-mode-individual = แบบเดี่ยว
game-team-mode-x-teams-of-y = { $num_teams } ทีมจาก { $team_size } คน

# Boolean option values
option-on = เปิด
option-off = ปิด

# Status box

# Game end
game-leave = ออกจากเกม

# Round timer
round-timer-paused = { $player } หยุดเกมชั่วคราว (กด p เพื่อเริ่มรอบถัดไป)
round-timer-resumed = ตั้งเวลารอบทำงานอีกครั้ง
round-timer-countdown = รอบถัดไปใน { $seconds } วินาที...

# Dice games - keeping/releasing dice
dice-keeping = เก็บ { $value }
dice-rerolling = ทอยใหม่ { $value }
dice-locked = ลูกเต้านั้นถูกล็อคและไม่สามารถเปลี่ยนได้
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = แจก { $current }/{ $total }
game-you-deal = คุณแจกไพ่
game-player-deals = { $player } แจกไพ่

# Card names
card-name = { $rank } ของ { $suit }
no-cards = ไม่มีไพ่

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = ดำ
color-black-m = ดำ
color-black-f = ดำ
color-blue = น้ำเงิน
color-blue-m = น้ำเงิน
color-blue-f = น้ำเงิน
color-brown = น้ำตาล
color-brown-m = น้ำตาล
color-brown-f = น้ำตาล
color-gray = เทา
color-gray-m = เทา
color-gray-f = เทา
color-green = เขียว
color-green-m = เขียว
color-green-f = เขียว
color-indigo = คราม
color-indigo-m = คราม
color-indigo-f = คราม
color-orange = ส้ม
color-orange-m = ส้ม
color-orange-f = ส้ม
color-pink = ชมพู
color-pink-m = ชมพู
color-pink-f = ชมพู
color-purple = ม่วง
color-purple-m = ม่วง
color-purple-f = ม่วง
color-red = แดง
color-red-m = แดง
color-red-f = แดง
color-violet = ม่วงอ่อน
color-violet-m = ม่วงอ่อน
color-violet-f = ม่วงอ่อน
color-white = ขาว
color-white-m = ขาว
color-white-f = ขาว
color-yellow = เหลือง
color-yellow-m = เหลือง
color-yellow-f = เหลือง

# Suit names
suit-diamonds = ข้าวหลามตัด
suit-clubs = ดอกจิก
suit-hearts = โพธิ์แดง
suit-spades = โพธิ์ดำ

# Rank names
rank-ace = เอซ
rank-ace-plural = เอซ
rank-two = 2
rank-two-plural = 2
rank-three = 3
rank-three-plural = 3
rank-four = 4
rank-four-plural = 4
rank-five = 5
rank-five-plural = 5
rank-six = 6
rank-six-plural = 6
rank-seven = 7
rank-seven-plural = 7
rank-eight = 8
rank-eight-plural = 8
rank-nine = 9
rank-nine-plural = 9
rank-ten = 10
rank-ten-plural = 10
rank-jack = แจ็ค
rank-jack-plural = แจ็ค
rank-queen = ควีน
rank-queen-plural = ควีน
rank-king = คิง
rank-king-plural = คิง

# Poker hand descriptions
poker-high-card-with = ไฮคาร์ด { $high }, พร้อม { $rest }
poker-high-card = ไฮคาร์ด { $high }
poker-pair-with = คู่ของ { $pair }, พร้อม { $rest }
poker-pair = คู่ของ { $pair }
poker-two-pair-with = สองคู่, { $high } และ { $low }, พร้อม { $kicker }
poker-two-pair = สองคู่, { $high } และ { $low }
poker-trips-with = สามใบเหมือนกัน, { $trips }, พร้อม { $rest }
poker-trips = สามใบเหมือนกัน, { $trips }
poker-straight-high = สเตรท { $high } สูง
poker-flush-high-with = ฟลัช { $high } สูง, พร้อม { $rest }
poker-full-house = ฟูลเฮาส์, { $trips } เหนือ { $pair }
poker-quads-with = สี่ใบเหมือนกัน, { $quads }, พร้อม { $kicker }
poker-quads = สี่ใบเหมือนกัน, { $quads }
poker-straight-flush-high = สเตรทฟลัช { $high } สูง
poker-unknown-hand = ไม่ทราบมือ

# Validation errors (common across games)
game-error-invalid-team-mode = โหมดทีมที่เลือกไม่ถูกต้องสำหรับจำนวนผู้เล่นปัจจุบัน
