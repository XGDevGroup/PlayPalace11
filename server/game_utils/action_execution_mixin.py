"""Mixin providing action execution for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player, ActionContext

from .actions import Action, MenuInput, EditboxInput
from .options import get_option_meta, MenuOption
from server.core.users.base import MenuItem, EscapeBehavior
from ..messages.localization import Localization


class ActionExecutionMixin:
    """Execute actions, resolve input, and dispatch handlers.

    This mixin coordinates action execution for both menu selections and
    keybind-triggered actions, including bot inputs and input prompts.

    Expected Game attributes:
        _pending_actions: dict[str, str] mapping player_id -> action_id.
        _action_context: dict[str, ActionContext] for keybind context.
        get_user(player) -> User | None.
        find_action(player, action_id) -> Action | None.
        resolve_action(player, action) -> ResolvedAction.
        advance_turn().
    """

    def execute_action(
        self,
        player: "Player",
        action_id: str,
        input_value: str | None = None,
        context: "ActionContext | None" = None,
    ) -> None:
        """Execute an action for a player, optionally with input value and context."""
        action = self.find_action(player, action_id)
        if not action:
            return

        # Check if action is enabled using declarative callback
        resolved = self.resolve_action(player, action)
        if not resolved.enabled:
            # Use custom disabled_message if set, otherwise speak the reason.
            user = self.get_user(player)
            if user:
                if action.disabled_message:
                    user.speak_l(action.disabled_message)
                else:
                    reason = resolved.disabled_reason
                    if reason and reason != "action-not-available":
                        if isinstance(reason, tuple):
                            user.speak_l(reason[0], **reason[1])
                        else:
                            user.speak_l(reason)
            return

        # If action requires input and we don't have it yet
        if action.input_request is not None and input_value is None:
            # For bots, get input automatically
            if player.is_bot:
                # Set pending action so options methods can access action_id
                self._pending_actions[player.id] = action_id
                input_value = self._get_bot_input(action, player)
                # Clean up pending action for bot
                if player.id in self._pending_actions:
                    del self._pending_actions[player.id]
                if input_value is None:
                    return  # Bot couldn't provide input
            else:
                # For humans, request input and store pending action
                self._request_action_input(action, player)
                return

        # Look up the handler method by name on this game object
        handler = getattr(self, action.handler, None)
        if not handler:
            return

        # Import here to avoid circular dependency at module level
        from ..games.base import ActionContext as AC

        # Store context for handlers that need it (e.g., keybind-triggered actions)
        self._action_context[player.id] = context or AC()

        try:
            # Execute the action handler (always pass action_id for context)
            if action.input_request is not None and input_value is not None:
                # Handler expects input value: (player, input_value, action_id)
                handler(player, input_value, action_id)
            else:
                # Handler doesn't expect input: (player, action_id)
                handler(player, action_id)
        finally:
            # Clean up context
            self._action_context.pop(player.id, None)

    def get_action_context(self, player: "Player") -> "ActionContext":
        """Get the current action context for a player (for use in handlers)."""
        # Import here to avoid circular dependency at module level
        from ..games.base import ActionContext

        return self._action_context.get(player.id, ActionContext())

    def _get_menu_options_for_action(self, action: Action, player: "Player") -> list[str] | None:
        """Get menu options for an action, checking method first then MenuOption metadata."""
        req = action.input_request
        if not isinstance(req, MenuInput):
            return None

        # First try the method name
        options_method = getattr(self, req.options, None)
        if options_method:
            return options_method(player)

        # Fallback: check if this is a set_* action for a MenuOption
        if action.id.startswith("set_") and hasattr(self, "options"):
            option_name = action.id[4:]  # Remove "set_" prefix
            meta = get_option_meta(type(self.options), option_name)
            if meta and isinstance(meta, MenuOption):
                choices = meta.choices
                # Choices can be a list or a callable
                if callable(choices):
                    return choices(self, player)
                return list(choices)

        return None

    def _get_bot_input(self, action: Action, player: "Player") -> str | None:
        """Get automatic input for a bot player."""
        req = action.input_request
        if isinstance(req, MenuInput):
            options = self._get_menu_options_for_action(action, player)
            if not options:
                return None
            if req.bot_select:
                # Look up bot_select method by name
                bot_select_method = getattr(self, req.bot_select, None)
                if bot_select_method:
                    return bot_select_method(player, options)
            # Default: pick first option
            return options[0]
        elif isinstance(req, EditboxInput):
            if req.bot_input:
                # Look up bot_input method by name
                bot_input_method = getattr(self, req.bot_input, None)
                if bot_input_method:
                    return bot_input_method(player)
            # Default: use default value
            return req.default
        return None

    def _request_action_input(self, action: Action, player: "Player") -> None:
        """Request input from a human player for an action."""
        user = self.get_user(player)
        if not user:
            return

        req = action.input_request
        self._pending_actions[player.id] = action.id

        if isinstance(req, MenuInput):
            options = self._get_menu_options_for_action(action, player)
            if not options:
                # No options available
                del self._pending_actions[player.id]
                user.speak_l("no-options-available")
                return

            # Check if this is a MenuOption with localized choice labels
            menu_option_meta = None
            if action.id.startswith("set_") and hasattr(self, "options"):
                option_name = action.id[4:]  # Remove "set_" prefix
                meta = get_option_meta(type(self.options), option_name)
                if meta and isinstance(meta, MenuOption):
                    menu_option_meta = meta

            # Build menu items with localized labels if available
            items = []
            for opt in options:
                if menu_option_meta:
                    display_text = menu_option_meta.get_localized_choice(opt, user.locale)
                elif getattr(self, "_menu_options_encode_ids", False) and "|" in opt:
                    # Opt-in convention: options are encoded "value|label" so a
                    # stable id can be carried as the selection value without
                    # being shown. Display only the human-readable label half.
                    display_text = opt.split("|", 1)[1]
                else:
                    display_text = opt
                items.append(MenuItem(text=display_text, id=opt))

            if req.include_cancel:
                items.append(MenuItem(text=Localization.get(user.locale, "cancel"), id="_cancel"))
            user.show_menu(
                "action_input_menu",
                items,
                multiletter=True,
                escape_behavior=EscapeBehavior.SELECT_LAST,
            )

        elif isinstance(req, EditboxInput):
            # Show editbox for text input
            prompt = Localization.get(user.locale, req.prompt)
            user.show_editbox("action_input_editbox", prompt, req.default)

    def end_turn(self) -> None:
        """End the current player's turn. Call this from action handlers."""
        self.advance_turn()
