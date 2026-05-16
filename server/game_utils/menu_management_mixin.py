"""Mixin providing menu management functionality for games."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Player, TransientDisplayState
    from server.core.users.base import User
    from .actions import ResolvedAction

from server.core.users.base import MenuItem, EscapeBehavior
from ..messages.localization import Localization

TRANSIENT_DISPLAY_MENU_ID = "transient_display"


class MenuManagementMixin:
    """Build and update turn menus and status boxes.

    Expected Game attributes:
        _destroyed: bool.
        status: str.
        players: list[Player].
        _transient_display_state: dict[str, TransientDisplayState].
        get_user(player) -> User | None.
        get_all_visible_actions(player) -> list[ResolvedAction].
    """

    def _build_action_menu_items(self, player: "Player", user: "User") -> list[MenuItem]:
        """Build menu items from visible actions for a player."""
        items: list[MenuItem] = []
        for resolved in self.get_all_visible_actions(player):
            label = resolved.label
            if not resolved.enabled and resolved.action.show_disabled_label:
                unavailable = Localization.get(user.locale, "visibility-unavailable")
                label = f"{label}; {unavailable}"
            items.append(MenuItem(text=label, id=resolved.action.id, sound=resolved.sound))
        return items

    def _get_transient_display_state(self, player: "Player") -> "TransientDisplayState | None":
        """Return the open transient display state for a player, if any."""
        return self._transient_display_state.get(player.id)

    def _is_transient_display_open(self, player: "Player") -> bool:
        """Return True when a transient display is open for a player."""
        return player.id in self._transient_display_state

    def _show_transient_display(
        self,
        player: "Player",
        *,
        kind: str,
        items: list[MenuItem],
        multiletter: bool,
        path: list[str] | None = None,
        position: int | None = None,
    ) -> None:
        """Show a transient display menu and store its runtime state."""
        user = self.get_user(player)
        if not user:
            return

        from ..games.base import TransientDisplayState

        existing_state = self._transient_display_state.get(player.id)
        positions = existing_state.positions if existing_state else {}
        self._transient_display_state[player.id] = TransientDisplayState(
            kind=kind,
            path=list(path or []),
            positions=positions,
        )
        user.show_menu(
            TRANSIENT_DISPLAY_MENU_ID,
            items,
            multiletter=multiletter,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=position,
        )

    def _close_transient_display(
        self,
        player: "Player",
        *,
        speak_key: str | None = None,
        rebuild_menu: bool = True,
    ) -> None:
        """Close a transient display and optionally rebuild the turn menu."""
        user = self.get_user(player)
        if user:
            user.remove_menu(TRANSIENT_DISPLAY_MENU_ID)
            if speak_key:
                user.speak_l(speak_key)
        self._transient_display_state.pop(player.id, None)
        if rebuild_menu:
            self.rebuild_player_menu(player)

    def _handle_transient_display_selection(self, player: "Player", selection_id: str) -> None:
        """Handle a selection from the shared transient display menu."""
        state = self._get_transient_display_state(player)
        if not state:
            return

        if state.kind == "status_box":
            self._close_transient_display(player)
            return

        if state.kind == "game_options":
            handler = getattr(self, "_handle_game_options_display_selection", None)
            if handler:
                handler(player, selection_id)

    def _remember_transient_display_position(self, player: "Player", event: dict) -> None:
        """Remember the user's current position within an open transient display."""
        state = self._get_transient_display_state(player)
        if not state:
            return

        current_path_key = tuple(state.path)
        selection = event.get("selection")
        if isinstance(selection, int) and selection > 0:
            state.positions[current_path_key] = selection
            return

        selection_id = event.get("selection_id")
        if not selection_id:
            return

        user = self.get_user(player)
        if not user:
            return

        current_menus = getattr(user, "_current_menus", None)
        if isinstance(current_menus, dict):
            current_menu = current_menus.get(TRANSIENT_DISPLAY_MENU_ID)
        else:
            menus = getattr(user, "menus", None)
            current_menu = menus.get(TRANSIENT_DISPLAY_MENU_ID) if isinstance(menus, dict) else None
        if not isinstance(current_menu, dict):
            return

        items = current_menu.get("items", [])
        for index, item in enumerate(items, start=1):
            if isinstance(item, dict) and item.get("id") == selection_id:
                state.positions[current_path_key] = index
                return
            if hasattr(item, "id") and getattr(item, "id", None) == selection_id:
                state.positions[current_path_key] = index
                return

    def rebuild_player_menu(self, player: "Player", *, position: int | None = None) -> None:
        """Rebuild the turn menu for a player.

        Args:
            player: The player whose menu to rebuild.
            position: Optional 1-based position to focus on. Use position=1
                to reset focus to the first item. When None, the client
                preserves focus on the previously selected item by ID. This
                causes a stuck-cursor bug when an always-visible action (like
                "view pipe") shifts position as turn actions appear/disappear.
                Pass position=1 in _start_turn for the current player to avoid
                this.
        """
        if self._destroyed:
            return
        if self.status == "finished":
            return
        if self._is_transient_display_open(player):
            return
        user = self.get_user(player)
        if not user:
            return

        items = self._build_action_menu_items(player, user)
        user.show_menu(
            "turn_menu",
            items,
            multiletter=False,
            escape_behavior=EscapeBehavior.KEYBIND,
            position=position,
        )

    def rebuild_all_menus(self) -> None:
        """Rebuild menus for all players."""
        if self._destroyed:
            return
        for player in self.players:
            self.rebuild_player_menu(player)

    def update_player_menu(
        self,
        player: "Player",
        selection_id: str | None = None,
        play_selection_sound: bool = False,
    ) -> None:
        """Update the turn menu for a player, preserving focus position."""
        if self._destroyed:
            return
        if self.status == "finished":
            return
        if self._is_transient_display_open(player):
            return
        user = self.get_user(player)
        if not user:
            return

        items = self._build_action_menu_items(player, user)
        user.update_menu(
            "turn_menu", items, selection_id=selection_id, play_selection_sound=play_selection_sound
        )

    def update_all_menus(self) -> None:
        """Update menus for all players, preserving focus position."""
        if self._destroyed:
            return
        for player in self.players:
            self.update_player_menu(player)

    def status_box(self, player: "Player", lines: list[str]) -> None:
        """Show a status box (menu with text items) to a player.

        Press Enter on any item to close. No header or close button needed
        since screen readers speak list items and Enter always closes.
        """
        items = [MenuItem(text=line, id="status_line") for line in lines]
        self._show_transient_display(
            player,
            kind="status_box",
            items=items,
            multiletter=False,
        )
