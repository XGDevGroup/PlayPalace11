# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = 마일 바이 마일

# Game options
milebymile-set-distance = 레이스 거리: { $miles }마일
milebymile-enter-distance = 레이스 거리를 입력하세요 (300-3000)
milebymile-set-winning-score = 승리 점수: { $score }점
milebymile-enter-winning-score = 승리 점수를 입력하세요 (1000-10000)
milebymile-toggle-perfect-crossing = 정확한 피니시 요구: { $enabled }
milebymile-toggle-stacking = 공격 누적 허용: { $enabled }
milebymile-toggle-reshuffle = 버린 카드 더미 재섞기: { $enabled }
milebymile-toggle-karma = 카르마 규칙: { $enabled }
milebymile-set-rig = 덱 조작: { $rig }
milebymile-select-rig = 덱 조작 옵션을 선택하세요

# Option change announcements
milebymile-option-changed-distance = 레이스 거리가 { $miles }마일로 설정되었습니다.
milebymile-option-changed-winning = 승리 점수가 { $score }점으로 설정되었습니다.
milebymile-option-changed-crossing = 정확한 피니시 요구 { $enabled }.
milebymile-option-changed-stacking = 공격 누적 허용 { $enabled }.
milebymile-option-changed-reshuffle = 버린 카드 더미 재섞기 { $enabled }.
milebymile-option-changed-karma = 카르마 규칙 { $enabled }.
milebymile-option-changed-rig = 덱 조작이 { $rig }(으)로 설정되었습니다.

milebymile-toggle-always-discard = Always allow discarding: { $enabled }
milebymile-option-changed-always-discard = Always allow discarding { $enabled }.

# Status
milebymile-status = { $name }: { $points }점, { $miles }마일, 문제: { $problems }, 안전: { $safeties }

# Card actions
milebymile-no-matching-safety = 일치하는 안전 카드가 없습니다!
milebymile-cant-play = { $reason }(으)로 인해 { $card }을(를) 플레이할 수 없습니다.
milebymile-no-card-selected = 버릴 카드가 선택되지 않았습니다.
milebymile-no-valid-targets = 이 위험에 대한 유효한 목표가 없습니다!
milebymile-you-drew = 당신은 다음을 뽑았습니다: { $card }
milebymile-discards = { $player }이(가) 카드를 버립니다.
milebymile-select-target = 목표를 선택하세요

# Distance plays
milebymile-plays-distance-individual = { $player }이(가) { $distance }마일을 플레이하여, 현재 { $total }마일입니다.
milebymile-plays-distance-team = { $player }이(가) { $distance }마일을 플레이했습니다; 팀은 현재 { $total }마일입니다.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player }이(가) 완벽한 크로싱으로 여정을 완료했습니다!
milebymile-journey-complete-perfect-team = 팀 { $team }이(가) 완벽한 크로싱으로 여정을 완료했습니다!
milebymile-journey-complete-individual = { $player }이(가) 여정을 완료했습니다!
milebymile-journey-complete-team = 팀 { $team }이(가) 여정을 완료했습니다!

# Hazard plays
milebymile-plays-hazard-individual = { $player }이(가) { $target }에게 { $card }을(를) 플레이합니다.
milebymile-plays-hazard-team = { $player }이(가) 팀 { $team }에게 { $card }을(를) 플레이합니다.

# Remedy/Safety plays
milebymile-plays-card = { $player }이(가) { $card }을(를) 플레이합니다.
milebymile-plays-dirty-trick = { $player }이(가) { $card }을(를) 더러운 속임수로 플레이합니다!

# Deck
milebymile-deck-reshuffled = 버린 카드 더미가 덱에 섞였습니다.

# Race
milebymile-new-race = 새로운 레이스가 시작됩니다!
milebymile-race-complete = 레이스 완료! 점수 계산 중...
milebymile-earned-points = { $name }이(가) 이번 레이스에서 { $score }점을 획득했습니다: { $breakdown }.
milebymile-total-scores = 총점:
milebymile-team-score = { $name }: { $score }점

# Scoring breakdown
milebymile-from-distance = 이동 거리에서 { $miles }
milebymile-from-trip = 여정 완료에서 { $points }
milebymile-from-perfect = 완벽한 크로싱에서 { $points }
milebymile-from-safe = 안전한 여정에서 { $points }
milebymile-from-shutout = 완전 차단에서 { $points }
milebymile-from-safeties = { $count }개 안전에서 { $points }
milebymile-from-all-safeties = 모든 4개 안전에서 { $points }
milebymile-from-dirty-tricks = { $count }개 더러운 속임수에서 { $points }

# Game end
milebymile-wins-individual = { $player }이(가) 게임에서 승리했습니다!
milebymile-wins-team = 팀 { $team }이(가) 게임에서 승리했습니다! ({ $members })
milebymile-final-score = 최종 점수: { $score }점

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = 당신과 목표 모두 배척당했습니다! 공격이 무력화됩니다.
milebymile-karma-clash-you-attacker = 당신과 { $attacker } 모두 배척당했습니다! 공격이 무력화됩니다.
milebymile-karma-clash-others = { $attacker }와(과) { $target } 모두 배척당했습니다! 공격이 무력화됩니다.
milebymile-karma-clash-your-team = 당신의 팀과 목표 모두 배척당했습니다! 공격이 무력화됩니다.
milebymile-karma-clash-target-team = 당신과 팀 { $team } 모두 배척당했습니다! 공격이 무력화됩니다.
milebymile-karma-clash-other-teams = 팀 { $attacker }와(과) 팀 { $target} 모두 배척당했습니다! 공격이 무력화됩니다.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = 당신은 공격성으로 인해 배척당했습니다! 당신의 카르마가 사라졌습니다.
milebymile-karma-shunned-other = { $player }이(가) 공격성으로 인해 배척당했습니다!
milebymile-karma-shunned-your-team = 당신의 팀이 공격성으로 인해 배척당했습니다! 팀의 카르마가 사라졌습니다.
milebymile-karma-shunned-other-team = 팀 { $team }이(가) 공격성으로 인해 배척당했습니다!

# False Virtue
milebymile-false-virtue-you = 당신은 거짓 미덕을 플레이하여 카르마를 되찾았습니다!
milebymile-false-virtue-other = { $player }이(가) 거짓 미덕을 플레이하여 카르마를 되찾았습니다!
milebymile-false-virtue-your-team = 당신의 팀이 거짓 미덕을 플레이하여 카르마를 되찾았습니다!
milebymile-false-virtue-other-team = 팀 { $team}이(가) 거짓 미덕을 플레이하여 카르마를 되찾았습니다!

# Problems/Safeties (for status display)
milebymile-none = 없음

# Unplayable card reasons
milebymile-reason-not-on-team = 팀에 속하지 않았습니다
milebymile-reason-stopped = 정지 상태입니다
milebymile-reason-has-problem = 운전을 방해하는 문제가 있습니다
milebymile-reason-speed-limit = 속도 제한이 활성화되어 있습니다
milebymile-reason-exceeds-distance = { $miles }마일을 초과합니다
milebymile-reason-no-targets = 유효한 목표가 없습니다
milebymile-reason-no-speed-limit = 속도 제한을 받고 있지 않습니다
milebymile-reason-has-right-of-way = 통행권으로 신호등 없이 갈 수 있습니다
milebymile-reason-already-moving = 이미 이동 중입니다
milebymile-reason-must-fix-first = 먼저 { $problem }을(를) 수리해야 합니다
milebymile-reason-has-gas = 차에 연료가 있습니다
milebymile-reason-tires-fine = 타이어가 멀쩡합니다
milebymile-reason-no-accident = 차가 사고를 당하지 않았습니다
milebymile-reason-has-safety = 이미 그 안전 카드를 가지고 있습니다
milebymile-reason-has-karma = 아직 카르마가 있습니다
milebymile-reason-generic = 지금은 플레이할 수 없습니다

# Card names
milebymile-card-out-of-gas = 연료 부족
milebymile-card-flat-tire = 펑크 난 타이어
milebymile-card-accident = 사고
milebymile-card-speed-limit = 속도 제한
milebymile-card-stop = 정지
milebymile-card-gasoline = 휘발유
milebymile-card-spare-tire = 예비 타이어
milebymile-card-repairs = 수리
milebymile-card-end-of-limit = 제한 종료
milebymile-card-green-light = 녹색 신호
milebymile-card-extra-tank = 추가 탱크
milebymile-card-puncture-proof = 펑크 방지
milebymile-card-driving-ace = 운전의 달인
milebymile-card-right-of-way = 통행권
milebymile-card-false-virtue = 거짓 미덕
milebymile-card-miles = { $miles }마일

# Disabled action reasons
milebymile-no-dirty-trick-window = 활성화된 더러운 속임수 창이 없습니다.
milebymile-not-your-dirty-trick = 당신의 팀의 더러운 속임수 창이 아닙니다.
milebymile-between-races = 다음 레이스가 시작될 때까지 기다리세요.

# Validation errors
milebymile-error-karma-needs-three-teams = 카르마 규칙은 최소 3개의 구별되는 차량/팀이 필요합니다.

milebymile-you-play-safety-with-effect = 당신이 { $card } 카드를 냅니다. { $effect }
milebymile-player-plays-safety-with-effect = { $player } 님이 { $card } 카드를 냅니다. { $effect }
milebymile-you-play-dirty-trick-with-effect = 당신이 { $card } 카드를 더티 트릭으로 냅니다. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } 님이 { $card } 카드를 더티 트릭으로 냅니다. { $effect }
milebymile-safety-effect-extra-tank = 이제 연료 부족으로부터 보호됩니다.
milebymile-safety-effect-puncture-proof = 이제 펑크로부터 보호됩니다.
milebymile-safety-effect-driving-ace = 이제 사고로부터 보호됩니다.
milebymile-safety-effect-right-of-way = 이제 정지와 속도 제한으로부터 보호됩니다.
