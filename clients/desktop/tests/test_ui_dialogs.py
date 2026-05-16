import pytest
import wx

from ui.login_dialog import LoginDialog
from ui.server_manager import AccountEditorDialog, ServerEditorDialog


class StubConfigManager:
    def __init__(self):
        self.servers = {
            "srv-1": {
                "name": "Localhost",
                "host": "localhost",
                "port": 8000,
                "accounts": {
                    "acct-1": {
                        "username": "alice",
                        "password": "secret",
                        "email": "alice@example.com",
                        "notes": "admin",
                        "refresh_token": None,
                        "refresh_expires_at": None,
                    }
                },
            },
            "srv-2": {
                "name": "Production",
                "host": "prod.example.com",
                "port": 8000,
                "accounts": {},
            },
        }
        self.last_server = "srv-1"
        self.last_account = "acct-1"
        self.add_calls = []
        self.update_calls = []
        self.add_server_calls = []
        self.update_server_calls = []
        self.delete_server_calls = []
        self.delete_account_calls = []
        self.last_account_calls = []

    def get_all_servers(self):
        return self.servers

    def get_server_by_id(self, server_id):
        return self.servers.get(server_id)

    def get_server_accounts(self, server_id):
        server = self.servers.get(server_id)
        return server["accounts"] if server else {}

    def get_last_server_id(self):
        return self.last_server

    def get_last_account_id(self, server_id):
        return self.last_account if server_id == self.last_server else None

    def get_server_url(self, server_id):
        server = self.servers.get(server_id)
        if not server:
            return None
        return f"ws://{server['host']}:{server['port']}"

    def add_account(self, server_id, username, password, email="", notes=""):
        self.add_calls.append(
            (
                server_id,
                {"username": username, "password": password, "email": email, "notes": notes},
            )
        )
        return "acct-new"

    def add_server(self, name, host, port, notes=""):
        self.add_server_calls.append(
            {"name": name, "host": host, "port": port, "notes": notes}
        )
        sid = f"srv-new-{len(self.add_server_calls)}"
        self.servers[sid] = {
            "name": name, "host": host, "port": port, "notes": notes, "accounts": {}
        }
        return sid

    def update_server(self, server_id, **kwargs):
        self.update_server_calls.append({"id": server_id, **kwargs})
        if server_id in self.servers:
            self.servers[server_id].update(kwargs)

    def update_account(self, server_id, account_id, **kwargs):
        self.update_calls.append((server_id, account_id, kwargs))

    def get_account_by_id(self, server_id, account_id):
        server = self.servers.get(server_id)
        if not server:
            return None
        return server["accounts"].get(account_id)

    def set_last_account(self, server_id, account_id):
        self.last_account_calls.append((server_id, account_id))

    def delete_server(self, server_id):
        self.delete_server_calls.append(server_id)
        self.servers.pop(server_id, None)

    def delete_account(self, server_id, account_id):
        self.delete_account_calls.append((server_id, account_id))
        server = self.servers.get(server_id)
        if server:
            server["accounts"].pop(account_id, None)


@pytest.fixture
def messagebox_spy(monkeypatch):
    calls = []

    def fake_messagebox(message, caption, style):
        calls.append({"message": message, "caption": caption, "style": style})
        return wx.ID_OK

    monkeypatch.setattr(wx, "MessageBox", fake_messagebox)
    return calls


def _make_login_dialog(monkeypatch, stub=None):
    """Create a LoginDialog backed by a StubConfigManager."""
    stub = stub or StubConfigManager()
    monkeypatch.setattr("ui.login_dialog.ConfigManager", lambda: stub)
    dlg = LoginDialog(None)
    return dlg, stub


def _count_top_level_items(tree):
    """Count top-level children (servers) in the tree."""
    root = tree.GetRootItem()
    count = 0
    item, cookie = tree.GetFirstChild(root)
    while item.IsOk():
        count += 1
        item, cookie = tree.GetNextChild(root, cookie)
    return count


def _count_children(tree, parent):
    """Count direct children of a tree item."""
    count = 0
    item, cookie = tree.GetFirstChild(parent)
    while item.IsOk():
        count += 1
        item, cookie = tree.GetNextChild(parent, cookie)
    return count


def _get_first_server_item(tree):
    """Get the first top-level (server) item."""
    root = tree.GetRootItem()
    item, _ = tree.GetFirstChild(root)
    return item


def _get_second_server_item(tree):
    """Get the second top-level (server) item."""
    root = tree.GetRootItem()
    first, cookie = tree.GetFirstChild(root)
    second, _ = tree.GetNextChild(root, cookie)
    return second


def _get_first_account_item(tree):
    """Get the first account (child of first server)."""
    server = _get_first_server_item(tree)
    item, _ = tree.GetFirstChild(server)
    return item


# =============================================================================
# Login dialog tree tests
# =============================================================================


def test_login_dialog_populates_servers(wx_app, monkeypatch):
    dlg, stub = _make_login_dialog(monkeypatch)
    try:
        assert _count_top_level_items(dlg.tree) == len(stub.servers)

        # First server should have 1 account child
        first_server = _get_first_server_item(dlg.tree)
        assert _count_children(dlg.tree, first_server) == 1

        # Second server should have 0 account children
        second_server = _get_second_server_item(dlg.tree)
        assert _count_children(dlg.tree, second_server) == 0
    finally:
        dlg.Destroy()


def test_login_dialog_selects_last_used_account(wx_app, monkeypatch):
    dlg, stub = _make_login_dialog(monkeypatch)
    try:
        sel = dlg.tree.GetSelection()
        assert sel.IsOk()
        data = dlg.tree.GetItemData(sel)
        assert data == ("account", "srv-1", "acct-1")
    finally:
        dlg.Destroy()


def test_login_dialog_button_states_on_account_select(wx_app, monkeypatch):
    dlg, stub = _make_login_dialog(monkeypatch)
    try:
        # Account is pre-selected (last used)
        assert dlg.login_btn.IsEnabled()
        assert dlg.edit_btn.IsEnabled()
        assert dlg.delete_btn.IsEnabled()
        assert dlg.add_account_btn.IsEnabled()
        assert "&Edit Account" in dlg.edit_btn.GetLabel()
        assert "&Delete Account" in dlg.delete_btn.GetLabel()
    finally:
        dlg.Destroy()


def test_login_dialog_button_states_on_server_select(wx_app, monkeypatch):
    dlg, stub = _make_login_dialog(monkeypatch)
    try:
        # Select a server node (second server, no accounts)
        second_server = _get_second_server_item(dlg.tree)
        dlg.tree.SelectItem(second_server)
        dlg._update_button_states()

        assert not dlg.login_btn.IsEnabled()
        assert dlg.edit_btn.IsEnabled()
        assert dlg.delete_btn.IsEnabled()
        assert "&Edit Server" in dlg.edit_btn.GetLabel()
        assert "&Delete Server" in dlg.delete_btn.GetLabel()
        assert "Production" in dlg.add_account_btn.GetLabel()
    finally:
        dlg.Destroy()


def test_login_dialog_button_states_empty_tree(wx_app, monkeypatch):
    stub = StubConfigManager()
    stub.servers = {}
    stub.last_server = None
    dlg, _ = _make_login_dialog(monkeypatch, stub)
    try:
        assert _count_top_level_items(dlg.tree) == 0
        assert not dlg.login_btn.IsEnabled()
        assert not dlg.edit_btn.IsEnabled()
        assert not dlg.delete_btn.IsEnabled()
        assert not dlg.add_account_btn.IsEnabled()
    finally:
        dlg.Destroy()


def test_login_dialog_login_reads_credentials(wx_app, monkeypatch):
    dlg, stub = _make_login_dialog(monkeypatch)
    try:
        # Prevent EndModal from raising (dialog is not shown modally in tests)
        monkeypatch.setattr(dlg, "EndModal", lambda code: None)

        # Account is pre-selected, simulate login
        dlg.on_login(wx.CommandEvent())
        creds = dlg.get_credentials()
        assert creds["username"] == "alice"
        assert creds["password"] == "secret"
        assert creds["server_id"] == "srv-1"
        assert creds["account_id"] == "acct-1"
        assert creds["server_url"] == "ws://localhost:8000"
        assert creds["config_manager"] is stub
        assert stub.last_account_calls == [("srv-1", "acct-1")]
    finally:
        dlg.Destroy()


def test_login_dialog_login_fails_without_account(wx_app, monkeypatch, messagebox_spy):
    dlg, stub = _make_login_dialog(monkeypatch)
    try:
        # Select a server node (no account)
        second_server = _get_second_server_item(dlg.tree)
        dlg.tree.SelectItem(second_server)

        dlg.on_login(wx.CommandEvent())
        assert messagebox_spy[-1]["message"] == "Please select an account."
    finally:
        dlg.Destroy()


class _FakeTreeEvent:
    """Minimal stand-in for wx.TreeEvent in tests."""

    def __init__(self, item):
        self._item = item

    def GetItem(self):
        return self._item


def test_login_dialog_activate_account_triggers_login(wx_app, monkeypatch):
    dlg, stub = _make_login_dialog(monkeypatch)
    try:
        # Prevent EndModal from raising (dialog is not shown modally in tests)
        monkeypatch.setattr(dlg, "EndModal", lambda code: None)

        # Simulate EVT_TREE_ITEM_ACTIVATED on the account item
        acct_item = _get_first_account_item(dlg.tree)
        dlg.tree.SelectItem(acct_item)
        dlg._on_tree_item_activated(_FakeTreeEvent(acct_item))

        # Login should have set credentials
        assert dlg.username == "alice"
        assert dlg.server_id == "srv-1"
    finally:
        dlg.Destroy()


def test_login_dialog_activate_server_does_not_login(wx_app, monkeypatch):
    dlg, stub = _make_login_dialog(monkeypatch)
    try:
        first_server = _get_first_server_item(dlg.tree)
        dlg.tree.SelectItem(first_server)
        dlg._on_tree_item_activated(_FakeTreeEvent(first_server))

        # Login should NOT have been triggered
        assert dlg.username == ""
        assert dlg.server_id is None
    finally:
        dlg.Destroy()


# =============================================================================
# Account editor dialog tests
# =============================================================================


def test_account_editor_dialog_creates_account(wx_app):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1")
    try:
        dlg.username_input.SetValue("newuser")
        dlg.password_input.SetValue("p@ss")
        dlg.email_input.SetValue("new@example.com")
        dlg.notes_input.SetValue("note")

        assert dlg._save_if_needed()
        assert stub.add_calls

        # Toggle password visibility
        dlg.on_show_password(wx.CommandEvent())
        assert dlg.password_plain.IsShown()
    finally:
        dlg.Destroy()


def test_account_editor_dialog_updates_existing_account(wx_app):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1", "acct-1")
    try:
        dlg.username_input.SetValue("alice-new")
        dlg.password_input.SetValue("new-secret")
        dlg.email_input.SetValue("alice+demo@example.com")
        dlg.notes_input.SetValue("updated")

        assert dlg._save_if_needed()
        assert stub.update_calls[-1] == (
            "srv-1",
            "acct-1",
            {
                "username": "alice-new",
                "password": "new-secret",
                "email": "alice+demo@example.com",
                "notes": "updated",
            },
        )
    finally:
        dlg.Destroy()


def test_account_editor_dialog_title_includes_server_name(wx_app):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1", server_name="Localhost")
    try:
        assert "Localhost" in dlg.GetTitle()
        assert "Add Account" in dlg.GetTitle()
    finally:
        dlg.Destroy()

    dlg2 = AccountEditorDialog(None, stub, "srv-1", "acct-1", server_name="Localhost")
    try:
        assert "Localhost" in dlg2.GetTitle()
        assert "Edit Account" in dlg2.GetTitle()
    finally:
        dlg2.Destroy()


def test_account_editor_validation_requires_username(wx_app, messagebox_spy):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1")
    try:
        dlg.username_input.SetValue("")
        dlg.password_input.SetValue("pass")
        assert dlg._validate_for_close() is False
        assert messagebox_spy[-1]["message"] == "Username cannot be empty."
    finally:
        dlg.Destroy()


def test_account_editor_validation_requires_password(wx_app, messagebox_spy):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1")
    try:
        dlg.username_input.SetValue("bob")
        dlg.password_input.SetValue("")
        assert dlg._validate_for_close() is False
        assert messagebox_spy[-1]["message"] == "Password cannot be empty."
    finally:
        dlg.Destroy()


def test_account_editor_validation_rejects_invalid_email(wx_app, messagebox_spy):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1")
    try:
        dlg.username_input.SetValue("carol")
        dlg.password_input.SetValue("pass")
        dlg.email_input.SetValue("bad-email@@example.com")
        assert dlg._validate_for_close() is False
        assert messagebox_spy[-1]["message"] == "Invalid email address format."
    finally:
        dlg.Destroy()


# =============================================================================
# Server/Account editor Save/Cancel flow (PR 228)
# =============================================================================


class _FakeEscapeEvent:
    def GetKeyCode(self):  # noqa: N802
        return wx.WXK_ESCAPE

    def Skip(self):
        pass


def test_server_editor_cancel_does_not_persist(wx_app, monkeypatch):
    stub = StubConfigManager()
    dlg = ServerEditorDialog(None, stub)
    try:
        ended = []
        monkeypatch.setattr(dlg, "EndModal", lambda code: ended.append(code))
        dlg.name_input.SetValue("Test")
        dlg.host_input.SetValue("h")
        dlg.port_input.SetValue("1234")
        dlg.on_cancel(None)
        assert ended == [wx.ID_CANCEL]
        assert stub.add_server_calls == []
        assert stub.update_server_calls == []
    finally:
        dlg.Destroy()


def test_server_editor_escape_returns_cancel_bypassing_validation(
    wx_app, monkeypatch, messagebox_spy
):
    stub = StubConfigManager()
    dlg = ServerEditorDialog(None, stub)
    try:
        ended = []
        monkeypatch.setattr(dlg, "EndModal", lambda code: ended.append(code))
        dlg.name_input.SetValue("")  # would trap user under old auto-save code
        dlg.on_key(_FakeEscapeEvent())
        assert ended == [wx.ID_CANCEL]
        assert stub.add_server_calls == []
        assert messagebox_spy == []  # no validation popup
    finally:
        dlg.Destroy()


def test_server_editor_save_persists_new_server(wx_app, monkeypatch):
    stub = StubConfigManager()
    dlg = ServerEditorDialog(None, stub)
    try:
        ended = []
        monkeypatch.setattr(dlg, "EndModal", lambda code: ended.append(code))
        dlg.name_input.SetValue("NewSrv")
        dlg.host_input.SetValue("example.com")
        dlg.port_input.SetValue("5555")
        dlg.on_save(None)
        assert stub.add_server_calls == [
            {"name": "NewSrv", "host": "example.com", "port": 5555, "notes": ""}
        ]
        assert ended == [wx.ID_OK]
    finally:
        dlg.Destroy()


def test_server_editor_save_blocks_on_empty_name(wx_app, monkeypatch, messagebox_spy):
    stub = StubConfigManager()
    dlg = ServerEditorDialog(None, stub)
    try:
        ended = []
        monkeypatch.setattr(dlg, "EndModal", lambda code: ended.append(code))
        dlg.name_input.SetValue("")
        dlg.host_input.SetValue("h")
        dlg.port_input.SetValue("1234")
        dlg.on_save(None)
        assert ended == []  # validation blocks EndModal
        assert stub.add_server_calls == []
        assert len(messagebox_spy) == 1
    finally:
        dlg.Destroy()


def test_server_editor_save_if_needed_handles_non_numeric_port(wx_app):
    """Bonus-bug fix: non-numeric port returns False rather than raising."""
    stub = StubConfigManager()
    dlg = ServerEditorDialog(None, stub)
    try:
        dlg.name_input.SetValue("N")
        dlg.host_input.SetValue("h")
        dlg.port_input.SetValue("notanumber")
        assert dlg._save_if_needed() is False
        assert stub.add_server_calls == []
    finally:
        dlg.Destroy()


def test_server_editor_save_gates_end_modal_on_save_result(wx_app, monkeypatch):
    """on_save must not call EndModal(wx.ID_OK) if _save_if_needed returns False."""
    stub = StubConfigManager()
    dlg = ServerEditorDialog(None, stub)
    try:
        ended = []
        monkeypatch.setattr(dlg, "EndModal", lambda code: ended.append(code))
        monkeypatch.setattr(dlg, "_validate_for_close", lambda: True)
        monkeypatch.setattr(dlg, "_save_if_needed", lambda: False)
        dlg.on_save(None)
        assert ended == []
    finally:
        dlg.Destroy()


def test_server_editor_trusted_cert_prompts_save_for_unsaved_server(wx_app, messagebox_spy):
    stub = StubConfigManager()
    dlg = ServerEditorDialog(None, stub)  # no server_id => unsaved
    try:
        dlg.on_trusted_certificate(None)
        assert len(messagebox_spy) == 1
        msg = messagebox_spy[0]["message"]
        assert "Save" in msg
        assert "Trusted Certificate" in msg
        assert stub.add_server_calls == []  # must not silently persist
    finally:
        dlg.Destroy()


def test_account_editor_cancel_does_not_persist(wx_app, monkeypatch):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1")
    try:
        ended = []
        monkeypatch.setattr(dlg, "EndModal", lambda code: ended.append(code))
        dlg.username_input.SetValue("bob")
        dlg.password_input.SetValue("pw")
        dlg.on_cancel(None)
        assert ended == [wx.ID_CANCEL]
        assert stub.add_calls == []
        assert stub.update_calls == []
    finally:
        dlg.Destroy()


def test_account_editor_escape_returns_cancel_bypassing_validation(
    wx_app, monkeypatch, messagebox_spy
):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1")
    try:
        ended = []
        monkeypatch.setattr(dlg, "EndModal", lambda code: ended.append(code))
        dlg.username_input.SetValue("")
        dlg.on_key(_FakeEscapeEvent())
        assert ended == [wx.ID_CANCEL]
        assert stub.add_calls == []
        assert messagebox_spy == []
    finally:
        dlg.Destroy()


def test_account_editor_save_persists_new_account(wx_app, monkeypatch):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1")
    try:
        ended = []
        monkeypatch.setattr(dlg, "EndModal", lambda code: ended.append(code))
        dlg.username_input.SetValue("charlie")
        dlg.password_input.SetValue("pw")
        dlg.on_save(None)
        assert len(stub.add_calls) == 1
        server_id, payload = stub.add_calls[0]
        assert server_id == "srv-1"
        assert payload["username"] == "charlie"
        assert ended == [wx.ID_OK]
    finally:
        dlg.Destroy()


def test_account_editor_save_blocks_on_empty_username(wx_app, monkeypatch, messagebox_spy):
    stub = StubConfigManager()
    dlg = AccountEditorDialog(None, stub, "srv-1")
    try:
        ended = []
        monkeypatch.setattr(dlg, "EndModal", lambda code: ended.append(code))
        dlg.username_input.SetValue("")
        dlg.password_input.SetValue("pw")
        dlg.on_save(None)
        assert ended == []
        assert stub.add_calls == []
        assert len(messagebox_spy) == 1
    finally:
        dlg.Destroy()
