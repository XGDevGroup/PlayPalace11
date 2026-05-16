import pytest


@pytest.fixture(scope="session")
def wx_app():
    """Ensure a wx App exists for dialog tests."""
    try:
        import wx
    except ModuleNotFoundError:
        pytest.skip("wxPython is not installed")

    if not wx.App.IsDisplayAvailable():
        pytest.skip("GUI display is not available for wx dialogs")
    app = wx.App(False)
    yield app
    app.Destroy()
