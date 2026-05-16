# Main UI messages for PlayPalace

# Game categories
category-card-games = เกมไพ่
category-dice-games = เกมลูกเต้า
category-rb-play-center = ศูนย์เล่น RB
category-poker = โป๊กเกอร์
category-uncategorized = ไม่จัดหมวดหมู่

# Menu titles
main-menu-title = เมนูหลัก
play-menu-title = เล่น
categories-menu-title = หมวดหมู่เกม
tables-menu-title = โต๊ะที่มีอยู่

# Menu items
play = เล่น
view-active-tables = ดูโต๊ะที่ใช้งาน
options = ตั้งค่า
logout = ออกจากระบบ
back = กลับ
go-back = ย้อนกลับ
context-menu = เมนูบริบท
no-actions-available = ไม่มีการกระทำที่ใช้ได้
create-table = สร้างโต๊ะใหม่
join-as-player = เข้าร่วมเป็นผู้เล่น
join-as-spectator = เข้าร่วมเป็นผู้ชม
leave-table = ออกจากโต๊ะ
start-game = เริ่มเกม
add-bot = เพิ่มบอต
remove-bot = ลบบอต
actions-menu = เมนูการกระทำ
save-table = บันทึกโต๊ะ
whose-turn = ตาของใคร
whos-at-table = ใครอยู่ที่โต๊ะ
check-scores = ตรวจสอบคะแนน
check-scores-detailed = คะแนนโดยละเอียด
check-game-options = ตรวจสอบตัวเลือกเกม
no-game-options = ไม่มีตัวเลือกเกม

# Turn messages
game-player-skipped = { $player } ถูกข้าม

# Table messages
table-created = { $host } สร้างโต๊ะ { $game } ใหม่
table-joined = { $player } เข้าร่วมโต๊ะ
table-left = { $player } ออกจากโต๊ะ
new-host = { $player } เป็นเจ้าบ้านตอนนี้
waiting-for-players = รอผู้เล่น ขั้นต่ำ {$min} สูงสุด { $max }
game-starting = กำลังเริ่มเกม!
table-listing = โต๊ะของ { $host } ({ $count } ผู้ใช้)
table-listing-one = โต๊ะของ { $host } ({ $count } ผู้ใช้)
table-listing-with = โต๊ะของ { $host } ({ $count } ผู้ใช้) กับ { $members }
table-listing-game = { $game }: โต๊ะของ { $host } ({ $count } ผู้ใช้)
table-listing-game-one = { $game }: โต๊ะของ { $host } ({ $count } ผู้ใช้)
table-listing-game-with = { $game }: โต๊ะของ { $host } ({ $count } ผู้ใช้) กับ { $members }
table-not-exists = โต๊ะไม่มีอยู่แล้ว
table-full = โต๊ะเต็มแล้ว
player-replaced-by-bot = { $player } ออกและถูกแทนที่ด้วยบอต
player-took-over = { $player } เข้าแทนบอต
spectator-joined = เข้าร่วมโต๊ะของ { $host } เป็นผู้ชม

# Spectator mode
spectate = ชม
now-playing = { $player } กำลังเล่นตอนนี้
now-spectating = { $player } กำลังชมตอนนี้
spectator-left = { $player } หลุดการชม

# General
welcome = ยินดีต้อนรับสู่ PlayPalace!
goodbye = ลาก่อน!

# User presence announcements
user-online = { $player } ออนไลน์
user-offline = { $player } ออฟไลน์
user-is-admin = { $player } เป็นผู้ดูแลระบบของ PlayPalace
user-is-server-owner = { $player } เป็นเจ้าของเซิร์ฟเวอร์ของ PlayPalace
online-users-none = ไม่มีผู้ใช้ออนไลน์
online-users-one = 1 ผู้ใช้: { $users }
online-users-many = { $count } ผู้ใช้: { $users }
online-user-not-in-game = ไม่ได้อยู่ในเกม
online-user-waiting-approval = รอการอนุมัติ

# Options
language = ภาษา
language-option = ภาษา: { $language }
language-changed = ตั้งภาษาเป็น { $language }

# Boolean option states
option-on = เปิด
option-off = ปิด

# Sound options
turn-sound-option = เสียงตา: { $status }

# Dice options
clear-kept-option = ล้างลูกเต้าที่เก็บไว้เมื่อทอย: { $status }
dice-keeping-style-option = รูปแบบการเก็บลูกเต้า: { $style }
dice-keeping-style-changed = ตั้งรูปแบบการเก็บลูกเต้าเป็น { $style }
dice-keeping-style-indexes = ดัชนีลูกเต้า
dice-keeping-style-values = ค่าลูกเต้า

# Bot names
cancel = ยกเลิก
no-bot-names-available = ไม่มีชื่อบอตที่ใช้ได้
select-bot-name = เลือกชื่อสำหรับบอต
enter-bot-name = ป้อนชื่อบอต
no-options-available = ไม่มีตัวเลือกที่ใช้ได้
no-scores-available = ไม่มีคะแนนที่ใช้ได้

# Duration estimation
estimate-duration = ประมาณระยะเวลา
estimate-computing = กำลังคำนวณระยะเวลาเกมโดยประมาณ...
estimate-result = บอตเฉลี่ย: { $bot_time } (± { $std_dev }). { $outlier_info }เวลามนุษย์โดยประมาณ: { $human_time }
estimate-error = ไม่สามารถประมาณระยะเวลาได้
estimate-already-running = การประมาณระยะเวลากำลังดำเนินการอยู่

# Save/Restore
saved-tables = โต๊ะที่บันทึก
no-saved-tables = คุณไม่มีโต๊ะที่บันทึก
no-active-tables = ไม่มีโต๊ะที่ใช้งาน
restore-table = คืนค่า
delete-saved-table = ลบ
saved-table-deleted = โต๊ะที่บันทึกถูกลบ
missing-players = ไม่สามารถคืนค่าได้: ผู้เล่นเหล่านี้ไม่พร้อมใช้งาน: { $players }
table-restored = คืนค่าโต๊ะแล้ว! ผู้เล่นทั้งหมดถูกโอนแล้ว
table-saved-destroying = บันทึกโต๊ะแล้ว! กลับสู่เมนูหลัก
game-type-not-found = ประเภทเกมไม่มีอยู่แล้ว

# Action disabled reasons
action-not-your-turn = ยังไม่ถึงตาคุณ
action-not-playing = เกมยังไม่เริ่ม
action-spectator = ผู้ชมไม่สามารถทำสิ่งนี้ได้
action-not-host = เฉพาะเจ้าบ้านเท่านั้นที่สามารถทำสิ่งนี้ได้
action-game-in-progress = ไม่สามารถทำสิ่งนี้ได้ขณะเกมกำลังดำเนินการ
action-need-more-players = ต้องการผู้เล่นเพิ่มเพื่อเริ่ม
action-table-full = โต๊ะเต็มแล้ว
action-no-bots = ไม่มีบอตที่จะลบ
action-bots-cannot = บอตไม่สามารถทำสิ่งนี้ได้
action-no-scores = ยังไม่มีคะแนน

# Dice actions
dice-not-rolled = คุณยังไม่ได้ทอย
dice-locked = ลูกเต้านี้ถูกล็อค
dice-no-dice = ไม่มีลูกเต้า

# Game actions
game-turn-start = ตาของ { $player }
game-no-turn = ยังไม่มีตาของใคร
table-no-players = ไม่มีผู้เล่น
table-players-one = { $count } ผู้เล่น: { $players }
table-players-many = { $count } ผู้เล่น: { $players }
table-spectators = ผู้ชม: { $spectators }
game-leave = ออก
game-over = จบเกม
game-final-scores = คะแนนสุดท้าย
game-points = { $count } คะแนน
play = เล่น

# Leaderboards
leaderboards = ตารางผู้นำ
leaderboards-menu-title = ตารางผู้นำ
leaderboards-select-game = เลือกเกมเพื่อดูตารางผู้นำ
leaderboard-no-data = ยังไม่มีข้อมูลตารางผู้นำสำหรับเกมนี้

# Leaderboard types
leaderboard-type-wins = ผู้นำชนะ
leaderboard-type-rating = คะแนนทักษะ
leaderboard-type-total-score = คะแนนรวม
leaderboard-type-high-score = คะแนนสูงสุด
leaderboard-type-games-played = เกมที่เล่น
leaderboard-type-avg-points-per-turn = คะแนนเฉลี่ยต่อตา
leaderboard-type-best-single-turn = ตาที่ดีที่สุด
leaderboard-type-score-per-round = คะแนนต่อรอบ

# Leaderboard headers
leaderboard-wins-header = { $game } - ผู้นำชนะ
leaderboard-total-score-header = { $game } - คะแนนรวม
leaderboard-high-score-header = { $game } - คะแนนสูงสุด
leaderboard-games-played-header = { $game } - เกมที่เล่น
leaderboard-rating-header = { $game } - คะแนนทักษะ
leaderboard-avg-points-header = { $game } - คะแนนเฉลี่ยต่อตา
leaderboard-best-turn-header = { $game } - ตาที่ดีที่สุด
leaderboard-score-per-round-header = { $game } - คะแนนต่อรอบ

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins } ชนะ { $losses } แพ้, { $percentage }% อัตราชนะ
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: { $value } เฉลี่ย
leaderboard-games-entry = { $rank }. { $player }: { $value } เกม

# Player stats
leaderboard-player-stats = สถิติของคุณ: { $wins } ชนะ, { $losses } แพ้ ({ $percentage }% อัตราชนะ)
leaderboard-no-player-stats = คุณยังไม่ได้เล่นเกมนี้

# Skill rating leaderboard
leaderboard-no-ratings = ยังไม่มีข้อมูลคะแนนสำหรับเกมนี้
leaderboard-rating-entry = { $rank }. { $player }: { $rating } คะแนน ({ $mu } ± { $sigma })
leaderboard-player-rating = คะแนนของคุณ: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = คุณยังไม่มีคะแนนสำหรับเกมนี้

# My Stats menu
my-stats = สถิติของฉัน
my-stats-select-game = เลือกเกมเพื่อดูสถิติของคุณ
my-stats-no-data = คุณยังไม่ได้เล่นเกมนี้
my-stats-no-games = คุณยังไม่ได้เล่นเกมใดๆ
my-stats-header = { $game } - สถิติของคุณ
my-stats-wins = ชนะ: { $value }
my-stats-losses = แพ้: { $value }
my-stats-winrate = อัตราชนะ: { $value }%
my-stats-games-played = เกมที่เล่น: { $value }
my-stats-total-score = คะแนนรวม: { $value }
my-stats-high-score = คะแนนสูงสุด: { $value }
my-stats-rating = คะแนนทักษะ: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = ยังไม่มีคะแนนทักษะ
my-stats-avg-per-turn = คะแนนเฉลี่ยต่อตา: { $value }
my-stats-best-turn = ตาที่ดีที่สุด: { $value }

# Prediction system
predict-outcomes = ทำนายผลลัพธ์
predict-header = ผลลัพธ์ที่ทำนาย (โดยคะแนนทักษะ)
predict-entry = { $rank }. { $player } (คะแนน: { $rating })
predict-entry-2p = { $rank }. { $player } (คะแนน: { $rating }, { $probability }% โอกาสชนะ)
predict-unavailable = การทำนายคะแนนไม่พร้อมใช้งาน
predict-need-players = ต้องการผู้เล่นมนุษย์อย่างน้อย 2 คนสำหรับการทำนาย
action-need-more-humans = ต้องการผู้เล่นมนุษย์เพิ่ม
confirm-leave-game = คุณแน่ใจหรือว่าต้องการออกจากโต๊ะ?
confirm-yes = ใช่
confirm-no = ไม่ใช่

# Administration
administration = การจัดการ
admin-menu-title = การจัดการ

# Account approval
account-approval = การอนุมัติบัญชี
account-approval-menu-title = การอนุมัติบัญชี
no-pending-accounts = ไม่มีบัญชีที่รออนุมัติ
approve-account = อนุมัติ
decline-account = ปฏิเสธ
account-approved = บัญชีของ { $player } ได้รับการอนุมัติแล้ว
account-declined = บัญชีของ { $player } ถูกปฏิเสธและลบแล้ว

# Waiting for approval (shown to unapproved users)
waiting-for-approval = บัญชีของคุณกำลังรอการอนุมัติจากผู้ดูแลระบบ
account-approved-welcome = บัญชีของคุณได้รับการอนุมัติแล้ว! ยินดีต้อนรับสู่ PlayPalace!
account-declined-goodbye = คำขอบัญชีของคุณถูกปฏิเสธ
    เหตุผล:
account-banned = บัญชีของคุณถูกแบนและไม่สามารถเข้าถึงได้

# Login errors
incorrect-username = ชื่อผู้ใช้ที่คุณป้อนไม่มีอยู่
incorrect-password = รหัสผ่านที่คุณป้อนไม่ถูกต้อง
already-logged-in = บัญชีนี้เข้าสู่ระบบอยู่แล้ว

# Credential validation
credential-username-length = ชื่อผู้ใช้ต้องมีความยาวระหว่าง { $min } ถึง { $max } ตัวอักษร
credential-password-length = รหัสผ่านต้องมีความยาวระหว่าง { $min } ถึง { $max } ตัวอักษร

# Rate limiting
rate-limit-login-ip = มีการพยายามเข้าสู่ระบบจากที่อยู่นี้มากเกินไป โปรดรอแล้วลองอีกครั้ง
rate-limit-login-user = มีการพยายามเข้าสู่ระบบล้มเหลวสำหรับชื่อผู้ใช้นี้มากเกินไป โปรดรอแล้วลองอีกครั้ง
rate-limit-registration = มีการพยายามลงทะเบียนจากที่อยู่นี้มากเกินไป โปรดรอแล้วลองอีกครั้ง
rate-limit-refresh = มีการพยายามรีเฟรชจากที่อยู่นี้มากเกินไป โปรดรอแล้วลองอีกครั้ง

# Session/auth errors
account-not-found = ไม่พบบัญชี
session-expired = เซสชันหมดอายุแล้ว โปรดเข้าสู่ระบบอีกครั้ง
session-token-mismatch = โทเค็นเซสชันไม่ตรงกับชื่อผู้ใช้
refresh-token-expired = โทเค็นรีเฟรชหมดอายุแล้ว โปรดเข้าสู่ระบบอีกครั้ง
refresh-token-mismatch = โทเค็นรีเฟรชไม่ตรงกับชื่อผู้ใช้

# Registration
registration-success = ลงทะเบียนสำเร็จ! บัญชีของคุณกำลังรอการอนุมัติ
registration-username-taken = ชื่อผู้ใช้นี้ถูกใช้งานแล้ว โปรดเลือกชื่อผู้ใช้อื่น

# Preference fallback
pref-invalid-value = การเลือกไม่ถูกต้อง ใช้ค่าเริ่มต้นแทน

# Decline reason
decline-reason-prompt = ป้อนเหตุผลในการปฏิเสธ (หรือกด Escape เพื่อยกเลิก):
account-action-empty-reason = ไม่มีเหตุผล

# Admin notifications for account requests
account-request = คำขอบัญชี
account-action = การกระทำบัญชีที่ดำเนินการ

# Admin promotion/demotion
promote-admin = เลื่อนเป็นผู้ดูแลระบบ
demote-admin = ปลดจากผู้ดูแลระบบ
promote-admin-menu-title = เลื่อนเป็นผู้ดูแลระบบ
demote-admin-menu-title = ปลดจากผู้ดูแลระบบ
no-users-to-promote = ไม่มีผู้ใช้ที่สามารถเลื่อนตำแหน่งได้
no-admins-to-demote = ไม่มีผู้ดูแลระบบที่สามารถปลดตำแหน่งได้
confirm-promote = คุณแน่ใจหรือว่าต้องการเลื่อน { $player } เป็นผู้ดูแลระบบ?
confirm-demote = คุณแน่ใจหรือว่าต้องการปลด { $player } จากผู้ดูแลระบบ?
broadcast-to-all = ประกาศให้ผู้ใช้ทั้งหมด
broadcast-to-admins = ประกาศให้ผู้ดูแลระบบเท่านั้น
broadcast-to-nobody = เงียบ (ไม่มีการประกาศ)
promote-announcement = { $player } ถูกเลื่อนเป็นผู้ดูแลระบบ!
promote-announcement-you = คุณถูกเลื่อนเป็นผู้ดูแลระบบ!
demote-announcement = { $player } ถูกปลดจากผู้ดูแลระบบ
demote-announcement-you = คุณถูกปลดจากผู้ดูแลระบบ
not-admin-anymore = คุณไม่ใช่ผู้ดูแลระบบอีกต่อไปและไม่สามารถทำการกระทำนี้ได้
not-server-owner = เฉพาะเจ้าของเซิร์ฟเวอร์เท่านั้นที่สามารถทำการกระทำนี้ได้

# Server ownership transfer
transfer-ownership = โอนความเป็นเจ้าของ
transfer-ownership-menu-title = โอนความเป็นเจ้าของ
no-admins-for-transfer = ไม่มีผู้ดูแลระบบที่สามารถโอนความเป็นเจ้าของได้
confirm-transfer-ownership = คุณแน่ใจหรือว่าต้องการโอนความเป็นเจ้าของเซิร์ฟเวอร์ให้ { $player }? คุณจะถูกปลดเป็นผู้ดูแลระบบ
transfer-ownership-announcement = { $player } เป็นเจ้าของเซิร์ฟเวอร์ Play Palace ตอนนี้!
transfer-ownership-announcement-you = คุณเป็นเจ้าของเซิร์ฟเวอร์ Play palace ตอนนี้!

# User banning
ban-user = แบนผู้ใช้
unban-user = ปลดแบนผู้ใช้
no-users-to-ban = ไม่มีผู้ใช้ที่สามารถแบนได้
no-users-to-unban = ไม่มีผู้ใช้ที่ถูกแบนที่จะปลดแบน
confirm-ban = คุณแน่ใจหรือว่าต้องการแบน { $player }?
confirm-unban = คุณแน่ใจหรือว่าต้องการปลดแบน { $player }?
ban-reason-prompt = ป้อนเหตุผลในการแบน (ไม่จำเป็น):
unban-reason-prompt = ป้อนเหตุผลในการปลดแบน (ไม่จำเป็น):
user-banned = { $player } ถูกแบน
user-unbanned = { $player } ถูกปลดแบน
you-have-been-banned = คุณถูกแบนจากเซิร์ฟเวอร์นี้
    เหตุผล:
you-have-been-unbanned = คุณถูกปลดแบนจากเซิร์ฟเวอร์นี้
    เหตุผล:
ban-no-reason = ไม่มีเหตุผล

# Virtual bots (server owner only)
virtual-bots = บอตเสมือน
virtual-bots-fill = เติมเต็มเซิร์ฟเวอร์
virtual-bots-clear = ล้างบอตทั้งหมด
virtual-bots-status = สถานะ
virtual-bots-clear-confirm = คุณแน่ใจหรือว่าต้องการล้างบอตเสมือนทั้งหมด? นี่จะทำลายโต๊ะที่พวกเขาอยู่ด้วย
virtual-bots-not-available = บอตเสมือนไม่พร้อมใช้งาน
virtual-bots-filled = เพิ่ม { $added } บอตเสมือน { $online } ออนไลน์ตอนนี้
virtual-bots-already-filled = บอตเสมือนทั้งหมดจากการกำหนดค่าใช้งานอยู่แล้ว
virtual-bots-cleared = ล้าง { $bots } บอตเสมือนและทำลาย { $tables } โต๊ะ
virtual-bot-table-closed = โต๊ะถูกปิดโดยผู้ดูแลระบบ
virtual-bots-none-to-clear = ไม่มีบอตเสมือนที่จะล้าง
virtual-bots-status-report = บอตเสมือน: { $total } ทั้งหมด, { $online } ออนไลน์, { $offline } ออฟไลน์, { $in_game } ในเกม
virtual-bots-guided-overview = โต๊ะแนะนำ
virtual-bots-groups-overview = กลุ่มบอต
virtual-bots-profiles-overview = โปรไฟล์
virtual-bots-guided-header = โต๊ะแนะนำ: { $count } กฎ การจัดสรร: { $allocation }, ทางเลือกอื่น: { $fallback }, โปรไฟล์เริ่มต้น: { $default_profile }
virtual-bots-guided-empty = ไม่มีกฎโต๊ะแนะนำที่กำหนดไว้
virtual-bots-guided-status-active = ใช้งาน
virtual-bots-guided-status-inactive = ไม่ใช้งาน
virtual-bots-guided-table-linked = เชื่อมโยงกับโต๊ะ { $table_id } (เจ้าบ้าน { $host }, ผู้เล่น { $players }, มนุษย์ { $humans })
virtual-bots-guided-table-stale = โต๊ะ { $table_id } ขาดหายไปบนเซิร์ฟเวอร์
virtual-bots-guided-table-unassigned = ไม่มีโต๊ะที่ติดตามอยู่ในขณะนี้
virtual-bots-guided-next-change = การเปลี่ยนแปลงถัดไปใน { $ticks } ติ๊ก
virtual-bots-guided-no-schedule = ไม่มีช่วงเวลากำหนดการ
virtual-bots-guided-warning = ⚠ ไม่เต็ม
virtual-bots-guided-line = { $table }: เกม { $game }, ลำดับความสำคัญ { $priority }, บอต { $assigned } (ขั้นต่ำ { $min_bots }, สูงสุด { $max_bots }), รอ { $waiting }, ไม่พร้อมใช้งาน { $unavailable }, สถานะ { $status }, โปรไฟล์ { $profile }, กลุ่ม { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = กลุ่มบอต: { $count } แท็ก, { $bots } บอตที่กำหนดค่า
virtual-bots-groups-empty = ไม่มีกลุ่มบอตที่กำหนดไว้
virtual-bots-groups-line = { $group }: โปรไฟล์ { $profile }, บอต { $total } (ออนไลน์ { $online }, รอ { $waiting }, ในเกม { $in_game }, ออฟไลน์ { $offline }), กฎ { $rules }
virtual-bots-groups-no-rules = ไม่มี
virtual-bots-no-profile = เริ่มต้น
virtual-bots-profile-inherit-default = สืบทอดโปรไฟล์เริ่มต้น
virtual-bots-profiles-header = โปรไฟล์: { $count } กำหนดไว้ (เริ่มต้น: { $default_profile })
virtual-bots-profiles-empty = ไม่มีโปรไฟล์ที่กำหนดไว้
virtual-bots-profiles-line = { $profile } ({ $bot_count } บอต) แทนที่: { $overrides }
virtual-bots-profiles-no-overrides = สืบทอดการกำหนดค่าพื้นฐาน

localization-in-progress-try-again = กำลังโหลดการแปลภาษา โปรดลองอีกครั้งในอีกหนึ่งนาที
