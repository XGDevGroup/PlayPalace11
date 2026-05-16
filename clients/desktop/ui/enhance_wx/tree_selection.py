"""
Selection management for wxPython tree controls.

Provides a mixin and ready-to-use control that automatically manages selection
state for tree controls:
- Auto-focus first item when control gains focus with no selection
- Helper to maintain valid selection after item deletion

Includes:
- TreeSelectionManagerMixin: For wx.TreeCtrl-style controls
- ManagedTreeCtrl: Ready-to-use tree with selection management

Requires: wxPython
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any

import wx

from .list_selection import FocusAfterDelete

if sys.platform == "darwin":
    import wx.dataview as dv


# =============================================================================
# MIXIN
# =============================================================================


class TreeSelectionManagerMixin:
    """
    Mixin that manages selection for wx.TreeCtrl-style controls.

    Features:
    - Auto-selects first visible item when focused with no selection
    - Provides select_after_delete() to maintain valid selection after removal

    Args:
        focus_after_delete: Where to focus after deleting an item.
            FocusAfterDelete.PREVIOUS (default) or FocusAfterDelete.NEXT
    """

    def __init__(
        self,
        *args: Any,
        focus_after_delete: FocusAfterDelete = FocusAfterDelete.PREVIOUS,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.focus_after_delete = focus_after_delete
        self.Bind(wx.EVT_SET_FOCUS, self._on_tree_focus_ensure_selection)

    def _on_tree_focus_ensure_selection(self, evt: wx.FocusEvent) -> None:
        """Auto-select first visible item when tree gains focus with no selection."""
        evt.Skip()
        sel = self.GetSelection()
        if sel.IsOk():
            return
        root = self.GetRootItem()
        if not root.IsOk():
            return
        first_child, _ = self.GetFirstChild(root)
        if first_child.IsOk():
            self.SelectItem(first_child)

    def select_after_delete(
        self,
        parent: wx.TreeItemId,
        prev_sibling: wx.TreeItemId | None,
        next_sibling: wx.TreeItemId | None,
    ) -> None:
        """Select an appropriate item after deletion.

        Call this AFTER deleting a tree item to move selection to the
        previous sibling, next sibling, or parent -- in order of preference
        based on the focus_after_delete setting.

        Args:
            parent: Parent of the deleted item.
            prev_sibling: Sibling before the deleted item, or None.
            next_sibling: Sibling after the deleted item, or None.
        """
        if self.focus_after_delete == FocusAfterDelete.PREVIOUS:
            primary, fallback = prev_sibling, next_sibling
        else:
            primary, fallback = next_sibling, prev_sibling

        target = None
        if primary and primary.IsOk():
            target = primary
        elif fallback and fallback.IsOk():
            target = fallback
        elif parent and parent.IsOk() and parent != self.GetRootItem():
            target = parent

        if target:
            self.SelectItem(target)


if sys.platform == "darwin":
    _EVENT_BINDER_MAP: dict[wx.PyEventBinder, wx.PyEventBinder] = {
        wx.EVT_TREE_SEL_CHANGED: dv.EVT_TREELIST_SELECTION_CHANGED,
        wx.EVT_TREE_ITEM_ACTIVATED: dv.EVT_TREELIST_ITEM_ACTIVATED,
    }
    _TREE_EVENT_BINDERS = tuple(
        getattr(wx, name)
        for name in dir(wx)
        if name.startswith("EVT_TREE_") and isinstance(getattr(wx, name), wx.PyEventBinder)
    )

    class _MacManagedTreeCtrl(dv.TreeListCtrl):
        """A macOS-friendly tree control backed by DataView for VoiceOver."""

        def __init__(
            self,
            parent: wx.Window,
            id: int = wx.ID_ANY,
            pos: wx.Point = wx.DefaultPosition,
            size: wx.Size = wx.DefaultSize,
            style: int = 0,
            focus_after_delete: FocusAfterDelete = FocusAfterDelete.PREVIOUS,
            **kwargs: Any,
        ) -> None:
            # TreeCtrl style flags do not apply to TreeListCtrl, so they are ignored here.
            super().__init__(parent, id=id, pos=pos, size=size, **kwargs)
            self.AppendColumn("", width=wx.COL_WIDTH_AUTOSIZE)
            self.focus_after_delete = focus_after_delete
            self._compat_root = super().GetRootItem()
            self._item_data: dict[object, object] = {}
            self._parent_by_item: dict[object, dv.TreeListItem] = {}
            self._children_by_parent: dict[object, list[dv.TreeListItem]] = {
                self._item_key(self._compat_root): []
            }
            self.Bind(wx.EVT_SET_FOCUS, self._on_tree_focus_ensure_selection)

        @staticmethod
        def _item_key(item: dv.TreeListItem) -> object | None:
            """Return a stable key for a tree item."""
            if not item:
                return None
            get_id = getattr(item, "GetID", None)
            if callable(get_id):
                return get_id()
            return item

        def _bind_event(self, event: wx.PyEventBinder) -> wx.PyEventBinder:
            """Map TreeCtrl event binders to TreeListCtrl equivalents."""
            mapped_event = _EVENT_BINDER_MAP.get(event)
            if mapped_event is not None:
                return mapped_event
            if event in _TREE_EVENT_BINDERS:
                raise NotImplementedError(
                    "ManagedTreeCtrl on macOS does not support this wx.TreeCtrl event binder."
                )
            return event

        def Bind(
            self,
            event: wx.PyEventBinder,
            handler: Callable[..., object],
            *args: Any,
            **kwargs: Any,
        ) -> None:
            """Bind handlers using wx.TreeCtrl-compatible event names."""
            super().Bind(self._bind_event(event), handler, *args, **kwargs)

        def _on_tree_focus_ensure_selection(self, evt: wx.FocusEvent) -> None:
            """Auto-select the first visible item when focus lands on the tree."""
            evt.Skip()
            sel = self.GetSelection()
            if sel and sel.IsOk():
                return
            first_child, _ = self.GetFirstChild(self.GetRootItem())
            if first_child and first_child.IsOk():
                self.SelectItem(first_child)

        def GetRootItem(self) -> dv.TreeListItem:
            """Return the compatibility root item."""
            return self._compat_root

        def AddRoot(self, text: str) -> dv.TreeListItem:
            """Match wx.TreeCtrl's explicit-root API without creating a visible node."""
            return self._compat_root

        def AppendItem(self, parent: dv.TreeListItem, text: str) -> dv.TreeListItem:
            """Append a child item and track parent/child relationships."""
            item = super().AppendItem(parent, text)
            parent_key = self._item_key(parent)
            item_key = self._item_key(item)
            self._parent_by_item[item_key] = parent
            self._children_by_parent.setdefault(parent_key, []).append(item)
            self._children_by_parent.setdefault(item_key, [])
            return item

        def DeleteAllItems(self) -> None:
            """Clear all items and compatibility bookkeeping."""
            super().DeleteAllItems()
            self._compat_root = super().GetRootItem()
            self._item_data.clear()
            self._parent_by_item.clear()
            self._children_by_parent = {self._item_key(self._compat_root): []}

        def SetItemData(self, item: dv.TreeListItem, data: object) -> None:
            """Store arbitrary item data like wx.TreeCtrl does."""
            self._item_data[self._item_key(item)] = data

        def GetItemData(self, item: dv.TreeListItem) -> object | None:
            """Return previously stored item data."""
            return self._item_data.get(self._item_key(item))

        def GetFirstChild(
            self, parent: dv.TreeListItem
        ) -> tuple[dv.TreeListItem, dv.TreeListItem | None]:
            """Return the first child and a cookie for GetNextChild()."""
            children = self._children_by_parent.get(self._item_key(parent), [])
            if not children:
                return dv.TreeListItem(), None
            first_child = children[0]
            return first_child, first_child

        def GetNextChild(
            self, parent: dv.TreeListItem, cookie: dv.TreeListItem | None
        ) -> tuple[dv.TreeListItem, dv.TreeListItem | None]:
            """Return the next child and updated cookie."""
            children = self._children_by_parent.get(self._item_key(parent), [])
            if not cookie:
                return dv.TreeListItem(), None
            try:
                index = children.index(cookie) + 1
            except ValueError:
                return dv.TreeListItem(), None
            if index >= len(children):
                return dv.TreeListItem(), None
            next_child = children[index]
            return next_child, next_child

        def GetItemParent(self, item: dv.TreeListItem) -> dv.TreeListItem:
            """Return the item's parent."""
            return self._parent_by_item.get(self._item_key(item), dv.TreeListItem())

        def GetChildrenCount(self, parent: dv.TreeListItem, recursively: bool = False) -> int:
            """Return the number of direct or recursive children."""
            children = self._children_by_parent.get(self._item_key(parent), [])
            if not recursively:
                return len(children)
            return len(children) + sum(self.GetChildrenCount(child, True) for child in children)

        def SelectItem(self, item: dv.TreeListItem) -> None:
            """Select an item using wx.TreeCtrl naming."""
            self.Select(item)

        def GetItemText(self, item: dv.TreeListItem, column: int = 0) -> str:
            """Return item text using wx.TreeCtrl's columnless default."""
            return super().GetItemText(item, column)

        def SetItemText(self, item: dv.TreeListItem, text: str, column: int = 0) -> None:
            """Set item text using a wx.TreeCtrl-compatible signature."""
            super().SetItemText(item, column, text)

        def select_after_delete(
            self,
            parent: dv.TreeListItem,
            prev_sibling: dv.TreeListItem | None,
            next_sibling: dv.TreeListItem | None,
        ) -> None:
            """Select an appropriate item after deletion, matching TreeSelectionManagerMixin."""
            if self.focus_after_delete == FocusAfterDelete.PREVIOUS:
                primary, fallback = prev_sibling, next_sibling
            else:
                primary, fallback = next_sibling, prev_sibling

            target = None
            if primary and primary.IsOk():
                target = primary
            elif fallback and fallback.IsOk():
                target = fallback
            elif parent and parent.IsOk() and parent != self.GetRootItem():
                target = parent

            if target:
                self.SelectItem(target)

    ManagedTreeCtrl = _MacManagedTreeCtrl

else:

    # =============================================================================
    # READY-TO-USE CONTROL
    # =============================================================================

    class ManagedTreeCtrl(TreeSelectionManagerMixin, wx.TreeCtrl):
        """A wx.TreeCtrl with automatic selection management."""

        pass
