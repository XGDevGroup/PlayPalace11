"""Login dialog for Play Palace client.

Uses a hierarchical TreeCtrl to display servers and their accounts,
making the ownership relationship clear to screen reader users.
"""

import wx
import sys
from pathlib import Path

# Add parent directory to path to import config_manager
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_manager import ConfigManager
from ui.enhance_wx.tree_selection import ManagedTreeCtrl
from ui.config_sharing import (
    ConfigSharingDialog,
    try_load_export_file,
    format_export_timestamp,
)


class LoginDialog(wx.Dialog):
    """Login dialog with a server/account tree and management buttons."""

    def __init__(self, parent=None):
        """Initialize the login dialog."""
        super().__init__(parent, title="Play Palace Login", size=(500, 450))

        # Initialize config manager
        self.config_manager = ConfigManager()

        self.username = ""
        # Placeholder for user-entered password.
        self.user_input_value = str()
        self.refresh_token = None
        self.refresh_expires_at = None
        self.server_id = None
        self.account_id = None
        self.server_url = None

        self._populating = False

        self._create_ui()
        self.CenterOnScreen()

    def _create_ui(self):
        """Create the UI components."""
        self.panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(self.panel, label="PlayPalace 11.")
        title_font = title.GetFont()
        title_font.PointSize += 4
        title_font = title_font.Bold()
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)

        # Server/Account tree label
        tree_label = wx.StaticText(self.panel, label="&Servers and Accounts:")
        sizer.Add(tree_label, 0, wx.LEFT | wx.TOP, 10)

        # Server/Account tree
        self.tree = ManagedTreeCtrl(
            self.panel,
            style=wx.TR_HAS_BUTTONS | wx.TR_SINGLE | wx.TR_HIDE_ROOT,
            name="Servers and accounts",
        )
        sizer.Add(self.tree, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Row 1: Add actions
        add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_server_btn = wx.Button(self.panel, label="Add &Server")
        add_sizer.Add(self.add_server_btn, 0, wx.RIGHT, 5)

        self.add_account_btn = wx.Button(self.panel, label="Add Acco&unt")
        add_sizer.Add(self.add_account_btn, 0)

        sizer.Add(add_sizer, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Row 2: Item actions + advanced
        item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.edit_btn = wx.Button(self.panel, label="&Edit")
        item_sizer.Add(self.edit_btn, 0, wx.RIGHT, 5)

        self.delete_btn = wx.Button(self.panel, label="&Delete")
        item_sizer.Add(self.delete_btn, 0, wx.RIGHT, 5)

        self.advanced_btn = wx.Button(self.panel, label="Ad&vanced")
        item_sizer.Add(self.advanced_btn, 0)

        sizer.Add(item_sizer, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Row 3: Dialog actions
        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.login_btn = wx.Button(self.panel, wx.ID_OK, "&Login")
        self.login_btn.SetDefault()
        action_sizer.Add(self.login_btn, 0, wx.RIGHT, 5)

        cancel_btn = wx.Button(self.panel, wx.ID_CANCEL, "&Cancel")
        action_sizer.Add(cancel_btn, 0)

        sizer.Add(action_sizer, 0, wx.ALL | wx.CENTER, 10)

        # Set sizer
        self.panel.SetSizer(sizer)

        # Bind events
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_tree_sel_changed)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_tree_item_activated)
        self.add_server_btn.Bind(wx.EVT_BUTTON, self.on_add_server)
        self.add_account_btn.Bind(wx.EVT_BUTTON, self.on_add_account)
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_edit)
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        self.advanced_btn.Bind(wx.EVT_BUTTON, self.on_advanced)
        self.login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

        # Populate tree
        last_server = self.config_manager.get_last_server_id()
        last_account = None
        if last_server:
            last_account = self.config_manager.get_last_account_id(last_server)
        self._populate_tree(select_server_id=last_server, select_account_id=last_account)

        # Set initial focus
        if self.tree.GetSelection().IsOk():
            self.tree.SetFocus()
        else:
            self.add_server_btn.SetFocus()

    # -------------------------------------------------------------------------
    # Tree population
    # -------------------------------------------------------------------------

    def _populate_tree(self, select_server_id=None, select_account_id=None):
        """Rebuild the tree from config, preserving expand state where possible.

        Args:
            select_server_id: Server to select (or expand if selecting an account).
            select_account_id: Account to select within select_server_id.
        """
        self._populating = True
        try:
            # Record currently expanded servers
            expanded_server_ids = set()
            root = self.tree.GetRootItem()
            if root.IsOk():
                item, cookie = self.tree.GetFirstChild(root)
                while item.IsOk():
                    data = self.tree.GetItemData(item)
                    if data and self.tree.IsExpanded(item):
                        expanded_server_ids.add(data[1])
                    item, cookie = self.tree.GetNextChild(root, cookie)

            self.tree.DeleteAllItems()
            tree_root = self.tree.AddRoot("")

            target_item = None
            servers = self.config_manager.get_all_servers()

            for server_id, server in servers.items():
                server_name = server.get("name", "Unknown Server")
                server_item = self.tree.AppendItem(tree_root, server_name)
                self.tree.SetItemData(server_item, ("server", server_id, None))

                accounts = self.config_manager.get_server_accounts(server_id)
                for account_id, account in accounts.items():
                    username = account.get("username", "Unknown")
                    acct_item = self.tree.AppendItem(server_item, username)
                    self.tree.SetItemData(acct_item, ("account", server_id, account_id))

                    # Target: specific account requested
                    if server_id == select_server_id and account_id == select_account_id:
                        target_item = acct_item

                # Expand if was previously expanded or contains the target
                should_expand = server_id in expanded_server_ids or server_id == select_server_id
                if should_expand and self.tree.GetChildrenCount(server_item, False) > 0:
                    self.tree.Expand(server_item)

                # Target: server requested but no specific account
                if server_id == select_server_id and target_item is None:
                    # Select the first account if available, otherwise the server
                    first_child, _ = self.tree.GetFirstChild(server_item)
                    target_item = first_child if first_child.IsOk() else server_item

            # Fallback: select first account of first server, or first server
            if target_item is None:
                first_server, _ = self.tree.GetFirstChild(tree_root)
                if first_server.IsOk():
                    first_account, _ = self.tree.GetFirstChild(first_server)
                    if first_account.IsOk():
                        self.tree.Expand(first_server)
                        target_item = first_account
                    else:
                        target_item = first_server

            if target_item:
                self.tree.SelectItem(target_item)
        finally:
            self._populating = False

        self._update_button_states()

    # -------------------------------------------------------------------------
    # Tree helpers
    # -------------------------------------------------------------------------

    def _get_selected_item_data(self):
        """Get data for the currently selected tree item.

        Returns:
            Tuple of (item_type, server_id, account_id) or (None, None, None).
        """
        sel = self.tree.GetSelection()
        if not sel.IsOk():
            return (None, None, None)
        data = self.tree.GetItemData(sel)
        if not data:
            return (None, None, None)
        return data

    def _get_server_id_for_selection(self):
        """Get the server_id for the current selection, walking up if needed."""
        item_type, server_id, _ = self._get_selected_item_data()
        return server_id

    def _get_server_name_for_selection(self):
        """Get the server display name for the current selection."""
        sel = self.tree.GetSelection()
        if not sel.IsOk():
            return ""
        data = self.tree.GetItemData(sel)
        if not data:
            return ""
        item_type = data[0]
        if item_type == "server":
            return self.tree.GetItemText(sel)
        elif item_type == "account":
            parent = self.tree.GetItemParent(sel)
            if parent.IsOk():
                return self.tree.GetItemText(parent)
        return ""

    # -------------------------------------------------------------------------
    # Button state management
    # -------------------------------------------------------------------------

    def _update_button_states(self):
        """Update button labels and enabled state based on tree selection."""
        item_type, server_id, account_id = self._get_selected_item_data()
        server_name = self._get_server_name_for_selection()

        if item_type == "server":
            self._set_label(self.edit_btn, "&Edit Server")
            self._set_label(self.delete_btn, "&Delete Server")
            self._set_label(self.add_account_btn, f"Add Acco&unt to {server_name}")
            self.edit_btn.Enable(True)
            self.delete_btn.Enable(True)
            self.add_account_btn.Enable(True)
            self.login_btn.Enable(False)
        elif item_type == "account":
            self._set_label(self.edit_btn, "&Edit Account")
            self._set_label(self.delete_btn, "&Delete Account")
            self._set_label(self.add_account_btn, f"Add Acco&unt to {server_name}")
            self.edit_btn.Enable(True)
            self.delete_btn.Enable(True)
            self.add_account_btn.Enable(True)
            self.login_btn.Enable(True)
        else:
            self._set_label(self.edit_btn, "&Edit")
            self._set_label(self.delete_btn, "&Delete")
            self._set_label(self.add_account_btn, "Add Acco&unt")
            self.edit_btn.Enable(False)
            self.delete_btn.Enable(False)
            self.add_account_btn.Enable(False)
            self.login_btn.Enable(False)

    @staticmethod
    def _set_label(btn, label):
        """Set button label only if it changed (avoids redundant screen reader announcements)."""
        if btn.GetLabel() != label:
            btn.SetLabel(label)

    # -------------------------------------------------------------------------
    # Event handlers
    # -------------------------------------------------------------------------

    def _on_tree_sel_changed(self, event):
        """Handle tree selection change."""
        event.Skip()
        if not self._populating:
            self._update_button_states()

    def _on_tree_item_activated(self, event):
        """Handle Enter/double-click on tree item."""
        item = event.GetItem()
        if not item.IsOk():
            return
        data = self.tree.GetItemData(item)
        if data and data[0] == "account":
            self.on_login(event)
        else:
            # Toggle expand/collapse for server nodes
            if self.tree.IsExpanded(item):
                self.tree.Collapse(item)
            else:
                self.tree.Expand(item)

    def on_add_server(self, event):
        """Open the server editor to create a new server."""
        from .server_manager import ServerEditorDialog

        dlg = ServerEditorDialog(self, self.config_manager)
        new_server_id = None
        if dlg.ShowModal() == wx.ID_OK:
            new_server_id = dlg.get_server_id()
            self._populate_tree(select_server_id=new_server_id)
        dlg.Destroy()

        if new_server_id:
            prompt = wx.MessageBox(
                "Server added. Would you like to add an account for it now?\nBy default, a server will accept new created accounts by users.",
                "Add Account?",
                wx.YES_NO | wx.ICON_QUESTION,
            )
            if prompt == wx.YES:
                self.on_add_account(None)
                return

        self.tree.SetFocus()

    def on_add_account(self, event):
        """Open the account editor to create a new account on the selected server."""
        from .server_manager import AccountEditorDialog

        server_id = self._get_server_id_for_selection()
        if not server_id:
            wx.MessageBox(
                "Please select a server first.", "No Server Selected", wx.OK | wx.ICON_WARNING
            )
            return

        server_name = self._get_server_name_for_selection()
        dlg = AccountEditorDialog(
            self, self.config_manager, server_id, account_id=None, server_name=server_name
        )
        new_account_id = None
        if dlg.ShowModal() == wx.ID_OK:
            new_account_id = dlg.get_account_id()
            self._populate_tree(select_server_id=server_id, select_account_id=new_account_id)
        dlg.Destroy()

        if new_account_id:
            prompt = wx.MessageBox(
                "Account added. Would you like to log in with this account now?\nBy default, a server will accept new created accounts by users.",
                "Log In Now?",
                wx.YES_NO | wx.ICON_QUESTION,
            )
            if prompt == wx.YES:
                self.on_login(None)
                return

        self.tree.SetFocus()

    def on_edit(self, event):
        """Edit the selected server or account."""
        item_type, server_id, account_id = self._get_selected_item_data()

        if item_type == "server":
            from .server_manager import ServerEditorDialog

            dlg = ServerEditorDialog(self, self.config_manager, server_id)
            if dlg.ShowModal() == wx.ID_OK:
                self._populate_tree(select_server_id=server_id)
            dlg.Destroy()
        elif item_type == "account":
            from .server_manager import AccountEditorDialog

            server_name = self._get_server_name_for_selection()
            dlg = AccountEditorDialog(
                self, self.config_manager, server_id, account_id, server_name=server_name
            )
            if dlg.ShowModal() == wx.ID_OK:
                self._populate_tree(select_server_id=server_id, select_account_id=account_id)
            dlg.Destroy()

        self.tree.SetFocus()

    def on_delete(self, event):
        """Delete the selected server or account."""
        item_type, server_id, account_id = self._get_selected_item_data()
        sel = self.tree.GetSelection()

        if item_type == "server":
            server_name = self.tree.GetItemText(sel)
            result = wx.MessageBox(
                f"Delete server '{server_name}' and all its accounts?",
                "Confirm Delete",
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
            )
            if result == wx.YES:
                self.config_manager.delete_server(server_id)
                self._populate_tree()

        elif item_type == "account":
            server_name = self._get_server_name_for_selection()
            username = self.tree.GetItemText(sel)
            result = wx.MessageBox(
                f"Delete account '{username}' from {server_name}?",
                "Confirm Delete",
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
            )
            if result == wx.YES:
                self.config_manager.delete_account(server_id, account_id)
                self._populate_tree(select_server_id=server_id)

        self.tree.SetFocus()

    def on_advanced(self, event):
        """Show advanced options menu (import, export, default options profile)."""
        menu = wx.Menu()
        import_id = wx.NewIdRef()
        export_id = wx.NewIdRef()
        options_id = wx.NewIdRef()

        menu.Append(import_id, "&Import Server Profiles")
        menu.Append(export_id, "E&xport Server Profiles")
        menu.Append(options_id, "Default &Options Profile")

        menu.Bind(wx.EVT_MENU, self._on_import_profiles, id=import_id)
        menu.Bind(wx.EVT_MENU, self._on_export_profiles, id=export_id)
        menu.Bind(wx.EVT_MENU, self._on_default_options_profile, id=options_id)

        self.PopupMenu(menu)
        menu.Destroy()

    def _on_import_profiles(self, event):
        """Handle import server profiles."""
        imported_data = self._load_import_file()
        if imported_data is None:
            return

        dlg = ConfigSharingDialog(
            self,
            self.config_manager,
            ConfigSharingDialog.MODE_IMPORT,
            imported_data=imported_data,
        )
        if dlg._no_data:
            dlg.Destroy()
            wx.MessageBox(
                "There is no data to import. All servers in this file either already "
                "exist with no changes, or the file contains no servers.",
                "Nothing to Import",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_OK:
            self._populate_tree()

    def _on_export_profiles(self, event):
        """Handle export server profiles."""
        servers = self.config_manager.get_all_servers()
        if not servers:
            wx.MessageBox(
                "No servers to export.",
                "Export",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        dlg = ConfigSharingDialog(self, self.config_manager, ConfigSharingDialog.MODE_EXPORT)
        dlg.ShowModal()
        dlg.Destroy()

    def _on_default_options_profile(self, event):
        """Handle default options profile."""
        wx.MessageBox(
            "Not implemented yet.",
            "Default Options Profile",
            wx.OK | wx.ICON_INFORMATION,
        )

    def _load_import_file(self):
        """Load an import file, with auto-detection and browser fallback.

        Returns:
            Parsed dict if a valid file was loaded, or None to abort.
        """
        auto_path = Path.cwd() / "identities-export.json"

        # Auto-detect file in cwd
        if auto_path.exists():
            data = try_load_export_file(str(auto_path))
            if data:
                desc = data.get("description", "")
                ts = format_export_timestamp(data.get("timestamp", 0))
                result = wx.MessageBox(
                    f"Found export file in current directory.\n\n"
                    f"Description: {desc}\n"
                    f"Date: {ts}\n\n"
                    f"Would you like to load this file?",
                    "Import Server Profiles",
                    wx.YES_NO | wx.ICON_QUESTION,
                )
                if result == wx.YES:
                    return data

        # File browser loop
        while True:
            file_dlg = wx.FileDialog(
                self,
                "Select Export File to Import",
                defaultDir=str(Path.cwd()),
                wildcard="JSON files (*.json)|*.json",
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            )
            if file_dlg.ShowModal() != wx.ID_OK:
                file_dlg.Destroy()
                return None
            chosen_path = file_dlg.GetPath()
            file_dlg.Destroy()

            data = try_load_export_file(chosen_path)
            if data is None:
                wx.MessageBox(
                    "The selected file is not a valid export file.",
                    "Invalid File",
                    wx.OK | wx.ICON_ERROR,
                )
                continue

            # Confirm file details
            desc = data.get("description", "")
            ts = format_export_timestamp(data.get("timestamp", 0))
            result = wx.MessageBox(
                f"Description: {desc}\nDate: {ts}\n\nWould you like to import this file?",
                "Confirm Import File",
                wx.YES_NO | wx.ICON_QUESTION,
            )
            if result == wx.YES:
                return data
            # If No, return to file browser

    def on_login(self, event):
        """Handle login button click or account activation."""
        item_type, server_id, account_id = self._get_selected_item_data()

        if item_type != "account" or not server_id or not account_id:
            wx.MessageBox("Please select an account.", "Error", wx.OK | wx.ICON_ERROR)
            self.tree.SetFocus()
            return

        # Get account credentials
        account = self.config_manager.get_account_by_id(server_id, account_id)
        if not account:
            wx.MessageBox("Account not found.", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.server_id = server_id
        self.account_id = account_id
        self.username = account.get("username", "")
        self.user_input_value = account.get("password", "")
        self.refresh_token = account.get("refresh_token")
        self.refresh_expires_at = account.get("refresh_expires_at")
        self.server_url = self.config_manager.get_server_url(server_id)

        # Save last used server and account
        self.config_manager.set_last_account(server_id, account_id)

        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        """Handle cancel button click."""
        self.EndModal(wx.ID_CANCEL)

    def get_credentials(self):
        """Get the login credentials."""
        return {
            "username": self.username,
            "password": self.user_input_value,
            "refresh_token": self.refresh_token,
            "refresh_expires_at": self.refresh_expires_at,
            "server_url": self.server_url,
            "server_id": self.server_id,
            "account_id": self.account_id,
            "config_manager": self.config_manager,
        }
