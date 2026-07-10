# Monopoly Rules
PlayPalace team, 2026.

This guide describes PlayPalace's Monopoly implementation. Before the host starts a game, choose one of the supported rulesets:

* **US Classic** uses the familiar Atlantic City board and the standard two-dice rules.
* **UK Waddingtons Classic** follows the 1996 Waddingtons rules and London board, using pounds sterling.
* **UK Waddingtons Short Game** deals two deeds to each player, uses three houses before a hotel, and ends after the second bankruptcy.
* **UK Waddingtons Time Limit Game** deals two deeds, then awards the game to the richest player when the host-selected time expires (60 minutes by default).
* **US Speed Die** uses the US Classic board with Hasbro's Speed Die additions.

The classic rules are informed by Hasbro's official Monopoly Classic Game instructions: https://instructions.hasbro.com/en-my/instruction/monopoly-classic-game

## TL;DR
Monopoly is a property trading game for 2 to 8 players. Move around the board, buy unowned properties, collect rent from opponents, build houses and hotels on complete color sets, and try to stay solvent while everyone else goes bankrupt. The last non-bankrupt player wins.

The default US Classic settings follow the standard rules: each player starts with $1500, passing GO pays $200, Free Parking does nothing, and the bank has 32 houses and 12 hotels. The UK ruleset uses the equivalent £ values and London properties. The host can enable optional house rules before the game starts.

## Object
Become the wealthiest surviving player by buying, renting, trading, mortgaging, and improving properties. A player who cannot pay a debt after raising money must declare bankruptcy. When only one solvent player remains, that player wins.

## Setup
Each player begins on GO with the configured starting cash. The classic board has 40 spaces, including:

* 22 street properties in color groups.
* 4 railroads.
* 2 utilities.
* 3 Chance spaces.
* 3 Community Chest spaces.
* GO, Jail / Just Visiting, Free Parking, Go to Jail, Income Tax, and Luxury Tax.

The Chance and Community Chest decks are shuffled at the start. Get Out of Jail Free cards stay with the player who drew them until used or traded; other cards return to their deck after they resolve.

## Turn Flow
On your turn, roll two dice and move clockwise that many spaces. If you roll doubles, you usually get another roll after the landing is resolved. If you roll doubles three times on the same turn, you go directly to Jail.

After you land, the server resolves the space:

* If you land on an unowned property, choose whether to buy it or send it to auction.
* If you land on an opponent's unmortgaged property, pay rent.
* If you land on Chance or Community Chest, draw and resolve the card.
* If you land on a tax space, pay the bank.
* If you land on Go to Jail, move directly to Jail.

Most turns advance automatically after all required choices and payments are complete.

### Speed Die

In the US Speed Die ruleset, every player begins with $2500. A player starts using the third die after they first land on or pass GO. Before that point, they use only the two white dice.

* **1, 2, or 3:** add it to the white-dice total.
* **Bus:** choose the first white die, second white die, or their total as the movement.
* **Mr. Monopoly:** resolve the normal white-dice move, then advance to the next unowned property. If none remain, advance to the next property where rent is due.
* **Three of a kind:** move to any board space.

Only the white dice determine doubles and are used for Jail. Utility rent uses all three dice, treating Bus and Mr. Monopoly as zero.

## Buying And Auctions
When you land on an unowned property, you may buy it for its printed price. If you do not buy it, an auction starts. Every solvent player may bid or pass. Bids must meet the minimum bid and increase by at least $10. The highest remaining bidder pays the winning bid and receives the property. If everyone passes without bidding, the property remains unowned.

## Rent
Rent is due when you land on another player's unmortgaged property.

* Streets charge the rent shown for their current building level.
* An unimproved street in a complete color set charges double base rent.
* Railroads charge more rent as their owner holds more railroads.
* Utilities charge 4 times the dice roll if the owner has one utility, or 10 times the dice roll if the owner has both utilities.
* Chance cards that send you to a railroad or utility may apply their special rent multiplier.

Mortgaged properties do not collect rent.

## Houses And Hotels
You may build only on a complete, unmortgaged color set. Buildings must be kept even across the set: build on the lowest properties first, and sell from the highest properties first.

Each street can hold up to 4 houses. The next build replaces those 4 houses with a hotel. Houses and hotels are limited by the bank supply. Selling a building returns half its purchase price.

## Mortgages
You may mortgage an unimproved property to receive its mortgage value. Streets cannot be mortgaged while any property in their color group has houses or a hotel.

To unmortgage a property, pay the mortgage value plus 10% interest. If a mortgaged property changes hands through a trade or bankruptcy transfer, the new owner pays the mortgage transfer interest.

## Trading
Players may trade cash, properties, and Get Out of Jail Free cards. A trade can include multiple properties from either side. Properties with buildings, or properties in a color group that currently has buildings, cannot be traded until the buildings are sold.

The proposing player builds an offer, sends it, and the target player accepts or declines. Trades are validated again when accepted, so an offer can become invalid if cash, ownership, debt, or buildings change before acceptance.

## Jail
You can enter Jail by landing on Go to Jail, drawing a Go to Jail card, or rolling doubles three times in one turn.

While in Jail, you may:

* Pay $50 bail before rolling.
* Use a Get Out of Jail Free card.
* Roll for doubles.

If you roll doubles, you leave Jail and move by that roll. If you fail to roll doubles three times, you must pay $50 and then move by the third roll. If you cannot pay, the amount becomes a debt.

## Chance And Community Chest
Cards may move you, award or charge cash, send you to Jail, give a Get Out of Jail Free card, charge repair fees based on your buildings, or transfer money between players.

When a card moves you past GO, you collect $200 unless the card or destination says otherwise. Get Out of Jail Free cards can be used later or traded.

## Debt And Bankruptcy
If you owe more cash than you have, the debt stays pending while you raise money by mortgaging properties, selling buildings, or accepting valid trades. Once you have enough cash, pay the debt.

If you still cannot or do not pay, declare bankruptcy. If you owe another player, your remaining cash, properties, and Get Out of Jail Free cards transfer to that player. If you owe the bank, your properties return to the bank.

## Free Parking
By default, Free Parking is only a resting space and pays nothing.

The host may enable the Free Parking jackpot house rule before the game. With that option on, bank payments such as taxes, fees, and bail go into a pot. Landing on Free Parking collects the pot, then resets it to the configured seed amount.

## Options
The host can configure these settings before play:

* **Ruleset:** US Classic, UK Waddingtons Classic, UK Short Game, UK Time Limit Game, or US Speed Die. This choice is locked once play starts.
* **Time limit:** The Time Limit Game duration. Default: 60 minutes.

* **Starting cash:** Cash each player receives at setup. Default: $1500.
* **Free Parking jackpot:** Optional house rule. Default: off.
* **Free Parking starting pot:** The pot amount at game start and after each payout when the jackpot rule is enabled. Default: $0.

## Controls
Common Monopoly actions:

* **Roll dice:** Roll on your turn.
* **Buy property / Auction property:** Resolve an unowned property you landed on.
* **Mortgage / Unmortgage property:** Raise cash or restore a property.
* **Build house or hotel / Sell house or hotel:** Improve or liquidate a complete color set.
* **Pay bail / Use Get Out of Jail Free card:** Jail options available before rolling.
* **Pay debt / Declare bankruptcy:** Resolve a pending debt.
* **Offer trade:** Build a trade offer with another player.
* **Check assets:** Review your cash, location, net worth, cards, and properties.
* **Check board:** Review bank supply, unowned property count, player positions, and pending table state.

Keyboard shortcuts include R or Space to roll, B to buy, A to auction, E to end a visible manual turn phase, Ctrl+T to offer a trade, C to check assets, Shift+C to check the board, F1 to show rules, and Escape to open the action menu.
