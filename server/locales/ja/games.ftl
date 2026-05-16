# PlayPalaceの共通ゲームメッセージ
# これらのメッセージは複数のゲームで共通です

# ゲーム名
game-name-ninetynine = Ninety Nine

# ラウンドとターンの流れ
game-round-start = ラウンド{ $round }。
game-round-end = ラウンド{ $round }が完了しました。
game-turn-start = { $player }のターンです。
game-your-turn = あなたのターンです。
game-no-turn = 現在は誰のターンでもありません。

# スコア表示
game-scores-header = 現在のスコア:
game-score-line = { $player }: { $score }点
game-final-scores-header = 最終スコア:

# 勝利/敗北
game-winner = { $player }の勝利!
game-winner-score = { $player }が{ $score }点で勝利!
game-tiebreaker = 引き分けです!タイブレーカーラウンド!
game-tiebreaker-players = { $players }間で引き分けです!タイブレーカーラウンド!
game-eliminated = { $player }は{ $score }点で敗退しました。

# 共通オプション
game-set-target-score = 目標スコア: { $score }
game-enter-target-score = 目標スコアを入力:
game-option-changed-target = 目標スコアが{ $score }に設定されました。

game-set-team-mode = チームモード: { $mode }
game-select-team-mode = チームモードを選択
game-option-changed-team = チームモードが{ $mode }に設定されました。
game-team-mode-individual = 個人
game-team-mode-x-teams-of-y = { $num_teams }チーム、各{ $team_size }人

# ブール値オプション
option-on = オン
option-off = オフ

# ステータスボックス

# ゲーム終了
game-leave = ゲームを退出

# ラウンドタイマー
round-timer-paused = { $player }がゲームを一時停止しました(pを押して次のラウンドを開始)。
round-timer-resumed = ラウンドタイマーが再開されました。
round-timer-countdown = 次のラウンドまで{ $seconds }秒...

# サイコロゲーム - サイコロの保持/再ロール
dice-keeping = { $value }を保持します。
dice-rerolling = { $value }を再ロールします。
dice-locked = そのサイコロはロックされており変更できません。
dice-status-locked = locked
dice-status-kept = kept

# 配る(カードゲーム)
game-deal-counter = { $current }/{ $total }を配ります。
game-you-deal = あなたがカードを配ります。
game-player-deals = { $player }がカードを配ります。

# カード名
card-name = { $suit }の{ $rank }
no-cards = カードなし

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = 黒
color-black-m = 黒
color-black-f = 黒
color-blue = 青
color-blue-m = 青
color-blue-f = 青
color-brown = 茶色
color-brown-m = 茶色
color-brown-f = 茶色
color-gray = 灰色
color-gray-m = 灰色
color-gray-f = 灰色
color-green = 緑
color-green-m = 緑
color-green-f = 緑
color-indigo = 藍色
color-indigo-m = 藍色
color-indigo-f = 藍色
color-orange = オレンジ
color-orange-m = オレンジ
color-orange-f = オレンジ
color-pink = ピンク
color-pink-m = ピンク
color-pink-f = ピンク
color-purple = 紫
color-purple-m = 紫
color-purple-f = 紫
color-red = 赤
color-red-m = 赤
color-red-f = 赤
color-violet = すみれ色
color-violet-m = すみれ色
color-violet-f = すみれ色
color-white = 白
color-white-m = 白
color-white-f = 白
color-yellow = 黄色
color-yellow-m = 黄色
color-yellow-f = 黄色

# スート名
suit-diamonds = ダイヤ
suit-clubs = クラブ
suit-hearts = ハート
suit-spades = スペード

# ランク名
rank-ace = エース
rank-ace-plural = エース
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
rank-jack = ジャック
rank-jack-plural = ジャック
rank-queen = クイーン
rank-queen-plural = クイーン
rank-king = キング
rank-king-plural = キング

# ポーカーハンドの説明
poker-high-card-with = { $high }ハイ、{ $rest }
poker-high-card = { $high }ハイ
poker-pair-with = { $pair }のペア、{ $rest }
poker-pair = { $pair }のペア
poker-two-pair-with = ツーペア、{ $high }と{ $low }、キッカー{ $kicker }
poker-two-pair = ツーペア、{ $high }と{ $low }
poker-trips-with = スリーカード、{ $trips }、{ $rest }
poker-trips = スリーカード、{ $trips }
poker-straight-high = { $high }ハイストレート
poker-flush-high-with = { $high }ハイフラッシュ、{ $rest }
poker-full-house = フルハウス、{ $trips }オーバー{ $pair }
poker-quads-with = フォーカード、{ $quads }、キッカー{ $kicker }
poker-quads = フォーカード、{ $quads }
poker-straight-flush-high = { $high }ハイストレートフラッシュ
poker-unknown-hand = 不明なハンド

# 検証エラー(ゲーム共通)
game-error-invalid-team-mode = 選択されたチームモードは現在のプレイヤー数に対して有効ではありません。
