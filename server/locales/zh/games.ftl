# PlayPalace 共享游戏消息 (简体中文)
# 这些消息在多个游戏中通用

# 游戏名称
game-name-ninetynine = 九十九

# 回合和轮次流程
game-round-start = 第 { $round } 回合。
game-round-end = 第 { $round } 回合结束。
game-turn-start = 轮到 { $player }。
game-your-turn = 轮到你了。
game-no-turn = 现在不是任何人的回合。

# 分数显示
game-scores-header = 当前分数：
game-score-line = { $player }：{ $score } 分
game-final-scores-header = 最终分数：

# 胜负
game-winner = { $player } 获胜！
game-winner-score = { $player } 以 { $score } 分获胜！
game-tiebreaker = 平局！加赛回合！
game-tiebreaker-players = { $players } 之间平局！加赛回合！
game-eliminated = { $player } 以 { $score } 分被淘汰。

# 通用选项
game-set-target-score = 目标分数：{ $score }
game-enter-target-score = 输入目标分数：
game-option-changed-target = 目标分数已设为 { $score }。

game-set-team-mode = 团队模式：{ $mode }
game-select-team-mode = 选择团队模式
game-option-changed-team = 团队模式已设为 { $mode }。
game-team-mode-individual = 个人
game-team-mode-x-teams-of-y = { $num_teams } 个 { $team_size } 人团队

# 布尔选项值
option-on = 开启
option-off = 关闭

# 状态框

# 游戏结束
game-leave = 离开游戏

# 回合计时器
round-timer-paused = { $player } 已暂停游戏 (按 p 开始下一回合)。
round-timer-resumed = 回合计时器已恢复。
round-timer-countdown = 下一回合倒计时 { $seconds } 秒...

# 骰子游戏 - 保留/释放骰子
dice-keeping = 保留 { $value }。
dice-rerolling = 重掷 { $value }。
dice-locked = 该骰子已锁定，无法更改。
dice-status-locked = locked
dice-status-kept = kept

# 发牌 (纸牌游戏)
game-deal-counter = 发牌 { $current }/{ $total }。
game-you-deal = 你发牌。
game-player-deals = { $player } 发牌。

# 牌名
card-name = { $suit }{ $rank }
no-cards = 没有牌

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = 黑色
color-black-m = 黑色
color-black-f = 黑色
color-blue = 蓝色
color-blue-m = 蓝色
color-blue-f = 蓝色
color-brown = 棕色
color-brown-m = 棕色
color-brown-f = 棕色
color-gray = 灰色
color-gray-m = 灰色
color-gray-f = 灰色
color-green = 绿色
color-green-m = 绿色
color-green-f = 绿色
color-indigo = 靖蓝色
color-indigo-m = 靖蓝色
color-indigo-f = 靖蓝色
color-orange = 橙色
color-orange-m = 橙色
color-orange-f = 橙色
color-pink = 粉色
color-pink-m = 粉色
color-pink-f = 粉色
color-purple = 紫色
color-purple-m = 紫色
color-purple-f = 紫色
color-red = 红色
color-red-m = 红色
color-red-f = 红色
color-violet = 紫罗兰色
color-violet-m = 紫罗兰色
color-violet-f = 紫罗兰色
color-white = 白色
color-white-m = 白色
color-white-f = 白色
color-yellow = 黄色
color-yellow-m = 黄色
color-yellow-f = 黄色

# 花色名称
suit-diamonds = 方块
suit-clubs = 梅花
suit-hearts = 红心
suit-spades = 黑桃

# 点数名称
rank-ace = A
rank-ace-plural = A
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
rank-jack = J
rank-jack-plural = J
rank-queen = Q
rank-queen-plural = Q
rank-king = K
rank-king-plural = K

# 扑克牌型描述
poker-high-card-with = { $high }高牌，带{ $rest }
poker-high-card = { $high }高牌
poker-pair-with = 一对{ $pair }，带{ $rest }
poker-pair = 一对{ $pair }
poker-two-pair-with = 两对{ $high }和{ $low }，带{ $kicker }
poker-two-pair = 两对{ $high }和{ $low }
poker-trips-with = 三条{ $trips }，带{ $rest }
poker-trips = 三条{ $trips }
poker-straight-high = { $high }高顺子
poker-flush-high-with = { $high }高同花，带{ $rest }
poker-full-house = 葫芦，{ $trips }带{ $pair }
poker-quads-with = 四条{ $quads }，带{ $kicker }
poker-quads = 四条{ $quads }
poker-straight-flush-high = { $high }高同花顺
poker-unknown-hand = 未知牌型
