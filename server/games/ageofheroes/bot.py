"""Bot AI for Age of Heroes."""

from __future__ import annotations
import random
from typing import TYPE_CHECKING

from .cards import Card, CardType, ResourceType, EventType
from .state import (
    GamePhase,
    PlaySubPhase,
    ActionType,
    BuildingType,
    WarGoal,
    BUILDING_COSTS,
    TRIBE_SPECIAL_RESOURCE,
)
from .construction import (
    can_build,
    get_affordable_buildings,
    get_road_targets,
    execute_single_build,
)
from .combat import (
    can_declare_war,
    get_valid_war_targets,
    get_valid_war_goals,
    check_olympics_defense,
    declare_war,
    prepare_forces,
    execute_war_battle,
)
from .trading import create_offer, announce_offer, check_and_execute_trades

if TYPE_CHECKING:
    from .game import AgeOfHeroesGame, AgeOfHeroesPlayer
    from .state import TribeState


def bot_think(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str | None:
    """Main bot AI decision function. Returns action ID or None."""
    # Eliminated players can't act
    if player.is_spectator:
        return None

    # Setup phase - roll dice
    if game.phase == GamePhase.SETUP:
        if player.id not in game.setup_rolls:
            return "roll_dice"
        return None

    # Play phase decisions
    if game.phase == GamePhase.PLAY:
        return bot_think_play_phase(game, player)

    # Fair phase - trading decisions
    if game.phase == GamePhase.FAIR:
        return bot_think_fair_phase(game, player)

    return None


def bot_think_play_phase(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str | None:
    """Bot decision making during play phase."""
    # War battle - both attacker and defender need to roll (regardless of whose turn it is)
    if game.sub_phase == PlaySubPhase.WAR_BATTLE:
        active_players = game.get_active_players()
        # Check if player is still active (not eliminated)
        if player not in active_players:
            return None

        player_index = active_players.index(player)
        war = game.war_state

        # Check if this bot is involved in the war and hasn't rolled
        if player_index == war.attacker_index and war.attacker_roll == 0:
            return "war_roll_dice"
        if player_index == war.defender_index and war.defender_roll == 0:
            return "war_roll_dice"

    # Road permission request - respond even if not current player
    active_players = game.get_active_players()
    if player in active_players:
        player_index = active_players.index(player)
        if game.road_request_to == player_index and game.road_request_from >= 0:
            # Bot is being asked for road permission - approve most of the time
            # Could add more sophisticated logic here (e.g., deny if at war with requester)
            if random.random() < 0.9:  # 90% approval rate  # nosec B311
                return "approve_road"
            else:
                return "deny_road"

    if game.current_player != player:
        return None

    if game.sub_phase == PlaySubPhase.SELECT_ACTION:
        return bot_select_action(game, player)

    if game.sub_phase == PlaySubPhase.DISCARD_EXCESS:
        return bot_discard_excess(game, player)

    return None


def bot_select_action(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str:
    """Bot selects main turn action."""
    if not player.tribe_state:
        return f"action_{ActionType.DO_NOTHING.value}"

    cities = player.tribe_state.cities
    armies = player.tribe_state.get_available_armies()
    monument = player.tribe_state.monument_progress

    # Check what we can build
    affordable = get_affordable_buildings(game, player)

    # Priority-based decision making:
    # 0. Play disaster cards if beneficial
    # 1. Build city if close to victory (4 cities) and can afford it
    # 2. Build city if possible (victory path)
    # 3. Collect special resources (monument victory)
    # 4. Build armies if threatened or planning war
    # 5. Attack weak opponents
    # 6. Build other structures
    # 7. Tax collection for cards
    # 8. Do nothing

    disaster_action = _bot_disaster_action(game, player)
    if disaster_action:
        return disaster_action

    city_action = _bot_city_build_action(affordable, cities)
    if city_action:
        return city_action

    monument_action = _bot_monument_tax_action(monument)
    if monument_action:
        return monument_action

    war_action = _bot_war_action(game, player, armies)
    if war_action:
        return war_action

    army_action = _bot_army_build_action(affordable, armies)
    if army_action:
        return army_action

    other_build_action = _bot_other_build_action(affordable)
    if other_build_action:
        return other_build_action

    tax_action = _bot_tax_action(cities)
    if tax_action:
        return tax_action

    # Default to do nothing
    return f"action_{ActionType.DO_NOTHING.value}"


def _bot_disaster_action(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str | None:
    """Consider playing a disaster card if the timing is right."""
    if game.current_day <= 1:
        return None
    return bot_should_play_disaster(game, player)


def _bot_city_build_action(affordable: list[BuildingType], cities: int) -> str | None:
    """Prefer building cities when it advances victory."""
    if cities == 4 and BuildingType.CITY in affordable:
        return f"action_{ActionType.CONSTRUCTION.value}"
    if BuildingType.CITY in affordable and cities < 5:
        if random.random() < 0.8:  # 80% chance to build  # nosec B311
            return f"action_{ActionType.CONSTRUCTION.value}"
    return None


def _bot_monument_tax_action(monument: int) -> str | None:
    """Collect cards to push monument progress."""
    if monument >= 3:
        return f"action_{ActionType.TAX_COLLECTION.value}"
    return None


def _bot_war_action(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, armies: int) -> str | None:
    """Decide whether to declare war."""
    if armies < 1:
        return None
    if can_declare_war(game, player) is not None:
        return None

    targets = get_valid_war_targets(game, player)
    for _target_idx, target in targets:
        if not hasattr(target, "tribe_state") or not target.tribe_state:
            continue
        target_armies = target.tribe_state.get_available_armies()
        target_fortresses = target.tribe_state.fortresses
        effective_defense = target_armies + target_fortresses
        advantage = armies - effective_defense

        if advantage >= 2:
            return f"action_{ActionType.WAR.value}"
        if advantage >= 0:  # Equal or better
            if random.random() < 0.75:  # nosec B311
                return f"action_{ActionType.WAR.value}"
            continue
        if advantage >= -1:  # Slight disadvantage
            if random.random() < 0.5:  # nosec B311
                return f"action_{ActionType.WAR.value}"
    return None


def _bot_army_build_action(affordable: list[BuildingType], armies: int) -> str | None:
    """Build armies when low on defense."""
    if armies < 3 and BuildingType.ARMY in affordable:
        if random.random() < 0.7:  # 70% chance to build army when low  # nosec B311
            return f"action_{ActionType.CONSTRUCTION.value}"
    return None


def _bot_other_build_action(affordable: list[BuildingType]) -> str | None:
    """Chance to build other affordable structures."""
    if affordable and random.random() < 0.4:  # nosec B311
        return f"action_{ActionType.CONSTRUCTION.value}"
    return None


def _bot_tax_action(cities: int) -> str | None:
    """Fallback tax collection when at least one city exists."""
    if cities >= 1:
        return f"action_{ActionType.TAX_COLLECTION.value}"
    return None


def bot_discard_excess(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str | None:
    """Bot decides which card to discard when over hand limit."""
    # This would trigger a discard action - for now handled automatically
    # The game.py already handles bot auto-discard
    return None


def bot_think_fair_phase(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str | None:
    """Bot decision making during fair/trading phase."""
    # For simplicity, bots don't actively trade - they just stop
    if not player.has_stopped_trading:
        return "stop_trading"
    return None


def bot_select_construction(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str | None:
    """Bot selects what to build."""
    if not player.tribe_state:
        return None

    affordable = get_affordable_buildings(game, player)
    if not affordable:
        return None

    cities = player.tribe_state.cities
    armies = player.tribe_state.get_available_armies()
    fortresses = player.tribe_state.fortresses

    # Priority order:
    # 1. City (if close to victory)
    # 2. Army (if vulnerable)
    # 3. Fortress (if no fortress)
    # 4. General (if armies > generals)
    # 5. Road (for fair cards)
    # 6. City (general case)
    # 7. Army (general case)

    # Close to victory - build city
    if cities >= 3 and BuildingType.CITY in affordable:
        return BuildingType.CITY

    # Vulnerable - build army
    if armies < 2 and BuildingType.ARMY in affordable:
        return BuildingType.ARMY

    # No fortress - build one
    if fortresses == 0 and BuildingType.FORTRESS in affordable:
        return BuildingType.FORTRESS

    # Need generals
    generals = player.tribe_state.generals
    if armies > generals + 1 and BuildingType.GENERAL in affordable:
        return BuildingType.GENERAL

    # Build road for fair cards
    if BuildingType.ROAD in affordable:
        targets = get_road_targets(game, player)
        if targets and random.random() < 0.3:  # nosec B311
            return BuildingType.ROAD

    # Default priorities
    if BuildingType.CITY in affordable:
        return BuildingType.CITY
    if BuildingType.ARMY in affordable:
        return BuildingType.ARMY

    # Build anything available
    return random.choice(affordable) if affordable else None  # nosec B311


def _select_war_goal(
    available_goals: list[str],
    target_state: "TribeState",
    our_state: "TribeState",
) -> str:
    """Select the best war goal based on strategic considerations."""
    from .state import TribeState

    # Priority 1: Destruction if target is close to monument victory
    if WarGoal.DESTRUCTION in available_goals and target_state.monument_progress >= 2:
        # Higher chance to destroy if they're closer to winning
        if target_state.monument_progress >= 4:
            return WarGoal.DESTRUCTION
        elif target_state.monument_progress >= 3 and random.random() < 0.8:  # nosec B311
            return WarGoal.DESTRUCTION
        elif random.random() < 0.5:  # nosec B311
            return WarGoal.DESTRUCTION

    # Priority 2: Conquest if target has cities and we want to expand
    if WarGoal.CONQUEST in available_goals:
        # Strong preference if target has many cities or we're close to city victory
        if target_state.cities >= 3 or our_state.cities >= 3:
            if random.random() < 0.7:  # nosec B311
                return WarGoal.CONQUEST
        # Otherwise still consider it
        elif random.random() < 0.4:  # nosec B311
            return WarGoal.CONQUEST

    # Priority 3: Plunder for resources
    if WarGoal.PLUNDER in available_goals:
        # Good if we need cards for building
        if random.random() < 0.6:  # nosec B311
            return WarGoal.PLUNDER

    # Default: pick first available
    return available_goals[0] if available_goals else WarGoal.CONQUEST


def bot_select_war_target(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer
) -> tuple[int, str] | None:
    """Bot selects war target and goal. Returns (target_index, goal) or None."""
    if not player.tribe_state:
        return None

    targets = get_valid_war_targets(game, player)
    if not targets:
        return None

    our_armies = player.tribe_state.get_available_armies()

    # Score each target
    best_target = None
    best_score = -999  # Can be negative now (fighting with disadvantage)
    best_goal = WarGoal.CONQUEST

    for target_idx, target in targets:
        if not hasattr(target, "tribe_state") or not target.tribe_state:
            continue

        target_armies = target.tribe_state.get_available_armies()
        target_fortresses = target.tribe_state.fortresses

        # Be willing to attack even if slightly disadvantaged
        effective_defense = target_armies + target_fortresses
        # Allow attacking if not more than 2 armies disadvantaged
        if our_armies < effective_defense - 2:
            continue

        # Get valid goals for this target
        goals = get_valid_war_goals(game, player, target)
        if not goals:
            continue

        # Score the target (can be negative now)
        score = our_armies - effective_defense

        # Select goal based on strategic value
        selected_goal = _select_war_goal(goals, target.tribe_state, player.tribe_state)

        # Bonus score for high-value targets
        if selected_goal == WarGoal.CONQUEST and target.tribe_state.cities >= 4:
            score += 10  # Target close to city victory
        elif selected_goal == WarGoal.DESTRUCTION and target.tribe_state.monument_progress >= 3:
            score += 8  # Target close to monument victory

        if score > best_score:
            best_score = score
            best_target = target_idx
            best_goal = selected_goal

    if best_target is not None:
        return (best_target, best_goal)

    return None


def bot_select_armies(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, is_attacking: bool
) -> tuple[int, int, int, int]:
    """Bot selects armies, generals, heroes for battle.

    Returns (armies, generals, heroes_as_armies, heroes_as_generals).
    """
    if not player.tribe_state:
        return (0, 0, 0, 0)

    available_armies = player.tribe_state.get_available_armies()
    available_generals = player.tribe_state.get_available_generals()

    # Count hero cards
    hero_cards = sum(
        1
        for card in player.hand
        if card.card_type == CardType.EVENT and card.subtype == EventType.HERO
    )

    if is_attacking:
        # Commit all or most forces when attacking
        # Only keep 1 back if we have 3+ armies, otherwise commit everything
        if available_armies >= 3:
            armies = available_armies - 1
        else:
            armies = available_armies
        generals = available_generals
        # Use hero cards as armies for extra strength
        heroes_as_armies = hero_cards
        heroes_as_generals = 0
    else:
        # Defending - commit all available forces
        armies = available_armies
        generals = available_generals
        # Use heroes as generals for defense bonus
        heroes_as_armies = 0
        heroes_as_generals = hero_cards

    return (armies, generals, heroes_as_armies, heroes_as_generals)


def bot_should_use_olympics(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> bool:
    """Bot decides whether to use Olympic Games to cancel war."""
    if not player.tribe_state:
        return False

    # Use Olympics if:
    # 1. We have few armies to defend
    # 2. The war goal threatens our victory

    our_armies = player.tribe_state.get_available_armies()
    our_cities = player.tribe_state.cities
    our_monument = player.tribe_state.monument_progress

    war = game.war_state

    # Definitely use if we have no armies
    if our_armies == 0:
        return True

    # Use if conquest and we're close to losing
    if war.goal == WarGoal.CONQUEST and our_cities <= 1:
        return True

    # Use if destruction and we're close to monument victory
    if war.goal == WarGoal.DESTRUCTION and our_monument >= 4:
        return True

    # Use if we're significantly outnumbered
    attacker_strength = war.get_attacker_total_armies() + war.get_attacker_total_generals()
    defender_strength = our_armies + player.tribe_state.fortresses
    if attacker_strength > defender_strength * 2:
        return True

    return False


def bot_should_use_fortune(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, lost_roll: bool
) -> bool:
    """Bot decides whether to use Fortune to reroll."""
    if not lost_roll:
        return False

    if not player.tribe_state:
        return False

    war = game.war_state
    active_players = game.get_active_players()
    player_index = active_players.index(player)

    # Use if we're the attacker and close to winning
    if player_index == war.attacker_index:
        if war.get_attacker_total_armies() > 0:
            # Use Fortune to try to win
            return True

    # Use if we're the defender and about to lose badly
    if player_index == war.defender_index:
        if war.get_defender_total_armies() <= 1:
            # Last chance - use Fortune
            return True

    return False


def score_card_for_discard(card: Card, player: AgeOfHeroesPlayer) -> int:
    """Score a card for discard decision. Higher = more likely to discard."""
    if not player.tribe_state:
        return 50

    score = 50  # Base score

    # Never discard our special monument resource
    if card.card_type == CardType.SPECIAL:
        own_special = player.tribe_state.get_special_resource()
        if card.subtype == own_special:
            return 0  # Never discard
        else:
            # Other special resources have some value for trading
            score = 30

    # Resources have moderate value
    if card.card_type == CardType.RESOURCE:
        # Check if we need this for building
        resource = card.subtype
        needed_count = 0
        for building, costs in BUILDING_COSTS.items():
            if resource in costs:
                needed_count += 1

        # More useful resources are less likely to be discarded
        score = 60 - (needed_count * 10)

    # Events have varying value
    if card.card_type == CardType.EVENT:
        if card.subtype == EventType.HERO:
            score = 20  # Very useful
        elif card.subtype == EventType.FORTUNE:
            score = 30  # Useful
        elif card.subtype == EventType.OLYMPICS:
            # More valuable if we have few armies
            if player.tribe_state.get_available_armies() < 2:
                score = 10
            else:
                score = 40
        else:
            # Other events (disasters handled elsewhere)
            score = 70

    return score


def bot_select_card_to_discard(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> int:
    """Bot selects which card to discard. Returns card index."""
    if not player.hand:
        return 0

    # Score each card
    best_index = 0
    best_score = -1

    for i, card in enumerate(player.hand):
        score = score_card_for_discard(card, player)
        if score > best_score:
            best_score = score
            best_index = i

    return best_index


# ==========================================================================
# Bot Orchestration Functions
# These functions orchestrate bot actions and call game methods.
# ==========================================================================


def bot_do_trading(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> None:
    """Bot performs trading actions during fair phase."""
    # Import here to get constants
    from .game import TRADING_TIMEOUT_TICKS

    if player.has_stopped_trading:
        return

    # First, make offers if we haven't yet
    if not player.has_made_offers:
        bot_make_trade_offers(game, player)
        player.has_made_offers = True
        return

    # Check for matching trades and execute them
    trades_made = check_and_execute_trades(game)

    # If a trade was made, reset the wait timer
    if trades_made:
        player.trading_ticks_waited = 0
        return

    # Increment wait time
    player.trading_ticks_waited += 1

    # Stop trading after timeout
    if player.trading_ticks_waited >= TRADING_TIMEOUT_TICKS:
        game._action_stop_trading(player, "stop_trading")


def bot_make_trade_offers(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> None:
    """Bot makes trade offers for cards they want."""
    if not player.tribe_state:
        return

    # What do we want? Our special resource for monument
    wanted_special = TRIBE_SPECIAL_RESOURCE.get(player.tribe_state.tribe)

    # Look through our hand for cards to offer
    for i, card in enumerate(player.hand):
        # Don't offer our own special resource
        if card.card_type == CardType.SPECIAL:
            if card.subtype == wanted_special:
                continue  # Keep this, we need it!

        # Offer other special resources (we can't use them)
        if card.card_type == CardType.SPECIAL:
            # Offer this for our special resource
            offer = create_offer(
                game,
                player,
                i,
                wanted_type=CardType.SPECIAL,
                wanted_subtype=wanted_special,
            )
            if offer:
                announce_offer(game, player, card, wanted_special)

        # Offer disaster cards for anything useful
        if card.is_disaster():
            # Offer for our special resource
            offer = create_offer(
                game,
                player,
                i,
                wanted_type=CardType.SPECIAL,
                wanted_subtype=wanted_special,
            )
            if offer:
                announce_offer(game, player, card, wanted_special)


def bot_perform_construction(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> None:
    """Bot performs construction - can build multiple things per turn."""
    if not player.tribe_state:
        game._end_action(player)
        return

    # Keep building as long as bot wants to and has resources
    while True:
        # Check if bot can still afford to build anything
        affordable = get_affordable_buildings(game, player)
        if not affordable:
            # No more buildings available
            game._end_action(player)
            return

        # Use bot AI to select what to build
        building_type = bot_select_construction(game, player)
        if not building_type:
            # Bot decided to stop building
            game._end_action(player)
            return

        # Execute the build using shared logic
        success = execute_single_build(game, player, building_type, auto_road=True)
        if not success:
            # Build failed or victory occurred - stop building
            if player.tribe_state:  # Only end action if not victory (which already ended game)
                game._end_action(player)
            return

        # If we're waiting for road permission, exit loop and wait for response
        if game.sub_phase == PlaySubPhase.ROAD_PERMISSION:
            return

        # Continue loop - bot might build more things


def bot_perform_war(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> None:
    """Bot performs war declaration and combat."""
    # Import here to avoid circular import at module level
    from .game import AgeOfHeroesPlayer as AOHPlayer

    if not player.tribe_state:
        game._end_action(player)
        return

    # Select target and goal using bot AI
    result = bot_select_war_target(game, player)
    if not result:
        game._end_action(player)
        return

    target_index, goal = result

    # Declare war
    if not declare_war(game, player, target_index, goal):
        game._end_action(player)
        return

    # Get defender
    active_players = game.get_active_players()
    defender = active_players[target_index]
    if not isinstance(defender, AOHPlayer):
        game.war_state.reset()
        game._end_action(player)
        return

    # Prepare attacker forces using bot AI
    att_armies, att_generals, att_heroes, att_hero_generals = bot_select_armies(
        game, player, is_attacking=True
    )
    prepare_forces(game, player, att_armies, att_generals, att_heroes, att_hero_generals)

    # Prepare defender forces (if bot) or auto-prepare
    if defender.is_bot:
        def_armies, def_generals, def_heroes, def_hero_generals = bot_select_armies(
            game, defender, is_attacking=False
        )
        prepare_forces(game, defender, def_armies, def_generals, def_heroes, def_hero_generals)
    else:
        # Auto-prepare defender with all available forces
        if defender.tribe_state:
            def_armies = defender.tribe_state.get_available_armies()
            def_generals = defender.tribe_state.get_available_generals()
            prepare_forces(game, defender, def_armies, def_generals, 0, 0)

    # Execute battle using shared logic
    # Note: execute_war_battle() enters interactive mode, battle will complete when both sides roll
    # finish_war_battle() will call _end_action() when battle is done
    execute_war_battle(game)


def bot_execute_discard_excess(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> None:
    """Bot executes discarding excess cards (orchestration function)."""
    from .game import MAX_HAND_SIZE

    while len(player.hand) > MAX_HAND_SIZE:
        # Discard least valuable card (simple heuristic)
        worst_index = 0
        player.hand.pop(worst_index)
    player.pending_discard = 0
    game._end_turn()


def bot_should_play_disaster(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str | None:
    """Check if bot should play a disaster card. Returns action_id or None."""
    if not player.tribe_state:
        return None

    # Find disaster cards in hand
    earthquake_indices = []
    eruption_indices = []
    for i, card in enumerate(player.hand):
        if card.card_type == CardType.EVENT:
            if card.subtype == EventType.EARTHQUAKE:
                earthquake_indices.append(i)
            elif card.subtype == EventType.ERUPTION:
                eruption_indices.append(i)

    if not earthquake_indices and not eruption_indices:
        return None

    # Get all other players as potential targets
    active_players = game.get_active_players()
    targets = []
    for i, p in enumerate(active_players):
        if p != player and hasattr(p, "tribe_state") and p.tribe_state:
            targets.append((i, p))

    if not targets:
        return None

    # Score each target for each disaster type
    best_score = -999
    best_action = None

    # Evaluate Earthquake (disable armies)
    for card_index in earthquake_indices:
        for target_idx, target in targets:
            score = _score_earthquake_target(player.tribe_state, target)
            if score > best_score:
                best_score = score
                best_action = f"play_earthquake_{card_index}"

    # Evaluate Eruption (destroy city)
    for card_index in eruption_indices:
        for target_idx, target in targets:
            score = _score_eruption_target(player.tribe_state, target)
            if score > best_score:
                best_score = score
                best_action = f"play_eruption_{card_index}"

    # Play if score is positive (beneficial) or even neutral if no better options
    # Slight bias: play disaster cards opportunistically (threshold of -5)
    if best_score > -5:
        return best_action

    return None


def _score_earthquake_target(our_state: "TribeState" | None, target: AgeOfHeroesPlayer) -> int:
    """Score a target for Earthquake. Higher = better target."""
    if not target.tribe_state or not our_state:
        return -999

    target_armies = target.tribe_state.get_available_armies()

    # Don't waste on targets with no armies
    if target_armies == 0:
        return -999

    score = 0

    # High value: Target with many armies (disrupt their plans)
    score += target_armies * 10

    # Higher value if target is close to victory
    if target.tribe_state.cities >= 4:
        score += 30  # They might attack us or win soon
    if target.tribe_state.monument_progress >= 4:
        score += 20

    # Lower value if they have few cities (less threatening)
    if target.tribe_state.cities <= 1:
        score -= 10

    return score


def _score_eruption_target(our_state: "TribeState" | None, target: AgeOfHeroesPlayer) -> int:
    """Score a target for Eruption. Higher = better target."""
    if not target.tribe_state or not our_state:
        return -999

    target_cities = target.tribe_state.cities

    # Don't waste on targets with no cities
    if target_cities == 0:
        return -999

    score = 0

    # Very high value: Target close to city victory
    if target_cities >= 4:
        score += 100  # Stop them from winning!
    elif target_cities >= 3:
        score += 50

    # Moderate value: Weaken a strong opponent
    if target_cities >= 2:
        score += 20

    # Small value: Any city destruction is somewhat useful
    score += 10

    return score


def bot_play_disaster_on_target(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer, disaster_type: str
) -> None:
    """Bot plays a disaster card against the best target.

    Called after bot selects a disaster action via bot_should_play_disaster.
    """
    from .events import apply_earthquake_effect, apply_eruption_effect

    if not player.tribe_state:
        game._end_action(player)
        return

    card_index = _find_disaster_card_index(player.hand, disaster_type)
    if card_index is None:
        game._end_action(player)
        return

    targets = _get_disaster_targets(game, player)
    if not targets:
        game._end_action(player)
        return

    best_target, best_score = _select_best_disaster_target(
        disaster_type, player.tribe_state, targets
    )
    if not best_target or best_score <= 0:
        game._end_action(player)
        return

    # Remove card and apply effect
    card = player.hand.pop(card_index)
    game.discard_pile.append(card)

    if disaster_type == EventType.EARTHQUAKE:
        apply_earthquake_effect(game, player, best_target)
    elif disaster_type == EventType.ERUPTION:
        apply_eruption_effect(game, player, best_target)

    # Return to action selection so bot can continue its turn
    game.sub_phase = PlaySubPhase.SELECT_ACTION
    game.rebuild_all_menus()


def _find_disaster_card_index(hand: list[Card], disaster_type: str) -> int | None:
    """Locate the first matching disaster card in hand."""
    for i, card in enumerate(hand):
        if card.card_type == CardType.EVENT and card.subtype == disaster_type:
            return i
    return None


def _get_disaster_targets(
    game: AgeOfHeroesGame, player: AgeOfHeroesPlayer
) -> list[tuple[int, AgeOfHeroesPlayer]]:
    """Collect valid disaster targets."""
    active_players = game.get_active_players()
    return [
        (i, p)
        for i, p in enumerate(active_players)
        if p != player and hasattr(p, "tribe_state") and p.tribe_state
    ]


def _select_best_disaster_target(
    disaster_type: str,
    our_state: "TribeState",
    targets: list[tuple[int, AgeOfHeroesPlayer]],
) -> tuple[AgeOfHeroesPlayer | None, int]:
    """Pick the highest scoring target for the given disaster type."""
    best_target = None
    best_score = -999

    if disaster_type == EventType.EARTHQUAKE:
        score_fn = _score_earthquake_target
    elif disaster_type == EventType.ERUPTION:
        score_fn = _score_eruption_target
    else:
        return None, best_score

    for _target_idx, target in targets:
        score = score_fn(our_state, target)
        if score > best_score:
            best_score = score
            best_target = target

    return best_target, best_score


def bot_do_select_action(game: AgeOfHeroesGame, player: AgeOfHeroesPlayer) -> str:
    """Bot selects a main action. Wrapper for bot_select_action."""
    return bot_select_action(game, player)
