import json
from pathlib import Path

import pytest

from config_manager import (
    ConfigManager,
    delete_item_from_dict,
    get_item_from_dict,
    set_item_in_dict,
)
from config_schemas import OptionsProfile


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def make_manager(tmp_path):
    return ConfigManager(base_path=tmp_path / "pp")


def test_get_item_from_dict_create_mode_builds_layers():
    data = {}
    result = get_item_from_dict(data, "servers/foo/bar", create_mode=True)
    assert result == {}
    assert "servers" in data and "foo" in data["servers"]


def test_set_item_in_dict_strict_mode_requires_existing_keys():
    data = {"section": {}}
    with pytest.raises(KeyError):
        set_item_in_dict(data, "section/missing/value", 1, create_mode=False)

    set_item_in_dict(data, "section/value", 2, create_mode=True)
    assert data["section"]["value"] == 2


def test_delete_item_from_dict_cleans_empty_layers():
    data = {"section": {"nested": {"leaf": 1, "keep": 2}}}
    assert delete_item_from_dict(data, "section/nested/leaf")
    assert "leaf" not in data["section"]["nested"]
    # Remove final value should collapse nested dict
    assert delete_item_from_dict(data, "section/nested/keep")
    assert "section" not in data


def test_identities_migration_adds_email_field(tmp_path):
    identities = {
        "last_server_id": None,
        "servers": {
            "server-1": {
                "accounts": {
                    "acct-1": {"username": "demo"},
                }
            }
        },
    }
    base = tmp_path / "pp"
    write_json(base / "identities.json", identities)
    cm = ConfigManager(base_path=base)

    account = cm.identities["servers"]["server-1"]["accounts"]["acct-1"]
    assert account["email"] == ""
    persisted = json.loads((base / "identities.json").read_text())
    assert persisted["servers"]["server-1"]["accounts"]["acct-1"]["email"] == ""


def test_invalid_identities_file_returns_defaults(tmp_path):
    base = tmp_path / "pp"
    (base / "identities.json").parent.mkdir(parents=True, exist_ok=True)
    (base / "identities.json").write_text("{not-json")

    cm = ConfigManager(base_path=base)
    assert cm.identities == cm._get_default_identities()


def test_profile_migration_moves_servers_and_languages(tmp_path):
    profiles = {
        "client_options_defaults": {
            "social": {
                "chat_input_language": "Check",
                "language_subscriptions": {"Check": True},
            },
            "table_creations": {"general": True},
        },
        "servers": {
            "srv-1": {
                "options_overrides": {
                    "social": {
                        "chat_input_language": "Check",
                        "language_subscriptions": {"Check": True},
                    },
                    "table_creations": {"vip": True},
                }
            }
        },
    }
    base = tmp_path / "pp"
    write_json(base / "identities.json", ConfigManager(base)._get_default_identities())
    write_json(base / "option_profiles.json", profiles)

    cm = ConfigManager(base_path=base)
    defaults = cm.profiles["client_options_defaults"]
    assert defaults["social"]["chat_input_language"] == "Czech"
    assert "creation_notifications" in defaults["local_table"]
    assert defaults["local_table"]["creation_notifications"] == {"general": True}

    overrides = cm.profiles["server_options"]["srv-1"]
    assert overrides["social"]["chat_input_language"] == "Czech"
    assert overrides["social"]["language_subscriptions"] == {"Czech": True}
    assert overrides["local_table"]["creation_notifications"] == {"vip": True}
    assert "servers" not in cm.profiles


def test_deep_merge_override_behavior(tmp_path):
    cm = make_manager(tmp_path)
    base = {"audio": {"volume": 10, "muted": False}, "theme": "light"}
    override = {"audio": {"volume": 20}, "new": 1}

    merged = cm._deep_merge(base, override, override_wins=True)
    assert merged["audio"]["volume"] == 20
    assert merged["audio"]["muted"] is False
    assert merged["new"] == 1

    merged_base_wins = cm._deep_merge(base, {"audio": {"muted": True}}, override_wins=False)
    assert merged_base_wins["audio"]["muted"] is False


def test_add_update_delete_server(tmp_path):
    cm = make_manager(tmp_path)
    server_id = cm.add_server("Local", "localhost", 9000, "notes")
    assert server_id in cm.get_all_servers()

    cm.update_server(server_id, name="Prod", port=8000)
    server = cm.get_server_by_id(server_id)
    assert server["name"] == "Prod"
    assert server["port"] == 8000

    assert cm.get_server_display_name(server_id) == "Prod"
    assert cm.get_server_url(server_id) == "ws://localhost:8000"

    cm.delete_server(server_id)
    assert server_id not in cm.get_all_servers()


def test_get_server_url_respects_existing_scheme(tmp_path):
    cm = make_manager(tmp_path)
    server_id = cm.add_server("Secure", "wss://example.com", 9001)
    assert cm.get_server_url(server_id) == "wss://example.com:9001"


def test_bundled_default_server_is_seeded(tmp_path, monkeypatch):
    defaults = tmp_path / "default_servers.json"
    defaults.write_text(
        json.dumps(
            {
                "description": "Bundled server",
                "timestamp": 1,
                "servers": [
                    {
                        "server_id": "public-palace",
                        "name": "Public Palace",
                        "host": "wss://palace.serrebiradio.com",
                        "port": 443,
                        "notes": "Public server",
                        "accounts": {},
                    }
                ],
            }
        )
    )
    monkeypatch.setenv("PLAYPALACE_DEFAULT_SERVERS_FILE", str(defaults))

    cm = ConfigManager(base_path=tmp_path / "pp")
    servers = cm.get_all_servers()

    assert list(servers) == ["public-palace"]
    assert servers["public-palace"]["host"] == "wss://palace.serrebiradio.com"
    assert servers["public-palace"]["port"] == 443
    assert cm.get_last_server_id() == "public-palace"


def test_bundled_default_server_does_not_duplicate_existing(tmp_path, monkeypatch):
    defaults = tmp_path / "default_servers.json"
    defaults.write_text(
        json.dumps(
            {
                "description": "Bundled server",
                "timestamp": 1,
                "servers": [
                    {
                        "server_id": "public-palace",
                        "name": "Public Palace",
                        "host": "wss://palace.serrebiradio.com",
                        "port": 443,
                        "accounts": {},
                    }
                ],
            }
        )
    )
    monkeypatch.setenv("PLAYPALACE_DEFAULT_SERVERS_FILE", str(defaults))

    base = tmp_path / "pp"
    write_json(
        base / "identities.json",
        {
            "last_server_id": "existing",
            "servers": {
                "existing": {
                    "server_id": "existing",
                    "name": "Existing",
                    "host": "wss://palace.serrebiradio.com",
                    "port": 443,
                    "accounts": {},
                }
            },
        },
    )

    cm = ConfigManager(base_path=base)
    assert list(cm.get_all_servers()) == ["existing"]
    assert cm.get_last_server_id() == "existing"


def test_last_server_and_accounts(tmp_path):
    cm = make_manager(tmp_path)
    server_id = cm.add_server("Local", "localhost", 8000)
    account_id = cm.add_account(server_id, "alice", "pwd", email="a@example.com")
    assert cm.get_server_accounts(server_id)
    cm.update_account(server_id, account_id, password="secret", notes="admin")
    acct = cm.get_account_by_id(server_id, account_id)
    assert acct["password"] == "secret"
    assert acct["notes"] == "admin"

    cm.set_last_server(server_id)
    cm.set_last_account(server_id, account_id)
    assert cm.get_last_server_id() == server_id
    assert cm.get_last_account_id(server_id) == account_id

    cm.delete_account(server_id, account_id)
    assert cm.get_last_account_id(server_id) is None


def test_trusted_certificate_round_trip(tmp_path):
    cm = make_manager(tmp_path)
    server_id = cm.add_server("Secure", "example", 8000)
    assert cm.get_trusted_certificate(server_id) is None

    cert_info = {"fingerprint": "aa:bb", "issued_to": "example"}
    cm.set_trusted_certificate(server_id, cert_info)
    assert cm.get_trusted_certificate(server_id) == cert_info

    cm.clear_trusted_certificate(server_id)
    assert cm.get_trusted_certificate(server_id) is None

    # Unknown server should be a no-op
    cm.set_trusted_certificate("missing", cert_info)  # Should not raise


def test_client_options_with_overrides(tmp_path):
    cm = make_manager(tmp_path)
    server_id = cm.add_server("Local", "localhost", 8000)

    cm.set_client_option("audio/music_volume", 25)
    cm.set_client_option("audio/music_volume", 60, server_id, create_mode=True)
    defaults = cm.get_client_options()
    overrides = cm.get_client_options(server_id)

    assert defaults["audio"]["music_volume"] == 25
    assert overrides["audio"]["music_volume"] == 60

    cm.clear_server_override(server_id, "audio/music_volume")
    assert cm.get_client_options(server_id)["audio"]["music_volume"] == 25


def test_set_client_option_creates_layers(tmp_path):
    cm = make_manager(tmp_path)
    cm.set_client_option("social/language_subscriptions/Spanish", True, create_mode=True)
    defaults = cm.get_client_options()
    assert defaults["social"]["language_subscriptions"]["Spanish"] is True


def test_clear_server_override_prunes_empty_dict(tmp_path):
    cm = make_manager(tmp_path)
    server_id = cm.add_server("Local", "localhost", 8000)
    cm.set_client_option("interface/play_typing_sounds", False, server_id, create_mode=True)
    cm.clear_server_override(server_id, "interface/play_typing_sounds", delete_empty_layers=True)
    assert cm.profiles["server_options"][server_id] == {}


def test_profiles_migration_converts_legacy_servers(tmp_path):
    base = tmp_path / "pp"
    helper = ConfigManager(base_path=base)
    legacy_profiles = helper._get_default_profiles()
    legacy_profiles["client_options_defaults"]["table_creations"] = {"general": True}
    legacy_profiles["servers"] = {
        "srv-legacy": {
            "options_overrides": {
                "social": {
                    "chat_input_language": "Check",
                    "language_subscriptions": {"Check": True},
                },
                "table_creations": {"vip": True},
            }
        }
    }
    legacy_profiles.pop("server_options", None)
    profiles_path = base / "option_profiles.json"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_path.write_text(json.dumps(legacy_profiles))

    migrated = ConfigManager(base_path=base)
    assert "servers" not in migrated.profiles
    overrides = migrated.profiles["server_options"]["srv-legacy"]
    assert overrides["social"]["chat_input_language"] == "Czech"
    assert overrides["social"]["language_subscriptions"] == {"Czech": True}
    assert overrides["local_table"]["creation_notifications"] == {"vip": True}
    defaults = migrated.profiles["client_options_defaults"]
    assert defaults["local_table"]["creation_notifications"] == {"general": True}


def test_invalid_profiles_file_returns_defaults(tmp_path):
    base = tmp_path / "pp"
    helper = ConfigManager(base_path=base)
    defaults = helper._get_default_profiles()
    profiles_path = base / "option_profiles.json"
    profiles_path.parent.mkdir(parents=True, exist_ok=True)
    profiles_path.write_text("{not-json")

    cm = ConfigManager(base_path=base)
    assert cm.profiles == defaults


# ========== Schema Validation Tests ==========


def test_schema_fills_missing_fields(tmp_path):
    """Loading identities with missing fields should fill them with defaults."""
    identities = {
        "last_server_id": None,
        "servers": {
            "srv-1": {
                "server_id": "srv-1",
                "name": "Test",
                "host": "localhost",
                "port": 9000,
                "accounts": {
                    "acct-1": {
                        "account_id": "acct-1",
                        "username": "demo",
                        "password": "pass",
                    }
                },
            }
        },
    }
    base = tmp_path / "pp"
    write_json(base / "identities.json", identities)
    cm = ConfigManager(base_path=base)

    server = cm.identities["servers"]["srv-1"]
    # Missing fields should be filled with defaults
    assert server["notes"] == ""
    assert server["last_account_id"] is None
    assert server["options_profile"] == OptionsProfile().model_dump()
    assert server["trusted_certificate"] is None
    assert "default_options_profile" in cm.identities

    account = server["accounts"]["acct-1"]
    assert account["email"] == ""
    assert account["notes"] == ""


def test_schema_strips_unknown_fields(tmp_path):
    """Loading identities with unknown fields should strip them."""
    identities = {
        "last_server_id": None,
        "default_options_profile": {},
        "unknown_root_field": "should be stripped",
        "servers": {
            "srv-1": {
                "server_id": "srv-1",
                "name": "Test",
                "host": "localhost",
                "port": 8000,
                "unknown_server_field": True,
                "accounts": {
                    "acct-1": {
                        "account_id": "acct-1",
                        "username": "demo",
                        "password": "pass",
                        "unknown_account_field": 42,
                    }
                },
            }
        },
    }
    base = tmp_path / "pp"
    write_json(base / "identities.json", identities)
    cm = ConfigManager(base_path=base)

    assert "unknown_root_field" not in cm.identities
    server = cm.identities["servers"]["srv-1"]
    assert "unknown_server_field" not in server
    account = server["accounts"]["acct-1"]
    assert "unknown_account_field" not in account


def test_schema_coerces_string_port(tmp_path):
    """Loading identities with port as string should coerce to int."""
    identities = {
        "last_server_id": None,
        "servers": {
            "srv-1": {
                "server_id": "srv-1",
                "name": "Test",
                "host": "localhost",
                "port": "9000",
                "accounts": {},
            }
        },
    }
    base = tmp_path / "pp"
    write_json(base / "identities.json", identities)
    cm = ConfigManager(base_path=base)

    server = cm.identities["servers"]["srv-1"]
    assert server["port"] == 9000
    assert isinstance(server["port"], int)


def test_new_server_has_all_fields(tmp_path):
    """Creating a new server should include all fields from the schema."""
    cm = make_manager(tmp_path)
    server_id = cm.add_server("Test", "localhost", 8000)
    server = cm.get_server_by_id(server_id)

    assert server["server_id"] == server_id
    assert server["name"] == "Test"
    assert server["host"] == "localhost"
    assert server["port"] == 8000
    assert server["notes"] == ""
    assert server["accounts"] == {}
    assert server["last_account_id"] is None
    assert server["options_profile"] == OptionsProfile().model_dump()
    assert server["trusted_certificate"] is None


def test_new_account_has_auto_generated_id(tmp_path):
    """Creating a new account should auto-generate an account_id."""
    cm = make_manager(tmp_path)
    server_id = cm.add_server("Test", "localhost", 8000)
    account_id = cm.add_account(server_id, "alice", "pwd")
    account = cm.get_account_by_id(server_id, account_id)

    assert account["account_id"] == account_id
    assert len(account_id) == 36  # UUID format
    assert account["username"] == "alice"
    assert account["password"] == "pwd"
    assert account["email"] == ""
    assert account["notes"] == ""
