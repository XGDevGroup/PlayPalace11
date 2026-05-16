"""Document browsing menus for the PlayPalace server."""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from ..users.network_user import NetworkUser
from ..users.base import MenuItem, EscapeBehavior, TrustLevel
from ...messages.localization import Localization
from server.core.ui.common_flows import show_yes_no_menu
from .manager import (
    DocumentManager,
    SCOPE_SHARED,
    SCOPE_INDEPENDENT,
    MODE_MANUAL,
    MODE_AUTO_COMMIT,
    MODE_AUTO_PR,
)

if TYPE_CHECKING:
    from ...persistence.database import Database

_MODULE_DIR = Path(__file__).parent.parent.parent
_DOCUMENTS_DIR = _MODULE_DIR / "documents"


class DocumentBrowsingMixin:
    """Provide document browsing menus.

    Expected attributes:
        _db: Database instance.
        _documents: DocumentManager instance.
        _user_states: dict[str, dict] of user menu states.
        _show_main_menu(user): Method to show the main menu.
    """

    _db: "Database"
    _documents: DocumentManager
    _user_states: dict[str, dict]

    # ------------------------------------------------------------------
    # Dispatch helpers (called by Server)
    # ------------------------------------------------------------------

    def _get_document_menu_handlers(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> dict[str, tuple]:
        """Return menu dispatch entries for the entire documents system."""
        handlers: dict[str, tuple] = {
            "documents_menu": (self._handle_documents_menu_selection, (user, selection_id, state)),
            "documents_list_menu": (
                self._handle_documents_list_selection,
                (user, selection_id, state),
            ),
            "document_actions_menu": (
                self._handle_document_actions_selection,
                (user, selection_id, state),
            ),
            "document_settings_menu": (
                self._handle_document_settings_selection,
                (user, selection_id, state),
            ),
            "document_title_lang_menu": (
                self._handle_document_title_lang_selection,
                (user, selection_id, state),
            ),
            "document_visibility_menu": (
                self._handle_document_visibility_selection,
                (user, selection_id, state),
            ),
            "document_categories_menu": (
                self._handle_document_categories_selection,
                (user, selection_id, state),
            ),
            "remove_translation_lang_menu": (
                self._handle_remove_translation_lang_selection,
                (user, selection_id, state),
            ),
            "remove_translation_confirm": (
                self._handle_remove_translation_confirm,
                (user, selection_id, state),
            ),
            "remove_translation_title_confirm": (
                self._handle_remove_translation_title_confirm,
                (user, selection_id, state),
            ),
            "delete_document_confirm": (
                self._handle_delete_document_confirm,
                (user, selection_id, state),
            ),
            "promote_to_shared_confirm": (
                self._handle_promote_confirm,
                (user, selection_id, state),
            ),
            "document_edit_lang_menu": (
                self._handle_edit_lang_selection,
                (user, selection_id, state),
            ),
            "add_translation_lang_menu": (
                self._handle_add_translation_lang_selection,
                (user, selection_id, state),
            ),
            "new_document_scope_menu": (
                self._handle_new_document_scope_selection,
                (user, selection_id, state),
            ),
            "new_document_categories_menu": (
                self._handle_new_document_categories_selection,
                (user, selection_id, state),
            ),
            "category_settings_menu": (
                self._handle_category_settings_selection,
                (user, selection_id, state),
            ),
            "category_sort_menu": (
                self._handle_category_sort_selection,
                (user, selection_id, state),
            ),
            "delete_category_confirm": (
                self._handle_delete_category_confirm,
                (user, selection_id, state),
            ),
            "sync_discard_menu": (
                self._handle_sync_discard_selection,
                (user, selection_id, state),
            ),
        }
        # Include transcriber management handlers.
        handlers.update(self._get_transcriber_menu_handlers(user, selection_id, state))
        return handlers

    async def _handle_document_editbox(
        self, user: NetworkUser, current_menu: str | None, packet: dict, state: dict
    ) -> bool:
        """Handle document-related editbox submissions.

        Returns ``True`` if the editbox was handled, ``False`` otherwise.
        """
        if current_menu == "document_view":
            folder_name = state.get("folder_name", "")
            if self._is_transcriber(user.username) or self._is_admin(user):
                self._show_document_actions(user, folder_name, state)
            else:
                category_slug = state.get("category_slug")
                self._show_documents_list(user, category_slug)
            return True

        if current_menu == "document_title_editbox":
            text = packet.get("text", "")
            await self._handle_document_title_editbox(user, text, state)
            return True

        if current_menu == "new_document_slug_editbox":
            text = packet.get("text", "")
            self._handle_new_document_slug(user, text, state)
            return True

        if current_menu == "new_category_slug_editbox":
            text = packet.get("text", "")
            self._handle_new_category_slug(user, text, state)
            return True

        if current_menu == "new_category_name_editbox":
            text = packet.get("text", "")
            self._handle_new_category_name(user, text, state)
            return True

        if current_menu == "rename_category_editbox":
            text = packet.get("text", "")
            self._handle_rename_category(user, text, state)
            return True

        if current_menu == "commit_message_editbox":
            text = packet.get("text", "")
            self._handle_commit_message(user, text, state)
            return True

        return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_transcriber(self, username: str) -> bool:
        """Return True if the user has any transcriber language assignments."""
        return len(self._db.get_transcriber_languages(username)) > 0

    def _is_admin(self, user: NetworkUser) -> bool:
        """Return True if the user is an admin."""
        return user.trust_level.value >= TrustLevel.ADMIN.value

    def _get_user_visible_locales(self, user: NetworkUser, folder_name: str) -> list[str]:
        """Return document locales the user is allowed to read."""
        meta = self._documents.get_document_metadata(folder_name)
        if meta is None:
            return []
        if self._is_admin(user):
            return sorted(meta.get("locales", {}).keys())

        assigned = self._get_user_assigned_languages(user.username)
        return sorted(
            locale_code
            for locale_code, loc_info in meta.get("locales", {}).items()
            if loc_info.get("public", False) or locale_code in assigned
        )

    def _get_user_assigned_languages(self, username: str) -> set[str]:
        """Return the set of languages assigned to a user as a transcriber."""
        return set(self._db.get_transcriber_languages(username))

    def _get_user_accessible_locales(self, user: NetworkUser, folder_name: str) -> list[str]:
        """Return document locales the user can edit (assigned/admin only)."""
        meta = self._documents.get_document_metadata(folder_name)
        if meta is None:
            return []
        if self._is_admin(user):
            return sorted(meta.get("locales", {}).keys())
        assigned = self._get_user_assigned_languages(user.username)
        return [loc for loc in meta.get("locales", {}).keys() if loc in assigned]

    def _deny_document_permission(
        self,
        user: NetworkUser,
        *,
        folder_name: str | None = None,
        state: dict | None = None,
    ) -> None:
        """Speak a permission error and return to the safest document menu."""
        user.speak_l("documents-no-permission")
        if folder_name and state is not None:
            self._show_document_actions(user, folder_name, state)
        else:
            self._show_documents_menu(user)

    def _get_document_title(self, folder_name: str, locale: str) -> str:
        """Get display title for a document."""
        meta = self._documents.get_document_metadata(folder_name)
        if meta is None:
            return folder_name
        titles = meta.get("titles", {})
        return titles.get(locale) or titles.get("en") or folder_name

    def _get_visible_document_title(
        self,
        folder_name: str,
        preferred_locale: str,
        visible_locales: list[str],
    ) -> str:
        """Get a document title without falling back to hidden locales."""
        meta = self._documents.get_document_metadata(folder_name)
        if meta is None:
            return folder_name

        titles = meta.get("titles", {})
        source_locale = meta.get("source_locale", "en")
        ordered_locales: list[str] = []
        for locale_code in [preferred_locale, source_locale, "en", *visible_locales]:
            if locale_code in visible_locales and locale_code not in ordered_locales:
                ordered_locales.append(locale_code)

        for locale_code in ordered_locales:
            title = titles.get(locale_code)
            if title:
                return title
        return folder_name

    def _get_title_candidate_locales(self, user: NetworkUser) -> list[str]:
        """Return locales this user may target for title edits."""
        if self._is_admin(user):
            return sorted(Localization.get_available_locale_codes())

        assigned = self._get_user_assigned_languages(user.username)
        return [
            code
            for code in Localization.get_available_locale_codes()
            if code in assigned
        ]

    def _get_add_translation_locales(
        self, user: NetworkUser, folder_name: str, meta: dict | None = None
    ) -> list[str]:
        """Return locales this user may add as new translations."""
        if meta is None:
            return []
        existing_locales = set(meta.get("locales", {}).keys())
        if self._is_admin(user):
            candidates = Localization.get_available_locale_codes()
        else:
            candidates = sorted(self._get_user_assigned_languages(user.username))
        return [code for code in candidates if code not in existing_locales]

    # ------------------------------------------------------------------
    # Category / document list browsing
    # ------------------------------------------------------------------

    def _show_documents_menu(self, user: NetworkUser) -> None:
        """Show the documents category menu."""
        categories = self._documents.get_categories(user.locale)
        is_admin = self._is_admin(user)
        counts = self._documents.get_category_document_counts(
            include_private=is_admin,
            allowed_private_locales=self._get_user_assigned_languages(user.username),
        )
        show_empty = is_admin or self._is_transcriber(user.username)

        items = []

        # "All documents" first
        all_count = counts.get(None, 0)
        all_label = Localization.get(user.locale, "documents-all")
        items.append(MenuItem(text=f"{all_label} ({all_count})", id="all"))

        # Real categories
        for cat in categories:
            cat_count = counts.get(cat["slug"], 0)
            if cat_count == 0 and not show_empty:
                continue
            items.append(
                MenuItem(
                    text=f"{cat['name']} ({cat_count})",
                    id=f"cat_{cat['slug']}",
                )
            )

        # "Uncategorized" at the bottom
        uncat_count = counts.get("", 0)
        uncat_label = Localization.get(user.locale, "documents-uncategorized")
        items.append(MenuItem(text=f"{uncat_label} ({uncat_count})", id="uncategorized"))

        if is_admin:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "documents-new-document"),
                    id="new_document",
                )
            )
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "documents-new-category"),
                    id="new_category",
                )
            )
            # Sync and export/pending admin actions
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "documents-sync"),
                    id="sync_documents",
                )
            )
            pending_count = self._documents.get_pending_change_count()
            mode = self._documents.contribution_mode
            if mode == MODE_MANUAL:
                pending_label = Localization.get(
                    user.locale,
                    "documents-export-pending",
                    count=str(pending_count),
                )
                items.append(MenuItem(text=pending_label, id="export_pending"))
            elif mode == MODE_AUTO_PR:
                pending_label = Localization.get(
                    user.locale,
                    "documents-pr-button",
                    count=str(pending_count),
                )
                items.append(MenuItem(text=pending_label, id="create_pr"))
            else:
                # auto_commit — informational button
                pending_label = Localization.get(
                    user.locale,
                    "documents-pending-commits-button",
                    count=str(pending_count),
                )
                items.append(MenuItem(text=pending_label, id="pending_info"))
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "transcribers-by-language"),
                id="transcribers_by_language",
            )
        )
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "transcribers-by-user"),
                id="transcribers_by_user",
            )
        )
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "documents_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "documents_menu"}

    async def _handle_documents_menu_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle documents category menu selection."""
        if selection_id == "back":
            self._show_main_menu(user)
        elif selection_id == "all":
            self._show_documents_list(user, None)
        elif selection_id == "uncategorized":
            self._show_documents_list(user, "")
        elif selection_id == "new_document":
            if not self._is_admin(user):
                self._deny_document_permission(user)
                return
            self._show_new_document_scope(user)
        elif selection_id == "new_category":
            if not self._is_admin(user):
                self._deny_document_permission(user)
                return
            self._show_new_category_slug_editbox(user)
        elif selection_id == "sync_documents":
            if not self._is_admin(user):
                self._deny_document_permission(user)
                return
            await self._handle_sync_documents(user)
        elif selection_id == "export_pending":
            if not self._is_admin(user):
                self._deny_document_permission(user)
                return
            await self._handle_export_pending(user)
        elif selection_id == "create_pr":
            if not self._is_admin(user):
                self._deny_document_permission(user)
                return
            await self._handle_create_pr(user)
        elif selection_id == "pending_info":
            if not self._is_admin(user):
                self._deny_document_permission(user)
                return
            self._handle_pending_info(user)
        elif selection_id == "transcribers_by_language":
            self._show_transcribers_by_language(user)
        elif selection_id == "transcribers_by_user":
            self._show_transcribers_by_user(user)
        elif selection_id.startswith("cat_"):
            slug = selection_id[4:]
            self._show_documents_list(user, slug)

    # ------------------------------------------------------------------
    # Sync and export
    # ------------------------------------------------------------------

    _CHANGE_TAG_KEYS = {
        "absent": "documents-sync-tag-absent",
        "present": "documents-sync-tag-present",
        "content": "documents-sync-tag-content",
        "metadata": "documents-sync-tag-metadata",
        "content_and_metadata": "documents-sync-tag-content-and-metadata",
    }

    async def _handle_sync_documents(self, user: NetworkUser) -> None:
        """Sync shared documents from the git repository.

        If there are uncommitted local changes to shared documents, the
        admin is shown a per-document toggle list to choose which to
        discard before syncing.
        """
        changed_docs = self._documents.get_uncommitted_shared_documents()
        if changed_docs:
            self._show_sync_discard_menu(user, changed_docs)
        else:
            self._do_sync(user)

    def _show_sync_discard_menu(
        self,
        user: NetworkUser,
        changed_docs: list[dict],
        focus_id: str | None = None,
    ) -> None:
        """Show per-document discard/keep toggles before syncing."""
        state = self._user_states.get(user.username, {})
        discard_set = set(state.get("sync_discard", []))

        user.speak_l(
            "documents-sync-local-changes",
            count=str(len(changed_docs)),
        )

        items: list[MenuItem] = []
        focus_position = 1
        for entry in changed_docs:
            folder = entry["folder_name"]
            tag = entry["change_tag"]
            title = self._get_document_title(folder, user.locale)
            description = Localization.get(
                user.locale,
                self._CHANGE_TAG_KEYS.get(tag, "documents-sync-tag-content"),
            )
            if folder in discard_set:
                label = Localization.get(
                    user.locale, "documents-sync-discard-label",
                    title=title, description=description,
                )
            else:
                label = Localization.get(
                    user.locale, "documents-sync-keep-label",
                    title=title, description=description,
                )
            item_id = f"toggle_{folder}"
            items.append(MenuItem(text=label, id=item_id))
            if item_id == focus_id:
                focus_position = len(items)

        items.append(MenuItem(
            text=Localization.get(user.locale, "documents-sync-discard-all"),
            id="discard_all",
        ))
        items.append(MenuItem(
            text=Localization.get(user.locale, "documents-sync-keep-all"),
            id="keep_all",
        ))
        items.append(MenuItem(
            text=Localization.get(user.locale, "documents-sync-confirm"),
            id="sync_confirm",
        ))
        items.append(MenuItem(
            text=Localization.get(user.locale, "back"),
            id="back",
        ))
        user.show_menu(
            "sync_discard_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=focus_position,
        )
        self._user_states[user.username] = {
            "menu": "sync_discard_menu",
            "sync_changed_docs": changed_docs,
            "sync_discard": list(discard_set),
        }

    async def _handle_sync_discard_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle discard/keep toggle and sync confirmation."""
        changed_docs: list[dict] = state.get("sync_changed_docs", [])
        all_folders = [d["folder_name"] for d in changed_docs]
        discard_set = set(state.get("sync_discard", []))

        if selection_id == "back":
            self._show_documents_menu(user)
            return

        if selection_id == "discard_all":
            discard_set = set(all_folders)
            state["sync_discard"] = list(discard_set)
            self._user_states[user.username] = state
            self._show_sync_discard_menu(user, changed_docs)
            return

        if selection_id == "keep_all":
            discard_set = set()
            state["sync_discard"] = []
            self._user_states[user.username] = state
            self._show_sync_discard_menu(user, changed_docs)
            return

        if selection_id == "sync_confirm":
            # Discard selected documents, then sync
            for folder in discard_set:
                self._documents.discard_document_changes(folder)
            self._do_sync(user)
            return

        if selection_id.startswith("toggle_"):
            folder = selection_id[7:]
            if folder in discard_set:
                discard_set.remove(folder)
                user.play_sound("checkbox_list_off.wav")
            else:
                discard_set.add(folder)
                user.play_sound("checkbox_list_on.wav")
            state["sync_discard"] = list(discard_set)
            self._user_states[user.username] = state
            self._show_sync_discard_menu(
                user, changed_docs, focus_id=selection_id,
            )

    def _do_sync(self, user: NetworkUser) -> None:
        """Run the actual sync and report the result."""
        success, message = self._documents.sync_shared_documents()
        if success:
            user.speak_l("documents-sync-success")
        else:
            user.speak_l("documents-sync-failed", reason=message)
        self._show_documents_menu(user)

    async def _handle_export_pending(self, user: NetworkUser) -> None:
        """Export pending shared document changes as a ZIP file."""
        pending_count = self._documents.get_pending_change_count()
        if pending_count == 0:
            user.speak_l("documents-export-no-changes")
            self._show_documents_menu(user)
            return

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        export_dir = _DOCUMENTS_DIR / "_exports"
        export_dir.mkdir(exist_ok=True)
        output_path = export_dir / f"document_changes_{timestamp}.zip"

        count = self._documents.export_pending_changes(output_path)
        if count > 0:
            user.speak_l(
                "documents-export-success",
                count=str(count),
                path=str(output_path),
            )
            self._documents.clear_pending_changes()
        else:
            user.speak_l("documents-export-no-changes")
        self._show_documents_menu(user)

    async def _handle_create_pr(self, user: NetworkUser) -> None:
        """Create a pull request from pending commits (auto_pr mode)."""
        pending_count = self._documents.get_pending_change_count()
        if pending_count == 0:
            user.speak_l("documents-pr-no-commits")
            self._show_documents_menu(user)
            return

        success, result = self._documents.create_pull_request()
        if success:
            user.speak_l("documents-pr-success", url=result)
        else:
            user.speak_l("documents-pr-failed", reason=result)
        self._show_documents_menu(user)

    def _handle_pending_info(self, user: NetworkUser) -> None:
        """Show informational message about pending commits (auto_commit mode)."""
        pending_count = self._documents.get_pending_change_count()
        user.speak_l(
            "documents-pending-commits-info",
            count=str(pending_count),
        )
        self._show_documents_menu(user)

    def _show_documents_list(self, user: NetworkUser, category_slug: str | None) -> None:
        """Show the list of documents in a category."""
        documents = self._documents.get_documents_in_category(
            category_slug,
            user.locale,
            include_private=self._is_admin(user),
            allowed_private_locales=self._get_user_assigned_languages(user.username),
        )
        is_real_category = category_slug is not None and category_slug != ""
        is_admin = self._is_admin(user)
        is_transcriber = self._is_transcriber(user.username)

        items = []
        for doc in documents:
            items.append(MenuItem(text=doc["title"], id=f"doc_{doc['folder_name']}"))

        if not items:
            user.speak_l("documents-no-documents")

        # Category management items for real categories.
        if is_real_category and (is_transcriber or is_admin):
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "documents-rename-category"),
                    id="rename_category",
                )
            )
        if is_real_category and is_admin:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "documents-category-settings"),
                    id="category_settings",
                )
            )
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "documents-delete-category"),
                    id="delete_category",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "documents_list_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "documents_list_menu",
            "category_slug": category_slug,
        }

    async def _handle_documents_list_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle document list menu selection."""
        category_slug = state.get("category_slug")
        if selection_id == "back":
            self._show_documents_menu(user)
        elif selection_id == "rename_category":
            if not (self._is_transcriber(user.username) or self._is_admin(user)):
                self._deny_document_permission(user)
                return
            self._show_rename_category_editbox(user, category_slug)
        elif selection_id == "category_settings":
            if not self._is_admin(user):
                self._deny_document_permission(user)
                return
            self._show_category_settings(user, category_slug)
        elif selection_id == "delete_category":
            if not self._is_admin(user):
                self._deny_document_permission(user)
                return
            self._show_delete_category_confirm(user, category_slug)
        elif selection_id.startswith("doc_"):
            folder_name = selection_id[4:]
            if self._is_transcriber(user.username) or self._is_admin(user):
                self._show_document_actions(user, folder_name, state)
            else:
                self._show_document_view(user, folder_name, state)

    # ------------------------------------------------------------------
    # Document view
    # ------------------------------------------------------------------

    def _show_document_view(self, user: NetworkUser, folder_name: str, state: dict) -> None:
        """Show a document in a read-only editbox."""
        visible_locales = self._get_user_visible_locales(user, folder_name)
        allowed_private_locales = self._get_user_assigned_languages(user.username)
        meta = self._documents.get_document_metadata(folder_name) or {}
        source_locale = meta.get("source_locale", "en")
        title_locale = None
        content = None
        for locale_code in [user.locale, "en", source_locale, *visible_locales]:
            if locale_code not in visible_locales or locale_code == title_locale:
                continue
            candidate_content = self._documents.get_document_content_for_access(
                folder_name,
                locale_code,
                include_private=self._is_admin(user),
                allowed_private_locales=allowed_private_locales,
            )
            if candidate_content is None:
                continue
            content = candidate_content
            title_locale = locale_code
            break
        if content is None:
            user.speak_l("documents-no-content")
            self._show_documents_list(user, state.get("category_slug"))
            return

        title = self._get_visible_document_title(
            folder_name,
            title_locale or user.locale,
            visible_locales,
        )

        user.show_editbox(
            "document_view",
            title,
            default_value=content,
            multiline=True,
            read_only=True,
            content_format="markdown",
        )
        self._user_states[user.username] = {
            "menu": "document_view",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    # ------------------------------------------------------------------
    # Action menu (transcriber/admin)
    # ------------------------------------------------------------------

    def _show_document_actions(self, user: NetworkUser, folder_name: str, state: dict) -> None:
        """Show the action menu for a document (View, Edit, Settings, Back)."""
        items = [
            MenuItem(
                text=Localization.get(user.locale, "documents-view"),
                id="view",
            ),
            MenuItem(
                text=Localization.get(user.locale, "documents-update-contents"),
                id="edit",
            ),
            MenuItem(
                text=Localization.get(user.locale, "documents-settings"),
                id="settings",
            ),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ]
        user.show_menu(
            "document_actions_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "document_actions_menu",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_document_actions_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle document action menu selection."""
        folder_name = state.get("folder_name", "")
        if selection_id == "back":
            self._show_documents_list(user, state.get("category_slug"))
        elif selection_id == "view":
            self._show_document_view(user, folder_name, state)
        elif selection_id == "edit":
            self._show_edit_language_menu(user, folder_name, state)
        elif selection_id == "settings":
            self._show_document_settings(user, folder_name, state)

    # ------------------------------------------------------------------
    # Document settings submenu
    # ------------------------------------------------------------------

    def _show_document_settings(self, user: NetworkUser, folder_name: str, state: dict) -> None:
        """Show the document settings submenu."""
        is_admin = self._is_admin(user)
        meta = self._documents.get_document_metadata(folder_name)

        items = [
            MenuItem(
                text=Localization.get(user.locale, "documents-update-title"),
                id="change_title",
            ),
        ]

        # Visibility with count info
        if meta:
            locales = meta.get("locales", {})
            total = len(locales)
            public_count = sum(1 for loc in locales.values() if loc.get("public", False))
            vis_label = Localization.get(
                user.locale,
                "documents-visibility-count",
                public=str(public_count),
                total=str(total),
            )
        else:
            vis_label = Localization.get(user.locale, "documents-manage-visibility")
        items.append(MenuItem(text=vis_label, id="manage_visibility"))

        if is_admin:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "documents-modify-categories"),
                    id="modify_categories",
                )
            )

        items.append(
            MenuItem(
                text=Localization.get(user.locale, "documents-add-translation"),
                id="add_translation",
            )
        )

        if is_admin:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "documents-remove-translation"),
                    id="remove_translation",
                )
            )
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "documents-delete-document"),
                    id="delete_document",
                )
            )
            # Promote to shared (only for independent documents)
            scope = self._documents.get_document_scope(folder_name)
            if scope == SCOPE_INDEPENDENT:
                items.append(
                    MenuItem(
                        text=Localization.get(user.locale, "documents-promote-to-shared"),
                        id="promote_to_shared",
                    )
                )

        # Based-on staleness indicator for independent documents
        if meta:
            stale = self._documents.check_based_on_stale(folder_name)
            if stale is True:
                based_on = meta.get("based_on", {})
                source_slug = based_on.get("slug", "")
                items.insert(
                    -1,
                    MenuItem(
                        text=Localization.get(
                            user.locale,
                            "documents-based-on-stale",
                            source=source_slug,
                        ),
                        id="based_on_stale_notice",
                    ),
                )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "document_settings_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "document_settings_menu",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_document_settings_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle document settings submenu selection."""
        folder_name = state.get("folder_name", "")
        if selection_id == "back":
            self._show_document_actions(user, folder_name, state)
        elif selection_id == "change_title":
            if not (self._is_admin(user) or self._is_transcriber(user.username)):
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            self._show_document_title_languages(user, folder_name, state)
        elif selection_id == "manage_visibility":
            if not (self._is_admin(user) or self._is_transcriber(user.username)):
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            self._show_document_visibility(user, folder_name, state)
        elif selection_id == "modify_categories":
            if not self._is_admin(user):
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            self._show_document_categories(user, folder_name, state)
        elif selection_id == "add_translation":
            if not (self._is_admin(user) or self._is_transcriber(user.username)):
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            self._show_add_translation_languages(user, folder_name, state)
        elif selection_id == "remove_translation":
            if not self._is_admin(user):
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            self._show_remove_translation_languages(user, folder_name, state)
        elif selection_id == "delete_document":
            if not self._is_admin(user):
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            self._show_delete_document_confirm(user, folder_name, state)
        elif selection_id == "promote_to_shared":
            if not self._is_admin(user):
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            self._show_promote_confirm(user, folder_name, state)
        elif selection_id == "based_on_stale_notice":
            # Informational item — just refresh the settings menu
            self._show_document_settings(user, folder_name, state)

    def _show_promote_confirm(
        self, user: NetworkUser, folder_name: str, state: dict
    ) -> None:
        """Show yes/no confirmation for promoting a document to shared."""
        question = Localization.get(user.locale, "documents-promote-confirm")
        show_yes_no_menu(user, "promote_to_shared_confirm", question)
        self._user_states[user.username] = {
            "menu": "promote_to_shared_confirm",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_promote_confirm(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle promote-to-shared confirmation."""
        folder_name = state.get("folder_name", "")
        if not self._is_admin(user):
            self._deny_document_permission(user, folder_name=folder_name, state=state)
            return
        if selection_id == "yes":
            result = self._documents.promote_to_shared(folder_name)
            if result:
                user.speak_l("documents-promoted-to-shared")
                meta = self._documents.get_document_metadata(folder_name)
                locale_code = meta.get("source_locale", "en") if meta else "en"
                mode = self._documents.contribution_mode
                if mode == MODE_MANUAL:
                    self._documents._log_attribution(
                        folder_name, locale_code, user.username,
                        "promote", "",
                    )
                else:
                    self._documents.commit_changes(
                        folder_name, locale_code, user.username,
                        f"Add {folder_name} (promoted from independent)",
                    )
            else:
                user.speak_l("documents-promote-failed")
        self._show_document_settings(user, folder_name, state)

    # ------------------------------------------------------------------
    # Change title
    # ------------------------------------------------------------------

    def _show_document_title_languages(
        self, user: NetworkUser, folder_name: str, state: dict
    ) -> None:
        """Show language selection for changing a document title."""
        meta = self._documents.get_document_metadata(folder_name)
        if meta is None:
            self._show_document_settings(user, folder_name, state)
            return

        # Titles are transcribable even without an existing translation.
        title_locales = self._get_title_candidate_locales(user)

        if not title_locales:
            user.speak_l("documents-no-permission")
            self._show_document_settings(user, folder_name, state)
            return

        titles = meta.get("titles", {})
        items = []
        for locale_code in title_locales:
            lang_name = Localization.get(user.locale, f"language-{locale_code}")
            current_title = titles.get(locale_code, "")
            display = f"{lang_name}: {current_title}" if current_title else lang_name
            items.append(
                MenuItem(
                    text=display,
                    id=f"lang_{locale_code}",
                )
            )
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "document_title_lang_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "document_title_lang_menu",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_document_title_lang_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle language selection for title change."""
        folder_name = state.get("folder_name", "")
        if selection_id == "back":
            self._show_document_settings(user, folder_name, state)
        elif selection_id.startswith("lang_"):
            locale_code = selection_id[5:]
            meta = self._documents.get_document_metadata(folder_name)
            current_title = ""
            if meta:
                current_title = meta.get("titles", {}).get(locale_code, "")
            lang_name = Localization.get(user.locale, f"language-{locale_code}")
            prompt = Localization.get(
                user.locale,
                "documents-title-prompt",
                language=lang_name,
            )
            user.show_editbox(
                "document_title_editbox",
                prompt,
                default_value=current_title,
            )
            self._user_states[user.username] = {
                "menu": "document_title_editbox",
                "folder_name": folder_name,
                "locale_code": locale_code,
                "category_slug": state.get("category_slug"),
            }

    async def _handle_document_title_editbox(
        self, user: NetworkUser, value: str, state: dict
    ) -> None:
        """Handle title editbox submission.

        Supports multiple flows via ``state["flow"]``:
        - ``"change_title"`` (default): save title, return to settings.
        - ``"add_translation"``: store title, open editor for content entry.
        - ``"new_document"``: store title, open editor for content entry.
        """
        folder_name = state.get("folder_name", "")
        locale_code = state.get("locale_code", "")
        flow = state.get("flow", "change_title")

        if not value.strip():
            # Empty/cancelled — return to appropriate menu
            if flow == "new_document":
                self._show_documents_menu(user)
            else:
                self._show_document_settings(user, folder_name, state)
            return

        title = value.strip()
        if flow == "new_document":
            # Slug was already validated in the slug editbox step.
            self._open_document_editor(
                user,
                folder_name,
                locale_code,
                state,
                flow="new_document",
                pending_title=title,
            )
        elif flow == "add_translation":
            self._open_document_editor(
                user,
                folder_name,
                locale_code,
                state,
                flow="add_translation",
                pending_title=title,
            )
        else:
            self._documents.set_document_title(folder_name, locale_code, title)
            lang_name = Localization.get(user.locale, f"language-{locale_code}")
            user.speak_l("documents-title-changed", language=lang_name)
            self._show_document_settings(user, folder_name, state)

    # ------------------------------------------------------------------
    # Manage visibility
    # ------------------------------------------------------------------

    def _show_document_visibility(
        self,
        user: NetworkUser,
        folder_name: str,
        state: dict,
        focus_locale: str | None = None,
    ) -> None:
        """Show toggle list of document locales with public on/off."""
        meta = self._documents.get_document_metadata(folder_name)
        if meta is None:
            self._show_document_settings(user, folder_name, state)
            return

        doc_locales = meta.get("locales", {})

        items = []
        focus_position = 1
        for locale_code, loc_info in doc_locales.items():
            lang_name = Localization.get(user.locale, f"language-{locale_code}")
            public = loc_info.get("public", False)
            status = Localization.get(
                user.locale, "visibility-public" if public else "visibility-private"
            )
            items.append(
                MenuItem(
                    text=f"{lang_name} {status}",
                    id=f"lang_{locale_code}",
                )
            )
            if locale_code == focus_locale:
                focus_position = len(items)

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "document_visibility_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=focus_position,
        )
        self._user_states[user.username] = {
            "menu": "document_visibility_menu",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_document_visibility_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle visibility toggle selection."""
        folder_name = state.get("folder_name", "")
        if selection_id == "back":
            self._show_document_settings(user, folder_name, state)
        elif selection_id.startswith("lang_"):
            locale_code = selection_id[5:]
            # Permission check: user must have this language assigned
            assigned = self._get_user_assigned_languages(user.username)
            if not self._is_admin(user) and locale_code not in assigned:
                lang_name = Localization.get(user.locale, f"language-{locale_code}")
                user.speak_l("documents-visibility-no-permission", language=lang_name)
                self._show_document_visibility(user, folder_name, state, focus_locale=locale_code)
                return

            meta = self._documents.get_document_metadata(folder_name)
            if meta:
                current_public = meta.get("locales", {}).get(locale_code, {}).get("public", False)
                self._documents.set_document_visibility(
                    folder_name, locale_code, not current_public
                )
                lang_name = Localization.get(user.locale, f"language-{locale_code}")
                user.speak_l("documents-visibility-changed", language=lang_name)
                if current_public:
                    user.play_sound("checkbox_list_off.wav")
                else:
                    user.play_sound("checkbox_list_on.wav")
            self._show_document_visibility(user, folder_name, state, focus_locale=locale_code)

    # ------------------------------------------------------------------
    # Modify categories (admin only)
    # ------------------------------------------------------------------

    def _show_document_categories(
        self,
        user: NetworkUser,
        folder_name: str,
        state: dict,
        focus_slug: str | None = None,
    ) -> None:
        """Show toggle list of all categories with included/excluded."""
        meta = self._documents.get_document_metadata(folder_name)
        if meta is None:
            self._show_document_settings(user, folder_name, state)
            return

        doc_cats = set(meta.get("categories", []))
        all_cats = self._documents.get_categories(user.locale)
        on_label = Localization.get(user.locale, "option-on")
        off_label = Localization.get(user.locale, "option-off")

        items = []
        focus_position = 1
        for cat in all_cats:
            included = cat["slug"] in doc_cats
            status = on_label if included else off_label
            items.append(
                MenuItem(
                    text=f"{cat['name']} {status}",
                    id=f"cat_{cat['slug']}",
                )
            )
            if cat["slug"] == focus_slug:
                focus_position = len(items)

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "document_categories_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=focus_position,
        )
        self._user_states[user.username] = {
            "menu": "document_categories_menu",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_document_categories_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle category toggle selection."""
        folder_name = state.get("folder_name", "")
        if selection_id == "back":
            self._show_document_settings(user, folder_name, state)
        elif selection_id.startswith("cat_"):
            if not self._is_admin(user):
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            slug = selection_id[4:]
            meta = self._documents.get_document_metadata(folder_name)
            if meta:
                cats = list(meta.get("categories", []))
                if slug in cats:
                    cats.remove(slug)
                    user.play_sound("checkbox_list_off.wav")
                else:
                    cats.append(slug)
                    user.play_sound("checkbox_list_on.wav")
                self._documents.set_document_categories(folder_name, cats)
                user.speak_l("documents-categories-updated")
            self._show_document_categories(user, folder_name, state, focus_slug=slug)

    # ------------------------------------------------------------------
    # Remove translation (admin only)
    # ------------------------------------------------------------------

    def _show_remove_translation_languages(
        self, user: NetworkUser, folder_name: str, state: dict
    ) -> None:
        """Show language selection for removing a translation."""
        meta = self._documents.get_document_metadata(folder_name)
        if meta is None:
            self._show_document_settings(user, folder_name, state)
            return

        source_locale = meta.get("source_locale", "en")
        doc_locales = self._get_user_accessible_locales(user, folder_name)

        if not doc_locales:
            user.speak_l("documents-no-permission")
            self._show_document_settings(user, folder_name, state)
            return

        items = []
        for locale_code in doc_locales:
            lang_name = Localization.get(user.locale, f"language-{locale_code}")
            items.append(MenuItem(text=lang_name, id=f"lang_{locale_code}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "remove_translation_lang_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "remove_translation_lang_menu",
            "folder_name": folder_name,
            "source_locale": source_locale,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_remove_translation_lang_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle language selection for removing a translation."""
        folder_name = state.get("folder_name", "")
        source_locale = state.get("source_locale", "en")
        if selection_id == "back":
            self._show_document_settings(user, folder_name, state)
        elif selection_id.startswith("lang_"):
            locale_code = selection_id[5:]
            if locale_code == source_locale:
                user.speak_l("documents-remove-translation-source")
                self._show_remove_translation_languages(user, folder_name, state)
            else:
                self._show_remove_translation_confirm(
                    user,
                    folder_name,
                    locale_code,
                    state,
                )

    def _show_remove_translation_confirm(
        self, user: NetworkUser, folder_name: str, locale_code: str, state: dict
    ) -> None:
        """Show yes/no confirmation for removing a translation."""

        lang_name = Localization.get(user.locale, f"language-{locale_code}")
        question = Localization.get(
            user.locale,
            "documents-remove-translation-confirm",
            language=lang_name,
        )
        show_yes_no_menu(user, "remove_translation_confirm", question)
        self._user_states[user.username] = {
            "menu": "remove_translation_confirm",
            "folder_name": folder_name,
            "locale_code": locale_code,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_remove_translation_confirm(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle remove-translation confirmation."""
        folder_name = state.get("folder_name", "")
        locale_code = state.get("locale_code", "")
        if not self._is_admin(user):
            self._deny_document_permission(user, folder_name=folder_name, state=state)
            return
        if selection_id == "yes":
            lock_holder = self._documents.get_edit_lock_holder(
                folder_name,
                locale_code,
            )
            if lock_holder:
                lang_name = Localization.get(
                    user.locale,
                    f"language-{locale_code}",
                )
                user.speak_l(
                    "documents-remove-translation-locked",
                    language=lang_name,
                    username=lock_holder,
                )
                self._show_document_settings(user, folder_name, state)
                return
            # Check if a title exists for this locale — if so, ask
            # whether to remove it as well.
            meta = self._documents.get_document_metadata(folder_name)
            has_title = bool(meta and meta.get("titles", {}).get(locale_code))
            if has_title:
                self._show_remove_translation_title_confirm(
                    user,
                    folder_name,
                    locale_code,
                    state,
                )
                return
            # No title to ask about — remove immediately.
            self._documents.remove_document_translation(
                folder_name,
                locale_code,
            )
            lang_name = Localization.get(
                user.locale,
                f"language-{locale_code}",
            )
            user.speak_l(
                "documents-translation-removed",
                language=lang_name,
            )
        self._show_document_settings(user, folder_name, state)

    def _show_remove_translation_title_confirm(
        self,
        user: NetworkUser,
        folder_name: str,
        locale_code: str,
        state: dict,
    ) -> None:
        """Ask whether to also remove the title when removing a translation."""

        lang_name = Localization.get(user.locale, f"language-{locale_code}")
        question = Localization.get(
            user.locale,
            "documents-remove-title-confirm",
            language=lang_name,
        )
        show_yes_no_menu(user, "remove_translation_title_confirm", question)
        self._user_states[user.username] = {
            "menu": "remove_translation_title_confirm",
            "folder_name": folder_name,
            "locale_code": locale_code,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_remove_translation_title_confirm(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle title removal confirmation after translation removal."""
        folder_name = state.get("folder_name", "")
        locale_code = state.get("locale_code", "")
        if not self._is_admin(user):
            self._deny_document_permission(user, folder_name=folder_name, state=state)
            return
        remove_title = selection_id == "yes"
        self._documents.remove_document_translation(
            folder_name,
            locale_code,
            remove_title=remove_title,
        )
        lang_name = Localization.get(user.locale, f"language-{locale_code}")
        user.speak_l("documents-translation-removed", language=lang_name)
        self._show_document_settings(user, folder_name, state)

    # ------------------------------------------------------------------
    # Delete document (admin only)
    # ------------------------------------------------------------------

    def _show_delete_document_confirm(
        self, user: NetworkUser, folder_name: str, state: dict
    ) -> None:
        """Show yes/no confirmation for deleting a document."""

        count = self._documents.get_document_locale_count(folder_name)
        question = Localization.get(
            user.locale,
            "documents-delete-confirm",
            count=str(count),
        )
        show_yes_no_menu(user, "delete_document_confirm", question)
        self._user_states[user.username] = {
            "menu": "delete_document_confirm",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_delete_document_confirm(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle delete-document confirmation."""
        folder_name = state.get("folder_name", "")
        category_slug = state.get("category_slug")
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        if selection_id == "yes":
            active_locks = self._documents.get_document_lock_holders(
                folder_name,
            )
            if active_locks:
                locale_code, lock_holder = next(iter(active_locks.items()))
                lang_name = Localization.get(
                    user.locale,
                    f"language-{locale_code}",
                )
                user.speak_l(
                    "documents-delete-locked",
                    language=lang_name,
                    username=lock_holder,
                )
                self._show_document_settings(user, folder_name, state)
            else:
                self._documents.delete_document(folder_name)
                user.speak_l("documents-deleted")
                self._show_documents_list(user, category_slug)
        else:
            self._show_document_settings(user, folder_name, state)

    # ------------------------------------------------------------------
    # Edit document content
    # ------------------------------------------------------------------

    def _show_edit_language_menu(self, user: NetworkUser, folder_name: str, state: dict) -> None:
        """Show language selection for editing document content."""
        locales = self._get_user_accessible_locales(user, folder_name)
        if not locales:
            user.speak_l("documents-no-permission")
            self._show_document_actions(user, folder_name, state)
            return

        meta = self._documents.get_document_metadata(folder_name)
        source_locale = meta.get("source_locale", "en") if meta else "en"

        items = []
        focus_position = 1
        for locale_code in locales:
            lang_name = Localization.get(user.locale, f"language-{locale_code}")
            items.append(MenuItem(text=lang_name, id=f"lang_{locale_code}"))
            if locale_code == user.locale:
                focus_position = len(items)
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "document_edit_lang_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=focus_position,
        )
        self._user_states[user.username] = {
            "menu": "document_edit_lang_menu",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_edit_lang_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle language selection for editing."""
        folder_name = state.get("folder_name", "")
        if selection_id == "back":
            self._show_document_actions(user, folder_name, state)
        elif selection_id.startswith("lang_"):
            locale_code = selection_id[5:]
            if locale_code not in self._get_user_accessible_locales(user, folder_name):
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            self._open_document_editor(
                user,
                folder_name,
                locale_code,
                state,
                flow="edit",
            )

    # ------------------------------------------------------------------
    # Add translation
    # ------------------------------------------------------------------

    def _show_add_translation_languages(
        self, user: NetworkUser, folder_name: str, state: dict
    ) -> None:
        """Show language selection for adding a new translation."""
        meta = self._documents.get_document_metadata(folder_name)
        if meta is None:
            self._show_document_settings(user, folder_name, state)
            return

        available = self._get_add_translation_locales(user, folder_name, meta)

        if not available:
            user.speak_l("documents-no-languages-available")
            self._show_document_settings(user, folder_name, state)
            return

        items = []
        focus_position = 1
        for locale_code in available:
            lang_name = Localization.get(user.locale, f"language-{locale_code}")
            items.append(MenuItem(text=lang_name, id=f"lang_{locale_code}"))
            if locale_code == user.locale:
                focus_position = len(items)
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "add_translation_lang_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=focus_position,
        )
        self._user_states[user.username] = {
            "menu": "add_translation_lang_menu",
            "folder_name": folder_name,
            "category_slug": state.get("category_slug"),
        }

    async def _handle_add_translation_lang_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle language selection for adding a translation."""
        folder_name = state.get("folder_name", "")
        if selection_id == "back":
            self._show_document_settings(user, folder_name, state)
        elif selection_id.startswith("lang_"):
            locale_code = selection_id[5:]
            assigned = self._get_user_assigned_languages(user.username)
            if not self._is_admin(user) and locale_code not in assigned:
                self._deny_document_permission(user, folder_name=folder_name, state=state)
                return
            # Show title editbox for the new translation, pre-populated
            # with existing title if one was set (e.g. via change-title).
            lang_name = Localization.get(user.locale, f"language-{locale_code}")
            prompt = Localization.get(
                user.locale,
                "documents-title-prompt",
                language=lang_name,
            )
            existing_title = ""
            meta = self._documents.get_document_metadata(folder_name)
            if meta:
                existing_title = meta.get("titles", {}).get(locale_code, "")
            user.show_editbox(
                "document_title_editbox",
                prompt,
                default_value=existing_title,
            )
            self._user_states[user.username] = {
                "menu": "document_title_editbox",
                "folder_name": folder_name,
                "locale_code": locale_code,
                "category_slug": state.get("category_slug"),
                "flow": "add_translation",
            }

    # ------------------------------------------------------------------
    # Shared document editor
    # ------------------------------------------------------------------

    def _open_document_editor(
        self,
        user: NetworkUser,
        folder_name: str,
        locale_code: str,
        state: dict,
        flow: str = "edit",
        pending_title: str | None = None,
    ) -> None:
        """Open the document editor dialog.

        Args:
            flow: ``"edit"`` for editing existing content,
                  ``"add_translation"`` for a new translation,
                  ``"new_document"`` for creating a new document.
            pending_title: Title for the new translation/document.
        """
        if flow == "new_document":
            # Document doesn't exist yet — no metadata, lock, or content.
            content = ""
            source_content = None
            source_label = None
            title = pending_title or folder_name
        else:
            meta = self._documents.get_document_metadata(folder_name)
            if meta is None:
                self._show_document_actions(user, folder_name, state)
                return

            # Acquire edit lock
            lock_owner = self._documents.acquire_edit_lock(
                folder_name,
                locale_code,
                user.username,
            )
            if lock_owner:
                user.speak_l("documents-locked", username=lock_owner)
                if flow == "add_translation":
                    self._show_document_settings(user, folder_name, state)
                else:
                    self._show_document_actions(user, folder_name, state)
                return

            # Load content
            if flow == "add_translation":
                content = ""
            else:
                content = (
                    self._documents.get_document_content(
                        folder_name,
                        locale_code,
                    )
                    or ""
                )

            # Source reference for non-source locales
            source_locale = meta.get("source_locale", "en")
            source_content = None
            source_label = None
            if locale_code != source_locale:
                source_content = self._documents.get_document_content(
                    folder_name,
                    source_locale,
                )
                if source_content:
                    source_lang = Localization.get(
                        user.locale,
                        f"language-{source_locale}",
                    )
                    source_label = Localization.get(
                        user.locale,
                        "documents-source-label",
                        language=source_lang,
                    )

            title = pending_title or self._get_document_title(
                folder_name,
                locale_code,
            )

        # Build prompt and content label
        lang_name = Localization.get(user.locale, f"language-{locale_code}")
        prompt = Localization.get(
            user.locale,
            "documents-editor-prompt",
            title=title,
            language=lang_name,
        )
        content_label = Localization.get(
            user.locale,
            "documents-content-label",
            language=lang_name,
        )

        dialog_id = f"doc_edit_{folder_name}_{locale_code}"
        user.show_document_editor(
            dialog_id=dialog_id,
            content=content,
            content_label=content_label,
            source_content=source_content,
            source_label=source_label,
            prompt=prompt,
        )
        self._user_states[user.username] = {
            "menu": "document_editor",
            "folder_name": folder_name,
            "locale_code": locale_code,
            "category_slug": state.get("category_slug"),
            "selected_categories": state.get("selected_categories", []),
            "new_document_scope": state.get("new_document_scope", SCOPE_INDEPENDENT),
            "flow": flow,
            "pending_title": pending_title,
            "dialog_id": dialog_id,
        }

    async def _handle_document_editor_response(
        self, user: NetworkUser, packet: dict, state: dict
    ) -> None:
        """Handle save/cancel from the document editor dialog."""
        if state.get("menu") != "document_editor":
            return

        folder_name = state.get("folder_name", "")
        locale_code = state.get("locale_code", "")
        flow = state.get("flow", "edit")
        dialog_id = state.get("dialog_id", "")

        if packet.get("dialog_id") != dialog_id:
            return

        action = packet.get("action", "cancel")

        if flow == "new_document":
            # Creating a brand-new document — no lock was acquired.
            if action == "save":
                content = packet.get("content", "")
                pending_title = state.get("pending_title", "")
                selected_categories = state.get("selected_categories", [])
                scope = state.get("new_document_scope", SCOPE_INDEPENDENT)
                self._documents.create_document(
                    folder_name,
                    selected_categories,
                    locale_code,
                    pending_title,
                    content,
                    scope=scope,
                )
                user.speak_l("documents-document-created")
                if scope == SCOPE_SHARED:
                    self._show_commit_message_editbox(
                        user, folder_name, locale_code, flow,
                    )
                    return
            self._show_documents_menu(user)
            return

        # Guard against the document or translation being removed while
        # the editor was open (e.g. an admin deleted it on the backend,
        # or a reconnected client submitted after its lock went stale).
        meta = self._documents.get_document_metadata(folder_name)

        if action == "save" and meta is not None:
            content = packet.get("content", "")
            is_shared = (
                self._documents.get_document_scope(folder_name) == SCOPE_SHARED
            )
            if flow == "add_translation":
                pending_title = state.get("pending_title", "")
                self._documents.add_document_translation(
                    folder_name,
                    locale_code,
                    pending_title,
                    content,
                )
                # Release lock (add_document_translation doesn't do it)
                self._documents.release_edit_lock(
                    folder_name,
                    locale_code,
                    user.username,
                )
                lang_name = Localization.get(
                    user.locale,
                    f"language-{locale_code}",
                )
                user.speak_l("documents-translation-added", language=lang_name)
            else:
                # save_document_content handles backup + lock release
                self._documents.save_document_content(
                    folder_name,
                    locale_code,
                    content,
                    user.username,
                )
                lang_name = Localization.get(
                    user.locale,
                    f"language-{locale_code}",
                )
                user.speak_l("documents-content-saved", language=lang_name)

            # Chain to commit message editbox for shared documents
            if is_shared:
                self._show_commit_message_editbox(
                    user, folder_name, locale_code, flow,
                )
                return
        else:
            # Cancel — release lock (safe even if already cleared)
            self._documents.release_edit_lock(
                folder_name,
                locale_code,
                user.username,
            )

        # Return to appropriate menu.  If the document was removed while
        # the editor was open, fall back to the top-level documents list.
        if meta is None:
            self._show_documents_menu(user)
        elif flow == "add_translation":
            self._show_document_settings(user, folder_name, state)
        else:
            self._show_document_actions(user, folder_name, state)

    # ------------------------------------------------------------------
    # Commit message (shared document saves)
    # ------------------------------------------------------------------

    def _show_commit_message_editbox(
        self,
        user: NetworkUser,
        folder_name: str,
        locale_code: str,
        flow: str,
    ) -> None:
        """Show an editbox prompting for a commit/change description.

        Displayed after every save to a shared document, regardless of
        contribution mode.  The text entered is used differently per mode:
        manual stores it in the attribution log; auto modes pass it as
        the git commit message.
        """
        prompt = Localization.get(
            user.locale, "documents-commit-message-prompt",
        )
        user.show_editbox("commit_message_editbox", prompt, multiline = True)
        self._user_states[user.username] = {
            "menu": "commit_message_editbox",
            "folder_name": folder_name,
            "locale_code": locale_code,
            "flow": flow,
        }

    def _handle_commit_message(
        self, user: NetworkUser, text: str, state: dict
    ) -> None:
        """Process the commit message after a shared document save."""
        folder_name = state.get("folder_name", "")
        locale_code = state.get("locale_code", "")
        flow = state.get("flow", "edit")
        message = text.strip()

        mode = self._documents.contribution_mode

        if mode == MODE_MANUAL:
            # Determine change type from the flow
            if flow == "new_document":
                change_type = "create"
            elif flow == "add_translation":
                change_type = "translation_add"
            else:
                change_type = "edit"
            self._documents._log_attribution(
                folder_name, locale_code, user.username, change_type, message,
            )
        else:
            # auto_commit / auto_pr — commit the staged changes
            success, error = self._documents.commit_changes(
                folder_name, locale_code, user.username, message,
            )
            if success:
                user.speak_l("documents-commit-success")
            else:
                user.speak_l("documents-commit-failed", reason=error)

        # Return to the appropriate menu
        if flow == "new_document":
            self._show_documents_menu(user)
        elif flow == "add_translation":
            self._show_document_settings(user, folder_name, state)
        else:
            self._show_document_actions(user, folder_name, state)

    # ------------------------------------------------------------------
    # New document creation
    # ------------------------------------------------------------------

    def _show_new_document_scope(self, user: NetworkUser) -> None:
        """Show scope selection menu for a new document."""
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        items = [
            MenuItem(
                text=Localization.get(user.locale, "documents-scope-shared"),
                id="shared",
            ),
            MenuItem(
                text=Localization.get(user.locale, "documents-scope-independent"),
                id="independent",
            ),
            MenuItem(
                text=Localization.get(user.locale, "back"),
                id="back",
            ),
        ]
        user.speak_l("documents-scope-prompt")
        user.show_menu(
            "new_document_scope_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "new_document_scope_menu"}

    async def _handle_new_document_scope_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle scope selection for new document creation."""
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        if selection_id == "back":
            self._show_documents_menu(user)
            return
        scope = SCOPE_SHARED if selection_id == "shared" else SCOPE_INDEPENDENT
        self._user_states[user.username] = {
            "menu": "new_document_scope_menu",
            "new_document_scope": scope,
        }
        self._show_new_document_categories(user)

    def _show_new_document_categories(
        self,
        user: NetworkUser,
        focus_slug: str | None = None,
    ) -> None:
        """Show category toggle list for a new document.

        If there are no categories, skips straight to the title editbox.
        """
        state = self._user_states.get(user.username, {})
        scope = state.get("new_document_scope", SCOPE_INDEPENDENT)
        selected = set(state.get("selected_categories", []))

        all_cats = self._documents.get_categories(user.locale)

        # No categories — skip straight to slug.
        if not all_cats:
            new_state = {
                "selected_categories": [],
                "new_document_scope": scope,
            }
            self._show_new_document_slug_editbox(user, new_state)
            return

        on_label = Localization.get(user.locale, "option-on")
        off_label = Localization.get(user.locale, "option-off")

        items = []
        focus_position = 1
        for cat in all_cats:
            included = cat["slug"] in selected
            status = on_label if included else off_label
            items.append(
                MenuItem(
                    text=f"{cat['name']} {status}",
                    id=f"cat_{cat['slug']}",
                )
            )
            if cat["slug"] == focus_slug:
                focus_position = len(items)

        items.append(MenuItem(text=Localization.get(user.locale, "done"), id="done"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        # Speak the prompt on first display (no focus_slug means fresh entry).
        if focus_slug is None:
            user.speak_l("documents-select-categories")

        user.show_menu(
            "new_document_categories_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=focus_position,
        )
        self._user_states[user.username] = {
            "menu": "new_document_categories_menu",
            "selected_categories": list(selected),
            "new_document_scope": scope,
        }

    async def _handle_new_document_categories_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle category toggle/done/back for new document creation."""
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        if selection_id == "back":
            self._show_documents_menu(user)
        elif selection_id == "done":
            self._show_new_document_slug_editbox(user, state)
        elif selection_id.startswith("cat_"):
            slug = selection_id[4:]
            selected = list(state.get("selected_categories", []))
            if slug in selected:
                selected.remove(slug)
                user.play_sound("checkbox_list_off.wav")
            else:
                selected.append(slug)
                user.play_sound("checkbox_list_on.wav")
            state["selected_categories"] = selected
            self._user_states[user.username]["selected_categories"] = selected
            self._show_new_document_categories(user, focus_slug=slug)

    def _show_new_document_slug_editbox(self, user: NetworkUser, state: dict) -> None:
        """Show the slug editbox for a new document."""
        prompt = Localization.get(
            user.locale,
            "documents-new-document-slug-prompt",
        )
        user.show_editbox("new_document_slug_editbox", prompt)
        self._user_states[user.username] = {
            "menu": "new_document_slug_editbox",
            "selected_categories": state.get("selected_categories", []),
            "new_document_scope": state.get("new_document_scope", SCOPE_INDEPENDENT),
        }

    def _handle_new_document_slug(self, user: NetworkUser, value: str, state: dict) -> None:
        """Handle slug editbox submission for a new document."""
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        if not value.strip():
            self._show_documents_menu(user)
            return

        slug = value.strip().lower().replace(" ", "_")
        if not re.fullmatch(r"[a-z0-9_]+", slug):
            user.speak_l("documents-slug-invalid")
            self._show_new_document_slug_editbox(user, state)
            return

        if self._documents.get_document_metadata(slug) is not None:
            user.speak_l("documents-slug-exists")
            self._show_new_document_slug_editbox(user, state)
            return

        # Proceed to title editbox.
        lang_name = Localization.get(user.locale, f"language-{user.locale}")
        prompt = Localization.get(
            user.locale,
            "documents-title-prompt",
            language=lang_name,
        )
        user.show_editbox("document_title_editbox", prompt)
        self._user_states[user.username] = {
            "menu": "document_title_editbox",
            "folder_name": slug,
            "locale_code": user.locale,
            "selected_categories": state.get("selected_categories", []),
            "new_document_scope": state.get("new_document_scope", SCOPE_INDEPENDENT),
            "flow": "new_document",
        }

    # ------------------------------------------------------------------
    # New category creation
    # ------------------------------------------------------------------

    def _show_new_category_slug_editbox(self, user: NetworkUser) -> None:
        """Show the slug editbox for a new category."""
        prompt = Localization.get(
            user.locale,
            "documents-new-category-slug-prompt",
        )
        user.show_editbox("new_category_slug_editbox", prompt)
        self._user_states[user.username] = {
            "menu": "new_category_slug_editbox",
        }

    def _handle_new_category_slug(self, user: NetworkUser, value: str, state: dict) -> None:
        """Handle slug editbox submission for a new category."""
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        if not value.strip():
            self._show_documents_menu(user)
            return

        slug = value.strip().lower().replace(" ", "_")
        if not re.fullmatch(r"[a-z0-9_]+", slug):
            user.speak_l("documents-slug-invalid")
            self._show_new_category_slug_editbox(user)
            return

        # Check for existing category with this slug.
        categories = self._documents.get_categories(user.locale)
        if any(cat["slug"] == slug for cat in categories):
            user.speak_l("documents-slug-exists-category")
            self._show_new_category_slug_editbox(user)
            return

        lang_name = Localization.get(user.locale, f"language-{user.locale}")
        prompt = Localization.get(
            user.locale,
            "documents-category-name-prompt",
            language=lang_name,
        )
        user.show_editbox(
            "new_category_name_editbox",
            prompt,
        )
        self._user_states[user.username] = {
            "menu": "new_category_name_editbox",
            "category_slug": slug,
        }

    def _handle_new_category_name(self, user: NetworkUser, value: str, state: dict) -> None:
        """Handle name editbox submission for a new category."""
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        slug = state.get("category_slug", "")
        if not value.strip():
            self._show_documents_menu(user)
            return

        name = value.strip()
        self._documents.create_category(slug, name, user.locale)
        user.speak_l("documents-category-created")
        self._show_documents_menu(user)

    # ------------------------------------------------------------------
    # Category management (rename, settings, delete)
    # ------------------------------------------------------------------

    def _show_rename_category_editbox(
        self,
        user: NetworkUser,
        category_slug: str,
    ) -> None:
        """Show the rename editbox for a category."""
        # Get current display name as default value
        categories = self._documents.get_categories(user.locale)
        current_name = ""
        for cat in categories:
            if cat["slug"] == category_slug:
                current_name = cat["name"]
                break

        lang_name = Localization.get(user.locale, f"language-{user.locale}")
        prompt = Localization.get(
            user.locale,
            "documents-category-name-prompt",
            language=lang_name,
        )
        user.show_editbox(
            "rename_category_editbox",
            prompt,
            default_value=current_name,
        )
        self._user_states[user.username] = {
            "menu": "rename_category_editbox",
            "category_slug": category_slug,
        }

    def _handle_rename_category(self, user: NetworkUser, value: str, state: dict) -> None:
        """Handle rename editbox submission for a category."""
        if not (self._is_transcriber(user.username) or self._is_admin(user)):
            self._deny_document_permission(user)
            return
        slug = state.get("category_slug", "")
        if not value.strip():
            self._show_documents_list(user, slug)
            return

        name = value.strip()
        self._documents.rename_category(slug, name, user.locale)
        user.speak_l("documents-category-renamed")
        self._show_documents_list(user, slug)

    def _show_category_settings(
        self,
        user: NetworkUser,
        category_slug: str,
    ) -> None:
        """Show category settings submenu (sort method)."""
        current_sort = self._documents.get_category_sort(category_slug)
        sort_label = Localization.get(
            user.locale,
            f"documents-sort-{current_sort.replace('_', '-')}",
        )
        sort_text = Localization.get(
            user.locale,
            "documents-sort-method",
        )
        items = [
            MenuItem(
                text=f"{sort_text}: {sort_label}",
                id="sort_method",
            ),
            MenuItem(
                text=Localization.get(user.locale, "back"),
                id="back",
            ),
        ]
        user.show_menu(
            "category_settings_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "category_settings_menu",
            "category_slug": category_slug,
        }

    async def _handle_category_settings_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle category settings submenu selection."""
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        category_slug = state.get("category_slug", "")
        if selection_id == "back":
            self._show_documents_list(user, category_slug)
        elif selection_id == "sort_method":
            self._show_category_sort_menu(user, category_slug)

    def _show_category_sort_menu(
        self,
        user: NetworkUser,
        category_slug: str,
    ) -> None:
        """Show the sort method selection menu."""
        current_sort = self._documents.get_category_sort(category_slug)
        sort_options = ["alphabetical", "date_created", "date_modified"]

        items = []
        focus_position = 1
        for sort_method in sort_options:
            label = Localization.get(
                user.locale,
                f"documents-sort-{sort_method.replace('_', '-')}",
            )
            if sort_method == current_sort:
                label = f"* {label}"
                focus_position = len(items) + 1
            items.append(MenuItem(text=label, id=sort_method))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "category_sort_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=focus_position,
        )
        self._user_states[user.username] = {
            "menu": "category_sort_menu",
            "category_slug": category_slug,
        }

    async def _handle_category_sort_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle sort method selection."""
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        category_slug = state.get("category_slug", "")
        if selection_id == "back":
            self._show_category_settings(user, category_slug)
        elif selection_id in ("alphabetical", "date_created", "date_modified"):
            self._documents.set_category_sort(category_slug, selection_id)
            user.speak_l("documents-sort-changed")
            self._show_category_settings(user, category_slug)

    def _show_delete_category_confirm(
        self,
        user: NetworkUser,
        category_slug: str,
    ) -> None:
        """Show yes/no confirmation for deleting a category."""
        question = Localization.get(
            user.locale,
            "documents-delete-category-confirm",
        )
        show_yes_no_menu(user, "delete_category_confirm", question)
        self._user_states[user.username] = {
            "menu": "delete_category_confirm",
            "category_slug": category_slug,
        }

    async def _handle_delete_category_confirm(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle delete-category confirmation."""
        if not self._is_admin(user):
            self._deny_document_permission(user)
            return
        category_slug = state.get("category_slug", "")
        if selection_id == "yes":
            self._documents.delete_category(category_slug)
            user.speak_l("documents-category-deleted")
            self._show_documents_menu(user)
        else:
            self._show_documents_list(user, category_slug)
