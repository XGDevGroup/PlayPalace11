# Monopoly game messages

# Game info
game-name-monopoly = Monopoly

# Lobby options
monopoly-set-preset = Preset: { $preset }
monopoly-select-preset = Select a Monopoly preset
monopoly-option-changed-preset = Preset set to { $preset }.

# Preset labels
monopoly-preset-classic-standard = Classic and Themed Standard
monopoly-preset-junior = Monopoly Junior
monopoly-preset-junior-modern = Monopoly Junior (Modern)
monopoly-preset-junior-legacy = Monopoly Junior (Legacy)
monopoly-preset-cheaters = Monopoly Cheaters Edition
monopoly-preset-electronic-banking = Electronic Banking
monopoly-preset-voice-banking = Voice Banking
monopoly-preset-sore-losers = Monopoly for Sore Losers
monopoly-preset-speed = Monopoly Speed
monopoly-preset-builder = Monopoly Builder
monopoly-preset-city = Monopoly City
monopoly-preset-bid-card-game = Monopoly Bid
monopoly-preset-deal-card-game = Monopoly Deal
monopoly-preset-knockout = Monopoly Knockout
monopoly-preset-free-parking-jackpot = Free Parking Jackpot

# Scaffold status
monopoly-announce-preset = Announce current preset
monopoly-current-preset = Current preset: { $preset } ({ $count } editions).
monopoly-scaffold-started = Monopoly scaffold started with { $preset } ({ $count } editions).

# Turn actions
monopoly-roll-dice = Roll dice
monopoly-buy-property = Buy property
monopoly-banking-balance = Check bank balance
monopoly-banking-transfer = Transfer funds
monopoly-banking-ledger = Review bank ledger
monopoly-voice-command = Voice command
monopoly-cheaters-claim-reward = Claim cheat reward
monopoly-end-turn = End turn

# Turn validation
monopoly-roll-first = You need to roll first.
monopoly-already-rolled = You already rolled this turn.
monopoly-no-property-to-buy = There is no property to buy right now.
monopoly-property-owned = That property is already owned.
monopoly-not-enough-cash = You do not have enough money to do this.
monopoly-action-disabled-for-preset = This action is disabled for the selected preset.
monopoly-buy-disabled = Buying property directly is disabled for this preset.

# Turn events
monopoly-pass-go = { $player } passed GO and collected { $amount }.
monopoly-roll-result = { $player } rolled { $die1 } + { $die2 } = { $total } and landed on { $space }.
monopoly-roll-only = { $player } rolled { $die1 } + { $die2 } = { $total }.
monopoly-you-roll-result = You rolled { $die1 } + { $die2 } = { $total } and landed on { $space }.
monopoly-player-roll-result = { $player } rolled { $die1 } + { $die2 } = { $total } and landed on { $space }.
monopoly-you-roll-only = You rolled { $die1 } + { $die2 } = { $total }.
monopoly-player-roll-only = { $player } rolled { $die1 } + { $die2 } = { $total }.
monopoly-you-roll-only-doubles = You rolled { $die1 } + { $die2 } = { $total }. Doubles!
monopoly-player-roll-only-doubles = { $player } rolled { $die1 } + { $die2 } = { $total }. Doubles!
monopoly-property-available = It's available for { $price }.
monopoly-property-bought = { $player } bought { $property } for { $price }.
monopoly-you-property-bought = You bought { $property } for { $price }.
monopoly-player-property-bought = { $player } bought { $property } for { $price }.
monopoly-rent-paid = { $player } paid { $amount } in rent to { $owner } for { $property }. { $detail }
monopoly-you-rent-paid = You paid { $amount } in rent to { $owner } for { $property }. { $detail }
monopoly-player-rent-paid = { $player } paid { $amount } in rent to { $owner } for { $property }. { $detail }
monopoly-player-paid-you-rent = { $player } paid { $amount } in rent to you for { $property }. { $detail }
monopoly-player-paid-player = { $player } paid { $amount } to { $target }.
monopoly-you-paid-player = You paid { $amount } to { $target }.
monopoly-player-paid-you = { $player } paid { $amount } to you.
monopoly-you-completed-color-set = You now own all of the { $group } properties.
monopoly-player-completed-color-set = { $player } now owns all of the { $group } properties.
monopoly-you-completed-railroads = You now own all of the railroads.
monopoly-player-completed-railroads = { $player } now owns all of the railroads.
monopoly-you-completed-utilities = You now own all of the utilities.
monopoly-player-completed-utilities = { $player } now owns all of the utilities.
monopoly-landed-owned = { $player } owns it.
monopoly-you-landed-owned = You own it.
monopoly-player-landed-owned = { $player } owns it.
monopoly-tax-paid = { $player } paid { $amount } for { $tax }.
monopoly-you-tax-paid = You paid { $amount } for { $tax }.
monopoly-player-tax-paid = { $player } paid { $amount } for { $tax }.
monopoly-go-to-jail = { $player } goes to jail (moved to { $space }).
monopoly-you-go-to-jail = You go to jail (moved to { $space }).
monopoly-player-go-to-jail = { $player } goes to jail (moved to { $space }).
monopoly-bankrupt-player = You are bankrupt and out of the game.
monopoly-player-bankrupt = { $player } is bankrupt. Creditor: { $creditor }.
monopoly-winner-by-bankruptcy = { $player } wins by bankruptcy with total asset value { $cash }.
monopoly-winner-by-cash = { $player } wins with the highest cash total: { $cash }.
monopoly-city-winner-by-value = { $player } wins Monopoly City with final value { $total }.

# Additional actions
monopoly-auction-property = Auction property
monopoly-auction-property-space = Auction { $property }
monopoly-auction-bid = Place auction bid
monopoly-auction-bid-custom-option = Enter bid amount
monopoly-auction-pass = Pass in auction
monopoly-mortgage-property = Mortgage property
monopoly-unmortgage-property = Unmortgage property
monopoly-build-house = Build house or hotel
monopoly-sell-house = Sell house or hotel
monopoly-offer-trade = Offer trade
monopoly-accept-trade = Accept trade
monopoly-decline-trade = Decline trade
monopoly-read-cash = Read cash
monopoly-pay-bail = Pay bail
monopoly-use-jail-card = Use get-out-of-jail card
monopoly-cash-report = { $cash } in cash.
monopoly-property-amount-option = { $property } for { $amount }
monopoly-banking-transfer-option = Transfer { $amount } to { $target }

# Additional prompts
monopoly-select-property-mortgage = Select a property to mortgage
monopoly-select-property-unmortgage = Select a property to unmortgage
monopoly-enter-auction-bid = Enter auction bid amount
monopoly-select-property-build = Select a property to build on
monopoly-select-property-sell = Select a property to sell from
monopoly-select-trade-offer = Select a trade offer
monopoly-select-auction-bid = Select your auction bid
monopoly-select-banking-transfer = Select a transfer
monopoly-select-voice-command = Enter a voice command beginning with voice:

# Additional validation
monopoly-no-property-to-auction = There is no property to auction right now.
monopoly-auction-active = Resolve the active auction first.
monopoly-no-auction-active = There is no auction in progress.
monopoly-not-your-auction-turn = It is not your turn in the auction.
monopoly-no-mortgage-options = You do not have properties available to mortgage.
monopoly-no-unmortgage-options = You do not have mortgaged properties to unmortgage.
monopoly-no-build-options = You do not have properties available to build on.
monopoly-no-sell-options = You do not have properties with buildings available to sell.
monopoly-no-trade-options = You do not have any valid trades to offer right now.
monopoly-no-trade-pending = There is no pending trade for you.
monopoly-trade-pending = A trade is already pending.
monopoly-trade-no-longer-valid = That trade is no longer valid.
monopoly-not-in-jail = You are not in jail.
monopoly-no-jail-card = You do not have a get-out-of-jail card.
monopoly-roll-again-required = You rolled doubles and must roll again.
monopoly-resolve-property-first = Resolve the pending property decision first.

# Additional turn events
monopoly-roll-again = { $player } rolled doubles and gets another roll.
monopoly-you-roll-again = You rolled doubles and get another roll.
monopoly-player-roll-again = { $player } rolled doubles and gets another roll.
monopoly-you-pass-go = You passed GO and collected { $amount }.
monopoly-player-pass-go = { $player } passed GO and collected { $amount }.
monopoly-jail-roll-doubles = { $player } rolled doubles ({ $die1 } and { $die2 }) and leaves jail.
monopoly-you-jail-roll-doubles = You rolled doubles ({ $die1 } and { $die2 }) and leave jail.
monopoly-player-jail-roll-doubles = { $player } rolled doubles ({ $die1 } and { $die2 }) and leaves jail.
monopoly-jail-roll-failed = { $player } rolled { $die1 } and { $die2 } in jail (attempt { $attempts }).
monopoly-bail-paid = { $player } paid { $amount } bail.
monopoly-you-bail-paid = You paid { $amount } bail.
monopoly-player-bail-paid = { $player } paid { $amount } bail.
monopoly-three-doubles-jail = { $player } rolled three doubles in one turn and is sent to jail.
monopoly-you-three-doubles-jail = You rolled three doubles in one turn and are sent to jail.
monopoly-player-three-doubles-jail = { $player } rolled three doubles in one turn and is sent to jail.
monopoly-jail-card-used = { $player } used a get-out-of-jail card.
monopoly-you-jail-card-used = You used a get-out-of-jail card.
monopoly-player-jail-card-used = { $player } used a get-out-of-jail card.
monopoly-sore-loser-rebate = { $player } received a sore loser rebate of { $amount }.
monopoly-cheaters-early-end-turn-blocked = { $player } tried to end the turn early and paid a cheating penalty of { $amount }.
monopoly-cheaters-payment-avoidance-blocked = { $player } triggered a cheaters payment penalty of { $amount }.
monopoly-cheaters-reward-granted = { $player } claimed a cheaters reward of { $amount }.
monopoly-cheaters-reward-unavailable = { $player } already claimed the cheaters reward this turn.

# Auctions and mortgages
monopoly-auction-no-bids = No bids for { $property }. It remains unsold.
monopoly-auction-started = Auction started for { $property } (opening bid: { $amount }).
monopoly-auction-turn = Auction turn: { $player } to act on { $property } (current bid: { $amount }).
monopoly-you-auction-turn = Your turn to act.
monopoly-player-auction-turn = { $player }'s turn to act.
monopoly-auction-bid-placed = { $player } bid { $amount } for { $property }.
monopoly-you-auction-bid-placed = You bid { $amount } for { $property }.
monopoly-player-auction-bid-placed = { $player } bid { $amount } for { $property }.
monopoly-auction-pass-event = { $player } passed on { $property }.
monopoly-auction-won = { $player } won the auction for { $property } at { $amount }.
monopoly-you-auction-pass-event = You passed on { $property }.
monopoly-player-auction-pass-event = { $player } passed on { $property }.
monopoly-you-auction-won = You won the auction for { $property } at { $amount }.
monopoly-player-auction-won = { $player } won the auction for { $property } at { $amount }.
monopoly-property-mortgaged = { $player } mortgaged { $property } for { $amount }.
monopoly-property-unmortgaged = { $player } unmortgaged { $property } for { $amount }.
monopoly-house-built-house = { $player } built a house on { $property } for { $amount }. It now has { $level }.
monopoly-house-built-hotel = { $player } built a hotel on { $property } for { $amount }.
monopoly-house-sold = { $player } sold a building on { $property } for { $amount } (level: { $level }).
monopoly-you-property-mortgaged = You mortgaged { $property } for { $amount }.
monopoly-player-property-mortgaged = { $player } mortgaged { $property } for { $amount }.
monopoly-you-property-unmortgaged = You unmortgaged { $property } for { $amount }.
monopoly-player-property-unmortgaged = { $player } unmortgaged { $property } for { $amount }.
monopoly-you-house-built-house = You built a house on { $property } for { $amount }. It now has { $level }.
monopoly-player-house-built-house = { $player } built a house on { $property } for { $amount }. It now has { $level }.
monopoly-you-house-built-hotel = You built a hotel on { $property } for { $amount }.
monopoly-player-house-built-hotel = { $player } built a hotel on { $property } for { $amount }.
monopoly-you-house-sold = You sold a building on { $property } for { $amount } (level: { $level }).
monopoly-player-house-sold = { $player } sold a building on { $property } for { $amount } (level: { $level }).
monopoly-trade-offered = { $proposer } offered { $target } a trade: { $offer }.
monopoly-trade-completed = Trade completed between { $proposer } and { $target }: { $offer }.
monopoly-trade-declined = { $target } declined trade from { $proposer }: { $offer }.
monopoly-trade-cancelled = Trade cancelled: { $offer }.
monopoly-free-parking-jackpot = { $player } collected the Free Parking jackpot of { $amount }.
monopoly-mortgaged-no-rent = { $player } landed on mortgaged { $property }; no rent is due.
monopoly-builder-blocks-awarded = { $player } gained { $amount } builder blocks ({ $blocks } total).
monopoly-builder-block-spent = { $player } spent a builder block ({ $blocks } remaining).
monopoly-banking-transfer-success = { $from_player } transferred { $amount } to { $to_player }.
monopoly-banking-transfer-failed = { $player } bank transfer failed ({ $reason }).
monopoly-you-banking-transfer-success = You transferred { $amount } to { $to_player }.
monopoly-player-banking-transfer-success = { $from_player } transferred { $amount } to { $to_player }.
monopoly-player-banking-transferred-to-you = { $from_player } transferred { $amount } to you.
monopoly-you-banking-transfer-failed = Your bank transfer failed ({ $reason }).
monopoly-player-banking-transfer-failed = { $player } bank transfer failed ({ $reason }).
monopoly-banking-balance-report = { $player } bank balance: { $cash }.
monopoly-banking-ledger-report = Recent banking activity: { $entries }.
monopoly-banking-ledger-empty = No banking transactions yet.
monopoly-voice-command-error = Voice command error: { $reason }.
monopoly-voice-command-accepted = Voice command accepted: { $intent }.
monopoly-voice-command-repeat = Repeating last banking response code: { $response }.
monopoly-voice-transfer-staged = Voice transfer staged: { $amount } to { $target }. Say voice: confirm transfer.
monopoly-mortgage-transfer-interest-paid = { $player } paid { $amount } in mortgage transfer interest.

# Card engine
monopoly-card-drawn = { $player } drew a { $deck } card: { $card }.
monopoly-card-collect = { $player } collected { $amount }.
monopoly-card-pay = { $player } paid { $amount }.
monopoly-you-card-collect = You collected { $amount }.
monopoly-player-card-collect = { $player } collected { $amount }.
monopoly-you-card-pay = You paid { $amount }.
monopoly-player-card-pay = { $player } paid { $amount }.
monopoly-card-move = { $player } moved to { $space }.
monopoly-you-card-move = You moved to { $space }.
monopoly-player-card-move = { $player } moved to { $space }.
monopoly-card-jail-free = { $player } received a get-out-of-jail card.
monopoly-card-utility-roll = { $player } rolled { $die1 } + { $die2 } = { $total } for utility rent.
monopoly-utility-rent-detail = { $multiplier } times roll of { $roll }.
monopoly-space-with-houses = With { $count } houses.
monopoly-space-with-hotel = With a hotel.
monopoly-deck-chance = Chance
monopoly-deck-community-chest = Community Chest

# Card descriptions
monopoly-card-advance-to-go = Advance to GO and collect { $amount }
monopoly-card-advance-to-illinois-avenue = Advance to Illinois Avenue
monopoly-card-advance-to-st-charles-place = Advance to St. Charles Place
monopoly-card-advance-to-nearest-utility = Advance to the nearest Utility
monopoly-card-advance-to-nearest-railroad = Advance to the nearest Railroad and pay double rent if owned
monopoly-card-bank-dividend-50 = Bank pays you dividend of { $amount }
monopoly-card-go-back-three = Go back 3 spaces
monopoly-card-go-to-jail = Go directly to jail
monopoly-card-general-repairs = Make general repairs on all your property: { $per_house } per house, { $per_hotel } per hotel
monopoly-card-poor-tax-15 = Pay poor tax of { $amount }
monopoly-card-reading-railroad = Take a trip to Reading Railroad
monopoly-card-boardwalk = Take a walk on Boardwalk
monopoly-card-chairman-of-the-board = Chairman of the Board, pay { $amount } to every player
monopoly-card-building-loan-matures = Your building loan matures, collect { $amount }
monopoly-card-crossword-competition = You won a crossword competition, collect { $amount }
monopoly-card-bank-error-200 = Bank error in your favor, collect { $amount }
monopoly-card-doctor-fee-50 = Doctor's fee, pay { $amount }
monopoly-card-sale-of-stock-50 = From sale of stock you get { $amount }
monopoly-card-holiday-fund = Holiday fund matures, receive { $amount }
monopoly-card-tax-refund-20 = Income tax refund, collect { $amount }
monopoly-card-birthday = It is your birthday, collect { $amount } from every player
monopoly-card-life-insurance = Life insurance matures, collect { $amount }
monopoly-card-hospital-fees-100 = Pay hospital fees of { $amount }
monopoly-card-school-fees-50 = Pay school fees of { $amount }
monopoly-card-consultancy-fee-25 = Receive { $amount } consultancy fee
monopoly-card-street-repairs = You are assessed for street repairs: { $per_house } per house, { $per_hotel } per hotel
monopoly-card-beauty-contest-10 = You have won second prize in a beauty contest, collect { $amount }
monopoly-card-inherit-100 = You inherit { $amount }
monopoly-card-get-out-of-jail = Get out of jail free

# Board profile options
monopoly-set-board = Board: { $board }
monopoly-select-board = Select a Monopoly board
monopoly-option-changed-board = Board set to { $board }.
monopoly-set-board-rules-mode = Board rules mode: { $mode }
monopoly-select-board-rules-mode = Select board rules mode
monopoly-option-changed-board-rules-mode = Board rules mode set to { $mode }.

# Board labels
monopoly-board-classic-default = Classic Default
monopoly-board-mario-collectors = Super Mario Bros. Collector's Edition
monopoly-board-mario-kart = Monopoly Gamer Mario Kart
monopoly-board-mario-celebration = Super Mario Celebration
monopoly-board-mario-movie = Super Mario Bros. Movie Edition
monopoly-board-junior-super-mario = Junior Super Mario Edition
monopoly-board-disney-princesses = Disney Princesses
monopoly-board-disney-animation = Disney Animation
monopoly-board-disney-lion-king = Disney Lion King
monopoly-board-disney-mickey-friends = Disney Mickey and Friends
monopoly-board-disney-villains = Disney Villains
monopoly-board-disney-lightyear = Disney Lightyear
monopoly-board-marvel-80-years = Marvel 80 Years
monopoly-board-marvel-avengers = Marvel Avengers
monopoly-board-marvel-spider-man = Marvel Spider-Man
monopoly-board-marvel-black-panther-wf = Marvel Black Panther Wakanda Forever
monopoly-board-marvel-super-villains = Marvel Super Villains
monopoly-board-marvel-deadpool = Marvel Deadpool
monopoly-board-star-wars-40th = Star Wars 40th
monopoly-board-star-wars-boba-fett = Star Wars Boba Fett
monopoly-board-star-wars-light-side = Star Wars Light Side
monopoly-board-star-wars-the-child = Star Wars The Child
monopoly-board-star-wars-mandalorian = Star Wars The Mandalorian
monopoly-board-star-wars-complete-saga = Star Wars Complete Saga
monopoly-board-harry-potter = Harry Potter
monopoly-board-fortnite = Fortnite
monopoly-board-stranger-things = Stranger Things
monopoly-board-jurassic-park = Jurassic Park
monopoly-board-lord-of-the-rings = Lord of the Rings
monopoly-board-animal-crossing = Animal Crossing
monopoly-board-barbie = Barbie
monopoly-board-disney-star-wars-dark-side = Disney Star Wars Dark Side
monopoly-board-disney-legacy = Disney Legacy Edition
monopoly-board-disney-the-edition = Disney The Edition
monopoly-board-lord-of-the-rings-trilogy = Lord of the Rings Trilogy
monopoly-board-star-wars-saga = Star Wars Saga
monopoly-board-marvel-avengers-legacy = Marvel Avengers Legacy
monopoly-board-star-wars-legacy = Star Wars Legacy
monopoly-board-star-wars-classic-edition = Star Wars Classic Edition
monopoly-board-star-wars-solo = Star Wars Solo
monopoly-board-game-of-thrones = Game of Thrones
monopoly-board-deadpool-collectors = Deadpool Collector's Edition
monopoly-board-toy-story = Toy Story
monopoly-board-black-panther = Black Panther
monopoly-board-stranger-things-collectors = Stranger Things Collector's Edition
monopoly-board-ghostbusters = Ghostbusters
monopoly-board-marvel-eternals = Marvel Eternals
monopoly-board-transformers = Transformers
monopoly-board-stranger-things-netflix = Stranger Things Netflix Edition
monopoly-board-fortnite-collectors = Fortnite Collector's Edition
monopoly-board-star-wars-mandalorian-s2 = Star Wars Mandalorian Season 2
monopoly-board-transformers-beast-wars = Transformers Beast Wars
monopoly-board-marvel-falcon-winter-soldier = Marvel Falcon and Winter Soldier
monopoly-board-fortnite-flip = Fortnite Flip Edition
monopoly-board-marvel-flip = Marvel Flip Edition
monopoly-board-pokemon = Pokemon Edition

# Board rules mode labels
monopoly-board-rules-mode-auto = Auto
monopoly-board-rules-mode-skin-only = Skin only

# Board runtime announcements
monopoly-board-preset-autofixed = Board { $board } is incompatible with { $from_preset }; switched to { $to_preset }.
monopoly-board-rules-simplified = Board rules for { $board } are partially implemented; base preset behavior is used for missing mechanics.
monopoly-board-active = Active board: { $board } (mode: { $mode }).

# Deed and ownership browsing
monopoly-view-active-deed = View active deed
monopoly-view-active-deed-space = View { $property }
monopoly-browse-all-deeds = Browse all deeds
monopoly-view-my-properties = View my properties
monopoly-view-player-properties = View player info
monopoly-view-selected-deed = View selected deed
monopoly-view-selected-owner-property-deed = View selected player deed
monopoly-select-property-deed = Select a property deed
monopoly-select-player-properties = Select a player
monopoly-select-player-property-deed = Select a player property deed
monopoly-no-active-deed = There is no active deed to view right now.
monopoly-no-deeds-available = No deed-capable properties are available on this board.
monopoly-no-owned-properties = No owned properties are available for this view.
monopoly-no-players-with-properties = No players are available.
monopoly-buy-for = Buy for { $amount }
monopoly-you-have-no-owned-properties = You do not own any properties.
monopoly-player-has-no-owned-properties = { $player } does not own any properties.
monopoly-owner-bank = Bank
monopoly-owner-unknown = Unknown
monopoly-building-status-hotel = with hotel
monopoly-building-status-one-house = with 1 house
monopoly-building-status-houses = with { $count } houses
monopoly-mortgaged-short = mortgaged
monopoly-deed-menu-label = { $property } ({ $owner })
monopoly-deed-menu-label-extra = { $property } ({ $owner }; { $extras })
monopoly-color-brown = Brown
monopoly-color-light_blue = Light Blue
monopoly-color-pink = Pink
monopoly-color-orange = Orange
monopoly-color-red = Red
monopoly-color-yellow = Yellow
monopoly-color-green = Green
monopoly-color-dark_blue = Dark Blue
monopoly-deed-type-color-group = Type: { $color } color group
monopoly-deed-type-railroad = Type: Railroad
monopoly-deed-type-utility = Type: Utility
monopoly-deed-type-generic = Type: { $kind }
monopoly-deed-purchase-price = Purchase price: { $amount }
monopoly-deed-rent = Rent: { $amount }
monopoly-deed-full-set-rent = If owner has full color set: { $amount }
monopoly-deed-rent-one-house = With 1 house: { $amount }
monopoly-deed-rent-houses = With { $count } houses: { $amount }
monopoly-deed-rent-hotel = With hotel: { $amount }
monopoly-deed-house-cost = House cost: { $amount }
monopoly-deed-railroad-rent = Rent with { $count } railroads: { $amount }
monopoly-deed-utility-one-owned = If one utility is owned: 4x dice roll
monopoly-deed-utility-both-owned = If both utilities are owned: 10x dice roll
monopoly-deed-utility-base-rent = Utility base rent (legacy fallback): { $amount }
monopoly-deed-mortgage-value = Mortgage value: { $amount }
monopoly-deed-unmortgage-cost = Unmortgage cost: { $amount }
monopoly-deed-owner = Owner: { $owner }
monopoly-deed-current-buildings = Current buildings: { $buildings }
monopoly-deed-status-mortgaged = Status: Mortgaged
monopoly-player-properties-label = { $player }, on { $space }, square { $position }
monopoly-player-properties-label-no-space = { $player }, square { $position }
monopoly-banking-ledger-entry-success = { $tx_id } { $kind } { $from_id }->{ $to_id } { $amount } ({ $reason })
monopoly-banking-ledger-entry-failed = { $tx_id } { $kind } failed ({ $reason })

# Trade menu summaries
monopoly-trade-buy-property-summary = Buy { $property } from { $target } for { $amount }
monopoly-trade-offer-cash-for-property-summary = Offer { $amount } to { $target } for { $property }
monopoly-trade-sell-property-summary = Sell { $property } to { $target } for { $amount }
monopoly-trade-offer-property-for-cash-summary = Offer { $property } to { $target } for { $amount }
monopoly-trade-swap-summary = Swap { $give_property } with { $target } for { $receive_property }
monopoly-trade-swap-plus-cash-summary = Swap { $give_property } + { $amount } with { $target } for { $receive_property }
monopoly-trade-swap-receive-cash-summary = Swap { $give_property } for { $receive_property } + { $amount } from { $target }
monopoly-trade-buy-jail-card-summary = Buy jail card from { $target } for { $amount }
monopoly-trade-sell-jail-card-summary = Sell jail card to { $target } for { $amount }

# Board space names
monopoly-space-go = GO
monopoly-space-mediterranean_avenue = Mediterranean Avenue
monopoly-space-community_chest_1 = Community Chest
monopoly-space-baltic_avenue = Baltic Avenue
monopoly-space-income_tax = Income Tax
monopoly-space-reading_railroad = Reading Railroad
monopoly-space-oriental_avenue = Oriental Avenue
monopoly-space-chance_1 = Chance
monopoly-space-vermont_avenue = Vermont Avenue
monopoly-space-connecticut_avenue = Connecticut Avenue
monopoly-space-jail = Jail / Just Visiting
monopoly-space-st_charles_place = St. Charles Place
monopoly-space-electric_company = Electric Company
monopoly-space-states_avenue = States Avenue
monopoly-space-virginia_avenue = Virginia Avenue
monopoly-space-pennsylvania_railroad = Pennsylvania Railroad
monopoly-space-st_james_place = St. James Place
monopoly-space-community_chest_2 = Community Chest
monopoly-space-tennessee_avenue = Tennessee Avenue
monopoly-space-new_york_avenue = New York Avenue
monopoly-space-free_parking = Free Parking
monopoly-space-kentucky_avenue = Kentucky Avenue
monopoly-space-chance_2 = Chance
monopoly-space-indiana_avenue = Indiana Avenue
monopoly-space-illinois_avenue = Illinois Avenue
monopoly-space-bo_railroad = B. & O. Railroad
monopoly-space-atlantic_avenue = Atlantic Avenue
monopoly-space-ventnor_avenue = Ventnor Avenue
monopoly-space-water_works = Water Works
monopoly-space-marvin_gardens = Marvin Gardens
monopoly-space-go_to_jail = Go to Jail
monopoly-space-pacific_avenue = Pacific Avenue
monopoly-space-north_carolina_avenue = North Carolina Avenue
monopoly-space-community_chest_3 = Community Chest
monopoly-space-pennsylvania_avenue = Pennsylvania Avenue
monopoly-space-short_line = Short Line
monopoly-space-chance_3 = Chance
monopoly-space-park_place = Park Place
monopoly-space-luxury_tax = Luxury Tax
monopoly-space-boardwalk = Boardwalk

# Jurassic Park Edition space names
monopoly-space-control_room = Control Room
monopoly-space-maintenance_shed = Maintenance Shed
monopoly-space-security_breach = Security Breach
monopoly-space-kitchen_attack = Kitchen Attack
monopoly-space-park_road_1 = Park Road
monopoly-space-park_road_2 = Park Road
monopoly-space-park_road_3 = Park Road
monopoly-space-park_road_4 = Park Road

# Jurassic Park Edition deck names
monopoly-jp-deck-impact-tremor = Impact Tremor
monopoly-jp-deck-cold-storage = Cold Storage

# Jurassic Park Edition property types
monopoly-jp-type-dino-paddock = Dino Paddock
monopoly-jp-type-park-road = Park Road
monopoly-jp-type-utility = Utility

# Jurassic Park Edition card descriptions
monopoly-jp-card-advance-to-go = Advance to GO. Activate the gate.
monopoly-jp-card-trex-moves-again = The T. Rex is on the move! Roll the amber die and move the T. Rex again.
monopoly-jp-card-activate-gate = Activate the Jurassic Park gate! Collect $200 or $100 depending on the sound.

# Jurassic Park Edition turn flow
monopoly-jp-repair-phase = You may repair damaged properties and build fences before rolling.
monopoly-jp-roll-prompt = Roll both dice. The amber die moves the T. Rex; both dice move your token.

# T. Rex messages
monopoly-jp-trex-moves = The T. Rex moves { $spaces } spaces to { $space }.
monopoly-jp-trex-passes-you = The T. Rex passed your token! You pay ${ $amount } to the Bank.
monopoly-jp-trex-lands-on-you = The T. Rex landed on your space! You pay ${ $amount } to the Bank.
monopoly-jp-trex-passes-player = The T. Rex passed { $player }! { $player } pays ${ $amount } to the Bank.
monopoly-jp-trex-lands-on-player = The T. Rex landed on { $player }'s space! { $player } pays ${ $amount } to the Bank.
monopoly-jp-trex-in-jail-safe = The T. Rex passed your space, but you are safe in Jail.
monopoly-jp-trex-damages-property = The T. Rex damages { $property }! It is now facedown and cannot collect rent.
monopoly-jp-trex-damages-unowned = The T. Rex damages unowned { $property }! It can still be bought, but the new owner must repair it first.
monopoly-jp-trex-destroys-fence = The T. Rex destroys the fence on { $property }! The paddock itself is safe, for now.
monopoly-jp-trex-blocked-by-set = The T. Rex lands on { $property }, but the complete { $group } set protects it!
monopoly-jp-trex-already-damaged = The T. Rex lands on { $property }, but it is already damaged. Nothing happens.
monopoly-jp-trex-no-property = The T. Rex lands on { $space }. No property is affected.
monopoly-jp-trex-position = The T. Rex is on { $space }.

# Electronic gate (GO) messages
monopoly-jp-gate-theme-you = You activate the gate and hear the Jurassic Park theme! Collect ${ $amount }.
monopoly-jp-gate-roar-you = You activate the gate and hear a dinosaur roar! Collect only ${ $amount }.
monopoly-jp-gate-theme-player = { $player } activates the gate and hears the Jurassic Park theme! { $player } collects ${ $amount }.
monopoly-jp-gate-roar-player = { $player } activates the gate and hears a dinosaur roar! { $player } collects only ${ $amount }.
monopoly-jp-gate-amber-theme = You rolled { $roll } on the amber die: it's the Jurassic Park theme! Collect ${ $amount }.
monopoly-jp-gate-amber-roar = You rolled { $roll } on the amber die: it's the roar of a dinosaur! Collect only ${ $amount }.

# Fence messages
monopoly-jp-fence-built = { $player } builds a fence on { $property } for ${ $amount }. ({ $remaining } fences left)
monopoly-jp-fence-built-you = You build a fence on { $property } for ${ $amount }. ({ $remaining } fences left)
monopoly-jp-fence-sold = { $player } sells the fence on { $property } for ${ $amount }.
monopoly-jp-fence-sold-you = You sell the fence on { $property } for ${ $amount }.
monopoly-jp-fence-not-paddock = Fences can only be built on Dino Paddocks.
monopoly-jp-fence-not-owner = You do not own this property.
monopoly-jp-fence-already-built = This paddock already has a fence.
monopoly-jp-fence-damaged = This property is damaged. Repair it before building a fence.
monopoly-jp-fence-none-left = There are no fences left to build.
monopoly-jp-fence-status = { $property } has a fence.
monopoly-jp-fences-remaining = { $count } fences remaining in the bank.

# Repair messages
monopoly-jp-repair-success = { $player } repairs { $property } for ${ $amount }.
monopoly-jp-repair-success-you = You repair { $property } for ${ $amount }.
monopoly-jp-repair-not-damaged = { $property } is not damaged.
monopoly-jp-repair-not-owner = You do not own this property.
monopoly-jp-repair-free = { $property } is repaired for free as part of the { $group } complete set!

# Complete set messages
monopoly-jp-set-complete = { $player } completes the { $group } set! Those properties are now immune to the T. Rex.
monopoly-jp-set-complete-you = You complete the { $group } set! Those properties are now immune to the T. Rex.
monopoly-jp-set-auto-repair = { $property } is automatically repaired for free!
monopoly-jp-set-immune = The { $group } set is immune to T. Rex damage.

# Property damage messages
monopoly-jp-property-damaged-status = { $property } is damaged and cannot collect rent.
monopoly-jp-property-no-rent-damaged = { $property } is damaged; no rent is due.

# Penalty space messages
monopoly-jp-penalty-paid-you = You pay ${ $amount } for { $space }.
monopoly-jp-penalty-paid-player = { $player } pays ${ $amount } for { $space }.

# Park status summary action
monopoly-jp-read-park-state = Read park state
monopoly-jp-park-summary-trex = T. Rex is on space { $position } ({ $space }).
monopoly-jp-park-summary-damaged = { $count } properties are damaged.
monopoly-jp-park-summary-fenced = { $count } properties have fences.
monopoly-jp-park-summary-fences-left = { $remaining } fences remain in the bank.
monopoly-jp-park-summary-sets = Complete sets immune to T. Rex: { $sets }.
monopoly-jp-park-summary-no-sets = No complete sets yet.

# Game actions specific to JP
monopoly-jp-build-fence = Build fence
monopoly-jp-repair-property = Repair property
monopoly-jp-sell-fence = Sell fence
monopoly-jp-select-property-fence = Select a property to fence
monopoly-jp-select-property-repair = Select a property to repair
monopoly-jp-select-fence-sell = Select a fence to sell

# Game end - all properties damaged
monopoly-jp-all-damaged = All properties have been damaged by the T. Rex. The game is over. Nobody wins!
monopoly-jp-all-damaged-warning = Warning: { $remaining } undamaged and unprotected properties remain. Protect them before the T. Rex destroys the park!

# Board announcement
monopoly-jp-board-announcement = Welcome to Jurassic Park! Secure dinosaur paddocks, build fences, and watch out for the rampaging T. Rex.

# Token names
monopoly-jp-token-grant = Dr. Alan Grant
monopoly-jp-token-malcolm = Dr. Ian Malcolm
monopoly-jp-token-sattler = Dr. Ellie Sattler
monopoly-jp-token-hammond = John Hammond
monopoly-jp-token-lex = Lex Murphy
monopoly-jp-token-tim = Tim Murphy

# Deed overrides for JP
monopoly-jp-deed-type-dino-paddock = Type: { $color } Dino Paddock
monopoly-jp-deed-type-park-road = Type: Park Road
monopoly-jp-deed-type-utility = Type: Utility
monopoly-jp-deed-fence-cost = Fence cost: { $amount }
monopoly-jp-deed-repair-cost = Repair cost: { $amount }
monopoly-jp-deed-rent-with-fence = Rent with fence: { $amount }
monopoly-jp-deed-park-road-rent = Rent with { $count } Park Roads: { $amount }

# Color group names for JP narration
monopoly-jp-group-park_road = Park Roads
monopoly-jp-group-utility = Utilities
