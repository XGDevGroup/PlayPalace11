# PlayPalaceのメインUIメッセージ

# ゲームカテゴリー
category-card-games = カードゲーム
category-dice-games = サイコロゲーム
category-board-games = ボードゲーム
category-rb-play-center = RBプレイセンター
category-poker = ポーカー
category-uncategorized = 未分類

# メニュータイトル
main-menu-title = メインメニュー
play-menu-title = プレイ
categories-menu-title = ゲームカテゴリー
tables-menu-title = 利用可能なテーブル

# メニュー項目
play = プレイ
view-active-tables = アクティブなテーブルを表示
options = オプション
logout = ログアウト
back = 戻る
context-menu = コンテキストメニュー。
no-actions-available = アクションはありません。
create-table = 新しいテーブルを作成
join-as-player = プレイヤーとして参加
join-as-spectator = 観戦者として参加
leave-table = テーブルを退出
start-game = ゲーム開始
add-bot = ボットを追加
remove-bot = ボットを削除
actions-menu = アクションメニュー
save-table = テーブルを保存
whose-turn = 誰のターン
whos-at-table = テーブルにいる人
check-scores = スコアを確認
check-scores-detailed = 詳細スコア
check-game-options = ゲームオプションを確認
no-game-options = ゲームオプションはありません。

# ターンメッセージ
game-player-skipped = { $player }はスキップされました。

# テーブルメッセージ
table-created = { $host }が新しい{ $game }テーブルを作成しました。
table-joined = { $player }がテーブルに参加しました。
table-left = { $player }がテーブルを退出しました。
new-host = { $player }がホストになりました。
waiting-for-players = プレイヤーを待っています。最低{ $min }人、最大{ $max }人。
game-starting = ゲーム開始!
table-listing = { $host }のテーブル({ $count }人)
table-listing-one = { $host }のテーブル({ $count }人)
table-listing-with = { $host }のテーブル({ $count }人、{ $members })
table-listing-game = { $game }: { $host }のテーブル({ $count }人)
table-listing-game-one = { $game }: { $host }のテーブル({ $count }人)
table-listing-game-with = { $game }: { $host }のテーブル({ $count }人、{ $members })
table-not-exists = テーブルはもう存在しません。
table-full = テーブルは満席です。
player-replaced-by-bot = { $player }が退出し、ボットに置き換えられました。
player-took-over = { $player }がボットから引き継ぎました。
spectator-joined = { $host }のテーブルに観戦者として参加しました。

# 観戦モード
spectate = 観戦
now-playing = { $player }はプレイ中です。
now-spectating = { $player }は観戦中です。
spectator-left = { $player }が観戦をやめました。

# 一般
welcome = PlayPalaceへようこそ!
goodbye = さようなら!

# ユーザープレゼンス通知
user-online = { $player }がオンラインになりました。
user-offline = { $player }がオフラインになりました。
user-is-admin = { $player }はPlayPalaceの管理者です。
user-is-server-owner = { $player }はPlayPalaceのサーバーオーナーです。
online-users-none = オンラインユーザーはいません。
online-users-one = 1人のユーザー: { $users }
online-users-many = { $count }人のユーザー: { $users }
online-user-not-in-game = ゲーム外
online-user-waiting-approval = 承認待ち

# オプション
language = 言語
language-option = 言語: { $language }
language-changed = 言語が{ $language }に設定されました。

# ブール値オプションの状態
option-on = オン
option-off = オフ

# サウンドオプション
turn-sound-option = ターンサウンド: { $status }

# サイコロオプション
clear-kept-option = ロール時に保持したサイコロをクリア: { $status }
dice-keeping-style-option = サイコロ保持スタイル: { $style }
dice-keeping-style-changed = サイコロ保持スタイルが{ $style }に設定されました。
dice-keeping-style-indexes = サイコロのインデックス
dice-keeping-style-values = サイコロの値

# ボット名
cancel = キャンセル
no-bot-names-available = 利用可能なボット名がありません。
select-bot-name = ボットの名前を選択
enter-bot-name = ボット名を入力
no-options-available = 利用可能なオプションがありません。
no-scores-available = 利用可能なスコアがありません。

# 所要時間推定
estimate-duration = 所要時間を推定
estimate-computing = ゲームの推定所要時間を計算中...
estimate-result = ボット平均: { $bot_time } (± { $std_dev })。{ $outlier_info }推定人間時間: { $human_time }。
estimate-error = 所要時間を推定できませんでした。
estimate-already-running = 所要時間の推定は既に実行中です。

# 保存/復元
saved-tables = 保存されたテーブル
no-saved-tables = 保存されたテーブルはありません。
no-active-tables = アクティブなテーブルはありません。
restore-table = 復元
delete-saved-table = 削除
saved-table-deleted = 保存されたテーブルが削除されました。
missing-players = 復元できません: 次のプレイヤーが利用できません: { $players }
table-restored = テーブルが復元されました!すべてのプレイヤーが転送されました。
table-saved-destroying = テーブルが保存されました!メインメニューに戻ります。
game-type-not-found = ゲームタイプはもう存在しません。

# アクション無効理由
action-not-your-turn = あなたのターンではありません。
action-not-playing = ゲームは開始されていません。
action-spectator = 観戦者はこれを実行できません。
action-not-host = ホストだけがこれを実行できます。
action-game-in-progress = ゲーム進行中はこれを実行できません。
action-need-more-players = 開始するには最低 { $min_players } 人のプレイヤーが必要です。
action-table-full = テーブルは満席です。
action-no-bots = 削除するボットはいません。
action-bots-cannot = ボットはこれを実行できません。
action-no-scores = まだスコアがありません。

# サイコロアクション
dice-not-rolled = まだロールしていません。
dice-locked = このサイコロはロックされています。
dice-no-dice = 利用可能なサイコロがありません。

# ゲームアクション
game-turn-start = { $player }のターンです。
game-no-turn = 現在は誰のターンでもありません。
table-no-players = プレイヤーはいません。
table-players-one = { $count }人のプレイヤー: { $players }。
table-players-many = { $count }人のプレイヤー: { $players }。
table-spectators = 観戦者: { $spectators }。
game-leave = 退出
game-over = ゲームオーバー
game-final-scores = 最終スコア
game-points = { $count }点
play = プレイ

# リーダーボード
leaderboards = リーダーボード
leaderboards-menu-title = リーダーボード
leaderboards-select-game = リーダーボードを表示するゲームを選択
leaderboard-no-data = このゲームのリーダーボードデータはまだありません。

# リーダーボードタイプ
leaderboard-type-wins = 勝利リーダー
leaderboard-type-rating = スキルレーティング
leaderboard-type-total-score = 合計スコア
leaderboard-type-high-score = ハイスコア
leaderboard-type-games-played = プレイ回数
leaderboard-type-avg-points-per-turn = ターンあたり平均点数
leaderboard-type-best-single-turn = 最高シングルターン
leaderboard-type-score-per-round = ラウンドあたりスコア

# リーダーボードヘッダー
leaderboard-wins-header = { $game } - 勝利リーダー
leaderboard-total-score-header = { $game } - 合計スコア
leaderboard-high-score-header = { $game } - ハイスコア
leaderboard-games-played-header = { $game } - プレイ回数
leaderboard-rating-header = { $game } - スキルレーティング
leaderboard-avg-points-header = { $game } - ターンあたり平均点数
leaderboard-best-turn-header = { $game } - 最高シングルターン
leaderboard-score-per-round-header = { $game } - ラウンドあたりスコア

# リーダーボードエントリー
leaderboard-wins-entry = { $rank }: { $player }、{ $wins }勝、{ $losses }敗、勝率{ $percentage }%
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: 平均{ $value }
leaderboard-games-entry = { $rank }. { $player }: { $value }ゲーム

# プレイヤー統計
leaderboard-player-stats = あなたの統計: { $wins }勝、{ $losses }敗(勝率{ $percentage }%)
leaderboard-no-player-stats = このゲームはまだプレイしていません。

# スキルレーティングリーダーボード
leaderboard-no-ratings = このゲームのレーティングデータはまだありません。
leaderboard-rating-entry = { $rank }. { $player }: レーティング{ $rating }({ $mu } ± { $sigma })
leaderboard-player-rating = あなたのレーティング: { $rating }({ $mu } ± { $sigma })
leaderboard-no-player-rating = このゲームのレーティングはまだありません。

# マイ統計メニュー
my-stats = マイ統計
my-stats-select-game = 統計を表示するゲームを選択
my-stats-no-data = このゲームはまだプレイしていません。
my-stats-no-games = ゲームはまだプレイしていません。
my-stats-header = { $game } - あなたの統計
my-stats-wins = 勝利: { $value }
my-stats-losses = 敗北: { $value }
my-stats-winrate = 勝率: { $value }%
my-stats-games-played = プレイ回数: { $value }
my-stats-total-score = 合計スコア: { $value }
my-stats-high-score = ハイスコア: { $value }
my-stats-rating = スキルレーティング: { $value }({ $mu } ± { $sigma })
my-stats-no-rating = スキルレーティングはまだありません
my-stats-avg-per-turn = ターンあたり平均点数: { $value }
my-stats-best-turn = 最高シングルターン: { $value }

# 予測システム
predict-outcomes = 結果を予測
predict-header = 予測結果(スキルレーティング別)
predict-entry = { $rank }. { $player }(レーティング: { $rating })
predict-entry-2p = { $rank }. { $player }(レーティング: { $rating }、勝率{ $probability }%)
predict-unavailable = レーティング予測は利用できません。
predict-need-players = 予測には少なくとも2人の人間プレイヤーが必要です。
action-need-more-humans = もっと人間プレイヤーが必要です。
confirm-leave-game = テーブルを退出してもよろしいですか?
confirm-yes = はい
confirm-no = いいえ

# 管理
administration = 管理
admin-menu-title = 管理

# アカウント承認
account-approval = アカウント承認
account-approval-menu-title = アカウント承認
no-pending-accounts = 保留中のアカウントはありません。
approve-account = 承認
decline-account = 拒否
account-approved = { $player }のアカウントが承認されました。
account-declined = { $player }のアカウントが拒否され削除されました。

# 承認待ち(未承認ユーザーに表示)
waiting-for-approval = あなたのアカウントは管理者の承認を待っています。
account-approved-welcome = あなたのアカウントが承認されました!PlayPalaceへようこそ!
account-declined-goodbye = あなたのアカウント申請は拒否されました。
    理由:
account-banned = あなたのアカウントは禁止されておりアクセスできません。

# ログインエラー
incorrect-username = 入力されたユーザー名は存在しません。
incorrect-password = 入力されたパスワードが正しくありません。
already-logged-in = このアカウントは既にログインしています。

# 認証情報の検証
credential-username-length = ユーザー名は{ $min }文字以上{ $max }文字以下にしてください。
credential-password-length = パスワードは{ $min }文字以上{ $max }文字以下にしてください。

# レート制限
rate-limit-login-ip = このアドレスからのログイン試行が多すぎます。しばらくお待ちの上、再試行してください。
rate-limit-login-user = このユーザー名でのログイン失敗が多すぎます。しばらくお待ちの上、再試行してください。
rate-limit-registration = このアドレスからの登録試行が多すぎます。しばらくお待ちの上、再試行してください。
rate-limit-refresh = このアドレスからの更新試行が多すぎます。しばらくお待ちの上、再試行してください。

# セッション/認証エラー
account-not-found = アカウントが見つかりません。
session-expired = セッションが期限切れです。再度ログインしてください。
session-token-mismatch = セッショントークンがユーザー名と一致しません。
refresh-token-expired = 更新トークンが期限切れです。再度ログインしてください。
refresh-token-mismatch = 更新トークンがユーザー名と一致しません。

# 登録
registration-success = 登録が完了しました。アカウントは承認待ちです。
registration-username-taken = このユーザー名は既に使用されています。別のユーザー名を選んでください。

# 設定のデフォルト値
pref-invalid-value = 無効な選択です。デフォルト値を使用します。

# 拒否理由
decline-reason-prompt = 拒否理由を入力してください(キャンセルするにはEscapeを押してください):
account-action-empty-reason = 理由が指定されていません。

# アカウント申請の管理者通知
account-request = アカウント申請
account-action = アカウントアクション実行済み

# 管理者昇格/降格
promote-admin = 管理者に昇格
demote-admin = 管理者から降格
promote-admin-menu-title = 管理者に昇格
demote-admin-menu-title = 管理者から降格
no-users-to-promote = 昇格可能なユーザーがいません。
no-admins-to-demote = 降格可能な管理者がいません。
confirm-promote = { $player }を管理者に昇格してもよろしいですか?
confirm-demote = { $player }を管理者から降格してもよろしいですか?
broadcast-to-all = すべてのユーザーに通知
broadcast-to-admins = 管理者のみに通知
broadcast-to-nobody = サイレント(通知なし)
promote-announcement = { $player }が管理者に昇格されました!
promote-announcement-you = あなたは管理者に昇格されました!
demote-announcement = { $player }が管理者から降格されました。
demote-announcement-you = あなたは管理者から降格されました。
not-admin-anymore = あなたはもう管理者ではないため、このアクションを実行できません。
not-server-owner = サーバーオーナーだけがこのアクションを実行できます。

# サーバー所有権の譲渡
transfer-ownership = 所有権を譲渡
transfer-ownership-menu-title = 所有権を譲渡
no-admins-for-transfer = 所有権を譲渡できる管理者がいません。
confirm-transfer-ownership = サーバー所有権を{ $player }に譲渡してもよろしいですか?あなたは管理者に降格されます。
transfer-ownership-announcement = { $player }がPlay Palaceサーバーオーナーになりました!
transfer-ownership-announcement-you = あなたがPlay palaceサーバーオーナーになりました!

# ユーザー禁止
ban-user = ユーザーを禁止
unban-user = ユーザーの禁止を解除
no-users-to-ban = 禁止可能なユーザーがいません。
no-users-to-unban = 禁止解除可能なユーザーがいません。
confirm-ban = { $player }を禁止してもよろしいですか?
confirm-unban = { $player }の禁止を解除してもよろしいですか?
ban-reason-prompt = 禁止理由を入力してください(任意):
unban-reason-prompt = 禁止解除理由を入力してください(任意):
user-banned = { $player }が禁止されました。
user-unbanned = { $player }の禁止が解除されました。
you-have-been-banned = あなたはこのサーバーから禁止されました。
    理由:
you-have-been-unbanned = あなたの禁止が解除されました。
    理由:
ban-no-reason = 理由が指定されていません。

# 仮想ボット(サーバーオーナーのみ)
virtual-bots = 仮想ボット
virtual-bots-fill = サーバーを埋める
virtual-bots-clear = すべてのボットをクリア
virtual-bots-status = ステータス
virtual-bots-clear-confirm = すべての仮想ボットをクリアしてもよろしいですか?彼らが参加しているテーブルも破棄されます。
virtual-bots-not-available = 仮想ボットは利用できません。
virtual-bots-filled = { $added }個の仮想ボットを追加しました。{ $online }個がオンラインです。
virtual-bots-already-filled = 設定からのすべての仮想ボットは既にアクティブです。
virtual-bots-cleared = { $bots }個の仮想ボットをクリアし、{ $tables }個のテーブルを破棄しました。
virtual-bot-table-closed = 管理者によってテーブルが閉じられました。
virtual-bots-none-to-clear = クリアする仮想ボットはありません。
virtual-bots-status-report = 仮想ボット: 合計{ $total }個、オンライン{ $online }個、オフライン{ $offline }個、ゲーム中{ $in_game }個。
virtual-bots-guided-overview = ガイド付きテーブル
virtual-bots-groups-overview = ボットグループ
virtual-bots-profiles-overview = プロファイル
virtual-bots-guided-header = ガイド付きテーブル: { $count }個のルール。割り当て: { $allocation }、フォールバック: { $fallback }、デフォルトプロファイル: { $default_profile }。
virtual-bots-guided-empty = ガイド付きテーブルルールは設定されていません。
virtual-bots-guided-status-active = アクティブ
virtual-bots-guided-status-inactive = 非アクティブ
virtual-bots-guided-table-linked = テーブル{ $table_id }にリンク(ホスト{ $host }、プレイヤー{ $players }人、人間{ $humans }人)
virtual-bots-guided-table-stale = テーブル{ $table_id }がサーバーに見つかりません
virtual-bots-guided-table-unassigned = 現在追跡されているテーブルはありません
virtual-bots-guided-next-change = { $ticks }ティック後に次の変更
virtual-bots-guided-no-schedule = スケジューリングウィンドウなし
virtual-bots-guided-warning = ⚠ 不足
virtual-bots-guided-line = { $table }: ゲーム{ $game }、優先度{ $priority }、ボット{ $assigned }個(最小{ $min_bots }、最大{ $max_bots })、待機中{ $waiting }、利用不可{ $unavailable }、ステータス{ $status }、プロファイル{ $profile }、グループ{ $groups }。{ $table_state }。{ $next_change } { $warning_text }
virtual-bots-groups-header = ボットグループ: { $count }個のタグ、{ $bots }個の設定済みボット。
virtual-bots-groups-empty = ボットグループは定義されていません。
virtual-bots-groups-line = { $group }: プロファイル{ $profile }、ボット{ $total }個(オンライン{ $online }、待機中{ $waiting }、ゲーム中{ $in_game }、オフライン{ $offline })、ルール{ $rules }。
virtual-bots-groups-no-rules = なし
virtual-bots-no-profile = デフォルト
virtual-bots-profile-inherit-default = デフォルトプロファイルを継承
virtual-bots-profiles-header = プロファイル: { $count }個定義済み(デフォルト: { $default_profile })。
virtual-bots-profiles-empty = プロファイルは定義されていません。
virtual-bots-profiles-line = { $profile }({ $bot_count }個のボット)オーバーライド: { $overrides }。
virtual-bots-profiles-no-overrides = ベース設定を継承

localization-in-progress-try-again = ローカライズ処理中です。1分後にもう一度お試しください。
