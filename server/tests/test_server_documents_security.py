"""Security tests for document and transcriber authorization."""

from types import SimpleNamespace

import pytest

from server.core.documents.manager import DocumentManager
from server.core.server import Server
from server.core.users.base import MenuItem, TrustLevel
from server.core.users.network_user import NetworkUser


class DummyConnection:
    def __init__(self):
        self.sent = []

    async def send(self, payload):
        self.sent.append(payload)


class DummyClient:
    def __init__(self, username: str):
        self.username = username


def make_user(name: str, *, trust: TrustLevel = TrustLevel.USER, locale: str = "en") -> NetworkUser:
    user = NetworkUser(name, locale, DummyConnection(), approved=True)
    user.set_trust_level(trust)
    user.set_approved(True)
    return user


@pytest.fixture
def documents_dir(tmp_path):
    docs = tmp_path / "documents"
    docs.mkdir()
    return docs


@pytest.fixture
def server(tmp_path, documents_dir):
    srv = Server(
        db_path=str(tmp_path / "security.db"),
        locales_dir="locales",
        config_path=tmp_path / "missing.toml",
    )
    srv._documents = DocumentManager(documents_dir)
    srv._documents.load()
    return srv


def last_spoken(user: NetworkUser) -> str:
    for message in reversed(user.get_queued_messages()):
        if message["type"] == "speak":
            return message["text"]
    return ""


def assert_permission_denied(user: NetworkUser) -> None:
    message = last_spoken(user).lower()
    assert "assigned languages" in message or "permission" in message


def write_document(documents_dir, folder_name: str, metadata: str, files: dict[str, str]) -> None:
    doc_dir = documents_dir / "shared" / folder_name
    doc_dir.mkdir(parents=True, exist_ok=True)
    for locale_code, content in files.items():
        (doc_dir / f"{locale_code}.md").write_text(content, encoding="utf-8")
    (doc_dir / "_metadata.json").write_text(metadata, encoding="utf-8")


@pytest.mark.asyncio
async def test_non_admin_cannot_open_new_document_flow(server):
    user = make_user("player")
    server._db = SimpleNamespace(get_transcriber_languages=lambda username: [])

    await server._handle_documents_menu_selection(user, "new_document", {})

    assert server._user_states[user.username]["menu"] == "documents_menu"
    assert_permission_denied(user)


@pytest.mark.asyncio
async def test_non_admin_cannot_open_delete_document_confirm(server, documents_dir):
    user = make_user("player")
    write_document(
        documents_dir,
        "private_doc",
        (
            '{"categories": [], "source_locale": "en", "titles": {"en": "Private Doc"}, '
            '"locales": {"en": {"created": "2026-01-01T00:00:00Z", '
            '"modified_contents": "2026-01-01T00:00:00Z", "public": true}}}'
        ),
        {"en": "hello"},
    )
    server._documents.load()
    server._db = SimpleNamespace(get_transcriber_languages=lambda username: [])

    await server._handle_document_settings_selection(
        user,
        "delete_document",
        {"folder_name": "private_doc", "category_slug": None},
    )

    assert server._user_states[user.username]["menu"] == "document_actions_menu"
    assert_permission_denied(user)


@pytest.mark.asyncio
async def test_non_admin_cannot_add_transcriber_user(server):
    user = make_user("player")
    server._db = SimpleNamespace(
        get_transcriber_languages=lambda username: [],
        get_category_document_counts=lambda: {},
    )

    await server._handle_transcribers_by_user_selection(user, "add_user", {})

    assert server._user_states[user.username]["menu"] == "documents_menu"
    assert_permission_denied(user)


@pytest.mark.asyncio
async def test_handle_menu_rejects_selection_not_present_in_current_menu(server, monkeypatch):
    user = make_user("player")
    user.show_menu("main_menu", [MenuItem(text="Options", id="options")])
    server._users = {user.username: user}
    server._user_states[user.username] = {"menu": "main_menu"}
    server._tables = SimpleNamespace(find_user_table=lambda username: None)

    called = False

    async def fake_dispatch(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(server, "_dispatch_menu_selection", fake_dispatch)

    await server._handle_menu(DummyClient(user.username), {"selection_id": "forged"})

    assert called is False


@pytest.mark.asyncio
async def test_handle_menu_allows_selection_present_in_current_menu(server, monkeypatch):
    user = make_user("player")
    user.show_menu("main_menu", [MenuItem(text="Options", id="options")])
    server._users = {user.username: user}
    server._user_states[user.username] = {"menu": "main_menu"}
    server._tables = SimpleNamespace(find_user_table=lambda username: None)

    seen = {}

    async def fake_dispatch(dispatch_user, selection_id, state, current_menu):
        seen["username"] = dispatch_user.username
        seen["selection_id"] = selection_id
        seen["current_menu"] = current_menu

    monkeypatch.setattr(server, "_dispatch_menu_selection", fake_dispatch)

    await server._handle_menu(DummyClient(user.username), {"selection_id": "options"})

    assert seen == {
        "username": user.username,
        "selection_id": "options",
        "current_menu": "main_menu",
    }


def test_admin_can_change_titles_without_transcriber_assignments(server, documents_dir):
    admin = make_user("admin", trust=TrustLevel.ADMIN)
    write_document(
        documents_dir,
        "title_doc",
        (
            '{"categories": [], "source_locale": "en", "titles": {"en": "Title Doc"}, '
            '"locales": {"en": {"created": "2026-01-01T00:00:00Z", '
            '"modified_contents": "2026-01-01T00:00:00Z", "public": true}}}'
        ),
        {"en": "hello"},
    )
    server._documents.load()
    server._db = SimpleNamespace(get_transcriber_languages=lambda username: [])

    server._show_document_title_languages(admin, "title_doc", {"category_slug": None})

    assert server._user_states[admin.username]["menu"] == "document_title_lang_menu"
    items = admin._current_menus["document_title_lang_menu"]["items"]
    assert any(item["id"] == "lang_en" for item in items if isinstance(item, dict))


def test_admin_can_add_translation_without_transcriber_assignments(server, documents_dir):
    admin = make_user("admin", trust=TrustLevel.ADMIN)
    write_document(
        documents_dir,
        "translation_doc",
        (
            '{"categories": [], "source_locale": "en", "titles": {"en": "Translation Doc"}, '
            '"locales": {"en": {"created": "2026-01-01T00:00:00Z", '
            '"modified_contents": "2026-01-01T00:00:00Z", "public": true}}}'
        ),
        {"en": "hello"},
    )
    server._documents.load()
    server._db = SimpleNamespace(get_transcriber_languages=lambda username: [])

    server._show_add_translation_languages(admin, "translation_doc", {"category_slug": None})

    assert server._user_states[admin.username]["menu"] == "add_translation_lang_menu"
    items = admin._current_menus["add_translation_lang_menu"]["items"]
    assert any(item["id"] == "lang_fr" for item in items if isinstance(item, dict))


def test_admin_can_open_delete_confirm_without_transcriber_assignments(server, documents_dir):
    admin = make_user("admin", trust=TrustLevel.ADMIN)
    write_document(
        documents_dir,
        "delete_doc",
        (
            '{"categories": [], "source_locale": "en", "titles": {"en": "Delete Doc"}, '
            '"locales": {"en": {"created": "2026-01-01T00:00:00Z", '
            '"modified_contents": "2026-01-01T00:00:00Z", "public": true}}}'
        ),
        {"en": "hello"},
    )
    server._documents.load()
    server._db = SimpleNamespace(get_transcriber_languages=lambda username: [])

    server._show_delete_document_confirm(admin, "delete_doc", {"category_slug": None})

    assert server._user_states[admin.username]["menu"] == "delete_document_confirm"


def test_document_view_uses_visible_title_for_fallback_locale(server, documents_dir):
    user = make_user("reader", locale="en")
    write_document(
        documents_dir,
        "visible_doc",
        (
            '{"categories": [], "source_locale": "fr", '
            '"titles": {"en": "Private English", "fr": "Public French"}, '
            '"locales": {'
            '"en": {"created": "2026-01-01T00:00:00Z", "modified_contents": "2026-01-01T00:00:00Z", "public": false}, '
            '"fr": {"created": "2026-01-01T00:00:00Z", "modified_contents": "2026-01-01T00:00:00Z", "public": true}'
            '}}'
        ),
        {"en": "secret", "fr": "bonjour"},
    )
    server._documents.load()
    server._db = SimpleNamespace(get_transcriber_languages=lambda username: [])

    server._show_document_view(user, "visible_doc", {"category_slug": None})

    packet = user.get_queued_messages()[-1]
    assert packet["type"] == "request_input"
    assert packet["prompt"] == "Public French"
    assert packet["default_value"] == "bonjour"


def test_document_view_does_not_fallback_to_private_english_title(server, documents_dir):
    user = make_user("reader", locale="fr")
    write_document(
        documents_dir,
        "title_safe_doc",
        (
            '{"categories": [], "source_locale": "fr", '
            '"titles": {"en": "Private English"}, '
            '"locales": {'
            '"en": {"created": "2026-01-01T00:00:00Z", "modified_contents": "2026-01-01T00:00:00Z", "public": false}, '
            '"fr": {"created": "2026-01-01T00:00:00Z", "modified_contents": "2026-01-01T00:00:00Z", "public": true}'
            '}}'
        ),
        {"fr": "bonjour"},
    )
    server._documents.load()
    server._db = SimpleNamespace(get_transcriber_languages=lambda username: [])

    server._show_document_view(user, "title_safe_doc", {"category_slug": None})

    packet = user.get_queued_messages()[-1]
    assert packet["type"] == "request_input"
    assert packet["prompt"] == "title_safe_doc"
    assert packet["default_value"] == "bonjour"


def test_document_view_skips_missing_visible_fallback_files(server, documents_dir):
    user = make_user("reader", locale="en")
    write_document(
        documents_dir,
        "fallback_doc",
        (
            '{"categories": [], "source_locale": "fr", '
            '"titles": {"en": "Missing English", "fr": "French Title", "de": "German Title"}, '
            '"locales": {'
            '"en": {"created": "2026-01-01T00:00:00Z", "modified_contents": "2026-01-01T00:00:00Z", "public": true}, '
            '"fr": {"created": "2026-01-01T00:00:00Z", "modified_contents": "2026-01-01T00:00:00Z", "public": true}, '
            '"de": {"created": "2026-01-01T00:00:00Z", "modified_contents": "2026-01-01T00:00:00Z", "public": true}'
            '}}'
        ),
        {"fr": "bonjour", "de": "guten tag"},
    )
    server._documents.load()
    server._db = SimpleNamespace(get_transcriber_languages=lambda username: [])

    server._show_document_view(user, "fallback_doc", {"category_slug": None})

    packet = user.get_queued_messages()[-1]
    assert packet["type"] == "request_input"
    assert packet["prompt"] == "French Title"
    assert packet["default_value"] == "bonjour"


def test_documents_menu_counts_hide_fully_private_documents(server, documents_dir):
    user = make_user("reader", locale="en")
    write_document(
        documents_dir,
        "hidden_doc",
        (
            '{"categories": ["rules"], "source_locale": "en", '
            '"titles": {"en": "Hidden Doc"}, '
            '"locales": {"en": {"created": "2026-01-01T00:00:00Z", '
            '"modified_contents": "2026-01-01T00:00:00Z", "public": false}}}'
        ),
        {"en": "secret"},
    )
    (documents_dir / "_metadata.json").write_text(
        '{"categories": {"rules": {"sort": "alphabetical", "name": {"en": "Rules"}}}}',
        encoding="utf-8",
    )
    server._documents.load()
    server._db = SimpleNamespace(get_transcriber_languages=lambda username: [])

    server._show_documents_menu(user)

    items = server._users.get(user.username, user)._current_menus["documents_menu"]["items"]
    assert any(item["id"] == "all" and item["text"] == "All documents (0)" for item in items)
    assert not any(item["id"] == "cat_rules" for item in items)
