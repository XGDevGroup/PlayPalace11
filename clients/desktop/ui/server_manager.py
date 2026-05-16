"""Server and account editor dialogs for Play Palace client."""

import re
import wx
import sys
from pathlib import Path

# Add parent directory to path to import config_manager
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_manager import ConfigManager


class AccountEditorDialog(wx.Dialog):
    """Dialog for editing or creating a user account."""

    def __init__(
        self,
        parent,
        config_manager: ConfigManager,
        server_id: str,
        account_id: str = None,
        server_name: str = "",
    ):
        """Initialize the account editor dialog.

        Args:
            parent: Parent window
            config_manager: ConfigManager instance
            server_id: Server ID this account belongs to
            account_id: Account ID to edit, or None to create new account
            server_name: Server display name for the dialog title
        """
        base_title = "Edit Account" if account_id else "Add Account"
        title = f"{base_title} \u2014 {server_name}" if server_name else base_title
        super().__init__(parent, title=title, size=(400, 330))

        self.config_manager = config_manager
        self.server_id = server_id
        self.account_id = account_id
        self.account_data = None

        # Load existing account data if editing
        if account_id:
            self.account_data = config_manager.get_account_by_id(server_id, account_id)

        self._create_ui()
        self.CenterOnParent()

        # Bind escape key to close
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def _create_ui(self):
        """Create the UI components."""
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Username
        username_label = wx.StaticText(panel, label="&Username:")
        sizer.Add(username_label, 0, wx.LEFT | wx.TOP, 10)

        username_value = ""
        if self.account_data:
            username_value = self.account_data.get("username", "")
        self.username_input = wx.TextCtrl(panel, value=username_value)
        sizer.Add(self.username_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Password
        password_label = wx.StaticText(panel, label="&Password:")
        sizer.Add(password_label, 0, wx.LEFT | wx.TOP, 10)

        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Placeholder for user-entered password.
        password_value = ""  # nosec B105
        if self.account_data:
            password_value = self.account_data.get("password", "")

        # Create both masked and plain text controls for password
        self.password_input = wx.TextCtrl(panel, value=password_value, style=wx.TE_PASSWORD)
        self.password_input.SetName("Password")
        self.password_plain = wx.TextCtrl(panel, value=password_value)
        self.password_plain.SetName("Password")
        self.password_plain.Hide()

        password_sizer.Add(self.password_input, 1, wx.RIGHT, 5)
        password_sizer.Add(self.password_plain, 1, wx.RIGHT, 5)

        self.show_password_btn = wx.Button(panel, label="&Show Password")
        password_sizer.Add(self.show_password_btn, 0)

        sizer.Add(password_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Email
        email_label = wx.StaticText(panel, label="&Email:")
        sizer.Add(email_label, 0, wx.LEFT | wx.TOP, 10)

        email_value = ""
        if self.account_data:
            email_value = self.account_data.get("email", "")
        self.email_input = wx.TextCtrl(panel, value=email_value)
        sizer.Add(self.email_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Notes
        notes_label = wx.StaticText(panel, label="&Notes:")
        sizer.Add(notes_label, 0, wx.LEFT | wx.TOP, 10)

        notes_value = ""
        if self.account_data:
            notes_value = self.account_data.get("notes", "")
        self.notes_input = wx.TextCtrl(
            panel, value=notes_value, style=wx.TE_MULTILINE, size=(-1, 60)
        )
        sizer.Add(self.notes_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        save_btn = wx.Button(panel, wx.ID_OK, "&Save")
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, "&Cancel")
        button_sizer.Add(save_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(cancel_btn, 0)

        sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)

        # Bind events
        self.show_password_btn.Bind(wx.EVT_BUTTON, self.on_show_password)
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

        # Set focus
        self.username_input.SetFocus()

    def on_key(self, event):
        """Handle key events."""
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def on_show_password(self, event):
        """Toggle password visibility."""
        if self.password_input.IsShown():
            # Switch to plain text (show password)
            current_value = self.password_input.GetValue()
            self.password_plain.SetValue(current_value)
            self.password_input.Hide()
            self.password_plain.Show()
            self.show_password_btn.SetLabel("&Hide Password")
            self.password_plain.SetFocus()
        else:
            # Switch to masked (hide password)
            current_value = self.password_plain.GetValue()
            self.password_input.SetValue(current_value)
            self.password_plain.Hide()
            self.password_input.Show()
            self.show_password_btn.SetLabel("&Show")
            self.password_input.SetFocus()

        self.password_input.GetParent().Layout()

    def _get_password_value(self) -> str:
        """Get the current password value from whichever control is visible."""
        if self.password_input.IsShown():
            return self.password_input.GetValue()
        else:
            return self.password_plain.GetValue()

    def _validate_email(self, email: str) -> bool:
        """Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid (empty or valid format), False otherwise
        """
        if not email:
            return True  # Empty is allowed
        # Lowercase and validate against pattern
        email_lower = email.lower()
        pattern = r"^[a-z0-9_.+-]+@[a-z0-9_.-]+$"
        return bool(re.match(pattern, email_lower))

    def _validate_for_close(self) -> bool:
        """Validate all fields before closing.

        Validates in display order: username, password, email.

        Returns:
            True if all fields are valid, False otherwise
        """
        username = self.username_input.GetValue().strip()
        password = self._get_password_value()
        email = self.email_input.GetValue().strip()

        # Validate username
        if not username:
            wx.MessageBox(
                "Username cannot be empty.",
                "Validation Error",
                wx.OK | wx.ICON_ERROR,
            )
            self.username_input.SetFocus()
            return False

        # Validate password
        if not password:
            wx.MessageBox(
                "Password cannot be empty.",
                "Validation Error",
                wx.OK | wx.ICON_ERROR,
            )
            # Focus the visible password field
            if self.password_input.IsShown():
                self.password_input.SetFocus()
            else:
                self.password_plain.SetFocus()
            return False

        # Validate email
        if not self._validate_email(email):
            wx.MessageBox(
                "Invalid email address format.",
                "Validation Error",
                wx.OK | wx.ICON_ERROR,
            )
            self.email_input.SetFocus()
            return False

        return True

    def _save_if_needed(self) -> bool:
        """Save account data if there are changes.

        Returns:
            True if saved successfully or no save needed, False if validation failed
        """
        username = self.username_input.GetValue().strip()
        password = self._get_password_value()
        email = self.email_input.GetValue().strip().lower()
        notes = self.notes_input.GetValue().strip()

        if not username:
            return True  # Don't save without a username, but not an error

        if not self._validate_email(email):
            return False  # Validation failed

        if self.account_id:
            # Update existing account
            self.config_manager.update_account(
                self.server_id,
                self.account_id,
                username=username,
                password=password,
                email=email,
                notes=notes,
            )
        else:
            # Create new account
            self.account_id = self.config_manager.add_account(
                self.server_id,
                username=username,
                password=password,
                email=email,
                notes=notes,
            )
        return True

    def on_save(self, event):
        """Handle save button click."""
        if not self._validate_for_close():
            return
        if self._save_if_needed():
            self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        """Handle cancel button click."""
        self.EndModal(wx.ID_CANCEL)

    def get_account_id(self) -> str:
        """Get the account ID (for newly created accounts)."""
        return self.account_id


class TrustedCertificateDialog(wx.Dialog):
    """Dialog for viewing and managing trusted certificates."""

    def __init__(
        self,
        parent,
        config_manager: ConfigManager,
        server_id: str,
    ):
        """Initialize the trusted certificate dialog.

        Args:
            parent: Parent window
            config_manager: ConfigManager instance
            server_id: Server ID to view certificate for
        """
        super().__init__(parent, title="Trusted Certificate", size=(450, 300))

        self.config_manager = config_manager
        self.server_id = server_id

        self._create_ui()
        self.CenterOnParent()

        # Bind escape key to close
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def _create_ui(self):
        """Create the UI components."""
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Certificate details label
        details_label = wx.StaticText(panel, label="Certificate &Details:")
        sizer.Add(details_label, 0, wx.LEFT | wx.TOP, 10)

        # Certificate details text field
        self.details_text = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(-1, 150),
        )
        sizer.Add(self.details_text, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Populate certificate details
        self._refresh_certificate_details()

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.forget_btn = wx.Button(panel, label="&Forget Certificate")
        self.forget_btn.Bind(wx.EVT_BUTTON, self.on_forget_certificate)
        button_sizer.Add(self.forget_btn, 0, wx.RIGHT, 5)

        close_btn = wx.Button(panel, wx.ID_CANCEL, "&Close")
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        button_sizer.Add(close_btn, 0)

        sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)

        # Update forget button state
        self._update_forget_button_state()

    def _refresh_certificate_details(self):
        """Refresh the certificate details text."""
        if not self.server_id:
            self.details_text.SetValue("No server saved yet.")
            return

        cert = self.config_manager.get_trusted_certificate(self.server_id)
        if not cert:
            self.details_text.SetValue("No trusted certificate stored.")
            return

        # Build certificate details text
        details = []
        if cert.get("host"):
            details.append(f"Host: {cert['host']}")
        if cert.get("common_name"):
            details.append(f"Common Name: {cert['common_name']}")
        if cert.get("fingerprint"):
            details.append(f"Fingerprint: {cert['fingerprint']}")
        if cert.get("pem"):
            details.append("")
            details.append("PEM Certificate:")
            details.append(cert["pem"])

        self.details_text.SetValue(
            "\n".join(details) if details else "Certificate data unavailable."
        )

    def _update_forget_button_state(self):
        """Enable/disable forget button based on certificate existence."""
        if not self.server_id:
            self.forget_btn.Enable(False)
            return
        cert = self.config_manager.get_trusted_certificate(self.server_id)
        self.forget_btn.Enable(cert is not None)

    def on_forget_certificate(self, event):
        """Remove stored trusted certificate for this server."""
        if not self.server_id:
            return
        confirm = wx.MessageBox(
            "Remove the trusted certificate for this server?",
            "Forget Certificate",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
        )
        if confirm == wx.YES:
            self.config_manager.clear_trusted_certificate(self.server_id)
            self._refresh_certificate_details()
            self._update_forget_button_state()

    def on_key(self, event):
        """Handle key events."""
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

    def on_close(self, event):
        """Handle close button click."""
        self.EndModal(wx.ID_OK)


class ServerEditorDialog(wx.Dialog):
    """Dialog for editing or creating a server's connection properties."""

    def __init__(
        self,
        parent,
        config_manager: ConfigManager,
        server_id: str = None,
    ):
        """Initialize the server editor dialog.

        Args:
            parent: Parent window
            config_manager: ConfigManager instance
            server_id: Server ID to edit, or None to create new server
        """
        base_title = "Edit Server" if server_id else "Add Server"
        # Include server name in title when editing
        if server_id:
            server_data = config_manager.get_server_by_id(server_id)
            server_name = server_data.get("name", "") if server_data else ""
            title = f"{base_title} \u2014 {server_name}" if server_name else base_title
        else:
            title = base_title
        super().__init__(parent, title=title, size=(450, 350))

        self.config_manager = config_manager
        self.server_id = server_id
        self.server_data = None

        # Load existing server data if editing
        if server_id:
            self.server_data = config_manager.get_server_by_id(server_id)

        self._create_ui()
        self.CenterOnParent()

        # Bind escape key to close
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def _create_ui(self):
        """Create the UI components."""
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Options Profile button
        self.options_profile_btn = wx.Button(panel, label="&Options Profile")
        self.options_profile_btn.Bind(wx.EVT_BUTTON, self.on_options_profile)
        sizer.Add(self.options_profile_btn, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Server Name
        name_label = wx.StaticText(panel, label="Server &Name:")
        sizer.Add(name_label, 0, wx.LEFT | wx.TOP, 10)

        name_value = ""
        if self.server_data:
            name_value = self.server_data.get("name", "")
        self.name_input = wx.TextCtrl(panel, value=name_value)
        sizer.Add(self.name_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Host Address
        host_label = wx.StaticText(panel, label="&Host Address:")
        sizer.Add(host_label, 0, wx.LEFT | wx.TOP, 10)

        host_value = ""
        if self.server_data:
            host_value = self.server_data.get("host", "")
        self.host_input = wx.TextCtrl(panel, value=host_value)
        sizer.Add(self.host_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Port
        port_label = wx.StaticText(panel, label="&Port:")
        sizer.Add(port_label, 0, wx.LEFT | wx.TOP, 10)

        port_value = 8000
        if self.server_data:
            port_value = self.server_data.get("port", 8000)
        self.port_input = wx.TextCtrl(panel, value=str(port_value))
        sizer.Add(self.port_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Trusted certificate button
        self.cert_btn = wx.Button(panel, label="&Trusted Certificate")
        self.cert_btn.Bind(wx.EVT_BUTTON, self.on_trusted_certificate)
        sizer.Add(self.cert_btn, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Notes
        notes_label = wx.StaticText(panel, label="&Notes:")
        sizer.Add(notes_label, 0, wx.LEFT | wx.TOP, 10)

        notes_value = ""
        if self.server_data:
            notes_value = self.server_data.get("notes", "")
        self.notes_input = wx.TextCtrl(
            panel, value=notes_value, style=wx.TE_MULTILINE, size=(-1, 50)
        )
        sizer.Add(self.notes_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        save_btn = wx.Button(panel, wx.ID_OK, "&Save")
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, "&Cancel")
        button_sizer.Add(save_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(cancel_btn, 0)

        sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)

        # Bind events
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

        # Set focus - options profile if editing existing server, otherwise name input
        if self.server_id:
            self.options_profile_btn.SetFocus()
        else:
            self.name_input.SetFocus()

    def on_trusted_certificate(self, event):
        """Open the trusted certificate dialog."""
        if not self.server_id:
            wx.MessageBox(
                "Please click Save to create the server first, then open Trusted Certificate again.",
                "Save Required",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        dlg = TrustedCertificateDialog(self, self.config_manager, self.server_id)
        dlg.ShowModal()
        dlg.Destroy()

    def on_options_profile(self, event):
        """Handle options profile button click."""
        wx.MessageBox(
            "Not implemented yet.",
            "Options Profile",
            wx.OK | wx.ICON_INFORMATION,
        )

    def on_key(self, event):
        """Handle key events."""
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def _validate_for_close(self) -> bool:
        """Validate all fields before closing.

        Validates in display order: name, host, port.
        Notes is optional.

        Returns:
            True if all fields are valid, False otherwise
        """
        name = self.name_input.GetValue().strip()
        host = self.host_input.GetValue().strip()
        port = self.port_input.GetValue().strip()

        # Validate server name
        if not name:
            wx.MessageBox(
                "Server name cannot be empty.",
                "Validation Error",
                wx.OK | wx.ICON_ERROR,
            )
            self.name_input.SetFocus()
            return False

        # Validate host address
        if not host:
            wx.MessageBox(
                "Host address cannot be empty.",
                "Validation Error",
                wx.OK | wx.ICON_ERROR,
            )
            self.host_input.SetFocus()
            return False

        # Validate port
        if not port:
            wx.MessageBox(
                "Port cannot be empty.",
                "Validation Error",
                wx.OK | wx.ICON_ERROR,
            )
            self.port_input.SetFocus()
            return False

        try:
            port_num = int(port)
            if port_num < 1000 or port_num > 65535:
                wx.MessageBox(
                    "Port must be between 1000 and 65535.",
                    "Validation Error",
                    wx.OK | wx.ICON_ERROR,
                )
                self.port_input.SetFocus()
                return False
        except ValueError:
            wx.MessageBox(
                "Port must be a valid number.",
                "Validation Error",
                wx.OK | wx.ICON_ERROR,
            )
            self.port_input.SetFocus()
            return False

        return True

    def _save_if_needed(self) -> bool:
        """Save server data if there are changes.

        Returns:
            True if saved successfully or no save needed, False if validation failed
        """
        name = self.name_input.GetValue().strip()
        host = self.host_input.GetValue().strip()
        port = self.port_input.GetValue().strip()
        notes = self.notes_input.GetValue().strip()

        if not name:
            return True  # Don't save without a name

        try:
            port_num = int(port)
        except ValueError:
            return False  # Validation failed

        if self.server_id:
            # Update existing server
            self.config_manager.update_server(
                self.server_id,
                name=name,
                host=host,
                port=port_num,
                notes=notes,
            )
        else:
            # Create new server
            self.server_id = self.config_manager.add_server(
                name=name,
                host=host,
                port=port_num,
                notes=notes,
            )
            # Reload server data
            self.server_data = self.config_manager.get_server_by_id(self.server_id)

        return True

    def on_save(self, event):
        """Handle save button click."""
        if not self._validate_for_close():
            return
        if self._save_if_needed():
            self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        """Handle cancel button click."""
        self.EndModal(wx.ID_CANCEL)

    def get_server_id(self) -> str:
        """Get the server ID (for newly created servers)."""
        return self.server_id
