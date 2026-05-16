"""Test user implementation for unit and play tests."""

import time
from dataclasses import dataclass
from typing import Any

from .base import User, MenuItem, EscapeBehavior, generate_uuid
from .preferences import UserPreferences


@dataclass
class Message:
    """A captured message from the test user."""

    type: str
    data: dict[str, Any]


class MockUser(User):
    """
    Mock implementation of User that captures all messages for assertion.

    Used in unit tests and play tests to verify game behavior.
    """

    def __init__(
        self, username: str, locale: str = "en", uuid: str | None = None, approved: bool = True
    ):
        """Initialize a mock user for tests."""
        self._uuid = uuid or generate_uuid()
        self._username = username
        self._locale = locale
        self._approved = approved
        self._connected_at: float = time.time()
        self._client_type: str = ""
        self._platform: str = ""
        self._preferences: UserPreferences = UserPreferences()
        self.messages: list[Message] = []
        self.menus: dict[str, dict[str, Any]] = {}
        self.editboxes: dict[str, dict[str, Any]] = {}

    @property
    def uuid(self) -> str:
        """Return the mock user's UUID."""
        return self._uuid

    @property
    def username(self) -> str:
        """Return the mock user's name."""
        return self._username

    @property
    def locale(self) -> str:
        """Return the mock user's locale."""
        return self._locale

    @property
    def approved(self) -> bool:
        """Return whether the mock user is approved."""
        return self._approved

    @property
    def preferences(self) -> UserPreferences:
        """Return the mock user's preferences."""
        return self._preferences

    @property
    def client_type(self) -> str:
        """Return the mock user's client type."""
        return self._client_type

    def set_client_type(self, client_type: str) -> None:
        """Set the mock user's client type."""
        self._client_type = client_type

    @property
    def platform(self) -> str:
        """Return the mock user's platform string."""
        return self._platform

    def set_platform(self, platform: str) -> None:
        """Set the mock user's platform string."""
        self._platform = platform

    def format_time_online(self) -> str:
        """Format the time this user has been connected."""
        elapsed = time.time() - self._connected_at
        minutes = int(elapsed // 60)
        hours = int(elapsed // 3600)
        days = int(elapsed // 86400)
        if hours < 1:
            return f"{max(minutes, 1)}m"
        if hours < 24:
            return f"{hours}h"
        remaining_hours = hours % 24
        return f"{days}d {remaining_hours}h"

    def speak(self, text: str, buffer: str = "misc") -> None:
        """Record a speech event."""
        self.messages.append(Message("speak", {"text": text, "buffer": buffer}))

    def play_sound(self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100) -> None:
        """Record a sound playback event."""
        self.messages.append(
            Message(
                "play_sound",
                {"name": name, "volume": volume, "pan": pan, "pitch": pitch},
            )
        )

    def play_music(self, name: str, looping: bool = True) -> None:
        """Record a music playback event."""
        self.messages.append(Message("play_music", {"name": name, "looping": looping}))

    def stop_music(self) -> None:
        """Record a music stop event."""
        self.messages.append(Message("stop_music", {}))

    def play_ambience(self, loop: str, intro: str = "", outro: str = "") -> None:
        """Record an ambience playback event."""
        self.messages.append(
            Message("play_ambience", {"loop": loop, "intro": intro, "outro": outro})
        )

    def stop_ambience(self) -> None:
        """Record an ambience stop event."""
        self.messages.append(Message("stop_ambience", {}))

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
        """Record menu display state and message."""
        menu_data = {
            "items": items,
            "multiletter": multiletter,
            "escape_behavior": escape_behavior,
            "position": position,
            "grid_enabled": grid_enabled,
            "grid_width": grid_width,
        }
        self.menus[menu_id] = menu_data
        self.messages.append(Message("show_menu", {"menu_id": menu_id, **menu_data}))

    def update_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        position: int | None = None,
        selection_id: str | None = None,
        play_selection_sound: bool = False,
    ) -> None:
        """Record menu update state and message."""
        if menu_id in self.menus:
            self.menus[menu_id]["items"] = items
            if position is not None:
                self.menus[menu_id]["position"] = position
        self.messages.append(
            Message(
                "update_menu",
                {
                    "menu_id": menu_id,
                    "items": items,
                    "position": position,
                    "selection_id": selection_id,
                },
            )
        )

    def remove_menu(self, menu_id: str) -> None:
        """Record menu removal state and message."""
        self.menus.pop(menu_id, None)
        self.messages.append(Message("remove_menu", {"menu_id": menu_id}))

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
        """Record editbox display state and message."""
        editbox_data = {
            "prompt": prompt,
            "default_value": default_value,
            "multiline": multiline,
            "read_only": read_only,
            "content_format": content_format,
        }
        self.editboxes[input_id] = editbox_data
        self.messages.append(Message("show_editbox", {"input_id": input_id, **editbox_data}))

    def remove_editbox(self, input_id: str) -> None:
        """Record editbox removal state and message."""
        self.editboxes.pop(input_id, None)
        self.messages.append(Message("remove_editbox", {"input_id": input_id}))

    def clear_ui(self) -> None:
        """Clear stored UI state and record the action."""
        self.menus.clear()
        self.editboxes.clear()
        self.messages.append(Message("clear_ui", {}))

    # Test helper methods

    def get_spoken_messages(self) -> list[str]:
        """Get all spoken text messages."""
        return [m.data["text"] for m in self.messages if m.type == "speak"]

    def get_last_spoken(self) -> str | None:
        """Get the most recent spoken message."""
        for m in reversed(self.messages):
            if m.type == "speak":
                return m.data["text"]
        return None

    def get_sounds_played(self) -> list[str]:
        """Get all sound effect names played."""
        return [m.data["name"] for m in self.messages if m.type == "play_sound"]

    def get_current_menu_items(self, menu_id: str) -> list[str | MenuItem] | None:
        """Get the current items for a menu."""
        if menu_id in self.menus:
            return self.menus[menu_id]["items"]
        return None

    def clear_messages(self) -> None:
        """Clear the message history (but not current UI state)."""
        self.messages.clear()
