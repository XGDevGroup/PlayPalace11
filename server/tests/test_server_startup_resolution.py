"""Tests for run_server resolution of host, port, and SSL from config vs CLI args."""

import asyncio
import logging

import pytest

import server.core.server as core_server


class _DummyDB:
    def __init__(self, path: str) -> None:
        self.path = path

    def connect(self) -> None:
        return None

    def get_user_count(self) -> int:
        return 1

    def get_server_owner(self) -> str:
        return "owner"

    def close(self) -> None:
        return None


@pytest.fixture()
def server_env(tmp_path, monkeypatch):
    """Wire run_server to use tmp_path for config and db, return (config_path, write_config).

    write_config(toml_text) writes config.toml and sets up the empty db file.
    captured["host"], captured["port"], captured["ssl_cert"], captured["ssl_key"]
    are populated by DummyServer after each run_server call.
    """
    var_dir = tmp_path / "var"
    var_dir.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "config.toml"
    example_path = tmp_path / "config.example.toml"
    example_path.write_text("", encoding="utf-8")
    (var_dir / "playpalace.db").write_text("", encoding="utf-8")

    monkeypatch.setattr(core_server, "get_default_config_path", lambda: config_path)
    monkeypatch.setattr(core_server, "get_example_config_path", lambda: example_path)
    monkeypatch.setattr(core_server, "ensure_default_config_dir", lambda: tmp_path)
    if hasattr(core_server, "_ensure_var_server_dir"):
        monkeypatch.setattr(core_server, "_ensure_var_server_dir", lambda: var_dir)
    else:
        monkeypatch.setattr(core_server, "_MODULE_DIR", tmp_path)

    captured = {}

    class DummyServer:
        def __init__(self, *args, **kwargs):
            captured.update(
                host=kwargs.get("host"),
                port=kwargs.get("port"),
                ssl_cert=kwargs.get("ssl_cert"),
                ssl_key=kwargs.get("ssl_key"),
            )

        async def start(self):
            return None

        async def stop(self):
            return None

    async def fake_sleep(_):
        raise KeyboardInterrupt

    monkeypatch.setattr(core_server, "Database", _DummyDB)
    monkeypatch.setattr(core_server, "Server", DummyServer)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(core_server, "_ensure_server_owner", lambda *args, **kwargs: None)

    def write_config(toml_text: str) -> None:
        config_path.write_text(toml_text, encoding="utf-8")

    return write_config, captured


# ---------------------------------------------------------------------------
# Host resolution
# ---------------------------------------------------------------------------

async def test_run_server_uses_bind_ip_from_config(server_env):
    write_config, captured = server_env
    write_config('[server]\nbind_ip = "0.0.0.0"\n')
    await core_server.run_server(host=None)
    assert captured["host"] == "0.0.0.0"


async def test_run_server_defaults_bind_ip_to_localhost(server_env):
    write_config, captured = server_env
    write_config("[server]\n")
    await core_server.run_server(host=None)
    assert captured["host"] == "127.0.0.1"


async def test_run_server_host_param_overrides_config(server_env):
    write_config, captured = server_env
    write_config('[server]\nbind_ip = "127.0.0.1"\n')
    await core_server.run_server(host="0.0.0.0")
    assert captured["host"] == "0.0.0.0"


# ---------------------------------------------------------------------------
# Port resolution
# ---------------------------------------------------------------------------

async def test_run_server_uses_port_from_config(server_env):
    write_config, captured = server_env
    write_config("[server]\nport = 9000\n")
    await core_server.run_server(port=None)
    assert captured["port"] == 9000


async def test_run_server_defaults_port_to_8000(server_env):
    write_config, captured = server_env
    write_config("[server]\n")
    await core_server.run_server(port=None)
    assert captured["port"] == 8000


async def test_run_server_port_param_overrides_config(server_env):
    write_config, captured = server_env
    write_config("[server]\nport = 9000\n")
    await core_server.run_server(port=7777)
    assert captured["port"] == 7777


@pytest.mark.parametrize("bad_port", [-1, 0, 70000, "not_a_port"])
async def test_run_server_invalid_port_in_config_falls_back(server_env, caplog, bad_port):
    write_config, captured = server_env
    if isinstance(bad_port, str):
        write_config(f'[server]\nport = "{bad_port}"\n')
    else:
        write_config(f"[server]\nport = {bad_port}\n")
    with caplog.at_level(logging.WARNING, logger="playpalace.server"):
        await core_server.run_server(port=None)
    assert captured["port"] == 8000


# ---------------------------------------------------------------------------
# SSL resolution
# ---------------------------------------------------------------------------

async def test_run_server_uses_ssl_from_config(server_env):
    write_config, captured = server_env
    write_config(
        '[network]\nssl_cert = "/etc/cert.pem"\nssl_key = "/etc/key.pem"\n'
        "allow_insecure_ws = false\n"
    )
    await core_server.run_server(ssl_cert=None, ssl_key=None)
    assert captured["ssl_cert"] == "/etc/cert.pem"
    assert captured["ssl_key"] == "/etc/key.pem"


async def test_run_server_ssl_cli_overrides_config(server_env):
    write_config, captured = server_env
    write_config(
        '[network]\nssl_cert = "/etc/cert.pem"\nssl_key = "/etc/key.pem"\n'
        "allow_insecure_ws = false\n"
    )
    await core_server.run_server(ssl_cert="/other/cert.pem", ssl_key="/other/key.pem")
    assert captured["ssl_cert"] == "/other/cert.pem"
    assert captured["ssl_key"] == "/other/key.pem"


async def test_run_server_partial_ssl_config_logs_warning(server_env, caplog):
    write_config, captured = server_env
    write_config('[network]\nssl_cert = "/etc/cert.pem"\nallow_insecure_ws = true\n')
    with caplog.at_level(logging.WARNING, logger="playpalace.server"):
        await core_server.run_server(ssl_cert=None, ssl_key=None)
    assert captured["ssl_cert"] is None
    assert captured["ssl_key"] is None
    assert any("ssl_cert" in r.message and "ssl_key" in r.message for r in caplog.records)
