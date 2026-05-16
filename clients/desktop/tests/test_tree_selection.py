import sys

import pytest
import wx

from ui.enhance_wx.list_selection import FocusAfterDelete
from ui.enhance_wx.tree_selection import ManagedTreeCtrl


def _build_tree(control):
    root = control.AddRoot("")
    server_a = control.AppendItem(root, "Server A")
    account_a1 = control.AppendItem(server_a, "alice")
    account_a2 = control.AppendItem(server_a, "bob")
    server_b = control.AppendItem(root, "Server B")
    control.SetItemData(server_a, ("server", "srv-a", None))
    control.SetItemData(account_a1, ("account", "srv-a", "acct-a1"))
    control.SetItemData(account_a2, ("account", "srv-a", "acct-a2"))
    control.SetItemData(server_b, ("server", "srv-b", None))
    return root, server_a, account_a1, account_a2, server_b


def test_managed_tree_ctrl_tracks_children_and_item_data(wx_app):
    frame = wx.Frame(None)
    panel = wx.Panel(frame)
    tree = ManagedTreeCtrl(panel, name="Test tree")
    try:
        root, server_a, account_a1, account_a2, server_b = _build_tree(tree)

        first_server, cookie = tree.GetFirstChild(root)
        second_server, next_cookie = tree.GetNextChild(root, cookie)
        end_item, end_cookie = tree.GetNextChild(root, next_cookie)

        assert first_server.IsOk()
        assert tree.GetItemText(first_server) == "Server A"
        assert second_server.IsOk()
        assert tree.GetItemText(second_server) == "Server B"
        assert not end_item.IsOk()
        assert end_cookie is None

        assert tree.GetChildrenCount(root, False) == 2
        assert tree.GetChildrenCount(server_a, False) == 2
        assert tree.GetChildrenCount(root, True) == 4
        assert tree.GetItemParent(account_a1) == server_a
        assert tree.GetItemData(account_a2) == ("account", "srv-a", "acct-a2")
    finally:
        frame.Destroy()


def test_managed_tree_ctrl_select_after_delete_prefers_configured_neighbor(wx_app):
    frame = wx.Frame(None)
    panel = wx.Panel(frame)
    tree = ManagedTreeCtrl(panel, name="Test tree", focus_after_delete=FocusAfterDelete.NEXT)
    try:
        root, server_a, account_a1, account_a2, server_b = _build_tree(tree)

        tree.select_after_delete(server_a, account_a1, account_a2)
        selection = tree.GetSelection()

        assert selection.IsOk()
        assert tree.GetItemText(selection) == "bob"

        tree.select_after_delete(root, server_a, server_b)
        selection = tree.GetSelection()

        assert selection.IsOk()
        assert tree.GetItemText(selection) == "Server B"
    finally:
        frame.Destroy()


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS TreeListCtrl shim only")
def test_managed_tree_ctrl_delete_all_items_resets_bookkeeping(wx_app):
    frame = wx.Frame(None)
    panel = wx.Panel(frame)
    tree = ManagedTreeCtrl(panel, name="Test tree")
    try:
        root, server_a, account_a1, account_a2, server_b = _build_tree(tree)

        tree.DeleteAllItems()

        root = tree.GetRootItem()
        first_child, cookie = tree.GetFirstChild(root)

        assert tree.GetChildrenCount(root, False) == 0
        assert not first_child.IsOk()
        assert cookie is None
        assert tree.GetItemData(server_a) is None
    finally:
        frame.Destroy()


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS TreeListCtrl shim only")
def test_managed_tree_ctrl_rejects_unsupported_tree_event_binders(wx_app):
    frame = wx.Frame(None)
    panel = wx.Panel(frame)
    tree = ManagedTreeCtrl(panel, name="Test tree")
    try:
        with pytest.raises(NotImplementedError):
            tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, lambda evt: None)
    finally:
        frame.Destroy()
