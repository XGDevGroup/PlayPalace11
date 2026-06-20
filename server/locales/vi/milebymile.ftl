# Thông báo trò chơi Mile by Mile
# Lưu ý: Các thông báo chung như bắt đầu vòng, bắt đầu lượt, chế độ đội nằm trong games.ftl

# Tên trò chơi
game-name-milebymile = Đua Xe Ngàn Dặm

# Tùy chọn game
milebymile-set-distance = Quãng đường đua: { $miles } dặm
milebymile-enter-distance = Nhập quãng đường (300-3000)
milebymile-set-winning-score = Điểm chiến thắng: { $score } điểm
milebymile-enter-winning-score = Nhập điểm chiến thắng (1000-10000)
milebymile-toggle-perfect-crossing = Yêu cầu về đích chính xác: { $enabled }
milebymile-toggle-stacking = Cho phép tấn công chồng (stacking): { $enabled }
milebymile-toggle-reshuffle = Xào lại bài đã bỏ: { $enabled }
milebymile-toggle-karma = Luật Nghiệp chướng (Karma): { $enabled }
milebymile-set-rig = Sắp xếp bộ bài (Rigging): { $rig }
milebymile-select-rig = Chọn tùy chọn sắp xếp bộ bài

# Thông báo thay đổi tùy chọn
milebymile-option-changed-distance = Quãng đường đua đã đặt là { $miles } dặm.
milebymile-option-changed-winning = Điểm chiến thắng đã đặt là { $score } điểm.
milebymile-option-changed-crossing = Yêu cầu về đích chính xác { $enabled }.
milebymile-option-changed-stacking = Cho phép tấn công chồng { $enabled }.
milebymile-option-changed-reshuffle = Xào lại bài đã bỏ { $enabled }.
milebymile-option-changed-karma = Luật Nghiệp chướng { $enabled }.
milebymile-option-changed-rig = Sắp xếp bộ bài đã đặt là { $rig }.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Trạng thái
milebymile-status = { $name }: { $points } điểm, { $miles } dặm, Sự cố: { $problems }, Bảo hộ: { $safeties }

# Hành động bài
milebymile-no-matching-safety = Bạn không có thẻ bảo hộ tương ứng!
milebymile-cant-play = Bạn không thể đánh lá { $card } vì { $reason }.
milebymile-no-card-selected = Chưa chọn lá bài để bỏ.
milebymile-no-valid-targets = Không có mục tiêu hợp lệ cho thẻ tai nạn này!
milebymile-you-drew = Bạn đã rút được: { $card }
milebymile-discards = { $player } bỏ một lá bài.
milebymile-select-target = Chọn mục tiêu

# Đánh bài quãng đường
milebymile-plays-distance-individual = { $player } đi được { $distance } dặm, hiện tại đã đi { $total } dặm.
milebymile-plays-distance-team = { $player } đi được { $distance } dặm; đội của họ đã đi { $total } dặm.

# Hoàn thành chặng đua
milebymile-journey-complete-perfect-individual = { $player } đã hoàn thành chặng đua với thành tích Về đích hoàn hảo!
milebymile-journey-complete-perfect-team = Đội { $team } đã hoàn thành chặng đua với thành tích Về đích hoàn hảo!
milebymile-journey-complete-individual = { $player } đã hoàn thành chặng đua!
milebymile-journey-complete-team = Đội { $team } đã hoàn thành chặng đua!

# Đánh bài tai nạn
milebymile-plays-hazard-individual = { $player } đánh lá { $card } vào { $target }.
milebymile-plays-hazard-team = { $player } đánh lá { $card } vào Đội { $team }.

# Đánh bài Khắc phục/Bảo hộ
milebymile-plays-card = { $player } đánh lá { $card }.
milebymile-plays-dirty-trick = { $player } đánh lá { $card } như một Mẹo bẩn (Coup-fourré)!

# Bộ bài
milebymile-deck-reshuffled = Chồng bài bỏ đã được xào lại vào bộ bài rút.

# Cuộc đua
milebymile-new-race = Cuộc đua mới bắt đầu!
milebymile-race-complete = Cuộc đua kết thúc! Đang tính điểm...
milebymile-earned-points = { $name } kiếm được { $score } điểm trong chặng này: { $breakdown }.
milebymile-total-scores = Tổng điểm:
milebymile-team-score = { $name }: { $score } điểm

# Chi tiết điểm số
milebymile-from-distance = { $miles } từ quãng đường đã đi
milebymile-from-trip = { $points } từ việc hoàn thành chuyến đi
milebymile-from-perfect = { $points } từ Về đích hoàn hảo
milebymile-from-safe = { $points } từ Chuyến đi an toàn
milebymile-from-shutout = { $points } từ Thắng trắng (đối thủ không đi được dặm nào)
milebymile-from-safeties = { $points } từ { $count } { $safeties ->
    [one] thẻ bảo hộ
   *[other] thẻ bảo hộ
}
milebymile-from-all-safeties = { $points } từ việc có đủ 4 thẻ bảo hộ
milebymile-from-dirty-tricks = { $points } từ { $count } { $tricks ->
    [one] mẹo bẩn
   *[other] mẹo bẩn
}

# Kết thúc game
milebymile-wins-individual = { $player } thắng trò chơi!
milebymile-wins-team = Đội { $team } thắng trò chơi! ({ $members })
milebymile-final-score = Điểm cuối cùng: { $score } điểm

# Thông báo Karma - Xung đột (cả hai đều mất karma)
milebymile-karma-clash-you-target = Cả bạn và mục tiêu đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-you-attacker = Cả bạn và { $attacker } đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-others = { $attacker } và { $target } đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-your-team = Đội của bạn và mục tiêu đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-target-team = Bạn và Đội { $team } đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.
milebymile-karma-clash-other-teams = Đội { $attacker } và Đội { $target } đều bị tẩy chay! Cuộc tấn công bị vô hiệu hóa.

# Thông báo Karma - Người tấn công bị tẩy chay
milebymile-karma-shunned-you = Bạn đã bị tẩy chay vì sự hung hăng! Karma của bạn đã mất.
milebymile-karma-shunned-other = { $player } đã bị tẩy chay vì sự hung hăng của họ!
milebymile-karma-shunned-your-team = Đội của bạn đã bị tẩy chay vì sự hung hăng! Karma của đội đã mất.
milebymile-karma-shunned-other-team = Đội { $team } đã bị tẩy chay vì sự hung hăng của họ!

# Giả nhân giả nghĩa (False Virtue)
milebymile-false-virtue-you = Bạn dùng Giả nhân giả nghĩa và lấy lại Karma!
milebymile-false-virtue-other = { $player } dùng Giả nhân giả nghĩa và lấy lại Karma!
milebymile-false-virtue-your-team = Đội bạn dùng Giả nhân giả nghĩa và lấy lại Karma!
milebymile-false-virtue-other-team = Đội { $team } dùng Giả nhân giả nghĩa và lấy lại Karma!

# Sự cố/Bảo hộ (để hiển thị trạng thái)
milebymile-none = không có

# Lý do không đánh được bài
milebymile-reason-not-on-team = bạn không ở trong đội nào
milebymile-reason-stopped = xe đang bị dừng
milebymile-reason-has-problem = xe đang gặp sự cố không thể chạy
milebymile-reason-speed-limit = đang bị giới hạn tốc độ
milebymile-reason-exceeds-distance = sẽ vượt quá { $miles } dặm
milebymile-reason-no-targets = không có mục tiêu hợp lệ
milebymile-reason-no-speed-limit = bạn không bị giới hạn tốc độ
milebymile-reason-has-right-of-way = thẻ Ưu tiên đường bộ cho phép đi mà không cần Đèn xanh
milebymile-reason-already-moving = xe đang chạy rồi
milebymile-reason-must-fix-first = bạn phải sửa lỗi { $problem } trước
milebymile-reason-has-gas = xe vẫn còn xăng
milebymile-reason-tires-fine = lốp xe vẫn ổn
milebymile-reason-no-accident = xe không bị tai nạn
milebymile-reason-has-safety = bạn đã có thẻ bảo hộ đó rồi
milebymile-reason-has-karma = bạn vẫn còn Karma
milebymile-reason-generic = thẻ này không thể đánh lúc này

# Tên lá bài
milebymile-card-out-of-gas = Hết xăng
milebymile-card-flat-tire = Xịt lốp
milebymile-card-accident = Tai nạn
milebymile-card-speed-limit = Giới hạn tốc độ
milebymile-card-stop = Dừng lại (Đèn đỏ)
milebymile-card-gasoline = Xăng
milebymile-card-spare-tire = Lốp dự phòng
milebymile-card-repairs = Sửa chữa
milebymile-card-end-of-limit = Hết giới hạn tốc độ
milebymile-card-green-light = Đèn xanh
milebymile-card-extra-tank = Thùng xăng phụ
milebymile-card-puncture-proof = Lốp chống thủng
milebymile-card-driving-ace = Tay lái lụa
milebymile-card-right-of-way = Ưu tiên đường bộ
milebymile-card-false-virtue = Giả nhân giả nghĩa
milebymile-card-miles = { $miles } dặm

# Lý do hành động bị vô hiệu hóa
milebymile-no-dirty-trick-window = Không có cơ hội đánh Mẹo bẩn.
milebymile-not-your-dirty-trick = Không phải cơ hội đánh Mẹo bẩn của đội bạn.
milebymile-between-races = Hãy đợi cuộc đua tiếp theo bắt đầu.

# Lỗi xác thực
milebymile-error-karma-needs-three-teams = Luật Karma yêu cầu ít nhất 3 xe/đội riêng biệt.

milebymile-you-play-safety-with-effect = Bạn chơi { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } chơi { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = Bạn chơi { $card } như một Đòn Bẩn. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } chơi { $card } như một Đòn Bẩn. { $effect }
milebymile-safety-effect-extra-tank = Giờ được bảo vệ khỏi Hết Xăng.
milebymile-safety-effect-puncture-proof = Giờ được bảo vệ khỏi Xịt Lốp.
milebymile-safety-effect-driving-ace = Giờ được bảo vệ khỏi Tai Nạn.
milebymile-safety-effect-right-of-way = Giờ được bảo vệ khỏi Dừng và Giới Hạn Tốc Độ.
