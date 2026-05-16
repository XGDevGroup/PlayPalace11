"""Markdown viewer dialog for displaying rendered document content."""

import wx
import wx.html2
import markdown
import nh3


def _sys_color_hex(color_id):
    """Return a wx system colour as a CSS hex string."""
    c = wx.SystemSettings.GetColour(color_id)
    return f"#{c.Red():02x}{c.Green():02x}{c.Blue():02x}"


_MD_EXTENSIONS = [
    "tables",
    "fenced_code",
    "sane_lists",
    "nl2br",
]

# Tags that python-markdown legitimately produces.  Everything else
# (script, iframe, object, form, style, etc.) is stripped.
_ALLOWED_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "ul", "ol", "li",
    "blockquote",
    "pre", "code",
    "em", "strong", "del", "s",
    "a",
    "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "div", "span",
    "sub", "sup",
    "dl", "dt", "dd",
    "abbr",
}

_ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title", "width", "height"},
    "abbr": {"title"},
    "td": {"align"},
    "th": {"align"},
}

# Block javascript: URIs on href / src.
_ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
body {{
    font-family: "Segoe UI", system-ui, Arial, sans-serif;
    font-size: 15px;
    line-height: 1.6;
    padding: 16px 24px;
    margin: 0;
    background: {bg};
    color: {fg};
}}
h1, h2, h3, h4, h5, h6 {{
    margin-top: 1em;
    margin-bottom: 0.4em;
    line-height: 1.3;
}}
h1 {{ font-size: 1.8em; }}
h2 {{ font-size: 1.5em; }}
h3 {{ font-size: 1.25em; }}
p {{ margin: 0.6em 0; }}
ul, ol {{ padding-left: 1.8em; }}
li {{ margin: 0.3em 0; }}
table {{
    border-collapse: collapse;
    margin: 0.8em 0;
    width: 100%;
}}
th, td {{
    border: 1px solid {border};
    padding: 6px 10px;
    text-align: left;
}}
th {{
    background: {th_bg};
    font-weight: 600;
}}
code {{
    font-family: "Cascadia Code", "Consolas", monospace;
    background: {code_bg};
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 0.92em;
}}
pre {{
    background: {code_bg};
    padding: 12px 16px;
    border-radius: 4px;
    overflow-x: auto;
    line-height: 1.45;
}}
pre code {{
    background: none;
    padding: 0;
}}
a {{
    color: {link};
}}
blockquote {{
    margin: 0.8em 0;
    padding: 4px 16px;
    border-left: 4px solid {border};
    background: {code_bg};
}}
hr {{
    border: none;
    border-top: 1px solid {border};
    margin: 1.2em 0;
}}
</style>
</head>
<body>
{content}
</body>
</html>
"""


class MarkdownViewerDialog(wx.Dialog):
    """Modal dialog for viewing rendered Markdown content.

    Converts markdown to HTML and displays it in a wx.html2.WebView,
    giving proper heading structure, lists, tables, etc. for screen
    reader navigation.

    Escape or the Close button dismisses the dialog.
    """

    def __init__(self, parent, title, markdown_content):
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self._create_ui(markdown_content)
        self.SetSize(750, 550)
        self.CenterOnScreen()

    def _create_ui(self, markdown_content):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Convert markdown to HTML, then sanitize to prevent XSS.
        # Documents are user-editable and transmitted over the network;
        # python-markdown passes raw HTML through by default.
        html_body = markdown.markdown(
            markdown_content,
            extensions=_MD_EXTENSIONS,
        )
        html_body = nh3.clean(
            html_body,
            tags=_ALLOWED_TAGS,
            attributes=_ALLOWED_ATTRIBUTES,
            url_schemes=_ALLOWED_URL_SCHEMES,
            link_rel="noopener noreferrer",
        )

        # Build full HTML page with system colours
        bg = _sys_color_hex(wx.SYS_COLOUR_WINDOW)
        fg = _sys_color_hex(wx.SYS_COLOUR_WINDOWTEXT)
        border = _sys_color_hex(wx.SYS_COLOUR_GRAYTEXT)
        link = _sys_color_hex(wx.SYS_COLOUR_HOTLIGHT)

        # Derive subtle tones from the background
        bg_c = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        fg_c = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)

        # Code background: slightly shift towards foreground
        code_r = bg_c.Red() + (fg_c.Red() - bg_c.Red()) // 10
        code_g = bg_c.Green() + (fg_c.Green() - bg_c.Green()) // 10
        code_b = bg_c.Blue() + (fg_c.Blue() - bg_c.Blue()) // 10
        code_bg = f"#{code_r:02x}{code_g:02x}{code_b:02x}"

        # Table header background: slightly more shift
        th_r = bg_c.Red() + (fg_c.Red() - bg_c.Red()) // 7
        th_g = bg_c.Green() + (fg_c.Green() - bg_c.Green()) // 7
        th_b = bg_c.Blue() + (fg_c.Blue() - bg_c.Blue()) // 7
        th_bg = f"#{th_r:02x}{th_g:02x}{th_b:02x}"

        full_html = _HTML_TEMPLATE.format(
            content=html_body,
            bg=bg,
            fg=fg,
            border=border,
            link=link,
            code_bg=code_bg,
            th_bg=th_bg,
        )

        # WebView for rendered content
        self.web_view = wx.html2.WebView.New(panel)
        self.web_view.SetPage(full_html, "")
        sizer.Add(self.web_view, 1, wx.EXPAND | wx.ALL, 5)

        # Close button
        close_btn = wx.Button(panel, wx.ID_CLOSE, "&Close")
        sizer.Add(close_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(sizer)

        # Bindings
        close_btn.Bind(wx.EVT_BUTTON, self._on_close)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        # Focus the WebView once content is loaded for screen reader access
        self.web_view.Bind(
            wx.html2.EVT_WEBVIEW_LOADED,
            self._on_webview_loaded,
        )

        # Escape key accelerator
        accel = wx.AcceleratorTable(
            [wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CLOSE)]
        )
        self.SetAcceleratorTable(accel)

    def _on_webview_loaded(self, event):
        """Set focus to the web view body once content is loaded."""
        self.web_view.SetFocus()
        # Help screen readers pick up the content
        self.web_view.RunScript("document.body.focus();")

    def _on_close(self, event):
        """Close the dialog."""
        self.EndModal(wx.ID_CLOSE)
