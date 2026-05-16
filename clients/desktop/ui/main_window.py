"""Main window for Play Palace v9 client."""

import wx
import logging
from .menu_list import MenuList
from .login_dialog import LoginDialog
import accessible_output2.outputs.auto as auto_output
import sys
import os
from dataclasses import dataclass
import json
from pathlib import Path

# Add parent directory to path to import sound_manager and network_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from . import slash_commands
from sound_manager import SoundManager
from network_manager import NetworkManager
from buffer_system import BufferSystem
from config_manager import set_item_in_dict

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class UiPlatformConfig:
    window_size: tuple[int, int]
    menu_size: tuple[int, int]
    history_size: tuple[int, int]
    chat_size: tuple[int, int]
    edit_size: tuple[int, int]
    multiline_size: tuple[int, int]

    @staticmethod
    def for_platform() -> "UiPlatformConfig":
        # Keep sizes modest but visible on all platforms
        return UiPlatformConfig(
            window_size=(980, 720),
            menu_size=(260, 520),
            history_size=(680, 520),
            chat_size=(680, 28),
            edit_size=(680, 28),
            multiline_size=(680, 120),
        )


class MainWindow(wx.Frame):
    """Main application window for Play Palace v9 client."""

    _NAVIGATION_KEYS = {
        wx.WXK_LEFT,
        wx.WXK_RIGHT,
        wx.WXK_UP,
        wx.WXK_DOWN,
        wx.WXK_NUMPAD_LEFT,
        wx.WXK_NUMPAD_RIGHT,
        wx.WXK_NUMPAD_UP,
        wx.WXK_NUMPAD_DOWN,
        wx.WXK_HOME,
        wx.WXK_END,
        wx.WXK_NUMPAD_HOME,
        wx.WXK_NUMPAD_END,
        wx.WXK_PAGEUP,
        wx.WXK_PAGEDOWN,
        wx.WXK_NUMPAD_PAGEUP,
        wx.WXK_NUMPAD_PAGEDOWN,
    }

    def __init__(self, credentials=None):
        """
        Initialize the main window.

        Args:
            credentials: Dict with username, password, server_url, server_id, config_manager
        """
        self.ui_cfg = UiPlatformConfig.for_platform()

        super().__init__(
            parent=None,
            title="PlayPalace 11",
            size=self.ui_cfg.window_size,
        )

        # Store credentials
        self.credentials = credentials or {}
        self.server_id = self.credentials.get("server_id")
        self.config_manager = self.credentials.get("config_manager")

        # Attributes mocked in headless tests (avoid accessing real widgets before they exist)
        self.menu_list = None
        self.chat_input = None
        self.history_text = None

        # Initialize TTS speaker
        self.speaker = auto_output.Auto()

        # Initialize sound manager
        self.sound_manager = SoundManager()

        slash_commands.client = self

        # Play open sound
        self.sound_manager.play("open.ogg", volume=1.0)

        # Initialize network manager
        self.network = NetworkManager(self)
        self.connected = False
        self._force_close = False  # Skip close confirmation for server-initiated closes
        self.expecting_reconnect = False  # Track if we're expecting to reconnect
        self.returning_to_login = False  # Track if we're returning to login dialog
        self.reconnect_attempts = 0  # Track reconnection attempts
        self.max_reconnect_attempts = 30  # Maximum reconnection attempts
        self.last_server_message = None  # Track last speak message for error display
        self.last_server_status_packet = None  # Track last lifecycle status packet
        self.last_status_announcement = None  # Track last lifecycle announcement text
        self.connection_timeout_timer = None  # Track connection timeout timer

        # Store user's options
        # Client-side options (from config file, per-server)
        self.client_options = {}
        # Server-side options (received from server on login)
        self.server_options = {}

        # Load client-side options for this server
        if self.config_manager and self.server_id:
            self.client_options = self.config_manager.get_client_options(self.server_id)
            # Apply initial volumes from client options
            self._apply_client_audio_options()

        # Track which test music is playing
        self.current_test_music = "mainmus.ogg"

        # Track current mode (list or edit)
        self.current_mode = "list"  # "list" or "edit"
        self.edit_mode_callback = None  # Callback for when edit mode submits
        self.current_menu_id = None  # Track which menu is currently displayed
        self.current_menu_state = None  # Track previous menu state for comparison
        self.current_menu_item_ids = []  # Track item IDs for current menu (parallel to menu items)
        self.current_edit_multiline = False  # Track if current editbox is multiline
        self.current_edit_read_only = False  # Track if current editbox is read-only
        self._pending_edit_clear = False  # Clear single-line value on first printable key
        self._pending_multiline_clear = False  # Clear multiline value on first printable key

        # Ping tracking
        self._ping_start_time = None  # Track when ping was sent

        # Initialize buffer system
        self.buffer_system = BufferSystem()
        self.buffer_system.create_buffer("all")
        self.buffer_system.create_buffer("table")
        self.buffer_system.create_buffer("chats")
        self.buffer_system.create_buffer("activity")
        self.buffer_system.create_buffer("misc")

        # Load muted buffers from preferences
        preferences = self._load_preferences()
        if "muted_buffers" in preferences:
            for buffer_name in preferences["muted_buffers"]:
                if not self.buffer_system.is_muted(buffer_name):
                    self.buffer_system.toggle_mute(buffer_name)

        # Initialize UI components
        self._create_ui()
        self._setup_accelerators()
        self._populate_test_data()

        # Bind close event (Alt+F4, window close button)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Auto-connect to localhost
        self._auto_connect()

    def _apply_client_audio_options(self):
        """Apply audio settings from client-side options."""
        if "audio" in self.client_options:
            audio = self.client_options["audio"]
            music_volume = audio.get("music_volume", 20) / 100.0
            ambience_volume = audio.get("ambience_volume", 20) / 100.0

            self.sound_manager.set_music_volume(music_volume)
            self.sound_manager.set_ambience_volume(ambience_volume)

    def _create_ui(self):
        """Create the UI components (audio-first, with basic visual layout)."""
        panel = wx.Panel(self)

        ui_cfg = self.ui_cfg

        # Menu label and list - labels help screen readers
        self.menu_label = wx.StaticText(panel, label="&Menu")
        self.menu_list = MenuList(
            panel,
            sound_manager=self.sound_manager,
            size=ui_cfg.menu_size,
            style=wx.LB_SINGLE | wx.WANTS_CHARS,
        )
        # Bind to activation events to handle menu selections
        self.menu_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_menu_activate)
        # Bind focus events to enable/disable buffer navigation
        self.menu_list.Bind(wx.EVT_SET_FOCUS, self.on_menu_focus)
        self.menu_list.Bind(wx.EVT_KILL_FOCUS, self.on_menu_unfocus)

        # Edit mode input - initially hidden, replaces menu list when in edit mode
        self.edit_label = wx.StaticText(panel, label="&Edit")
        self.edit_input = wx.TextCtrl(panel, size=ui_cfg.edit_size, style=wx.TE_PROCESS_ENTER)
        self.edit_input.Bind(wx.EVT_TEXT_ENTER, self.on_edit_enter)
        self.edit_input.Bind(wx.EVT_CHAR, self.on_edit_char)
        self.edit_input.Hide()
        self.edit_label.Hide()

        # Multiline edit input - for longer text
        self.edit_input_multiline = wx.TextCtrl(
            panel, size=ui_cfg.multiline_size, style=wx.TE_MULTILINE | wx.TE_DONTWRAP
        )
        self.edit_input_multiline.Bind(wx.EVT_CHAR, self.on_edit_multiline_char)
        self.edit_input_multiline.Hide()

        # Multiletter navigation is now server-controlled
        self.multiletter_enabled = True  # Track state from server
        self.escape_behavior = "keybind"  # Track escape behavior from server

        # Chat input comes before history in tab order
        self.chat_label = wx.StaticText(panel, label="&Chat")
        self.chat_input = wx.TextCtrl(panel, size=ui_cfg.chat_size, style=wx.TE_PROCESS_ENTER)
        self.chat_input.Bind(wx.EVT_TEXT_ENTER, self.on_chat_enter)

        # History text - accessible but not visible (small size for screen readers)
        # No word wrap for better screen reader accessibility
        self.history_label = wx.StaticText(panel, label="&History")
        self.history_text = wx.TextCtrl(
            panel,
            size=ui_cfg.history_size,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP,
        )
        # Make sure it's accessible to screen readers despite small size
        self.history_text.SetName("History")

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.menu_label, 0, wx.ALL, 4)
        left_sizer.Add(self.menu_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.history_label, 0, wx.ALL, 4)
        right_sizer.Add(self.history_text, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        right_sizer.Add(self.chat_label, 0, wx.ALL, 4)
        right_sizer.Add(self.chat_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left_sizer, 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(right_sizer, 1, wx.EXPAND | wx.ALL, 4)
        panel.SetSizer(sizer)

    def _setup_accelerators(self):
        """Setup keyboard accelerators."""
        # Create unique IDs for each accelerator
        self.ID_FOCUS_MENU = wx.NewIdRef()
        self.ID_VOLUME_DOWN = wx.NewIdRef()
        self.ID_VOLUME_UP = wx.NewIdRef()
        self.ID_AMBIENCE_DOWN = wx.NewIdRef()
        self.ID_AMBIENCE_UP = wx.NewIdRef()
        self.ID_TOGGLE_TABLE_CHAT = wx.NewIdRef()
        self.ID_TOGGLE_GLOBAL_CHAT = wx.NewIdRef()
        self.ID_PING = wx.NewIdRef()
        self.ID_LIST_ONLINE = wx.NewIdRef()
        self.ID_LIST_ONLINE_WITH_GAMES = wx.NewIdRef()

        # Buffer system IDs
        self.ID_PREV_BUFFER = wx.NewIdRef()
        self.ID_NEXT_BUFFER = wx.NewIdRef()
        self.ID_FIRST_BUFFER = wx.NewIdRef()
        self.ID_LAST_BUFFER = wx.NewIdRef()
        self.ID_OLDER_MESSAGE = wx.NewIdRef()
        self.ID_NEWER_MESSAGE = wx.NewIdRef()
        self.ID_OLDEST_MESSAGE = wx.NewIdRef()
        self.ID_NEWEST_MESSAGE = wx.NewIdRef()
        self.ID_TOGGLE_MUTE = wx.NewIdRef()

        # Common accelerators that work everywhere
        common_entries = [
            wx.AcceleratorEntry(wx.ACCEL_ALT, ord("M"), self.ID_FOCUS_MENU),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F6, self.ID_TOGGLE_TABLE_CHAT),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_F6, self.ID_TOGGLE_GLOBAL_CHAT),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F7, self.ID_AMBIENCE_DOWN),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F8, self.ID_AMBIENCE_UP),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F9, self.ID_VOLUME_DOWN),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F10, self.ID_VOLUME_UP),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F2, self.ID_LIST_ONLINE),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_F2, self.ID_LIST_ONLINE_WITH_GAMES),
            wx.AcceleratorEntry(wx.ACCEL_ALT, ord("P"), self.ID_PING),
        ]

        # Buffer navigation accelerators (only for menu list)
        buffer_entries = [
            # Buffer switching: [ and ]
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord("["), self.ID_PREV_BUFFER),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord("]"), self.ID_NEXT_BUFFER),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, ord("["), self.ID_FIRST_BUFFER),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, ord("]"), self.ID_LAST_BUFFER),
            # Message navigation: , and .
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord(","), self.ID_OLDER_MESSAGE),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord("."), self.ID_NEWER_MESSAGE),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, ord(","), self.ID_OLDEST_MESSAGE),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, ord("."), self.ID_NEWEST_MESSAGE),
            # Buffer mute: F4
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F4, self.ID_TOGGLE_MUTE),
        ]

        # Create two accelerator tables
        self.accel_table_with_buffers = wx.AcceleratorTable(common_entries + buffer_entries)
        self.accel_table_without_buffers = wx.AcceleratorTable(common_entries)

        # Start without buffer keys (will be enabled when menu gets focus)
        self.SetAcceleratorTable(self.accel_table_without_buffers)

        # Bind the accelerator events
        self.Bind(wx.EVT_MENU, self.on_focus_menu, id=self.ID_FOCUS_MENU)
        self.Bind(wx.EVT_MENU, self.on_toggle_table_chat, id=self.ID_TOGGLE_TABLE_CHAT)
        self.Bind(wx.EVT_MENU, self.on_toggle_global_chat, id=self.ID_TOGGLE_GLOBAL_CHAT)
        self.Bind(wx.EVT_MENU, self.on_ambience_down, id=self.ID_AMBIENCE_DOWN)
        self.Bind(wx.EVT_MENU, self.on_ambience_up, id=self.ID_AMBIENCE_UP)
        self.Bind(wx.EVT_MENU, self.on_volume_down, id=self.ID_VOLUME_DOWN)
        self.Bind(wx.EVT_MENU, self.on_volume_up, id=self.ID_VOLUME_UP)
        self.Bind(wx.EVT_MENU, self.on_ping, id=self.ID_PING)
        self.Bind(wx.EVT_MENU, self.on_list_online, id=self.ID_LIST_ONLINE)
        self.Bind(
            wx.EVT_MENU,
            self.on_list_online_with_games,
            id=self.ID_LIST_ONLINE_WITH_GAMES,
        )

        # Buffer system event bindings
        self.Bind(wx.EVT_MENU, self.on_prev_buffer, id=self.ID_PREV_BUFFER)
        self.Bind(wx.EVT_MENU, self.on_next_buffer, id=self.ID_NEXT_BUFFER)
        self.Bind(wx.EVT_MENU, self.on_first_buffer, id=self.ID_FIRST_BUFFER)
        self.Bind(wx.EVT_MENU, self.on_last_buffer, id=self.ID_LAST_BUFFER)
        self.Bind(wx.EVT_MENU, self.on_older_message, id=self.ID_OLDER_MESSAGE)
        self.Bind(wx.EVT_MENU, self.on_newer_message, id=self.ID_NEWER_MESSAGE)
        self.Bind(wx.EVT_MENU, self.on_oldest_message, id=self.ID_OLDEST_MESSAGE)
        self.Bind(wx.EVT_MENU, self.on_newest_message, id=self.ID_NEWEST_MESSAGE)
        self.Bind(wx.EVT_MENU, self.on_buffer_mute_toggle, id=self.ID_TOGGLE_MUTE)

        # Bind key events for game keypresses
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def _populate_test_data(self):
        """Populate UI with test data."""
        # Menu will be populated by server after connection
        # History starts empty - first message will be "Connecting..."
        pass

    def on_close(self, event):
        """Handle window close (Alt+F4, close button) with confirmation."""
        if self.connected and not self._force_close:
            dlg = wx.MessageDialog(
                self,
                "Are you sure you want to exit?",
                "Confirm Exit",
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            if result != wx.ID_YES:
                return
        event.Skip()

    def on_focus_menu(self, event):
        """Handle Alt+M shortcut to focus menu list."""
        self.menu_list.SetFocus()

    def on_menu_focus(self, event):
        """Handle menu list gaining focus - enable buffer navigation."""
        self.SetAcceleratorTable(self.accel_table_with_buffers)
        event.Skip()

    def on_menu_unfocus(self, event):
        """Handle menu list losing focus - disable buffer navigation."""
        try:
            self.SetAcceleratorTable(self.accel_table_without_buffers)
        except RuntimeError:
            # Window is being destroyed, ignore
            pass
        event.Skip()

    def modify_option_value(self, key_path: str, value, *, create_mode: bool = True) -> bool:
        if not self.config_manager or not self.server_id:
            return False
        self.config_manager.set_client_option(
            key_path, value, self.server_id, create_mode=create_mode
        )
        # Update local cache
        set_item_in_dict(self.client_options, key_path, value, create_mode=create_mode)

    def on_ambience_down(self, event):
        """Handle F7 to decrease ambience volume."""
        current_volume = self.sound_manager.ambience_volume
        new_volume = max(0.0, current_volume - 0.1)
        self.sound_manager.set_ambience_volume(new_volume)
        percentage = int(new_volume * 100)
        self.speaker.speak(f"Ambience: {percentage}%")
        self.modify_option_value("audio/ambience_volume", percentage)

    def on_ambience_up(self, event):
        """Handle F8 to increase ambience volume."""
        current_volume = self.sound_manager.ambience_volume
        new_volume = min(1.0, current_volume + 0.1)
        self.sound_manager.set_ambience_volume(new_volume)
        percentage = int(new_volume * 100)
        self.speaker.speak(f"Ambience: {percentage}%")
        self.modify_option_value("audio/ambience_volume", percentage)

    def on_volume_down(self, event):
        """Handle F9 to decrease music volume."""
        current_volume = self.sound_manager.music_volume
        new_volume = max(0.0, current_volume - 0.1)
        self.sound_manager.set_music_volume(new_volume)
        percentage = int(new_volume * 100)
        self.speaker.speak(f"Music: {percentage}%")
        self.modify_option_value("audio/music_volume", percentage)

    def on_volume_up(self, event):
        """Handle F10 to increase music volume."""
        current_volume = self.sound_manager.music_volume
        new_volume = min(1.0, current_volume + 0.1)
        self.sound_manager.set_music_volume(new_volume)
        percentage = int(new_volume * 100)
        self.speaker.speak(f"Music: {percentage}%")
        self.modify_option_value("audio/music_volume", percentage)

    def on_ping(self, event):
        """Handle Alt+P to ping the server and measure latency."""
        import time

        self._ping_start_time = time.time()
        self.sound_manager.play("pingstart.ogg")
        self.network.send_packet({"type": "ping"})

    def on_list_online(self, event):
        """Handle F2 to request list of online users."""
        if self.connected:
            self.network.send_packet({"type": "list_online"})

    def on_list_online_with_games(self, event):
        """Handle Shift+F2 to request online users with game info."""
        if self.connected:
            if self.current_menu_id == "online_users":
                return
            self.network.send_packet({"type": "list_online_with_games"})

    def on_server_pong(self, packet):
        """Handle pong response from server."""
        import time

        if self._ping_start_time is not None:
            elapsed_ms = int((time.time() - self._ping_start_time) * 1000)
            self._ping_start_time = None
            self.sound_manager.play("pingstop.ogg")
            self.speaker.speak(f"Ping: {elapsed_ms}ms")

    def on_toggle_table_chat(self, event):
        """Handle F6 to toggle muting table chat."""
        if not self.config_manager or not self.server_id:
            return
        # Get current state
        current_state = self.client_options.get("social", {}).get("mute_table_chat", False)
        # Toggle it
        current_state = not current_state
        # Announce
        status = "muted" if current_state else "unmuted"
        self.speaker.speak(f"Table chat {status}")
        self.modify_option_value("social/mute_table_chat", current_state)

    def on_toggle_global_chat(self, event):
        """Handle Shift+F6 to toggle muting global chat."""
        if not self.config_manager or not self.server_id:
            return
        # Get current state
        current_state = self.client_options.get("social", {}).get("mute_global_chat", False)
        # Toggle it
        current_state = not current_state
        # Announce
        status = "muted" if current_state else "unmuted"
        self.speaker.speak(f"Global chat {status}")
        self.modify_option_value("social/mute_global_chat", current_state)

    # Buffer navigation event handlers

    def on_prev_buffer(self, event):
        """Handle [ key to switch to previous buffer."""
        self.buffer_system.previous_buffer()
        self._announce_buffer_info()

    def on_next_buffer(self, event):
        """Handle ] key to switch to next buffer."""
        self.buffer_system.next_buffer()
        self._announce_buffer_info()

    def on_first_buffer(self, event):
        """Handle Shift+[ to jump to first buffer."""
        self.buffer_system.first_buffer()
        self._announce_buffer_info()

    def on_last_buffer(self, event):
        """Handle Shift+] to jump to last buffer."""
        self.buffer_system.last_buffer()
        self._announce_buffer_info()

    def on_older_message(self, event):
        """Handle , key to move to older message in current buffer."""
        self.buffer_system.move_in_buffer("older")
        self._announce_current_message()

    def on_newer_message(self, event):
        """Handle . key to move to newer message in current buffer."""
        self.buffer_system.move_in_buffer("newer")
        self._announce_current_message()

    def on_oldest_message(self, event):
        """Handle Shift+, to jump to oldest message in buffer."""
        self.buffer_system.move_in_buffer("oldest")
        self._announce_current_message()

    def on_newest_message(self, event):
        """Handle Shift+. to jump to newest message in buffer."""
        self.buffer_system.move_in_buffer("newest")
        self._announce_current_message()

    def on_buffer_mute_toggle(self, event):
        """Handle F4 to toggle mute for current buffer."""
        buffer_name = self.buffer_system.get_current_buffer_name()
        self.buffer_system.toggle_mute(buffer_name)
        is_muted = self.buffer_system.is_muted(buffer_name)

        # Save muted buffers to config
        self._save_muted_buffers()

        # Announce mute status
        status = "muted" if is_muted else "unmuted"
        self.speaker.speak(f"Buffer {buffer_name} {status}.", interrupt=True)

    def _announce_buffer_info(self):
        """Announce current buffer information (matches Legends format)."""
        name, count, position = self.buffer_system.get_buffer_info()
        is_muted = self.buffer_system.is_muted(name)
        mute_status = ", muted" if is_muted else ""
        # Format: "{name}{mute_status}. {count} items"
        self.speaker.speak(f"{name}{mute_status}. {count} items", interrupt=True)

    def _announce_current_message(self):
        """Announce the current message in the buffer (matches Legends format)."""
        item = self.buffer_system.get_current_item()
        if item:
            # Just speak the message text, no position info
            self.speaker.speak(item["text"], interrupt=True)
        # If no item, fail silently (don't announce empty buffer)

    def _announce_menu_selection(self):
        """Announce the currently selected menu item to screen reader."""
        selection = self.menu_list.GetSelection()
        if selection != wx.NOT_FOUND:
            text = self.menu_list.GetString(selection)
            # Force focus event to trigger screen reader announcement
            # First ensure the list has focus
            if wx.Window.FindFocus() != self.menu_list:
                self.menu_list.SetFocus()
            # Then trigger an accessibility event by selecting the item again
            # This forces Orca to re-announce the selection
            self.menu_list.SetSelection(selection)
            # Also use accessible_output2 as backup
            try:
                self.speaker.speak(text, interrupt=True)
            except (AttributeError, RuntimeError) as exc:
                LOG.debug("Failed to announce menu selection: %s", exc)

    def on_char_hook(self, event):
        """Handle character input for game keypresses."""
        key_code = event.GetKeyCode()
        if self._handle_edit_mode_char(event, key_code):
            return
        if not self._should_handle_menu_key(event):
            return
        if self._handle_escape_behavior(event, key_code):
            return

        key_name = self._map_keybind_name(event, key_code)
        if not key_name:
            event.Skip()
            return

        if self._send_keybind_if_allowed(event, key_name):
            return

        event.Skip()

    def _handle_edit_mode_char(self, event, key_code: int) -> bool:
        """Handle key presses while in edit mode."""
        if self.current_mode != "edit":
            return False
        if key_code == wx.WXK_ESCAPE:
            if self.edit_mode_callback:
                self.edit_mode_callback("")
            self.switch_to_list_mode()
            return True
        event.Skip()
        return True

    def _should_handle_menu_key(self, event) -> bool:
        """Return True if menu list has focus; otherwise allow default handling."""
        focused = wx.Window.FindFocus()
        if focused != self.menu_list:
            event.Skip()
            return False
        return True

    def _handle_escape_behavior(self, event, key_code: int) -> bool:
        """Handle escape/backspace behaviors that bypass normal keybind flow."""
        if key_code not in (wx.WXK_ESCAPE, wx.WXK_BACK):
            return False
        if key_code == wx.WXK_BACK and self.current_menu_id == "main_menu":
            event.Skip()
            return True
        if self.escape_behavior == "select_last_option":
            if self.current_mode == "list" and self.connected:
                item_count = self.menu_list.GetCount()
                if item_count > 0:
                    if self.sound_manager:
                        self.sound_manager.play_menuenter()
                    packet = {
                        "type": "menu",
                        "menu_id": self.current_menu_id,
                        "selection": item_count,
                    }
                    last_index = item_count - 1
                    if 0 <= last_index < len(self.current_menu_item_ids):
                        item_id = self.current_menu_item_ids[last_index]
                        if item_id is not None:
                            packet["selection_id"] = item_id
                    self.network.send_packet(packet)
            return True
        if self.escape_behavior == "escape_event":
            if self.connected:
                self.network.send_packet({"type": "escape", "menu_id": self.current_menu_id})
            return True
        return False

    def _map_keybind_name(self, event, key_code: int) -> str | None:
        """Map wx key codes to server keybind names."""
        menu_is_empty = self.menu_list.GetCount() == 0
        direction_key = self._map_direction_key(event, key_code, menu_is_empty)
        if direction_key is not None:
            return direction_key

        function_key = self._map_function_key(event, key_code)
        if function_key is not None:
            return function_key

        if key_code == wx.WXK_ESCAPE:
            return "escape"
        if key_code == wx.WXK_BACK:
            return "backspace"
        if key_code == wx.WXK_SPACE:
            return "space"

        enter_key = self._map_enter_key(event, key_code)
        if enter_key is not None:
            return enter_key

        letter_key = self._map_letter_key(event, key_code)
        if letter_key is not None:
            return letter_key

        number_key = self._map_number_key(key_code)
        if number_key is not None:
            return number_key

        return None

    def _map_direction_key(self, event, key_code: int, menu_is_empty: bool) -> str | None:
        key_map = {
            wx.WXK_UP: "up",
            wx.WXK_DOWN: "down",
            wx.WXK_LEFT: "left",
            wx.WXK_RIGHT: "right",
        }
        if key_code not in key_map:
            return None
        if menu_is_empty:
            return key_map[key_code]
        # Ctrl+Arrow: send to server as keybind (e.g. navigate destinations)
        if event.ControlDown():
            return key_map[key_code]
        event.Skip()
        return None

    def _map_function_key(self, event, key_code: int) -> str | None:
        key_map = {
            wx.WXK_F1: "f1",
            wx.WXK_F3: "f3",
            wx.WXK_F5: "f5",
        }
        if key_code in (wx.WXK_F2, wx.WXK_F4):
            event.Skip()
            return None
        return key_map.get(key_code)

    def _map_enter_key(self, event, key_code: int) -> str | None:
        if key_code not in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            return None
        if event.ControlDown() or event.ShiftDown() or event.AltDown():
            return "enter"
        return None

    def _map_letter_key(self, event, key_code: int) -> str | None:
        if key_code < 65 or key_code > 90:
            return None
        if key_code == ord("P") and event.AltDown():
            event.Skip()
            return None
        return chr(key_code).lower()

    def _map_number_key(self, key_code: int) -> str | None:
        if 48 <= key_code <= 57:
            return chr(key_code)
        return None

    def _send_keybind_if_allowed(self, event, key_name: str) -> bool:
        """Send a keybind packet when policy allows it."""
        modifiers = event.GetModifiers()
        has_control = (modifiers & wx.MOD_CONTROL) != 0
        has_alt = (modifiers & wx.MOD_ALT) != 0
        has_shift = (modifiers & wx.MOD_SHIFT) != 0

        is_function_key = key_name in [
            "f1",
            "f2",
            "f3",
            "f5",
            "escape",
            "space",
            "backspace",
            "enter",
            "up",
            "down",
            "left",
            "right",
        ]

        should_send = (
            key_name
            and self.connected
            and (
                is_function_key
                or not self.multiletter_enabled
                or has_control
                or has_alt
                or has_shift
            )
        )
        if not should_send:
            return False

        menu_selection = self.menu_list.GetSelection()
        if menu_selection == wx.NOT_FOUND:
            menu_index = None
            menu_item_id = None
        else:
            menu_index = menu_selection + 1
            if 0 <= menu_selection < len(self.current_menu_item_ids):
                menu_item_id = self.current_menu_item_ids[menu_selection]
            else:
                menu_item_id = None

        self.network.send_packet(
            {
                "type": "keybind",
                "key": key_name,
                "control": has_control,
                "alt": has_alt,
                "shift": has_shift,
                "menu_id": self.current_menu_id,
                "menu_index": menu_index,
                "menu_item_id": menu_item_id,
            }
        )
        return True

    def on_menu_activate(self, event):
        """Handle menu item activation (Enter/Space/Double-click)."""
        selection = self.menu_list.GetSelection()
        if selection == wx.NOT_FOUND:
            return

        # Send menu event to server with selection index and ID
        if self.connected:
            packet = {
                "type": "menu",
                "selection": selection + 1,  # Server expects 1-indexed
            }
            # Include menu_id if we have one
            if self.current_menu_id:
                packet["menu_id"] = self.current_menu_id
            # Include selection_id if available
            if 0 <= selection < len(self.current_menu_item_ids):
                item_id = self.current_menu_item_ids[selection]
                if item_id is not None:
                    packet["selection_id"] = item_id
            self.network.send_packet(packet)

        event.Skip()

    def set_multiletter_navigation(self, enabled):
        """Set multiletter navigation state (called by server)."""
        self.multiletter_enabled = enabled
        self.menu_list.enable_multiletter_navigation(enabled)

    def set_grid_mode(self, enabled, grid_width=1):
        """Set grid mode navigation state (called by server)."""
        self.grid_enabled = enabled
        self.grid_width = grid_width
        self.menu_list.enable_grid_mode(enabled, grid_width)

    def on_chat_enter(self, event):
        """Handle chat message send."""
        message = self.chat_input.GetValue().strip()
        if not message:
            return
        if message[0] in "/.":
            # Trim the prefix from the message if there is a space, otherwise the prefix is the entire message
            index = message.find(" ")
            if index >= 0:
                prefix = message[:index]
                message = message[index + 1 :]
            else:
                prefix = message
                message = ""
            func = self.send_global_chat if prefix[0] == "." else slash_commands.process_command
            prefix = prefix[1:]
            func(prefix, message)
        else:
            self.send_table_chat(message)
        self.chat_input.Clear()

    def get_language_name(self, text: str = "") -> str:
        """Get the name of a language based on input."""
        if not text:
            return self.client_options["social"]["chat_input_language"]
        text = text.lower()
        if text in self.lang_codes.keys():
            return self.lang_codes[text]
        if text.capitalize() in self.lang_codes.values():
            return text.capitalize()
        self.speaker.speak(f"{text} is not a valid language name or ISO code.")
        return ""

    def get_language_code(self, name: str = "") -> str:
        """Get a language code from its name."""
        if not name:
            name = self.client_options["social"]["chat_input_language"]
        try:
            return tuple(self.lang_codes.keys())[tuple(self.lang_codes.values()).index(name)]
        except ValueError:
            return ""

    def send_table_chat(self, message: str):
        """Send table chat message to server."""
        if not message:
            return
        # For now send all chats in English
        lang = "English"  # self.get_language_name()
        if not lang:
            return
        self.network.send_packet(
            {"type": "chat", "convo": "local", "message": message, "language": lang}
        )

    def send_global_chat(self, prefix: str, message: str):
        """Send global chat message to server."""
        if not message:
            return
        # For now send all chats in English
        lang = "English"  # self.get_language_name(prefix)
        if not lang:
            return
        self.network.send_packet(
            {"type": "chat", "convo": "global", "message": message, "language": lang}
        )

    def add_history(self, text, buffer_name="misc", speak_aloud=True):
        """
        Add text to the history window and optionally speak it.

        Args:
            text: The message to add
            buffer_name: Which buffer to add to (default: "misc")
            speak_aloud: Whether to speak the text aloud (default: True)
        """
        # Add to buffer system (automatically adds to "all" as well)
        self.buffer_system.add_item(buffer_name, text)

        # Only update UI if current buffer is not muted
        if not self.buffer_system.is_muted(self.buffer_system.get_current_buffer_name()):
            current = self.history_text.GetValue()
            if current and not current.endswith("\n"):
                text = "\n" + text

            # Save current insertion point to prevent auto-scrolling
            old_insertion_point = self.history_text.GetInsertionPoint()

            # Append text to history widget
            self.history_text.AppendText(text + "\n")

            # Restore insertion point (prevents auto-scroll to end)
            self.history_text.SetInsertionPoint(old_insertion_point)

            # Only speak if speak_aloud is True
            if speak_aloud:
                # Speak the text using TTS
                # Use interrupt=False to queue messages without interrupting
                try:
                    self.speaker.speak(text, interrupt=False)
                except (AttributeError, RuntimeError) as exc:
                    LOG.debug("Failed to speak history text: %s", exc)

    # List/Edit mode switching methods

    def switch_to_edit_mode(
        self,
        prompt="",
        callback=None,
        default_value="",
        multiline=False,
        read_only=False,
    ):
        """
        Switch from list mode to edit mode.

        Args:
            prompt: Optional prompt text to speak/display
            callback: Optional callback function to call with the entered text
            default_value: Default text to populate the editbox with
            multiline: Whether to use a multiline editbox
            read_only: Whether the editbox is read-only
        """
        already_in_edit = self.current_mode == "edit"

        if not already_in_edit:
            # Hide menu list and label
            self.menu_list.Hide()
            self.menu_label.Hide()

        # Set the edit label to the prompt
        label = prompt or "&Edit"
        self.edit_label.SetLabel(label)

        # Choose which edit control to use
        if multiline:
            self.edit_input.Hide()
            self.edit_input_multiline.Show()
            self.edit_input_multiline.Clear()
            self.edit_input_multiline.SetValue(default_value)
            self.edit_input_multiline.SetEditable(not read_only)
            self.edit_input_multiline.SetName(label)
            self.edit_input_multiline.SetFocus()
            self.current_edit_multiline = True
            self._schedule_pending_clear(self.edit_input_multiline, True, default_value, read_only)
        else:
            self.edit_input_multiline.Hide()
            self.edit_input.Show()
            self.edit_input.Clear()
            self.edit_input.SetValue(default_value)
            self.edit_input.SetEditable(not read_only)
            self.edit_input.SetName(label)
            self.edit_input.SetFocus()
            self.current_edit_multiline = False
            self._schedule_pending_clear(self.edit_input, False, default_value, read_only)

        self.edit_label.Show()

        self.current_mode = "edit"
        self.edit_mode_callback = callback
        self.current_edit_read_only = read_only

    def switch_to_list_mode(self):
        """Switch from edit mode back to list mode."""
        if self.current_mode == "list":
            return  # Already in list mode

        # Hide edit inputs and label
        self.edit_input.Hide()
        self.edit_input_multiline.Hide()
        self.edit_label.Hide()

        # Show menu list and label
        self.menu_list.Show()
        self.menu_label.Show()
        self.menu_list.SetFocus()

        self.current_mode = "list"
        self.edit_mode_callback = None
        self._pending_edit_clear = False
        self._pending_multiline_clear = False

    def on_edit_enter(self, event):
        """Handle Enter key in edit mode input."""
        text = self.edit_input.GetValue().strip()

        # For read-only editboxes, Enter just closes them
        # For editable editboxes, Enter submits the value
        if self.edit_mode_callback:
            self.edit_mode_callback(text)
        else:
            # Default behavior: just show what was entered
            self.add_history(f"Entered: {text}")

        # Switch back to list mode
        self.switch_to_list_mode()

    def on_edit_char(self, event):
        """Handle character input in edit mode to play typing sounds."""
        import random

        key_code = event.GetKeyCode()

        # Handle Escape key - send empty value
        if key_code == wx.WXK_ESCAPE:
            if self.edit_mode_callback:
                self.edit_mode_callback("")
            self.switch_to_list_mode()
            return  # Don't process the Escape key

        if (
            key_code in self._NAVIGATION_KEYS
            or event.ControlDown()
            or event.AltDown()
            or event.MetaDown()
        ):
            self._pending_edit_clear = False
            event.Skip()
            return

        if (
            self._pending_edit_clear
            and self._should_clear_on_char_event(event, key_code)
            and not self.current_edit_read_only
        ):
            self.edit_input.Clear()
            self._pending_edit_clear = False

        # Only play typing sounds for printable characters (not Enter, Backspace, etc.)
        # Don't play if read-only or if user has disabled typing sounds
        if 32 <= key_code <= 126:  # Printable ASCII range
            should_play = not self.current_edit_read_only and self.client_options.get(
                "interface", {}
            ).get("play_typing_sounds", True)
            if should_play:  # nosec B311
                # Randomly pick typing1.ogg through typing4.ogg
                sound_num = random.randint(1, 4)  # nosec B311
                sound_name = f"typing{sound_num}.ogg"
                self.sound_manager.play(sound_name, volume=0.5)

        # Let the event continue to process normally
        event.Skip()

    def on_edit_multiline_char(self, event):
        """Handle character input in multiline edit mode."""
        import random

        key_code = event.GetKeyCode()

        if self._handle_multiline_escape(key_code):
            return
        if self._should_defer_multiline_to_default(event, key_code):
            return
        self._clear_multiline_pending_if_needed(event, key_code)
        if self._handle_multiline_enter(event, key_code):
            return

        # Play typing sounds for printable characters (not Enter, Backspace, etc.)
        # Don't play if read-only or if user has disabled typing sounds
        if 32 <= key_code <= 126:  # Printable ASCII range
            should_play = not self.current_edit_read_only and self.client_options.get(
                "interface", {}
            ).get("play_typing_sounds", True)
            if should_play:  # nosec B311
                # Randomly pick typing1.ogg through typing4.ogg
                sound_num = random.randint(1, 4)  # nosec B311
                sound_name = f"typing{sound_num}.ogg"
                self.sound_manager.play(sound_name, volume=0.5)

        # Allow all other keys (including plain Enter for newlines in editable mode)
        event.Skip()

    def _handle_multiline_escape(self, key_code: int) -> bool:
        if key_code != wx.WXK_ESCAPE:
            return False
        if self.edit_mode_callback:
            self.edit_mode_callback("")
        self.switch_to_list_mode()
        return True

    def _should_defer_multiline_to_default(self, event, key_code: int) -> bool:
        if (
            key_code in self._NAVIGATION_KEYS
            or event.ControlDown()
            or event.AltDown()
            or event.MetaDown()
        ):
            self._pending_multiline_clear = False
            event.Skip()
            return True
        return False

    def _clear_multiline_pending_if_needed(self, event, key_code: int) -> None:
        if (
            self._pending_multiline_clear
            and self._should_clear_on_char_event(event, key_code)
            and not self.current_edit_read_only
        ):
            self.edit_input_multiline.Clear()
            self._pending_multiline_clear = False

    def _handle_multiline_enter(self, event, key_code: int) -> bool:
        if key_code != wx.WXK_RETURN:
            return False
        if self.current_edit_read_only:
            text = self.edit_input_multiline.GetValue()
            if self.edit_mode_callback:
                self.edit_mode_callback(text)
            self.switch_to_list_mode()
            return True
        invert = self.client_options.get("interface", {}).get(
            "invert_multiline_enter_behavior", False
        )
        if not invert:
            if not event.ShiftDown() and not event.ControlDown():
                text = self.edit_input_multiline.GetValue()
                if self.edit_mode_callback:
                    self.edit_mode_callback(text)
                self.switch_to_list_mode()
                return True
        else:
            if event.ShiftDown() or event.ControlDown():
                text = self.edit_input_multiline.GetValue()
                if self.edit_mode_callback:
                    self.edit_mode_callback(text)
                self.switch_to_list_mode()
                return True
        return False

    def _schedule_pending_clear(
        self, ctrl, multiline: bool, default_value: str, read_only: bool
    ) -> None:
        should_select = bool(default_value) and not read_only and ctrl.IsEnabled()
        if multiline:
            self._pending_edit_clear = False
            self._pending_multiline_clear = should_select
        else:
            self._pending_multiline_clear = False
            self._pending_edit_clear = should_select

        if should_select:
            wx.CallAfter(self._select_all_text, ctrl)

    @staticmethod
    def _select_all_text(ctrl) -> None:
        if not ctrl:
            return
        length = ctrl.GetLastPosition()
        ctrl.SetSelection(0, length)

    @staticmethod
    def _should_clear_on_char_event(event, key_code: int) -> bool:
        if not (32 <= key_code <= 126):
            return False
        if event.ControlDown() or event.AltDown() or event.MetaDown():
            return False
        return True

    # Sound and music methods (for server calls via CallAfter)

    def play_sound(self, sound_name, volume=1.0, pan=0.0, pitch=1.0):
        """
        Play a sound effect (called via CallAfter for non-blocking).

        Args:
            sound_name: Name of sound file (in sounds/ folder)
            volume: Volume 0.0-1.0
            pan: Pan -1.0 to 1.0
            pitch: Pitch multiplier
        """
        wx.CallAfter(self.sound_manager.play, sound_name, volume, pan, pitch)

    def play_music(self, music_name: str, looping: bool = True, fade_out_old: bool = True):
        """
        Play background music (called via CallAfter for non-blocking).

        Args:
            music_name: Name of music file (in sounds/ folder)
            looping: whether to loop the music
            fade_out_old: Whether to fade out current music
        """
        wx.CallAfter(self.sound_manager.music, music_name, looping, fade_out_old)

    def stop_music(self, fade=True):
        """Stop background music."""
        wx.CallAfter(self.sound_manager.stop_music, fade)

    def set_music_volume(self, volume):
        """Set music volume 0.0-1.0."""
        wx.CallAfter(self.sound_manager.set_music_volume, volume)

    def set_menuclick_sound(self, sound_name):
        """Set the menu click sound (server command)."""
        self.sound_manager.set_menuclick_sound(sound_name)

    def set_menuenter_sound(self, sound_name):
        """Set the menu enter/activate sound (server command)."""
        self.sound_manager.set_menuenter_sound(sound_name)

    # Network methods

    def _auto_connect(self):
        """Auto-connect to server using login credentials."""
        username = self.credentials.get("username", "Guest")
        password = self.credentials.get("password", "")
        refresh_token = self.credentials.get("refresh_token")
        refresh_expires_at = self.credentials.get("refresh_expires_at")
        server_url = self.credentials.get("server_url", "ws://localhost:8000")

        # Play connection loop sound
        self.sound_manager.music("connectloop.ogg")

        self.add_history(f"Connecting to {server_url}...", "activity")
        if self.network.connect(server_url, username, password, refresh_token, refresh_expires_at):
            self.add_history(f"Connecting as {username}...", "activity")

            # Set a timeout to detect if connection never succeeds
            self.connection_timeout_timer = wx.CallLater(10000, self._check_connection_timeout)
        else:
            self._show_connection_error("Failed to start connection to server.")

    def _check_connection_timeout(self):
        """Check if connection succeeded within timeout period."""
        # Don't timeout if we're in the middle of reconnecting or returning to login
        if not self.connected and not self.expecting_reconnect and not self.returning_to_login:
            self._show_connection_error("Connection timeout: Could not connect to server.")

    def on_connection_lost(self):
        """Handle connection loss."""
        self.connected = False
        # Don't show error if we're expecting to reconnect or returning to login
        if not self.expecting_reconnect and not self.returning_to_login:
            self._show_connection_error("Connection lost!")

    def on_server_status(self, packet):
        """Handle lifecycle status updates (initializing/maintenance)."""
        self.last_server_status_packet = packet
        message = self._format_status_text(packet)
        self.last_status_announcement = message
        self._announce_status_message(message)

    def on_server_disconnect(self, packet):
        """Handle server disconnect packet."""
        should_reconnect = packet.get("reconnect", False)
        show_message = packet.get("show_message", False)
        return_to_login = packet.get("return_to_login", False)
        status_mode = packet.get("status_mode")
        retry_after = packet.get("retry_after")
        disconnect_message = packet.get("message")

        if status_mode:
            message = disconnect_message or self._format_status_text(
                self.last_server_status_packet or {}
            )
            self._show_connection_error(message, return_to_login=True)
            if retry_after:
                delay = max(1, int(retry_after))
                self._schedule_reconnect_after(
                    delay,
                    f"{message} Reconnecting in {delay} seconds...",
                )
            return

        if should_reconnect:
            delay = max(1, int(packet.get("retry_after", 3)))
            self._schedule_reconnect_after(
                delay,
                f"Server is restarting. Reconnecting in {delay} seconds...",
            )
        elif show_message:
            # Explicit disconnect with message dialog (e.g., account declined)
            message = disconnect_message or self.last_server_message or "Disconnected by server."
            self._show_connection_error(message, return_to_login=return_to_login)
        else:
            # Explicit disconnect, close quietly (e.g., user logout)
            self._force_close = True
            self.speaker.speak("Disconnected.", interrupt=False)
            wx.CallLater(500, self.Close)

    def _format_status_text(self, packet):
        """Format a lifecycle status packet into readable text."""
        if not packet:
            return "Server is temporarily unavailable."
        message = packet.get("message") or "Server is temporarily unavailable."
        resume_at = packet.get("resume_at")
        if resume_at:
            message = f"{message} Expected availability: {resume_at}."
        return message

    def _announce_status_message(self, message: str):
        """Speak and optionally log lifecycle status messages."""
        buffer_system = getattr(self, "buffer_system", None)
        history_text = getattr(self, "history_text", None)
        can_log = (
            buffer_system
            and hasattr(buffer_system, "add_item")
            and hasattr(buffer_system, "is_muted")
            and hasattr(buffer_system, "get_current_buffer_name")
            and history_text
            and hasattr(history_text, "GetValue")
        )
        if can_log:
            self.add_history(message, buffer_name="activity")
        try:
            self.speaker.speak(message, interrupt=False)
        except (AttributeError, RuntimeError) as exc:
            LOG.debug("Failed to speak status message: %s", exc)

    def _schedule_reconnect_after(self, delay_seconds: int, announce_text: str):
        """Schedule a reconnect attempt after a delay."""
        delay_ms = max(1000, int(delay_seconds * 1000))
        self.expecting_reconnect = True
        if self.connection_timeout_timer:
            self.connection_timeout_timer.Stop()
            self.connection_timeout_timer = None
        self.speaker.speak(announce_text, interrupt=False)

        def reconnect():
            server_url = self.credentials.get("server_url")
            username = self.credentials.get("username")
            password = self.credentials.get("password", "")
            if server_url and username:
                self.speaker.speak("Reconnecting...", interrupt=False)
                self.network.disconnect()
                wx.CallLater(1000, lambda: self._do_reconnect(server_url, username, password))

        wx.CallLater(delay_ms, reconnect)

    def _do_reconnect(self, server_url, username, password):
        """Actually perform the reconnection attempt."""
        self.reconnect_attempts += 1

        # Check if already connected (successful)
        if self.connected:
            self.expecting_reconnect = False
            self.reconnect_attempts = 0
            return

        # Check if exceeded max attempts
        if self.reconnect_attempts > self.max_reconnect_attempts:
            self.expecting_reconnect = False
            self.reconnect_attempts = 0
            self.speaker.speak("Failed to reconnect after multiple attempts.", interrupt=False)
            self.Close()
            return

        # Attempt to connect
        self.add_history(f"Reconnecting as {username}... (attempt {self.reconnect_attempts})")
        self.network.disconnect()

        refresh_token = self.credentials.get("refresh_token")
        refresh_expires_at = self.credentials.get("refresh_expires_at")
        if self.network.connect(server_url, username, password, refresh_token, refresh_expires_at):
            # Wait 3 seconds then check again
            wx.CallLater(3000, lambda: self._do_reconnect(server_url, username, password))
        else:
            self.expecting_reconnect = False
            self.reconnect_attempts = 0
            self.speaker.speak("Failed to reconnect.", interrupt=False)
            self.Close()

    def _show_connection_error(self, message, return_to_login=False):
        """Show error modal and either quit application or return to login."""
        # Set flags and cancel timers BEFORE showing dialog to prevent race conditions
        if return_to_login:
            self.returning_to_login = True
        if self.connection_timeout_timer:
            self.connection_timeout_timer.Stop()
            self.connection_timeout_timer = None

        # Stop any music
        self.sound_manager.stop_music(fade=False)

        # Disconnect network and wait for thread to fully stop before showing dialog
        self.network.disconnect(wait=True)

        # Build error message, including last server message if available
        error_body = message
        if self.last_server_message and self.last_server_message not in error_body:
            error_body += f"\n\nServer message: {self.last_server_message}"

        if return_to_login:
            error_body += "\n\nReturning to the login dialog."
        else:
            error_body += "\n\nThe application will now close."

        # Show error dialog (blocking)
        wx.MessageBox(error_body, "Connection Error", wx.OK | wx.ICON_ERROR)

        if return_to_login:
            self._return_to_login()
        else:
            # Quit the application
            self.Close()
            wx.GetApp().ExitMainLoop()

    def _return_to_login(self):
        """Close main window and show login dialog again."""
        # Hide the main window
        self.Hide()

        # Show login dialog
        login_dialog = LoginDialog(self)
        if login_dialog.ShowModal() == wx.ID_OK:
            # Get new credentials and reconnect
            new_credentials = login_dialog.get_credentials()
            login_dialog.Destroy()

            # Update credentials
            self.credentials = new_credentials
            self.server_id = new_credentials.get("server_id")
            self.config_manager = new_credentials.get("config_manager")

            # Reset connection state completely
            self.connected = False
            self.expecting_reconnect = False
            self.returning_to_login = False
            self.reconnect_attempts = 0
            self.last_server_message = None
            self.connection_timeout_timer = None

            # Create fresh network manager to ensure clean state
            self.network = NetworkManager(self)

            # Clear history and show window
            self.history_text.Clear()
            self.Show()

            # Connect with new credentials
            server_url = new_credentials.get("server_url")
            username = new_credentials.get("username")
            password = new_credentials.get("password", "")
            refresh_token = new_credentials.get("refresh_token")
            refresh_expires_at = new_credentials.get("refresh_expires_at")

            self.add_history(f"Connecting to {server_url} as {username}...", "activity")
            self.sound_manager.music("connectloop.ogg")
            if self.network.connect(
                server_url, username, password, refresh_token, refresh_expires_at
            ):
                # Set connection timeout
                self.connection_timeout_timer = wx.CallLater(15000, self._check_connection_timeout)
            else:
                self._show_connection_error("Failed to start connection to server.")
        else:
            # User cancelled, close the application
            login_dialog.Destroy()
            self.Close()
            wx.GetApp().ExitMainLoop()

    # Server packet handlers

    def on_authorize_success(self, packet):
        """Handle authorization success from server."""
        self.connected = True
        version = packet.get("version", "unknown")
        username = packet.get("username") or self.credentials.get("username", "Guest")
        server_url = self.credentials.get("server_url", "")
        refresh_token = packet.get("refresh_token")
        refresh_expires_at = packet.get("refresh_expires_at")

        # Cancel any pending timeout timer
        if self.connection_timeout_timer:
            self.connection_timeout_timer.Stop()
            self.connection_timeout_timer = None

        # Stop connection loop and play welcome sound
        self.sound_manager.stop_music(fade=False)
        self.sound_manager.play("welcome.ogg", volume=1.0)

        if server_url:
            self.add_history(
                f"Connected to {server_url} as {username} (server {version})",
                "activity",
            )
        else:
            self.add_history(
                f"Connected as {username} (server {version})",
                "activity",
            )

        if refresh_token and self.config_manager and self.server_id:
            account_id = self.credentials.get("account_id")
            if account_id:
                self.config_manager.update_account(
                    self.server_id,
                    account_id,
                    refresh_token=refresh_token,
                    refresh_expires_at=refresh_expires_at,
                )
                self.credentials["refresh_token"] = refresh_token
                self.credentials["refresh_expires_at"] = refresh_expires_at

    def on_open_server_options(self, packet):
        """Handle open server options packet from server.

        #This handler is for
        server-side options like battle reserves and account settings.
        """
        self.server_options = packet.get("options", {})

    def on_update_options_lists(self, packet):
        """Handle update_options_lists packet from server.

        Automatically updates client options to include new games and languages
        without requiring the user to open the options dialog.
        """
        self.games_list = packet.get("games", [])
        languages = packet.get("languages", {})
        # Server may send list (codes) or dict (code->name). Normalize to dict.
        if isinstance(languages, list):
            languages = {code: code for code in languages}
        self.lang_codes = languages
        if not self.config_manager or not self.server_id:
            return

        # Ensure profile structure exists
        profiles = self.config_manager.profiles
        profiles.setdefault("server_options", {})
        profiles.setdefault("client_options_defaults", {}).setdefault("local_table", {}).setdefault(
            "creation_notifications", {}
        )
        profiles.setdefault("client_options_defaults", {}).setdefault("social", {}).setdefault(
            "language_subscriptions", {}
        )

        updated = False

        languages = tuple(self.lang_codes.values())
        # Update games in both default profile and server profile
        if self.games_list:
            # Update default profile
            default_local_table = profiles["client_options_defaults"].setdefault("local_table", {})
            default_creation_notifications = default_local_table.setdefault(
                "creation_notifications", {}
            )
            for game_info in self.games_list:
                game_name = game_info["name"]
                if game_name not in default_creation_notifications:
                    default_creation_notifications[game_name] = True
                    updated = True

            # Update server profile
            server_profiles = profiles.get("server_options", {})
            if self.server_id in server_profiles:
                server_overrides = server_profiles[self.server_id].setdefault(
                    "options_overrides", {}
                )
                server_local_table = server_overrides.setdefault("local_table", {})
                server_creation_notifications = server_local_table.setdefault(
                    "creation_notifications", {}
                )
                for game_info in self.games_list:
                    game_name = game_info["name"]
                    if game_name not in server_creation_notifications:
                        server_creation_notifications[game_name] = True
                        updated = True

        # Update languages in both default profile and server profile
        # Rebuild dicts to match server order (alphabetical ascending)
        if languages:
            # Update default profile - rebuild to match server order
            default_social = profiles["client_options_defaults"].setdefault("social", {})
            default_lang_subscriptions = default_social.get("language_subscriptions", {})
            new_default_subscriptions = {}
            for language in languages:
                # Preserve existing value or default to False
                new_default_subscriptions[language] = default_lang_subscriptions.get(
                    language, False
                )
            # Update if keys changed (order or new languages added)
            if list(new_default_subscriptions.keys()) != list(default_lang_subscriptions.keys()):
                default_social["language_subscriptions"] = new_default_subscriptions
                updated = True

            # Update server profile - rebuild to match server order
            server_profiles = profiles.get("server_options", {})
            if self.server_id in server_profiles:
                server_overrides = server_profiles[self.server_id].setdefault(
                    "options_overrides", {}
                )
                social_overrides = server_overrides.setdefault("social", {})
                lang_subscriptions = social_overrides.get("language_subscriptions", {})
                new_subscriptions = {}
                for language in languages:
                    # Preserve existing value or default to False
                    new_subscriptions[language] = lang_subscriptions.get(language, False)
                # Update if keys changed (order or new languages added)
                if list(new_subscriptions.keys()) != list(lang_subscriptions.keys()):
                    social_overrides["language_subscriptions"] = new_subscriptions
                    updated = True

        # Save if any changes were made
        if updated:
            self.config_manager.save_profiles()
            # Reload client options to reflect the changes
            self.client_options = self.config_manager.get_client_options(self.server_id)

        # Send client options to server after update_options_lists is complete
        # (this ensures migration and options list updates are both finished)
        self.send_client_options_to_server()

    def send_client_options_to_server(self):
        """Send server profile client options to the server.

        Sends only the server-specific options (not defaults) to inform
        the server of the client's preferences.
        """
        if not self.connected or not self.config_manager or not self.server_id:
            return

        # Get server profile options (defaults + overrides merged)
        options = self.config_manager.get_client_options(self.server_id)

        self.network.send_packet(
            {
                "type": "client_options",
                "options": options,
            }
        )

    def on_open_client_options(self, packet):
        """Handle server request to open client options dialog (includes server nickname)."""
        if not self.config_manager or not self.server_id:
            wx.MessageBox("Client options not available", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Import the dialog
        from .options_dialog import ClientOptionsDialog

        # Open client-side dialog (pass client_options for in-memory updates)
        # Games and languages will be read from config (already populated at login)
        dlg = ClientOptionsDialog(
            self,
            self.config_manager,
            self.server_id,
            self.lang_codes,
            self.sound_manager,
            self.client_options,
        )

        dlg.Destroy()
        # Send updated client options to server after saving
        self.send_client_options_to_server()

    def on_server_speak(self, packet):
        """Handle speak packet from server."""
        text = packet.get("text", "")
        buffer_name = packet.get("buffer", "misc")  # Optional buffer parameter, defaults to "misc"
        is_muted = packet.get("muted", False)  # Check if message should be muted (no TTS)

        if text:
            # Store last message for error display on disconnect
            self.last_server_message = text
            # Add to history regardless of mute status
            self.add_history(text, buffer_name, speak_aloud=(not is_muted))

    def on_receive_chat(self, packet):
        """Handle chat packet from server."""
        convo = packet.get("convo")
        lang = packet.get("language")
        # For now all chats are in English
        same_user = packet.get("sender") == self.credentials["username"]
        """comment out all of this code for now
        if lang not in self.lang_codes.values():
            lang = "Other"
        # If language matches, ignore subscription tracking
        if (
            not same_user
            and lang != self.client_options["social"]["chat_input_language"]
        ):
            if convo == "global" or (
                convo == "local"
                and self.client_options["social"][
                    "include_language_filters_for_table_chat"
                ]
            ):
                # Check if the user is ignoring this language
                if not self.client_options["social"]["language_subscriptions"][lang]:
                    return
        end this comment"""
        if convo == "global":
            message = f"{packet.get('sender')} globally: {packet.get('message')}"
        else:
            message = f"{packet.get('sender')}: {packet.get('message')}"
        # Convo doesn't support muting, or the mute flag is disabled
        if True:
            """(
            same_user
            or convo not in {"global", "local"}
            or not self.client_options["social"][f"mute_{convo}_chat"]
        ):"""
            sound = "chat"
            if convo == "local":
                sound += "local"
            self.sound_manager.play(sound + ".ogg")
            self.speaker.speak(message)
        self.add_history(message, "chats", False)

    def on_server_play_sound(self, packet):
        """Handle play_sound packet from server."""
        sound = packet.get("name", packet.get("sound", ""))  # Server sends "name"
        volume = packet.get("volume", 100) / 100.0  # Convert 0-100 to 0.0-1.0
        pan = packet.get("pan", 0) / 100.0  # Convert -100 to 100 to -1.0 to 1.0
        pitch = packet.get("pitch", 100) / 100.0  # Convert 0-200 to 0.0-2.0
        if sound:
            self.sound_manager.play(sound, volume, pan, pitch)

    def on_server_play_music(self, packet):
        """Handle play_music packet from server."""
        music = packet.get("name", packet.get("music", ""))  # Server sends "name"
        looping = packet.get("looping", True)  # Default to True for backwards compatibility
        if music:
            self.sound_manager.music(music, looping=looping)

    def on_server_play_ambience(self, packet):
        """Handle play_ambience packet from server."""
        intro = packet.get("intro")
        loop = packet.get("loop")
        outro = packet.get("outro")
        if loop:  # Loop is required
            self.sound_manager.ambience(intro, loop, outro)

    def on_server_stop_ambience(self, packet):
        """Handle stop_ambience packet from server."""
        self.sound_manager.stop_ambience()

    def on_server_add_playlist(self, packet):
        """Handle add_playlist packet from server."""
        playlist_id = packet.get(
            "playlist_id", "music_playlist"
        )  # Default to backward-compatible ID
        tracks = packet.get("tracks", [])
        audio_type = packet.get("audio_type", "music")  # Default to music
        shuffle_tracks = packet.get("shuffle_tracks", False)
        repeats = packet.get("repeats", 1)  # Default to 1 repeat
        auto_start = packet.get("auto_start", True)
        auto_remove = packet.get("auto_remove", True)  # Default to True
        if tracks:
            self.sound_manager.add_playlist(
                playlist_id,
                tracks,
                audio_type,
                shuffle_tracks,
                repeats,
                auto_start,
                auto_remove,
            )

    def on_server_start_playlist(self, packet):
        """Handle start_playlist packet from server."""
        playlist_id = packet.get("playlist_id", "music_playlist")
        playlist = self.sound_manager.get_playlist(playlist_id)
        if playlist and not playlist.is_active:
            playlist.is_active = True
            playlist._play_next_track()

    def on_server_remove_playlist(self, packet):
        """Handle remove_playlist packet from server."""
        playlist_id = packet.get("playlist_id", "music_playlist")
        self.sound_manager.remove_playlist(playlist_id)

    def on_server_get_playlist_duration(self, packet):
        """Handle get_playlist_duration packet from server."""
        playlist_id = packet.get("playlist_id", "music_playlist")
        duration_type = packet.get("duration_type", "total")  # "total", "elapsed", or "remaining"
        request_id = packet.get("request_id")

        playlist = self.sound_manager.get_playlist(playlist_id)
        duration = 0

        if playlist:
            if duration_type == "total":
                result = playlist.get_total_duration()
                duration = result if result is not None else 0
            elif duration_type == "elapsed":
                duration = playlist.get_elapsed_duration()
            elif duration_type == "remaining":
                duration = playlist.get_remaining_duration()

        # Send response back to server
        if request_id:
            response = {
                "type": "playlist_duration_response",
                "request_id": request_id,
                "playlist_id": playlist_id,
                "duration_type": duration_type,
                "duration": duration,
            }
            self.network.send_packet(response)

    def on_table_create(self, packet):
        host = packet.get("host")
        game = packet.get("game")
        if not self.client_options["local_table"]["creation_notifications"][game]:
            return
        self.sound_manager.play("notify.ogg")
        self.add_history(f"{host} is hosting {game}.", "activity")

    def compute_menu_diff_by_id(self, old_items, new_items, old_ids, new_ids):
        """
        Compute minimal operations using item IDs to transform old_items into new_items.
        This is much simpler and more reliable than text-based LCS diffing.

        Returns list of operations: ('insert', index, text), ('delete', index), ('update', index, text)

        Algorithm:
        1. Build maps of IDs to (index, text) for old and new lists
        2. Identify deleted IDs (in old but not new)
        3. Identify inserted IDs (in new but not old)
        4. Identify common IDs that may need text updates
        5. Generate operations accordingly
        """
        operations = []

        # Build ID maps: {id: (index, text)}
        old_map = {}
        for i, (item_id, text) in enumerate(zip(old_ids, old_items)):
            if item_id is not None:
                old_map[item_id] = (i, text)

        new_map = {}
        for i, (item_id, text) in enumerate(zip(new_ids, new_items)):
            if item_id is not None:
                new_map[item_id] = (i, text)

        # Identify deleted, inserted, and common IDs
        old_id_set = set(old_map.keys())
        new_id_set = set(new_map.keys())

        deleted_ids = old_id_set - new_id_set
        inserted_ids = new_id_set - old_id_set
        common_ids = old_id_set & new_id_set

        # If all IDs are common (no inserts/deletes) but reordered,
        # fall back to position-based text comparison so the ListBox
        # actually reflects the new order.
        if not deleted_ids and not inserted_ids and old_ids != new_ids:
            operations = []
            for i, (old_text, new_text) in enumerate(zip(old_items, new_items)):
                if old_text != new_text:
                    operations.append(("update", i, new_text))
            return operations

        # Generate delete operations (using old indices)
        for item_id in deleted_ids:
            old_index = old_map[item_id][0]
            operations.append(("delete", old_index))

        # Generate insert and update operations (using new indices)
        for i, (new_id, new_text) in enumerate(zip(new_ids, new_items)):
            if new_id is None:
                continue

            if new_id in inserted_ids:
                # New item - insert it
                operations.append(("insert", i, new_text))
            elif new_id in common_ids:
                # Existing item - check if text changed
                old_text = old_map[new_id][1]
                if old_text != new_text:
                    operations.append(("update", i, new_text))

        return operations

    def compute_menu_diff(self, old_items, new_items, old_ids=None, new_ids=None):
        """
        Compute minimal operations to transform old_items into new_items.
        Returns list of operations: ('insert', index, text), ('delete', index), ('update', index, text)

        If all items have IDs (old_ids and new_ids provided and no None values), use the simpler
        ID-based algorithm. Otherwise fall back to LCS-based text diffing.

        For simplicity and screen reader friendliness:
        - If lists are same length, generate update operations for changed items
        - Otherwise use LCS-based diff for structural changes
        """
        if self._can_use_id_diff(old_items, new_items, old_ids, new_ids):
            return self.compute_menu_diff_by_id(old_items, new_items, old_ids, new_ids)

        # Fall back to text-based LCS algorithm
        operations = []

        same_length_ops = self._diff_same_length(old_items, new_items)
        if same_length_ops is not None:
            return same_length_ops

        operations = self._diff_with_lcs(old_items, new_items)

        return operations

    @staticmethod
    def _can_use_id_diff(old_items, new_items, old_ids, new_ids) -> bool:
        return (
            old_ids is not None
            and new_ids is not None
            and len(old_ids) == len(old_items)
            and len(new_ids) == len(new_items)
            and all(item_id is not None for item_id in old_ids)
            and all(item_id is not None for item_id in new_ids)
        )

    @staticmethod
    def _diff_same_length(old_items, new_items):
        if len(old_items) != len(new_items):
            return None
        operations = []
        for i in range(len(old_items)):
            if old_items[i] != new_items[i]:
                operations.append(("update", i, new_items[i]))
        return operations

    @staticmethod
    def _diff_with_lcs(old_items, new_items):
        m, n = len(old_items), len(new_items)
        lcs = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if old_items[i - 1] == new_items[j - 1]:
                    lcs[i][j] = lcs[i - 1][j - 1] + 1
                else:
                    lcs[i][j] = max(lcs[i - 1][j], lcs[i][j - 1])

        operations = []
        i, j = m, n
        while i > 0 or j > 0:
            if i > 0 and j > 0 and old_items[i - 1] == new_items[j - 1]:
                i -= 1
                j -= 1
            elif j > 0 and (i == 0 or lcs[i][j - 1] >= lcs[i - 1][j]):
                operations.insert(0, ("insert", j - 1, new_items[j - 1]))
                j -= 1
            else:
                operations.insert(0, ("delete", i - 1))
                i -= 1
        return operations

    def apply_menu_diff(self, operations, old_selection):
        """
        Apply diff operations to menu_list while preserving screen reader context.
        Returns new selection index after operations.

        Operations must be applied carefully:
        - Deletes in reverse order (high index to low) to avoid index shifting issues
        - Inserts in forward order
        - Updates in any order
        """
        new_selection = old_selection

        # Separate operations by type
        deletes = [(op[1],) for op in operations if op[0] == "delete"]
        inserts = [op for op in operations if op[0] == "insert"]
        updates = [op for op in operations if op[0] == "update"]

        # Apply deletes in reverse order (highest index first)
        # This prevents index shifting issues
        for (index,) in sorted(deletes, key=lambda x: x[0], reverse=True):
            self.menu_list.Delete(index)
            # Adjust selection if deleting before/at selected item
            if new_selection != wx.NOT_FOUND:
                if index < new_selection:
                    new_selection -= 1
                elif index == new_selection:
                    # Selected item was deleted, select next item (or last if at end)
                    new_selection = min(new_selection, self.menu_list.GetCount() - 1)

        # Apply inserts in forward order
        for op_type, *args in inserts:
            index, text = args
            self.menu_list.Insert(text, index)
            # Adjust selection if inserting before selected item
            if new_selection != wx.NOT_FOUND and index <= new_selection:
                new_selection += 1

        # Apply updates (order doesn't matter)
        for op_type, *args in updates:
            index, text = args
            self.menu_list.SetString(index, text)

        return new_selection

    def on_server_menu(self, packet):
        """Handle menu packet from server."""
        menu_data = self._parse_menu_packet(packet)
        items = menu_data["items"]
        item_ids = menu_data["item_ids"]
        item_sounds = menu_data["item_sounds"]
        menu_id = menu_data["menu_id"]
        position = menu_data["position"]
        play_selection_sound = packet.get("play_selection_sound", False)

        if self._menu_state_is_unchanged(menu_data):
            self._apply_menu_position(items, position)
            if play_selection_sound:
                self._play_menu_selection_sound(position, item_sounds)
            return

        self._apply_menu_settings(menu_data)
        is_same_menu_id = self.current_menu_id == menu_id
        self._prepare_menu_mode(menu_id)
        old_item_ids = getattr(self, "current_menu_item_ids", [])
        self.current_menu_item_ids = item_ids

        if not is_same_menu_id:
            self._rebuild_menu(items, position)
        elif self.menu_list.GetCount() > 0:
            self._apply_menu_diff_update(items, item_ids, old_item_ids, position)
        else:
            self._rebuild_menu(items, position)

        self._update_menu_sounds(item_sounds)
        if play_selection_sound:
            self._play_menu_selection_sound(position, item_sounds)

    def _parse_menu_packet(self, packet: dict) -> dict:
        """Parse menu packet into structured data."""
        items_raw = packet.get("items", [])
        menu_id = packet.get("menu_id", None)
        previous_state = (
            self.current_menu_state
            if isinstance(self.current_menu_state, dict)
            and self.current_menu_state.get("menu_id") == menu_id
            else {}
        )
        multiletter_enabled = packet.get(
            "multiletter_enabled",
            previous_state.get("multiletter_enabled", True),
        )
        escape_behavior = packet.get(
            "escape_behavior",
            previous_state.get("escape_behavior", "keybind"),
        )
        position = packet.get("position", None)
        selection_id = packet.get("selection_id", None)
        grid_enabled = packet.get("grid_enabled", previous_state.get("grid_enabled", False))
        grid_width = packet.get("grid_width", previous_state.get("grid_width", 1))

        items = []
        item_ids = []
        item_sounds = []
        for item in items_raw:
            if isinstance(item, dict):
                items.append(item.get("text", ""))
                item_ids.append(item.get("id"))
                item_sounds.append(item.get("sound"))
            else:
                items.append(str(item))
                item_ids.append(None)
                item_sounds.append(None)

        if selection_id is not None and position is None:
            try:
                position = item_ids.index(selection_id)
            except ValueError:
                pass

        return {
            "items": items,
            "item_ids": item_ids,
            "item_sounds": item_sounds,
            "menu_id": menu_id,
            "multiletter_enabled": multiletter_enabled,
            "escape_behavior": escape_behavior,
            "grid_enabled": grid_enabled,
            "grid_width": grid_width,
            "position": position,
        }

    def _menu_state_is_unchanged(self, menu_data: dict) -> bool:
        new_menu_state = {
            "menu_id": menu_data["menu_id"],
            "items": menu_data["items"],
            "item_sounds": menu_data["item_sounds"],
            "multiletter_enabled": menu_data["multiletter_enabled"],
            "escape_behavior": menu_data["escape_behavior"],
            "grid_enabled": menu_data["grid_enabled"],
            "grid_width": menu_data["grid_width"],
        }
        if self.current_menu_state == new_menu_state:
            return True
        self.current_menu_state = new_menu_state
        return False

    def _apply_menu_settings(self, menu_data: dict) -> None:
        self.set_multiletter_navigation(menu_data["multiletter_enabled"])
        self.set_grid_mode(menu_data["grid_enabled"], menu_data["grid_width"])
        self.escape_behavior = menu_data["escape_behavior"]

    def _prepare_menu_mode(self, menu_id) -> None:
        if self.current_mode == "edit":
            self.switch_to_list_mode()
        self.current_menu_id = menu_id

    def _apply_menu_position(self, items: list[str], position: int | None) -> None:
        if position is not None and len(items) > 0 and 0 <= position < len(items):
            self.menu_list.SetSelection(position)
            self.menu_list.EnsureVisible(position)

    def _play_menu_selection_sound(self, position: int | None, item_sounds: list) -> None:
        """Play the selection sound for the item at position."""
        if not self.sound_manager or position is None:
            return
        if 0 <= position < len(item_sounds) and item_sounds[position]:
            self.sound_manager.play(item_sounds[position])
        else:
            self.sound_manager.play_menuclick()

    def _set_menu_focus(self) -> None:
        focused = wx.Window.FindFocus()
        if focused != self.chat_input and focused != self.history_text:
            self.menu_list.SetFocus()

    def _rebuild_menu(self, items: list[str], position: int | None) -> None:
        self.menu_list.Clear()
        for item in items:
            self.menu_list.Append(item)
        self._set_menu_focus()
        if len(items) > 0:
            if position is not None and 0 <= position < len(items):
                self.menu_list.SetSelection(position)
            else:
                self.menu_list.SetSelection(0)

    def _apply_menu_diff_update(
        self,
        items: list[str],
        item_ids: list[str | None],
        old_item_ids: list[str | None],
        position: int | None,
    ) -> None:
        old_items = [self.menu_list.GetString(i) for i in range(self.menu_list.GetCount())]
        old_selection = self.menu_list.GetSelection()
        operations = self.compute_menu_diff(old_items, items, old_item_ids, item_ids)
        new_selection = self.apply_menu_diff(operations, old_selection)

        if position is not None and len(items) > 0 and 0 <= position < len(items):
            new_selection = position
            self.menu_list.SetSelection(new_selection)
        elif len(items) > 0:
            current_selection = self.menu_list.GetSelection()
            if new_selection != wx.NOT_FOUND:
                if current_selection != new_selection:
                    self.menu_list.SetSelection(new_selection)
            else:
                if current_selection == wx.NOT_FOUND:
                    self.menu_list.SetSelection(0)

    def _update_menu_sounds(self, item_sounds: list[str | None]) -> None:
        for i, sound in enumerate(item_sounds):
            if i < self.menu_list.GetCount():
                if sound:
                    self.menu_list.SetClientData(i, {"sound": sound})
                else:
                    self.menu_list.SetClientData(i, None)

    def on_server_request_input(self, packet):
        """Handle request_input packet from server."""
        prompt = packet.get("prompt", "Enter text:")
        input_id = packet.get("input_id", None)
        default_value = packet.get("default_value", "")
        multiline = packet.get("multiline", False)
        read_only = packet.get("read_only", False)
        content_format = packet.get("content_format", "text")

        def on_submit(text):
            # Send editbox event back to server
            event_packet = {"type": "editbox", "text": text}
            if input_id:
                event_packet["input_id"] = input_id
            self.network.send_packet(event_packet)

        # When the server explicitly requests markdown rendering, show the
        # content in the markdown viewer instead of a plain text control.
        if content_format == "markdown":
            if not default_value:
                default_value = "*No documentation available.*"
                
            from .markdown_viewer_dialog import MarkdownViewerDialog

            dlg = MarkdownViewerDialog(self, prompt, default_value)
            dlg.ShowModal()
            dlg.Destroy()
            # Send empty response so the server navigates back
            on_submit("")
            return

        self.switch_to_edit_mode(prompt, on_submit, default_value, multiline, read_only)

    def on_server_document_editor(self, packet):
        """Handle document_editor packet from server — open the editor dialog."""
        from .document_editor_dialog import DocumentEditorDialog

        dialog_id = packet.get("dialog_id", "")
        content = packet.get("content", "")
        content_label = packet.get("content_label")
        source_content = packet.get("source_content")
        source_label = packet.get("source_label")
        prompt = packet.get("prompt", "Edit document")

        def on_save(text):
            self.network.send_packet(
                {
                    "type": "document_editor",
                    "dialog_id": dialog_id,
                    "action": "save",
                    "content": text,
                }
            )

        def on_cancel():
            self.network.send_packet(
                {
                    "type": "document_editor",
                    "dialog_id": dialog_id,
                    "action": "cancel",
                    "content": "",
                }
            )

        dlg = DocumentEditorDialog(
            self,
            prompt,
            content,
            content_label=content_label,
            source_content=source_content,
            source_label=source_label,
            on_save=on_save,
            on_cancel=on_cancel,
        )
        result = dlg.ShowModal()
        dlg.Destroy()
        # If the dialog was closed without triggering save or cancel callbacks
        # (shouldn't happen with current flow, but safety net)
        if result not in (wx.ID_SAVE, wx.ID_CANCEL):
            on_cancel()

    def on_server_clear_ui(self, packet):
        """Handle clear_ui packet from server."""
        # Clear menu
        self.menu_list.Clear()
        self.current_menu_id = None
        self.current_menu_state = None
        # Switch to list mode if in edit mode
        if self.current_mode == "edit":
            self.switch_to_list_mode()
        # Remove all playlists when leaving game
        self.sound_manager.remove_all_playlists()
        # Stop music and ambience when leaving game
        self.sound_manager.stop_music(fade=True)
        self.sound_manager.stop_ambience(force=False)

    def on_server_game_list(self, packet):
        """Handle game_list packet from server."""
        games = packet.get("games", [])
        if games:
            game_list_str = "Available games:\n"
            for game in games:
                game_list_str += f"{game['id']}: {game['name']} ({game['type']}) - {game['players']}/{game['max_players']} players\n"
            self.add_history(game_list_str)
        else:
            self.add_history("No games available")

    # Config persistence methods

    def _load_preferences(self):
        """
        Load preferences from ~/.playpalace/preferences.json

        Returns:
            Dict containing preferences, or empty dict if file doesn't exist
        """
        config_dir = Path.home() / ".playpalace"
        preferences_file = config_dir / "preferences.json"

        if preferences_file.exists():
            try:
                with open(preferences_file, "r") as f:
                    return json.load(f)
            except Exception:
                # If preferences is corrupted, return empty dict
                return {}
        return {}

    def _save_muted_buffers(self):
        """Save muted buffers to preferences file."""
        config_dir = Path.home() / ".playpalace"
        preferences_file = config_dir / "preferences.json"

        # Load existing preferences
        preferences = self._load_preferences()

        # Update muted buffers
        preferences["muted_buffers"] = list(self.buffer_system.get_muted_buffers())

        # Save
        config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(preferences_file, "w") as f:
                json.dump(preferences, f, indent=2)
        except (OSError, TypeError, ValueError) as exc:
            LOG.debug("Failed to save preferences: %s", exc)
