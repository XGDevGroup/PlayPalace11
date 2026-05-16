from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types


def _load_markdown_viewer_dialog_module():
    if "wx" not in sys.modules:
        wx_module = types.ModuleType("wx")

        class _Dialog:
            pass

        class _Panel:
            def __init__(self, *args, **kwargs):
                pass

            def SetSizer(self, *args, **kwargs):
                pass

        class _BoxSizer:
            def __init__(self, *args, **kwargs):
                pass

            def Add(self, *args, **kwargs):
                pass

        class _Button:
            def __init__(self, *args, **kwargs):
                pass

            def Bind(self, *args, **kwargs):
                pass

        class _AcceleratorTable:
            def __init__(self, *args, **kwargs):
                pass

        class _AcceleratorEntry:
            def __init__(self, *args, **kwargs):
                pass

        class _Color:
            def Red(self):
                return 0

            def Green(self):
                return 0

            def Blue(self):
                return 0

        class _SystemSettings:
            @staticmethod
            def GetColour(_color_id):
                return _Color()

        wx_module.Dialog = _Dialog
        wx_module.Panel = _Panel
        wx_module.BoxSizer = _BoxSizer
        wx_module.Button = _Button
        wx_module.AcceleratorTable = _AcceleratorTable
        wx_module.AcceleratorEntry = _AcceleratorEntry
        wx_module.SystemSettings = _SystemSettings
        wx_module.DEFAULT_DIALOG_STYLE = 0
        wx_module.RESIZE_BORDER = 0
        wx_module.VERTICAL = 0
        wx_module.EXPAND = 0
        wx_module.ALL = 0
        wx_module.ALIGN_RIGHT = 0
        wx_module.ID_CLOSE = 0
        wx_module.EVT_BUTTON = object()
        wx_module.EVT_CLOSE = object()
        wx_module.ACCEL_NORMAL = 0
        wx_module.WXK_ESCAPE = 27
        wx_module.SYS_COLOUR_WINDOW = 0
        wx_module.SYS_COLOUR_WINDOWTEXT = 1
        wx_module.SYS_COLOUR_GRAYTEXT = 2
        wx_module.SYS_COLOUR_HOTLIGHT = 3

        wx_html2_module = types.ModuleType("wx.html2")

        class _WebView:
            @staticmethod
            def New(*args, **kwargs):
                return _WebView()

            def Bind(self, *args, **kwargs):
                pass

            def SetPage(self, *args, **kwargs):
                pass

            def SetFocus(self):
                pass

            def RunScript(self, *args, **kwargs):
                pass

        wx_html2_module.WebView = _WebView
        wx_html2_module.EVT_WEBVIEW_LOADED = object()
        wx_html2_module.EVT_WEBVIEW_NAVIGATING = object()

        wx_module.html2 = wx_html2_module
        sys.modules["wx"] = wx_module
        sys.modules["wx.html2"] = wx_html2_module

    module_path = Path(__file__).resolve().parents[1] / "ui" / "markdown_viewer_dialog.py"
    spec = spec_from_file_location("test_markdown_viewer_dialog", module_path)
    module = module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


markdown_viewer_dialog = _load_markdown_viewer_dialog_module()
sanitize_markdown = markdown_viewer_dialog.sanitize_markdown
should_allow_navigation = markdown_viewer_dialog.should_allow_navigation


def test_sanitize_markdown_strips_scripts_and_event_handlers():
    html = sanitize_markdown("[x](javascript:alert(1))\n\n<script>alert(1)</script>\n\n<span onclick=\"x()\">ok</span>")

    assert "javascript:" not in html
    assert "<script" not in html
    assert "onclick" not in html
    assert "ok" in html


def test_sanitize_markdown_strips_remote_images():
    html = sanitize_markdown("![track](https://tracker.example/pixel.png)")

    assert "<img" not in html
    assert "tracker.example" not in html


def test_should_allow_navigation_only_for_initial_internal_load():
    assert should_allow_navigation("", document_loaded=False)
    assert should_allow_navigation("about:blank", document_loaded=False)
    assert not should_allow_navigation("https://example.com", document_loaded=False)
    assert not should_allow_navigation("https://example.com", document_loaded=True)
