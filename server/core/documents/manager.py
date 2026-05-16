"""Document manager for loading, editing, and versioning server documents.

Supports a shared/independent directory split for pull-only sync infrastructure:
- ``shared/`` contains canonical documents tracked in the git repository.
- ``independent/`` contains server-specific documents (gitignored).

Three contribution modes (configured via ``config.toml``):
- **manual**: changes stay uncommitted; admin exports a ZIP.
- **auto_commit** (default): server auto-commits after each save.
- **auto_pr**: auto-commit + admin can create a PR via ``gh`` CLI.
"""

import hashlib
import json
import logging
import re
import shutil
import subprocess
import time
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path

LOG = logging.getLogger("playpalace.documents")

_MAX_HISTORY_PER_LOCALE = 5

SCOPE_SHARED = "shared"
SCOPE_INDEPENDENT = "independent"

MODE_MANUAL = "manual"
MODE_AUTO_COMMIT = "auto_commit"
MODE_AUTO_PR = "auto_pr"


class DocumentManager:
    """Manages document metadata, content, edit locks, and version history.

    Documents live in a directory tree split into ``shared/`` (git-tracked)
    and ``independent/`` (server-local) subdirectories.  Each subfolder is a
    document containing locale-specific ``.md`` files and a ``_metadata.json``.

    The ``contribution_mode`` controls how edits to shared documents are
    tracked and exported.  See module docstring for the three modes.
    """

    def __init__(self, documents_dir: Path, contribution_mode: str = MODE_AUTO_COMMIT):
        self._dir = documents_dir
        self._shared_dir = documents_dir / "shared"
        self._independent_dir = documents_dir / "independent"
        self._attribution_path = documents_dir / "_attribution.json"
        self.contribution_mode = contribution_mode
        self._categories: dict = {}  # slug -> {sort, name: {locale: str}}
        self._documents: dict = {}  # folder_name -> document metadata dict
        self._scopes: dict = {}  # folder_name -> SCOPE_SHARED | SCOPE_INDEPENDENT
        self._edit_locks: dict = {}  # (folder_name, locale) -> {user, timestamp}

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self) -> int:
        """Load document metadata from disk.

        Performs migration from the legacy flat layout if needed, then
        loads documents from both ``shared/`` and ``independent/``.

        Returns the number of documents loaded.
        """
        self._dir.mkdir(parents=True, exist_ok=True)
        self._shared_dir.mkdir(exist_ok=True)
        self._independent_dir.mkdir(exist_ok=True)

        # Migrate legacy flat layout into shared/
        self._migrate_legacy_layout()

        # Load or create root metadata
        root_meta_path = self._dir / "_metadata.json"
        if root_meta_path.exists():
            with open(root_meta_path, "r", encoding="utf-8") as f:
                root_meta = json.load(f)
            self._categories = root_meta.get("categories", {})
        else:
            self._categories = {}
            self._save_root_metadata()

        # Scan both directories
        self._documents.clear()
        self._scopes.clear()
        self._load_scope_dir(self._shared_dir, SCOPE_SHARED)
        self._load_scope_dir(self._independent_dir, SCOPE_INDEPENDENT)

        return len(self._documents)

    def _migrate_legacy_layout(self) -> None:
        """Move document folders from the legacy flat layout into shared/.

        The legacy layout stored documents directly in the documents root
        directory.  This migration moves them into the ``shared/``
        subdirectory.  The root ``_metadata.json`` is left in place.
        """
        for entry in sorted(self._dir.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith("_"):
                continue
            if entry.name in ("shared", "independent"):
                continue
            # This is a legacy document folder — move it to shared/
            dest = self._shared_dir / entry.name
            if not dest.exists():
                shutil.move(str(entry), str(dest))
                LOG.info("Migrated document '%s' to shared/", entry.name)
            else:
                LOG.warning(
                    "Skipping migration of '%s': already exists in shared/",
                    entry.name,
                )

    def _load_scope_dir(self, scope_dir: Path, scope: str) -> None:
        """Load documents from a single scope directory."""
        if not scope_dir.exists():
            return
        for entry in sorted(scope_dir.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith("_"):
                continue

            doc_meta_path = entry / "_metadata.json"
            self._scopes[entry.name] = scope
            if doc_meta_path.exists():
                with open(doc_meta_path, "r", encoding="utf-8") as f:
                    self._documents[entry.name] = json.load(f)
            else:
                # Auto-generate metadata for existing document folders
                self._documents[entry.name] = self._generate_default_metadata(entry)
                self._save_document_metadata(entry.name)

    def _generate_default_metadata(self, folder: Path) -> dict:
        """Generate default metadata for a document folder without one."""
        now = datetime.now(timezone.utc).isoformat()
        title = folder.name.replace("_", " ").title()

        # Detect existing locale files
        locales = {}
        locale_codes = []
        for md_file in sorted(folder.glob("*.md")):
            locale_code = md_file.stem
            locale_codes.append(locale_code)
            locales[locale_code] = {
                "created": now,
                "modified_contents": now,
                "public": True,
            }

        # Ensure at least an 'en' entry
        if not locales:
            locale_codes.append("en")
            locales["en"] = {
                "created": now,
                "modified_contents": now,
                "public": True,
            }

        titles = {code: title for code in locale_codes}

        return {
            "categories": [],
            "source_locale": "en",
            "titles": titles,
            "locales": locales,
        }

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_categories(self, locale: str) -> list[dict]:
        """Return categories sorted by sort order with display names.

        Each entry has keys ``slug`` and ``name``.
        """
        result = []
        for slug, info in self._categories.items():
            names = info.get("name", {})
            display = names.get(locale) or names.get("en") or slug
            result.append({"slug": slug, "name": display})
        result.sort(key=lambda c: c["name"].lower())
        return result

    def get_category_document_counts(
        self,
        *,
        include_private: bool = True,
        allowed_private_locales: set[str] | None = None,
    ) -> dict[str | None, int]:
        """Return document counts per category in a single pass.

        Keys are category slugs, plus ``None`` for all documents and
        ``""`` for uncategorized.
        """
        counts: dict[str | None, int] = {None: 0, "": 0}
        for meta in self._documents.values():
            visible_locales = self._get_visible_locale_codes(
                meta,
                include_private=include_private,
                allowed_private_locales=allowed_private_locales,
            )
            if not visible_locales:
                continue

            counts[None] += 1
            cats = meta.get("categories", [])
            if not cats:
                counts[""] += 1
            for slug in cats:
                counts[slug] = counts.get(slug, 0) + 1
        return counts

    @staticmethod
    def _get_visible_locale_codes(
        meta: dict,
        *,
        include_private: bool,
        allowed_private_locales: set[str] | None = None,
    ) -> list[str]:
        """Return locale codes visible to the current caller."""
        locales = meta.get("locales", {})
        if include_private:
            return list(locales.keys())

        allowed_private_locales = allowed_private_locales or set()
        return [
            locale_code
            for locale_code, locale_meta in locales.items()
            if locale_meta.get("public", False) or locale_code in allowed_private_locales
        ]

    @staticmethod
    def _select_display_title_locale(
        visible_locales: list[str],
        preferred_locale: str,
        source_locale: str,
    ) -> str | None:
        """Pick the best locale to display from the visible locales."""
        if preferred_locale in visible_locales:
            return preferred_locale
        if source_locale in visible_locales:
            return source_locale
        if "en" in visible_locales:
            return "en"
        if visible_locales:
            return sorted(visible_locales)[0]
        return None

    @staticmethod
    def _select_visible_title(
        titles: dict[str, str],
        visible_locales: list[str],
        preferred_locale: str,
        source_locale: str,
        folder_name: str,
    ) -> str:
        """Pick the best available title without using hidden locales."""
        ordered_locales: list[str] = []
        for locale_code in [
            preferred_locale,
            source_locale,
            "en",
            *sorted(visible_locales),
        ]:
            if locale_code in visible_locales and locale_code not in ordered_locales:
                ordered_locales.append(locale_code)

        for locale_code in ordered_locales:
            title = titles.get(locale_code)
            if title:
                return title
        return folder_name

    def get_documents_in_category(
        self,
        category_slug: str | None,
        locale: str,
        *,
        include_private: bool = True,
        allowed_private_locales: set[str] | None = None,
    ) -> list[dict]:
        """Return documents in a category.

        Args:
            category_slug: Category slug to filter by.  ``None`` returns all
                documents, ``""`` returns uncategorized documents.
            locale: Locale for display title resolution.
            include_private: When ``True``, include private locales.
            allowed_private_locales: Private locales still visible when
                ``include_private`` is ``False``.

        Returns a list of dicts with ``folder_name`` and ``title``.
        """
        results = []
        for folder_name, meta in self._documents.items():
            cats = meta.get("categories", [])
            if category_slug is None:
                pass  # include all
            elif category_slug == "":
                if cats:
                    continue
            else:
                if category_slug not in cats:
                    continue

            visible_locales = self._get_visible_locale_codes(
                meta,
                include_private=include_private,
                allowed_private_locales=allowed_private_locales,
            )
            if not visible_locales:
                continue

            titles = meta.get("titles", {})
            source = meta.get("source_locale", "en")
            title_locale = self._select_display_title_locale(visible_locales, locale, source)
            title = self._select_visible_title(
                titles,
                visible_locales,
                title_locale or locale,
                source,
                folder_name,
            )

            # Include sort-relevant timestamps from a visible locale.
            timestamp_locale = source if source in visible_locales else title_locale
            loc_info = meta.get("locales", {}).get(timestamp_locale or "", {})
            results.append(
                {
                    "folder_name": folder_name,
                    "title": title,
                    "created": loc_info.get("created", ""),
                    "modified": loc_info.get("modified_contents", ""),
                }
            )

        sort_method = self.get_category_sort(category_slug) if category_slug else "alphabetical"
        if sort_method == "date_created":
            results.sort(key=lambda d: d["created"], reverse=True)
        elif sort_method == "date_modified":
            results.sort(key=lambda d: d["modified"], reverse=True)
        else:
            results.sort(key=lambda d: d["title"].lower())
        return results

    def get_document_metadata(self, folder_name: str) -> dict | None:
        """Return the full metadata dict for a document, or None."""
        return self._documents.get(folder_name)

    def get_document_locale_count(self, folder_name: str) -> int:
        """Return the number of locales for a document."""
        meta = self._documents.get(folder_name)
        if meta is None:
            return 0
        return len(meta.get("locales", {}))

    def get_document_scope(self, folder_name: str) -> str | None:
        """Return the scope of a document (shared or independent), or None."""
        return self._scopes.get(folder_name)

    def get_document_content(self, folder_name: str, locale: str) -> str | None:
        """Read a document's ``.md`` file for the given locale."""
        if folder_name not in self._documents:
            return None
        meta = self._documents[folder_name]
        visible_locales = self._get_visible_locale_codes(meta, include_private=True)
        if locale not in visible_locales:
            return None
        doc_dir = self._document_dir(folder_name)
        if doc_dir is None:
            return None
        md_path = doc_dir / f"{locale}.md"
        if not md_path.exists():
            return None
        return md_path.read_text(encoding="utf-8")

    def get_document_content_for_access(
        self,
        folder_name: str,
        locale: str,
        *,
        include_private: bool = True,
        allowed_private_locales: set[str] | None = None,
    ) -> str | None:
        """Read document content only if the locale is visible to the caller."""
        meta = self._documents.get(folder_name)
        if meta is None:
            return None
        visible_locales = self._get_visible_locale_codes(
            meta,
            include_private=include_private,
            allowed_private_locales=allowed_private_locales,
        )
        if locale not in visible_locales:
            return None
        return self.get_document_content(folder_name, locale)

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------

    def save_document_content(
        self,
        folder_name: str,
        locale: str,
        content: str,
        editor_username: str,
    ) -> bool:
        """Write document content, back up the previous version, and release lock.

        For shared documents, the change is also recorded in the pending
        changeset so it can be exported and submitted upstream.

        Returns ``True`` on success, ``False`` if the document doesn't exist.
        """
        if folder_name not in self._documents:
            return False

        doc_dir = self._document_dir(folder_name)
        if doc_dir is None:
            return False

        md_path = doc_dir / f"{locale}.md"

        # Back up existing version before overwriting
        if md_path.exists():
            self._backup_version(folder_name, locale)

        md_path.write_text(content, encoding="utf-8")

        # Update metadata timestamp
        meta = self._documents[folder_name]
        locales = meta.setdefault("locales", {})
        now = datetime.now(timezone.utc).isoformat()
        if locale in locales:
            locales[locale]["modified_contents"] = now
        else:
            locales[locale] = {
                "created": now,
                "modified_contents": now,
                "public": True,
            }
        self._save_document_metadata(folder_name)

        # Release edit lock
        self.release_edit_lock(folder_name, locale, editor_username)
        return True

    def create_document(
        self,
        folder_name: str,
        categories: list[str],
        locale: str,
        title: str,
        content: str,
        scope: str = SCOPE_INDEPENDENT,
    ) -> bool:
        """Create a new document folder with initial content.

        Args:
            folder_name: The slug/folder name for the document.
            categories: List of category slugs.
            locale: The initial locale code.
            title: The display title for the initial locale.
            content: The markdown content for the initial locale.
            scope: Either ``SCOPE_SHARED`` or ``SCOPE_INDEPENDENT``.

        Returns ``False`` if a document with that folder name already exists.
        """
        if folder_name in self._documents:
            return False

        scope_dir = self._shared_dir if scope == SCOPE_SHARED else self._independent_dir
        doc_dir = scope_dir / folder_name
        doc_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc).isoformat()
        meta = {
            "categories": categories,
            "source_locale": locale,
            "titles": {locale: title},
            "locales": {
                locale: {
                    "created": now,
                    "modified_contents": now,
                    "public": True,
                }
            },
        }
        self._documents[folder_name] = meta
        self._scopes[folder_name] = scope
        self._save_document_metadata(folder_name)

        md_path = doc_dir / f"{locale}.md"
        md_path.write_text(content, encoding="utf-8")

        return True

    def set_document_title(self, folder_name: str, locale: str, title: str) -> bool:
        """Update the title for a locale in document metadata.

        Titles are stored separately from locale entries, so setting a title
        for a locale that has no translation yet does not create a locale entry.

        Returns ``True`` on success, ``False`` if the document is not found.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        titles = meta.setdefault("titles", {})
        titles[locale] = title
        self._save_document_metadata(folder_name)
        return True

    def set_document_visibility(self, folder_name: str, locale: str, public: bool) -> bool:
        """Update the public flag for a locale in document metadata.

        Returns ``True`` on success, ``False`` if document or locale not found.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        locales = meta.get("locales", {})
        if locale not in locales:
            return False
        locales[locale]["public"] = public
        self._save_document_metadata(folder_name)
        return True

    def set_document_categories(self, folder_name: str, categories: list[str]) -> bool:
        """Replace the category list for a document.

        Returns ``True`` on success, ``False`` if document not found.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        meta["categories"] = categories
        self._save_document_metadata(folder_name)
        return True

    def add_document_translation(
        self, folder_name: str, locale: str, title: str, content: str
    ) -> bool:
        """Create a new locale entry (private by default) and write the .md file.

        Returns ``False`` if the document doesn't exist or the locale already exists.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        locales = meta.setdefault("locales", {})
        if locale in locales:
            return False
        doc_dir = self._document_dir(folder_name)
        if doc_dir is None:
            return False
        now = datetime.now(timezone.utc).isoformat()
        locales[locale] = {
            "created": now,
            "modified_contents": now,
            "public": False,
        }
        titles = meta.setdefault("titles", {})
        titles[locale] = title
        md_path = doc_dir / f"{locale}.md"
        md_path.write_text(content, encoding="utf-8")
        self._save_document_metadata(folder_name)

        return True

    def remove_document_translation(
        self,
        folder_name: str,
        locale: str,
        *,
        remove_title: bool = True,
    ) -> bool:
        """Delete a locale entry, its .md file, and history backups.

        When *remove_title* is ``False`` the title for the locale is kept
        in metadata so it can be reused if the translation is re-added later.

        Returns ``False`` if the locale is the source locale or doesn't exist.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        if meta.get("source_locale") == locale:
            return False
        locales = meta.get("locales", {})
        if locale not in locales:
            return False
        doc_dir = self._document_dir(folder_name)
        if doc_dir is None:
            return False
        del locales[locale]
        if remove_title:
            meta.get("titles", {}).pop(locale, None)
        md_path = doc_dir / f"{locale}.md"
        if md_path.exists():
            md_path.unlink()
        # Remove history backups for this locale
        history_dir = doc_dir / "_history"
        if history_dir.exists():
            for backup in history_dir.glob(f"{locale}_*.md"):
                backup.unlink()
        self._save_document_metadata(folder_name)
        # Fail-safe: clean up orphaned locks.
        self._edit_locks.pop((folder_name, locale), None)
        return True

    def delete_document(self, folder_name: str) -> bool:
        """Remove a document folder from disk and from memory.

        Returns ``False`` if the document doesn't exist.
        """
        if folder_name not in self._documents:
            return False
        doc_dir = self._document_dir(folder_name)
        if doc_dir is not None and doc_dir.exists():
            shutil.rmtree(doc_dir)
        del self._documents[folder_name]
        del self._scopes[folder_name]
        # Fail-safe: clean up orphaned locks.
        stale = [key for key in self._edit_locks if key[0] == folder_name]
        for key in stale:
            del self._edit_locks[key]
        return True

    def create_category(self, slug: str, name: str, locale: str) -> bool:
        """Create a new category.

        Returns ``False`` if the slug already exists.
        """
        if slug in self._categories:
            return False
        self._categories[slug] = {
            "sort": "alphabetical",
            "name": {locale: name},
        }
        self._save_root_metadata()
        return True

    def delete_category(self, slug: str) -> bool:
        """Delete a category and remove it from all documents.

        Returns ``False`` if the category doesn't exist.
        """
        if slug not in self._categories:
            return False
        del self._categories[slug]
        self._save_root_metadata()
        # Remove from all documents that reference this category.
        for folder_name, meta in self._documents.items():
            cats = meta.get("categories", [])
            if slug in cats:
                cats.remove(slug)
                self._save_document_metadata(folder_name)
        return True

    def rename_category(self, slug: str, name: str, locale: str) -> bool:
        """Update the display name for a category in a specific locale.

        Returns ``False`` if the category doesn't exist.
        """
        cat = self._categories.get(slug)
        if cat is None:
            return False
        cat.setdefault("name", {})[locale] = name
        self._save_root_metadata()
        return True

    def set_category_sort(self, slug: str, sort_method: str) -> bool:
        """Update the sort method for a category.

        Returns ``False`` if the category doesn't exist.
        """
        cat = self._categories.get(slug)
        if cat is None:
            return False
        cat["sort"] = sort_method
        self._save_root_metadata()
        return True

    def get_category_sort(self, slug: str) -> str:
        """Return the sort method for a category (default ``"alphabetical"``)."""
        cat = self._categories.get(slug)
        if cat is None:
            return "alphabetical"
        return cat.get("sort", "alphabetical")

    @staticmethod
    def slugify(title: str) -> str:
        """Convert a document title to a folder-name slug.

        Lowercases, replaces whitespace/hyphens with underscores, strips
        non-ASCII and special characters, and collapses runs of underscores.
        """
        slug = unicodedata.normalize("NFKD", title)
        slug = slug.encode("ascii", "ignore").decode("ascii")
        slug = slug.lower()
        slug = re.sub(r"[\s\-]+", "_", slug)
        slug = re.sub(r"[^\w]", "", slug)
        slug = re.sub(r"_+", "_", slug)
        slug = slug.strip("_")
        return slug

    # ------------------------------------------------------------------
    # Edit locks
    # ------------------------------------------------------------------

    def acquire_edit_lock(self, folder_name: str, locale: str, username: str) -> str | None:
        """Attempt to acquire an edit lock.

        Returns ``None`` on success, or the locking username on failure.
        """
        self.cleanup_stale_locks()
        key = (folder_name, locale)
        existing = self._edit_locks.get(key)
        if existing and existing["user"] != username:
            return existing["user"]
        self._edit_locks[key] = {"user": username, "timestamp": time.time()}
        return None

    def release_edit_lock(self, folder_name: str, locale: str, username: str) -> None:
        """Release an edit lock if held by *username*."""
        key = (folder_name, locale)
        existing = self._edit_locks.get(key)
        if existing and existing["user"] == username:
            del self._edit_locks[key]

    def get_edit_lock_holder(self, folder_name: str, locale: str) -> str | None:
        """Return the username holding the lock, or ``None``."""
        self.cleanup_stale_locks()
        lock = self._edit_locks.get((folder_name, locale))
        return lock["user"] if lock else None

    def get_document_lock_holders(self, folder_name: str) -> dict[str, str]:
        """Return ``{locale: username}`` for every active lock on *folder_name*."""
        self.cleanup_stale_locks()
        return {
            locale: lock["user"]
            for (doc, locale), lock in self._edit_locks.items()
            if doc == folder_name
        }

    def cleanup_stale_locks(self, timeout_seconds: int = 1800) -> None:
        """Remove locks older than *timeout_seconds*."""
        now = time.time()
        stale = [
            key
            for key, lock in self._edit_locks.items()
            if now - lock["timestamp"] > timeout_seconds
        ]
        for key in stale:
            del self._edit_locks[key]

    # ------------------------------------------------------------------
    # Attribution log (manual mode only)
    # ------------------------------------------------------------------

    def _log_attribution(
        self,
        folder_name: str,
        locale: str,
        editor_username: str,
        change_type: str,
        message: str = "",
    ) -> None:
        """Append an entry to the attribution log.

        Only used in manual mode.  The log records which in-app user
        made each edit so the export ZIP can include proper credit.
        """
        entries = self._load_attribution_log()
        entries.append(
            {
                "folder_name": folder_name,
                "locale": locale,
                "editor": editor_username,
                "change_type": change_type,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._save_attribution_log(entries)

    def _load_attribution_log(self) -> list[dict]:
        """Load the attribution log, or return an empty list."""
        if self._attribution_path.exists():
            with open(self._attribution_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        return []

    def _save_attribution_log(self, entries: list[dict]) -> None:
        """Write the attribution log to disk."""
        with open(self._attribution_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=4, ensure_ascii=False)

    def get_attribution_log(self) -> list[dict]:
        """Return the current attribution log entries."""
        return self._load_attribution_log()

    # ------------------------------------------------------------------
    # Auto-commit (auto_commit and auto_pr modes)
    # ------------------------------------------------------------------

    def commit_changes(
        self,
        folder_name: str,
        locale: str,
        editor_username: str,
        message: str,
    ) -> tuple[bool, str]:
        """Stage and commit changes for a shared document.

        Runs ``git add`` on the document's files, then ``git commit``
        with the given message and ``--author`` set to the in-app user.

        Returns ``(success, error_message)``.
        """
        if self.contribution_mode == MODE_MANUAL:
            return False, "Auto-commit is disabled in manual mode."

        repo_root = self._find_git_root()
        if repo_root is None:
            return False, "Not inside a git repository."

        doc_dir = self._document_dir(folder_name)
        if doc_dir is None:
            return False, f"Document '{folder_name}' not found."

        # Resolve paths to stage
        try:
            rel_dir = str(doc_dir.resolve().relative_to(repo_root.resolve()))
        except ValueError:
            return False, "Document directory is outside the git repository."

        # Stage the entire document folder (catches .md + _metadata.json)
        add_result = subprocess.run(
            ["git", "add", "--", rel_dir],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if add_result.returncode != 0:
            error = add_result.stderr.strip() or "Unknown git error."
            LOG.error("git add failed: %s", error)
            return False, error

        # Build commit message
        if not message.strip():
            message = f"Update {folder_name}/{locale}"

        author = f"{editor_username} <noreply@playpalace>"

        commit_result = subprocess.run(
            [
                "git", "commit",
                "-m", message,
                "--author", author,
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if commit_result.returncode != 0:
            error = commit_result.stderr.strip() or "Unknown git error."
            # "nothing to commit" is not a real error
            if "nothing to commit" in error.lower() or "nothing to commit" in (
                commit_result.stdout or ""
            ).lower():
                return True, ""
            LOG.error("git commit failed: %s", error)
            return False, error

        return True, ""

    # ------------------------------------------------------------------
    # Change detection
    # ------------------------------------------------------------------

    def get_pending_changes(self) -> list[str]:
        """Return pending changes for shared documents.

        In manual mode, returns file paths that differ from HEAD
        (uncommitted working-tree changes).  In auto modes, returns
        commit subject lines ahead of ``origin/main``.
        """
        repo_root = self._find_git_root()
        if repo_root is None:
            return []

        if self.contribution_mode == MODE_MANUAL:
            return self._get_uncommitted_changes(repo_root)
        return self._get_commits_ahead(repo_root)

    def _get_uncommitted_changes(self, repo_root: Path) -> list[str]:
        """Return file paths with uncommitted changes under shared/."""
        try:
            rel_shared = str(
                self._shared_dir.resolve().relative_to(repo_root.resolve())
            )
        except ValueError:
            return []

        changed: list[str] = []

        # Tracked files that differ from HEAD
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD", "--", rel_shared],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                changed.extend(
                    line for line in result.stdout.strip().splitlines() if line
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

        # Untracked new files
        try:
            result = subprocess.run(
                [
                    "git", "ls-files",
                    "--others", "--exclude-standard",
                    "--", rel_shared,
                ],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    if line and line not in changed:
                        changed.append(line)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return changed

    def _get_commits_ahead(self, repo_root: Path) -> list[str]:
        """Return commit subject lines ahead of origin/main."""
        try:
            result = subprocess.run(
                [
                    "git", "log", "--oneline",
                    "origin/main..HEAD",
                ],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return [
                    line for line in result.stdout.strip().splitlines() if line
                ]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return []

    def get_pending_change_count(self) -> int:
        """Return the number of pending changes or commits ahead."""
        return len(self.get_pending_changes())

    def get_uncommitted_shared_documents(self) -> list[dict]:
        """Return shared documents with uncommitted changes and descriptions.

        Each entry is a dict with ``folder_name`` and ``change_tag`` keys.
        ``change_tag`` is one of: ``"absent"``, ``"present"``, ``"content"``,
        ``"metadata"``, or ``"content_and_metadata"``.
        """
        repo_root = self._find_git_root()
        if repo_root is None:
            return []

        try:
            rel_shared = str(
                self._shared_dir.resolve().relative_to(repo_root.resolve())
            ).replace("\\", "/")
        except ValueError:
            return []

        # Collect tracked modifications/deletions
        modified_paths: list[str] = []
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD", "--", rel_shared],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                modified_paths = [
                    l for l in result.stdout.strip().splitlines() if l
                ]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

        # Collect untracked (new) files
        untracked_paths: list[str] = []
        try:
            result = subprocess.run(
                [
                    "git", "ls-files",
                    "--others", "--exclude-standard",
                    "--", rel_shared,
                ],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                untracked_paths = [
                    l for l in result.stdout.strip().splitlines() if l
                ]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        untracked_set = {p.replace("\\", "/") for p in untracked_paths}

        # Group file paths by document folder and classify changes
        # folder -> {"content": bool, "metadata": bool, "new": bool}
        folder_info: dict[str, dict[str, bool]] = {}
        for path in modified_paths + untracked_paths:
            normalized = path.replace("\\", "/")
            if not normalized.startswith(rel_shared + "/"):
                continue
            rest = normalized[len(rel_shared) + 1:]
            parts = rest.split("/")
            if not parts:
                continue
            folder_name = parts[0]
            filename = parts[1] if len(parts) > 1 else ""

            info = folder_info.setdefault(
                folder_name, {"content": False, "metadata": False, "new": False},
            )
            if normalized in untracked_set:
                info["new"] = True
            if filename.endswith(".md"):
                info["content"] = True
            elif filename == "_metadata.json":
                info["metadata"] = True

        results: list[dict] = []
        for folder_name, info in folder_info.items():
            doc_dir = self._shared_dir / folder_name
            if not doc_dir.exists():
                tag = "absent"
            elif info["new"] and not info["content"] and not info["metadata"]:
                tag = "present"
            elif info["content"] and info["metadata"]:
                tag = "content_and_metadata"
            elif info["metadata"]:
                tag = "metadata"
            else:
                tag = "content"
            results.append({"folder_name": folder_name, "change_tag": tag})

        return results

    def discard_document_changes(self, folder_name: str) -> bool:
        """Discard uncommitted changes for a specific shared document.

        Restores the document's directory to match HEAD.
        Returns ``True`` on success.
        """
        repo_root = self._find_git_root()
        if repo_root is None:
            return False

        doc_dir = self._shared_dir / folder_name
        if not doc_dir.exists():
            # Document was deleted locally — restore from HEAD
            pass

        try:
            rel_path = str(
                doc_dir.resolve().relative_to(repo_root.resolve())
            )
        except ValueError:
            return False

        result = subprocess.run(
            ["git", "checkout", "HEAD", "--", rel_path],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            LOG.error("Failed to discard changes for %s: %s",
                      folder_name, result.stderr.strip())
            return False
        return True

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_pending_changes(self, output_path: Path) -> int:
        """Package uncommitted shared document changes into a ZIP.

        Only used in manual mode.  The ZIP mirrors the ``shared/``
        directory structure with only the changed files, plus an
        ``attribution.json`` built from the attribution log.

        Returns the number of files included, or 0 if nothing changed.
        """
        changed_paths = self._get_uncommitted_changes(
            self._find_git_root() or Path()
        )
        if not changed_paths:
            return 0

        repo_root = self._find_git_root()
        if repo_root is None:
            return 0

        output_path.parent.mkdir(parents=True, exist_ok=True)
        included = 0

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel_path in changed_paths:
                abs_path = repo_root / rel_path
                if abs_path.exists() and abs_path.is_file():
                    try:
                        archive_path = str(
                            abs_path.resolve().relative_to(
                                self._dir.resolve()
                            )
                        )
                    except ValueError:
                        archive_path = rel_path
                    zf.write(abs_path, archive_path)
                    included += 1

            attribution = self._load_attribution_log()
            zf.writestr(
                "attribution.json",
                json.dumps(
                    {"changes": attribution},
                    indent=4,
                    ensure_ascii=False,
                ),
            )

        if included == 0:
            output_path.unlink(missing_ok=True)

        return included

    def create_pull_request(self) -> tuple[bool, str]:
        """Create a pull request from local commits via ``gh`` CLI.

        Only used in auto_pr mode.  Creates a branch from the current
        commits ahead of ``origin/main``, pushes it, and opens a PR.

        Returns ``(success, pr_url_or_error)``.
        """
        repo_root = self._find_git_root()
        if repo_root is None:
            return False, "Not inside a git repository."

        commits = self._get_commits_ahead(repo_root)
        if not commits:
            return False, "No commits to include in a pull request."

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        branch = f"documents/{timestamp}"

        try:
            # Create and switch to the new branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return False, result.stderr.strip() or "Failed to create branch."

            # Push the branch
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                # Return to main before reporting error
                subprocess.run(
                    ["git", "checkout", "main"],
                    cwd=str(repo_root),
                    capture_output=True,
                    timeout=10,
                )
                return False, result.stderr.strip() or "Failed to push branch."

            # Create the PR via gh CLI
            title = f"Document updates ({len(commits)} commits)"
            body = "Automated document contribution from PlayPalace server.\n\n"
            body += "## Commits\n"
            for line in commits:
                body += f"- {line}\n"

            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", title,
                    "--body", body,
                    "--base", "main",
                ],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Return to main regardless of PR result
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=str(repo_root),
                capture_output=True,
                timeout=10,
            )

            if result.returncode != 0:
                error = result.stderr.strip() or "Failed to create pull request."
                return False, error

            pr_url = result.stdout.strip()
            return True, pr_url

        except FileNotFoundError:
            return False, "Git or gh CLI is not installed or not in PATH."
        except subprocess.TimeoutExpired:
            return False, "Operation timed out."

    def clear_pending_changes(self) -> None:
        """Clear the attribution log (manual mode only).

        In auto modes this is a no-op since git log is the record.
        """
        if self.contribution_mode == MODE_MANUAL and self._attribution_path.exists():
            self._attribution_path.unlink()

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    def sync_shared_documents(self) -> tuple[bool, str]:
        """Sync shared documents from the remote repository.

        In auto modes, uses ``git pull --rebase`` to preserve local
        commits on top of upstream changes.  In manual mode, fetches
        and checks out ``origin/main`` (overwriting local edits).

        Returns a ``(success, message)`` tuple.
        """
        repo_root = self._find_git_root()
        if repo_root is None:
            return False, "Not inside a git repository."

        try:
            if self.contribution_mode != MODE_MANUAL:
                # Auto modes: rebase local commits on top of upstream.
                # --autostash lets git atomically stash/restore any dirty
                # working-tree state so the rebase can proceed even when
                # unrelated files in the repo have uncommitted changes.
                result = subprocess.run(
                    ["git", "pull", "--rebase", "--autostash", "origin", "main"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode != 0:
                    error = result.stderr.strip() or "Unknown git error."
                    LOG.error("Document sync pull failed: %s", error)
                    return False, f"Sync failed: {error}"
            else:
                # Manual mode: overwrite local shared/ with upstream
                rel_path = self._shared_dir.resolve().relative_to(
                    repo_root.resolve()
                )
                fetch = subprocess.run(
                    ["git", "fetch", "origin"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if fetch.returncode != 0:
                    error = fetch.stderr.strip() or "Unknown git error."
                    LOG.error("Document sync fetch failed: %s", error)
                    return False, f"Fetch failed: {error}"

                checkout = subprocess.run(
                    ["git", "checkout", "origin/main", "--", str(rel_path)],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if checkout.returncode != 0:
                    error = checkout.stderr.strip() or "Unknown git error."
                    LOG.error("Document sync checkout failed: %s", error)
                    return False, f"Sync failed: {error}"

            # Reload documents from disk after sync
            old_count = len(self._documents)
            self.load()
            new_count = len(self._documents)
            msg = f"Synced shared documents. {new_count} documents loaded."
            if new_count != old_count:
                msg += f" (was {old_count})"
            LOG.info(msg)
            return True, msg

        except FileNotFoundError:
            return False, "Git is not installed or not in PATH."
        except subprocess.TimeoutExpired:
            return False, "Sync timed out."

    def _find_git_root(self) -> Path | None:
        """Find the git repository root, or None if not in a repo."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(self._dir),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None

    # ------------------------------------------------------------------
    # Promotion (independent -> shared)
    # ------------------------------------------------------------------

    def promote_to_shared(self, folder_name: str) -> bool:
        """Move a document from independent to shared scope.

        Returns ``False`` if the document doesn't exist or is already shared.
        """
        if folder_name not in self._documents:
            return False
        if self._scopes.get(folder_name) != SCOPE_INDEPENDENT:
            return False

        src = self._independent_dir / folder_name
        dest = self._shared_dir / folder_name
        if dest.exists():
            LOG.warning(
                "Cannot promote '%s': already exists in shared/",
                folder_name,
            )
            return False

        shutil.move(str(src), str(dest))
        self._scopes[folder_name] = SCOPE_SHARED
        LOG.info("Promoted document '%s' to shared.", folder_name)
        return True

    # ------------------------------------------------------------------
    # Based-on tracking (mixed scopes)
    # ------------------------------------------------------------------

    @staticmethod
    def content_hash(content: str) -> str:
        """Compute a SHA-256 hash of document content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def set_based_on(
        self,
        folder_name: str,
        shared_slug: str,
        locale: str,
    ) -> bool:
        """Set the ``based_on`` field for an independent document.

        Records which shared document and content hash this independent
        document was derived from, so the system can detect when the
        upstream version changes.

        Returns ``False`` if the document or shared source doesn't exist,
        or the document is not independent.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return False
        if self._scopes.get(folder_name) != SCOPE_INDEPENDENT:
            return False
        # Get the shared document's content hash
        shared_content = self.get_document_content(shared_slug, locale)
        if shared_content is None:
            return False
        meta["based_on"] = {
            "slug": shared_slug,
            "locale": locale,
            "content_hash": self.content_hash(shared_content),
        }
        self._save_document_metadata(folder_name)
        return True

    def check_based_on_stale(self, folder_name: str) -> bool | None:
        """Check if an independent document's upstream source has changed.

        Returns ``True`` if the shared source content has changed since
        the ``based_on`` hash was recorded, ``False`` if unchanged,
        or ``None`` if the document has no ``based_on`` field or the
        shared source no longer exists.
        """
        meta = self._documents.get(folder_name)
        if meta is None:
            return None
        based_on = meta.get("based_on")
        if based_on is None:
            return None
        shared_slug = based_on.get("slug")
        locale = based_on.get("locale", "en")
        stored_hash = based_on.get("content_hash")
        if not shared_slug or not stored_hash:
            return None
        shared_content = self.get_document_content(shared_slug, locale)
        if shared_content is None:
            return None
        current_hash = self.content_hash(shared_content)
        return current_hash != stored_hash

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _document_dir(self, folder_name: str) -> Path | None:
        """Return the directory path for a document based on its scope."""
        scope = self._scopes.get(folder_name)
        if scope == SCOPE_SHARED:
            return self._shared_dir / folder_name
        elif scope == SCOPE_INDEPENDENT:
            return self._independent_dir / folder_name
        return None

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _save_root_metadata(self) -> None:
        """Write categories to the root ``_metadata.json``."""
        path = self._dir / "_metadata.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"categories": self._categories}, f, indent=4, ensure_ascii=False)

    def _save_document_metadata(self, folder_name: str) -> None:
        """Write a document's ``_metadata.json``."""
        meta = self._documents.get(folder_name)
        if meta is None:
            return
        doc_dir = self._document_dir(folder_name)
        if doc_dir is None:
            return
        path = doc_dir / "_metadata.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)

    def _backup_version(self, folder_name: str, locale: str) -> None:
        """Copy the current ``.md`` to ``_history/`` and enforce version cap."""
        doc_dir = self._document_dir(folder_name)
        if doc_dir is None:
            return
        md_path = doc_dir / f"{locale}.md"
        if not md_path.exists():
            return

        history_dir = doc_dir / "_history"
        history_dir.mkdir(exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_name = f"{locale}_{timestamp}.md"
        shutil.copy2(md_path, history_dir / backup_name)

        # Enforce per-locale cap
        backups = sorted(
            history_dir.glob(f"{locale}_*.md"),
            key=lambda p: p.name,
        )
        while len(backups) > _MAX_HISTORY_PER_LOCALE:
            oldest = backups.pop(0)
            oldest.unlink()
