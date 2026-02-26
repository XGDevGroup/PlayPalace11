# 21 (Survival Rules)

## Status

Implemented in `server/games/twentyone.py`.

## Overview

- Type: card game
- Players: 2
- Mode: head-to-head HP battle
- Base target: `21` (can be changed by target change cards)
- Damage: loser of a round takes damage equal to their current bet

## Round Flow

1. Both players receive 2 number cards.
2. First dealt card is hidden (private), second dealt card is face-up (public).
3. Turn actions:
- `hit`: draw a number card
- `play_modifier`: play one change card from hand
- `stand`: mark as standing
4. Change-card selection menu options are one-based (`1`, `2`, `3`, ...).
5. Turn does not pass on `hit` or `play_modifier`.
6. Turn passes only when the current player chooses `stand`.
7. Round resolves only after both players stand consecutively.
- Any non-stand card action between stands resets pending stands.
8. Round winner is decided by closest to target with bust rules.

## Visibility Rules

- Hidden:
- Each player's first dealt card (hole card)
- All change cards in hand
- Public:
- Each player's second dealt card
- Number cards drawn after the initial deal
- Active table effects
- Private readouts are available for hand/change-card details.

## Deck Rules

- There is no discard pile.
- If a change card removes a face-up card from a hand, that card is placed on top of the deck.
- This applies to both opponent and self removals where relevant.

## Bets And Damage

- Bet starts from `base_bet` and is modified by active table effects.
- `raise` effects increase incoming damage to the opponent.
- `defend` effects reduce incoming damage to the player.
- At round settle, the loser takes damage equal to their computed current bet.

## Change Card Summary

### Bet/Defense Effects

- `raise one`: Opponent damage +1; gain 1 change card.
- `raise two`: Opponent damage +2; gain 1 change card.
- `withdraw and raise two`: Opponent damage +2; return opponent last card to top of deck; gain 1 change card.
- `defend`: Reduce incoming damage by 1.
- `defend enhanced`: Reduce incoming damage by 2.
- `best draw and raise five`: Best draw and increase opponent damage by 5.

### Numbered Draw Effects

- `draw 2`, `draw 3`, `draw 4`, `draw 5`, `draw 6`, `draw 7`: draw that number if available.

### Card/Effect Control

- `withdraw`: Return opponent last card to top of deck.
- `undraw`: Return your own last card to top of deck.
- `swap top cards`: Exchange your last card with the opponent's last card.
- `delete`: Destroy opponent newest change card effect.
- `delete enhanced`: Destroy all opponent change card effects.
- `delete double enhanced`: Clear opponent change card effects and prevent opponent playing change cards.

### Change Card Economy

- `change-up`: Discard 2 change cards; gain 3 change cards.
- `change-up enhanced`: Discard 1 change card; gain 4 change cards.
- `embrace change`: Whenever any change card is played, gain 1 change card.
- `best draw with change`: Best draw and gain 2 change cards.

### Target Control

- `target 17`: Set round target to 17.
- `target 24`: Set round target to 24.
- `target 27`: Set round target to 27.
- A target change card matching the current target value is not playable.

### Opponent Assistance

- `trojan horse`: Opponent draws their best available card for the current target.

## Bot Behavior Notes

- Bot evaluation uses visible opponent cards plus a hidden-card estimate.
- Bot does not replay a target change card that would keep the same target value.

## Audio Cues (Current)

- Stand uses separate cues for acting player and opponent.
- Change-card menu opening has its own cue.
- A round-resolve transition cue plays when both players stand and the round settles.
- Winner/no-winner end-game branches have distinct cues.
- Target reminder cues can play at turn start when target is not `21`.
- Target-proximity cue plays only for the acting player, and only on exact target total.
- Invalid/unavailable action-input cases play a fail cue.

## Keybinds

- `1`: Hit
- `2`: Stand
- `3`: Play change card
- `4`: Check 21 status
- `M`: Change card guide
- `O`: Read opponent face-up cards
- `R`: Read current hand
- `B`: Read current bets
- `E`: Read active change-card effects

Note:
- Global/common table keybinds from base systems still apply.

## Test Coverage

Covered by `server/tests/test_twentyone.py`, including:

- Hidden/public card visibility rules
- Turn and stand-resolution behavior
- Change card visibility and playability
- Keybind mappings and readout actions
- Top-of-deck return behavior for removed face-up cards
- Target-card playability guard for already-active target value
- Target-proximity cue only on exact target total for the acting player
- Bot play with save/reload round-trip
