"""Handler helpers for Monopoly turn actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...base import Player
from ..voice_commands import parse_voice_command

if TYPE_CHECKING:
    from ..game import MonopolyGame


def _game_randint(low: int, high: int) -> int:
    """Use Monopoly game-module RNG so existing monkeypatches keep working."""
    from .. import game as monopoly_game_module

    return monopoly_game_module.random.randint(low, high)


MONOPOLY_MOVE_START_DELAY_TICKS = 8
MONOPOLY_MOVE_STEP_INTERVAL_TICKS = 4


def _resolve_property_amount_selection(
    game: MonopolyGame,
    player: Player,
    option: str,
    *,
    option_builder: str,
    space_ids: list[str],
) -> str | None:
    """Map a property amount label back to its underlying space id."""
    resolved = game._parse_property_amount_option(option)
    if resolved in space_ids:
        return resolved
    built_options = getattr(game, option_builder)(player)
    for built_option, space_id in zip(built_options, space_ids, strict=False):
        if built_option == option:
            return space_id
    return option if option in space_ids else None


def _resolve_space_selection(
    game: MonopolyGame,
    player: Player,
    option: str,
    *,
    option_builder: str,
    space_ids: list[str],
) -> str | None:
    """Map one menu label back to a space id by matching current option order."""
    if option in space_ids:
        return option
    built_options = getattr(game, option_builder)(player)
    for built_option, space_id in zip(built_options, space_ids, strict=False):
        if built_option == option:
            return space_id
    return None


def _schedule_monopoly_roll_resolution(
    game: MonopolyGame,
    player: Player,
    *,
    die_1: int,
    die_2: int,
    total: int,
    is_doubles: bool,
    collect_pass_go: bool,
    roll_message_key: str | None = "monopoly-roll-only",
    extra_powerup_die: int | None = None,
    allow_doubles_bonus_roll: bool = False,
) -> None:
    """Queue Monopoly movement pacing, then resolve the landing."""
    game.is_animating = True
    if roll_message_key:
        game._broadcast_roll_only(
            player,  # type: ignore[arg-type]
            die_1=die_1,
            die_2=die_2,
            total=total,
            is_doubles=is_doubles,
        )
    delay = game.schedule_standard_token_movement_sounds(
        total,
        start_delay_ticks=MONOPOLY_MOVE_START_DELAY_TICKS,
        step_interval_ticks=MONOPOLY_MOVE_STEP_INTERVAL_TICKS,
    )
    game.schedule_event(
        "monopoly_resolve_roll",
        {
            "player_id": player.id,
            "die_1": die_1,
            "die_2": die_2,
            "total": total,
            "is_doubles": is_doubles,
            "collect_pass_go": collect_pass_go,
            "extra_powerup_die": extra_powerup_die,
            "allow_doubles_bonus_roll": allow_doubles_bonus_roll,
        },
        delay_ticks=delay,
    )
    game.rebuild_all_menus()


def handle_scheduled_event(game: MonopolyGame, event_type: str, data: dict) -> None:
    """Handle Monopoly-specific scheduled events."""
    if event_type != "monopoly_resolve_roll":
        return

    player = game.get_player_by_id(data.get("player_id", ""))
    if player is None:
        game.is_animating = False
        return
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        game.is_animating = False
        game.rebuild_all_menus()
        return

    total = int(data["total"])
    landed_space = game._move_player(
        mono_player,
        total,
        collect_pass_go=bool(data["collect_pass_go"]),
    )
    game._broadcast_space_name(landed_space)
    resolution = game._resolve_space(mono_player, landed_space, dice_total=total)

    powerup_die = data.get("extra_powerup_die")
    if powerup_die is not None and not mono_player.bankrupt and resolution == "resolved":
        resolution = game._apply_junior_super_mario_powerup(mono_player, int(powerup_die))

    if (
        bool(data.get("allow_doubles_bonus_roll"))
        and bool(data.get("is_doubles"))
        and not mono_player.bankrupt
    ):
        if resolution == "resolved":
            game._prepare_next_roll_after_doubles(mono_player)
        elif resolution == "pending_purchase":
            game.turn_can_roll_again = True

    game.is_animating = False
    game._sync_cash_scores()
    game._advance_after_roll_resolution(mono_player)


def action_banking_balance(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Announce current electronic bank balance to the requesting player."""
    _ = action_id
    if not game._is_electronic_banking_preset():
        return
    mono_player = player  # type: ignore[assignment]
    user = game.get_user(player)
    if user:
        game._speak_monopoly_l(
            user,
            "monopoly-banking-balance-report",
            player=mono_player.name,
            cash=game._bank_balance(mono_player),
        )


def action_banking_transfer(game: MonopolyGame, player: Player, option: str, action_id: str) -> None:
    """Execute one manual bank transfer between players."""
    _ = action_id
    if not game._is_electronic_banking_preset() or game.banking_state is None:
        return
    mono_player = player  # type: ignore[assignment]
    if option not in game._options_for_banking_transfer(player):
        return
    parsed = game._parse_banking_transfer_option(option)
    if not parsed:
        return

    target_id, amount = parsed
    target = game.get_player_by_id(target_id)
    if not target or target.bankrupt:
        return

    transferred = game._transfer_between_players(
        mono_player,
        target,
        amount,
        "manual_transfer",
    )
    if transferred == amount:
        game._broadcast_monopoly_transaction(
            mono_player,
            target,
            actor_message_id="monopoly-you-banking-transfer-success",
            recipient_message_id="monopoly-player-banking-transferred-to-you",
            others_message_id="monopoly-player-banking-transfer-success",
            actor_fallback=f"You transferred {game._format_money(transferred)} to {target.name}.",
            recipient_fallback=(
                f"{mono_player.name} transferred {game._format_money(transferred)} to you."
            ),
            others_fallback=(
                f"{mono_player.name} transferred {game._format_money(transferred)} to {target.name}."
            ),
            from_player=mono_player.name,
            to_player=target.name,
            amount=transferred,
        )
    else:
        game._broadcast_monopoly_personal(
            mono_player,
            personal_message_id="monopoly-you-banking-transfer-failed",
            others_message_id="monopoly-player-banking-transfer-failed",
            personal_fallback="Your bank transfer failed (insufficient_funds).",
            others_fallback=f"{mono_player.name} bank transfer failed (insufficient_funds).",
            player=mono_player.name,
            reason="insufficient_funds",
        )

    game._sync_cash_scores()
    game.rebuild_all_menus()


def action_banking_ledger(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Announce recent banking ledger events to the requesting player."""
    _ = action_id
    user = game.get_user(player)
    if not user:
        return
    if not game._is_electronic_banking_preset() or game.banking_state is None:
        return

    entries: list[str] = []
    for tx in game.banking_state.ledger[-5:]:
        if tx.status == "success":
            entries.append(
                game._monopoly_text(
                    user.locale,
                    "monopoly-banking-ledger-entry-success",
                    fallback=f"{tx.tx_id} {tx.kind} {tx.from_id}->{tx.to_id} {tx.amount} ({tx.reason})",
                    tx_id=tx.tx_id,
                    kind=tx.kind,
                    from_id=tx.from_id,
                    to_id=tx.to_id,
                    amount=tx.amount,
                    reason=tx.reason,
                )
            )
        else:
            entries.append(
                game._monopoly_text(
                    user.locale,
                    "monopoly-banking-ledger-entry-failed",
                    fallback=f"{tx.tx_id} {tx.kind} failed ({tx.failure_reason or 'unknown'})",
                    tx_id=tx.tx_id,
                    kind=tx.kind,
                    reason=tx.failure_reason or "unknown",
                )
            )

    if not entries:
        game._speak_monopoly_l(user, "monopoly-banking-ledger-empty")
        return
    game._speak_monopoly_l(user, "monopoly-banking-ledger-report", entries=" | ".join(entries))


def action_voice_command(game: MonopolyGame, player: Player, text: str, action_id: str) -> None:
    """Parse and execute one voice-style command in voice banking preset."""
    if game.active_preset_id != "voice_banking":
        return
    mono_player = player  # type: ignore[assignment]
    parsed = parse_voice_command(text)

    user = game.get_user(player)
    if parsed.error:
        game.voice_last_response_by_player_id[mono_player.id] = parsed.error
        if user:
            game._speak_monopoly_l(user, "monopoly-voice-command-error", reason=parsed.error)
        return

    if parsed.intent == "check_balance":
        game.voice_last_response_by_player_id[mono_player.id] = parsed.intent
        if user:
            game._speak_monopoly_l(
                user,
                "monopoly-banking-balance-report",
                player=mono_player.name,
                cash=game._bank_balance(mono_player),
            )
        return

    if parsed.intent == "show_recent_ledger":
        game.voice_last_response_by_player_id[mono_player.id] = parsed.intent
        action_banking_ledger(game, player, action_id)
        return

    if parsed.intent == "repeat_last_bank_result":
        previous = game.voice_last_response_by_player_id.get(mono_player.id, "none")
        game.voice_last_response_by_player_id[mono_player.id] = parsed.intent
        if user:
            game._speak_monopoly_l(user, "monopoly-voice-command-repeat", response=previous)
        return

    if parsed.intent == "transfer_amount_to_player":
        target = None
        wanted_name = parsed.target_name.strip().lower()
        for turn_player in game.turn_players:
            if turn_player.id == mono_player.id or turn_player.bankrupt:
                continue
            if turn_player.name.lower() == wanted_name:
                target = turn_player
                break

        if target is None:
            game.voice_last_response_by_player_id[mono_player.id] = "invalid_target"
            if user:
                game._speak_monopoly_l(user, "monopoly-voice-command-error", reason="invalid_target")
            return

        game.voice_pending_transfer_by_player_id[mono_player.id] = (target.id, parsed.amount)
        game.voice_last_response_by_player_id[mono_player.id] = "transfer_pending_confirm"
        if user:
            game._speak_monopoly_l(
                user,
                "monopoly-voice-transfer-staged",
                amount=parsed.amount,
                target=target.name,
            )
        return

    if parsed.intent == "confirm_transfer":
        pending = game.voice_pending_transfer_by_player_id.get(mono_player.id)
        if not pending:
            game.voice_last_response_by_player_id[mono_player.id] = "no_pending_transfer"
            if user:
                game._speak_monopoly_l(user, "monopoly-voice-command-error", reason="no_pending_transfer")
            return

        target_id, amount = pending
        target = game.get_player_by_id(target_id)
        if not target or target.bankrupt:
            game.voice_pending_transfer_by_player_id.pop(mono_player.id, None)
            game.voice_last_response_by_player_id[mono_player.id] = "invalid_target"
            if user:
                game._speak_monopoly_l(user, "monopoly-voice-command-error", reason="invalid_target")
            return

        transferred = game._transfer_between_players(
            mono_player,
            target,
            amount,
            "voice_transfer",
        )
        game.voice_pending_transfer_by_player_id.pop(mono_player.id, None)
        if transferred == amount:
            game.voice_last_response_by_player_id[mono_player.id] = "transfer_confirmed"
            game._broadcast_monopoly_transaction(
                mono_player,
                target,
                actor_message_id="monopoly-you-banking-transfer-success",
                recipient_message_id="monopoly-player-banking-transferred-to-you",
                others_message_id="monopoly-player-banking-transfer-success",
                actor_fallback=f"You transferred {game._format_money(transferred)} to {target.name}.",
                recipient_fallback=(
                    f"{mono_player.name} transferred {game._format_money(transferred)} to you."
                ),
                others_fallback=(
                    f"{mono_player.name} transferred {game._format_money(transferred)} to {target.name}."
                ),
                from_player=mono_player.name,
                to_player=target.name,
                amount=transferred,
            )
            game._sync_cash_scores()
            game.rebuild_all_menus()
        else:
            game.voice_last_response_by_player_id[mono_player.id] = "insufficient_funds"
            if user:
                game._speak_monopoly_l(user, "monopoly-voice-command-error", reason="insufficient_funds")
        return

    game.voice_last_response_by_player_id[mono_player.id] = parsed.intent
    if user:
        game._speak_monopoly_l(user, "monopoly-voice-command-accepted", intent=parsed.intent)


def action_auction_property(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Start an interactive auction for the pending unpurchased property."""
    _ = action_id
    mono_player = player  # type: ignore[assignment]
    if game._is_auction_active():
        return
    space = game._pending_purchase_space()
    if not space:
        return

    game._start_property_auction(space, mono_player)


def action_auction_bid(game: MonopolyGame, player: Player, option: str, action_id: str) -> None:
    """Place a bid in the active interactive auction."""
    _ = action_id
    if not game._is_auction_active():
        return
    current_bidder = game._current_auction_bidder()
    if current_bidder is None or current_bidder.id != player.id:
        return
    space = game._pending_auction_space()
    if not space:
        return

    user = game.get_user(player)
    locale = user.locale if user else "en"
    bid_options = game._options_for_auction_bid(player)
    custom_label = game._monopoly_text(
        locale,
        "monopoly-auction-bid-custom-option",
        fallback="Enter bid amount",
    )
    if option == custom_label:
        if user:
            game._pending_actions[player.id] = "auction_bid"
            user.show_editbox(
                "action_input_editbox",
                game._monopoly_text(
                    locale,
                    "monopoly-enter-auction-bid",
                    fallback="Enter auction bid amount",
                ),
                str(game._auction_min_bid()),
            )
        return
    try:
        bid = int(option)
    except ValueError:
        if option not in bid_options:
            return
        return

    min_bid = game._auction_min_bid()
    if bid < min_bid or bid > game._current_liquid_balance(current_bidder):
        return

    game.pending_auction_current_bid = bid
    game.pending_auction_high_bidder_id = current_bidder.id
    game._broadcast_monopoly_personal(
        current_bidder,
        personal_message_id="monopoly-you-auction-bid-placed",
        others_message_id="monopoly-player-auction-bid-placed",
        personal_fallback=f"You bid {game._format_money(bid)} for {space.name}.",
        others_fallback=f"{current_bidder.name} bid {game._format_money(bid)} for {space.name}.",
        player=current_bidder.name,
        property=space.name,
        amount=bid,
    )

    current_index = game.pending_auction_turn_index % len(game.pending_auction_bidder_ids)
    game._advance_pending_auction_turn(current_index)
    if game._is_auction_active():
        game.rebuild_all_menus()


def action_auction_pass(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Pass on bidding in the active interactive auction."""
    _ = action_id
    if not game._is_auction_active():
        return
    current_bidder = game._current_auction_bidder()
    if current_bidder is None or current_bidder.id != player.id:
        return
    if player.id not in game.pending_auction_bidder_ids:
        return

    space = game._pending_auction_space()
    if not space:
        game._finish_pending_auction()
        return

    current_index = game.pending_auction_bidder_ids.index(player.id)
    game.pending_auction_bidder_ids.remove(player.id)
    if game.pending_auction_high_bidder_id == player.id:
        game.pending_auction_high_bidder_id = ""
        game.pending_auction_current_bid = 0
    game._broadcast_monopoly_personal(
        current_bidder,
        personal_message_id="monopoly-you-auction-pass-event",
        others_message_id="monopoly-player-auction-pass-event",
        personal_fallback=f"You passed on {space.name}.",
        others_fallback=f"{current_bidder.name} passed on {space.name}.",
        player=current_bidder.name,
        property=space.name,
    )

    game._advance_pending_auction_turn(current_index - 1)
    if game._is_auction_active():
        game.rebuild_all_menus()


def action_mortgage_property(
    game: MonopolyGame, player: Player, space_id: str, action_id: str
) -> None:
    """Mortgage one owned property to raise cash."""
    _ = action_id
    if game._is_junior_preset():
        return
    mono_player = player  # type: ignore[assignment]
    mortgage_space_ids = game._mortgage_space_ids(player)
    resolved_space_id = _resolve_property_amount_selection(
        game,
        player,
        space_id,
        option_builder="_options_for_mortgage_property",
        space_ids=mortgage_space_ids,
    )
    if resolved_space_id not in mortgage_space_ids:
        return
    space = game.active_space_by_id.get(resolved_space_id)
    if not space:
        return

    value = game._mortgage_value(space)
    credited = game._credit_player(mono_player, value, f"mortgage:{space.space_id}")
    if credited <= 0:
        return
    game.mortgaged_space_ids.append(resolved_space_id)
    game._broadcast_monopoly_personal(
        mono_player,
        personal_message_id="monopoly-you-property-mortgaged",
        others_message_id="monopoly-player-property-mortgaged",
        personal_fallback=f"You mortgaged {space.name} for {game._format_money(credited)}.",
        others_fallback=f"{mono_player.name} mortgaged {space.name} for {game._format_money(credited)}.",
        player=mono_player.name,
        property=space.name,
        amount=credited,
    )

    game._sync_cash_scores()
    game._try_resolve_pending_rent_payment(mono_player)
    if not game._can_manage_assets_now(player):
        game.rebuild_all_menus()
        return
    remaining_options = game._options_for_mortgage_property(player)
    if remaining_options:
        game._reopen_action_options_menu(
            player,
            pending_action_id="mortgage_property",
            options=remaining_options,
        )
        return
    game.rebuild_all_menus()


def action_unmortgage_property(
    game: MonopolyGame, player: Player, space_id: str, action_id: str
) -> None:
    """Unmortgage one owned property."""
    _ = action_id
    if game._is_junior_preset():
        return
    mono_player = player  # type: ignore[assignment]
    unmortgage_space_ids = game._unmortgage_space_ids(player)
    resolved_space_id = _resolve_property_amount_selection(
        game,
        player,
        space_id,
        option_builder="_options_for_unmortgage_property",
        space_ids=unmortgage_space_ids,
    )
    if resolved_space_id not in unmortgage_space_ids:
        return
    space = game.active_space_by_id.get(resolved_space_id)
    if not space:
        return

    cost = game._unmortgage_cost(space)
    if game._current_liquid_balance(mono_player) < cost:
        user = game.get_user(player)
        if user:
            user.speak_l("monopoly-not-enough-cash")
        remaining_options = game._options_for_unmortgage_property(player)
        if remaining_options:
            game._reopen_action_options_menu(
                player,
                pending_action_id="unmortgage_property",
                options=remaining_options,
            )
        return
    paid = game._debit_player_to_bank(mono_player, cost, f"unmortgage:{space.space_id}")
    if paid < cost:
        return
    game.mortgaged_space_ids.remove(resolved_space_id)
    game._broadcast_monopoly_personal(
        mono_player,
        personal_message_id="monopoly-you-property-unmortgaged",
        others_message_id="monopoly-player-property-unmortgaged",
        personal_fallback=f"You unmortgaged {space.name} for {game._format_money(paid)}.",
        others_fallback=f"{mono_player.name} unmortgaged {space.name} for {game._format_money(paid)}.",
        player=mono_player.name,
        property=space.name,
        amount=paid,
    )

    game._sync_cash_scores()
    game._try_resolve_pending_rent_payment(mono_player)
    remaining_options = game._options_for_unmortgage_property(player)
    if remaining_options:
        game._reopen_action_options_menu(
            player,
            pending_action_id="unmortgage_property",
            options=remaining_options,
        )
        return
    game.rebuild_all_menus()


def action_build_house(game: MonopolyGame, player: Player, space_id: str, action_id: str) -> None:
    """Build one house/hotel on an owned eligible street property."""
    _ = action_id
    if game._is_junior_preset():
        return
    mono_player = player  # type: ignore[assignment]
    build_space_ids = game._build_house_space_ids(player)
    resolved_space_id = _resolve_space_selection(
        game,
        player,
        space_id,
        option_builder="_options_for_build_house",
        space_ids=build_space_ids,
    )
    if resolved_space_id is None:
        return
    space = game.active_space_by_id.get(resolved_space_id)
    if not space or not game._is_street_property(space):
        return

    cost = max(0, space.house_cost)
    if game._current_liquid_balance(mono_player) < cost:
        return
    if game.rule_profile.builder_block_required_for_build and mono_player.builder_blocks <= 0:
        return

    if not game._can_raise_building_level(resolved_space_id):
        return
    paid = game._debit_player_to_bank(mono_player, cost, f"build:{space.space_id}")
    if paid < cost:
        return
    new_level = game._building_level(resolved_space_id) + 1
    game._set_building_level(resolved_space_id, new_level)
    if game.rule_profile.builder_block_required_for_build:
        mono_player.builder_blocks -= 1
        game.broadcast_l(
            "monopoly-builder-block-spent",
            player=mono_player.name,
            blocks=mono_player.builder_blocks,
        )
    if new_level >= 5:
        game._broadcast_monopoly_personal(
            mono_player,
            personal_message_id="monopoly-you-house-built-hotel",
            others_message_id="monopoly-player-house-built-hotel",
            personal_fallback=f"You built a hotel on {space.name} for {game._format_money(paid)}.",
            others_fallback=f"{mono_player.name} built a hotel on {space.name} for {game._format_money(paid)}.",
            player=mono_player.name,
            property=space.name,
            amount=paid,
        )
    else:
        game._broadcast_monopoly_personal(
            mono_player,
            personal_message_id="monopoly-you-house-built-house",
            others_message_id="monopoly-player-house-built-house",
            personal_fallback=(
                f"You built a house on {space.name} for {game._format_money(paid)}. It now has {new_level}."
            ),
            others_fallback=(
                f"{mono_player.name} built a house on {space.name} for {game._format_money(paid)}. It now has {new_level}."
            ),
            player=mono_player.name,
            property=space.name,
            amount=paid,
            level=new_level,
        )

    game._sync_cash_scores()
    remaining_options = game._options_for_build_house(player)
    if remaining_options:
        game._reopen_action_options_menu(
            player,
            pending_action_id="build_house",
            options=remaining_options,
        )
        return
    game.rebuild_all_menus()


def action_sell_house(game: MonopolyGame, player: Player, space_id: str, action_id: str) -> None:
    """Sell one house/hotel from an owned eligible street property."""
    _ = action_id
    if game._is_junior_preset():
        return
    mono_player = player  # type: ignore[assignment]
    sell_space_ids = game._sell_house_space_ids(player)
    resolved_space_id = _resolve_space_selection(
        game,
        player,
        space_id,
        option_builder="_options_for_sell_house",
        space_ids=sell_space_ids,
    )
    if resolved_space_id is None:
        return
    space = game.active_space_by_id.get(resolved_space_id)
    if not space or not game._is_street_property(space):
        return

    current_level = game._building_level(resolved_space_id)
    if current_level <= 0:
        return
    if not game._can_lower_building_level(resolved_space_id):
        return

    value = max(0, space.house_cost // 2)
    game._set_building_level(resolved_space_id, current_level - 1)
    new_level = game._building_level(resolved_space_id)
    credited = game._credit_player(mono_player, value, f"sell_building:{space.space_id}")
    game._broadcast_monopoly_personal(
        mono_player,
        personal_message_id="monopoly-you-house-sold",
        others_message_id="monopoly-player-house-sold",
        personal_fallback=(
            f"You sold a building on {space.name} for {game._format_money(credited)} (level: {new_level})."
        ),
        others_fallback=(
            f"{mono_player.name} sold a building on {space.name} for {game._format_money(credited)} (level: {new_level})."
        ),
        player=mono_player.name,
        property=space.name,
        amount=credited,
        level=new_level,
    )

    game._sync_cash_scores()
    game._try_resolve_pending_rent_payment(mono_player)
    if not game._can_manage_assets_now(player):
        game.rebuild_all_menus()
        return
    remaining_options = game._options_for_sell_house(player)
    if remaining_options:
        game._reopen_action_options_menu(
            player,
            pending_action_id="sell_house",
            options=remaining_options,
        )
        return
    game.rebuild_all_menus()


def action_offer_trade(game: MonopolyGame, player: Player, option: str, action_id: str) -> None:
    """Create a pending trade offer for another player."""
    _ = action_id
    if game._is_junior_preset():
        return
    mono_player = player  # type: ignore[assignment]
    if game.pending_trade_offer is not None:
        return
    if option not in game._options_for_offer_trade(player):
        return
    parsed = game._parse_trade_option(option)
    if not parsed:
        return

    target = game.get_player_by_id(parsed.target_id)
    if not target or not isinstance(target, type(mono_player)):
        return
    parsed.proposer_id = mono_player.id
    if not game._is_trade_offer_valid(mono_player, target, parsed):
        return

    game.pending_trade_offer = parsed
    game.broadcast_l(
        "monopoly-trade-offered",
        proposer=mono_player.name,
        target=target.name,
        offer=parsed.summary,
    )

    if target.is_bot:
        if game._bot_accepts_trade_offer(mono_player, target, parsed) and game._apply_trade_offer(
            mono_player, target, parsed
        ):
            game.broadcast_l(
                "monopoly-trade-completed",
                proposer=mono_player.name,
                target=target.name,
                offer=parsed.summary,
            )
            game._try_resolve_pending_rent_payment(mono_player)
            game._try_resolve_pending_rent_payment(target)
        else:
            game.broadcast_l(
                "monopoly-trade-declined",
                proposer=mono_player.name,
                target=target.name,
                offer=parsed.summary,
            )
        game.pending_trade_offer = None

    game._sync_cash_scores()
    game.rebuild_all_menus()


def action_accept_trade(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Accept the currently pending trade for this player."""
    _ = action_id
    if game._is_junior_preset():
        return
    mono_player = player  # type: ignore[assignment]
    offer = game._pending_trade_for_target(mono_player)
    if offer is None:
        return
    proposer = game.get_player_by_id(offer.proposer_id)
    if not proposer or not isinstance(proposer, type(mono_player)):
        game.pending_trade_offer = None
        game.rebuild_all_menus()
        return

    if not game._apply_trade_offer(proposer, mono_player, offer):
        game.broadcast_l(
            "monopoly-trade-cancelled",
            offer=offer.summary,
        )
        game.pending_trade_offer = None
        game._sync_cash_scores()
        game.rebuild_all_menus()
        return

    game.broadcast_l(
        "monopoly-trade-completed",
        proposer=proposer.name,
        target=mono_player.name,
        offer=offer.summary,
    )
    game.pending_trade_offer = None
    game._sync_cash_scores()
    game._try_resolve_pending_rent_payment(proposer)
    game._try_resolve_pending_rent_payment(mono_player)
    game.rebuild_all_menus()


def action_decline_trade(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Decline the currently pending trade for this player."""
    _ = action_id
    if game._is_junior_preset():
        return
    mono_player = player  # type: ignore[assignment]
    offer = game._pending_trade_for_target(mono_player)
    if offer is None:
        return
    proposer = game.get_player_by_id(offer.proposer_id)
    proposer_name = proposer.name if proposer and isinstance(proposer, type(mono_player)) else "Unknown"
    game.broadcast_l(
        "monopoly-trade-declined",
        proposer=proposer_name,
        target=mono_player.name,
        offer=offer.summary,
    )
    game.pending_trade_offer = None
    game.rebuild_all_menus()


def action_pay_bail(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Pay bail to leave jail before rolling."""
    _ = action_id
    mono_player = player  # type: ignore[assignment]
    bail_amount = game._bail_amount()
    if (
        not mono_player.in_jail
        or game.turn_has_rolled
        or game._current_liquid_balance(mono_player) < bail_amount
    ):
        return

    paid = game._debit_player_to_bank(mono_player, bail_amount, "pay_bail")
    if paid < bail_amount:
        return
    mono_player.in_jail = False
    mono_player.jail_turns = 0
    game._broadcast_monopoly_personal(
        mono_player,
        personal_message_id="monopoly-you-bail-paid",
        others_message_id="monopoly-player-bail-paid",
        personal_fallback=f"You paid {game._format_money(paid)} bail.",
        others_fallback=f"{mono_player.name} paid {game._format_money(paid)} bail.",
        player=mono_player.name,
        amount=paid,
    )
    game._apply_sore_loser_rebate(mono_player, paid)

    game._sync_cash_scores()
    game.rebuild_all_menus()


def action_use_jail_card(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Use a get-out-of-jail-free card."""
    _ = action_id
    mono_player = player  # type: ignore[assignment]
    if not mono_player.in_jail or game.turn_has_rolled or mono_player.get_out_of_jail_cards <= 0:
        return

    mono_player.get_out_of_jail_cards -= 1
    held_card = game._pop_held_get_out_of_jail_card(mono_player)
    if held_card is not None:
        deck_type, card_id = held_card
        game._return_get_out_of_jail_card_to_deck(deck_type, card_id)
    mono_player.in_jail = False
    mono_player.jail_turns = 0
    game._broadcast_monopoly_personal(
        mono_player,
        personal_message_id="monopoly-you-jail-card-used",
        others_message_id="monopoly-player-jail-card-used",
        personal_fallback="You used a get-out-of-jail card.",
        others_fallback=f"{mono_player.name} used a get-out-of-jail card.",
        player=mono_player.name,
    )

    game._sync_cash_scores()
    game.rebuild_all_menus()


def action_claim_cheat_reward(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Apply cheaters reward claim outcome for the active player."""
    _ = action_id
    mono_player = player  # type: ignore[assignment]
    if game.cheaters_engine is None or mono_player.bankrupt:
        return
    outcome = game.cheaters_engine.on_action_attempt(
        mono_player.id,
        "claim_cheat_reward",
        context={"turn_has_rolled": game.turn_has_rolled},
    )
    game._apply_cheaters_outcome(
        mono_player,
        outcome,
        reason="reward_claim",
    )
    game.rebuild_all_menus()


def action_end_turn(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Ignore manual end-turn attempts; Monopoly advances automatically."""
    _ = action_id
    _ = player
    game.rebuild_all_menus()


def action_roll_dice(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Handle rolling and landing logic for classic scaffold."""
    _ = action_id
    mono_player = player  # type: ignore[assignment]
    bail_amount = game._bail_amount()

    if game.turn_has_rolled or mono_player.bankrupt or game.turn_pending_purchase_space_id:
        return

    if game._is_junior_super_mario_manual_core_active():
        numbered_die = _game_randint(1, 6)
        power_up_die = _game_randint(1, 6)
        die_1 = numbered_die
        die_2 = power_up_die
        total = numbered_die
        is_doubles = False
        game.turn_last_roll = [die_1, die_2]
    elif game._is_junior_preset() and game.junior_ruleset:
        rolls = [_game_randint(1, 6) for _ in range(game.junior_ruleset.dice_count)]
        die_1 = rolls[0]
        die_2 = rolls[1] if len(rolls) > 1 else 0
        total = sum(rolls)
        is_doubles = len(rolls) > 1 and all(value == rolls[0] for value in rolls)
        game.turn_last_roll = rolls
    else:
        die_1 = _game_randint(1, 6)
        die_2 = _game_randint(1, 6)
        total = die_1 + die_2
        is_doubles = die_1 == die_2
        game.turn_last_roll = [die_1, die_2]

    game.turn_has_rolled = True
    game.turn_pending_purchase_space_id = ""
    game.play_standard_dice_roll_sound()
    if mono_player.in_jail:
        if game._is_junior_super_mario_manual_core_active():
            if mono_player.get_out_of_jail_cards > 0:
                mono_player.get_out_of_jail_cards -= 1
                held_card = game._pop_held_get_out_of_jail_card(mono_player)
                if held_card is not None:
                    deck_type, card_id = held_card
                    game._return_get_out_of_jail_card_to_deck(deck_type, card_id)
                mono_player.in_jail = False
                mono_player.jail_turns = 0
                game._broadcast_monopoly_personal(
                    mono_player,
                    personal_message_id="monopoly-you-jail-card-used",
                    others_message_id="monopoly-player-jail-card-used",
                    personal_fallback="You used a get-out-of-jail card.",
                    others_fallback=f"{mono_player.name} used a get-out-of-jail card.",
                    player=mono_player.name,
                )
            elif game._current_liquid_balance(mono_player) >= 1:
                paid = game._debit_player_to_bank(mono_player, 1, "pay_bail")
                if paid < 1:
                    game.turn_doubles_count = 0
                    game._sync_cash_scores()
                    game._advance_after_roll_resolution(mono_player)
                    return
                mono_player.in_jail = False
                mono_player.jail_turns = 0
                game._broadcast_monopoly_personal(
                    mono_player,
                    personal_message_id="monopoly-you-bail-paid",
                    others_message_id="monopoly-player-bail-paid",
                    personal_fallback=f"You paid {game._format_money(paid)} bail.",
                    others_fallback=f"{mono_player.name} paid {game._format_money(paid)} bail.",
                    player=mono_player.name,
                    amount=paid,
                )
            else:
                game.turn_doubles_count = 0
                game._sync_cash_scores()
                game._advance_after_roll_resolution(mono_player)
                return

            game.turn_doubles_count = 0
            _schedule_monopoly_roll_resolution(
                game,
                mono_player,
                die_1=die_1,
                die_2=die_2,
                total=total,
                is_doubles=False,
                collect_pass_go=False,
                extra_powerup_die=die_2,
            )
            return
        if is_doubles:
            mono_player.in_jail = False
            mono_player.jail_turns = 0
            game._broadcast_jail_roll_doubles(
                mono_player,
                die_1=die_1,
                die_2=die_2,
            )
            _schedule_monopoly_roll_resolution(
                game,
                mono_player,
                die_1=die_1,
                die_2=die_2,
                total=total,
                is_doubles=True,
                collect_pass_go=False,
                roll_message_key=None,
            )
        else:
            mono_player.jail_turns += 1
            game.broadcast_l(
                "monopoly-jail-roll-failed",
                player=mono_player.name,
                die1=die_1,
                die2=die_2,
                attempts=mono_player.jail_turns,
            )
            if mono_player.jail_turns >= 3:
                if game._current_liquid_balance(mono_player) < bail_amount:
                    game._liquidate_assets_for_debt(mono_player, bail_amount)
                if game._current_liquid_balance(mono_player) < bail_amount:
                    game._declare_bankrupt(mono_player)
                    game._sync_cash_scores()
                    game._advance_after_roll_resolution(mono_player)
                    return
                paid = game._debit_player_to_bank(mono_player, bail_amount, "jail_bail")
                if paid < bail_amount:
                    game._declare_bankrupt(mono_player)
                    game._sync_cash_scores()
                    game._advance_after_roll_resolution(mono_player)
                    return
                mono_player.in_jail = False
                mono_player.jail_turns = 0
                game._broadcast_monopoly_personal(
                    mono_player,
                    personal_message_id="monopoly-you-bail-paid",
                    others_message_id="monopoly-player-bail-paid",
                    personal_fallback=f"You paid {game._format_money(paid)} bail.",
                    others_fallback=f"{mono_player.name} paid {game._format_money(paid)} bail.",
                    player=mono_player.name,
                    amount=paid,
                )
                game._apply_sore_loser_rebate(mono_player, paid)
                _schedule_monopoly_roll_resolution(
                    game,
                    mono_player,
                    die_1=die_1,
                    die_2=die_2,
                    total=total,
                    is_doubles=False,
                    collect_pass_go=False,
                    roll_message_key=None,
                )
        game.turn_doubles_count = 0
        if not game.is_animating:
            game._sync_cash_scores()
            game._advance_after_roll_resolution(mono_player)
        return

    if game.rule_profile.doubles_grant_extra_roll and is_doubles:
        game.turn_doubles_count += 1
    else:
        game.turn_doubles_count = 0

    if game.rule_profile.doubles_grant_extra_roll and game.turn_doubles_count >= 3:
        game._broadcast_roll_only(
            mono_player,
            die_1=die_1,
            die_2=die_2,
            total=total,
            is_doubles=is_doubles,
        )
        game._send_to_jail(mono_player, by_triple_doubles=True)
        game._sync_cash_scores()
        game._advance_after_roll_resolution(mono_player)
        return

    _schedule_monopoly_roll_resolution(
        game,
        mono_player,
        die_1=die_1,
        die_2=die_2,
        total=total,
        is_doubles=is_doubles,
        collect_pass_go=True,
        extra_powerup_die=die_2 if game._is_junior_super_mario_manual_core_active() else None,
        allow_doubles_bonus_roll=game.rule_profile.doubles_grant_extra_roll,
    )


def action_buy_property(game: MonopolyGame, player: Player, action_id: str) -> None:
    """Buy currently pending property."""
    _ = action_id
    if game._is_auction_active():
        return
    if not game.rule_profile.allow_manual_property_buy:
        return
    mono_player = player  # type: ignore[assignment]
    space = game._pending_purchase_space()
    if not space:
        return
    if space.space_id in game.property_owners:
        game.turn_pending_purchase_space_id = ""
        game._advance_after_roll_resolution(mono_player)
        return
    if not game._buy_property_for_player(mono_player, space):
        return
    game.turn_pending_purchase_space_id = ""

    if game.turn_can_roll_again:
        game._prepare_next_roll_after_doubles(mono_player)
        game._sync_cash_scores()
        game.rebuild_all_menus()
        return

    game._sync_cash_scores()
    game._advance_after_roll_resolution(mono_player)
