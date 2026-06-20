# 一里一里 游戏消息
# 注：回合开始、轮次开始、团队模式等通用消息在 games.ftl 中

# 游戏名称
game-name-milebymile = 一里一里

# 游戏选项
milebymile-set-distance = 比赛距离：{ $miles } 英里
milebymile-enter-distance = 输入比赛距离 (300-3000)
milebymile-set-winning-score = 获胜分数：{ $score } 分
milebymile-enter-winning-score = 输入获胜分数 (1000-10000)
milebymile-toggle-perfect-crossing = 必须精确到达：{ $enabled }
milebymile-toggle-stacking = 允许叠加攻击：{ $enabled }
milebymile-toggle-reshuffle = 重新洗牌弃牌堆：{ $enabled }
milebymile-toggle-karma = 因果规则：{ $enabled }
milebymile-set-rig = 牌组调整：{ $rig }
milebymile-select-rig = 选择牌组调整选项

# 选项变更通知
milebymile-option-changed-distance = 比赛距离已设为 { $miles } 英里。
milebymile-option-changed-winning = 获胜分数已设为 { $score } 分。
milebymile-option-changed-crossing = 必须精确到达 { $enabled }。
milebymile-option-changed-stacking = 允许叠加攻击 { $enabled }。
milebymile-option-changed-reshuffle = 重新洗牌弃牌堆 { $enabled }。
milebymile-option-changed-karma = 因果规则 { $enabled }。
milebymile-option-changed-rig = 牌组调整已设为 { $rig }。

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# 状态
milebymile-status = { $name }：{ $miles } 英里，问题：{ $problems }，安全牌：{ $safeties }

# 出牌动作
milebymile-no-matching-safety = 你没有对应的安全牌！
milebymile-cant-play = 你不能打出 { $card }，因为{ $reason }。
milebymile-no-card-selected = 没有选中要弃掉的牌。
milebymile-no-valid-targets = 没有有效的攻击目标！
milebymile-you-drew = 你抽到：{ $card }
milebymile-discards = { $player } 弃掉一张牌。
milebymile-select-target = 选择目标

# 里程牌
milebymile-plays-distance-individual = { $player } 打出 { $distance } 英里，现在共 { $total } 英里。
milebymile-plays-distance-team = { $player } 打出 { $distance } 英里；队伍现在共 { $total } 英里。

# 完成旅程
milebymile-journey-complete-perfect-individual = { $player } 完美抵达，完成了旅程！
milebymile-journey-complete-perfect-team = 第 { $team } 队完美抵达，完成了旅程！
milebymile-journey-complete-individual = { $player } 完成了旅程！
milebymile-journey-complete-team = 第 { $team } 队完成了旅程！

# 危险牌
milebymile-plays-hazard-individual = { $player } 对 { $target } 打出 { $card }。
milebymile-plays-hazard-team = { $player } 对第 { $team } 队打出 { $card }。

# 补救牌/安全牌
milebymile-plays-card = { $player } 打出 { $card }。
milebymile-plays-dirty-trick = { $player } 打出 { $card } 作为反击！

# 牌组
milebymile-deck-reshuffled = 弃牌堆已洗回牌组。

# 比赛
milebymile-new-race = 新的比赛开始！
milebymile-race-complete = 比赛结束！计算得分中...
milebymile-earned-points = { $name } 本场获得 { $score } 分：{ $breakdown }。
milebymile-total-scores = 总分：
milebymile-team-score = { $name }：{ $score } 分

# 得分明细
milebymile-from-distance = 行驶距离 { $miles } 分
milebymile-from-trip = 完成旅程 { $points } 分
milebymile-from-perfect = 完美抵达 { $points } 分
milebymile-from-safe = 安全旅程 { $points } 分
milebymile-from-shutout = 完封对手 { $points } 分
milebymile-from-safeties = { $count } 张安全牌 { $points } 分
milebymile-from-all-safeties = 集齐4张安全牌 { $points } 分
milebymile-from-dirty-tricks = { $count } 次反击 { $points } 分

# 游戏结束
milebymile-wins-individual = { $player } 赢得游戏！
milebymile-wins-team = 第 { $team } 队赢得游戏！（{ $members }）
milebymile-final-score = 最终得分：{ $score } 分

# 因果消息 - 双方失去因果
milebymile-karma-clash-you-target = 你和你的目标都被遗弃了！攻击被抵消。
milebymile-karma-clash-you-attacker = 你和 { $attacker } 都被遗弃了！攻击被抵消。
milebymile-karma-clash-others = { $attacker } 和 { $target } 都被遗弃了！攻击被抵消。
milebymile-karma-clash-your-team = 你的队伍和目标队伍都被遗弃了！攻击被抵消。
milebymile-karma-clash-target-team = 你和第 { $team } 队都被遗弃了！攻击被抵消。
milebymile-karma-clash-other-teams = 第 { $attacker } 队和第 { $target } 队都被遗弃了！攻击被抵消。

# 因果消息 - 攻击者被遗弃
milebymile-karma-shunned-you = 你因攻击而被遗弃！你的因果已失去。
milebymile-karma-shunned-other = { $player } 因攻击而被遗弃！
milebymile-karma-shunned-your-team = 你的队伍因攻击而被遗弃！队伍的因果已失去。
milebymile-karma-shunned-other-team = 第 { $team } 队因攻击而被遗弃！

# 虚假美德
milebymile-false-virtue-you = 你打出虚假美德，恢复了因果！
milebymile-false-virtue-other = { $player } 打出虚假美德，恢复了因果！
milebymile-false-virtue-your-team = 你的队伍打出虚假美德，恢复了因果！
milebymile-false-virtue-other-team = 第 { $team } 队打出虚假美德，恢复了因果！

# 问题/安全牌（状态显示用）
milebymile-none = 无

# 不可打出的原因
milebymile-reason-not-on-team = 你不在队伍中
milebymile-reason-stopped = 你被停止了
milebymile-reason-has-problem = 你有问题阻止行驶
milebymile-reason-speed-limit = 限速生效中
milebymile-reason-exceeds-distance = 会超过 { $miles } 英里
milebymile-reason-no-targets = 没有有效目标
milebymile-reason-no-speed-limit = 你没有被限速
milebymile-reason-has-right-of-way = 优先通行权让你无需绿灯
milebymile-reason-already-moving = 你已经在行驶中
milebymile-reason-must-fix-first = 你必须先修复{ $problem }
milebymile-reason-has-gas = 你的车有油
milebymile-reason-tires-fine = 你的轮胎完好
milebymile-reason-no-accident = 你的车没有发生事故
milebymile-reason-has-safety = 你已经有那张安全牌
milebymile-reason-has-karma = 你还有因果
milebymile-reason-generic = 现在无法打出

# 卡牌名称
milebymile-card-out-of-gas = 油尽
milebymile-card-flat-tire = 爆胎
milebymile-card-accident = 事故
milebymile-card-speed-limit = 限速
milebymile-card-stop = 停车
milebymile-card-gasoline = 加油
milebymile-card-spare-tire = 备胎
milebymile-card-repairs = 修理
milebymile-card-end-of-limit = 解除限速
milebymile-card-green-light = 绿灯
milebymile-card-extra-tank = 备用油箱
milebymile-card-puncture-proof = 防爆轮胎
milebymile-card-driving-ace = 王牌司机
milebymile-card-right-of-way = 优先通行
milebymile-card-false-virtue = 虚假美德
milebymile-card-miles = { $miles } 英里

milebymile-you-play-safety-with-effect = 你打出 { $card }。{ $effect }
milebymile-player-plays-safety-with-effect = { $player } 打出 { $card }。{ $effect }
milebymile-you-play-dirty-trick-with-effect = 你将 { $card } 作为反击打出。{ $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } 将 { $card } 作为反击打出。{ $effect }
milebymile-safety-effect-extra-tank = 现在可防止缺油。
milebymile-safety-effect-puncture-proof = 现在可防止爆胎。
milebymile-safety-effect-driving-ace = 现在可防止事故。
milebymile-safety-effect-right-of-way = 现在可防止停车和限速。
