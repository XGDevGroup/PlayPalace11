"""Abstract User class that games interact with."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any
import uuid as uuid_module

from ...messages.localization import Localization

if TYPE_CHECKING:
    from .preferences import UserPreferences


class EscapeBehavior(Enum):
    """How the escape key behaves in menus."""

    KEYBIND = "keybind"  # Sent as keybind event (ignored if no handler)
    SELECT_LAST = "select_last_option"  # Auto-selects the last menu item
    ESCAPE_EVENT = "escape_event"  # Sends explicit escape event to server


class TrustLevel(Enum):
    """User trust level for permission checks."""

    BANNED = 0  # Banned user
    USER = 1  # Normal user
    ADMIN = 2  # Administrator
    SERVER_OWNER = 3  # Server owner (highest privilege)


@dataclass
class MenuItem:
    """A menu item with text and optional ID."""

    text: str
    id: str | None = None
    sound: str | None = None

    def to_dict(self) -> dict[str, Any] | str:
        """Serialize menu item to a dict or string for client payloads."""
        if self.id is not None or self.sound is not None:
            data = {"text": self.text}
            if self.id is not None:
                data["id"] = self.id
            if self.sound is not None:
                data["sound"] = self.sound
            return data
        return self.text


class User(ABC):
    """
    Abstract base class for users.

    Games interact with this interface, never with network code directly.
    Implementations include NetworkUser (real players), TestUser (for testing),
    and Bot (AI players).
    """

    @property
    @abstractmethod
    def uuid(self) -> str:
        """The user's unique identifier (UUID string)."""
        ...

    @property
    @abstractmethod
    def username(self) -> str:
        """The user's display name."""
        ...

    @property
    @abstractmethod
    def locale(self) -> str:
        """The user's locale for localization (e.g., 'en', 'es')."""
        ...

    @property
    def is_bot(self) -> bool:
        """Whether this user is a bot. Overridden by Bot subclass."""
        return False

    @property
    def trust_level(self) -> TrustLevel:
        """The user's trust level. Defaults to USER if not overridden."""
        return TrustLevel.USER

    @property
    def preferences(self) -> "UserPreferences":
        """The user's preferences. Returns defaults if not overridden."""
        from .preferences import UserPreferences

        return UserPreferences()

    @abstractmethod
    def speak(self, text: str, buffer: str = "misc") -> None:
        """
        Send a text message to be displayed and spoken via TTS.

        Args:
            text: The message text.
            buffer: Which buffer to route the message to (misc, activity, chats).
        """
        ...

    def speak_l(self, message_id: str, buffer: str = "misc", **kwargs) -> None:
        """
        Send a localized message to be displayed and spoken via TTS.

        Args:
            message_id: The message ID from the .ftl file.
            buffer: Which buffer to route the message to (misc, activity, chats).
            **kwargs: Variables to substitute into the message.
        """
        text = Localization.get(self.locale, message_id, **kwargs)
        self.speak(text, buffer)

    @abstractmethod
    def play_sound(self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100) -> None:
        """
        Play a sound effect.

        Args:
            name: Sound filename.
            volume: Volume 0-100.
            pan: Pan -100 to 100.
            pitch: Pitch 0-200, where 100 is normal.
        """
        ...

    @abstractmethod
    def play_music(self, name: str, looping: bool = True) -> None:
        """
        Play background music.

        Args:
            name: Music filename.
            looping: Whether to loop the music.
        """
        ...

    @abstractmethod
    def stop_music(self) -> None:
        """Stop background music."""
        ...

    @abstractmethod
    def play_ambience(self, loop: str, intro: str = "", outro: str = "") -> None:
        """
        Play ambient background sound.

        Args:
            loop: Looping ambient sound filename.
            intro: Optional intro sound played once before loop.
            outro: Optional outro sound played when stopping.
        """
        ...

    @abstractmethod
    def stop_ambience(self) -> None:
        """Stop ambient background sound."""
        ...

    @abstractmethod
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
        """
        Display a menu to the user.

        Args:
            menu_id: String identifier for this menu.
            items: List of menu items (strings or MenuItem objects).
            multiletter: Enable type-to-search navigation.
            escape_behavior: How escape key behaves (see EscapeBehavior enum).
            position: 1-based position to select (None for first item).
            grid_enabled: Enable grid navigation mode.
            grid_width: Number of columns in grid mode.
            play_selection_sound: Play the selection sound for the focused item.
        """
        ...

    @abstractmethod
    def update_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        position: int | None = None,
        selection_id: str | None = None,
        play_selection_sound: bool = False,
    ) -> None:
        """
        Update an existing menu's items.

        Args:
            menu_id: The menu to update.
            items: New list of items.
            position: Optional new position (1-based).
            selection_id: Optional item ID to focus on.
            play_selection_sound: If True, client plays selection sound at new focus.
        """
        ...

    @abstractmethod
    def remove_menu(self, menu_id: str) -> None:
        """
        Remove a menu.

        Args:
            menu_id: The menu to remove.
        """
        ...

    @abstractmethod
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
        """
        Display an editbox to the user.

        Args:
            input_id: String identifier for this editbox.
            prompt: Prompt text to display.
            default_value: Default text in the editbox.
            multiline: Whether to use a multiline editbox.
            read_only: Whether the editbox is read-only.
            content_format: How the client should render the content.
                "text" for a plain text control, "markdown" for a
                rendered markdown viewer.
        """
        ...

    @abstractmethod
    def remove_editbox(self, input_id: str) -> None:
        """
        Remove an editbox.

        Args:
            input_id: The editbox to remove.
        """
        ...

    @abstractmethod
    def clear_ui(self) -> None:
        """Clear all menus and editboxes."""
        ...


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid_module.uuid4())


def generate_virtual_bot_uuid(name: str) -> str:
    """Generate a deterministic UUID for a virtual bot based on its name.

    This ensures virtual bots have consistent UUIDs across server restarts
    so their game stats persist properly.
    """
    # Use UUID5 with a custom namespace for virtual bots
    namespace = uuid_module.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    return str(uuid_module.uuid5(namespace, f"virtual_bot:{name}"))
