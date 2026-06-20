# マイルバイマイル

# ゲーム名
game-name-milebymile = マイルバイマイル

# ゲームオプション
milebymile-set-distance = レース距離: { $miles }マイル
milebymile-enter-distance = レース距離を入力(300-3000)
milebymile-set-winning-score = 勝利スコア: { $score }点
milebymile-enter-winning-score = 勝利スコアを入力(1000-10000)
milebymile-toggle-perfect-crossing = 正確なフィニッシュを要求: { $enabled }
milebymile-toggle-stacking = 攻撃のスタッキングを許可: { $enabled }
milebymile-toggle-reshuffle = 捨て札をシャッフル: { $enabled }
milebymile-toggle-karma = カルマルール: { $enabled }
milebymile-set-rig = デッキ操作: { $rig }
milebymile-select-rig = デッキ操作オプションを選択

# オプション変更通知
milebymile-option-changed-distance = レース距離が{ $miles }マイルに設定されました。
milebymile-option-changed-winning = 勝利スコアが{ $score }点に設定されました。
milebymile-option-changed-crossing = 正確なフィニッシュ要求が{ $enabled }になりました。
milebymile-option-changed-stacking = 攻撃のスタッキング許可が{ $enabled }になりました。
milebymile-option-changed-reshuffle = 捨て札のシャッフルが{ $enabled }になりました。
milebymile-option-changed-karma = カルマルールが{ $enabled }になりました。
milebymile-option-changed-rig = デッキ操作が{ $rig }に設定されました。

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# ステータス
milebymile-status = { $name }: { $points }点、{ $miles }マイル、問題: { $problems }、セーフティ: { $safeties }

# カードアクション
milebymile-no-matching-safety = 対応するセーフティカードを持っていません!
milebymile-cant-play = { $card }はプレイできません、理由: { $reason }。
milebymile-no-card-selected = 破棄するカードが選択されていません。
milebymile-no-valid-targets = このハザードの有効なターゲットがありません!
milebymile-you-drew = あなたは{ $card }をドローしました
milebymile-discards = { $player }がカードを破棄しました。
milebymile-select-target = ターゲットを選択

# 距離のプレイ
milebymile-plays-distance-individual = { $player }は{ $distance }マイルをプレイし、現在{ $total }マイルです。
milebymile-plays-distance-team = { $player }は{ $distance }マイルをプレイし、チームは現在{ $total }マイルです。

# 旅の完了
milebymile-journey-complete-perfect-individual = { $player }が完璧なクロッシングで旅を完了しました!
milebymile-journey-complete-perfect-team = チーム{ $team }が完璧なクロッシングで旅を完了しました!
milebymile-journey-complete-individual = { $player }が旅を完了しました!
milebymile-journey-complete-team = チーム{ $team }が旅を完了しました!

# ハザードのプレイ
milebymile-plays-hazard-individual = { $player }は{ $target }に{ $card }をプレイしました。
milebymile-plays-hazard-team = { $player }はチーム{ $team }に{ $card }をプレイしました。

# レメディ/セーフティのプレイ
milebymile-plays-card = { $player }は{ $card }をプレイしました。
milebymile-plays-dirty-trick = { $player }は{ $card }をダーティトリックとしてプレイしました!

# デッキ
milebymile-deck-reshuffled = 捨て札がデッキにシャッフルされました。

# レース
milebymile-new-race = 新しいレースが始まります!
milebymile-race-complete = レース完了!スコアを計算中...
milebymile-earned-points = { $name }はこのレースで{ $score }点を獲得しました: { $breakdown }。
milebymile-total-scores = 合計スコア:
milebymile-team-score = { $name }: { $score }点

# スコアリング詳細
milebymile-from-distance = 移動距離から{ $miles }
milebymile-from-trip = 旅の完了から{ $points }
milebymile-from-perfect = 完璧なクロッシングから{ $points }
milebymile-from-safe = 安全な旅から{ $points }
milebymile-from-shutout = シャットアウトから{ $points }
milebymile-from-safeties = { $count }個のセーフティから{ $points }
milebymile-from-all-safeties = すべての4つのセーフティから{ $points }
milebymile-from-dirty-tricks = { $count }個のダーティトリックから{ $points }

# ゲーム終了
milebymile-wins-individual = { $player }がゲームに勝利しました!
milebymile-wins-team = チーム{ $team }がゲームに勝利しました!({ $members })
milebymile-final-score = 最終スコア: { $score }点

# カルマメッセージ - 衝突(両方カルマ喪失)
milebymile-karma-clash-you-target = あなたとターゲットの両方が軽蔑されました!攻撃は無効化されました。
milebymile-karma-clash-you-attacker = あなたと{ $attacker }の両方が軽蔑されました!攻撃は無効化されました。
milebymile-karma-clash-others = { $attacker }と{ $target }の両方が軽蔑されました!攻撃は無効化されました。
milebymile-karma-clash-your-team = あなたのチームとターゲットの両方が軽蔑されました!攻撃は無効化されました。
milebymile-karma-clash-target-team = あなたとチーム{ $team }の両方が軽蔑されました!攻撃は無効化されました。
milebymile-karma-clash-other-teams = チーム{ $attacker }とチーム{ $target }の両方が軽蔑されました!攻撃は無効化されました。

# カルマメッセージ - 攻撃者が軽蔑される
milebymile-karma-shunned-you = あなたは攻撃性のために軽蔑されました!あなたのカルマは失われました。
milebymile-karma-shunned-other = { $player }は攻撃性のために軽蔑されました!
milebymile-karma-shunned-your-team = あなたのチームは攻撃性のために軽蔑されました!チームのカルマは失われました。
milebymile-karma-shunned-other-team = チーム{ $team }は攻撃性のために軽蔑されました!

# フォールスバーチュー
milebymile-false-virtue-you = あなたはフォールスバーチューをプレイしてカルマを取り戻しました!
milebymile-false-virtue-other = { $player }はフォールスバーチューをプレイしてカルマを取り戻しました!
milebymile-false-virtue-your-team = あなたのチームはフォールスバーチューをプレイしてカルマを取り戻しました!
milebymile-false-virtue-other-team = チーム{ $team }はフォールスバーチューをプレイしてカルマを取り戻しました!

# 問題/セーフティ(ステータス表示用)
milebymile-none = なし

# プレイできないカードの理由
milebymile-reason-not-on-team = チームに所属していません
milebymile-reason-stopped = 停止中です
milebymile-reason-has-problem = 運転を妨げる問題があります
milebymile-reason-speed-limit = 速度制限がアクティブです
milebymile-reason-exceeds-distance = { $miles }マイルを超えてしまいます
milebymile-reason-no-targets = 有効なターゲットがありません
milebymile-reason-no-speed-limit = 速度制限を受けていません
milebymile-reason-has-right-of-way = ライトオブウェイがあるので青信号なしで進めます
milebymile-reason-already-moving = 既に移動中です
milebymile-reason-must-fix-first = まず{ $problem }を修理する必要があります
milebymile-reason-has-gas = 車にはガソリンがあります
milebymile-reason-tires-fine = タイヤは問題ありません
milebymile-reason-no-accident = 車は事故に遭っていません
milebymile-reason-has-safety = 既にそのセーフティを持っています
milebymile-reason-has-karma = まだカルマを持っています
milebymile-reason-generic = 今はプレイできません

# カード名
milebymile-card-out-of-gas = ガス欠
milebymile-card-flat-tire = パンク
milebymile-card-accident = 事故
milebymile-card-speed-limit = 速度制限
milebymile-card-stop = 停止
milebymile-card-gasoline = ガソリン
milebymile-card-spare-tire = スペアタイヤ
milebymile-card-repairs = 修理
milebymile-card-end-of-limit = 制限終了
milebymile-card-green-light = 青信号
milebymile-card-extra-tank = エクストラタンク
milebymile-card-puncture-proof = パンク防止
milebymile-card-driving-ace = ドライビングエース
milebymile-card-right-of-way = ライトオブウェイ
milebymile-card-false-virtue = フォールスバーチュー
milebymile-card-miles = { $miles }マイル

# アクション無効理由
milebymile-no-dirty-trick-window = ダーティトリックウィンドウはアクティブではありません。
milebymile-not-your-dirty-trick = あなたのチームのダーティトリックウィンドウではありません。
milebymile-between-races = 次のレース開始を待ってください。

# 検証エラー
milebymile-error-karma-needs-three-teams = カルマルールには少なくとも3つの異なる車/チームが必要です。

milebymile-you-play-safety-with-effect = あなたは { $card } をプレイします。{ $effect }
milebymile-player-plays-safety-with-effect = { $player } が { $card } をプレイします。{ $effect }
milebymile-you-play-dirty-trick-with-effect = あなたは { $card } をダーティートリックとしてプレイします。{ $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } が { $card } をダーティートリックとしてプレイします。{ $effect }
milebymile-safety-effect-extra-tank = ガス欠から保護されました。
milebymile-safety-effect-puncture-proof = パンクから保護されました。
milebymile-safety-effect-driving-ace = 事故から保護されました。
milebymile-safety-effect-right-of-way = 停止と速度制限から保護されました。
