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
monopoly-trade-give = Choose properties to give
monopoly-trade-request = Choose properties to request
monopoly-trade-cash = Set cash in this trade
monopoly-trade-jail = Include a Get Out of Jail Free card
monopoly-trade-review = Review this trade
monopoly-trade-send = Send trade offer
monopoly-trade-cancel = Cancel trade
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
monopoly-select-trade-partner = Select a player to trade with
monopoly-select-trade-give = Choose one of your properties to add to or remove from the offer
monopoly-select-trade-request = Choose one of their properties to add to or remove from the offer
monopoly-select-trade-jail = Choose a Get Out of Jail Free card to include or remove
monopoly-enter-trade-cash = Enter the cash for this trade: a positive amount if you pay the other player, a negative amount if they pay you, or 0.

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
monopoly-free-parking-jackpot = { $player } landed on Free Parking and scooped the { $amount } jackpot!
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
monopoly-trade-building = Building a trade with { $target }. Add properties, cash, and cards, then send the offer.
monopoly-trade-cancelled = Trade offer cancelled.
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
monopoly-winner = { $player } wins Monopoly with net worth { $value }.

# House-rule options (lobby settings; defaults reproduce the official ruleset)
monopoly-option-starting-cash = Starting cash: ${ $cash }
monopoly-option-enter-starting-cash = Enter the starting cash each player receives
monopoly-option-changed-starting-cash = Starting cash set to ${ $cash }.
monopoly-option-desc-starting-cash = How much money each player begins with. The official rule is 1500.
monopoly-option-free-parking-jackpot = Free Parking jackpot: { $enabled }
monopoly-option-changed-free-parking-jackpot = Free Parking jackpot turned { $enabled }.
monopoly-option-desc-free-parking-jackpot = House rule: taxes, fees, and bail paid to the bank pile into a pot that a player wins by landing on Free Parking. Off by default for official rules.
monopoly-option-free-parking-seed = Free Parking starting pot: ${ $cash }
monopoly-option-enter-free-parking-seed = Enter the amount the Free Parking pot starts and resets to
monopoly-option-changed-free-parking-seed = Free Parking starting pot set to ${ $cash }.
monopoly-option-desc-free-parking-seed = The amount the pot holds at the start and resets to after a player collects it. Default 0.
