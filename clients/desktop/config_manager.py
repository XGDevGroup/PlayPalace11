"""Configuration manager for Play Palace client.

Handles client-side configuration including:
- Server management with user accounts (identities.json - private)
- Global default options (option_profiles.json - shareable)
- Per-server option overrides (option_profiles.json - shareable)
"""

import json
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from config_schemas import ExportedIdentities, Identities, Server, UserAccount, validate_identities
from resource_paths import find_resource_path


DEFAULT_SERVERS_ENV = "PLAYPALACE_DEFAULT_SERVERS_FILE"


def get_item_from_dict(dictionary: dict, key_path: (str, tuple), *, create_mode: bool = False):
    """Return the item in a dictionary, typically a nested layer dict.
    Optionally create keys that don't exist, or require the full path to exist already.
    This function supports an infinite number of layers."""
    if isinstance(key_path, str) and len(key_path) > 0:
        if key_path[0] == "/":
            key_path = key_path[1:]
        if key_path[-1] == "/":
            key_path = key_path[:-1]
        key_path = key_path.split("/")
    scope = dictionary
    for l in range(len(key_path)):
        if key_path[l] == "":
            continue
        layer = key_path[l]
        if layer not in scope:
            if not create_mode:
                raise KeyError(
                    f"Key '{layer}' not in "
                    + (
                        ("nested dictionary " + "/".join(key_path[:l]))
                        if l > 0
                        else "root dictionary"
                    )
                    + "."
                )
            scope[layer] = {}
        scope = scope[layer]
    return scope


def set_item_in_dict(
    dictionary: dict, key_path: (str, tuple), value, *, create_mode: bool = False
) -> bool:
    """Modify the value of an item in a dictionary.
    Optionally create keys that don't exist, or require the full path to exist already.
    This function supports an infinite number of layers."""
    if isinstance(key_path, str) and len(key_path) > 0:
        if key_path[0] == "/":
            key_path = key_path[1:]
        if key_path[-1] == "/":
            key_path = key_path[:-1]
        key_path = key_path.split("/")
    if not key_path or key_path[-1] == "":
        raise ValueError("No dictionary key path was specified.")
    final_key = key_path.pop(-1)
    obj = get_item_from_dict(dictionary, key_path, create_mode=create_mode)
    if not isinstance(obj, dict):
        raise TypeError(f"Expected type 'dict', instead got '{type(obj)}'.")
    if not create_mode and final_key not in obj:
        raise KeyError(f"Key '{final_key}' not in dictionary '{key_path}'.")
    obj[final_key] = value
    return True


def delete_item_from_dict(
    dictionary: dict, key_path: (str, tuple), *, delete_empty_layers: bool = True
) -> bool:
    """Delete an item in a dictionary.
    Optionally delete layers that are empty.
    This function supports an infinite number of layers."""
    if isinstance(key_path, str) and len(key_path) > 0:
        if key_path[0] == "/":
            key_path = key_path[1:]
        if key_path[-1] == "/":
            key_path = key_path[:-1]
        key_path = key_path.split("/")
    if not key_path or key_path[-1] == "":
        raise ValueError("No dictionary key path was specified.")
    final_key = key_path.pop(-1)
    obj = get_item_from_dict(dictionary, key_path)
    if not isinstance(obj, dict):
        raise TypeError(f"Expected type 'dict', instead got '{type(obj)}'.")
    if final_key not in obj:
        return False
    del obj[final_key]
    if not delete_empty_layers:
        return True
    # Walk from deepest to shallowest, removing empty dicts
    for i in range(len(key_path), 0, -1):
        try:
            obj = get_item_from_dict(dictionary, key_path[:i])
            if isinstance(obj, dict) and not obj:  # Empty dict
                if i == 1:
                    del dictionary[key_path[0]]
                else:
                    parent = get_item_from_dict(dictionary, key_path[: i - 1])
                    del parent[key_path[i - 1]]
        except KeyError:
            break
    return True


class ConfigManager:
    """Manages client configuration and per-server settings.

    Uses two separate files:
    - identities.json: Contains servers with user accounts (private, not shareable)
    - option_profiles.json: Contains client options (shareable, no credentials)
    """

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the config manager.

        Args:
            base_path: Base directory path. Defaults to ~/.playpalace/
        """
        if base_path is None:
            base_path = Path.home() / ".playpalace"

        self.base_path = base_path
        self.identities_path = base_path / "identities.json"
        self.profiles_path = base_path / "option_profiles.json"

        self.identities = self._load_identities()
        if self._apply_bundled_default_servers():
            self.save_identities()
        self.profiles = self._load_profiles()

    def _load_identities(self) -> Dict[str, Any]:
        """Load identities from file (servers with user accounts)."""
        if self.identities_path.exists():
            try:
                with open(self.identities_path, "r") as f:
                    raw = json.load(f)
                    validated = validate_identities(raw)
                    if validated != raw:
                        self.identities = validated
                        self.save_identities()
                        print("Identities validated and saved.")
                    return validated
            except Exception as e:
                print(f"Error loading identities: {e}")
                return self._get_default_identities()

        return self._get_default_identities()

    def _get_default_identities(self) -> Dict[str, Any]:
        """Get default identities structure."""
        return Identities().model_dump()

    def _resolve_default_servers_path(self) -> Path:
        """Return the bundled default-server export path.

        The environment override is primarily for tests and packaging sanity
        checks. Production builds fall back to the bundled defaults file.
        """
        override = os.environ.get(DEFAULT_SERVERS_ENV)
        if override:
            return Path(override)
        return find_resource_path("defaults/default_servers.json")

    @staticmethod
    def _server_match_key(host: str, port: int) -> tuple[str, int]:
        """Normalize a server endpoint for duplicate detection."""
        return (host.strip().lower().rstrip("/"), int(port))

    def _apply_bundled_default_servers(self) -> bool:
        """Seed shipped server entries into otherwise-empty or older configs."""
        defaults_path = self._resolve_default_servers_path()
        if not defaults_path.exists():
            return False

        try:
            export = ExportedIdentities.model_validate(json.loads(defaults_path.read_text()))
        except Exception as e:
            print(f"Error loading bundled default servers: {e}")
            return False

        existing = {
            self._server_match_key(server.get("host", ""), server.get("port", 8000)): server_id
            for server_id, server in self.identities.get("servers", {}).items()
        }

        changed = False
        selected_server_id = self.identities.get("last_server_id")

        for bundled_server in export.servers:
            key = self._server_match_key(bundled_server.host, bundled_server.port)
            if key in existing:
                continue
            self.identities["servers"][bundled_server.server_id] = bundled_server.model_dump()
            existing[key] = bundled_server.server_id
            if not selected_server_id:
                selected_server_id = bundled_server.server_id
            changed = True

        if selected_server_id and self.identities.get("last_server_id") != selected_server_id:
            self.identities["last_server_id"] = selected_server_id
            changed = True

        return changed

    def _load_profiles(self) -> Dict[str, Any]:
        """Load option profiles from file (shareable, no credentials)."""
        if not self.profiles_path.exists():
            return self._get_default_profiles()

        try:
            with open(self.profiles_path, "r") as f:
                profiles = json.load(f)
                # Migrate old combined config if needed
                return self._migrate_profiles(profiles)
        except Exception as e:
            print(f"Error loading profiles: {e}")
            return self._get_default_profiles()

    def _get_default_profiles(self) -> Dict[str, Any]:
        """Get default profiles structure (shareable)."""
        return {
            "client_options_defaults": {
                "audio": {"music_volume": 20, "ambience_volume": 20},
                "social": {
                    "mute_global_chat": False,
                    "mute_table_chat": False,
                    "include_language_filters_for_table_chat": False,
                    "chat_input_language": "English",
                    "language_subscriptions": {},
                },
                "interface": {
                    "invert_multiline_enter_behavior": False,
                    "play_typing_sounds": True,
                },
                "local_table": {
                    "start_as_visible": "always",
                    # Config keys only; not secrets.
                    "start_with_password": "never",  # nosec B105
                    "default_password_text": "",  # nosec B105
                    "creation_notifications": {},
                },  # Will be populated dynamically
            },
            "server_options": {},  # server_id -> options_overrides dict
        }

    def _migrate_profiles(self, profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate profiles to fix data issues.

        Args:
            profiles: The loaded profiles dictionary

        Returns:
            Migrated profiles dictionary
        """
        needs_save = False

        if self._migrate_server_options(profiles):
            needs_save = True
        if self._ensure_server_options(profiles):
            needs_save = True
        if self._fix_default_language_subscriptions(profiles):
            needs_save = True
        if self._fix_server_language_subscriptions(profiles):
            needs_save = True
        if self._migrate_default_table_creations(profiles):
            needs_save = True
        if self._migrate_server_table_creations(profiles):
            needs_save = True

        # Save immediately if migration occurred
        if needs_save:
            self.profiles = profiles
            self.save_profiles()
            print("Profile migration completed and saved to disk.")

        return profiles

    def _migrate_server_options(self, profiles: Dict[str, Any]) -> bool:
        if "servers" not in profiles or "server_options" in profiles:
            return False
        profiles["server_options"] = {}
        for server_id, server_info in profiles["servers"].items():
            if "options_overrides" in server_info and server_info["options_overrides"]:
                profiles["server_options"][server_id] = server_info["options_overrides"]
        del profiles["servers"]
        print("Migrated 'servers' to 'server_options' in profiles")
        return True

    def _ensure_server_options(self, profiles: Dict[str, Any]) -> bool:
        if "server_options" in profiles:
            return False
        profiles["server_options"] = {}
        return True

    def _fix_default_language_subscriptions(self, profiles: Dict[str, Any]) -> bool:
        defaults = profiles.get("client_options_defaults")
        if not isinstance(defaults, dict):
            return False
        social = defaults.get("social")
        if not isinstance(social, dict):
            return False
        changed = False
        changed |= self._fix_language_subs_in_profile(social, "default profile", prefix="default")
        return changed

    def _fix_server_language_subscriptions(self, profiles: Dict[str, Any]) -> bool:
        changed = False
        for server_id, overrides in profiles.get("server_options", {}).items():
            if not isinstance(overrides, dict):
                continue
            social = overrides.get("social")
            if not isinstance(social, dict):
                continue
            if self._fix_language_subs_in_profile(social, f"server {server_id}"):
                changed = True
        return changed

    def _fix_language_subs_in_profile(
        self, social: Dict[str, Any], label: str, prefix: str | None = None
    ) -> bool:
        changed = False
        lang_subs = social.get("language_subscriptions")
        if isinstance(lang_subs, dict) and "Check" in lang_subs:
            lang_subs["Czech"] = lang_subs.pop("Check")
            changed = True
            print(f"Migrated language subscription: 'Check' -> 'Czech' in {label}")
        chat_lang = social.get("chat_input_language")
        if chat_lang == "Check":
            social["chat_input_language"] = "Czech"
            changed = True
            print(f"Migrated chat_input_language: 'Check' -> 'Czech' in {label}")
        return changed

    def _migrate_default_table_creations(self, profiles: Dict[str, Any]) -> bool:
        defaults = profiles.get("client_options_defaults")
        if not isinstance(defaults, dict) or "table_creations" not in defaults:
            return False
        table_creations_value = defaults.pop("table_creations")
        defaults["local_table"] = self._build_local_table_migration(
            defaults.get("local_table", {}),
            table_creations_value,
        )
        print(
            "Migrated 'table_creations' -> 'local_table/creation_notifications' in default profile"
        )
        return True

    def _migrate_server_table_creations(self, profiles: Dict[str, Any]) -> bool:
        changed = False
        for server_id, overrides in profiles.get("server_options", {}).items():
            if not isinstance(overrides, dict) or "table_creations" not in overrides:
                continue
            table_creations_value = overrides.pop("table_creations")
            overrides["local_table"] = self._build_local_table_migration(
                overrides.get("local_table", {}),
                table_creations_value,
            )
            print(
                f"Migrated 'table_creations' -> 'local_table/creation_notifications' in server {server_id}"
            )
            changed = True
        return changed

    @staticmethod
    def _build_local_table_migration(
        local_table: Dict[str, Any], table_creations_value: Dict[str, Any]
    ) -> Dict[str, Any]:
        new_local_table = {
            "start_as_visible": local_table.get("start_as_visible", "always"),
            "start_with_password": local_table.get("start_with_password", "never"),
            "default_password_text": local_table.get("default_password_text", ""),
            "creation_notifications": table_creations_value,
        }
        for key, value in local_table.items():
            if key not in new_local_table:
                new_local_table[key] = value
        return new_local_table

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any], override_wins: bool = True
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries with configurable precedence.

        Supports infinite nesting depth.

        Args:
            base: Base dictionary
            override: Dictionary to merge into base
            override_wins: If True, override values take precedence on conflicts.
                           If False, base values take precedence (override fills missing keys only).

        Returns:
            Merged dictionary
        """
        result = self._deep_copy(base)

        for key, value in override.items():
            if key not in result:
                result[key] = self._deep_copy(value)
            elif isinstance(value, dict) and isinstance(result[key], dict):
                result[key] = self._deep_merge(result[key], value, override_wins)
            elif override_wins:
                result[key] = self._deep_copy(value)
            # else: base wins, keep existing value

        return result

    def save_identities(self):
        """Save identities to file."""
        try:
            # Create directory if it doesn't exist
            self.base_path.mkdir(parents=True, exist_ok=True)

            with open(self.identities_path, "w") as f:
                json.dump(self.identities, f, indent=2)
        except Exception as e:
            print(f"Error saving identities: {e}")

    def save_profiles(self):
        """Save option profiles to file."""
        try:
            # Create config directory if it doesn't exist
            self.base_path.mkdir(parents=True, exist_ok=True)

            with open(self.profiles_path, "w") as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            print(f"Error saving profiles: {e}")

    def save(self):
        """Save both identities and profiles."""
        self.save_identities()
        self.save_profiles()

    # ========== Server Management ==========

    def get_last_server_id(self) -> Optional[str]:
        """Get ID of last connected server."""
        return self.identities.get("last_server_id")

    def get_last_account_id(self, server_id: str) -> Optional[str]:
        """Get ID of last used account for a server.

        Args:
            server_id: Server ID

        Returns:
            Account ID or None if not set
        """
        server = self.get_server_by_id(server_id)
        if server:
            return server.get("last_account_id")
        return None

    def get_server_by_id(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get server info by ID.

        Args:
            server_id: Unique server ID

        Returns:
            Server info dict or None if not found
        """
        return self.identities["servers"].get(server_id)

    def get_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get all servers.

        Returns:
            Dict mapping server_id to server info
        """
        return self.identities["servers"]

    def add_server(
        self,
        name: str,
        host: str,
        port: int,
        notes: str = "",
    ) -> str:
        """Add a new server.

        Args:
            name: Server display name
            host: Server host address
            port: Server port
            notes: Optional notes about the server

        Returns:
            New server ID
        """
        server = Server(name=name, host=host, port=port, notes=notes)
        server_id = server.server_id
        self.identities["servers"][server_id] = server.model_dump()
        self.save_identities()
        return server_id

    def update_server(
        self,
        server_id: str,
        name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        notes: Optional[str] = None,
    ):
        """Update server information.

        Args:
            server_id: Server ID
            name: New server name (if provided)
            host: New host address (if provided)
            port: New port (if provided)
            notes: New notes (if provided)
        """
        if server_id not in self.identities["servers"]:
            return

        server = self.identities["servers"][server_id]
        if name is not None:
            server["name"] = name
        if host is not None:
            server["host"] = host
        if port is not None:
            server["port"] = port
        if notes is not None:
            server["notes"] = notes
        self.save_identities()

    def delete_server(self, server_id: str):
        """Delete a server and all its accounts.

        Args:
            server_id: Server ID to delete
        """
        if server_id in self.identities["servers"]:
            del self.identities["servers"][server_id]
            # Clear last_server_id if it was this server
            if self.identities.get("last_server_id") == server_id:
                self.identities["last_server_id"] = None
            self.save_identities()

    def get_server_display_name(self, server_id: str) -> str:
        """Get display name for a server.

        Args:
            server_id: Server ID

        Returns:
            Display name
        """
        server = self.get_server_by_id(server_id)
        if server:
            return server.get("name", "Unknown Server")
        return "Unknown Server"

    def get_server_url(self, server_id: str) -> Optional[str]:
        """Build WebSocket URL for a server.

        Args:
            server_id: Server ID

        Returns:
            WebSocket URL or None if server not found
        """
        server = self.get_server_by_id(server_id)
        if not server:
            return None

        host = server.get("host", "")
        port = server.get("port", 8000)

        # Check if host already has a scheme
        if "://" in host:
            scheme = host.split("://")[0].lower()
            host_part = host.split("://", 1)[1]
            return f"{scheme}://{host_part}:{port}"
        else:
            return f"ws://{host}:{port}"

    def set_last_server(self, server_id: str):
        """Set the last connected server.

        Args:
            server_id: Server ID
        """
        self.identities["last_server_id"] = server_id
        self.save_identities()

    # ========== Certificate Trust Management ==========

    def get_trusted_certificate(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Return trusted certificate metadata for a server."""
        server = self.get_server_by_id(server_id)
        if server:
            return server.get("trusted_certificate")
        return None

    def set_trusted_certificate(self, server_id: str, cert_info: Dict[str, Any]) -> None:
        """Store trusted certificate metadata for a server."""
        server = self.get_server_by_id(server_id)
        if not server:
            return
        server["trusted_certificate"] = cert_info
        self.save_identities()

    def clear_trusted_certificate(self, server_id: str) -> None:
        """Remove stored certificate metadata for a server."""
        server = self.get_server_by_id(server_id)
        if not server:
            return
        if "trusted_certificate" in server:
            server["trusted_certificate"] = None
            self.save_identities()

    # ========== Account Management ==========

    def get_server_accounts(self, server_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all accounts for a server.

        Args:
            server_id: Server ID

        Returns:
            Dict mapping account_id to account info
        """
        server = self.get_server_by_id(server_id)
        if server:
            return server.get("accounts", {})
        return {}

    def get_account_by_id(self, server_id: str, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account info by ID.

        Args:
            server_id: Server ID
            account_id: Account ID

        Returns:
            Account info dict or None if not found
        """
        server = self.get_server_by_id(server_id)
        if server:
            return server.get("accounts", {}).get(account_id)
        return None

    def add_account(
        self,
        server_id: str,
        username: str,
        # User-supplied password, not a default.
        password: str,  # nosec B107
        email: str = "",
        notes: str = "",
        refresh_token: str = "",
        refresh_expires_at: Optional[int] = None,
    ) -> Optional[str]:
        """Add a new account to a server.

        Args:
            server_id: Server ID
            username: Account username
            password: Account password
            email: Optional email address
            notes: Optional notes about the account

        Returns:
            New account ID, or None if server not found
        """
        if server_id not in self.identities["servers"]:
            return None

        account = UserAccount(
            username=username,
            password=password,
            refresh_token=refresh_token,
            refresh_expires_at=refresh_expires_at,
            email=email,
            notes=notes,
        )
        account_id = account.account_id
        if "accounts" not in self.identities["servers"][server_id]:
            self.identities["servers"][server_id]["accounts"] = {}

        self.identities["servers"][server_id]["accounts"][account_id] = account.model_dump()
        self.save_identities()
        return account_id

    def update_account(
        self,
        server_id: str,
        account_id: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        refresh_token: Optional[str] = None,
        refresh_expires_at: Optional[int] = None,
        email: Optional[str] = None,
        notes: Optional[str] = None,
    ):
        """Update account information.

        Args:
            server_id: Server ID
            account_id: Account ID
            username: New username (if provided)
            password: New password (if provided)
            email: New email address (if provided)
            notes: New notes (if provided)
        """
        account = self.get_account_by_id(server_id, account_id)
        if not account:
            return

        if username is not None:
            account["username"] = username
        if password is not None:
            account["password"] = password
        if refresh_token is not None:
            account["refresh_token"] = refresh_token
        if refresh_expires_at is not None:
            account["refresh_expires_at"] = refresh_expires_at
        if email is not None:
            account["email"] = email
        if notes is not None:
            account["notes"] = notes
        self.save_identities()

    def delete_account(self, server_id: str, account_id: str):
        """Delete an account from a server.

        Args:
            server_id: Server ID
            account_id: Account ID to delete
        """
        server = self.get_server_by_id(server_id)
        if server and account_id in server.get("accounts", {}):
            del server["accounts"][account_id]
            # Clear last_account_id if it was this account
            if server.get("last_account_id") == account_id:
                server["last_account_id"] = None
            self.save_identities()

    def set_last_account(self, server_id: str, account_id: str):
        """Set the last used account for a server.

        Args:
            server_id: Server ID
            account_id: Account ID
        """
        self.identities["last_server_id"] = server_id
        server = self.get_server_by_id(server_id)
        if server:
            server["last_account_id"] = account_id
        self.save_identities()

    def get_client_options(self, server_id: Optional[str] = None) -> Dict[str, Any]:
        """Get client options for a server (defaults + overrides).

        Args:
            server_id: Server ID, or None for just defaults

        Returns:
            Complete options dict with overrides applied
        """
        # Start with defaults
        options = self._deep_copy(self.profiles["client_options_defaults"])

        # Apply server-specific overrides if provided
        if server_id and server_id in self.profiles.get("server_options", {}):
            overrides = self.profiles["server_options"][server_id]
            options = self._deep_merge(options, overrides)

        return options

    def set_client_option(
        self,
        key_path: str,
        value: Any,
        server_id: Optional[str] = None,
        *,
        create_mode: bool = False,
    ):
        """Set a client option (either default or server-specific override).

        Args:
            key_path: Path to the option (e.g., "audio/music_volume", "social/language_subscriptions/English")
            value: Option value
            server_id: Server ID for override, or None for default
            create_mode: If True, create intermediate dictionaries as needed
        """
        if server_id is None:
            # Set default
            target = self.profiles["client_options_defaults"]
        else:
            # Set server override
            if "server_options" not in self.profiles:
                self.profiles["server_options"] = {}
            target = self.profiles["server_options"].setdefault(server_id, {})

        success = set_item_in_dict(target, key_path, value, create_mode=create_mode)
        if success:
            self.save_profiles()

    def clear_server_override(
        self, server_id: str, key_path: str, *, delete_empty_layers: bool = True
    ):
        """Clear a server-specific override (revert to default).

        Args:
            server_id: Server ID
            key_path: Path to the option (e.g., "audio/music_volume")
            delete_empty_layers: If True, delete intermediate dictionaries if empty
        """
        if server_id not in self.profiles.get("server_options", {}):
            return

        overrides = self.profiles["server_options"][server_id]

        success = delete_item_from_dict(
            overrides, key_path, delete_empty_layers=delete_empty_layers
        )
        if success:
            self.save_profiles()

    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy a nested dict/list structure."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
