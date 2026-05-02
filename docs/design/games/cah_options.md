I have a plan for cards against humanity for expanding the options. It is divided into 3 parts.
The descriptions given here for the options should also be the description string for the option itself.

Status note, May 2026: Parts 1, 2, and 5 are not implemented yet. Part 3 is partially complete: multiple-judge grammar and the multiple-judge race condition are fixed. Part 4 is partially complete: number of judges supports 1 to max players, and judging method supports Independent, Jury, and Random with single-judge rounds enforced as Independent. The remaining cardzar behavior settings are still planned.


# Part 1: multiple submissions
Status: Not implemented.

On the player class replace player.submitted_cards with a list called current_submissions.
Refactor the game to allow players to enter multiple submissions in one turn.
Whenever a player enters a submission, append it to the "current_submissions" list.
Clear the list after each turn.
The hard coded number of 10 submission slots for judging also needs to be dynamic, not fixed. Since later on players will be able to add extra submissions or omit them.

## new options:

below card pack selection
submissions required per turn (int): 1 to 3
The number of submissions each player must enter each turn.
default 1

# Part 2: extra and absent submissions tracking
Status: Not implemented.

Before adding judge settings, implement the extra and absent submission features so the tracking infrastructure can be tested independently.

On the player class add "total_extra_submissions" and "total_abscent_submissions" both = 0.
Use the length of player.current_submissions for determining the extra / abscent submissions counts for the last turn.

def get_submission_counts(player):
	extra_submission_count = 0
	abscent_submission_count = 0
	if len(player.current_submissions) > options.submissions_required:
		extra_submission_count = len(player.current_submissions) - options.submissions_required
		player.total_extra_submissions += extra_submission_count
	elif len(player.current_submissions) < options.submissions_required:
		abscent_submission_count = options.submissions_required - len(player.current_submissions)
		player.total_abscent_submissions += abscent_submission_count
	return extra_submission_count, abscent_submission_count

# Part 3: bug fixes and refactors
These should be done before introducing new judge settings, since the new settings replace the old ones.

## Bug: multiple judge grammar
Status: Complete.

When listing the judges with the j and t keys, the grammar is incorrect. For example with 3 judges it would say, "John and James, Jack are the judges". Instead of the word "and" being put before the last judge.

## Bug: multiple judges race condition
Status: Complete.

Currently when there are multiple judges, the winning card is chosen by whichever judge selects a submission first. The other judges do not get to judge. This needs to be fixed so all judges participate.

## Refactor: migrate number of judges
Status: Partially complete. The existing option now supports 1 to max players, but it has not moved into a new judging behavior subgroup.

The existing number of judges setting is migrated into the new judging behavior subgroup (Part 4). Saved option profiles referencing the old setting should still work.

## Refactor: remove cardzar selection setting
Status: Not implemented.

The existing cardzar selection setting is removed altogether and replaced by the new chain-of-appointment subgroup (Part 5).

# Part 4: cardzar behavior settings
Status: Partially implemented. Number of judges and judging method are present. Timer, judge submission, self-pick controls, and min/max picked submission settings are not implemented yet.

Note: For all instances of "enforce x when y = z", enforce the value. These are meant to be locked values. Leave them visible so the user can still see the locked values.

below required submissions
Cardzar behavior settings (child group)
Submenu for controlling judging behaviors

number of judges (int): 1 to max players
Status: Complete.
The number of people who are allowed to judge each turn.
default 1

Timer limit for judging (string):
Status: Not implemented.
Determines how much time (in seconds) a judge has for picking submissions before submissions are randomly selected.
Use existing turn limit code from crazy eights game server/games/crazyeights/game.py.
Default is unlimited

Timer behavior in jury mode: The timer applies per-judge. If a judge times out, one of the already-voted submissions is selected on their behalf. If ALL judges time out without voting, a random submission is chosen.

Allow judges to submit cards (bool):
Status: Not implemented. Current behavior only lets judges submit when all players are judges.
Determines if judges are allowed to submit their own cards for a chance at winning the round.
Enforce true if number of judges = max players.
default false

Allow judges to pick their own submissions (bool):
Status: Not implemented. Current behavior blocks self-picks.
Determines if judges are allowed to select their own or another judge's submissions as a winner. This is an all-or-nothing setting that applies the same way in both independent and jury modes.
Enforce false if allow judges to submit cards = false.
default false

Judging method (string):
Status: Complete for Independent, Jury, Random, and single-judge Independent enforcement.
Determines how winning submissions are chosen by judges.
Enforce independent if number of judges = 1.
Default independent

Independent = each judge chooses their own winning submissions, allowing for a wider range of point distribution.
Jury = all judges must agree on the winning submissions, making the game more fair and intense. Jury mode is also the voting system referenced by the popularity-based judge selection in Part 5.
Random = each turn any judging method can be chosen, allowing for chaotic scoring.

number of required minimum picked submissions (int): 1 to (total submissions received that round - 1)
Status: Not implemented.
The fewest number of submissions each judge must pick.
default 1

number of allowed maximum picked submissions (int): 1 to (total submissions received that round - 1)
Status: Not implemented.
The greatest number of submissions each judge must pick.
default 1

# Part 5: cardzar selection
Status: Not implemented. Current code still uses the existing Card Czar selection option.

This part focuses on expanding how the next cardzars are chosen. Certain actions throughout the last round or game can influence who will be the next to judge. This adds an element of forced control and balance to the game.
Currently multiple judges is handled by whatever the cardzar selection setting is for the first judge, followed by random selection for the remaining judges.

new options:

below judge behavior settings
Cardzars selection settings (child group)
Submenu for configuring how the judges for the next turn should be chosen.
Hidden if number of judges = max players (no selection needed when everyone judges).

Prioritize popularity (string):
Use the popularity of submissions from the last round to determine the first judge seats of the next round.
Popularity is measured by last-round score: players can score higher in a single round through multiple winning submissions or multiple votes (in jury mode).
Ignore = Do not take popularity into account.
Biggest winners only = Only the people with the highest last-round score will have a seat.
Biggest losers only = Only the people with the lowest last-round score will have a seat.
Descending popularity = From highest to lowest last-round score, judges will fill seats. This will only work with jury mode (the voting system), otherwise only the biggest winners will be chosen.
Ascending popularity = From lowest to highest last-round score, judges will fill seats. This will only work with jury mode (the voting system), otherwise only the biggest losers will be chosen.

Prioritize extra submissions  (string):
For players that entered extra submissions they will be punished by filling any available seats after popularity is taken into account. All options go in descending order, meaning highest number is punished the most.
Ignore = Do not take extra submissions into account.
Last turn = in descending order of extra submissions this turn, all relevant players who entered extra submissions in the last turn will be selected.
total uses = in descending order of total extra submissions, all relevant players who entered extra submissions during the entire game will be selected.
Last turn and total uses = Take both into account, with last turn being evaluated first since it is a more immediate action.

Last turn and total uses example: this would be the order of priority.
total uses uses include the last turn. So when someone enters extra submissions for a turn, their total uses increases by (submissions -1).
*Person a with 3 submissions last turn and 2 extra submissions in total.
*Person b with 2 submissions last turn and 4 extra submissions in total.
*Person c with 2 submissions last turn and 2 extra submissions in total.
*Person d with 1 submissions last turn and 6 extra submissions in total.

Prioritize abscent submissions actions (string):
For players that chose not to submit anything they will be punished by filling any available seats after extra submissions is taken into account. All options go in descending order, meaning highest number is punished the most.
Ignore = Do not take abscent submissions into account.
Last turn = in descending order of abscent submissions uses this turn, all relevant players who used abscent submissions in the last turn will be selected.
total uses = in descending order of total abscent submissions uses, all relevant players who used abscent submissions during the entire game will be selected.
Last turn and total uses = Take both into account, with last turn being evaluated first since it is a more immediate action.

Last turn and total uses example: this would be the order of priority.
total uses uses include the last turn. So when someone uses abscent submissions for a turn, their total uses increases by 1.
*Person a with 0 submissions last turn and 3 abscent submissions in total.
*Person b with 0 submissions last turn and 1 abscent submissions in total.
*Person c with 1 submissions last turn and 6 abscent submissions in total.
*Person d with 1 submissions last turn and 2 abscent submissions in total.

Rotate judge seats in order (bool):
Determines who will fill the remaining seats if any are available. This is used as a last resort. If checked, players will rotate according to the turn order; if not they will be randomized.

Order Execution:
Picking the next cardzars should work like a looping chain. If people have the same popularity status such as biggest loser, evaluate extra submissions next on those losers. If some of them have the same stats based on the selected extra submission criteria, then evaluate abscent submissions. If some players still have the same relevant abscent submissions stats, use the last resort rotating / random to determine the choices.
If there are more seats after all losers are chosen, evaluate all remaining players and work down the chain as before, starting with extra submissions.
If all players who have met the extra submission criteria have been selected and there are more judge seats available, start again for remaining players with abscent submissions.
If there are still available seats after filtering out abscent submissions, the rest will be handled by rotating / random only.
It is very unlikely that the table host will enable all criterias, so the chain should not get this deep. But in case it does, I want the execution to be clear.
Be smart about when to chain to avoid extra work. For example if there are 5 judge seats and only 4 losers, automatically select all 4 losers without chaining since all losers will need to be selected. Then fill the last remaining seat with the remaining criterias.

# Ignore presets since the game options system does not support them.
cardzar presets:

minimal:
number of judges = 1
judging method = independent
min picks = 1
max picks = 1

democratic:
number of judges = maximum players
judging method = independent
min picks = 1
max picks = 1

Collective:
number of judges = maximum players
judging method = jury
min picks = 1
max picks = 1
