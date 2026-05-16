from ui.markdown_viewer_dialog import sanitize_markdown


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
