# Rules Of Phase 10
PlayPalace team, 2026.

## TL;DR
Phase 10 is a card game for 2 to 6 players, designed by Kenneth Johnson and published by Fundex Games. It is one of the best-selling card games in the United States.

Each player works through ten phases in order, from Phase 1 to Phase 10. A phase is a specific combination of cards — such as two sets of three, or a run of seven — that you must assemble in your hand and lay down on the table. Each hand, players race to go out (empty their hand) by drawing, laying down their phase, and discarding. Only players who successfully laid down their phase this hand advance to the next phase. The first player to complete Phase 10 wins.

## The Cards
The deck contains 108 cards:

* **Numbered cards:** 1 through 12, in four colors (Red, Blue, Green, Yellow). Two copies of each combination, for 96 numbered cards total.
* **Wild cards:** 8 Wilds. A Wild can stand in for any numbered card in any phase group.
* **Skip cards:** 4 Skips. A Skip has no numeric value and cannot be used in a phase group. When discarded, you must immediately choose a player to skip — their next turn is forfeited. Skip cards cannot be taken from the discard pile.

## Card Values (Penalty Points)
At the end of each hand, players who did not go out score penalty points for every card remaining in their hand. Lower scores are better.

* Numbered cards 1–9: **5 points each**
* Numbered cards 10–12: **10 points each**
* Skip cards: **15 points each**
* Wild cards: **25 points each**

## The Phases
There are ten phases. Each player must complete them in order, one per hand.

* **Phase 1:** 2 sets of 3
* **Phase 2:** 1 set of 3 + 1 run of 4
* **Phase 3:** 1 set of 4 + 1 run of 4
* **Phase 4:** 1 run of 7
* **Phase 5:** 1 run of 8
* **Phase 6:** 1 run of 9
* **Phase 7:** 2 sets of 4
* **Phase 8:** 7 cards of one color
* **Phase 9:** 1 set of 5 + 1 set of 2
* **Phase 10:** 1 set of 4 + 1 set of 3

### Sets
A set is a group of cards all sharing the same number. For example, three 7s (of any colors) form a set of 3. Wilds may substitute for any card in a set.

### Runs
A run is a group of cards with consecutive numbers, for example 3-4-5-6-7. Colors do not matter in a run. Wilds may substitute for any missing number in a run. A run cannot wrap around (12 is not followed by 1).

### Color Groups
A color group is a group of cards all sharing the same color, regardless of number. Wilds may substitute for any card in a color group, but at least one natural (non-Wild) card of the target color is required to establish the color.

## Gameplay

### Setup
Each player is dealt 10 cards at the start of every hand. The remaining cards form the draw pile. The top card of the draw pile is turned face up to start the discard pile. If the starting card is a Skip, the first player's turn is automatically skipped.

All players start on Phase 1. A player advances to the next phase only if they successfully laid down their phase during the hand that just ended.

### Turn Structure
On your turn you must do three things in order:

1. **Draw** one card, either from the top of the draw pile or the top of the discard pile. You cannot take a Skip from the discard pile.
2. **Optionally lay down your phase** (if you have not already done so this hand) and/or **hit** cards onto laid-down groups on the table.
3. **Discard** one card to end your turn.

### Laying Down a Phase
Once you have the cards to satisfy your current phase, you may lay it down during step 2 of your turn. Laying down is a multi-step process:

1. Press N (or select "Lay down Phase" from the menu) to enter lay-down mode.
2. Navigate to cards in your hand and press Enter to toggle them in or out of the current group. You can press "Check requirement" at any time to hear the requirement for the group you are currently building.
3. When you have selected enough cards for the current group, press F or Enter on "Confirm group" to lock that group in. You then move on to the next group.
4. Once all groups are confirmed, the phase is laid down to the table and the cards leave your hand.
5. Press Escape at any time to cancel the entire lay-down (your hand is returned unchanged).

Each group requires at least one natural (non-Wild) card. You may use Wilds to fill any remaining slots.

### Hitting
After laying down your own phase (not before), you may hit additional cards onto any group already on the table, including your own. A hit card must be a valid extension of that group:

* **Set:** The card must match the set's number. Any color is fine.
* **Run:** The card must extend the run at either end. You cannot insert cards into the interior of a run. Wilds extend at either end (you will be asked which end when hitting a Wild onto a run).
* **Color group:** The card must match the color of the group.

The primary way to hit is to navigate to the card in your hand and press Enter. If your phase is already laid down and groups are on the table, this immediately enters hit mode with that card ready, and the turn menu switches to showing available groups to hit onto. Alternatively, press H to enter hit mode first and then navigate to select a card — useful if you want to browse the groups before committing to a card.

### Discarding
After drawing and taking any optional actions, you must discard exactly one card to end your turn. Navigate to the card you want to discard and press J — whichever card is currently focused in your hand menu is used directly. No prior selection step is needed.

If you were in hit mode and cancelled with Escape, the card you had selected for hitting remains marked, and pressing J will discard that card.

When you discard a Skip card, you must immediately choose a player to skip (the skip-target menu appears automatically). You cannot skip yourself. Each player can only be skipped once per round (once per full rotation around the table).

### Going Out
A player goes out when they have no cards left in their hand after discarding. This ends the hand immediately.

Going out requires that you have already laid down your phase. It is possible to lay down your phase and hit all remaining cards onto the table in the same turn, ending with no cards to discard — but you must still make at least one discard to go out, so plan accordingly.

### End of Hand Scoring
When someone goes out, the hand ends. Each player who did not go out counts up penalty points for every card remaining in their hand. Wilds are especially costly (25 points each), so discard them as soon as possible if you are not close to laying down.

Players who successfully laid down their phase this hand advance to the next phase. Players who did not lay down their phase stay on the same phase.

### Winning
The first player to complete Phase 10 (or whichever phase is set as the winning phase in the options) wins. If multiple players complete the winning phase in the same hand, the player among them with the lowest penalty point total wins. If there is a tie on penalty points as well, those players replay the final phase until the tie is broken.

## Customizable Options
The host can configure the following settings before the game starts:

* **Winning Phase:** The phase number a player must complete to win. Defaults to 10. Can be set from 1 to 10. Setting it to a lower number makes for a shorter game.
* **Even Phases Only:** When enabled, players work through only the even-numbered phases (2, 4, 6, 8, 10) instead of all ten. Useful for a shorter game with a different character — the even phases tend to be longer runs and larger groups.
* **Fixed Hands Mode:** When enabled, the game always runs for exactly 10 hands regardless of whether anyone has completed the winning phase. Phases are still awarded normally, but the game ends after hand 10. The player on the highest phase (with lowest score as tiebreaker) wins.
* **Turn Timer:** A time limit for each turn. Defaults to no limit. Options range from 5 seconds to 90 seconds. If a player's timer expires, their turn is forfeited.

## Keyboard Shortcuts
Shortcuts specific to Phase 10:

* **Space:** Draw from the deck.
* **Shift+D:** Draw from the discard pile.
* **N:** Lay down your phase (opens lay-down mode).
* **Enter (on a group):** Confirm the selected hit group (after entering hit mode via a card).
* **F:** Confirm the current group during lay-down.
* **Escape:** Cancel lay-down mode or cancel a hit in progress.
* **Enter (on a hand card):** If your phase is laid down and groups are on the table, immediately enters hit mode with that card. In lay-down mode, toggles the card in or out of the current group.
* **H:** Enter hit mode without pre-selecting a card (browse groups first, then select a card).
* **J:** Discard the currently focused hand card.
* **D:** Read the top card of the discard pile.
* **C:** Read all groups currently on the table.
* **P:** Check your current phase and all players' phase status.
* **E:** Read card counts for all players and the draw pile.
* **Shift+C:** Sort your hand by color.
* **Shift+H:** Sort your hand by number (ascending; press again for descending).
* **S:** Check scores.
* **Shift+T:** Check the turn timer.

## Strategy Tips
* **Hold Wilds for your phase, not for hitting.** Wilds are worth 25 penalty points if you get caught with them. Use them to complete your phase as quickly as possible. Only hold onto Wilds if you are close to laying down and they are the key to completing your phase.
* **Draw from the discard pile when it gives you a phase card.** The discard pile shows only the top card, so you always know exactly what you are getting. If it completes or advances your phase, take it. If not, draw from the deck.
* **Track other players' phases.** Press P at any time to hear which phase each player is on. If someone is close to completing Phase 10, you may want to skip them rather than a player who is far behind.
* **Skip players who are close to going out.** A well-timed Skip can prevent an opponent from going out this hand, giving you extra turns to lay down your own phase and minimize your penalty.
* **Lay down early, even if your phase is incomplete.** Wait — you cannot lay down a partial phase. But if you have your phase and can lay it down this turn, do it immediately: it lets you start hitting off cards rather than holding them in hand.
* **Hit aggressively once you are laid down.** Every card you hit onto the table is a card that costs you nothing if someone goes out. Even low-value cards (5 points) add up fast over many hands.
* **Sort your hand.** Use Shift+C (by color) or Shift+H (by number) to reorder your hand so you can quickly navigate to the cards you need during lay-down.
* **Long runs (Phases 4–6) need planning.** You need 7, 8, or 9 consecutive numbers. Start collecting early. Wilds are your best friend here — they can fill a single gap anywhere in the sequence.
* **Phase 8 (7 of one color) is often the hardest.** Color is not evenly distributed in draws; you may need to discard useful numbered cards to focus on a single color. Once you identify your target color early in a hand, commit to it and discard off-color cards.
* **Managing penalty points matters.** The lowest score among tied players wins. Even in a hand where you cannot lay down, discarding your Wilds and Skips early keeps your penalty low.
