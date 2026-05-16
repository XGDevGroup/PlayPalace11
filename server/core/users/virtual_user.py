"""Virtual user implementation for server-level virtual bots."""

from typing import TYPE_CHECKING

from .base import User, MenuItem, EscapeBehavior, TrustLevel, generate_virtual_bot_uuid

if TYPE_CHECKING:
    pass


class VirtualUser(User):
    """
    Virtual user implementation for server-level virtual bots.

    Unlike regular Bots which are added to games, VirtualUsers simulate
    real users - they navigate menus, create/join games, and go online/offline.
    They track menu state to make decisions about what to do.
    """

    def __init__(self, name: str, locale: str = "en", uuid: str | None = None):
        """Initialize a virtual bot user with deterministic UUID."""
        # Use deterministic UUID based on name so stats persist across restarts
        self._uuid = uuid or generate_virtual_bot_uuid(name)
        self._username = name
        self._locale = locale

        # Menu state tracking for decision-making
        self._current_menu_id: str | None = None
        self._current_menu_items: list[str | MenuItem] = []

    @property
    def uuid(self) -> str:
        """Return the virtual bot UUID."""
        return self._uuid

    @property
    def username(self) -> str:
        """Return the virtual bot name."""
        return self._username

    @property
    def locale(self) -> str:
        """Return the virtual bot locale."""
        return self._locale

    @property
    def is_bot(self) -> bool:
        """Indicates this is a bot user (for game player creation)."""
        return True

    @property
    def is_virtual_bot(self) -> bool:
        """Indicates this is a virtual bot user (server-level bot)."""
        return True

    @property
    def approved(self) -> bool:
        """Virtual bots are always approved."""
        return True

    @property
    def trust_level(self) -> TrustLevel:
        """Virtual bots have normal user trust level."""
        return TrustLevel.USER

    @property
    def current_menu_id(self) -> str | None:
        """The ID of the current menu being shown."""
        return self._current_menu_id

    @property
    def current_menu_items(self) -> list[str | MenuItem]:
        """The items in the current menu."""
        return self._current_menu_items

    # UI methods track state but don't send anything

    def speak(self, text: str, buffer: str = "misc") -> None:
        """No-op: virtual bots do not receive speech."""
        pass

    def play_sound(self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100) -> None:
        """No-op: virtual bots do not play sounds."""
        pass

    def play_music(self, name: str, looping: bool = True) -> None:
        """No-op: virtual bots do not play music."""
        pass

    def stop_music(self) -> None:
        """No-op: virtual bots do not stop music."""
        pass

    def play_ambience(self, loop: str, intro: str = "", outro: str = "") -> None:
        """No-op: virtual bots do not play ambience."""
        pass

    def stop_ambience(self) -> None:
        """No-op: virtual bots do not stop ambience."""
        pass

    def show_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        *,
        multiletter: bool = True,
        escape_behavior: EscapeBehavior = EscapeBehavior.KEYBIND,
        position: int | None = None,
        grid_enabled: bool = False,
        grid_width: int = 1,
        play_selection_sound: bool = False,
    ) -> None:
        """Track menu state for decision-making."""
        self._current_menu_id = menu_id
        self._current_menu_items = items

    def update_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        position: int | None = None,
        selection_id: str | None = None,
        play_selection_sound: bool = False,
    ) -> None:
        """Track menu updates."""
        if menu_id == self._current_menu_id:
            self._current_menu_items = items

    def remove_menu(self, menu_id: str) -> None:
        """Track menu removal."""
        if menu_id == self._current_menu_id:
            self._current_menu_id = None
            self._current_menu_items = []

    def show_editbox(
        self,
        input_id: str,
        prompt: str,
        default_value: str = "",
        *,
        multiline: bool = False,
        read_only: bool = False,
        content_format: str = "text",
    ) -> None:
        """No-op: virtual bots ignore editboxes."""
        pass

    def remove_editbox(self, input_id: str) -> None:
        """No-op: virtual bots ignore editboxes."""
        pass

    def clear_ui(self) -> None:
        """Clear menu state."""
        self._current_menu_id = None
        self._current_menu_items = []

    def get_queued_messages(self) -> list:
        """Virtual users have no queued messages to send."""
        return []
