# Mile by Mile game messages
# Note: Common messages like round-start, turn-start, team-mode are in games.ftl

# Game name
game-name-milebymile = Mile by Mile

# Game options
milebymile-set-distance = Race distance: { $miles } miles
milebymile-desc-round-distance = Target distance for each race
milebymile-enter-distance = Enter race distance (300-3000)
milebymile-option-changed-distance = Race distance set to { $miles } miles.

milebymile-set-winning-score = Winning score: { $score } points
milebymile-desc-winning-score = Total points needed to win the game
milebymile-enter-winning-score = Enter winning score (1000-10000)
milebymile-option-changed-winning = Winning score set to { $score } points.

milebymile-toggle-perfect-crossing = Require exact finish: { $enabled }
milebymile-desc-perfect-crossing = Prevent playing distance cards that would exceed the race target
milebymile-option-changed-crossing = Require exact finish { $enabled }.

milebymile-toggle-stacking = Allow stacking attacks: { $enabled }
milebymile-desc-stacking = Allow multiple hazard cards to be played on the same team
milebymile-option-changed-stacking = Allow stacking attacks { $enabled }.

milebymile-toggle-reshuffle = Reshuffle discard pile: { $enabled }
milebymile-desc-reshuffle = When the deck runs out, reshuffle the discard pile to continue. If disabled, the race ends when no one has playable cards.
milebymile-option-changed-reshuffle = Reshuffle discard pile { $enabled }.

milebymile-toggle-karma = Karma rule: { $enabled }
milebymile-desc-karma = Teams start with karma protection and lose it when attacking. False Virtue cards can restore karma.
milebymile-option-changed-karma = Karma rule { $enabled }.

milebymile-set-rig = Deck rigging: { $rig }
milebymile-desc-rig = Modify deck composition and hand rules
milebymile-select-rig = Select deck rigging option
milebymile-option-changed-rig = Deck rigging set to { $rig }.

milebymile-desc-always-discard = When enabled, press backspace on a card to discard it even if it could be played.

# Status
milebymile-status = { $name }: { $points } points, { $miles } miles, Problems: { $problems }, Safeties: { $safeties }

# Card actions
milebymile-no-matching-safety = You don't have the matching safety card!
milebymile-cant-play = You can't play { $card } because { $reason }.
milebymile-no-card-selected = No card selected to discard.
milebymile-cant-discard-playable = You can't discard a card that can be played.
milebymile-discard-confirm = Do you want to discard this card?
milebymile-no-valid-targets = No valid targets for this hazard!
milebymile-you-drew = You drew: { $card }
milebymile-discards = { $player } discards a card.
milebymile-select-target = Select a target

# Distance plays
milebymile-plays-distance-individual = { $player } plays { $distance } miles, and is now at { $total } miles.
milebymile-plays-distance-team = { $player } plays { $distance } miles; their team is now at { $total } miles.

# Journey complete
milebymile-journey-complete-perfect-individual = { $player } has completed the journey with a perfect crossing!
milebymile-journey-complete-perfect-team = Team { $team } has completed the journey with a perfect crossing!
milebymile-journey-complete-individual = { $player } has completed the journey!
milebymile-journey-complete-team = Team { $team } has completed the journey!

# Hazard plays
milebymile-plays-hazard-individual = { $player } plays { $card } on { $target }.
milebymile-plays-hazard-team = { $player } plays { $card } on Team { $team }.

# Remedy/Safety plays
milebymile-plays-card = { $player } plays { $card }.
milebymile-plays-dirty-trick = { $player } plays { $card } as a Dirty Trick!

# Deck
milebymile-deck-reshuffled = Discard pile shuffled back into deck.

# Race
milebymile-new-race = New race begins!
milebymile-race-complete = Race complete! Calculating scores...
milebymile-earned-points = { $name } earned { $score } points this race: { $breakdown }.
milebymile-total-scores = Total scores:
milebymile-team-score = { $name }: { $score } points

# Scoring breakdown
milebymile-from-distance = { $miles } from distance travelled
milebymile-from-trip = { $points } from completing the trip
milebymile-from-perfect = { $points } from a perfect crossing
milebymile-from-safe = { $points } from a safe trip
milebymile-from-shutout = { $points } from a shut out
milebymile-from-safeties = { $points } from { $count } { $safeties ->
    [one] safety
    *[other] safeties
}
milebymile-from-all-safeties = { $points } from all 4 safeties
milebymile-from-dirty-tricks = { $points } from { $count } { $tricks ->
    [one] dirty trick
    *[other] dirty tricks
}

# Game end
milebymile-wins-individual = { $player } wins the game!
milebymile-wins-team = Team { $team } wins the game! ({ $members })
milebymile-final-score = Final score: { $score } points

# Karma messages - clash (both lose karma)
milebymile-karma-clash-you-target = You and your target are both shunned! The attack is neutralized.
milebymile-karma-clash-you-attacker = You and { $attacker } are both shunned! The attack is neutralized.
milebymile-karma-clash-others = { $attacker } and { $target } are both shunned! The attack is neutralized.
milebymile-karma-clash-your-team = Your team and your target are both shunned! The attack is neutralized.
milebymile-karma-clash-target-team = You and Team { $team } are both shunned! The attack is neutralized.
milebymile-karma-clash-other-teams = Team { $attacker } and Team { $target } are both shunned! The attack is neutralized.

# Karma messages - attacker shunned
milebymile-karma-shunned-you = You have been shunned for your aggression! Your karma is lost.
milebymile-karma-shunned-other = { $player } has been shunned for their aggression!
milebymile-karma-shunned-your-team = Your team has been shunned for its aggression! Your team's karma is lost.
milebymile-karma-shunned-other-team = Team { $team } has been shunned for its aggression!

# False Virtue
milebymile-false-virtue-you = You play False Virtue and regain your karma!
milebymile-false-virtue-other = { $player } plays False Virtue and regains their karma!
milebymile-false-virtue-your-team = Your team plays False Virtue and regains its karma!
milebymile-false-virtue-other-team = Team { $team } plays False Virtue and regains its karma!

# Problems/Safeties (for status display)
milebymile-none = none

# Unplayable card reasons
milebymile-reason-not-on-team = you're not on a team
milebymile-reason-stopped = you're stopped
milebymile-reason-has-problem = you have a problem that prevents driving
milebymile-reason-speed-limit = the speed limit is active
milebymile-reason-exceeds-distance = it would exceed { $miles } miles
milebymile-reason-no-targets = there are no valid targets
milebymile-reason-no-speed-limit = you're not under a speed limit
milebymile-reason-has-right-of-way = Right of Way lets you go without green lights
milebymile-reason-already-moving = you're already moving
milebymile-reason-must-fix-first = you must fix the { $problem } first
milebymile-reason-has-gas = your car has gas
milebymile-reason-tires-fine = your tires are fine
milebymile-reason-no-accident = your car hasn't been in an accident
milebymile-reason-has-safety = you already have that safety
milebymile-reason-has-karma = you still have your karma
milebymile-reason-generic = it can't be played right now

# Card names
milebymile-card-out-of-gas = Out of Gas
milebymile-card-flat-tire = Flat Tire
milebymile-card-accident = Accident
milebymile-card-speed-limit = Speed Limit
milebymile-card-stop = Stop
milebymile-card-gasoline = Gasoline
milebymile-card-spare-tire = Spare Tire
milebymile-card-repairs = Repairs
milebymile-card-end-of-limit = End of Limit
milebymile-card-green-light = Green Light
milebymile-card-extra-tank = Extra Tank
milebymile-card-puncture-proof = Puncture Proof
milebymile-card-driving-ace = Driving Ace
milebymile-card-right-of-way = Right of Way
milebymile-card-false-virtue = False Virtue
milebymile-card-miles = { $miles } miles

# Disabled action reasons
milebymile-no-dirty-trick-window = No dirty trick window is active.
milebymile-not-your-dirty-trick = It's not your team's dirty trick window.
milebymile-between-races = Wait for the next race to start.

# Validation errors
milebymile-error-karma-needs-three-teams = Karma rule requires at least 3 distinct cars/teams.

milebymile-you-play-safety-with-effect = You play { $card }. { $effect }
milebymile-player-plays-safety-with-effect = { $player } plays { $card }. { $effect }
milebymile-you-play-dirty-trick-with-effect = You play { $card } as a Dirty Trick. { $effect }
milebymile-player-plays-dirty-trick-with-effect = { $player } plays { $card } as a Dirty Trick. { $effect }
milebymile-safety-effect-extra-tank = Now protected from Out of Gas.
milebymile-safety-effect-puncture-proof = Now protected from Flat Tire.
milebymile-safety-effect-driving-ace = Now protected from Accident.
milebymile-safety-effect-right-of-way = Now protected from Stop and Speed Limit.
