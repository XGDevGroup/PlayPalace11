from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import sys
import types


def _load_markdown_viewer_dialog_module():
    if "markdown" not in sys.modules:
        markdown_module = types.ModuleType("markdown")

        def _markdown_to_html(text, extensions=None):
            text = re.sub(
                r"!\[([^\]]*)\]\(([^)]+)\)",
                lambda match: f'<img alt="{match.group(1)}" src="{match.group(2)}" />',
                text,
            )
            text = re.sub(
                r"\[([^\]]+)\]\(([^)]+)\)",
                lambda match: f'<a href="{match.group(2)}">{match.group(1)}</a>',
                text,
            )
            blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
            html_blocks = []
            for block in blocks:
                if block.startswith("<"):
                    html_blocks.append(block)
                else:
                    html_blocks.append(f"<p>{block}</p>")
            return "\n".join(html_blocks)

        markdown_module.markdown = _markdown_to_html
        sys.modules["markdown"] = markdown_module

    if "nh3" not in sys.modules:
        nh3_module = types.ModuleType("nh3")

        def _clean_html(html, tags=None, attributes=None, url_schemes=None, link_rel=None):
            cleaned = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.IGNORECASE | re.DOTALL)
            cleaned = re.sub(r'\s+on\w+="[^"]*"', "", cleaned)
            cleaned = re.sub(r'\s+on\w+=\'[^\']*\'', "", cleaned)
            cleaned = re.sub(r'(href|src)="javascript:[^"]*"', "", cleaned, flags=re.IGNORECASE)
            if link_rel:
                cleaned = re.sub(r"<a\b(?![^>]*\brel=)", f'<a rel="{link_rel}"', cleaned)
            if tags is not None and "img" not in tags:
                cleaned = re.sub(r"<img\b[^>]*>", "", cleaned)
            return cleaned

        nh3_module.clean = _clean_html
        sys.modules["nh3"] = nh3_module

    wx_module = types.ModuleType("wx")

    class _Dialog:
        def __init__(self, *args, **kwargs):
            pass

        def Bind(self, *args, **kwargs):
            pass

        def SetAcceleratorTable(self, *args, **kwargs):
            pass

        def SetSize(self, *args, **kwargs):
            pass

        def CenterOnScreen(self):
            pass

        def EndModal(self, *args, **kwargs):
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
        last_created = None

        def __init__(self):
            self.bound_events = []
            self.set_page_calls = []

        @staticmethod
        def New(*args, **kwargs):
            web_view = _WebView()
            _WebView.last_created = web_view
            return web_view

        def Bind(self, *args, **kwargs):
            self.bound_events.append((args, kwargs))

        def SetPage(self, html, base_url):
            self.set_page_calls.append((html, base_url))

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
MARKDOWN_DOCUMENT_BASE_URL = markdown_viewer_dialog.MARKDOWN_DOCUMENT_BASE_URL
MarkdownViewerDialog = markdown_viewer_dialog.MarkdownViewerDialog
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


def test_should_allow_navigation_allows_internal_document_url():
    assert should_allow_navigation(MARKDOWN_DOCUMENT_BASE_URL)


def test_should_allow_navigation_allows_internal_document_fragment():
    assert should_allow_navigation(f"{MARKDOWN_DOCUMENT_BASE_URL}#section-1")


def test_should_allow_navigation_blocks_external_url():
    assert not should_allow_navigation("https://example.com")


def test_on_webview_navigating_skips_internal_urls_and_vetoes_external_urls():
    dialog = MarkdownViewerDialog.__new__(MarkdownViewerDialog)

    class _Event:
        def __init__(self, url):
            self._url = url
            self.skipped = False
            self.vetoed = False

        def GetURL(self):
            return self._url

        def Skip(self):
            self.skipped = True

        def Veto(self):
            self.vetoed = True

    internal_event = _Event(f"{MARKDOWN_DOCUMENT_BASE_URL}#top")
    MarkdownViewerDialog._on_webview_navigating(dialog, internal_event)
    assert internal_event.skipped
    assert not internal_event.vetoed

    external_event = _Event("https://example.com")
    MarkdownViewerDialog._on_webview_navigating(dialog, external_event)
    assert external_event.vetoed
    assert not external_event.skipped


def test_create_ui_sets_page_with_explicit_internal_base_url():
    dialog = MarkdownViewerDialog(None, "Security", "hello")

    set_page_calls = dialog.web_view.set_page_calls
    assert set_page_calls
    _html, base_url = set_page_calls[-1]
    assert base_url == MARKDOWN_DOCUMENT_BASE_URL
