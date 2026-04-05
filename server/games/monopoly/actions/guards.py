"""Guard helpers for Monopoly turn actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ....game_utils.actions import Visibility
from ...base import Player

if TYPE_CHECKING:
    from ..game import MonopolyGame


def is_banking_balance_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable bank balance checks only for electronic banking preset."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    if game.turn_has_rolled:
        return "monopoly-already-rolled"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if not game._is_electronic_banking_preset() or game.banking_state is None:
        return "monopoly-action-disabled-for-preset"
    return None


def is_banking_balance_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show bank balance action only in electronic banking mode."""
    return game.turn_action_visibility(
        player,
        extra_condition=game._is_electronic_banking_preset() and not game.turn_has_rolled,
    )


def is_banking_transfer_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable manual transfer only when options are available."""
    error = is_banking_balance_enabled(game, player)
    if error:
        return error
    if not game._options_for_banking_transfer(player):
        return "monopoly-not-enough-cash"
    return None


def is_banking_transfer_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show transfer action only when electronic transfer options exist."""
    return game.turn_action_visibility(
        player,
        extra_condition=not game.turn_has_rolled
        and game._is_electronic_banking_preset()
        and bool(game._options_for_banking_transfer(player)),
    )


def is_banking_ledger_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable ledger announcements in electronic banking mode."""
    return is_banking_balance_enabled(game, player)


def is_banking_ledger_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show ledger action only in electronic banking mode."""
    return game.turn_action_visibility(
        player,
        extra_condition=game._is_electronic_banking_preset() and not game.turn_has_rolled,
    )


def is_voice_command_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable voice command entry only for voice banking preset."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if game.active_preset_id != "voice_banking":
        return "monopoly-action-disabled-for-preset"
    return None


def is_voice_command_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show voice command entry only during voice banking games."""
    return game.turn_action_visibility(
        player,
        extra_condition=game.active_preset_id == "voice_banking" and not game.turn_has_rolled,
    )


def is_auction_property_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable auction action for pending unpurchased property."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    if game._is_auction_active():
        return "monopoly-auction-active"
    if not game.turn_has_rolled:
        return "monopoly-roll-first"
    if game._pending_purchase_space() is None:
        return "monopoly-no-property-to-auction"
    return None


def is_auction_property_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show auction only when property purchase is pending."""
    return game.turn_action_visibility(
        player,
        extra_condition=not game._is_auction_active()
        and game.turn_has_rolled
        and game._pending_purchase_space() is not None,
    )


def is_auction_bid_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable placing a bid when it is this player's auction turn."""
    error = game.guard_turn_action_enabled(player, require_current_player=False)
    if error:
        return error
    if not game._is_auction_active():
        return "monopoly-no-auction-active"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    current_bidder = game._current_auction_bidder()
    if current_bidder is None or current_bidder.id != mono_player.id:
        return "monopoly-not-your-auction-turn"
    if not game._options_for_auction_bid(player):
        return "monopoly-not-enough-cash"
    return None


def is_auction_bid_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show bid action only to the active non-bankrupt auction bidder."""
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return Visibility.HIDDEN
    current_bidder = game._current_auction_bidder()
    return game.turn_action_visibility(
        player,
        require_current_player=False,
        extra_condition=game._is_auction_active()
        and current_bidder is not None
        and current_bidder.id == player.id,
    )


def is_auction_pass_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable passing in an active interactive auction."""
    error = game.guard_turn_action_enabled(player, require_current_player=False)
    if error:
        return error
    if not game._is_auction_active():
        return "monopoly-no-auction-active"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    current_bidder = game._current_auction_bidder()
    if current_bidder is None or current_bidder.id != mono_player.id:
        return "monopoly-not-your-auction-turn"
    return None


def is_auction_pass_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show pass action only to the active non-bankrupt auction bidder."""
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return Visibility.HIDDEN
    current_bidder = game._current_auction_bidder()
    return game.turn_action_visibility(
        player,
        require_current_player=False,
        extra_condition=game._is_auction_active()
        and current_bidder is not None
        and current_bidder.id == player.id,
    )


def is_mortgage_property_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable mortgage action when player owns eligible properties."""
    error = game.guard_turn_action_enabled(
        player,
        require_current_player=not game._is_auction_active(),
    )
    if error:
        return error
    if not game._can_manage_assets_now(player):
        return "monopoly-not-your-auction-turn" if game._is_auction_active() else "action-not-your-turn"
    if (
        game.turn_has_rolled
        and not game.turn_pending_purchase_space_id
        and not game._has_pending_rent_payment(player)  # type: ignore[arg-type]
        and not game._is_auction_active()
    ):
        return "monopoly-already-rolled"
    if game._is_junior_preset():
        return "monopoly-action-disabled-for-preset"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if not game._options_for_mortgage_property(player):
        return "monopoly-no-mortgage-options"
    return None


def is_mortgage_property_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show mortgage action when options exist."""
    if game._is_junior_preset():
        return Visibility.HIDDEN
    return game.turn_action_visibility(
        player,
        require_current_player=not game._is_auction_active(),
        extra_condition=(
            game._can_manage_assets_now(player)
            and (
                not game.turn_has_rolled
                or bool(game.turn_pending_purchase_space_id)
                or game._has_pending_rent_payment(player)  # type: ignore[arg-type]
                or game._is_auction_active()
            )
            and bool(game._options_for_mortgage_property(player))
        ),
    )


def is_unmortgage_property_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable unmortgage action when player has mortgaged properties."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    if game.turn_has_rolled and not game.turn_pending_purchase_space_id:
        return "monopoly-already-rolled"
    if game._is_junior_preset():
        return "monopoly-action-disabled-for-preset"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if not game._options_for_unmortgage_property(player):
        return "monopoly-no-unmortgage-options"
    return None


def is_unmortgage_property_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show unmortgage action only when options exist."""
    if game._is_junior_preset():
        return Visibility.HIDDEN
    return game.turn_action_visibility(
        player,
        extra_condition=(
            (not game.turn_has_rolled or bool(game.turn_pending_purchase_space_id))
            and bool(game._options_for_unmortgage_property(player))
        ),
    )


def is_build_house_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable house-building when at least one valid build exists."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    if game.turn_has_rolled:
        return "monopoly-already-rolled"
    if game._is_junior_preset():
        return "monopoly-action-disabled-for-preset"
    if game.turn_pending_purchase_space_id:
        return "monopoly-resolve-property-first"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if not game._options_for_build_house(player):
        return "monopoly-no-build-options"
    return None


def is_build_house_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show build action when options exist."""
    if game._is_junior_preset():
        return Visibility.HIDDEN
    return game.turn_action_visibility(
        player, extra_condition=not game.turn_has_rolled and bool(game._options_for_build_house(player))
    )


def is_sell_house_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable house selling when at least one valid sell exists."""
    error = game.guard_turn_action_enabled(
        player,
        require_current_player=not game._is_auction_active(),
    )
    if error:
        return error
    if not game._can_manage_assets_now(player):
        return "monopoly-not-your-auction-turn" if game._is_auction_active() else "action-not-your-turn"
    if game.turn_has_rolled and not game._has_pending_rent_payment(player) and not game._is_auction_active():  # type: ignore[arg-type]
        return "monopoly-already-rolled"
    if game._is_junior_preset():
        return "monopoly-action-disabled-for-preset"
    if game.turn_pending_purchase_space_id and not game._has_pending_rent_payment(player):  # type: ignore[arg-type]
        return "monopoly-resolve-property-first"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if not game._options_for_sell_house(player):
        return "monopoly-no-sell-options"
    return None


def is_sell_house_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show sell action when options exist."""
    if game._is_junior_preset():
        return Visibility.HIDDEN
    return game.turn_action_visibility(
        player,
        require_current_player=not game._is_auction_active(),
        extra_condition=game._can_manage_assets_now(player)
        and (
            not game.turn_has_rolled
            or game._has_pending_rent_payment(player)  # type: ignore[arg-type]
            or game._is_auction_active()
        )
        and bool(game._options_for_sell_house(player)),
    )


def is_offer_trade_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable trade offers for active players with at least one valid option."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    if game.turn_has_rolled and not game._has_pending_rent_payment(player):  # type: ignore[arg-type]
        return "monopoly-already-rolled"
    if game._is_junior_preset():
        return "monopoly-action-disabled-for-preset"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if game.turn_pending_purchase_space_id:
        return "monopoly-resolve-property-first"
    if game.pending_trade_offer is not None:
        return "monopoly-trade-pending"
    if not game._options_for_offer_trade(player):
        return "monopoly-no-trade-options"
    return None


def is_offer_trade_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show offer-trade when player can open a new trade."""
    if game._is_junior_preset():
        return Visibility.HIDDEN
    return game.turn_action_visibility(
        player,
        extra_condition=(not game.turn_has_rolled or game._has_pending_rent_payment(player))  # type: ignore[arg-type]
        and game.pending_trade_offer is None
        and bool(game._options_for_offer_trade(player)),
    )


def is_accept_trade_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable accepting a pending trade for the addressed target player."""
    error = game.guard_turn_action_enabled(player, require_current_player=False)
    if error:
        return error
    if game._is_junior_preset():
        return "monopoly-action-disabled-for-preset"
    if game.turn_pending_purchase_space_id:
        return "monopoly-resolve-property-first"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if game._pending_trade_for_target(mono_player) is None:
        return "monopoly-no-trade-pending"
    return None


def is_accept_trade_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show accept-trade only to the targeted non-bankrupt player."""
    if game._is_junior_preset():
        return Visibility.HIDDEN
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return Visibility.HIDDEN
    return game.turn_action_visibility(
        player,
        require_current_player=False,
        extra_condition=game._pending_trade_for_target(mono_player) is not None,
    )


def is_decline_trade_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable declining a pending trade for the addressed target player."""
    error = game.guard_turn_action_enabled(player, require_current_player=False)
    if error:
        return error
    if game._is_junior_preset():
        return "monopoly-action-disabled-for-preset"
    if game.turn_pending_purchase_space_id:
        return "monopoly-resolve-property-first"
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if game._pending_trade_for_target(mono_player) is None:
        return "monopoly-no-trade-pending"
    return None


def is_decline_trade_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show decline-trade only to the targeted non-bankrupt player."""
    if game._is_junior_preset():
        return Visibility.HIDDEN
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return Visibility.HIDDEN
    return game.turn_action_visibility(
        player,
        require_current_player=False,
        extra_condition=game._pending_trade_for_target(mono_player) is not None,
    )


def is_pay_bail_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable paying bail while in jail before rolling."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    mono_player = player  # type: ignore[assignment]
    if not mono_player.in_jail:
        return "monopoly-not-in-jail"
    if game.turn_has_rolled:
        return "monopoly-already-rolled"
    if game._current_liquid_balance(mono_player) < game._bail_amount():
        return "monopoly-not-enough-cash"
    return None


def is_pay_bail_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show pay bail only while player is jailed and has not rolled."""
    mono_player = player  # type: ignore[assignment]
    return game.turn_action_visibility(
        player,
        extra_condition=mono_player.in_jail and not game.turn_has_rolled,
    )


def is_use_jail_card_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable jail-card use while in jail before rolling."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    mono_player = player  # type: ignore[assignment]
    if not mono_player.in_jail:
        return "monopoly-not-in-jail"
    if game.turn_has_rolled:
        return "monopoly-already-rolled"
    if mono_player.get_out_of_jail_cards <= 0:
        return "monopoly-no-jail-card"
    return None


def is_use_jail_card_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show jail-card action only while usable."""
    mono_player = player  # type: ignore[assignment]
    return game.turn_action_visibility(
        player,
        extra_condition=mono_player.in_jail
        and not game.turn_has_rolled
        and mono_player.get_out_of_jail_cards > 0,
    )


def is_claim_cheat_reward_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable reward claim action only during cheaters preset turns."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if game.active_preset_id != "cheaters" or game.cheaters_engine is None:
        return "monopoly-action-disabled-for-preset"
    return None


def is_claim_cheat_reward_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show reward claim only while the cheaters engine is active."""
    return game.turn_action_visibility(
        player,
        extra_condition=game.active_preset_id == "cheaters" and game.cheaters_engine is not None,
    )


def is_end_turn_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Keep manual end-turn disabled; Monopoly advances automatically."""
    _ = game
    _ = player
    return "action-disabled"


def is_end_turn_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Never expose manual end-turn in Monopoly."""
    _ = game
    _ = player
    return Visibility.HIDDEN


def is_roll_dice_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable roll action for active player before rolling."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    mono_player = player  # type: ignore[assignment]
    if mono_player.bankrupt:
        return "monopoly-bankrupt-player"
    if game.turn_pending_purchase_space_id:
        return "monopoly-resolve-property-first"
    if game.turn_has_rolled:
        return "monopoly-already-rolled"
    return None


def is_roll_dice_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Hide roll once a roll has been made this turn."""
    return game.turn_action_visibility(
        player,
        extra_condition=not game.turn_has_rolled and not game.turn_pending_purchase_space_id,
    )


def is_buy_property_enabled(game: MonopolyGame, player: Player) -> str | None:
    """Enable buy action when current player can buy landed property."""
    error = game.guard_turn_action_enabled(player)
    if error:
        return error
    if game._is_auction_active():
        return "monopoly-auction-active"
    if not game.rule_profile.allow_manual_property_buy:
        return "monopoly-buy-disabled"
    if not game.turn_has_rolled:
        return "monopoly-roll-first"
    mono_player = player  # type: ignore[assignment]
    space = game._pending_purchase_space()
    if not space:
        return "monopoly-no-property-to-buy"
    if space.space_id in game.property_owners:
        return "monopoly-property-owned"
    if game._current_liquid_balance(mono_player) < space.price:
        return "monopoly-not-enough-cash"
    return None


def is_buy_property_hidden(game: MonopolyGame, player: Player) -> Visibility:
    """Show buy action only after a roll when a property is pending."""
    return game.turn_action_visibility(
        player,
        extra_condition=game.rule_profile.allow_manual_property_buy
        and not game._is_auction_active()
        and game.turn_has_rolled
        and game._pending_purchase_space() is not None,
    )
