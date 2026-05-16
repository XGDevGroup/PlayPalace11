"""Bot user implementation for AI players."""

from .base import User, MenuItem, EscapeBehavior, generate_uuid


class Bot(User):
    """
    Bot implementation of User for AI players.

    Bots don't receive UI updates (they're discarded), but they can
    call game actions directly through the game's action system.
    """

    def __init__(self, name: str, locale: str = "en", uuid: str | None = None):
        """Initialize a bot with a name, locale, and optional UUID."""
        self._uuid = uuid or generate_uuid()
        self._username = name
        self._locale = locale

    @property
    def uuid(self) -> str:
        """Return the bot's UUID."""
        return self._uuid

    @property
    def username(self) -> str:
        """Return the bot's display name."""
        return self._username

    @property
    def locale(self) -> str:
        """Return the bot's locale."""
        return self._locale

    @property
    def is_bot(self) -> bool:
        """Bots always report True for is_bot."""
        return True

    @property
    def client_type(self) -> str:
        """Return the bot's client type."""
        return getattr(self, "_client_type", "")

    def set_client_type(self, client_type: str) -> None:
        """Set the bot's client type."""
        self._client_type = client_type

    def speak(self, text: str, buffer: str = "misc") -> None:
        """No-op: bots do not receive speech."""
        pass

    def play_sound(self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100) -> None:
        """No-op: bots do not play sounds."""
        pass

    def play_music(self, name: str, looping: bool = True) -> None:
        """No-op: bots do not play music."""
        pass

    def stop_music(self) -> None:
        """No-op: bots do not stop music."""
        pass

    def play_ambience(self, loop: str, intro: str = "", outro: str = "") -> None:
        """No-op: bots do not play ambience."""
        pass

    def stop_ambience(self) -> None:
        """No-op: bots do not stop ambience."""
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
        """No-op: bots do not render menus."""
        pass

    def update_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        position: int | None = None,
        selection_id: str | None = None,
        play_selection_sound: bool = False,
    ) -> None:
        """No-op: bots do not update menus."""
        pass

    def remove_menu(self, menu_id: str) -> None:
        """No-op: bots do not remove menus."""
        pass

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
        """No-op: bots do not show edit boxes."""
        pass

    def remove_editbox(self, input_id: str) -> None:
        """No-op: bots do not remove edit boxes."""
        pass

    def clear_ui(self) -> None:
        """No-op: bots do not clear UI."""
        pass
