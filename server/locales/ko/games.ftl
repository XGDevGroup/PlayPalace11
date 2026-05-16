# Shared game messages for PlayPalace
# These messages are common across multiple games

# Game names
game-name-ninetynine = 나인티 나인

# Round and turn flow
game-round-start = 라운드 { $round }.
game-round-end = 라운드 { $round } 완료.
game-turn-start = { $player }님의 차례입니다.
game-your-turn = 당신의 차례입니다.
game-no-turn = 지금은 아무도 차례가 아닙니다.

# Score display
game-scores-header = 현재 점수:
game-score-line = { $player }: { $score }점
game-final-scores-header = 최종 점수:

# Win/loss
game-winner = { $player }님이 승리했습니다!
game-winner-score = { $player }님이 { $score }점으로 승리했습니다!
game-tiebreaker = 무승부! 타이브레이커 라운드!
game-tiebreaker-players = { $players } 간 무승부! 타이브레이커 라운드!
game-eliminated = { $player }님이 { $score }점으로 탈락했습니다.

# Common options
game-set-target-score = 목표 점수: { $score }
game-enter-target-score = 목표 점수 입력:
game-option-changed-target = 목표 점수가 { $score }점으로 설정되었습니다.

game-set-team-mode = 팀 모드: { $mode }
game-select-team-mode = 팀 모드 선택
game-option-changed-team = 팀 모드가 { $mode }(으)로 설정되었습니다.
game-team-mode-individual = 개인전
game-team-mode-x-teams-of-y = { $num_teams }팀 { $team_size }명

# Boolean option values
option-on = 켜짐
option-off = 꺼짐

# Status box

# Game end
game-leave = 게임 나가기

# Round timer
round-timer-paused = { $player }님이 게임을 일시정지했습니다 (p를 눌러 다음 라운드를 시작하세요).
round-timer-resumed = 라운드 타이머가 재개되었습니다.
round-timer-countdown = { $seconds }초 후 다음 라운드...

# Dice games - keeping/releasing dice
dice-keeping = { $value }을(를) 보관합니다.
dice-rerolling = { $value }을(를) 다시 굴립니다.
dice-locked = 해당 주사위는 잠겨있어서 변경할 수 없습니다.
dice-status-locked = locked
dice-status-kept = kept

# Dealing (card games)
game-deal-counter = 딜 { $current }/{ $total }.
game-you-deal = 카드를 나눠줍니다.
game-player-deals = { $player }님이 카드를 나눠줍니다.

# Card names
card-name = { $suit }의 { $rank }
no-cards = 카드 없음

# Colors (with gendered forms: m = masculine, f = feminine)
color-black = 검정
color-black-m = 검정
color-black-f = 검정
color-blue = 파랑
color-blue-m = 파랑
color-blue-f = 파랑
color-brown = 갈색
color-brown-m = 갈색
color-brown-f = 갈색
color-gray = 회색
color-gray-m = 회색
color-gray-f = 회색
color-green = 초록
color-green-m = 초록
color-green-f = 초록
color-indigo = 남색
color-indigo-m = 남색
color-indigo-f = 남색
color-orange = 주황
color-orange-m = 주황
color-orange-f = 주황
color-pink = 분홍
color-pink-m = 분홍
color-pink-f = 분홍
color-purple = 보라
color-purple-m = 보라
color-purple-f = 보라
color-red = 빨강
color-red-m = 빨강
color-red-f = 빨강
color-violet = 보라색
color-violet-m = 보라색
color-violet-f = 보라색
color-white = 하양
color-white-m = 하양
color-white-f = 하양
color-yellow = 노랑
color-yellow-m = 노랑
color-yellow-f = 노랑

# Suit names
suit-diamonds = 다이아몬드
suit-clubs = 클로버
suit-hearts = 하트
suit-spades = 스페이드

# Rank names
rank-ace = 에이스
rank-ace-plural = 에이스
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
rank-jack = 잭
rank-jack-plural = 잭
rank-queen = 퀸
rank-queen-plural = 퀸
rank-king = 킹
rank-king-plural = 킹

# Poker hand descriptions
poker-high-card-with = { $high } 하이, { $rest } 포함
poker-high-card = { $high } 하이
poker-pair-with = { $pair } 원페어, { $rest } 포함
poker-pair = { $pair } 원페어
poker-two-pair-with = 투페어, { $high }와 { $low }, { $kicker } 포함
poker-two-pair = 투페어, { $high }와 { $low }
poker-trips-with = 트리플, { $trips }, { $rest } 포함
poker-trips = 트리플, { $trips }
poker-straight-high = { $high } 하이 스트레이트
poker-flush-high-with = { $high } 하이 플러시, { $rest } 포함
poker-full-house = 풀하우스, { $trips } 오버 { $pair }
poker-quads-with = 포카드, { $quads }, { $kicker } 포함
poker-quads = 포카드, { $quads }
poker-straight-flush-high = { $high } 하이 스트레이트 플러시
poker-unknown-hand = 알 수 없는 핸드

# Validation errors (common across games)
game-error-invalid-team-mode = 선택한 팀 모드는 현재 플레이어 수에 유효하지 않습니다.
