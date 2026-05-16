"""Transcriber management menus for the PlayPalace server."""

from typing import TYPE_CHECKING

from ..users.network_user import NetworkUser
from ..users.base import MenuItem, EscapeBehavior, TrustLevel
from ...messages.localization import Localization

if TYPE_CHECKING:
    from ...persistence.database import Database


class TranscriberRoleMixin:
    """Provide transcriber assignment and management menus.

    Expected attributes:
        _db: Database instance.
        _user_states: dict[str, dict] of user menu states.
        _show_documents_menu(user): Method to show the documents menu.
    """

    _db: "Database"
    _user_states: dict[str, dict]

    def _transcriber_admin_denied(self, user: NetworkUser) -> None:
        """Reject a transcriber-management action for non-admins."""
        user.speak_l("documents-no-permission")
        self._show_documents_menu(user)

    def _get_transcriber_menu_handlers(
        self, user: "NetworkUser", selection_id: str, state: dict
    ) -> dict[str, tuple]:
        """Return menu dispatch entries for transcriber management."""
        return {
            "transcribers_for_language_menu": (
                self._handle_transcribers_for_language_selection,
                (user, selection_id, state),
            ),
            "transcriber_remove_confirm": (
                self._handle_transcriber_remove_confirm,
                (user, selection_id, state),
            ),
            "add_transcriber_users_menu": (
                self._handle_add_transcriber_users_selection,
                (user, selection_id, state),
            ),
            "transcribers_by_user_menu": (
                self._handle_transcribers_by_user_selection,
                (user, selection_id, state),
            ),
            "add_transcriber_user_picker_menu": (
                self._handle_add_transcriber_user_picker_selection,
                (user, selection_id, state),
            ),
            "transcriber_user_languages_menu": (
                self._handle_transcriber_user_languages_selection,
                (user, selection_id, state),
            ),
            "transcriber_remove_lang_confirm": (
                self._handle_transcriber_remove_lang_confirm,
                (user, selection_id, state),
            ),
            "transcriber_remove_all_confirm": (
                self._handle_transcriber_remove_all_confirm,
                (user, selection_id, state),
            ),
        }

    # -- Transcriber management menus --

    def _show_transcribers_by_language(self, user: NetworkUser) -> None:
        """Show the language list with transcriber counts per language."""
        from server.core.ui.common_flows import show_language_menu

        all_transcribers = self._db.get_all_transcribers()
        is_admin = user.trust_level.value >= TrustLevel.ADMIN.value
        # Count transcribers per language
        lang_counts: dict[str, int] = {}
        for langs in all_transcribers.values():
            for lang in langs:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

        status_labels = {}
        lang_codes = None
        if is_admin:
            for code in Localization.get_available_locale_codes():
                count = lang_counts.get(code, 0)
                label = f"({count} {'user' if count == 1 else 'users'})"
                status_labels[code] = label
        else:
            # Non-admins only see languages that have at least one transcriber.
            lang_codes = [
                code
                for code in Localization.get_available_locale_codes()
                if lang_counts.get(code, 0) > 0
            ]
            if not lang_codes:
                user.speak_l("transcribers-no-transcribers")
                self._show_documents_menu(user)
                return
            for code in lang_codes:
                count = lang_counts[code]
                label = f"({count} {'user' if count == 1 else 'users'})"
                status_labels[code] = label

        if show_language_menu(
            user,
            highlight_active_locale=False,
            lang_codes=lang_codes,
            status_labels=status_labels,
            on_select=self._on_transcribers_by_language_select,
            on_back=lambda u: self._show_documents_menu(u),
        ):
            self._user_states[user.username] = {"menu": "language_menu"}

    async def _on_transcribers_by_language_select(self, user: NetworkUser, lang_code: str) -> None:
        """Handle language selection in transcribers-by-language view."""
        self._show_transcribers_for_language(user, lang_code)

    def _show_transcribers_for_language(self, user: NetworkUser, lang_code: str) -> None:
        """Show list of transcribers assigned to a language."""
        usernames = self._db.get_transcribers_for_language(lang_code)
        is_admin = user.trust_level.value >= TrustLevel.ADMIN.value

        if not usernames and not is_admin:
            user.speak_l("transcribers-no-users")
            self._show_transcribers_by_language(user)
            return

        items = []
        for username in usernames:
            items.append(MenuItem(text=username, id=f"user_{username}"))
        if is_admin:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "transcribers-add-users"),
                    id="add_users",
                )
            )
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "transcribers_for_language_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "transcribers_for_language_menu",
            "lang_code": lang_code,
        }

    async def _handle_transcribers_for_language_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle selection in the transcribers-for-language menu."""
        lang_code = state.get("lang_code", "")
        if selection_id == "back":
            self._show_transcribers_by_language(user)
        elif selection_id == "add_users":
            if user.trust_level.value < TrustLevel.ADMIN.value:
                self._transcriber_admin_denied(user)
                return
            self._show_add_transcriber_users(user, lang_code)
        elif selection_id.startswith("user_"):
            target_username = selection_id[5:]
            if user.trust_level.value >= TrustLevel.ADMIN.value:
                self._show_transcriber_remove_confirm(user, target_username, lang_code)
            else:
                self._show_transcribers_for_language(user, lang_code)

    def _show_transcriber_remove_confirm(
        self, user: NetworkUser, target_username: str, lang_code: str
    ) -> None:
        """Ask admin to confirm removing a transcriber from a language."""
        from server.core.ui.common_flows import show_yes_no_menu

        lang_name = Localization.get(user.locale, f"language-{lang_code}")
        question = Localization.get(
            user.locale,
            "transcribers-remove-confirm",
            user=target_username,
            language=lang_name,
        )
        show_yes_no_menu(user, "transcriber_remove_confirm", question)
        self._user_states[user.username] = {
            "menu": "transcriber_remove_confirm",
            "target_username": target_username,
            "lang_code": lang_code,
        }

    async def _handle_transcriber_remove_confirm(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle transcriber removal confirmation."""
        lang_code = state.get("lang_code", "")
        target_username = state.get("target_username", "")
        if user.trust_level.value < TrustLevel.ADMIN.value:
            self._transcriber_admin_denied(user)
            return
        if selection_id == "yes":
            self._db.remove_transcriber_assignment(target_username, lang_code)
            lang_name = Localization.get(user.locale, f"language-{lang_code}")
            user.speak_l(
                "transcribers-removed",
                user=target_username,
                language=lang_name,
            )
        self._show_transcribers_for_language(user, lang_code)

    def _show_add_transcriber_users(
        self,
        user: NetworkUser,
        lang_code: str,
        enabled_users: set[str] | None = None,
        focus_username: str | None = None,
    ) -> None:
        """Show toggle list of eligible users to add as transcribers for a language.

        Only shows users who are fluent in the language but not already assigned.
        """
        existing = set(self._db.get_transcribers_for_language(lang_code))
        all_users = self._db.get_non_admin_users() + self._db.get_admin_users()
        if enabled_users is None:
            enabled_users = set()
        on_label = Localization.get(user.locale, "option-on")
        off_label = Localization.get(user.locale, "option-off")
        items = []
        focus_position = 1
        for u in sorted(all_users, key=lambda r: r.username.lower()):
            if lang_code not in u.fluent_languages:
                continue
            if u.username in existing:
                continue
            status = on_label if u.username in enabled_users else off_label
            items.append(
                MenuItem(
                    text=f"{u.username} {status}",
                    id=f"toggle_{u.username}",
                )
            )
            if u.username == focus_username:
                focus_position = len(items)
        if not items:
            user.speak_l("transcribers-no-eligible-users")
            self._show_transcribers_for_language(user, lang_code)
            return

        items.append(MenuItem(text=Localization.get(user.locale, "done"), id="done"))
        items.append(MenuItem(text=Localization.get(user.locale, "cancel"), id="cancel"))
        user.show_menu(
            "add_transcriber_users_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=focus_position,
        )
        self._user_states[user.username] = {
            "menu": "add_transcriber_users_menu",
            "lang_code": lang_code,
            "enabled_users": enabled_users,
        }

    async def _handle_add_transcriber_users_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle selection in the add-transcriber-users menu."""
        lang_code = state.get("lang_code", "")
        enabled_users: set[str] = state.get("enabled_users", set())
        if user.trust_level.value < TrustLevel.ADMIN.value:
            self._transcriber_admin_denied(user)
            return
        if selection_id == "done":
            if enabled_users:
                lang_name = Localization.get(user.locale, f"language-{lang_code}")
                for username in enabled_users:
                    self._db.add_transcriber_assignment(username, lang_code)
                users_str = ", ".join(sorted(enabled_users))
                user.speak_l(
                    "transcribers-users-added",
                    users=users_str,
                    language=lang_name,
                )
            self._show_transcribers_for_language(user, lang_code)
        elif selection_id == "cancel":
            self._show_transcribers_for_language(user, lang_code)
        elif selection_id.startswith("toggle_"):
            target_username = selection_id[7:]
            if target_username in enabled_users:
                enabled_users.discard(target_username)
                user.play_sound("checkbox_list_off.wav")
            else:
                enabled_users.add(target_username)
                user.play_sound("checkbox_list_on.wav")
            self._show_add_transcriber_users(
                user,
                lang_code,
                enabled_users,
                focus_username=target_username,
            )

    # -- Transcribers by user --

    def _show_transcribers_by_user(self, user: NetworkUser) -> None:
        """Show list of transcriber users with language counts."""
        all_transcribers = self._db.get_all_transcribers()
        is_admin = user.trust_level.value >= TrustLevel.ADMIN.value

        if not all_transcribers and not is_admin:
            user.speak_l("transcribers-no-transcribers")
            self._show_documents_menu(user)
            return

        items = []
        for username in sorted(all_transcribers.keys(), key=str.lower):
            count = len(all_transcribers[username])
            label = f"{username} ({count} {'language' if count == 1 else 'languages'})"
            items.append(MenuItem(text=label, id=f"user_{username}"))

        if is_admin:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "transcribers-add-user"),
                    id="add_user",
                )
            )
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "transcribers_by_user_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "transcribers_by_user_menu"}

    async def _handle_transcribers_by_user_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle selection in transcribers-by-user menu."""
        if selection_id == "back":
            self._show_documents_menu(user)
        elif selection_id == "add_user":
            if user.trust_level.value < TrustLevel.ADMIN.value:
                self._transcriber_admin_denied(user)
                return
            self._show_add_transcriber_user_picker(user)
        elif selection_id.startswith("user_"):
            target_username = selection_id[5:]
            self._show_transcriber_user_languages(user, target_username)

    def _show_add_transcriber_user_picker(self, user: NetworkUser) -> None:
        """Show list of users who are not yet transcribers to pick one to add."""
        all_transcribers = self._db.get_all_transcribers()
        existing_usernames = set(all_transcribers.keys())
        all_users = self._db.get_non_admin_users() + self._db.get_admin_users()
        items = []
        for u in sorted(all_users, key=lambda r: r.username.lower()):
            if u.username in existing_usernames:
                continue
            if not u.fluent_languages:
                continue
            items.append(MenuItem(text=u.username, id=f"pick_{u.username}"))
        if not items:
            user.speak_l("transcribers-no-users-to-add")
            self._show_transcribers_by_user(user)
            return
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "add_transcriber_user_picker_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "add_transcriber_user_picker_menu",
        }

    async def _handle_add_transcriber_user_picker_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle selection in the add-transcriber user picker."""
        if user.trust_level.value < TrustLevel.ADMIN.value:
            self._transcriber_admin_denied(user)
            return
        if selection_id == "back":
            self._show_transcribers_by_user(user)
        elif selection_id.startswith("pick_"):
            target_username = selection_id[5:]
            self._show_add_transcriber_languages(
                user,
                target_username,
                from_user_list=True,
            )

    def _show_transcriber_user_languages(self, user: NetworkUser, target_username: str) -> None:
        """Show languages assigned to a specific transcriber."""
        lang_codes = self._db.get_transcriber_languages(target_username)
        is_admin = user.trust_level.value >= TrustLevel.ADMIN.value

        if not lang_codes and not is_admin:
            user.speak_l("transcribers-no-languages")
            self._show_transcribers_by_user(user)
            return

        items = []
        for code in lang_codes:
            name = Localization.get(user.locale, f"language-{code}")
            items.append(MenuItem(text=name, id=f"lang_{code}"))
        if is_admin:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "transcribers-add-languages"),
                    id="add_languages",
                )
            )
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "transcribers-remove-transcriber"),
                    id="remove_transcriber",
                )
            )
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "transcriber_user_languages_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "transcriber_user_languages_menu",
            "target_username": target_username,
        }

    async def _handle_transcriber_user_languages_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle selection in a transcriber's language list."""
        target_username = state.get("target_username", "")
        if selection_id == "back":
            self._show_transcribers_by_user(user)
        elif selection_id == "add_languages":
            if user.trust_level.value < TrustLevel.ADMIN.value:
                self._transcriber_admin_denied(user)
                return
            self._show_add_transcriber_languages(user, target_username)
        elif selection_id == "remove_transcriber":
            if user.trust_level.value < TrustLevel.ADMIN.value:
                self._transcriber_admin_denied(user)
                return
            self._show_transcriber_remove_all_confirm(user, target_username)
        elif selection_id.startswith("lang_"):
            lang_code = selection_id[5:]
            if user.trust_level.value >= TrustLevel.ADMIN.value:
                self._show_transcriber_remove_lang_confirm(user, target_username, lang_code)
            else:
                self._show_transcriber_user_languages(user, target_username)

    def _show_transcriber_remove_lang_confirm(
        self, user: NetworkUser, target_username: str, lang_code: str
    ) -> None:
        """Ask admin to confirm removing a language from a transcriber."""
        from server.core.ui.common_flows import show_yes_no_menu

        lang_name = Localization.get(user.locale, f"language-{lang_code}")
        question = Localization.get(
            user.locale,
            "transcribers-remove-lang-confirm",
            user=target_username,
            language=lang_name,
        )
        show_yes_no_menu(user, "transcriber_remove_lang_confirm", question)
        self._user_states[user.username] = {
            "menu": "transcriber_remove_lang_confirm",
            "target_username": target_username,
            "lang_code": lang_code,
        }

    async def _handle_transcriber_remove_lang_confirm(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle language removal confirmation."""
        target_username = state.get("target_username", "")
        lang_code = state.get("lang_code", "")
        if user.trust_level.value < TrustLevel.ADMIN.value:
            self._transcriber_admin_denied(user)
            return
        if selection_id == "yes":
            self._db.remove_transcriber_assignment(target_username, lang_code)
            lang_name = Localization.get(user.locale, f"language-{lang_code}")
            user.speak_l(
                "transcribers-removed",
                user=target_username,
                language=lang_name,
            )
        self._show_transcriber_user_languages(user, target_username)

    def _show_transcriber_remove_all_confirm(self, user: NetworkUser, target_username: str) -> None:
        """Ask admin to confirm removing all transcriber assignments from a user."""
        from server.core.ui.common_flows import show_yes_no_menu

        question = Localization.get(
            user.locale,
            "transcribers-remove-all-confirm",
            user=target_username,
        )
        show_yes_no_menu(user, "transcriber_remove_all_confirm", question)
        self._user_states[user.username] = {
            "menu": "transcriber_remove_all_confirm",
            "target_username": target_username,
        }

    async def _handle_transcriber_remove_all_confirm(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle removal of all transcriber assignments."""
        target_username = state.get("target_username", "")
        if user.trust_level.value < TrustLevel.ADMIN.value:
            self._transcriber_admin_denied(user)
            return
        if selection_id == "yes":
            lang_codes = self._db.get_transcriber_languages(target_username)
            for lang_code in lang_codes:
                self._db.remove_transcriber_assignment(target_username, lang_code)
            user.speak_l("transcribers-removed-all", user=target_username)
        self._show_transcribers_by_user(user)

    def _show_add_transcriber_languages(
        self,
        user: NetworkUser,
        target_username: str,
        from_user_list: bool = False,
    ) -> None:
        """Show language menu filtered to the user's unassigned fluent languages."""
        from server.core.ui.common_flows import show_language_menu

        fluent = self._db.get_user_fluent_languages(target_username)
        assigned = set(self._db.get_transcriber_languages(target_username))
        available = [code for code in fluent if code not in assigned]

        if not available:
            user.speak_l("transcribers-no-eligible-languages")
            if from_user_list:
                self._show_transcribers_by_user(user)
            else:
                self._show_transcriber_user_languages(user, target_username)
            return

        def on_done(u: NetworkUser, selected: set[str]) -> None:
            if selected:
                for lang_code in selected:
                    self._db.add_transcriber_assignment(target_username, lang_code)
                lang_names = [Localization.get(u.locale, f"language-{code}") for code in selected]
                langs_str = ", ".join(sorted(lang_names))
                u.speak_l(
                    "transcribers-languages-added",
                    user=target_username,
                    languages=langs_str,
                )
            if from_user_list:
                self._show_transcribers_by_user(u)
            else:
                self._show_transcriber_user_languages(u, target_username)

        def on_cancel(u: NetworkUser) -> None:
            if from_user_list:
                self._show_transcribers_by_user(u)
            else:
                self._show_transcriber_user_languages(u, target_username)

        if show_language_menu(
            user,
            highlight_active_locale=False,
            multi_select=True,
            lang_codes=available,
            selected=set(),
            on_done=on_done,
            on_cancel=on_cancel,
        ):
            self._user_states[user.username] = {
                "menu": "language_menu",
                "target_username": target_username,
                "from_user_list": from_user_list,
            }
