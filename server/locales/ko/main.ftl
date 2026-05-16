# Main UI messages for PlayPalace

# Game categories
category-card-games = 카드 게임
category-dice-games = 주사위 게임
category-rb-play-center = RB 플레이 센터
category-poker = 포커
category-uncategorized = 미분류

# Menu titles
main-menu-title = 메인 메뉴
play-menu-title = 플레이
categories-menu-title = 게임 카테고리
tables-menu-title = 사용 가능한 테이블

# Menu items
play = 플레이
view-active-tables = 활성 테이블 보기
options = 옵션
logout = 로그아웃
back = 뒤로
go-back = 뒤로 가기
context-menu = 컨텍스트 메뉴.
no-actions-available = 사용 가능한 동작이 없습니다.
create-table = 새 테이블 만들기
join-as-player = 플레이어로 참가
join-as-spectator = 관전자로 참가
leave-table = 테이블 나가기
start-game = 게임 시작
add-bot = 봇 추가
remove-bot = 봇 제거
actions-menu = 동작 메뉴
save-table = 테이블 저장
whose-turn = 누구 차례인지
whos-at-table = 누가 테이블에 있는지
check-scores = 점수 확인
check-scores-detailed = 세부 점수
check-game-options = 게임 옵션 확인
no-game-options = 게임 옵션이 없습니다.

# Turn messages
game-player-skipped = { $player }님은 건너뛰었습니다.

# Table messages
table-created = { $host }님이 새로운 { $game } 테이블을 만들었습니다.
table-joined = { $player }님이 테이블에 참가했습니다.
table-left = { $player }님이 테이블을 떠났습니다.
new-host = { $player }님이 이제 호스트입니다.
waiting-for-players = 플레이어 대기 중. 최소 {$min}명, 최대 { $max }명.
game-starting = 게임 시작!
table-listing = { $host }님의 테이블 ({ $count }명)
table-listing-one = { $host }님의 테이블 ({ $count }명)
table-listing-with = { $host }님의 테이블 ({ $count }명) - { $members }
table-listing-game = { $game }: { $host }님의 테이블 ({ $count }명)
table-listing-game-one = { $game }: { $host }님의 테이블 ({ $count }명)
table-listing-game-with = { $game }: { $host }님의 테이블 ({ $count }명) - { $members }
table-not-exists = 테이블이 더 이상 존재하지 않습니다.
table-full = 테이블이 가득 찼습니다.
player-replaced-by-bot = { $player }님이 떠나고 봇으로 교체되었습니다.
player-took-over = { $player }님이 봇을 대신했습니다.
spectator-joined = { $host }님의 테이블에 관전자로 참가했습니다.

# Spectator mode
spectate = 관전
now-playing = { $player }님이 이제 플레이 중입니다.
now-spectating = { $player }님이 이제 관전 중입니다.
spectator-left = { $player }님이 관전을 중단했습니다.

# General
welcome = PlayPalace에 오신 것을 환영합니다!
goodbye = 안녕히 가세요!

# User presence announcements
user-online = { $player }님이 접속했습니다.
user-offline = { $player }님이 접속을 종료했습니다.
user-is-admin = { $player }님은 PlayPalace의 관리자입니다.
user-is-server-owner = { $player }님은 PlayPalace의 서버 소유자입니다.
online-users-none = 접속한 사용자가 없습니다.
online-users-one = 1명: { $users }
online-users-many = { $count }명: { $users }
online-user-not-in-game = 게임 중이 아님
online-user-waiting-approval = 승인 대기 중

# Options
language = 언어
language-option = 언어: { $language }
language-changed = 언어가 { $language }(으)로 설정되었습니다.

# Boolean option states
option-on = 켜짐
option-off = 꺼짐

# Sound options
turn-sound-option = 턴 사운드: { $status }

# Dice options
clear-kept-option = 굴릴 때 보관된 주사위 지우기: { $status }
dice-keeping-style-option = 주사위 보관 방식: { $style }
dice-keeping-style-changed = 주사위 보관 방식이 { $style }(으)로 설정되었습니다.
dice-keeping-style-indexes = 주사위 번호
dice-keeping-style-values = 주사위 값

# Bot names
cancel = 취소
no-bot-names-available = 사용 가능한 봇 이름이 없습니다.
select-bot-name = 봇 이름을 선택하세요
enter-bot-name = 봇 이름 입력
no-options-available = 사용 가능한 옵션이 없습니다.
no-scores-available = 사용 가능한 점수가 없습니다.

# Duration estimation
estimate-duration = 예상 시간 계산
estimate-computing = 게임 예상 시간 계산 중...
estimate-result = 봇 평균: { $bot_time } (± { $std_dev }). { $outlier_info }예상 플레이어 시간: { $human_time }.
estimate-error = 시간을 예상할 수 없습니다.
estimate-already-running = 시간 예상이 이미 진행 중입니다.

# Save/Restore
saved-tables = 저장된 테이블
no-saved-tables = 저장된 테이블이 없습니다.
no-active-tables = 활성 테이블이 없습니다.
restore-table = 복원
delete-saved-table = 삭제
saved-table-deleted = 저장된 테이블이 삭제되었습니다.
missing-players = 복원할 수 없습니다: 다음 플레이어를 사용할 수 없습니다: { $players }
table-restored = 테이블이 복원되었습니다! 모든 플레이어가 전송되었습니다.
table-saved-destroying = 테이블이 저장되었습니다! 메인 메뉴로 돌아갑니다.
game-type-not-found = 게임 유형이 더 이상 존재하지 않습니다.

# Action disabled reasons
action-not-your-turn = 당신의 차례가 아닙니다.
action-not-playing = 게임이 시작되지 않았습니다.
action-spectator = 관전자는 이 작업을 할 수 없습니다.
action-not-host = 호스트만 이 작업을 할 수 있습니다.
action-game-in-progress = 게임이 진행 중일 때는 이 작업을 할 수 없습니다.
action-need-more-players = 시작하려면 더 많은 플레이어가 필요합니다.
action-table-full = 테이블이 가득 찼습니다.
action-no-bots = 제거할 봇이 없습니다.
action-bots-cannot = 봇은 이 작업을 할 수 없습니다.
action-no-scores = 아직 사용 가능한 점수가 없습니다.

# Dice actions
dice-not-rolled = 아직 굴리지 않았습니다.
dice-locked = 이 주사위는 잠겨 있습니다.
dice-no-dice = 사용 가능한 주사위가 없습니다.

# Game actions
game-turn-start = { $player }님의 차례입니다.
game-no-turn = 지금은 아무도 차례가 아닙니다.
table-no-players = 플레이어가 없습니다.
table-players-one = { $count }명: { $players }.
table-players-many = { $count }명: { $players }.
table-spectators = 관전자: { $spectators }.
game-leave = 나가기
game-over = 게임 종료
game-final-scores = 최종 점수
game-points = { $count }점
play = 플레이

# Leaderboards
leaderboards = 리더보드
leaderboards-menu-title = 리더보드
leaderboards-select-game = 리더보드를 볼 게임을 선택하세요
leaderboard-no-data = 이 게임에 대한 리더보드 데이터가 아직 없습니다.

# Leaderboard types
leaderboard-type-wins = 승리 리더
leaderboard-type-rating = 실력 등급
leaderboard-type-total-score = 총 점수
leaderboard-type-high-score = 최고 점수
leaderboard-type-games-played = 플레이한 게임
leaderboard-type-avg-points-per-turn = 턴당 평균 점수
leaderboard-type-best-single-turn = 최고 단일 턴
leaderboard-type-score-per-round = 라운드당 점수

# Leaderboard headers
leaderboard-wins-header = { $game } - 승리 리더
leaderboard-total-score-header = { $game } - 총 점수
leaderboard-high-score-header = { $game } - 최고 점수
leaderboard-games-played-header = { $game } - 플레이한 게임
leaderboard-rating-header = { $game } - 실력 등급
leaderboard-avg-points-header = { $game } - 턴당 평균 점수
leaderboard-best-turn-header = { $game } - 최고 단일 턴
leaderboard-score-per-round-header = { $game } - 라운드당 점수

# Leaderboard entries
leaderboard-wins-entry = { $rank }: { $player }, { $wins }승 { $losses }패, 승률 { $percentage }%
leaderboard-score-entry = { $rank }. { $player }: { $value }
leaderboard-avg-entry = { $rank }. { $player }: 평균 { $value }
leaderboard-games-entry = { $rank }. { $player }: { $value }게임

# Player stats
leaderboard-player-stats = 당신의 통계: { $wins }승, { $losses }패 (승률 { $percentage }%)
leaderboard-no-player-stats = 아직 이 게임을 플레이하지 않았습니다.

# Skill rating leaderboard
leaderboard-no-ratings = 이 게임에 대한 등급 데이터가 아직 없습니다.
leaderboard-rating-entry = { $rank }. { $player }: 등급 { $rating } ({ $mu } ± { $sigma })
leaderboard-player-rating = 당신의 등급: { $rating } ({ $mu } ± { $sigma })
leaderboard-no-player-rating = 아직 이 게임에 대한 등급이 없습니다.

# My Stats menu
my-stats = 내 통계
my-stats-select-game = 통계를 볼 게임을 선택하세요
my-stats-no-data = 아직 이 게임을 플레이하지 않았습니다.
my-stats-no-games = 아직 게임을 플레이하지 않았습니다.
my-stats-header = { $game } - 당신의 통계
my-stats-wins = 승리: { $value }
my-stats-losses = 패배: { $value }
my-stats-winrate = 승률: { $value }%
my-stats-games-played = 플레이한 게임: { $value }
my-stats-total-score = 총 점수: { $value }
my-stats-high-score = 최고 점수: { $value }
my-stats-rating = 실력 등급: { $value } ({ $mu } ± { $sigma })
my-stats-no-rating = 아직 실력 등급 없음
my-stats-avg-per-turn = 턴당 평균 점수: { $value }
my-stats-best-turn = 최고 단일 턴: { $value }

# Prediction system
predict-outcomes = 결과 예측
predict-header = 예상 결과 (실력 등급 기준)
predict-entry = { $rank }. { $player } (등급: { $rating })
predict-entry-2p = { $rank }. { $player } (등급: { $rating }, 승률 { $probability }%)
predict-unavailable = 등급 예측을 사용할 수 없습니다.
predict-need-players = 예측을 위해 최소 2명의 플레이어가 필요합니다.
action-need-more-humans = 더 많은 플레이어가 필요합니다.
confirm-leave-game = 정말 테이블을 떠나시겠습니까?
confirm-yes = 예
confirm-no = 아니오

# Administration
administration = 관리
admin-menu-title = 관리

# Account approval
account-approval = 계정 승인
account-approval-menu-title = 계정 승인
no-pending-accounts = 대기 중인 계정이 없습니다.
approve-account = 승인
decline-account = 거부
account-approved = { $player }님의 계정이 승인되었습니다.
account-declined = { $player }님의 계정이 거부되고 삭제되었습니다.

# Waiting for approval (shown to unapproved users)
waiting-for-approval = 귀하의 계정은 관리자의 승인을 기다리고 있습니다.
account-approved-welcome = 귀하의 계정이 승인되었습니다! PlayPalace에 오신 것을 환영합니다!
account-declined-goodbye = 귀하의 계정 요청이 거부되었습니다.
    사유:
account-banned = 귀하의 계정은 차단되어 액세스할 수 없습니다.

# Login errors
incorrect-username = 입력한 사용자 이름이 존재하지 않습니다.
incorrect-password = 입력한 비밀번호가 올바르지 않습니다.
already-logged-in = 이 계정은 이미 로그인되어 있습니다.

# 자격 증명 검증
credential-username-length = 사용자 이름은 { $min }자 이상 { $max }자 이하여야 합니다.
credential-password-length = 비밀번호는 { $min }자 이상 { $max }자 이하여야 합니다.

# 속도 제한
rate-limit-login-ip = 이 주소에서 로그인 시도가 너무 많습니다. 잠시 후 다시 시도해 주세요.
rate-limit-login-user = 이 사용자 이름으로 로그인 실패가 너무 많습니다. 잠시 후 다시 시도해 주세요.
rate-limit-registration = 이 주소에서 등록 시도가 너무 많습니다. 잠시 후 다시 시도해 주세요.
rate-limit-refresh = 이 주소에서 갱신 시도가 너무 많습니다. 잠시 후 다시 시도해 주세요.

# 세션/인증 오류
account-not-found = 계정을 찾을 수 없습니다.
session-expired = 세션이 만료되었습니다. 다시 로그인해 주세요.
session-token-mismatch = 세션 토큰이 사용자 이름과 일치하지 않습니다.
refresh-token-expired = 갱신 토큰이 만료되었습니다. 다시 로그인해 주세요.
refresh-token-mismatch = 갱신 토큰이 사용자 이름과 일치하지 않습니다.

# 등록
registration-success = 등록이 완료되었습니다! 계정 승인을 기다리고 있습니다.
registration-username-taken = 이미 사용 중인 사용자 이름입니다. 다른 사용자 이름을 선택해 주세요.

# 기본 설정
pref-invalid-value = 잘못된 선택입니다. 기본값을 사용합니다.

# Decline reason
decline-reason-prompt = 거부 사유를 입력하세요 (또는 Escape를 눌러 취소):
account-action-empty-reason = 사유가 제공되지 않았습니다.

# Admin notifications for account requests
account-request = 계정 요청
account-action = 계정 조치 완료

# Admin promotion/demotion
promote-admin = 관리자 승격
demote-admin = 관리자 강등
promote-admin-menu-title = 관리자 승격
demote-admin-menu-title = 관리자 강등
no-users-to-promote = 승격할 사용자가 없습니다.
no-admins-to-demote = 강등할 관리자가 없습니다.
confirm-promote = { $player }님을 관리자로 승격하시겠습니까?
confirm-demote = { $player }님을 관리자에서 강등하시겠습니까?
broadcast-to-all = 모든 사용자에게 알림
broadcast-to-admins = 관리자에게만 알림
broadcast-to-nobody = 무음 (알림 없음)
promote-announcement = { $player }님이 관리자로 승격되었습니다!
promote-announcement-you = 당신은 관리자로 승격되었습니다!
demote-announcement = { $player }님이 관리자에서 강등되었습니다.
demote-announcement-you = 당신은 관리자에서 강등되었습니다.
not-admin-anymore = 당신은 더 이상 관리자가 아니므로 이 작업을 수행할 수 없습니다.
not-server-owner = 서버 소유자만 이 작업을 수행할 수 있습니다.

# Server ownership transfer
transfer-ownership = 소유권 이전
transfer-ownership-menu-title = 소유권 이전
no-admins-for-transfer = 소유권을 이전할 관리자가 없습니다.
confirm-transfer-ownership = { $player }님에게 서버 소유권을 이전하시겠습니까? 당신은 관리자로 강등됩니다.
transfer-ownership-announcement = { $player }님이 이제 Play Palace 서버 소유자입니다!
transfer-ownership-announcement-you = 당신은 이제 Play Palace 서버 소유자입니다!

# User banning
ban-user = 사용자 차단
unban-user = 사용자 차단 해제
no-users-to-ban = 차단할 사용자가 없습니다.
no-users-to-unban = 차단 해제할 사용자가 없습니다.
confirm-ban = { $player }님을 차단하시겠습니까?
confirm-unban = { $player }님의 차단을 해제하시겠습니까?
ban-reason-prompt = 차단 사유를 입력하세요 (선택 사항):
unban-reason-prompt = 차단 해제 사유를 입력하세요 (선택 사항):
user-banned = { $player }님이 차단되었습니다.
user-unbanned = { $player }님의 차단이 해제되었습니다.
you-have-been-banned = 이 서버에서 차단되었습니다.
    사유:
you-have-been-unbanned = 이 서버에서 차단이 해제되었습니다.
    사유:
ban-no-reason = 사유가 제공되지 않았습니다.

# Virtual bots (server owner only)
virtual-bots = 가상 봇
virtual-bots-fill = 서버 채우기
virtual-bots-clear = 모든 봇 제거
virtual-bots-status = 상태
virtual-bots-clear-confirm = 모든 가상 봇을 제거하시겠습니까? 이렇게 하면 봇이 있는 모든 테이블도 제거됩니다.
virtual-bots-not-available = 가상 봇을 사용할 수 없습니다.
virtual-bots-filled = { $added }개의 가상 봇을 추가했습니다. { $online }개가 현재 접속 중입니다.
virtual-bots-already-filled = 구성의 모든 가상 봇이 이미 활성화되어 있습니다.
virtual-bots-cleared = { $bots }개의 가상 봇을 제거하고 { $tables }개의 테이블을 파괴했습니다.
virtual-bot-table-closed = 관리자가 테이블을 닫았습니다.
virtual-bots-none-to-clear = 제거할 가상 봇이 없습니다.
virtual-bots-status-report = 가상 봇: 총 { $total }개, 접속 중 { $online }개, 오프라인 { $offline }개, 게임 중 { $in_game }개.
virtual-bots-guided-overview = 가이드 테이블
virtual-bots-groups-overview = 봇 그룹
virtual-bots-profiles-overview = 프로필
virtual-bots-guided-header = 가이드 테이블: { $count }개 규칙. 할당: { $allocation }, 대체: { $fallback }, 기본 프로필: { $default_profile }.
virtual-bots-guided-empty = 구성된 가이드 테이블 규칙이 없습니다.
virtual-bots-guided-status-active = 활성
virtual-bots-guided-status-inactive = 비활성
virtual-bots-guided-table-linked = 테이블 { $table_id }에 연결됨 (호스트 { $host }, 플레이어 { $players }, 인간 { $humans })
virtual-bots-guided-table-stale = 테이블 { $table_id }가 서버에 없음
virtual-bots-guided-table-unassigned = 현재 추적 중인 테이블 없음
virtual-bots-guided-next-change = { $ticks }틱 후 다음 변경
virtual-bots-guided-no-schedule = 스케줄 시간대 없음
virtual-bots-guided-warning = ⚠ 미달
virtual-bots-guided-line = { $table }: 게임 { $game }, 우선순위 { $priority }, 봇 { $assigned } (최소 { $min_bots }, 최대 { $max_bots }), 대기 { $waiting }, 사용 불가 { $unavailable }, 상태 { $status }, 프로필 { $profile }, 그룹 { $groups }. { $table_state }. { $next_change } { $warning_text }
virtual-bots-groups-header = 봇 그룹: { $count }개 태그, { $bots }개 구성된 봇.
virtual-bots-groups-empty = 정의된 봇 그룹이 없습니다.
virtual-bots-groups-line = { $group }: 프로필 { $profile }, 봇 { $total } (접속 { $online }, 대기 { $waiting }, 게임 중 { $in_game }, 오프라인 { $offline }), 규칙 { $rules }.
virtual-bots-groups-no-rules = 없음
virtual-bots-no-profile = 기본
virtual-bots-profile-inherit-default = 기본 프로필 상속
virtual-bots-profiles-header = 프로필: { $count }개 정의됨 (기본: { $default_profile }).
virtual-bots-profiles-empty = 정의된 프로필이 없습니다.
virtual-bots-profiles-line = { $profile } ({ $bot_count }개 봇) 재정의: { $overrides }.
virtual-bots-profiles-no-overrides = 기본 구성 상속

localization-in-progress-try-again = 현지화 작업이 진행 중입니다. 1분 후에 다시 시도해 주세요.
