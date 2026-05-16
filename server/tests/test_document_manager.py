"""Tests for the DocumentManager class."""

from __future__ import annotations

import json
import subprocess
import time
import zipfile

import pytest

from server.core.documents.manager import (
    DocumentManager,
    MODE_AUTO_COMMIT,
    MODE_AUTO_PR,
    MODE_MANUAL,
    SCOPE_INDEPENDENT,
    SCOPE_SHARED,
)


@pytest.fixture
def docs_dir(tmp_path):
    """Return a clean temporary documents directory."""
    d = tmp_path / "documents"
    d.mkdir()
    return d


@pytest.fixture
def manager(docs_dir):
    return DocumentManager(docs_dir)


@pytest.fixture
def manual_manager(docs_dir):
    return DocumentManager(docs_dir, contribution_mode=MODE_MANUAL)


# ------------------------------------------------------------------
# Helper to create documents in shared/ or independent/
# ------------------------------------------------------------------


def _create_doc_on_disk(
    docs_dir,
    folder_name,
    content="Hello",
    locale="en",
    scope="shared",
    categories=None,
    meta_override=None,
):
    """Create a document directly on disk in the given scope directory."""
    scope_dir = docs_dir / scope
    scope_dir.mkdir(exist_ok=True)
    doc_dir = scope_dir / folder_name
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / f"{locale}.md").write_text(content, encoding="utf-8")

    if meta_override:
        meta = meta_override
    else:
        meta = {
            "categories": categories or [],
            "source_locale": locale,
            "titles": {locale: folder_name.replace("_", " ").title()},
            "locales": {
                locale: {
                    "created": "2026-01-01T00:00:00Z",
                    "modified_contents": "2026-01-01T00:00:00Z",
                    "public": True,
                }
            },
        }
    with open(doc_dir / "_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f)
    return doc_dir


# ------------------------------------------------------------------
# load()
# ------------------------------------------------------------------


class TestLoad:
    def test_load_empty_directory(self, manager, docs_dir):
        count = manager.load()
        assert count == 0
        # Root _metadata.json should be created
        assert (docs_dir / "_metadata.json").exists()
        # Subdirectories should be created
        assert (docs_dir / "shared").is_dir()
        assert (docs_dir / "independent").is_dir()

    def test_load_creates_root_metadata_if_missing(self, manager, docs_dir):
        assert not (docs_dir / "_metadata.json").exists()
        manager.load()
        with open(docs_dir / "_metadata.json", encoding="utf-8") as f:
            data = json.load(f)
        assert data == {"categories": {}}

    def test_load_with_existing_root_metadata(self, manager, docs_dir):
        root_meta = {
            "categories": {"rules": {"sort": "alphabetical", "name": {"en": "Game Rules"}}}
        }
        with open(docs_dir / "_metadata.json", "w", encoding="utf-8") as f:
            json.dump(root_meta, f)

        manager.load()
        cats = manager.get_categories("en")
        assert len(cats) == 1
        assert cats[0]["slug"] == "rules"
        assert cats[0]["name"] == "Game Rules"

    def test_load_shared_documents(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "my_doc", scope="shared")
        count = manager.load()
        assert count == 1
        assert manager.get_document_scope("my_doc") == SCOPE_SHARED

    def test_load_independent_documents(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "local_doc", scope="independent")
        count = manager.load()
        assert count == 1
        assert manager.get_document_scope("local_doc") == SCOPE_INDEPENDENT

    def test_load_both_scopes(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "shared_doc", scope="shared")
        _create_doc_on_disk(docs_dir, "local_doc", scope="independent")
        count = manager.load()
        assert count == 2
        assert manager.get_document_scope("shared_doc") == SCOPE_SHARED
        assert manager.get_document_scope("local_doc") == SCOPE_INDEPENDENT

    def test_load_existing_documents_auto_generates_metadata(self, manager, docs_dir):
        shared_dir = docs_dir / "shared"
        shared_dir.mkdir(exist_ok=True)
        doc_dir = shared_dir / "my_doc"
        doc_dir.mkdir()
        (doc_dir / "en.md").write_text("Hello", encoding="utf-8")

        count = manager.load()
        assert count == 1
        assert (doc_dir / "_metadata.json").exists()
        with open(doc_dir / "_metadata.json", encoding="utf-8") as f:
            meta = json.load(f)
        assert "en" in meta["locales"]
        assert meta["titles"]["en"] == "My Doc"
        assert meta["source_locale"] == "en"

    def test_load_skips_underscore_dirs(self, manager, docs_dir):
        shared_dir = docs_dir / "shared"
        shared_dir.mkdir(exist_ok=True)
        hidden = shared_dir / "_internal"
        hidden.mkdir()
        (hidden / "en.md").write_text("hidden", encoding="utf-8")

        count = manager.load()
        assert count == 0

    def test_load_multiple_locales_detected(self, manager, docs_dir):
        shared_dir = docs_dir / "shared"
        shared_dir.mkdir(exist_ok=True)
        doc_dir = shared_dir / "multi_lang"
        doc_dir.mkdir()
        (doc_dir / "en.md").write_text("English", encoding="utf-8")
        (doc_dir / "es.md").write_text("Spanish", encoding="utf-8")

        manager.load()
        meta_path = doc_dir / "_metadata.json"
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        assert "en" in meta["locales"]
        assert "es" in meta["locales"]


# ------------------------------------------------------------------
# Legacy migration
# ------------------------------------------------------------------


class TestLegacyMigration:
    def test_migrates_flat_documents_to_shared(self, manager, docs_dir):
        """Documents in the root should be moved to shared/."""
        doc_dir = docs_dir / "old_doc"
        doc_dir.mkdir()
        (doc_dir / "en.md").write_text("legacy content", encoding="utf-8")
        meta = {
            "categories": [],
            "source_locale": "en",
            "titles": {"en": "Old Doc"},
            "locales": {
                "en": {
                    "created": "2026-01-01T00:00:00Z",
                    "modified_contents": "2026-01-01T00:00:00Z",
                    "public": True,
                }
            },
        }
        with open(doc_dir / "_metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta, f)

        count = manager.load()
        assert count == 1
        # Should now be in shared/
        assert not (docs_dir / "old_doc").exists()
        assert (docs_dir / "shared" / "old_doc" / "en.md").exists()
        assert manager.get_document_scope("old_doc") == SCOPE_SHARED

    def test_migration_skips_existing_in_shared(self, manager, docs_dir):
        """If a doc already exists in shared/, don't overwrite it."""
        # Create in root (legacy)
        doc_dir = docs_dir / "conflict_doc"
        doc_dir.mkdir()
        (doc_dir / "en.md").write_text("legacy", encoding="utf-8")

        # Also in shared/
        shared_dir = docs_dir / "shared"
        shared_dir.mkdir(exist_ok=True)
        shared_doc = shared_dir / "conflict_doc"
        shared_doc.mkdir()
        (shared_doc / "en.md").write_text("canonical", encoding="utf-8")

        manager.load()
        # shared/ version should be untouched
        assert (shared_doc / "en.md").read_text(encoding="utf-8") == "canonical"


# ------------------------------------------------------------------
# get_categories
# ------------------------------------------------------------------


class TestGetCategories:
    def test_locale_fallback_to_english(self, manager, docs_dir):
        root_meta = {
            "categories": {
                "news": {
                    "sort": "alphabetical",
                    "name": {"en": "News", "es": "Noticias"},
                }
            }
        }
        with open(docs_dir / "_metadata.json", "w", encoding="utf-8") as f:
            json.dump(root_meta, f)
        manager.load()

        cats_fr = manager.get_categories("fr")
        assert cats_fr[0]["name"] == "News"  # falls back to en

        cats_es = manager.get_categories("es")
        assert cats_es[0]["name"] == "Noticias"

    def test_fallback_to_slug(self, manager, docs_dir):
        root_meta = {"categories": {"misc": {"sort": "alphabetical", "name": {}}}}
        with open(docs_dir / "_metadata.json", "w", encoding="utf-8") as f:
            json.dump(root_meta, f)
        manager.load()

        cats = manager.get_categories("en")
        assert cats[0]["name"] == "misc"


# ------------------------------------------------------------------
# get_documents_in_category
# ------------------------------------------------------------------


class TestGetDocumentsInCategory:
    def _setup_docs(self, docs_dir):
        """Create two docs, one categorized and one not."""
        root_meta = {"categories": {"rules": {"sort": "alphabetical", "name": {"en": "Rules"}}}}
        with open(docs_dir / "_metadata.json", "w", encoding="utf-8") as f:
            json.dump(root_meta, f)

        _create_doc_on_disk(docs_dir, "doc_a", categories=["rules"])
        _create_doc_on_disk(docs_dir, "doc_b", categories=[])

    def test_filter_by_category(self, manager, docs_dir):
        self._setup_docs(docs_dir)
        manager.load()
        docs = manager.get_documents_in_category("rules", "en")
        assert len(docs) == 1
        assert docs[0]["folder_name"] == "doc_a"

    def test_uncategorized(self, manager, docs_dir):
        self._setup_docs(docs_dir)
        manager.load()
        docs = manager.get_documents_in_category("", "en")
        assert len(docs) == 1
        assert docs[0]["folder_name"] == "doc_b"

    def test_all_documents(self, manager, docs_dir):
        self._setup_docs(docs_dir)
        manager.load()
        docs = manager.get_documents_in_category(None, "en")
        assert len(docs) == 2

    def test_mixed_scopes_all_visible(self, manager, docs_dir):
        """Both shared and independent docs should appear in listings."""
        _create_doc_on_disk(docs_dir, "shared_doc", scope="shared")
        _create_doc_on_disk(docs_dir, "indie_doc", scope="independent")
        manager.load()
        docs = manager.get_documents_in_category(None, "en")
        names = {d["folder_name"] for d in docs}
        assert names == {"shared_doc", "indie_doc"}

    def test_private_documents_are_hidden_without_access(self, manager, docs_dir):
        _create_doc_on_disk(
            docs_dir,
            "private_doc",
            meta_override={
                "categories": [],
                "source_locale": "fr",
                "titles": {"fr": "Document prive"},
                "locales": {
                    "fr": {
                        "created": "2026-01-01T00:00:00Z",
                        "modified_contents": "2026-01-01T00:00:00Z",
                        "public": False,
                    }
                },
            },
        )
        manager.load()

        docs = manager.get_documents_in_category(None, "fr", include_private=False)

        assert docs == []

    def test_assigned_private_locale_remains_visible_in_listings(self, manager, docs_dir):
        _create_doc_on_disk(
            docs_dir,
            "translator_doc",
            locale="fr",
            meta_override={
                "categories": [],
                "source_locale": "fr",
                "titles": {"fr": "Document prive"},
                "locales": {
                    "fr": {
                        "created": "2026-01-01T00:00:00Z",
                        "modified_contents": "2026-01-01T00:00:00Z",
                        "public": False,
                    }
                },
            },
        )
        manager.load()

        docs = manager.get_documents_in_category(
            None,
            "fr",
            include_private=False,
            allowed_private_locales={"fr"},
        )

        assert [doc["folder_name"] for doc in docs] == ["translator_doc"]

    def test_listing_falls_back_to_other_visible_title(self, manager, docs_dir):
        _create_doc_on_disk(
            docs_dir,
            "partially_translated_doc",
            locale="fr",
            meta_override={
                "categories": [],
                "source_locale": "en",
                "titles": {"en": "English Title"},
                "locales": {
                    "en": {
                        "created": "2026-01-01T00:00:00Z",
                        "modified_contents": "2026-01-01T00:00:00Z",
                        "public": True,
                    },
                    "fr": {
                        "created": "2026-01-01T00:00:00Z",
                        "modified_contents": "2026-01-01T00:00:00Z",
                        "public": False,
                    },
                },
            },
        )
        manager.load()

        docs = manager.get_documents_in_category(
            None,
            "fr",
            include_private=False,
            allowed_private_locales={"fr"},
        )

        assert len(docs) == 1
        assert docs[0]["title"] == "English Title"


class TestGetCategoryDocumentCounts:
    def test_hidden_private_documents_are_excluded_from_counts(self, manager, docs_dir):
        _create_doc_on_disk(
            docs_dir,
            "hidden_doc",
            meta_override={
                "categories": ["rules"],
                "source_locale": "en",
                "titles": {"en": "Hidden Doc"},
                "locales": {
                    "en": {
                        "created": "2026-01-01T00:00:00Z",
                        "modified_contents": "2026-01-01T00:00:00Z",
                        "public": False,
                    }
                },
            },
        )
        manager.load()

        counts = manager.get_category_document_counts(include_private=False)

        assert counts == {None: 0, "": 0}

    def test_allowed_private_locales_still_count_documents(self, manager, docs_dir):
        _create_doc_on_disk(
            docs_dir,
            "translator_doc",
            locale="fr",
            meta_override={
                "categories": ["rules"],
                "source_locale": "fr",
                "titles": {"fr": "Translator Doc"},
                "locales": {
                    "fr": {
                        "created": "2026-01-01T00:00:00Z",
                        "modified_contents": "2026-01-01T00:00:00Z",
                        "public": False,
                    }
                },
            },
        )
        manager.load()

        counts = manager.get_category_document_counts(
            include_private=False,
            allowed_private_locales={"fr"},
        )

        assert counts[None] == 1
        assert counts["rules"] == 1


# ------------------------------------------------------------------
# get_document_content
# ------------------------------------------------------------------


class TestGetDocumentContent:
    def test_reads_md_on_demand(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "hello", content="# Hello World")
        manager.load()

        content = manager.get_document_content("hello", "en")
        assert content == "# Hello World"

    def test_returns_none_for_missing_locale(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "hello", content="hi")
        manager.load()

        assert manager.get_document_content("hello", "fr") is None

    def test_returns_none_for_missing_document(self, manager):
        manager.load()
        assert manager.get_document_content("nonexistent", "en") is None

    def test_private_locale_requires_explicit_access(self, manager, docs_dir):
        _create_doc_on_disk(
            docs_dir,
            "hello",
            locale="fr",
            content="bonjour",
            meta_override={
                "categories": [],
                "source_locale": "fr",
                "titles": {"fr": "Bonjour"},
                "locales": {
                    "fr": {
                        "created": "2026-01-01T00:00:00Z",
                        "modified_contents": "2026-01-01T00:00:00Z",
                        "public": False,
                    }
                },
            },
        )
        manager.load()

        assert manager.get_document_content_for_access(
            "hello", "fr", include_private=False
        ) is None
        assert (
            manager.get_document_content_for_access(
                "hello",
                "fr",
                include_private=False,
                allowed_private_locales={"fr"},
            )
            == "bonjour"
        )


# ------------------------------------------------------------------
# get_document_scope
# ------------------------------------------------------------------


class TestGetDocumentScope:
    def test_shared_scope(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "s_doc", scope="shared")
        manager.load()
        assert manager.get_document_scope("s_doc") == SCOPE_SHARED

    def test_independent_scope(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "i_doc", scope="independent")
        manager.load()
        assert manager.get_document_scope("i_doc") == SCOPE_INDEPENDENT

    def test_unknown_document_returns_none(self, manager):
        manager.load()
        assert manager.get_document_scope("nope") is None


# ------------------------------------------------------------------
# save_document_content
# ------------------------------------------------------------------


class TestSaveDocumentContent:
    def test_writes_file_and_updates_timestamp(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "editable", content="original")
        manager.load()

        original_ts = manager._documents["editable"]["locales"]["en"]["modified_contents"]
        result = manager.save_document_content("editable", "en", "updated", "alice")
        assert result is True
        assert (docs_dir / "shared" / "editable" / "en.md").read_text(encoding="utf-8") == "updated"
        new_ts = manager._documents["editable"]["locales"]["en"]["modified_contents"]
        assert new_ts != original_ts

    def test_creates_new_locale_entry_on_save(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "editable", content="english")
        manager.load()

        result = manager.save_document_content("editable", "fr", "français", "bob")
        assert result is True
        assert "fr" in manager._documents["editable"]["locales"]

    def test_returns_false_for_unknown_document(self, manager):
        manager.load()
        assert manager.save_document_content("nope", "en", "x", "alice") is False

    def test_save_does_not_auto_log_attribution(self, manager, docs_dir):
        """Attribution is logged by the browsing layer, not save_document_content."""
        _create_doc_on_disk(docs_dir, "shared_doc", scope="shared")
        manager.load()

        manager.save_document_content("shared_doc", "en", "updated content", "alice")
        assert manager.get_attribution_log() == []

    def test_independent_edit_does_not_log_attribution(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "indie_doc", scope="independent")
        manager.load()

        manager.save_document_content("indie_doc", "en", "updated", "bob")
        assert manager.get_attribution_log() == []


# ------------------------------------------------------------------
# Version history
# ------------------------------------------------------------------


class TestVersionHistory:
    def test_backup_created_on_save(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "versioned", content="v1")
        manager.load()

        manager.save_document_content("versioned", "en", "v2", "alice")
        history = list((docs_dir / "shared" / "versioned" / "_history").glob("en_*.md"))
        assert len(history) == 1
        assert history[0].read_text(encoding="utf-8") == "v1"

    def test_version_cap_enforced(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "capped", content="v0")
        manager.load()

        # Pre-create 6 backup files to test the cap without timestamp collisions
        history_dir = docs_dir / "shared" / "capped" / "_history"
        history_dir.mkdir()
        for i in range(6):
            (history_dir / f"en_20260101T0000{i:02d}Z.md").write_text(f"old_v{i}", encoding="utf-8")
        assert len(list(history_dir.glob("en_*.md"))) == 6

        # One more save triggers backup + prune
        manager.save_document_content("capped", "en", "v_new", "alice")

        history = list(history_dir.glob("en_*.md"))
        assert len(history) == 5  # cap


# ------------------------------------------------------------------
# Edit locks
# ------------------------------------------------------------------


class TestEditLocks:
    def test_acquire_and_release(self, manager):
        manager.load()
        result = manager.acquire_edit_lock("doc", "en", "alice")
        assert result is None  # success
        manager.release_edit_lock("doc", "en", "alice")

    def test_conflict_detection(self, manager):
        manager.load()
        manager.acquire_edit_lock("doc", "en", "alice")
        result = manager.acquire_edit_lock("doc", "en", "bob")
        assert result == "alice"

    def test_same_user_reacquires(self, manager):
        manager.load()
        manager.acquire_edit_lock("doc", "en", "alice")
        result = manager.acquire_edit_lock("doc", "en", "alice")
        assert result is None

    def test_stale_lock_cleanup(self, manager):
        manager.load()
        manager.acquire_edit_lock("doc", "en", "alice")
        # Manually age the lock
        manager._edit_locks[("doc", "en")]["timestamp"] = time.time() - 3600

        manager.cleanup_stale_locks(timeout_seconds=1800)
        # Lock should be cleaned up, so bob can acquire
        result = manager.acquire_edit_lock("doc", "en", "bob")
        assert result is None

    def test_save_releases_lock(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "locked", content="text")
        manager.load()

        manager.acquire_edit_lock("locked", "en", "alice")
        manager.save_document_content("locked", "en", "new text", "alice")
        # Lock should be released
        assert ("locked", "en") not in manager._edit_locks


# ------------------------------------------------------------------
# create_document / create_category
# ------------------------------------------------------------------


class TestCreateOperations:
    def test_create_document_defaults_to_independent(self, manager, docs_dir):
        manager.load()
        result = manager.create_document("new_doc", ["rules"], "en", "New Doc", "# New")
        assert result is True
        assert (docs_dir / "independent" / "new_doc" / "en.md").exists()
        assert (docs_dir / "independent" / "new_doc" / "_metadata.json").exists()
        assert manager.get_document_content("new_doc", "en") == "# New"
        assert manager.get_document_scope("new_doc") == SCOPE_INDEPENDENT

    def test_create_document_shared(self, manager, docs_dir):
        manager.load()
        result = manager.create_document(
            "shared_new",
            [],
            "en",
            "Shared",
            "content",
            scope=SCOPE_SHARED,
        )
        assert result is True
        assert (docs_dir / "shared" / "shared_new" / "en.md").exists()
        assert manager.get_document_scope("shared_new") == SCOPE_SHARED

    def test_create_duplicate_document_fails(self, manager, docs_dir):
        manager.load()
        manager.create_document("dup", [], "en", "Dup", "content")
        result = manager.create_document("dup", [], "en", "Dup", "content2")
        assert result is False

    def test_create_category(self, manager, docs_dir):
        manager.load()
        result = manager.create_category("faq", "FAQ", "en")
        assert result is True
        cats = manager.get_categories("en")
        assert any(c["slug"] == "faq" for c in cats)

    def test_create_duplicate_category_fails(self, manager, docs_dir):
        manager.load()
        manager.create_category("faq", "FAQ", "en")
        result = manager.create_category("faq", "FAQ 2", "en")
        assert result is False


# ------------------------------------------------------------------
# slugify
# ------------------------------------------------------------------


class TestSlugify:
    def test_basic_title(self):
        assert DocumentManager.slugify("Uno Rules") == "uno_rules"

    def test_special_characters(self):
        assert DocumentManager.slugify("FAQ & Tips!") == "faq_tips"

    def test_hyphens_become_underscores(self):
        assert DocumentManager.slugify("how-to-play") == "how_to_play"

    def test_multiple_spaces_collapse(self):
        assert DocumentManager.slugify("Game   Rules   2") == "game_rules_2"

    def test_leading_trailing_stripped(self):
        assert DocumentManager.slugify("  Hello World  ") == "hello_world"

    def test_empty_string(self):
        assert DocumentManager.slugify("") == ""

    def test_only_special_chars(self):
        assert DocumentManager.slugify("!!!") == ""

    def test_unicode_stripped(self):
        assert DocumentManager.slugify("Café Rules") == "cafe_rules"

    def test_numbers_preserved(self):
        assert DocumentManager.slugify("Chapter 3") == "chapter_3"


# ------------------------------------------------------------------
# delete_category
# ------------------------------------------------------------------


class TestDeleteCategory:
    def test_delete_existing_category(self, manager, docs_dir):
        manager.load()
        manager.create_category("news", "News", "en")
        result = manager.delete_category("news")
        assert result is True
        cats = manager.get_categories("en")
        assert not any(c["slug"] == "news" for c in cats)

    def test_delete_nonexistent_category(self, manager):
        manager.load()
        assert manager.delete_category("nope") is False

    def test_delete_category_removes_from_documents(self, manager, docs_dir):
        manager.load()
        manager.create_category("rules", "Rules", "en")
        manager.create_document("doc1", ["rules"], "en", "Doc", "content")
        manager.delete_category("rules")
        meta = manager.get_document_metadata("doc1")
        assert "rules" not in meta["categories"]

    def test_delete_category_persists(self, manager, docs_dir):
        manager.load()
        manager.create_category("temp", "Temp", "en")
        manager.delete_category("temp")
        # Reload from disk
        manager2 = DocumentManager(docs_dir)
        manager2.load()
        cats = manager2.get_categories("en")
        assert not any(c["slug"] == "temp" for c in cats)


# ------------------------------------------------------------------
# rename_category
# ------------------------------------------------------------------


class TestRenameCategory:
    def test_rename_category(self, manager, docs_dir):
        manager.load()
        manager.create_category("faq", "FAQ", "en")
        result = manager.rename_category("faq", "Frequently Asked Questions", "en")
        assert result is True
        cats = manager.get_categories("en")
        faq = next(c for c in cats if c["slug"] == "faq")
        assert faq["name"] == "Frequently Asked Questions"

    def test_rename_adds_locale(self, manager, docs_dir):
        manager.load()
        manager.create_category("news", "News", "en")
        manager.rename_category("news", "Noticias", "es")
        cats = manager.get_categories("es")
        news = next(c for c in cats if c["slug"] == "news")
        assert news["name"] == "Noticias"

    def test_rename_nonexistent(self, manager):
        manager.load()
        assert manager.rename_category("nope", "Name", "en") is False


# ------------------------------------------------------------------
# set_category_sort / get_category_sort
# ------------------------------------------------------------------


class TestCategorySort:
    def test_default_sort(self, manager, docs_dir):
        manager.load()
        manager.create_category("rules", "Rules", "en")
        assert manager.get_category_sort("rules") == "alphabetical"

    def test_set_sort_method(self, manager, docs_dir):
        manager.load()
        manager.create_category("rules", "Rules", "en")
        result = manager.set_category_sort("rules", "date_modified")
        assert result is True
        assert manager.get_category_sort("rules") == "date_modified"

    def test_set_sort_nonexistent(self, manager):
        manager.load()
        assert manager.set_category_sort("nope", "alphabetical") is False

    def test_get_sort_nonexistent_returns_default(self, manager):
        manager.load()
        assert manager.get_category_sort("nope") == "alphabetical"

    def test_sort_by_date_created(self, manager, docs_dir):
        manager.load()
        manager.create_category("rules", "Rules", "en")
        manager.set_category_sort("rules", "date_created")
        manager.create_document(
            "old_doc",
            ["rules"],
            "en",
            "Old Doc",
            "old",
        )
        # Manually set timestamps to control ordering
        meta = manager.get_document_metadata("old_doc")
        meta["locales"]["en"]["created"] = "2026-01-01T00:00:00Z"
        manager.create_document(
            "new_doc",
            ["rules"],
            "en",
            "New Doc",
            "new",
        )
        meta2 = manager.get_document_metadata("new_doc")
        meta2["locales"]["en"]["created"] = "2026-06-01T00:00:00Z"

        docs = manager.get_documents_in_category("rules", "en")
        # date_created sorts newest first
        assert docs[0]["folder_name"] == "new_doc"
        assert docs[1]["folder_name"] == "old_doc"


# ------------------------------------------------------------------
# Attribution log
# ------------------------------------------------------------------


class TestAttributionLog:
    """Attribution logging is used in manual mode only.

    Attribution is now logged explicitly by the browsing layer (after the
    commit-message editbox), so these tests call ``_log_attribution``
    directly rather than expecting it to be triggered by save methods.
    """

    def test_attribution_initially_empty(self, manual_manager):
        manual_manager.load()
        assert manual_manager.get_attribution_log() == []

    def test_log_attribution_edit(self, manual_manager, docs_dir):
        _create_doc_on_disk(docs_dir, "tracked", scope="shared")
        manual_manager.load()

        manual_manager._log_attribution("tracked", "en", "alice", "edit", "fixed typo")
        log = manual_manager.get_attribution_log()
        assert len(log) == 1
        assert log[0]["folder_name"] == "tracked"
        assert log[0]["locale"] == "en"
        assert log[0]["editor"] == "alice"
        assert log[0]["change_type"] == "edit"
        assert log[0]["message"] == "fixed typo"
        assert "timestamp" in log[0]

    def test_multiple_edits_accumulate(self, manual_manager, docs_dir):
        _create_doc_on_disk(docs_dir, "multi_edit", scope="shared")
        manual_manager.load()

        manual_manager._log_attribution("multi_edit", "en", "alice", "edit")
        manual_manager._log_attribution("multi_edit", "en", "bob", "edit")
        log = manual_manager.get_attribution_log()
        assert len(log) == 2
        assert log[0]["editor"] == "alice"
        assert log[1]["editor"] == "bob"

    def test_clear_pending_changes_clears_attribution(self, manual_manager, docs_dir):
        manual_manager.load()

        manual_manager._log_attribution("clear_test", "en", "alice", "edit")
        assert len(manual_manager.get_attribution_log()) == 1

        manual_manager.clear_pending_changes()
        assert manual_manager.get_attribution_log() == []

    def test_translation_add_attribution(self, manual_manager, docs_dir):
        manual_manager.load()

        manual_manager._log_attribution("translatable", "fr", "bob", "translation_add")
        log = manual_manager.get_attribution_log()
        assert len(log) == 1
        assert log[0]["change_type"] == "translation_add"
        assert log[0]["locale"] == "fr"

    def test_create_attribution(self, manual_manager, docs_dir):
        manual_manager.load()

        manual_manager._log_attribution("new_shared", "en", "alice", "create")
        log = manual_manager.get_attribution_log()
        assert len(log) == 1
        assert log[0]["change_type"] == "create"

    def test_auto_commit_mode_clear_is_noop(self, manager, docs_dir):
        """clear_pending_changes is a no-op in auto_commit mode."""
        manager.load()
        # Shouldn't crash or create attribution file
        manager.clear_pending_changes()
        assert manager.get_attribution_log() == []


# ------------------------------------------------------------------
# Git-based change detection
# ------------------------------------------------------------------


def _git_run(cwd, *args):
    """Run a git command in the given directory."""
    subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture
def git_docs_dir(tmp_path):
    """Create a documents directory inside an initialized git repo."""
    repo = tmp_path / "repo"
    repo.mkdir()
    docs_dir = repo / "documents"
    docs_dir.mkdir()

    _git_run(repo, "init", "-b", "main")
    _git_run(repo, "config", "user.email", "test@test.com")
    _git_run(repo, "config", "user.name", "Test")

    return docs_dir


@pytest.fixture
def git_manager(git_docs_dir):
    """Manual-mode manager in a git repo (default for existing tests)."""
    return DocumentManager(git_docs_dir, contribution_mode=MODE_MANUAL)


@pytest.fixture
def git_auto_manager(git_docs_dir):
    """Auto-commit-mode manager in a git repo."""
    return DocumentManager(git_docs_dir, contribution_mode=MODE_AUTO_COMMIT)


class TestGitChangeDetection:
    def test_no_changes_after_commit(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "committed", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        assert git_manager.get_pending_changes() == []
        assert git_manager.get_pending_change_count() == 0

    def test_modified_file_detected(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "tracked", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        # Now modify via manager
        git_manager.save_document_content("tracked", "en", "changed", "alice")
        changes = git_manager.get_pending_changes()
        assert len(changes) >= 1
        # Should include the .md file
        md_paths = [p for p in changes if p.endswith("en.md")]
        assert len(md_paths) == 1

    def test_new_untracked_file_detected(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "existing", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        # Create new document via manager
        git_manager.create_document("brand_new", [], "en", "New", "content", scope=SCOPE_SHARED)
        changes = git_manager.get_pending_changes()
        assert any("brand_new" in p for p in changes)

    def test_metadata_change_detected(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "meta_test", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        # Change title (metadata only)
        git_manager.set_document_title("meta_test", "en", "New Title")
        changes = git_manager.get_pending_changes()
        meta_paths = [p for p in changes if "_metadata.json" in p]
        assert len(meta_paths) == 1

    def test_no_git_repo_returns_empty(self, manager):
        """Non-git directory returns empty changes gracefully."""
        manager.load()
        assert manager.get_pending_changes() == []


# ------------------------------------------------------------------
# Export
# ------------------------------------------------------------------


class TestExport:
    """Export is manual-mode only."""

    def test_export_creates_zip(self, git_manager, git_docs_dir, tmp_path):
        _create_doc_on_disk(git_docs_dir, "exportable", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_manager.save_document_content("exportable", "en", "exported text", "alice")
        # Simulate browsing layer logging attribution (manual mode)
        git_manager._log_attribution("exportable", "en", "alice", "edit", "test edit")

        output = tmp_path / "export.zip"
        count = git_manager.export_pending_changes(output)
        assert count >= 1
        assert output.exists()

        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            md_entries = [n for n in names if n.endswith("en.md")]
            assert len(md_entries) >= 1
            assert "attribution.json" in names

            attr = json.loads(zf.read("attribution.json"))
            assert len(attr["changes"]) == 1
            assert attr["changes"][0]["editor"] == "alice"

    def test_export_empty_returns_zero(self, git_manager, git_docs_dir, tmp_path):
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        output = tmp_path / "empty.zip"
        count = git_manager.export_pending_changes(output)
        assert count == 0
        assert not output.exists()

    def test_export_multiple_changes(self, git_manager, git_docs_dir, tmp_path):
        _create_doc_on_disk(git_docs_dir, "doc_a", scope="shared")
        _create_doc_on_disk(git_docs_dir, "doc_b", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_manager.save_document_content("doc_a", "en", "a content", "alice")
        git_manager.save_document_content("doc_b", "en", "b content", "bob")

        output = tmp_path / "multi.zip"
        count = git_manager.export_pending_changes(output)
        assert count >= 2

        with zipfile.ZipFile(output, "r") as zf:
            names = zf.namelist()
            assert any("doc_a" in n for n in names)
            assert any("doc_b" in n for n in names)


# ------------------------------------------------------------------
# Promote (independent -> shared)
# ------------------------------------------------------------------


class TestPromote:
    def test_promote_independent_to_shared(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "promotable", scope="independent")
        manager.load()
        assert manager.get_document_scope("promotable") == SCOPE_INDEPENDENT

        result = manager.promote_to_shared("promotable")
        assert result is True
        assert manager.get_document_scope("promotable") == SCOPE_SHARED
        assert (docs_dir / "shared" / "promotable" / "en.md").exists()
        assert not (docs_dir / "independent" / "promotable").exists()

    def test_promote_already_shared_fails(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "shared_doc", scope="shared")
        manager.load()
        assert manager.promote_to_shared("shared_doc") is False

    def test_promote_nonexistent_fails(self, manager):
        manager.load()
        assert manager.promote_to_shared("nope") is False

    def test_promote_conflict_fails(self, manager, docs_dir):
        """Cannot promote if a doc with the same name exists in shared."""
        _create_doc_on_disk(docs_dir, "conflict", scope="independent", content="indie")
        _create_doc_on_disk(docs_dir, "conflict", scope="shared", content="shared")
        manager.load()
        # The independent version won't load because shared has the same name,
        # but test the safety check in promote_to_shared directly
        # (Only the first one loaded wins in the dict, but let's test the method)
        # Force both scopes to test the safeguard
        manager._scopes["conflict"] = SCOPE_INDEPENDENT
        result = manager.promote_to_shared("conflict")
        assert result is False  # dest already exists


# ------------------------------------------------------------------
# Based-on tracking
# ------------------------------------------------------------------


class TestBasedOn:
    def test_set_based_on(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "source_doc", scope="shared", content="original")
        _create_doc_on_disk(docs_dir, "derived_doc", scope="independent", content="my version")
        manager.load()

        result = manager.set_based_on("derived_doc", "source_doc", "en")
        assert result is True

        meta = manager.get_document_metadata("derived_doc")
        assert "based_on" in meta
        assert meta["based_on"]["slug"] == "source_doc"
        assert meta["based_on"]["content_hash"] == DocumentManager.content_hash("original")

    def test_based_on_not_stale(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "source", scope="shared", content="original")
        _create_doc_on_disk(docs_dir, "derived", scope="independent")
        manager.load()

        manager.set_based_on("derived", "source", "en")
        assert manager.check_based_on_stale("derived") is False

    def test_based_on_stale_after_source_edit(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "source", scope="shared", content="original")
        _create_doc_on_disk(docs_dir, "derived", scope="independent")
        manager.load()

        manager.set_based_on("derived", "source", "en")
        # Edit the source
        manager.save_document_content("source", "en", "updated content", "admin")
        assert manager.check_based_on_stale("derived") is True

    def test_based_on_no_field_returns_none(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "standalone", scope="independent")
        manager.load()
        assert manager.check_based_on_stale("standalone") is None

    def test_set_based_on_shared_doc_fails(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "source", scope="shared")
        _create_doc_on_disk(docs_dir, "also_shared", scope="shared")
        manager.load()
        # Can only set based_on for independent docs
        # Force scope for testing
        result = manager.set_based_on("also_shared", "source", "en")
        assert result is False

    def test_set_based_on_missing_source_fails(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "derived", scope="independent")
        manager.load()
        result = manager.set_based_on("derived", "nonexistent", "en")
        assert result is False


# ------------------------------------------------------------------
# Delete document
# ------------------------------------------------------------------


class TestDeleteDocument:
    def test_delete_shared_document(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "del_doc", scope="shared")
        manager.load()
        result = manager.delete_document("del_doc")
        assert result is True
        assert not (docs_dir / "shared" / "del_doc").exists()
        assert manager.get_document_metadata("del_doc") is None
        assert manager.get_document_scope("del_doc") is None

    def test_delete_independent_document(self, manager, docs_dir):
        _create_doc_on_disk(docs_dir, "indie_del", scope="independent")
        manager.load()
        result = manager.delete_document("indie_del")
        assert result is True
        assert not (docs_dir / "independent" / "indie_del").exists()

    def test_delete_nonexistent_fails(self, manager):
        manager.load()
        assert manager.delete_document("nope") is False


# ------------------------------------------------------------------
# Auto-commit mode
# ------------------------------------------------------------------


class TestAutoCommit:
    """Tests for commit_changes() in auto_commit mode."""

    def test_commit_creates_git_commit(self, git_auto_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "autotest", scope="shared")
        git_auto_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_auto_manager.save_document_content("autotest", "en", "updated", "alice")

        success, error = git_auto_manager.commit_changes(
            "autotest", "en", "alice", "Fixed typo in autotest"
        )
        assert success is True
        assert error == ""

        # Verify the git log has our commit
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=str(repo),
            capture_output=True,
            text=True,
        )
        assert "Fixed typo in autotest" in result.stdout

    def test_commit_uses_default_message_when_empty(self, git_auto_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "defmsg", scope="shared")
        git_auto_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_auto_manager.save_document_content("defmsg", "en", "changed", "bob")

        success, _ = git_auto_manager.commit_changes("defmsg", "en", "bob", "")
        assert success is True

        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=str(repo),
            capture_output=True,
            text=True,
        )
        assert "Update defmsg/en" in result.stdout

    def test_commit_sets_author(self, git_auto_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "authored", scope="shared")
        git_auto_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_auto_manager.save_document_content("authored", "en", "new text", "charlie")
        git_auto_manager.commit_changes("authored", "en", "charlie", "test")

        result = subprocess.run(
            ["git", "log", "-1", "--format=%an <%ae>"],
            cwd=str(repo),
            capture_output=True,
            text=True,
        )
        assert "charlie" in result.stdout
        assert "noreply@playpalace" in result.stdout

    def test_commit_nothing_to_commit_is_ok(self, git_auto_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "nochange", scope="shared")
        git_auto_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        # Don't modify anything — commit should succeed (nothing to commit)
        success, _ = git_auto_manager.commit_changes("nochange", "en", "alice", "noop")
        assert success is True

    def test_commit_rejected_in_manual_mode(self, git_manager, git_docs_dir):
        git_manager.load()
        success, error = git_manager.commit_changes("any", "en", "alice", "msg")
        assert success is False
        assert "manual mode" in error.lower()

    def test_commit_nonexistent_document(self, git_auto_manager, git_docs_dir):
        git_auto_manager.load()
        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        success, error = git_auto_manager.commit_changes("ghost", "en", "alice", "msg")
        assert success is False
        assert "not found" in error.lower()


# ------------------------------------------------------------------
# Pending detection in auto modes
# ------------------------------------------------------------------


class TestPendingDetectionAutoMode:
    """In auto modes, pending changes are commits ahead of origin/main."""

    def test_no_commits_ahead(self, git_auto_manager, git_docs_dir):
        """With no remote, get_commits_ahead returns empty."""
        git_auto_manager.load()
        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        # No origin remote configured, so git log origin/main..HEAD will fail
        changes = git_auto_manager.get_pending_changes()
        assert changes == []

    def test_commits_ahead_detected(self, git_auto_manager, git_docs_dir, tmp_path):
        """Commits ahead of origin/main are detected as pending."""
        repo = git_docs_dir.parent

        # Set up a bare remote so we have an origin/main
        bare = tmp_path / "bare.git"
        subprocess.run(
            ["git", "init", "--bare", str(bare)],
            capture_output=True,
            check=True,
        )
        _git_run(repo, "remote", "add", "origin", str(bare))

        _create_doc_on_disk(git_docs_dir, "remote_test", scope="shared")
        git_auto_manager.load()
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")
        _git_run(repo, "push", "-u", "origin", "main")

        # Now make a local commit
        git_auto_manager.save_document_content("remote_test", "en", "v2", "alice")
        git_auto_manager.commit_changes("remote_test", "en", "alice", "local change")

        changes = git_auto_manager.get_pending_changes()
        assert len(changes) == 1
        assert "local change" in changes[0]

    def test_manual_mode_uses_diff(self, git_manager, git_docs_dir):
        """Manual mode uses git diff, not git log."""
        _create_doc_on_disk(git_docs_dir, "manual_test", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_manager.save_document_content("manual_test", "en", "edited", "alice")
        changes = git_manager.get_pending_changes()
        # Should be file paths, not commit messages
        assert any("en.md" in c for c in changes)


# ------------------------------------------------------------------
# Uncommitted shared documents and discard
# ------------------------------------------------------------------


class TestUncommittedSharedDocuments:
    def _folder_names(self, results):
        return [r["folder_name"] for r in results]

    def _find_entry(self, results, folder_name):
        for r in results:
            if r["folder_name"] == folder_name:
                return r
        return None

    def test_no_uncommitted_changes(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "clean", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        assert git_manager.get_uncommitted_shared_documents() == []

    def test_detects_modified_content(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "edited_doc", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_manager.save_document_content("edited_doc", "en", "changed", "alice")
        results = git_manager.get_uncommitted_shared_documents()
        assert len(results) == 1
        assert results[0]["folder_name"] == "edited_doc"
        # Content change includes both .md and _metadata.json (timestamp update)
        assert results[0]["change_tag"] in ("content", "content_and_metadata")

    def test_detects_metadata_only_change(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "meta_only", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_manager.set_document_title("meta_only", "en", "New Title")
        results = git_manager.get_uncommitted_shared_documents()
        assert len(results) == 1
        assert results[0]["change_tag"] == "metadata"

    def test_detects_deleted_document(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "doomed", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        import shutil
        shutil.rmtree(git_docs_dir / "shared" / "doomed")

        results = git_manager.get_uncommitted_shared_documents()
        entry = self._find_entry(results, "doomed")
        assert entry is not None
        assert entry["change_tag"] == "absent"

    def test_deduplicates_content_and_metadata(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "multi_file", scope="shared")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_manager.save_document_content("multi_file", "en", "new", "alice")
        git_manager.set_document_title("multi_file", "en", "New Title")

        results = git_manager.get_uncommitted_shared_documents()
        assert len(results) == 1
        assert results[0]["change_tag"] == "content_and_metadata"

    def test_no_git_repo_returns_empty(self, manager):
        manager.load()
        assert manager.get_uncommitted_shared_documents() == []


class TestDiscardDocumentChanges:
    def test_discard_restores_content(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "restorable", scope="shared", content="original")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        git_manager.save_document_content("restorable", "en", "modified", "alice")
        assert git_manager.discard_document_changes("restorable") is True

        restored = (git_docs_dir / "shared" / "restorable" / "en.md").read_text(
            encoding="utf-8"
        )
        assert restored == "original"

    def test_discard_restores_deleted_document(self, git_manager, git_docs_dir):
        _create_doc_on_disk(git_docs_dir, "deleted_doc", scope="shared", content="alive")
        git_manager.load()

        repo = git_docs_dir.parent
        _git_run(repo, "add", "-A")
        _git_run(repo, "commit", "-m", "initial")

        import shutil
        shutil.rmtree(git_docs_dir / "shared" / "deleted_doc")
        assert not (git_docs_dir / "shared" / "deleted_doc").exists()

        assert git_manager.discard_document_changes("deleted_doc") is True
        assert (git_docs_dir / "shared" / "deleted_doc" / "en.md").exists()

    def test_no_git_repo_returns_false(self, manager):
        manager.load()
        assert manager.discard_document_changes("anything") is False


# ------------------------------------------------------------------
# Contribution mode property
# ------------------------------------------------------------------


class TestContributionMode:
    def test_default_mode_is_auto_commit(self, manager):
        assert manager.contribution_mode == MODE_AUTO_COMMIT

    def test_manual_mode(self, manual_manager):
        assert manual_manager.contribution_mode == MODE_MANUAL

    def test_mode_can_be_changed(self, manager):
        manager.contribution_mode = MODE_AUTO_PR
        assert manager.contribution_mode == MODE_AUTO_PR
