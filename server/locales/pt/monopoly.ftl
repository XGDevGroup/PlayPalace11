# Monopoly game messages

game-name-monopoly = Monopoly

monopoly-started = Monopoly started on { $board }. Each player begins with { $cash }.
monopoly-turn = { $player }'s turn.
monopoly-in-jail-turn = { $player } is in jail. Failed roll attempts: { $turns }.

# Actions
monopoly-roll-dice = Roll dice
monopoly-buy-property = Buy property
monopoly-auction-property = Auction property
monopoly-end-turn = End turn
monopoly-auction-bid = Place auction bid
monopoly-auction-pass = Pass in auction
monopoly-mortgage-property = Mortgage property
monopoly-unmortgage-property = Unmortgage property
monopoly-build-house = Build house or hotel
monopoly-sell-house = Sell house or hotel
monopoly-pay-bail = Pay bail
monopoly-use-jail-card = Use Get Out of Jail Free card
monopoly-pay-debt = Pay debt
monopoly-declare-bankruptcy = Declare bankruptcy
monopoly-offer-trade = Offer trade
monopoly-submit-trade-amount = Set trade amount
monopoly-accept-trade = Accept trade
monopoly-decline-trade = Decline trade
monopoly-check-assets = Check assets
monopoly-check-board = Check board

# Prompts
monopoly-enter-auction-bid = Enter auction bid amount
monopoly-select-property-mortgage = Select a property to mortgage
monopoly-select-property-unmortgage = Select a property to unmortgage
monopoly-select-property-build = Select a property to build on
monopoly-select-property-sell = Select a property to sell from
monopoly-select-trade-offer = Select a trade offer
monopoly-enter-trade-cash = Enter the cash amount for this trade. For property swaps, use a positive amount if you pay the other player, a negative amount if they pay you, or 0.

# Validation
monopoly-player-bankrupt-disabled = You are bankrupt.
monopoly-auction-active = Resolve the active auction first.
monopoly-resolve-property-first = Resolve the pending property decision first.
monopoly-debt-pending = Resolve the pending debt first.
monopoly-roll-not-available = Rolling is not available right now.
monopoly-roll-first = Roll first.
monopoly-no-property-to-buy = There is no property to buy right now.
monopoly-no-property-to-auction = There is no property to auction right now.
monopoly-no-debt = There is no debt to pay.
monopoly-no-auction-active = There is no auction in progress.
monopoly-auction-already-passed = You have already passed in this auction.
monopoly-not-enough-cash = You do not have enough cash.
monopoly-not-in-jail = You are not in jail.
monopoly-no-jail-card = You do not have a Get Out of Jail Free card.
monopoly-no-mortgage-options = You do not have any properties available to mortgage.
monopoly-no-unmortgage-options = You do not have any properties available to unmortgage.
monopoly-no-build-options = You do not have any properties available to build on.
monopoly-no-sell-options = You do not have any buildings available to sell.
monopoly-no-trade-options = You do not have any valid trades to offer.
monopoly-trade-pending = Resolve the pending trade first.
monopoly-no-trade-pending = There is no trade pending for you.
monopoly-trade-no-longer-valid = That trade is no longer valid.
monopoly-invalid-trade-amount = That trade amount is not a valid number.
monopoly-invalid-bid = That bid is not a valid number.
monopoly-bid-out-of-range = Bid at least { $minimum } and no more than your cash ({ $cash }).

# Board events
monopoly-roll-result = { $player } rolled { $die1 } + { $die2 } = { $total }.
monopoly-landed = { $player } landed on { $space }.
monopoly-moved-to = { $player } moved to { $space }.
monopoly-pass-go = { $player } passed GO and collected { $amount }.
monopoly-collected = { $player } collected { $amount } for { $reason }.
monopoly-paid-bank = { $player } paid { $amount } to the bank for { $reason }.
monopoly-paid-player = { $player } paid { $amount } to { $target } for { $reason }.
monopoly-free-parking = { $player } is resting on Free Parking.
monopoly-just-visiting = { $player } is just visiting jail.
monopoly-go-to-jail = { $player } goes directly to jail.
monopoly-landed-own-property = { $player } landed on their own { $property }.

# Properties and rent
monopoly-property-available = { $property } is unowned and costs { $price }.
monopoly-property-bought = { $player } bought { $property } for { $price }.
monopoly-completed-set = { $player } completed the { $group } set.
monopoly-mortgaged-no-rent = { $player } landed on mortgaged { $property }; no rent is due.
monopoly-property-mortgaged = { $player } mortgaged { $property } for { $amount }.
monopoly-property-unmortgaged = { $player } unmortgaged { $property } for { $amount }.
monopoly-building-built = { $player } built a { $building } on { $property } for { $amount }. Level: { $level }.
monopoly-building-sold = { $player } sold a building on { $property } for { $amount }. Level: { $level }.

# Trades
monopoly-trade-offered = { $player } offered { $target } a trade: { $summary }.
monopoly-trade-accepted = { $target } accepted { $player }'s trade: { $summary }.
monopoly-trade-declined = { $target } declined { $player }'s trade: { $summary }.
monopoly-mortgage-transfer-interest-paid = { $player } paid { $amount } mortgage transfer interest.

# Auctions
monopoly-auction-started = Auction started for { $property }. Minimum bid: { $amount }.
monopoly-auction-bid-placed = { $player } bid { $amount } for { $property }.
monopoly-auction-pass-event = { $player } passed on { $property }.
monopoly-auction-no-bids = No bids for { $property }. It remains unsold.
monopoly-auction-won = { $player } won { $property } for { $amount }.

# Jail and doubles
monopoly-roll-again = { $player } rolled doubles and gets another roll.
monopoly-three-doubles-jail = { $player } rolled doubles three times and is sent to jail.
monopoly-jail-roll-doubles = { $player } rolled doubles ({ $die1 } and { $die2 }) and leaves jail.
monopoly-jail-roll-failed = { $player } rolled { $die1 } and { $die2 } in jail. Attempt { $attempts }.
monopoly-bail-paid = { $player } paid { $amount } bail.
monopoly-jail-card-used = { $player } used a Get Out of Jail Free card.

# Cards and debt
monopoly-card-drawn = { $player } drew { $deck }: { $text }
monopoly-debt-created = { $player } owes { $amount } to { $target } for { $reason }.
monopoly-debt-can-pay = { $player } has enough cash to pay the pending debt.
monopoly-player-bankrupt = { $player } is bankrupt. Creditor: { $creditor }.

# Ruleset and Speed Die options
monopoly-speed-die-choose-move = Choose Speed Die move
monopoly-speed-die-select-move = Select how to move with the Speed Die
monopoly-speed-die-roll-result = { $player } rolled { $die1 } + { $die2 } with Speed Die { $speed_die }.
monopoly-speed-die-bus = { $player } rolled the Bus. Choose one white die or their total.
monopoly-speed-die-three-of-a-kind = { $player } rolled three of a kind and may move anywhere on the board.
monopoly-option-ruleset = Ruleset: { $ruleset }
monopoly-option-select-ruleset = Select the Monopoly ruleset
monopoly-option-changed-ruleset = Ruleset changed to { $ruleset }.
monopoly-option-desc-ruleset = Choose US Classic, 1996 UK Waddingtons Classic, or US Speed Die before the game starts.
monopoly-ruleset-us-classic = US Classic
monopoly-ruleset-uk-classic = UK Waddingtons Classic
monopoly-ruleset-uk-short = UK Waddingtons Short Game
monopoly-ruleset-uk-time-limit = UK Waddingtons Time Limit Game
monopoly-option-time-limit = Time limit: { $minutes } minutes
monopoly-option-enter-time-limit = Enter the Time Limit Game duration in minutes
monopoly-option-changed-time-limit = Time limit set to { $minutes } minutes.
monopoly-option-desc-time-limit = The Time Limit Game ends after this many minutes; the richest player wins.
