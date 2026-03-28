import asyncio

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


def _patch_run_server_environment(tmp_path, monkeypatch):
    """Point run_server at the temporary config/db paths."""
    var_dir = tmp_path / "var"
    var_dir.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "config.toml"
    example_path = tmp_path / "config.example.toml"

    monkeypatch.setattr(core_server, "get_default_config_path", lambda: config_path)
    monkeypatch.setattr(core_server, "get_example_config_path", lambda: example_path)
    monkeypatch.setattr(core_server, "ensure_default_config_dir", lambda: tmp_path)
    if hasattr(core_server, "_ensure_var_server_dir"):
        monkeypatch.setattr(core_server, "_ensure_var_server_dir", lambda: var_dir)
    else:
        monkeypatch.setattr(core_server, "_MODULE_DIR", tmp_path)

    return config_path, example_path, var_dir


@pytest.mark.asyncio
async def test_run_server_uses_bind_ip_from_config(tmp_path, monkeypatch):
    config_path, example_path, var_dir = _patch_run_server_environment(tmp_path, monkeypatch)
    config_path.write_text('[server]\nbind_ip = "0.0.0.0"\n', encoding="utf-8")

    example_path.write_text("", encoding="utf-8")
    (var_dir / "playpalace.db").write_text("", encoding="utf-8")

    captured = {}

    class DummyServer:
        def __init__(self, *args, **kwargs):
            captured["host"] = kwargs.get("host")

        async def start(self) -> None:
            return None

        async def stop(self) -> None:
            return None

    async def fake_sleep(_):
        raise KeyboardInterrupt

    monkeypatch.setattr(core_server, "Database", _DummyDB)
    monkeypatch.setattr(core_server, "Server", DummyServer)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(core_server, "_ensure_server_owner", lambda *args, **kwargs: None)

    await core_server.run_server(host=None)

    assert captured["host"] == "0.0.0.0"


@pytest.mark.asyncio
async def test_run_server_defaults_bind_ip_to_localhost(tmp_path, monkeypatch):
    config_path, example_path, var_dir = _patch_run_server_environment(tmp_path, monkeypatch)
    config_path.write_text("[server]\n", encoding="utf-8")

    example_path.write_text("", encoding="utf-8")
    (var_dir / "playpalace.db").write_text("", encoding="utf-8")

    captured = {}

    class DummyServer:
        def __init__(self, *args, **kwargs):
            captured["host"] = kwargs.get("host")

        async def start(self) -> None:
            return None

        async def stop(self) -> None:
            return None

    async def fake_sleep(_):
        raise KeyboardInterrupt

    monkeypatch.setattr(core_server, "Database", _DummyDB)
    monkeypatch.setattr(core_server, "Server", DummyServer)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(core_server, "_ensure_server_owner", lambda *args, **kwargs: None)

    await core_server.run_server(host=None)

    assert captured["host"] == "127.0.0.1"


@pytest.mark.asyncio
async def test_run_server_host_param_overrides_config(tmp_path, monkeypatch):
    config_path, example_path, var_dir = _patch_run_server_environment(tmp_path, monkeypatch)
    config_path.write_text('[server]\nbind_ip = "127.0.0.1"\n', encoding="utf-8")

    example_path.write_text("", encoding="utf-8")
    (var_dir / "playpalace.db").write_text("", encoding="utf-8")

    captured = {}

    class DummyServer:
        def __init__(self, *args, **kwargs):
            captured["host"] = kwargs.get("host")

        async def start(self) -> None:
            return None

        async def stop(self) -> None:
            return None

    async def fake_sleep(_):
        raise KeyboardInterrupt

    monkeypatch.setattr(core_server, "Database", _DummyDB)
    monkeypatch.setattr(core_server, "Server", DummyServer)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(core_server, "_ensure_server_owner", lambda *args, **kwargs: None)

    await core_server.run_server(host="0.0.0.0")

    assert captured["host"] == "0.0.0.0"


# ---------------------------------------------------------------------------
# Port resolution tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_server_uses_port_from_config(tmp_path, monkeypatch):
    config_path, example_path, var_dir = _patch_run_server_environment(tmp_path, monkeypatch)
    config_path.write_text('[server]\nport = 9000\n', encoding="utf-8")
    example_path.write_text("", encoding="utf-8")
    (var_dir / "playpalace.db").write_text("", encoding="utf-8")

    captured = {}

    class DummyServer:
        def __init__(self, *args, **kwargs):
            captured["port"] = kwargs.get("port")

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

    await core_server.run_server(port=None)

    assert captured["port"] == 9000


@pytest.mark.asyncio
async def test_run_server_defaults_port_to_8000(tmp_path, monkeypatch):
    config_path, example_path, var_dir = _patch_run_server_environment(tmp_path, monkeypatch)
    config_path.write_text("[server]\n", encoding="utf-8")
    example_path.write_text("", encoding="utf-8")
    (var_dir / "playpalace.db").write_text("", encoding="utf-8")

    captured = {}

    class DummyServer:
        def __init__(self, *args, **kwargs):
            captured["port"] = kwargs.get("port")

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

    await core_server.run_server(port=None)

    assert captured["port"] == 8000


@pytest.mark.asyncio
async def test_run_server_port_param_overrides_config(tmp_path, monkeypatch):
    config_path, example_path, var_dir = _patch_run_server_environment(tmp_path, monkeypatch)
    config_path.write_text("[server]\nport = 9000\n", encoding="utf-8")
    example_path.write_text("", encoding="utf-8")
    (var_dir / "playpalace.db").write_text("", encoding="utf-8")

    captured = {}

    class DummyServer:
        def __init__(self, *args, **kwargs):
            captured["port"] = kwargs.get("port")

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

    await core_server.run_server(port=7777)

    assert captured["port"] == 7777


# ---------------------------------------------------------------------------
# SSL resolution tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_server_uses_ssl_from_config(tmp_path, monkeypatch):
    config_path, example_path, var_dir = _patch_run_server_environment(tmp_path, monkeypatch)
    config_path.write_text(
        '[network]\nssl_cert = "/etc/cert.pem"\nssl_key = "/etc/key.pem"\n'
        "allow_insecure_ws = false\n",
        encoding="utf-8",
    )
    example_path.write_text("", encoding="utf-8")
    (var_dir / "playpalace.db").write_text("", encoding="utf-8")

    captured = {}

    class DummyServer:
        def __init__(self, *args, **kwargs):
            captured["ssl_cert"] = kwargs.get("ssl_cert")
            captured["ssl_key"] = kwargs.get("ssl_key")

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

    await core_server.run_server(ssl_cert=None, ssl_key=None)

    assert captured["ssl_cert"] == "/etc/cert.pem"
    assert captured["ssl_key"] == "/etc/key.pem"


@pytest.mark.asyncio
async def test_run_server_ssl_cli_overrides_config(tmp_path, monkeypatch):
    config_path, example_path, var_dir = _patch_run_server_environment(tmp_path, monkeypatch)
    config_path.write_text(
        '[network]\nssl_cert = "/etc/cert.pem"\nssl_key = "/etc/key.pem"\n'
        "allow_insecure_ws = false\n",
        encoding="utf-8",
    )
    example_path.write_text("", encoding="utf-8")
    (var_dir / "playpalace.db").write_text("", encoding="utf-8")

    captured = {}

    class DummyServer:
        def __init__(self, *args, **kwargs):
            captured["ssl_cert"] = kwargs.get("ssl_cert")
            captured["ssl_key"] = kwargs.get("ssl_key")

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

    await core_server.run_server(ssl_cert="/other/cert.pem", ssl_key="/other/key.pem")

    assert captured["ssl_cert"] == "/other/cert.pem"
    assert captured["ssl_key"] == "/other/key.pem"
