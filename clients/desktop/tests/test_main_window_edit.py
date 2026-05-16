import types

import pytest

from ui import main_window as main_mod


class DummyWidget:
    def __init__(self):
        self.visible = True
        self.label = ""
        self.focused = False
        self.enabled = True
        self.selection = None
        self.value = ""

    def Hide(self):
        self.visible = False

    def Show(self):
        self.visible = True

    def SetLabel(self, text):  # noqa: N802
        self.label = text

    def SetName(self, name):  # noqa: N802
        self.name = name

    def SetFocus(self):  # noqa: N802
        self.focused = True

    def IsEnabled(self):  # noqa: N802
        return self.enabled

    def SetValue(self, value):  # noqa: N802
        self.value = value

    def GetValue(self):  # noqa: N802
        return self.value

    def Clear(self):
        self.value = ""

    def SetEditable(self, _editable):  # noqa: N802
        pass

    def GetLastPosition(self):  # noqa: N802
        return len(self.value)

    def SetSelection(self, start, end):  # noqa: N802
        self.selection = (start, end)


class DummyKeyEvent:
    def __init__(self, key_code, *, shift=False, control=False, alt=False, meta=False):
        self._key_code = key_code
        self._shift = shift
        self._control = control
        self._alt = alt
        self._meta = meta
        self.skipped = False

    def GetKeyCode(self):  # noqa: N802
        return self._key_code

    def ShiftDown(self):  # noqa: N802
        return self._shift

    def ControlDown(self):  # noqa: N802
        return self._control

    def AltDown(self):  # noqa: N802
        return self._alt

    def MetaDown(self):  # noqa: N802
        return self._meta

    def Skip(self):
        self.skipped = True


def make_minimal_window(monkeypatch):
    window = main_mod.MainWindow.__new__(main_mod.MainWindow)
    window.menu_list = DummyWidget()
    window.menu_label = DummyWidget()
    window.edit_label = DummyWidget()
    window.edit_input = DummyWidget()
    window.edit_input_multiline = DummyWidget()
    window.sound_manager = types.SimpleNamespace(play=lambda *args, **kwargs: None)
    window.client_options = {}
    window.current_mode = "list"
    window.edit_mode_callback = None
    window.current_edit_read_only = False
    window.current_edit_multiline = False
    window._pending_edit_clear = False
    window._pending_multiline_clear = False
    window.menu_list.Hide()
    window.menu_label.Hide()
    window.edit_input.Hide()
    window.edit_input_multiline.Hide()
    window.edit_label.Hide()

    def immediate_call_after(func, ctrl):
        func(ctrl)

    monkeypatch.setattr(main_mod.wx, "CallAfter", immediate_call_after)
    return window


def test_switch_to_edit_mode_selects_default_value(monkeypatch):
    window = make_minimal_window(monkeypatch)

    window.switch_to_edit_mode(
        prompt="Max score", default_value="500", multiline=False, read_only=False
    )

    assert window.edit_input.selection == (0, 3)
    assert window._pending_edit_clear is True
    assert window._pending_multiline_clear is False


def test_on_edit_char_clears_pending_text(monkeypatch):
    window = make_minimal_window(monkeypatch)
    window.switch_to_edit_mode(
        prompt="Score", default_value="500", multiline=False, read_only=False
    )

    event = DummyKeyEvent(ord("1"))
    window.on_edit_char(event)

    assert window.edit_input.GetValue() == ""
    assert window._pending_edit_clear is False
    assert event.skipped is True


def test_on_edit_multiline_char_clears_pending_text(monkeypatch):
    window = make_minimal_window(monkeypatch)
    window.switch_to_edit_mode(
        prompt="Notes", default_value="Hello", multiline=True, read_only=False
    )

    event = DummyKeyEvent(ord("A"))
    window.on_edit_multiline_char(event)

    assert window.edit_input_multiline.GetValue() == ""
    assert window._pending_multiline_clear is False
    assert event.skipped is True
