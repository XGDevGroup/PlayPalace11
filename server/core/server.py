"""Main server class that ties everything together."""

import asyncio
import contextlib
from contextlib import asynccontextmanager
import logging
import os
import shutil
import sys
import threading
import time
from collections import deque
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

import json
import websockets
from enum import Enum
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python <3.11 fallback when available
    import tomli as tomllib  # type: ignore[import]

from pydantic import ValidationError

from .config_paths import (
    get_default_config_path,
    get_example_config_path,
    ensure_default_config_dir,
    load_full_config,
)
from .state import ModeSnapshot, ServerLifecycleState, ServerMode
from .tick import TickScheduler, load_server_config
from .administration import AdministrationMixin
from .documents.browsing import DocumentBrowsingMixin, _DOCUMENTS_DIR
from .documents.transcriber_role import TranscriberRoleMixin
from .virtual_bots import VirtualBotManager
from ..network.websocket_server import WebSocketServer, ClientConnection
from ..persistence.database import Database
from ..auth.auth import AuthManager, AuthResult
from .tables.manager import TableManager
from .users.network_user import NetworkUser
from .users.base import MenuItem, EscapeBehavior, TrustLevel
from .users.preferences import UserPreferences, DiceKeepingStyle, PREF_CATEGORIES, PrefMeta
from ..games.registry import GameRegistry, get_game_class
from ..messages.localization import Localization
from .ui.common_flows import show_yes_no_menu
from .documents.manager import DocumentManager
from ..network.packet_models import CLIENT_TO_SERVER_PACKET_ADAPTER


VERSION = "11.0.0"
BOOTSTRAP_WARNING_ENV = "PLAYPALACE_SUPPRESS_BOOTSTRAP_WARNING"
PACKET_LOGGER = logging.getLogger("playpalace.packets")
LOG = logging.getLogger("playpalace.server")

DEFAULT_USERNAME_MIN_LENGTH = 3
DEFAULT_USERNAME_MAX_LENGTH = 32
DEFAULT_PASSWORD_MIN_LENGTH = 8
DEFAULT_PASSWORD_MAX_LENGTH = 128
DEFAULT_WS_MAX_MESSAGE_BYTES = 1_048_576  # 1 MB
DEFAULT_LOGIN_ATTEMPTS_PER_MINUTE = 5
DEFAULT_LOGIN_FAILURES_PER_MINUTE = 3
DEFAULT_REGISTRATION_ATTEMPTS_PER_MINUTE = 2
DEFAULT_REFRESH_ATTEMPTS_PER_MINUTE = 10
LOGIN_RATE_WINDOW_SECONDS = 60
REGISTRATION_RATE_WINDOW_SECONDS = 60
REFRESH_RATE_WINDOW_SECONDS = 60
DEFAULT_ACCESS_TOKEN_TTL_SECONDS = 60 * 60
DEFAULT_REFRESH_TOKEN_TTL_SECONDS = 30 * 24 * 60 * 60

STARTUP_GATE_ID = "startup"
LOCALIZATION_GATE_ID = "localization"


def _coerce_bool(value: Any, default: bool) -> bool:
    """Parse truthy values from config inputs with a fallback default.

    Args:
        value: Raw value from config input.
        default: Default value when parsing fails.

    Returns:
        Parsed boolean value.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


# Default paths based on module location
_MODULE_DIR = Path(__file__).parent.parent
_REPO_ROOT = Path(__file__).resolve().parents[2]
_VAR_SERVER_DIR = _REPO_ROOT / "var" / "server"
_DEFAULT_LOCALES_DIR = _MODULE_DIR / "locales"


def _ensure_var_server_dir() -> Path:
    """Ensure the repo-local var directory exists for server artifacts."""
    _VAR_SERVER_DIR.mkdir(parents=True, exist_ok=True)
    return _VAR_SERVER_DIR


class Server(AdministrationMixin, DocumentBrowsingMixin, TranscriberRoleMixin):
    """
    Main PlayPalace v11 server.

    Coordinates all components: network, auth, tables, games, and persistence.
    """

    def __init__(
        self,
        host: str = "::",
        port: int = 8000,
        db_path: str = "playpalace.db",
        locales_dir: str | Path | None = None,
        ssl_cert: str | Path | None = None,
        ssl_key: str | Path | None = None,
        config_path: str | Path | None = None,
        preload_locales: bool = False,
    ):
        """Initialize the server and core managers.

        Args:
            host: Address to bind the server to.
            port: Port to bind the server to.
            db_path: Path to the sqlite database file.
            locales_dir: Optional directory for locale files.
            ssl_cert: Optional SSL certificate path for TLS.
            ssl_key: Optional SSL private key path for TLS.
            config_path: Optional config.toml path override.
            preload_locales: Whether to block startup while compiling all locales.
        """
        self.host = host
        self.port = port
        self._ssl_cert = ssl_cert
        self._ssl_key = ssl_key
        self._default_locale = "en"
        self._enabled_locales: list[str] | None = None

        if db_path == "playpalace.db":
            db_path_obj = _ensure_var_server_dir() / "playpalace.db"
        else:
            db_path_obj = Path(db_path)
            db_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self._db = Database(db_path_obj)
        self._auth: AuthManager | None = None
        self._tables = TableManager()
        self._tables._server = self  # Enable callbacks from TableManager
        self._ws_server: WebSocketServer | None = None
        self._tick_scheduler: TickScheduler | None = None

        # User tracking
        self._users: dict[str, NetworkUser] = {}  # username -> NetworkUser
        self._user_states: dict[str, dict] = {}  # username -> UI state

        # Document manager
        self._documents = DocumentManager(_DOCUMENTS_DIR)

        # Virtual bot manager
        self._virtual_bots = VirtualBotManager(self)
        self._localization_warmup_task: asyncio.Task | None = None

        # Credential limits (overridable via config)
        self._username_min_length = DEFAULT_USERNAME_MIN_LENGTH
        self._username_max_length = DEFAULT_USERNAME_MAX_LENGTH
        self._password_min_length = DEFAULT_PASSWORD_MIN_LENGTH
        self._password_max_length = DEFAULT_PASSWORD_MAX_LENGTH
        self._ws_max_message_size = DEFAULT_WS_MAX_MESSAGE_BYTES
        self._config_path = Path(config_path) if config_path else get_default_config_path()
        self._allow_insecure_ws = False
        self._preload_locales = preload_locales
        self._login_ip_limit = DEFAULT_LOGIN_ATTEMPTS_PER_MINUTE
        self._login_user_limit = DEFAULT_LOGIN_FAILURES_PER_MINUTE
        self._registration_ip_limit = DEFAULT_REGISTRATION_ATTEMPTS_PER_MINUTE
        self._refresh_ip_limit = DEFAULT_REFRESH_ATTEMPTS_PER_MINUTE
        self._access_token_ttl_seconds = DEFAULT_ACCESS_TOKEN_TTL_SECONDS
        self._refresh_token_ttl_seconds = DEFAULT_REFRESH_TOKEN_TTL_SECONDS
        self._login_ip_window = LOGIN_RATE_WINDOW_SECONDS
        self._login_user_window = LOGIN_RATE_WINDOW_SECONDS
        self._registration_ip_window = REGISTRATION_RATE_WINDOW_SECONDS
        self._refresh_ip_window = REFRESH_RATE_WINDOW_SECONDS
        self._login_attempts_ip: dict[str, deque[float]] = {}
        self._login_attempts_user: dict[str, deque[float]] = {}
        self._registration_attempts_ip: dict[str, deque[float]] = {}
        self._refresh_attempts_ip: dict[str, deque[float]] = {}
        self._lifecycle = ServerLifecycleState()
        self._lifecycle.add_gate(STARTUP_GATE_ID, message="Server is starting up.")
        self._localization_gate_registered = False
        self._load_config_settings()

        # Initialize localization
        if locales_dir is None:
            resolved_locales = _DEFAULT_LOCALES_DIR
        else:
            provided_locales = Path(locales_dir)
            if not provided_locales.is_absolute():
                candidate = _MODULE_DIR / provided_locales
                if candidate.exists():
                    provided_locales = candidate
            resolved_locales = provided_locales
        Localization.init(resolved_locales, enabled_locales=self._enabled_locales)

    async def start(self) -> None:
        """Start the server."""
        # Load server configuration early to surface config errors before DB/network init
        server_config = load_server_config(self._config_path)
        tick_interval_ms = server_config.get("tick_interval_ms")
        if tick_interval_ms is not None:
            try:
                tick_interval_ms = int(tick_interval_ms)
            except (TypeError, ValueError) as exc:
                print(
                    f"ERROR: Invalid tick_interval_ms value '{tick_interval_ms}' in server configuration: {exc}",
                    file=sys.stderr,
                )
                raise SystemExit(1) from exc
            if tick_interval_ms < 1:
                print(
                    "ERROR: tick_interval_ms must be at least 1 millisecond.",
                    file=sys.stderr,
                )
                raise SystemExit(1)

        await self._preload_locales_if_requested()

        # Enforce transport requirements before bringing up listeners
        self._validate_transport_security()

        # Connect to database
        self._db.connect()
        self._auth = AuthManager(self._db)

        # Initialize trust levels for users
        promoted_user = self._db.initialize_trust_levels()
        if promoted_user:
            print(f"User '{promoted_user}' has been promoted to server owner (trust level 3).")
        self._warn_if_no_users()

        # Load existing tables
        self._load_tables()

        # Load documents
        doc_count = self._documents.load()
        print(f"Loaded {doc_count} documents.")

        # Initialize virtual bots
        try:
            self._virtual_bots.load_config()
        except ValueError as exc:
            print(f"ERROR: Invalid virtual bot configuration: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        loaded = self._virtual_bots.load_state()
        if loaded > 0:
            print(f"Restored {loaded} virtual bots from previous session.")

        # Start WebSocket server
        self._ws_server = WebSocketServer(
            host=self.host,
            port=self.port,
            on_connect=self._on_client_connect,
            on_disconnect=self._on_client_disconnect,
            on_message=self._on_client_message,
            ssl_cert=self._ssl_cert,
            ssl_key=self._ssl_key,
            max_message_size=self._ws_max_message_size,
        )
        await self._ws_server.start()
        if not self._ssl_cert:
            print("WARNING: Running without TLS (ws://). Credentials will be sent in plaintext.")
        if self._ws_max_message_size != DEFAULT_WS_MAX_MESSAGE_BYTES:
            print(f"Max inbound websocket message size: {self._ws_max_message_size} bytes")

        # Start tick scheduler
        self._tick_scheduler = TickScheduler(self._on_tick, tick_interval_ms)
        await self._tick_scheduler.start()
        # Tick interval message suppressed by default (configurable via config.toml).

        protocol = "wss" if self._ssl_cert else "ws"
        print(f"Server running on {protocol}://{self.host}:{self.port}")
        if self.host == "127.0.0.1":
            # Guidance message only; not a bind default.
            print("Bind IP is 127.0.0.1, use 0.0.0.0 to allow connections on all interfaces.")  # nosec B104
        elif self.host == "0.0.0.0":  # nosec B104
            # Guidance message only; not a bind default.
            print("Bind IP is 0.0.0.0, use 127.0.0.1 to limit to local connections.")  # nosec B104
        self._start_localization_warmup()
        self._lifecycle.resolve_gate(STARTUP_GATE_ID)

    async def stop(self) -> None:
        """Stop the server."""
        print("Stopping server...")

        if self._localization_warmup_task:
            self._localization_warmup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._localization_warmup_task
            self._localization_warmup_task = None

        # Save all tables
        self._save_tables()

        # Save virtual bot state (they persist across restarts)
        self._virtual_bots.save_state()

        # Stop tick scheduler
        if self._tick_scheduler:
            await self._tick_scheduler.stop()

        # Stop WebSocket server
        if self._ws_server:
            await self._ws_server.stop()

        # Close database
        self._db.close()

        print("Server stopped.")

    def _load_config_settings(self) -> None:
        """Load credential and network limits from config.toml if available."""
        path_obj = Path(self._config_path) if self._config_path is not None else None
        if path_obj is None or not path_obj.exists():
            return

        try:
            with open(path_obj, "rb") as f:
                config: dict[str, Any] = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError) as exc:  # pragma: no cover - logging only
            print(f"Failed to load config from {path_obj}: {exc}")
            return

        auth_cfg = config.get("auth")
        if not isinstance(auth_cfg, dict):
            auth_cfg = {}

        locale_cfg = config.get("localization")
        if isinstance(locale_cfg, dict):
            default_locale = locale_cfg.get("default_locale")
            if isinstance(default_locale, str) and default_locale.strip():
                self._default_locale = default_locale.strip()
            enabled = locale_cfg.get("enabled_locales")
            if isinstance(enabled, list) and all(isinstance(v, str) for v in enabled):
                self._enabled_locales = enabled

        def _read_limit(source: dict[str, Any], key: str, current: int, minimum: int = 1) -> int:
            """Read an integer limit from config with a minimum clamp."""
            value = source.get(key)
            if value is None:
                return current
            try:
                value_int = int(value)
            except (TypeError, ValueError):
                return current
            return max(minimum, value_int)

        if auth_cfg:
            self._username_min_length = _read_limit(
                auth_cfg, "username_min_length", self._username_min_length
            )
            self._username_max_length = _read_limit(
                auth_cfg,
                "username_max_length",
                self._username_max_length,
                self._username_min_length,
            )
            self._password_min_length = _read_limit(
                auth_cfg, "password_min_length", self._password_min_length
            )
            self._password_max_length = _read_limit(
                auth_cfg,
                "password_max_length",
                self._password_max_length,
                self._password_min_length,
            )
            self._refresh_token_ttl_seconds = _read_limit(
                auth_cfg, "refresh_token_ttl_seconds", self._refresh_token_ttl_seconds, minimum=60
            )

            # Ensure ranges are sane
            if self._username_min_length > self._username_max_length:
                self._username_max_length = self._username_min_length
            if self._password_min_length > self._password_max_length:
                self._password_max_length = self._password_min_length

        net_cfg = config.get("network")
        if isinstance(net_cfg, dict):
            max_bytes = _read_limit(
                net_cfg, "max_message_bytes", self._ws_max_message_size, minimum=1
            )
            self._ws_max_message_size = max_bytes
            self._allow_insecure_ws = _coerce_bool(
                net_cfg.get("allow_insecure_ws"), self._allow_insecure_ws
            )

        rate_cfg = auth_cfg.get("rate_limits") if isinstance(auth_cfg, dict) else None
        if isinstance(rate_cfg, dict):
            self._login_ip_limit = _read_limit(
                rate_cfg, "login_per_minute", self._login_ip_limit, minimum=0
            )
            self._login_user_limit = _read_limit(
                rate_cfg, "login_failures_per_minute", self._login_user_limit, minimum=0
            )
            self._registration_ip_limit = _read_limit(
                rate_cfg, "registration_per_minute", self._registration_ip_limit, minimum=0
            )
            self._refresh_ip_limit = _read_limit(
                rate_cfg, "refresh_per_minute", self._refresh_ip_limit, minimum=0
            )
            self._login_ip_window = _read_limit(
                rate_cfg, "login_window_seconds", self._login_ip_window, minimum=1
            )
            self._login_user_window = _read_limit(
                rate_cfg, "login_failure_window_seconds", self._login_user_window, minimum=1
            )
            self._registration_ip_window = _read_limit(
                rate_cfg, "registration_window_seconds", self._registration_ip_window, minimum=1
            )
            self._refresh_ip_window = _read_limit(
                rate_cfg, "refresh_window_seconds", self._refresh_ip_window, minimum=1
            )

    def _validate_transport_security(self) -> None:
        """Validate TLS/insecure configuration and exit on invalid combos."""
        if self._allow_insecure_ws and (self._ssl_cert or self._ssl_key):
            print(
                "ERROR: allow_insecure_ws=true cannot be combined with SSL certificate or key. "
                "Remove the certificate settings or disable insecure mode.",
                file=sys.stderr,
            )
            raise SystemExit(1)

        if not self._allow_insecure_ws and (not self._ssl_cert or not self._ssl_key):
            print(
                "ERROR: TLS is required. Provide --ssl-cert and --ssl-key "
                "or set [network].allow_insecure_ws to true.",
                file=sys.stderr,
            )
            raise SystemExit(1)

    @staticmethod
    def _get_client_ip(client: ClientConnection) -> str:
        """Return the client IP string (or "unknown")."""
        if not client.address:
            return "unknown"
        return client.address.split(":")[0]

    @staticmethod
    def _sanitize_credentials(username: str | None, password: str | None) -> tuple[str, str]:
        """Normalize credential fields before validation."""
        username = (username or "").strip()
        password = password or ""
        return username, password

    def _validate_credentials(self, username: str, password: str) -> tuple[str, str, str | None]:
        """Validate username/password lengths and return an error message if invalid."""
        username, password = self._sanitize_credentials(username, password)

        if len(username) < self._username_min_length or len(username) > self._username_max_length:
            return (
                username,
                password,
                (
                    f"Username must be between {self._username_min_length} and {self._username_max_length} characters."
                ),
            )

        if len(password) < self._password_min_length or len(password) > self._password_max_length:
            return (
                username,
                password,
                (
                    f"Password must be between {self._password_min_length} and {self._password_max_length} characters."
                ),
            )

        return username, password, None

    @staticmethod
    async def _send_credential_error(client: ClientConnection, message: str) -> None:
        """Send a credential validation error and disconnect the client."""
        await client.send({"type": "play_sound", "name": "accounterror.ogg"})
        await client.send({"type": "speak", "text": message})
        await client.send(
            {
                "type": "disconnect",
                "reconnect": False,
                "show_message": True,
                "return_to_login": True,
                "message": message,
            }
        )

    def _allow_attempt(
        self, bucket: dict[str, deque[float]], key: str, limit: int, window: float, now: float
    ) -> bool:
        """Record and evaluate a rate-limit attempt.

        Args:
            bucket: Mapping of key -> deque[timestamps].
            key: Rate-limit key (e.g., IP or username).
            limit: Max attempts within the window.
            window: Window size in seconds.
            now: Current monotonic time.

        Returns:
            True if the attempt is allowed, False if throttled.
        """
        if limit <= 0:
            return True
        dq = bucket.setdefault(key, deque())
        while dq and now - dq[0] > window:
            dq.popleft()
        if len(dq) >= limit:
            return False
        dq.append(now)
        return True

    def _get_attempt_count(
        self, bucket: dict[str, deque[float]], key: str, window: float, now: float
    ) -> int:
        """Return count of attempts within the window for a key."""
        dq = bucket.get(key)
        if not dq:
            return 0
        while dq and now - dq[0] > window:
            dq.popleft()
        if not dq:
            bucket.pop(key, None)
            return 0
        return len(dq)

    def _record_attempt(self, bucket: dict[str, deque[float]], key: str, now: float) -> None:
        """Record an attempt timestamp for a key."""
        dq = bucket.setdefault(key, deque())
        dq.append(now)

    def _check_login_rate_limit(self, client_ip: str, username: str) -> str | None:
        """Check login rate limits and return an error message if blocked."""
        now = time.monotonic()
        if not self._allow_attempt(
            self._login_attempts_ip, client_ip, self._login_ip_limit, self._login_ip_window, now
        ):
            return "Too many login attempts from this address. Please wait and try again."
        if username:
            failures = self._get_attempt_count(
                self._login_attempts_user, username, self._login_user_window, now
            )
            if self._login_user_limit > 0 and failures >= self._login_user_limit:
                return (
                    "Too many failed login attempts for this username. Please wait and try again."
                )
        return None

    def _record_login_failure(self, username: str) -> None:
        """Record a failed login attempt for username rate limiting."""
        if not username or self._login_user_limit <= 0:
            return
        now = time.monotonic()
        self._get_attempt_count(self._login_attempts_user, username, self._login_user_window, now)
        self._record_attempt(self._login_attempts_user, username, now)

    def _check_registration_rate_limit(self, client_ip: str) -> str | None:
        """Check registration rate limits and return an error message if blocked."""
        now = time.monotonic()
        if not self._allow_attempt(
            self._registration_attempts_ip,
            client_ip,
            self._registration_ip_limit,
            self._registration_ip_window,
            now,
        ):
            return "Too many registration attempts from this address. Please wait and try again."
        return None

    def _check_refresh_rate_limit(self, client_ip: str) -> str | None:
        """Check refresh token rate limits and return an error message if blocked."""
        now = time.monotonic()
        if not self._allow_attempt(
            self._refresh_attempts_ip,
            client_ip,
            self._refresh_ip_limit,
            self._refresh_ip_window,
            now,
        ):
            return "Too many refresh attempts from this address. Please wait and try again."
        return None

    def _warn_if_no_users(self) -> None:
        """Print a warning if no user accounts exist yet."""
        if os.environ.get(BOOTSTRAP_WARNING_ENV):
            return
        try:
            if self._db.get_user_count() > 0:
                return
        except Exception:
            return

        print(
            "WARNING: No user accounts exist. Run "
            "`uv run python -m server.cli bootstrap-owner --username <name>` "
            "to create an initial administrator before exposing this server on the network. "
            f"Set {BOOTSTRAP_WARNING_ENV}=1 to suppress this warning for CI or local testing."
        )

    def _start_localization_warmup(self) -> None:
        """Kick off localization compilation in the background."""
        if self._preload_locales:
            return
        if self._localization_warmup_task:
            return
        Localization.set_warmup_active(True)
        loop = asyncio.get_running_loop()
        self._localization_warmup_task = loop.create_task(self._warm_locales_async())
        print(
            "Localization bundles compiling in background "
            "(pass --preload-locales to block startup until finished)."
        )

    def _is_localization_warmup_active(self) -> bool:
        """Return whether non-blocking localization warmup is still running."""
        return Localization.is_warmup_active()

    @staticmethod
    def _notify_localization_in_progress(user: NetworkUser) -> None:
        """Tell the user localization is still warming up."""
        user.speak_l("localization-in-progress-try-again", buffer="misc")

    async def _warm_locales_async(self) -> None:
        """Compile all locale bundles without blocking startup."""
        logger = logging.getLogger("playpalace")
        try:
            await self._run_localization_warmup_in_daemon_thread()
            self._lifecycle.resolve_gate(LOCALIZATION_GATE_ID)
            print("Localization bundles compiled.")
        except SystemExit:
            logger.warning("Localization preload aborted due to configuration error.")
            self._lifecycle.enter_maintenance(
                message="Localization preload failed due to configuration error."
            )
            await self._disconnect_clients_for_status(self._lifecycle.snapshot())
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Localization preload failed")
            self._lifecycle.enter_maintenance(
                message="Localization preload failed. Check server logs."
            )
            await self._disconnect_clients_for_status(self._lifecycle.snapshot())
        finally:
            Localization.set_warmup_active(False)

    async def _run_localization_warmup_in_daemon_thread(self) -> None:
        """Run localization warmup in a daemon thread so shutdown isn't blocked."""
        loop = asyncio.get_running_loop()
        done: asyncio.Future[None] = loop.create_future()

        def _finish_ok() -> None:
            if not done.done():
                done.set_result(None)

        def _finish_err(exc: BaseException) -> None:
            if not done.done():
                done.set_exception(exc)

        def _worker() -> None:
            try:
                Localization.preload_bundles()
            except BaseException as exc:  # pragma: no cover - exercised via awaiter
                with contextlib.suppress(RuntimeError):
                    loop.call_soon_threadsafe(_finish_err, exc)
            else:
                with contextlib.suppress(RuntimeError):
                    loop.call_soon_threadsafe(_finish_ok)

        thread = threading.Thread(
            target=_worker,
            daemon=True,
            name="playpalace-localization-warmup",
        )
        thread.start()
        await done

    def _ensure_localization_gate(self) -> None:
        """Register the localization gate exactly once."""
        if self._localization_gate_registered:
            return
        self._localization_gate_registered = True
        self._lifecycle.add_gate(LOCALIZATION_GATE_ID, message="Compiling localization bundles...")

    async def _reject_client_during_unavailable(
        self, client: ClientConnection, snapshot: ModeSnapshot
    ) -> None:
        """Inform a newly connected client about current server status and disconnect."""
        await self._send_status_and_disconnect(client, snapshot)

    async def _disconnect_clients_for_status(self, snapshot: ModeSnapshot) -> None:
        """Broadcast lifecycle status to all connected clients and disconnect them."""
        if not self._ws_server or not self._ws_server.clients:
            return
        await asyncio.gather(
            *[
                self._send_status_and_disconnect(client, snapshot)
                for client in list(self._ws_server.clients.values())
            ]
        )

    @asynccontextmanager
    async def maintenance_mode(self, message: str, resume_at: datetime | None = None):
        """Context manager for internal maintenance tasks that require pausing clients."""
        self._lifecycle.enter_maintenance(message=message, resume_at=resume_at)
        await self._disconnect_clients_for_status(self._lifecycle.snapshot())
        try:
            yield
        finally:
            self._lifecycle.exit_maintenance()

    async def _send_status_and_disconnect(
        self, client: ClientConnection, snapshot: ModeSnapshot
    ) -> None:
        """Send a lifecycle status update followed by a disconnect packet."""
        retry_after = self._calculate_retry_after(snapshot)
        status_packet = self._build_status_packet(snapshot, retry_after)
        disconnect_packet = self._build_status_disconnect(snapshot, retry_after)
        await client.send(status_packet)
        await client.send(disconnect_packet)
        await client.close()

    def _build_status_packet(self, snapshot: ModeSnapshot, retry_after: int) -> dict[str, object]:
        """Construct a status payload for clients."""
        payload: dict[str, object] = {
            "type": "server_status",
            "mode": snapshot.mode.value,
            "retry_after": retry_after,
        }
        if snapshot.message:
            payload["message"] = snapshot.message
        if snapshot.resume_at:
            payload["resume_at"] = self._format_datetime(snapshot.resume_at)
        return payload

    def _build_status_disconnect(
        self, snapshot: ModeSnapshot, retry_after: int
    ) -> dict[str, object]:
        """Construct the disconnect payload paired with a lifecycle notification."""
        message_text = self._format_status_message(snapshot)
        return {
            "type": "disconnect",
            "reconnect": False,
            "show_message": True,
            "return_to_login": True,
            "status_mode": snapshot.mode.value,
            "retry_after": retry_after,
            "message": message_text,
        }

    @staticmethod
    def _format_status_message(snapshot: ModeSnapshot) -> str:
        """Build a human-readable lifecycle status summary."""
        message = snapshot.message or "Server is temporarily unavailable."
        if snapshot.resume_at:
            resume_text = Server._format_datetime(snapshot.resume_at)
            message = f"{message} Expected availability: {resume_text}."
        return message

    def _calculate_retry_after(self, snapshot: ModeSnapshot) -> int:
        """Compute a recommended retry delay for clients."""
        if snapshot.resume_at:
            now = datetime.now(timezone.utc)
            delta = int((snapshot.resume_at - now).total_seconds())
            return max(1, delta)
        if snapshot.mode == ServerMode.INITIALIZING:
            return 5
        if snapshot.mode == ServerMode.MAINTENANCE:
            return 30
        return 5

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        """Format datetimes as ISO-8601 strings with Z suffix when UTC."""
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        iso_value = value.astimezone(timezone.utc).isoformat()
        if iso_value.endswith("+00:00"):
            iso_value = iso_value[:-6] + "Z"
        return iso_value

    async def _preload_locales_if_requested(self) -> None:
        """Synchronously compile locales when preload flag is set."""
        if not self._preload_locales:
            return
        self._ensure_localization_gate()
        await asyncio.to_thread(Localization.preload_bundles)
        self._lifecycle.resolve_gate(LOCALIZATION_GATE_ID)

    def _load_tables(self) -> None:
        """Load tables from database and restore their games."""
        from .users.bot import Bot

        tables = self._db.load_all_tables()
        for table in tables:
            self._tables.add_table(table)

            # Restore game from JSON if present
            if table.game_json:
                game_class = get_game_class(table.game_type)
                if not game_class:
                    print(f"WARNING: Could not find game class for {table.game_type}")
                    continue

                # Deserialize game and rebuild runtime state
                game = game_class.from_json(table.game_json)
                game.rebuild_runtime_state()
                table.game = game
                game._table = table

                # Setup keybinds (runtime only, not serialized)
                game.setup_keybinds()
                if hasattr(game, "_reset_transcripts"):
                    game._reset_transcripts()
                # Attach bots (humans will be attached when they reconnect)
                # Action sets are already restored from serialization
                for player in game.players:
                    if player.is_bot:
                        bot_user = Bot(player.name)
                        game.attach_user(player.id, bot_user)

        print(f"Loaded {len(tables)} tables from database.")

        # Delete all tables from database after loading to prevent stale data
        # on subsequent restarts. Tables will be re-saved on shutdown.
        self._db.delete_all_tables()

    def _save_tables(self) -> None:
        """Save all tables to database."""
        tables = self._tables.save_all()
        self._db.save_all_tables(tables)
        print(f"Saved {len(tables)} tables to database.")

    def _on_tick(self) -> None:
        """Called every tick (50ms)."""
        # Tick all tables
        self._tables.on_tick()

        # Tick virtual bots (handle state transitions)
        self._virtual_bots.on_tick()

        # Flush queued messages for all users
        self._flush_user_messages()

    def _flush_user_messages(self) -> None:
        """Send all queued messages for all users."""
        for username, user in self._users.items():
            messages = user.get_queued_messages()
            if messages and self._ws_server:
                client = self._ws_server.get_client_by_username(username)
                if client:
                    for msg in messages:
                        asyncio.create_task(client.send(msg))

    async def _handoff_existing_session(
        self, user: NetworkUser, new_client: ClientConnection
    ) -> None:
        """Disconnect the existing client session for a user and bind the new connection."""
        old_client = user.connection
        if old_client:
            old_client.replaced = True
            try:
                await old_client.send(
                    {
                        "type": "disconnect",
                        "reconnect": False,
                        "show_message": True,
                        "return_to_login": True,
                        "message": Localization.get(user.locale, "already-logged-in"),
                    }
                )
            except (OSError, RuntimeError, websockets.exceptions.ConnectionClosed) as exc:
                LOG.debug("Failed to notify replaced session: %s", exc)
            with contextlib.suppress(Exception):
                await old_client.close()
        new_client.username = user.username
        new_client.authenticated = True
        user.set_connection(new_client)

    def _queue_transcript_replay(self, user: NetworkUser, game, player_id: str) -> None:
        """Queue buffered transcript packets for a user."""
        if not hasattr(game, "get_transcript"):
            return
        history = game.get_transcript(player_id)
        if not history:
            return
        for entry in history:
            packet = {
                "type": "speak",
                "text": entry.get("text", ""),
                "muted": True,
            }
            buffer_name = entry.get("buffer")
            if buffer_name:
                packet["buffer"] = buffer_name
            user.queue_packet(packet)

    async def _on_client_connect(self, client: ClientConnection) -> None:
        """Handle new client connection."""
        snapshot = self._lifecycle.snapshot()
        if snapshot.mode != ServerMode.RUNNING:
            print(f"Client deferred ({snapshot.mode.value}): {client.address}")
            await self._reject_client_during_unavailable(client, snapshot)
            return
        print(f"Client connected: {client.address}")

    async def _on_client_disconnect(self, client: ClientConnection) -> None:
        """Handle client disconnection."""
        username = client.username or "unknown"
        print(f"Client disconnected: {username}@{client.address}")
        if getattr(client, "replaced", False):
            return
        if client.username:
            username = client.username
            table = self._tables.find_user_table(username)
            # Check user status before cleanup
            user = self._users.get(username)

            if table and user:
                if table.game:
                    player = table.game.get_player_by_id(user.uuid)
                    if player:
                        table.game._perform_leave_game(player)
                # Keep membership for rejoin unless this was the last member
                if len(table.members) <= 1:
                    table.remove_member(username)

            # Only broadcast offline if user was approved and not banned
            if user and user.approved and user.trust_level != TrustLevel.BANNED:
                is_admin = user.trust_level.value >= TrustLevel.ADMIN.value
                offline_sound = "offlineadmin.ogg" if is_admin else "offline.ogg"
                self._broadcast_presence_l("user-offline", username, offline_sound)

            # Clean up user state
            self._users.pop(username, None)
            self._user_states.pop(username, None)

    def _broadcast_presence_l(self, message_id: str, player_name: str, sound: str) -> None:
        """Broadcast a localized presence announcement to all approved online users with sound."""
        for username, user in self._users.items():
            if not user.approved:
                continue  # Don't send broadcasts to unapproved users
            user.speak_l(message_id, buffer="activity", player=player_name)
            user.play_sound(sound)

    def _broadcast_admin_announcement(self, admin_name: str) -> None:
        """Broadcast an admin announcement to all approved online users."""
        for username, user in self._users.items():
            if not user.approved:
                continue  # Don't send broadcasts to unapproved users
            user.speak_l("user-is-admin", buffer="activity", player=admin_name)

    def _broadcast_server_owner_announcement(self, owner_name: str) -> None:
        """Broadcast a server owner announcement to all approved online users."""
        for username, user in self._users.items():
            if not user.approved:
                continue  # Don't send broadcasts to unapproved users
            user.speak_l("user-is-server-owner", buffer="activity", player=owner_name)

    def _broadcast_table_created(self, host_name: str, game_type: str) -> None:
        """Broadcast a table creation announcement to all approved online users not in a game."""
        game_class = get_game_class(game_type)
        if not game_class:
            return
        name_key = game_class.get_name_key()
        for username, user in self._users.items():
            if not user.approved:
                continue
            state = self._user_states.get(username, {})
            if state.get("menu") == "in_game":
                continue
            game_name = Localization.get(user.locale, name_key)
            user.speak_l("table-created", buffer="activity", host=host_name, game=game_name)
            user.play_sound("table_created.ogg")

    async def _on_client_message(self, client: ClientConnection, packet: dict) -> None:
        """Handle incoming message from client."""
        try:
            await self._dispatch_client_message(client, packet)
        except Exception:
            identifier = client.username or client.address
            LOG.exception("Unhandled error processing message from %s", identifier)
            user = self._users.get(client.username) if client.username else None
            if user:
                user.speak_l("internal-error")

    async def _dispatch_client_message(self, client: ClientConnection, packet: dict) -> None:
        """Dispatch an incoming client message to the appropriate handler."""
        try:
            packet_model = CLIENT_TO_SERVER_PACKET_ADAPTER.validate_python(packet)
            packet = packet_model.model_dump(exclude_none=True)
        except ValidationError as exc:
            identifier = client.username or client.address
            PACKET_LOGGER.warning("Dropping invalid packet from %s: %s", identifier, exc)
            return

        packet_type = packet.get("type")

        if packet_type == "authorize":
            await self._handle_authorize(client, packet)
        elif packet_type == "register":
            await self._handle_register(client, packet)
        elif packet_type == "refresh_session":
            await self._handle_refresh_session(client, packet)
        elif not client.authenticated:
            # Ignore non-auth packets from unauthenticated clients
            return
        elif packet_type == "ping":
            # Always allow ping to keep connection alive
            await self._handle_ping(client)
        elif packet_type == "menu":
            # Allow menu selections for all authenticated users (including unapproved)
            await self._handle_menu(client, packet)
        else:
            # For all other packets, check if user is approved
            user = self._users.get(client.username)
            if user and not user.approved:
                # Unapproved users can only ping and use menus - drop all other packets
                return

            if packet_type == "keybind":
                await self._handle_keybind(client, packet)
            elif packet_type == "document_editor":
                await self._handle_document_editor_packet(client, packet)
            elif packet_type == "editbox":
                await self._handle_editbox(client, packet)
            elif packet_type == "chat":
                await self._handle_chat(client, packet)
            elif packet_type == "list_online":
                await self._handle_list_online(client)
            elif packet_type == "list_online_with_games":
                await self._handle_list_online_with_games(client)

    async def _finalize_login(
        self,
        client: ClientConnection,
        username: str,
        *,
        session_token: str,
        session_expires_at: int,
        refresh_token: str,
        refresh_expires_at: int,
        success_type: str = "authorize_success",
    ) -> None:
        """Attach user state and send login success packets."""
        # Create or update network user with preferences and persistent UUID
        user_record = self._auth.get_user(username)
        if not user_record:
            await self._send_credential_error(client, "Account not found.")
            return
        preferences = self._load_user_preferences(user_record)
        user, is_new_login = await self._attach_or_update_user(
            client, username, user_record, preferences
        )

        await self._send_login_success(
            client,
            username,
            session_token=session_token,
            session_expires_at=session_expires_at,
            refresh_token=refresh_token,
            refresh_expires_at=refresh_expires_at,
            success_type=success_type,
        )

        # Send game list
        await self._send_game_list(client)

        # Check if user is banned
        if await self._handle_banned_login(user):
            return

        # Check if user is approved
        if self._handle_unapproved_login(user):
            return

        # Broadcast online announcement (only for approved, non-banned users) once per login
        if is_new_login:
            self._broadcast_login_presence(user)

        # Notify admin of pending account approvals (excluding banned users)
        if user.trust_level.value >= TrustLevel.ADMIN.value:
            self._notify_pending_account_requests(user)

        # Check if user is in a table
        if not self._restore_login_table(user, username):
            self._show_main_menu(user)

    def _load_user_preferences(self, user_record: "AuthUserRecord") -> UserPreferences:
        """Load stored preferences, falling back to defaults."""
        if user_record.preferences_json:
            try:
                prefs_data = json.loads(user_record.preferences_json)
                return UserPreferences.from_dict(prefs_data)
            except (json.JSONDecodeError, KeyError):
                pass
        return UserPreferences()

    async def _attach_or_update_user(
        self,
        client: ClientConnection,
        username: str,
        user_record: "AuthUserRecord",
        preferences: UserPreferences,
    ) -> tuple[NetworkUser, bool]:
        """Attach a connection to an existing user or create a new one."""
        locale = user_record.locale or "en"
        user_uuid = user_record.uuid
        trust_level = user_record.trust_level or TrustLevel.USER
        is_approved = user_record.approved

        existing_user = self._users.get(username)
        if existing_user:
            await self._handoff_existing_session(existing_user, client)
            existing_user.set_locale(locale)
            existing_user.set_preferences(preferences)
            existing_user.set_trust_level(trust_level)
            existing_user.set_approved(is_approved)
            existing_user.set_client_type(client.client_type)
            existing_user.set_platform(client.platform)
            existing_user.set_fluent_languages(user_record.fluent_languages)
            return existing_user, False

        client.username = username
        client.authenticated = True
        user = NetworkUser(
            username,
            locale,
            client,
            uuid=user_uuid,
            preferences=preferences,
            trust_level=trust_level,
            approved=is_approved,
            fluent_languages=user_record.fluent_languages,
        )
        user.set_client_type(client.client_type)
        user.set_platform(client.platform)
        self._users[username] = user
        return user, True

    async def _send_login_success(
        self,
        client: ClientConnection,
        username: str,
        *,
        session_token: str,
        session_expires_at: int,
        refresh_token: str,
        refresh_expires_at: int,
        success_type: str,
    ) -> None:
        """Send the login/refresh success packet."""
        payload = {
            "username": username,
            "session_token": session_token,
            "session_expires_at": session_expires_at,
            "refresh_token": refresh_token,
            "refresh_expires_at": refresh_expires_at,
        }
        if success_type == "authorize_success":
            payload.update({"type": "authorize_success", "version": VERSION})
        else:
            payload.update({"type": "refresh_session_success", "version": VERSION})
        await client.send(payload)
        print(f"Client authorized: {username}@{client.address}")

    async def _handle_banned_login(self, user: NetworkUser) -> bool:
        """Handle disconnecting banned users."""
        if user.trust_level != TrustLevel.BANNED:
            return False
        ban_message = Localization.get(user.locale, "account-banned")
        user.play_sound("accountban.ogg")
        user.speak_l("account-banned", buffer="activity")
        for msg in user.get_queued_messages():
            await user.connection.send(msg)
        await user.connection.send(
            {
                "type": "disconnect",
                "reconnect": False,
                "show_message": True,
                "message": ban_message,
            }
        )
        return True

    def _handle_unapproved_login(self, user: NetworkUser) -> bool:
        """Route unapproved users to the limited main menu."""
        if user.approved:
            return False
        user.speak_l("waiting-for-approval", buffer="activity")
        self._show_main_menu(user)
        return True

    def _broadcast_login_presence(self, user: NetworkUser) -> None:
        """Broadcast login presence and role announcements."""
        online_sound = (
            "onlineadmin.ogg" if user.trust_level.value >= TrustLevel.ADMIN.value else "online.ogg"
        )
        self._broadcast_presence_l("user-online", user.username, online_sound)

        if user.trust_level.value >= TrustLevel.SERVER_OWNER.value:
            self._broadcast_server_owner_announcement(user.username)
        elif user.trust_level.value >= TrustLevel.ADMIN.value:
            self._broadcast_admin_announcement(user.username)

    def _notify_pending_account_requests(self, user: NetworkUser) -> None:
        """Notify admins about pending account approvals."""
        pending_users = self._db.get_pending_users(exclude_banned=True)
        if not pending_users:
            return
        user.speak_l("account-request", buffer="activity")
        user.play_sound("accountrequest.ogg")

    def _restore_login_table(self, user: NetworkUser, username: str) -> bool:
        """Attempt to restore a user into their existing table."""
        table = self._tables.find_user_table(username)
        if not (table and table.game):
            return False

        game = table.game
        table.attach_user(username, user)
        table.add_member(username, user, as_spectator=False)
        player = game.get_player_by_id(user.uuid)
        if not player:
            return True

        was_bot = player.is_bot
        if was_bot:
            player.is_bot = False
        game.attach_user(player.id, user)
        if was_bot:
            game.broadcast_l("player-took-over", player=user.username)
            game.broadcast_sound("join.ogg")
            game.rebuild_all_menus()

        self._user_states[username] = {
            "menu": "in_game",
            "table_id": table.table_id,
        }
        game.rebuild_player_menu(player)
        self._queue_transcript_replay(user, game, player.id)
        return True

    async def _handle_authorize(self, client: ClientConnection, packet: dict) -> None:
        """Authorize a client and attach a NetworkUser if successful.

        Args:
            client: Client connection.
            packet: Incoming authorize payload.
        """
        username_raw = packet.get("username", "")
        password_raw = packet.get("password", "")
        session_token = packet.get("session_token")
        locale = packet.get("locale") or self._default_locale
        client.client_type = packet.get("client_type") or ""
        client.platform = packet.get("platform") or ""

        if session_token:
            token_username = self._auth.validate_session(session_token)
            if not token_username:
                await self._send_credential_error(client, "Session expired. Please log in again.")
                return
            if username_raw and token_username.lower() != username_raw.lower():
                await self._send_credential_error(client, "Session token does not match username.")
                return
            username = token_username
        else:
            username, password, error = self._validate_credentials(username_raw, password_raw)
            if error:
                await self._send_credential_error(client, error)
                return

            client_ip = self._get_client_ip(client)
            throttle_message = self._check_login_rate_limit(client_ip, username)
            if throttle_message:
                await self._send_credential_error(client, throttle_message)
                return

            # Try to authenticate or register
            auth_result = self._auth.authenticate(username, password)
            if auth_result != AuthResult.SUCCESS:
                if auth_result == AuthResult.WRONG_PASSWORD:
                    self._record_login_failure(username)
                    # Username exists but password is wrong - show error dialog
                    error_message = Localization.get(locale, "incorrect-password")
                    await client.send({"type": "play_sound", "name": "accounterror.ogg"})
                    await client.send(
                        {"type": "speak", "text": error_message, "buffer": "activity"}
                    )
                    await client.send(
                        {
                            "type": "disconnect",
                            "reconnect": False,
                            "show_message": True,
                            "return_to_login": True,
                            "message": error_message,
                        }
                    )
                    return

                # User not found - check if this will be a new user that needs approval
                needs_approval = self._db.get_user_count() > 0

                # Try to register
                if not self._auth.register(username, password, locale=locale):
                    self._record_login_failure(username)
                    # Registration failed (shouldn't happen if user not found, but handle anyway)
                    error_message = Localization.get(locale, "incorrect-username")
                    await client.send({"type": "play_sound", "name": "accounterror.ogg"})
                    await client.send(
                        {"type": "speak", "text": error_message, "buffer": "activity"}
                    )
                    await client.send(
                        {
                            "type": "disconnect",
                            "reconnect": False,
                            "show_message": True,
                            "return_to_login": True,
                            "message": error_message,
                        }
                    )
                    return

                # New user registered - notify admins if approval is needed
                if needs_approval:
                    self._notify_admins("account-request", "accountrequest.ogg")

        access_token, access_expires = self._auth.create_session(
            username, self._access_token_ttl_seconds
        )
        refresh_token, refresh_expires = self._auth.create_refresh_token(
            username, self._refresh_token_ttl_seconds
        )

        await self._finalize_login(
            client,
            username,
            session_token=access_token,
            session_expires_at=access_expires,
            refresh_token=refresh_token,
            refresh_expires_at=refresh_expires,
            success_type="authorize_success",
        )

    async def _handle_register(self, client: ClientConnection, packet: dict) -> None:
        """Register a new user from the registration dialog.

        Args:
            client: Client connection.
            packet: Incoming register payload.
        """
        username_raw = packet.get("username", "")
        password_raw = packet.get("password", "")
        # email and bio are sent but not stored yet
        locale = packet.get("locale") or self._default_locale

        username, password, error = self._validate_credentials(username_raw, password_raw)
        if error:
            await client.send({"type": "speak", "text": error, "buffer": "activity"})
            return

        client_ip = self._get_client_ip(client)
        throttle_message = self._check_registration_rate_limit(client_ip)
        if throttle_message:
            await client.send({"type": "speak", "text": throttle_message, "buffer": "activity"})
            return

        # All self-registered users require approval.
        needs_approval = True

        # Try to register the user
        if self._auth.register(username, password, locale=locale):
            await client.send(
                {
                    "type": "speak",
                    "text": "Registration successful! Your account is waiting for approval.",
                    "buffer": "activity",
                }
            )
            # Notify admins of new account request (only if user needs approval)
            if needs_approval:
                self._notify_admins("account-request", "accountrequest.ogg")
        else:
            await client.send(
                {
                    "type": "speak",
                    "text": "Username already taken. Please choose a different username.",
                    "buffer": "activity",
                }
            )

    async def _handle_refresh_session(self, client: ClientConnection, packet: dict) -> None:
        """Refresh an access session using a refresh token."""
        refresh_token = packet.get("refresh_token", "")
        username_hint = packet.get("username", "")
        client.client_type = packet.get("client_type") or ""
        client.platform = packet.get("platform") or ""
        client_ip = self._get_client_ip(client)
        throttle_message = self._check_refresh_rate_limit(client_ip)
        if throttle_message:
            await self._send_credential_error(client, throttle_message)
            return

        result = self._auth.refresh_session(
            refresh_token, self._access_token_ttl_seconds, self._refresh_token_ttl_seconds
        )
        if not result:
            await client.send(
                {
                    "type": "refresh_session_failure",
                    "message": "Refresh token expired. Please log in again.",
                }
            )
            await client.send(
                {
                    "type": "disconnect",
                    "reconnect": False,
                    "show_message": True,
                    "return_to_login": True,
                    "message": "Session expired. Please log in again.",
                }
            )
            return

        username, access_token, access_expires, new_refresh_token, refresh_expires = result
        if username_hint and username_hint.lower() != username.lower():
            await client.send(
                {
                    "type": "refresh_session_failure",
                    "message": "Refresh token does not match username.",
                }
            )
            await client.send(
                {
                    "type": "disconnect",
                    "reconnect": False,
                    "show_message": True,
                    "return_to_login": True,
                    "message": "Session expired. Please log in again.",
                }
            )
            return

        await self._finalize_login(
            client,
            username,
            session_token=access_token,
            session_expires_at=access_expires,
            refresh_token=new_refresh_token,
            refresh_expires_at=refresh_expires,
            success_type="refresh_session_success",
        )

    async def _send_game_list(self, client: ClientConnection) -> None:
        """Send the list of available games to the client."""
        games = []
        for game_class in GameRegistry.get_all():
            games.append(
                {
                    "type": game_class.get_type(),
                    "name": game_class.get_name(),
                }
            )

        await client.send({"type": "update_options_lists", "games": games})

    def _show_main_menu(self, user: NetworkUser, *, reset_history: bool = False) -> None:
        """Show the main menu to a user."""
        if reset_history:
            # Fresh navigation tree (used when returning from active game flows).
            current_menus = getattr(user, "_current_menus", None)
            if isinstance(current_menus, dict):
                for menu_id in list(current_menus.keys()):
                    if menu_id != "main_menu":
                        current_menus.pop(menu_id, None)

        items = []
        if user.approved:
            # Full menu for approved users
            items = [
                MenuItem(text=Localization.get(user.locale, "play"), id="play"),
                MenuItem(
                    text=Localization.get(user.locale, "view-active-tables"),
                    id="active_tables",
                ),
                MenuItem(text=Localization.get(user.locale, "saved-tables"), id="saved_tables"),
                MenuItem(text=Localization.get(user.locale, "leaderboards"), id="leaderboards"),
                MenuItem(text=Localization.get(user.locale, "my-stats"), id="my_stats"),
                MenuItem(text=Localization.get(user.locale, "options"), id="options"),
                MenuItem(
                    text=Localization.get(user.locale, "documents-menu-title"), id="documents"
                ),
            ]
            # Add administration menu for admins
            if user.trust_level.value >= TrustLevel.ADMIN.value:
                items.append(
                    MenuItem(
                        text=Localization.get(user.locale, "administration"), id="administration"
                    )
                )
        else:
            # Limited menu for users waiting for approval
            items = [
                MenuItem(text=Localization.get(user.locale, "leaderboards"), id="leaderboards"),
                MenuItem(text=Localization.get(user.locale, "options"), id="options"),
                MenuItem(
                    text=Localization.get(user.locale, "documents-menu-title"), id="documents"
                ),
            ]
        items.append(MenuItem(text=Localization.get(user.locale, "logout"), id="logout"))
        user.show_menu(
            "main_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=1 if reset_history else None,
        )
        user.play_music("mainmus.ogg")
        user.stop_ambience()
        self._user_states[user.username] = {"menu": "main_menu"}

    def _show_categories_menu(self, user: NetworkUser) -> None:
        """Show game categories menu."""
        categories = GameRegistry.get_by_category()
        items = []
        for category_key in sorted(categories.keys()):
            category_name = Localization.get(user.locale, category_key)
            game_count = len(categories.get(category_key, []))
            items.append(
                MenuItem(
                    text=f"{category_name} ({game_count})",
                    id=f"category_{category_key}",
                )
            )
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "categories_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "categories_menu"}

    def _show_games_menu(self, user: NetworkUser, category: str) -> None:
        """Show games in a category."""
        categories = GameRegistry.get_by_category()
        games = categories.get(category, [])

        items = []
        for game_class in games:
            game_name = Localization.get(user.locale, game_class.get_name_key())
            items.append(MenuItem(text=game_name, id=f"game_{game_class.get_type()}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "games_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "games_menu", "category": category}

    def _show_tables_menu(self, user: NetworkUser, game_type: str) -> None:
        """Show available tables for a game."""
        tables = self._tables.get_waiting_tables(game_type)
        game_class = get_game_class(game_type)
        game_name = (
            Localization.get(user.locale, game_class.get_name_key()) if game_class else game_type
        )

        items = [MenuItem(text=Localization.get(user.locale, "create-table"), id="create_table")]

        for table in tables:
            member_count = len(table.members)
            member_names = [
                member.username for member in table.members if member.username != table.host
            ]
            members_str = Localization.format_list_and(user.locale, member_names)
            if member_count == 1:
                listing_key = "table-listing-one"
            elif member_names:
                listing_key = "table-listing-with"
            else:
                listing_key = "table-listing"
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        listing_key,
                        host=table.host,
                        count=member_count,
                        members=members_str,
                    ),
                    id=f"table_{table.table_id}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "tables_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "tables_menu",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_active_tables_menu(self, user: NetworkUser) -> bool:
        """Show available tables across all games.

        Returns True if the menu was shown, False if there was nothing to show.
        """
        tables = self._tables.get_waiting_tables()
        if not tables:
            user.speak_l("no-active-tables")
            return False
        items: list[MenuItem] = []
        for table in tables:
            game_class = get_game_class(table.game_type)
            game_name = (
                Localization.get(user.locale, game_class.get_name_key())
                if game_class
                else table.game_type
            )
            member_count = len(table.members)
            member_names = [
                member.username for member in table.members if member.username != table.host
            ]
            members_str = Localization.format_list_and(user.locale, member_names)
            if member_count == 1:
                listing_key = "table-listing-game-one"
            elif member_names:
                listing_key = "table-listing-game-with"
            else:
                listing_key = "table-listing-game"
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        listing_key,
                        game=game_name,
                        host=table.host,
                        count=member_count,
                        members=members_str,
                    ),
                    id=f"table_{table.table_id}",
                )
            )
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "active_tables_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "active_tables_menu"}
        return True

    # Dice keeping style display names (legacy, kept for any external refs)
    DICE_KEEPING_STYLES = {
        DiceKeepingStyle.PLAYPALACE: "dice-keeping-style-indexes",
        DiceKeepingStyle.QUENTIN_C: "dice-keeping-style-values",
    }

    def _show_options_menu(self, user: NetworkUser) -> None:
        """Show top-level options menu: language, fluent langs, then pref categories."""
        if self._is_localization_warmup_active():
            lang_key = f"language-{user.locale}"
            current_lang = Localization.get(user.locale, lang_key)
            if current_lang == lang_key:
                current_lang = user.locale
        else:
            languages = Localization.get_available_languages(user.locale, fallback=user.locale)
            current_lang = languages.get(user.locale, user.locale)

        items = [
            MenuItem(
                text=Localization.get(user.locale, "language-option", language=current_lang),
                id="language",
            ),
            MenuItem(
                text=Localization.get(
                    user.locale,
                    "fluent-languages-option",
                    count=len(user.fluent_languages),
                ),
                id="fluent_languages",
            ),
        ]

        # Add preference categories
        for cat_key, cat_fluent in PREF_CATEGORIES:
            cat_name = Localization.get(user.locale, cat_fluent)
            items.append(MenuItem(text=cat_name, id=f"pref_cat_{cat_key}"))

        # Reset all
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "pref-reset-all"),
                id="pref_reset_all",
            )
        )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "options_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        user.play_music("settingsmus.ogg")
        self._user_states[user.username] = {"menu": "options_menu"}

    def _show_pref_category_menu(
        self, user: NetworkUser, category: str, *, refresh: bool = False
    ) -> None:
        """Show preferences within a category.

        Args:
            refresh: If True, send a lightweight items-only update instead of
                a full menu rebuild.  Used after toggling a value so screen
                readers don't re-read the entire menu.
        """
        prefs = user.preferences
        pref_fields = UserPreferences.get_fields_for_category(category)

        items: list[MenuItem] = []
        for name, meta in pref_fields:
            label = self._get_pref_label(user.locale, prefs, name, meta)
            items.append(MenuItem(text=label, id=f"pref_{name}"))

        # Reset category
        cat_name = ""
        for cat_key, cat_fluent in PREF_CATEGORIES:
            if cat_key == category:
                cat_name = Localization.get(user.locale, cat_fluent)
                break
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "pref-reset-category", category=cat_name),
                id=f"pref_reset_cat_{category}",
            )
        )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        if refresh:
            user.update_menu("pref_category_menu", items)
        else:
            user.show_menu(
                "pref_category_menu",
                items,
                multiletter=True,
                escape_behavior=EscapeBehavior.SELECT_LAST,
            )
            user.play_music("settingsmus.ogg")
            self._user_states[user.username] = {
                "menu": "pref_category_menu",
                "pref_category": category,
            }

    def _show_pref_detail_menu(
        self, user: NetworkUser, field_name: str, *, refresh: bool = False
    ) -> None:
        """Show detail menu for a pref with per-game overrides.

        Layout:
            Default: <global value>  (toggle/choose)
            Farkle: Default          (toggle/choose with Default option)
            Yahtzee: On
            ...
            Back

        Args:
            refresh: If True, send a lightweight items-only update instead of
                a full menu rebuild.
        """
        meta = UserPreferences.get_pref_meta(field_name)
        if not meta:
            return

        prefs = user.preferences
        global_value = getattr(prefs, field_name)

        items: list[MenuItem] = []

        # Global default line
        global_display = self._format_pref_value(user.locale, meta, global_value)
        default_label = Localization.get(
            user.locale,
            "pref-per-game-for",
            game=Localization.get(user.locale, "pref-default"),
            value=global_display,
        )
        items.append(MenuItem(text=default_label, id="detail_global"))

        # Per-game lines
        relevant_games = GameRegistry.get_games_for_preference(field_name)
        if relevant_games:
            for game_type in relevant_games:
                game_cls = GameRegistry.get(game_type)
                if not game_cls:
                    continue
                game_name = Localization.get(user.locale, game_cls.get_name_key())

                if prefs.has_game_override(field_name, game_type):
                    raw = prefs.get_game_override(field_name, game_type)
                    value_text = self._format_pref_value(user.locale, meta, raw)
                else:
                    value_text = Localization.get(user.locale, "pref-default")

                label = Localization.get(
                    user.locale,
                    "pref-per-game-for",
                    game=game_name,
                    value=value_text,
                )
                items.append(MenuItem(text=label, id=f"detail_game_{game_type}"))

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        if refresh:
            user.update_menu("pref_detail_menu", items)
        else:
            user.show_menu(
                "pref_detail_menu",
                items,
                multiletter=True,
                escape_behavior=EscapeBehavior.SELECT_LAST,
            )
            user.play_music("settingsmus.ogg")
            self._user_states[user.username] = {
                "menu": "pref_detail_menu",
                "pref_field": field_name,
                "pref_category": meta.category,
            }

    def _show_pref_menu_choices(
        self, user: NetworkUser, field_name: str, game_type: str | None = None
    ) -> None:
        """Show menu choices for a menu-type preference.

        If game_type is set, shows choices for a per-game override
        (with an extra Default option at the top).
        """
        prefs = user.preferences
        meta = UserPreferences.get_pref_meta(field_name)
        if not meta or not meta.choices:
            return

        items: list[MenuItem] = []
        selected_position = 1

        if game_type:
            # Per-game: current override or None
            current_override = prefs.get_game_override(field_name, game_type)
            current_raw = str(current_override) if current_override is not None else None

            # Default option
            is_default = current_override is None
            prefix = "* " if is_default else ""
            items.append(
                MenuItem(
                    text=f"{prefix}{Localization.get(user.locale, 'pref-default')}",
                    id="choice_default",
                )
            )
            if is_default:
                selected_position = 1

            for index, (value, fluent_key) in enumerate(meta.choices, start=2):
                is_selected = current_raw == value
                prefix = "* " if is_selected else ""
                choice_name = Localization.get(user.locale, fluent_key)
                items.append(MenuItem(text=f"{prefix}{choice_name}", id=f"choice_{value}"))
                if is_selected:
                    selected_position = index
        else:
            # Global
            current_value = getattr(prefs, field_name)
            if isinstance(current_value, Enum):
                current_value = current_value.value

            for index, (value, fluent_key) in enumerate(meta.choices, start=1):
                prefix = "* " if value == current_value else ""
                choice_name = Localization.get(user.locale, fluent_key)
                items.append(MenuItem(text=f"{prefix}{choice_name}", id=f"choice_{value}"))
                if value == current_value:
                    selected_position = index

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "pref_choices_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=selected_position,
        )
        user.play_music("settingsmus.ogg")
        self._user_states[user.username] = {
            "menu": "pref_choices_menu",
            "pref_field": field_name,
            "pref_category": meta.category,
            "pref_game_type": game_type,
        }

    # ------------------------------------------------------------------
    # Preference display helpers
    # ------------------------------------------------------------------

    def _get_pref_label(
        self, locale: str, prefs: UserPreferences, name: str, meta: PrefMeta
    ) -> str:
        """Generate the localized label for a preference field."""
        value = getattr(prefs, name)
        if meta.kind == "bool":
            status = Localization.get(locale, "option-on" if value else "option-off")
            return Localization.get(locale, meta.label, status=status)
        elif meta.kind == "menu" and meta.choices:
            raw = value.value if isinstance(value, Enum) else value
            for choice_val, fluent_key in meta.choices:
                if choice_val == raw:
                    choice_text = Localization.get(locale, fluent_key)
                    return Localization.get(locale, meta.label, choice=choice_text)
            return Localization.get(locale, meta.label, choice=str(raw))
        return str(value)

    def _format_pref_value(self, locale: str, meta: PrefMeta, raw: Any) -> str:
        """Format a raw preference value for display."""
        if meta.kind == "bool":
            return Localization.get(locale, "option-on" if raw else "option-off")
        elif meta.kind == "menu" and meta.choices:
            val_str = raw.value if isinstance(raw, Enum) else str(raw)
            for choice_val, fluent_key in meta.choices:
                if choice_val == val_str:
                    return Localization.get(locale, fluent_key)
            return str(raw)
        return str(raw)

    async def _apply_locale_change(self, user: NetworkUser, lang_code: str) -> None:
        """Apply a locale change from the language menu."""
        if self._is_localization_warmup_active():
            self._notify_localization_in_progress(user)
            self._show_options_menu(user)
            return
        languages = Localization.get_available_languages(fallback=user.locale)
        if lang_code in languages:
            user.set_locale(lang_code)
            self._db.update_user_locale(user.username, lang_code)
            user.speak_l("language-changed", language=languages[lang_code])
        self._show_options_menu(user)

    async def _handle_language_menu_dispatch(self, user: NetworkUser, selection_id: str) -> None:
        """Thin wrapper that delegates to the common language menu handler."""
        from server.core.ui.common_flows import handle_language_menu_selection

        await handle_language_menu_selection(user, selection_id)

    def _show_saved_tables_menu(self, user: NetworkUser) -> bool:
        """Show saved tables menu.

        Returns True if the menu was shown, False if there was nothing to show.
        """
        saved = self._db.get_user_saved_tables(user.username)

        if not saved:
            user.speak_l("no-saved-tables")
            return False

        items = []
        for record in saved:
            items.append(MenuItem(text=record.save_name, id=f"saved_{record.id}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "saved_tables_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "saved_tables_menu"}
        return True

    def _show_saved_table_actions_menu(self, user: NetworkUser, save_id: int) -> None:
        """Show actions for a saved table (restore, delete)."""
        items = [
            MenuItem(text=Localization.get(user.locale, "restore-table"), id="restore"),
            MenuItem(text=Localization.get(user.locale, "delete-saved-table"), id="delete"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ]
        user.show_menu(
            "saved_table_actions_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "saved_table_actions_menu",
            "save_id": save_id,
        }

    async def _handle_menu(self, client: ClientConnection, packet: dict) -> None:
        """Handle menu selection packets.

        Args:
            client: Client connection.
            packet: Incoming menu payload.
        """
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        if not user:
            return

        selection_id = packet.get("selection_id", "")

        state = self._user_states.get(username, {})
        current_menu = state.get("menu")
        self._remember_menu_position(user, current_menu, packet)

        # Check if user is in a table - delegate all events to game
        table = self._tables.find_user_table(username)
        if table and table.game:
            player = table.game.get_player_by_id(user.uuid)
            if player:
                table.game.handle_event(player, packet)
                # Check if player left the game (user replaced by bot or removed)
                game_user = table.game._users.get(user.uuid)
                if game_user is not user:
                    table.remove_member(username)
                    self._show_main_menu(user, reset_history=True)
            return

        await self._dispatch_menu_selection(user, selection_id, state, current_menu)
        self._prune_menu_history_after_dispatch(
            user=user,
            previous_menu=current_menu,
            selection_id=selection_id,
            previous_state=state,
        )

    def _prune_menu_history_after_dispatch(
        self,
        *,
        user: NetworkUser,
        previous_menu: str | None,
        selection_id: str,
        previous_state: dict,
    ) -> None:
        """Prune menu history for back-style navigation.

        Keeps position memory scoped to the current navigation path by dropping
        menus that were exited with a back action.
        """
        if not previous_menu:
            return
        new_state = self._user_states.get(user.username, {})
        new_menu = new_state.get("menu")
        if new_menu == previous_menu:
            return
        if selection_id != "back" and previous_menu != "online_users":
            return
        current_menus = getattr(user, "_current_menus", None)
        if isinstance(current_menus, dict):
            current_menus.pop(previous_menu, None)

    def _remember_menu_position(
        self, user: NetworkUser, current_menu: str | None, packet: dict
    ) -> None:
        """Store the user's last selected position for the active menu."""
        if not current_menu:
            return
        current_menus = getattr(user, "_current_menus", {})
        menu_state = current_menus.get(current_menu)
        if not menu_state:
            return

        selection = packet.get("selection")
        if isinstance(selection, int) and selection > 0:
            menu_state["position"] = selection
            return

        selection_id = packet.get("selection_id")
        if not selection_id:
            return
        items = menu_state.get("items", [])
        for index, item in enumerate(items, start=1):
            if isinstance(item, dict) and item.get("id") == selection_id:
                menu_state["position"] = index
                return

    async def _dispatch_menu_selection(
        self,
        user: NetworkUser,
        selection_id: str,
        state: dict,
        current_menu: str | None,
    ) -> None:
        """Dispatch menu selections based on current menu context."""
        handlers: dict[str, tuple[callable, tuple]] = {
            "main_menu": (self._handle_main_menu_selection, (user, selection_id)),
            "logout_confirm_menu": (self._handle_logout_confirm_selection, (user, selection_id)),
            "categories_menu": (self._handle_categories_selection, (user, selection_id, state)),
            "games_menu": (self._handle_games_selection, (user, selection_id, state)),
            "tables_menu": (self._handle_tables_selection, (user, selection_id, state)),
            "active_tables_menu": (self._handle_active_tables_selection, (user, selection_id)),
            "join_menu": (self._handle_join_selection, (user, selection_id, state)),
            "options_menu": (self._handle_options_selection, (user, selection_id)),
            "language_menu": (self._handle_language_menu_dispatch, (user, selection_id)),
            "dice_keeping_style_menu": (
                self._handle_dice_keeping_style_selection,
                (user, selection_id),
            ),
            "pref_category_menu": (self._handle_pref_category_selection, (user, selection_id)),
            "pref_detail_menu": (self._handle_pref_detail_selection, (user, selection_id)),
            "pref_choices_menu": (self._handle_pref_choices_selection, (user, selection_id)),
            "saved_tables_menu": (self._handle_saved_tables_selection, (user, selection_id, state)),
            "saved_table_actions_menu": (
                self._handle_saved_table_actions_selection,
                (user, selection_id, state),
            ),
            "leaderboards_menu": (self._handle_leaderboards_selection, (user, selection_id, state)),
            "leaderboard_types_menu": (
                self._handle_leaderboard_types_selection,
                (user, selection_id, state),
            ),
            "game_leaderboard": (
                self._handle_game_leaderboard_selection,
                (user, selection_id, state),
            ),
            "my_stats_menu": (self._handle_my_stats_selection, (user, selection_id, state)),
            "my_game_stats": (self._handle_my_game_stats_selection, (user, selection_id, state)),
            **self._get_document_menu_handlers(user, selection_id, state),
            "online_users": (self._restore_previous_menu, (user, state)),
            "admin_menu": (self._handle_admin_menu_selection, (user, selection_id)),
            "account_approval_menu": (
                self._handle_account_approval_selection,
                (user, selection_id),
            ),
            "pending_user_actions_menu": (
                self._handle_pending_user_actions_selection,
                (user, selection_id, state),
            ),
            "promote_admin_menu": (self._handle_promote_admin_selection, (user, selection_id)),
            "demote_admin_menu": (self._handle_demote_admin_selection, (user, selection_id)),
            "promote_confirm_menu": (
                self._handle_promote_confirm_selection,
                (user, selection_id, state),
            ),
            "demote_confirm_menu": (
                self._handle_demote_confirm_selection,
                (user, selection_id, state),
            ),
            "broadcast_choice_menu": (
                self._handle_broadcast_choice_selection,
                (user, selection_id, state),
            ),
            "transfer_ownership_menu": (
                self._handle_transfer_ownership_selection,
                (user, selection_id),
            ),
            "transfer_ownership_confirm_menu": (
                self._handle_transfer_ownership_confirm_selection,
                (user, selection_id, state),
            ),
            "transfer_broadcast_choice_menu": (
                self._handle_transfer_broadcast_choice_selection,
                (user, selection_id, state),
            ),
            "ban_user_menu": (self._handle_ban_user_selection, (user, selection_id)),
            "unban_user_menu": (self._handle_unban_user_selection, (user, selection_id)),
            "ban_confirm_menu": (self._handle_ban_confirm_selection, (user, selection_id, state)),
            "unban_confirm_menu": (
                self._handle_unban_confirm_selection,
                (user, selection_id, state),
            ),
            "virtual_bots_menu": (self._handle_virtual_bots_selection, (user, selection_id)),
            "virtual_bots_clear_confirm_menu": (
                self._handle_virtual_bots_clear_confirm_selection,
                (user, selection_id),
            ),
        }
        if not current_menu:
            return
        handler_entry = handlers.get(current_menu)
        if not handler_entry:
            return
        func, args = handler_entry
        result = func(*args)
        if asyncio.iscoroutine(result):
            await result

    def _ensure_user_approved(self, user: NetworkUser) -> bool:
        """Return True if user is approved or admin/server owner; otherwise show approval notice."""
        if user.approved:
            return True
        if user.trust_level.value >= TrustLevel.ADMIN.value:
            return True
        user.speak_l("waiting-for-approval", buffer="activity")
        self._show_main_menu(user)
        return False

    async def _handle_main_menu_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle main menu selections.

        Args:
            user: Acting user.
            selection_id: Selected menu item id.
        """
        if selection_id == "play":
            if not self._ensure_user_approved(user):
                return
            self._show_categories_menu(user)
        elif selection_id == "active_tables":
            if not self._ensure_user_approved(user):
                return
            if not self._show_active_tables_menu(user):
                return  # No tables — user stays on main menu
        elif selection_id == "saved_tables":
            if not self._ensure_user_approved(user):
                return
            if not self._show_saved_tables_menu(user):
                return  # No saved tables — user stays on main menu
        elif selection_id == "leaderboards":
            if not self._ensure_user_approved(user):
                return
            self._show_leaderboards_menu(user)
        elif selection_id == "my_stats":
            if not self._ensure_user_approved(user):
                return
            if not self._show_my_stats_menu(user):
                return  # No stats — user stays on main menu
        elif selection_id == "documents":
            self._show_documents_menu(user)
        elif selection_id == "options":
            self._show_options_menu(user)
        elif selection_id == "administration":
            if user.trust_level.value >= TrustLevel.ADMIN.value:
                self._show_admin_menu(user)
        elif selection_id == "logout":
            self._show_logout_confirm_menu(user)

    def _show_logout_confirm_menu(self, user: NetworkUser) -> None:
        """Show confirmation menu for logging out."""
        question = Localization.get(user.locale, "confirm-logout")
        show_yes_no_menu(user, "logout_confirm_menu", question)
        self._user_states[user.username] = {"menu": "logout_confirm_menu"}

    async def _handle_logout_confirm_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle logout confirmation menu selection."""
        if selection_id == "yes":
            user.speak_l("goodbye", buffer="activity")
            await user.connection.send({"type": "disconnect", "reconnect": False})
        else:
            self._show_main_menu(user)

    async def _handle_options_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle top-level options menu selections."""
        if selection_id == "language":
            from server.core.ui.common_flows import show_language_menu

            if show_language_menu(
                user,
                include_native_names=True,
                on_select=self._apply_locale_change,
                on_back=lambda u: self._show_options_menu(u),
            ):
                self._user_states[user.username] = {"menu": "language_menu"}
        elif selection_id == "fluent_languages":
            self._show_fluent_languages_menu(user)
        elif selection_id.startswith("pref_cat_"):
            category = selection_id[9:]  # Remove "pref_cat_"
            self._show_pref_category_menu(user, category)
        elif selection_id == "pref_reset_all":
            user.preferences.reset_all()
            self._save_user_preferences(user)
            user.speak_l("pref-reset-done")
            self._show_options_menu(user)
        elif selection_id == "back":
            self._show_main_menu(user)

    def _show_fluent_languages_menu(self, user: NetworkUser) -> None:
        """Show fluent languages toggle menu."""
        if self._is_localization_warmup_active():
            self._notify_localization_in_progress(user)
            return

        from server.core.ui.common_flows import show_language_menu

        original = list(user.fluent_languages)

        def on_done(u: NetworkUser, selected: set[str]) -> None:
            u.fluent_languages[:] = list(selected)
            self._db.set_user_fluent_languages(u.username, u.fluent_languages)
            self._show_options_menu(u)

        def on_cancel(u: NetworkUser) -> None:
            u.fluent_languages[:] = original
            self._show_options_menu(u)

        if show_language_menu(
            user,
            highlight_active_locale=False,
            multi_select=True,
            selected=set(user.fluent_languages),
            on_done=on_done,
            on_cancel=on_cancel,
        ):
            self._user_states[user.username] = {"menu": "language_menu"}

    def _show_dice_keeping_style_menu(self, user: NetworkUser) -> None:
        """Show dice keeping style selection menu."""
        items = []
        current_style = user.preferences.dice_keeping_style
        selected_position = 1
        for index, (style, name_key) in enumerate(self.DICE_KEEPING_STYLES.items(), start=1):
            prefix = "* " if style == current_style else ""
            name = Localization.get(user.locale, name_key)
            items.append(MenuItem(text=f"{prefix}{name}", id=f"style_{style.value}"))
            if style == current_style:
                selected_position = index
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        user.show_menu(
            "dice_keeping_style_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=selected_position,
        )
        user.play_music("settingsmus.ogg")
        self._user_states[user.username] = {"menu": "dice_keeping_style_menu"}

    async def _handle_dice_keeping_style_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle dice keeping style selection.

        Args:
            user: Acting user.
            selection_id: Selected menu item id.
        """
        if selection_id.startswith("style_"):
            style_value = selection_id[6:]  # Remove "style_" prefix
            style = DiceKeepingStyle.from_str(style_value)
            user.preferences.dice_keeping_style = style
            self._save_user_preferences(user)
            style_key = self.DICE_KEEPING_STYLES.get(style, "dice-keeping-style-indexes")
            style_name = Localization.get(user.locale, style_key)
            user.speak_l("dice-keeping-style-changed", style=style_name)
            self._show_options_menu(user)
            return
        # Back or invalid
        self._show_options_menu(user)

    # ------------------------------------------------------------------
    # Declarative preference handlers
    # ------------------------------------------------------------------

    async def _handle_pref_category_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle selections within a preference category menu."""
        state = self._user_states.get(user.username, {})
        category = state.get("pref_category", "")

        if selection_id.startswith("pref_") and not selection_id.startswith("pref_reset_"):
            field_name = selection_id[5:]  # Remove "pref_"
            meta = UserPreferences.get_pref_meta(field_name)
            if not meta:
                return
            if GameRegistry.get_games_for_preference(field_name):
                # Has per-game overrides — open detail submenu
                self._show_pref_detail_menu(user, field_name)
            elif meta.kind == "bool":
                # Simple global toggle
                prefs = user.preferences
                new_val = not getattr(prefs, field_name)
                setattr(prefs, field_name, new_val)
                user.play_sound("checkbox_list_on.wav" if new_val else "checkbox_list_off.wav")
                self._save_user_preferences(user)
                self._show_pref_category_menu(user, category, refresh=True)
            elif meta.kind == "menu":
                # Global menu choice
                self._show_pref_menu_choices(user, field_name)
        elif selection_id.startswith("pref_reset_cat_"):
            cat = selection_id[15:]  # Remove "pref_reset_cat_"
            user.preferences.reset_category(cat)
            self._save_user_preferences(user)
            user.speak_l("pref-reset-done")
            self._show_pref_category_menu(user, cat, refresh=True)
        elif selection_id == "back":
            self._show_options_menu(user)

    async def _handle_pref_detail_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle selections in the pref detail menu (global + per-game lines)."""
        state = self._user_states.get(user.username, {})
        field_name = state.get("pref_field", "")
        category = state.get("pref_category", "")
        meta = UserPreferences.get_pref_meta(field_name)
        if not meta:
            return

        if selection_id == "detail_global":
            # Toggle/choose the global value
            if meta.kind == "bool":
                prefs = user.preferences
                new_val = not getattr(prefs, field_name)
                setattr(prefs, field_name, new_val)
                user.play_sound("checkbox_list_on.wav" if new_val else "checkbox_list_off.wav")
                self._save_user_preferences(user)
                self._show_pref_detail_menu(user, field_name, refresh=True)
            elif meta.kind == "menu":
                self._show_pref_menu_choices(user, field_name)
        elif selection_id.startswith("detail_game_"):
            game_type = selection_id[12:]  # Remove "detail_game_"
            if meta.kind == "bool":
                # Cycle: Default → On → Off → Default
                prefs = user.preferences
                current = prefs.get_game_override(field_name, game_type)
                if current is None:
                    prefs.set_game_override(field_name, game_type, True)
                    user.play_sound("checkbox_list_on.wav")
                elif current is True:
                    prefs.set_game_override(field_name, game_type, False)
                    user.play_sound("checkbox_list_off.wav")
                else:
                    prefs.clear_game_override(field_name, game_type)
                    user.play_sound("checkbox_list_off.wav")
                self._save_user_preferences(user)
                self._show_pref_detail_menu(user, field_name, refresh=True)
            elif meta.kind == "menu":
                self._show_pref_menu_choices(user, field_name, game_type=game_type)
        elif selection_id == "back":
            self._show_pref_category_menu(user, category)

    async def _handle_pref_choices_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle menu choice selection for a preference."""
        state = self._user_states.get(user.username, {})
        field_name = state.get("pref_field", "")
        category = state.get("pref_category", "")
        game_type = state.get("pref_game_type")
        meta = UserPreferences.get_pref_meta(field_name)

        if selection_id.startswith("choice_") and meta:
            value_str = selection_id[7:]  # Remove "choice_"

            if game_type:
                # Per-game override
                if value_str == "default":
                    user.preferences.clear_game_override(field_name, game_type)
                else:
                    user.preferences.set_game_override(field_name, game_type, value_str)
                self._save_user_preferences(user)
                self._show_pref_detail_menu(user, field_name)
            else:
                # Global value
                prefs = user.preferences
                if meta.enum_class:
                    try:
                        new_val = meta.enum_class(value_str)
                    except (ValueError, KeyError):
                        new_val = meta.default
                else:
                    new_val = value_str
                setattr(prefs, field_name, new_val)
                self._save_user_preferences(user)

                display = self._format_pref_value(user.locale, meta, new_val)
                user.speak_l(meta.change_msg, choice=display)
                # Return to detail menu if it has per-game, otherwise category
                if GameRegistry.get_games_for_preference(field_name):
                    self._show_pref_detail_menu(user, field_name)
                else:
                    self._show_pref_category_menu(user, category)
        elif selection_id == "back":
            if meta and GameRegistry.get_games_for_preference(field_name):
                self._show_pref_detail_menu(user, field_name)
            else:
                self._show_pref_category_menu(user, category)

    def _save_user_preferences(self, user: NetworkUser) -> None:
        """Save user preferences to database."""
        prefs_json = json.dumps(user.preferences.to_dict())
        self._db.update_user_preferences(user.username, prefs_json)

    async def _handle_categories_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle category selection.

        Args:
            user: Acting user.
            selection_id: Selected category id.
            state: Current menu state.
        """
        if selection_id.startswith("category_"):
            category = selection_id[9:]  # Remove "category_" prefix
            self._show_games_menu(user, category)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_games_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle game selection.

        Args:
            user: Acting user.
            selection_id: Selected game id.
            state: Current menu state.
        """
        if selection_id.startswith("game_"):
            game_type = selection_id[5:]  # Remove "game_" prefix
            self._show_tables_menu(user, game_type)
        elif selection_id == "back":
            self._show_categories_menu(user)

    async def _handle_tables_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle tables menu selection.

        Args:
            user: Acting user.
            selection_id: Selected table id or action.
            state: Current menu state.
        """
        game_type = state.get("game_type", "")

        if selection_id == "create_table":
            table = self._tables.create_table(game_type, user.username, user)

            # Create game immediately and initialize lobby
            game_class = get_game_class(game_type)
            if game_class:
                game = game_class()
                table.game = game
                game._table = table  # Enable game to call table.destroy()
                game.initialize_lobby(user.username, user)

                # Broadcast table creation to all users
                self._broadcast_table_created(user.username, game_type)

                min_players = game_class.get_min_players()
                max_players = game_class.get_max_players()
                user.speak_l(
                    "waiting-for-players",
                    current=len(game.players),
                    min=min_players,
                    max=max_players,
                    buffer="table",
                )
            self._user_states[user.username] = {
                "menu": "in_game",
                "table_id": table.table_id,
            }

        elif selection_id.startswith("table_"):
            table_id = selection_id[6:]  # Remove "table_" prefix
            table = self._tables.get_table(table_id)
            if table:
                self._auto_join_table(user, table, game_type)
            else:
                user.speak_l("table-not-exists")
                self._show_tables_menu(user, game_type)

        elif selection_id == "back":
            category = None
            for cat, games in GameRegistry.get_by_category().items():
                if any(g.get_type() == game_type for g in games):
                    category = cat
                    break
            if category:
                self._show_games_menu(user, category)
            else:
                self._show_categories_menu(user)

    async def _handle_active_tables_selection(self, user: NetworkUser, selection_id: str) -> None:
        """Handle active tables menu selection.

        Args:
            user: Acting user.
            selection_id: Selected table id or action.
        """
        if selection_id.startswith("table_"):
            table_id = selection_id[6:]
            table = self._tables.get_table(table_id)
            if table:
                self._auto_join_table(user, table, table.game_type)
            else:
                user.speak_l("table-not-exists")
                if not self._show_active_tables_menu(user):
                    self._show_main_menu(user)
        elif selection_id == "back":
            self._show_main_menu(user)

    def _auto_join_table(self, user: NetworkUser, table: "Table", game_type: str) -> None:
        """Automatically join a table as player or spectator.

        Joins as player if:
            - Game has not started yet (status is "waiting").
            - Game has room for more players (less than max_players).
        Otherwise joins as spectator.

        Args:
            user: User joining the table.
            table: Table to join.
            game_type: Game type identifier.
        """
        game = table.game
        if not game:
            user.speak_l("table-not-exists")
            self._show_tables_menu(user, game_type)
            return

        table_id = table.table_id

        # Determine if user can join as player
        can_join_as_player = (
            game.status != "playing"
            and sum(1 for p in game.players if not p.is_spectator) < game.get_max_players()
        )

        if can_join_as_player:
            # Join as player
            table.add_member(user.username, user, as_spectator=False)
            game.add_player(user.username, user)
            game.broadcast_l("table-joined", player=user.username)
            game.broadcast_sound("join.ogg")
            game.rebuild_all_menus()
        else:
            # Join as spectator
            table.add_member(user.username, user, as_spectator=True)
            game.add_spectator(user.username, user)
            user.speak_l("spectator-joined", host=table.host)
            game.broadcast_l("now-spectating", player=user.username)
            game.broadcast_sound("join_spectator.ogg")
            game.rebuild_all_menus()

        self._user_states[user.username] = {"menu": "in_game", "table_id": table_id}

    def _return_from_join_menu(self, user: NetworkUser, state: dict) -> None:
        """Return to the appropriate tables menu after join."""
        if state.get("return_menu") == "active_tables_menu":
            if not self._show_active_tables_menu(user):
                self._show_main_menu(user)
        else:
            self._show_tables_menu(user, state.get("game_type", ""))

    async def _handle_join_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle join menu selection.

        Args:
            user: Acting user.
            selection_id: Selected join option.
            state: Current menu state.
        """
        table_id = state.get("table_id")
        table = self._tables.get_table(table_id)

        if not table or not table.game:
            user.speak_l("table-not-exists")
            self._return_from_join_menu(user, state)
            return

        game = table.game

        if selection_id == "join_player":
            # Check if game is already in progress
            if game.status == "playing":
                # Look for a player with matching UUID that is now a bot
                matching_player = None
                for p in game.players:
                    if p.id == user.uuid and p.is_bot:
                        matching_player = p
                        break

                if matching_player:
                    # Take over from the bot
                    matching_player.is_bot = False
                    game.attach_user(matching_player.id, user)
                    table.add_member(user.username, user, as_spectator=False)
                    game.broadcast_l("player-took-over", player=user.username)
                    game.broadcast_sound("join.ogg")
                    game.rebuild_all_menus()
                    self._user_states[user.username] = {
                        "menu": "in_game",
                        "table_id": table_id,
                    }
                    return
                else:
                    # No matching player - join as spectator instead
                    table.add_member(user.username, user, as_spectator=True)
                    game.add_spectator(user.username, user)
                    user.speak_l("spectator-joined", host=table.host)
                    game.broadcast_l("now-spectating", player=user.username)
                    game.broadcast_sound("join_spectator.ogg")
                    game.rebuild_all_menus()
                    self._user_states[user.username] = {
                        "menu": "in_game",
                        "table_id": table_id,
                    }
                    return

            active_count = sum(1 for p in game.players if not p.is_spectator)
            if active_count >= game.get_max_players():
                user.speak_l("table-full")
                self._return_from_join_menu(user, state)
                return

            # Add player to game
            table.add_member(user.username, user, as_spectator=False)
            game.add_player(user.username, user)
            game.broadcast_l("table-joined", player=user.username)
            game.broadcast_sound("join.ogg")
            game.rebuild_all_menus()
            self._user_states[user.username] = {"menu": "in_game", "table_id": table_id}

        elif selection_id == "join_spectator":
            table.add_member(user.username, user, as_spectator=True)
            game.add_spectator(user.username, user)
            user.speak_l("spectator-joined", host=table.host)
            game.broadcast_l("now-spectating", player=user.username)
            game.broadcast_sound("join_spectator.ogg")
            game.rebuild_all_menus()
            self._user_states[user.username] = {"menu": "in_game", "table_id": table_id}

        elif selection_id == "back":
            self._return_from_join_menu(user, state)

    async def _handle_saved_tables_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle saved tables menu selection.

        Args:
            user: Acting user.
            selection_id: Selected saved table item.
            state: Current menu state.
        """
        if selection_id.startswith("saved_"):
            save_id = int(selection_id[6:])  # Remove "saved_" prefix
            self._show_saved_table_actions_menu(user, save_id)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_saved_table_actions_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle saved table actions (restore/delete).

        Args:
            user: Acting user.
            selection_id: Selected action id.
            state: Current menu state.
        """
        save_id = state.get("save_id")
        if not save_id:
            self._show_main_menu(user)
            return

        if selection_id == "restore":
            await self._restore_saved_table(user, save_id)
        elif selection_id == "delete":
            self._db.delete_saved_table(save_id)
            user.speak_l("saved-table-deleted")
            if not self._show_saved_tables_menu(user):
                self._show_main_menu(user)
        elif selection_id == "back":
            if not self._show_saved_tables_menu(user):
                self._show_main_menu(user)

    async def _restore_saved_table(self, user: NetworkUser, save_id: int) -> None:
        """Restore a saved table into an active table.

        Args:
            user: Acting user.
            save_id: Saved table id.
        """
        import json
        from .users.bot import Bot

        record = self._db.get_saved_table(save_id)
        if not record:
            user.speak_l("table-not-exists")
            self._show_main_menu(user)
            return

        # Get the game class
        game_class = get_game_class(record.game_type)
        if not game_class:
            user.speak_l("game-type-not-found")
            self._show_main_menu(user)
            return

        # Parse members from saved state
        members_data = json.loads(record.members_json)
        human_players = [m for m in members_data if not m.get("is_bot", False)]

        # Check all human players are available
        missing_players = []
        for member in human_players:
            member_username = member.get("username")
            if member_username not in self._users:
                missing_players.append(member_username)
            else:
                # Check they're not already in a table
                existing_table = self._tables.find_user_table(member_username)
                if existing_table:
                    missing_players.append(member_username)

        if missing_players:
            user.speak_l("missing-players", players=", ".join(missing_players))
            if not self._show_saved_tables_menu(user):
                self._show_main_menu(user)
            return

        # All players available - create table and restore game
        table = self._tables.create_table(record.game_type, user.username, user)

        # Load game from JSON and rebuild runtime state
        game = game_class.from_json(record.game_json)
        game.rebuild_runtime_state()
        table.game = game
        game._table = table  # Enable game to call table.destroy()

        # Update host to the restorer
        game.host = user.username

        # Attach users and transfer all human players
        # NOTE: We must attach users by player.id (UUID), not by username.
        # The deserialized game has player objects with their original IDs.
        for member in members_data:
            member_username = member.get("username")
            is_bot = member.get("is_bot", False)

            # Find the player object by name to get their ID
            player = game.get_player_by_name(member_username)
            if not player:
                continue

            if is_bot:
                # Recreate bot with the player's original ID
                bot_user = Bot(member_username, uuid=player.id)
                game.attach_user(player.id, bot_user)
            else:
                # Attach human user by player ID
                member_user = self._users.get(member_username)
                if member_user:
                    table.add_member(member_username, member_user, as_spectator=False)
                    game.attach_user(player.id, member_user)
                    self._user_states[member_username] = {
                        "menu": "in_game",
                        "table_id": table.table_id,
                    }

        # Setup keybinds (runtime only, not serialized)
        # Action sets are already restored from serialization
        game.setup_keybinds()

        # Rebuild menus for all players
        game.rebuild_all_menus()

        # Notify all players
        game.broadcast_l("table-restored")

        # Delete the saved table now that it's been restored
        self._db.delete_saved_table(save_id)

    def _show_leaderboards_menu(self, user: NetworkUser) -> None:
        """Show leaderboards game selection menu.

        Args:
            user: Acting user.
        """
        categories = GameRegistry.get_by_category()
        items = []

        # Add all games from all categories
        for category_key in sorted(categories.keys()):
            for game_class in categories[category_key]:
                game_name = Localization.get(user.locale, game_class.get_name_key())
                items.append(MenuItem(text=game_name, id=f"lb_{game_class.get_type()}"))

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "leaderboards_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "leaderboards_menu"}

    def _show_leaderboard_types_menu(self, user: NetworkUser, game_type: str) -> None:
        """Show leaderboard type selection menu for a game.

        Args:
            user: Acting user.
            game_type: Game type identifier.
        """
        game_class = get_game_class(game_type)
        if not game_class:
            user.speak_l("game-type-not-found")
            return

        # Check if there's any data for this game
        results = self._db.get_game_stats(game_type, limit=1)
        if not results:
            # No data - speak message and stay on game selection
            user.speak_l("leaderboard-no-data")
            return

        game_name = Localization.get(user.locale, game_class.get_name_key())

        # Available leaderboard types (common to all games)
        items = [
            MenuItem(
                text=Localization.get(user.locale, "leaderboard-type-wins"),
                id="type_wins",
            ),
            MenuItem(
                text=Localization.get(user.locale, "leaderboard-type-rating"),
                id="type_rating",
            ),
            MenuItem(
                text=Localization.get(user.locale, "leaderboard-type-total-score"),
                id="type_total_score",
            ),
            MenuItem(
                text=Localization.get(user.locale, "leaderboard-type-high-score"),
                id="type_high_score",
            ),
            MenuItem(
                text=Localization.get(user.locale, "leaderboard-type-games-played"),
                id="type_games_played",
            ),
        ]

        # Game-specific leaderboards (declared by each game class)
        for lb_config in game_class.get_leaderboard_types():
            lb_id = lb_config["id"]
            # Convert underscores to hyphens for localization key
            loc_key = f"leaderboard-type-{lb_id.replace('_', '-')}"
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, loc_key),
                    id=f"type_{lb_id}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "leaderboard_types_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "leaderboard_types_menu",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _get_game_results(self, game_type: str) -> list:
        """Get game results as GameResult objects."""
        from ..game_utils.game_result import GameResult, PlayerResult
        import json

        results = self._db.get_game_stats(game_type, limit=100)
        game_results = []

        for row in results:
            custom_data = json.loads(row[4]) if row[4] else {}
            player_rows = self._db.get_game_result_players(row[0])
            player_results = [
                PlayerResult(
                    player_id=p["player_id"],
                    player_name=p["player_name"],
                    is_bot=p["is_bot"],
                    is_virtual_bot=p.get("is_virtual_bot", False),
                )
                for p in player_rows
            ]
            game_results.append(
                GameResult(
                    game_type=row[1],
                    timestamp=row[2],
                    duration_ticks=row[3],
                    player_results=player_results,
                    custom_data=custom_data,
                )
            )

        return game_results

    def _show_wins_leaderboard(self, user: NetworkUser, game_type: str, game_name: str) -> None:
        """Show win count leaderboard for a game.

        Args:
            user: Acting user.
            game_type: Game type identifier.
            game_name: Localized game name.
        """
        from ..game_utils.stats_helpers import LeaderboardHelper

        game_results = self._get_game_results(game_type)

        # Build player stats: {player_id: {wins, losses, name}}
        player_stats: dict[str, dict] = {}
        for result in game_results:
            winner_name = result.custom_data.get("winner_name")
            for p in result.player_results:
                if p.is_bot and not p.is_virtual_bot:
                    continue
                if p.player_id not in player_stats:
                    player_stats[p.player_id] = {
                        "wins": 0,
                        "losses": 0,
                        "name": p.player_name,
                    }
                if winner_name == p.player_name:
                    player_stats[p.player_id]["wins"] += 1
                else:
                    player_stats[p.player_id]["losses"] += 1

        # Sort by wins descending
        sorted_players = sorted(player_stats.items(), key=lambda x: x[1]["wins"], reverse=True)

        items = []

        for rank, (player_id, stats) in enumerate(sorted_players[:10], 1):
            wins = stats["wins"]
            losses = stats["losses"]
            total = wins + losses
            percentage = round((wins / total * 100) if total > 0 else 0)
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "leaderboard-wins-entry",
                        rank=rank,
                        player=stats["name"],
                        wins=wins,
                        losses=losses,
                        percentage=percentage,
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_rating_leaderboard(self, user: NetworkUser, game_type: str, game_name: str) -> None:
        """Show skill rating leaderboard.

        Args:
            user: Acting user.
            game_type: Game type identifier.
            game_name: Localized game name.
        """
        from ..game_utils.stats_helpers import RatingHelper

        rating_helper = RatingHelper(self._db, game_type)
        ratings = rating_helper.get_leaderboard(limit=10)

        items = []

        if not ratings:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "leaderboard-no-ratings"),
                    id="no_data",
                )
            )
        else:
            for rank, rating in enumerate(ratings, 1):
                # Get player name from UUID - check recent game results
                player_name = rating.player_id
                # Look up name from game results
                results = self._db.get_game_stats(game_type, limit=100)
                for result in results:
                    players = self._db.get_game_result_players(result[0])
                    for p in players:
                        if p["player_id"] == rating.player_id:
                            player_name = p["player_name"]
                            break
                    if player_name != rating.player_id:
                        break

                items.append(
                    MenuItem(
                        text=Localization.get(
                            user.locale,
                            "leaderboard-rating-entry",
                            rank=rank,
                            player=player_name,
                            rating=round(rating.ordinal),
                            mu=round(rating.mu, 1),
                            sigma=round(rating.sigma, 1),
                        ),
                        id=f"entry_{rank}",
                    )
                )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_total_score_leaderboard(
        self, user: NetworkUser, game_type: str, game_name: str
    ) -> None:
        """Show total score leaderboard.

        Args:
            user: Acting user.
            game_type: Game type identifier.
            game_name: Localized game name.
        """
        from ..game_utils.stats_helpers import LeaderboardHelper

        game_results = self._get_game_results(game_type)

        # Build total scores per player
        player_scores: dict[str, dict] = {}
        for result in game_results:
            final_scores = result.custom_data.get("final_scores", {})
            for p in result.player_results:
                if p.is_bot and not p.is_virtual_bot:
                    continue
                if p.player_id not in player_scores:
                    player_scores[p.player_id] = {"total": 0, "name": p.player_name}
                # Try to get score by player name
                score = final_scores.get(p.player_name, 0)
                if score:
                    player_scores[p.player_id]["total"] += score

        # Sort by total score descending
        sorted_players = sorted(player_scores.items(), key=lambda x: x[1]["total"], reverse=True)

        items = []

        for rank, (player_id, stats) in enumerate(sorted_players[:10], 1):
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "leaderboard-score-entry",
                        rank=rank,
                        player=stats["name"],
                        value=int(stats["total"]),
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_high_score_leaderboard(
        self, user: NetworkUser, game_type: str, game_name: str
    ) -> None:
        """Show high score leaderboard.

        Args:
            user: Acting user.
            game_type: Game type identifier.
            game_name: Localized game name.
        """
        game_results = self._get_game_results(game_type)

        # Build high scores per player
        player_high: dict[str, dict] = {}
        for result in game_results:
            final_scores = result.custom_data.get("final_scores", {})
            for p in result.player_results:
                if p.is_bot and not p.is_virtual_bot:
                    continue
                score = final_scores.get(p.player_name, 0)
                if p.player_id not in player_high:
                    player_high[p.player_id] = {"high": score, "name": p.player_name}
                elif score > player_high[p.player_id]["high"]:
                    player_high[p.player_id]["high"] = score

        # Sort by high score descending
        sorted_players = sorted(player_high.items(), key=lambda x: x[1]["high"], reverse=True)

        items = []

        for rank, (player_id, stats) in enumerate(sorted_players[:10], 1):
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "leaderboard-score-entry",
                        rank=rank,
                        player=stats["name"],
                        value=int(stats["high"]),
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _show_games_played_leaderboard(
        self, user: NetworkUser, game_type: str, game_name: str
    ) -> None:
        """Show games played leaderboard.

        Args:
            user: Acting user.
            game_type: Game type identifier.
            game_name: Localized game name.
        """
        game_results = self._get_game_results(game_type)

        # Count games per player
        player_games: dict[str, dict] = {}
        for result in game_results:
            for p in result.player_results:
                if p.is_bot and not p.is_virtual_bot:
                    continue
                if p.player_id not in player_games:
                    player_games[p.player_id] = {"count": 0, "name": p.player_name}
                player_games[p.player_id]["count"] += 1

        # Sort by games played descending
        sorted_players = sorted(player_games.items(), key=lambda x: x[1]["count"], reverse=True)

        items = []

        for rank, (player_id, stats) in enumerate(sorted_players[:10], 1):
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "leaderboard-games-entry",
                        rank=rank,
                        player=stats["name"],
                        value=stats["count"],
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _extract_value_from_path(
        self, data: dict, path: str, player_id: str, player_name: str
    ) -> float | None:
        """Extract a value from custom_data using a dot-separated path.

        Supports {player_id} and {player_name} placeholders in path.
        """
        # Replace placeholders
        resolved_path = path.replace("{player_id}", player_id)
        resolved_path = resolved_path.replace("{player_name}", player_name)

        # Navigate the path
        parts = resolved_path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        # Convert to float if possible
        if isinstance(current, (int, float)):
            return float(current)
        return None

    def _show_custom_leaderboard(
        self,
        user: NetworkUser,
        game_type: str,
        game_name: str,
        config: dict,
    ) -> None:
        """Show a custom leaderboard using declarative config.

        Args:
            user: Acting user.
            game_type: Game type identifier.
            game_name: Localized game name.
            config: Leaderboard config dict from game class.
        """
        game_results = self._get_game_results(game_type)

        lb_id = config["id"]
        aggregate = config.get("aggregate", "sum")
        format_key = config.get("format", "score")
        decimals = config.get("decimals", 0)

        # Check if this is a ratio calculation or simple path
        is_ratio = "numerator" in config and "denominator" in config

        # Aggregate data per player
        player_data: dict[str, dict] = {}

        for result in game_results:
            custom_data = result.custom_data
            for p in result.player_results:
                if p.is_bot and not p.is_virtual_bot:
                    continue

                if p.player_id not in player_data:
                    player_data[p.player_id] = {
                        "name": p.player_name,
                        "values": [],
                        "numerators": [],
                        "denominators": [],
                    }

                if is_ratio:
                    num = self._extract_value_from_path(
                        custom_data, config["numerator"], p.player_id, p.player_name
                    )
                    denom = self._extract_value_from_path(
                        custom_data, config["denominator"], p.player_id, p.player_name
                    )
                    if num is not None and denom is not None:
                        player_data[p.player_id]["numerators"].append(num)
                        player_data[p.player_id]["denominators"].append(denom)
                else:
                    value = self._extract_value_from_path(
                        custom_data, config["path"], p.player_id, p.player_name
                    )
                    if value is not None:
                        player_data[p.player_id]["values"].append(value)

        # Calculate final values based on aggregate type
        player_scores: list[tuple[str, str, float]] = []

        for player_id, data in player_data.items():
            if is_ratio:
                total_num = sum(data["numerators"])
                total_denom = sum(data["denominators"])
                if total_denom > 0:
                    value = total_num / total_denom
                    player_scores.append((player_id, data["name"], value))
            else:
                values = data["values"]
                if not values:
                    continue

                if aggregate == "sum":
                    value = sum(values)
                elif aggregate == "max":
                    value = max(values)
                elif aggregate == "avg":
                    value = sum(values) / len(values)
                else:
                    value = sum(values)

                player_scores.append((player_id, data["name"], value))

        # Sort descending
        player_scores.sort(key=lambda x: x[2], reverse=True)

        # Build menu items
        items = []
        entry_key = f"leaderboard-{format_key}-entry"

        for rank, (player_id, name, value) in enumerate(player_scores[:10], 1):
            display_value = round(value, decimals) if decimals > 0 else int(value)
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        entry_key,
                        rank=rank,
                        player=name,
                        value=display_value,
                    ),
                    id=f"entry_{rank}",
                )
            )

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "game_leaderboard",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "game_leaderboard",
            "game_type": game_type,
            "game_name": game_name,
        }

    async def _handle_leaderboards_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle leaderboards menu selection.

        Args:
            user: Acting user.
            selection_id: Selected menu item id.
            state: Current menu state.
        """
        if selection_id.startswith("lb_"):
            game_type = selection_id[3:]  # Remove "lb_" prefix
            self._show_leaderboard_types_menu(user, game_type)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_leaderboard_types_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle leaderboard type selection.

        Args:
            user: Acting user.
            selection_id: Selected leaderboard type id.
            state: Current menu state.
        """
        game_type = state.get("game_type", "")
        game_name = state.get("game_name", "")

        # Built-in leaderboard types
        if selection_id == "type_wins":
            self._show_wins_leaderboard(user, game_type, game_name)
        elif selection_id == "type_rating":
            self._show_rating_leaderboard(user, game_type, game_name)
        elif selection_id == "type_total_score":
            self._show_total_score_leaderboard(user, game_type, game_name)
        elif selection_id == "type_high_score":
            self._show_high_score_leaderboard(user, game_type, game_name)
        elif selection_id == "type_games_played":
            self._show_games_played_leaderboard(user, game_type, game_name)
        elif selection_id == "back":
            self._show_leaderboards_menu(user)
        elif selection_id.startswith("type_"):
            # Custom leaderboard type - look up config from game class
            lb_id = selection_id[5:]  # Remove "type_" prefix
            game_class = get_game_class(game_type)
            if game_class:
                for config in game_class.get_leaderboard_types():
                    if config["id"] == lb_id:
                        self._show_custom_leaderboard(user, game_type, game_name, config)
                        return

    async def _handle_game_leaderboard_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle game leaderboard menu selection.

        Args:
            user: Acting user.
            selection_id: Selected menu item id.
            state: Current menu state.
        """
        if selection_id == "back":
            game_type = state.get("game_type", "")
            game_name = state.get("game_name", "")
            self._show_leaderboard_types_menu(user, game_type)
        # Other selections (entries, header) are informational only

    # =========================================================================
    # My Stats menu
    # =========================================================================

    def _show_my_stats_menu(self, user: NetworkUser) -> bool:
        """Show game selection menu for personal stats.

        Returns True if the menu was shown, False if there was nothing to show.
        """
        categories = GameRegistry.get_by_category()
        items = []

        # Add only games where the user has stats
        for category_key in sorted(categories.keys()):
            for game_class in categories[category_key]:
                game_type = game_class.get_type()
                # Check if user has played this game
                game_results = self._get_game_results(game_type)
                has_stats = any(
                    p.player_id == user.uuid
                    for result in game_results
                    for p in result.player_results
                )
                if has_stats:
                    game_name = Localization.get(user.locale, game_class.get_name_key())
                    items.append(MenuItem(text=game_name, id=f"stats_{game_type}"))

        if not items:
            user.speak_l("my-stats-no-games")
            return False

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "my_stats_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "my_stats_menu"}
        return True

    def _show_my_game_stats(self, user: NetworkUser, game_type: str) -> None:
        """Show personal stats for a specific game.

        Args:
            user: Acting user.
            game_type: Game type identifier.
        """
        from ..game_utils.stats_helpers import RatingHelper

        game_class = get_game_class(game_type)
        if not game_class:
            user.speak_l("game-type-not-found")
            return

        game_name = Localization.get(user.locale, game_class.get_name_key())
        game_results = self._get_game_results(game_type)

        # Calculate player's personal stats
        wins = 0
        losses = 0
        total_score = 0
        high_score = 0
        games_played = 0

        for result in game_results:
            winner_name = result.custom_data.get("winner_name")
            final_scores = result.custom_data.get("final_scores", {})
            final_light = result.custom_data.get("final_light", {})

            for p in result.player_results:
                if p.player_id == user.uuid:
                    games_played += 1
                    if winner_name == p.player_name:
                        wins += 1
                    else:
                        losses += 1

                    # Get score from final_scores or final_light (for Light Turret)
                    score = final_scores.get(p.player_name, 0)
                    if not score:
                        score = final_light.get(p.player_name, 0)
                    total_score += score
                    if score > high_score:
                        high_score = score

        if games_played == 0:
            user.speak_l("my-stats-no-data")
            return

        items = []
        # Basic stats
        winrate = round((wins / games_played * 100) if games_played > 0 else 0)

        items.append(
            MenuItem(
                text=Localization.get(user.locale, "my-stats-games-played", value=games_played),
                id="games_played",
            )
        )
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "my-stats-wins", value=wins),
                id="wins",
            )
        )
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "my-stats-losses", value=losses),
                id="losses",
            )
        )
        items.append(
            MenuItem(
                text=Localization.get(user.locale, "my-stats-winrate", value=winrate),
                id="winrate",
            )
        )

        # Score stats (if applicable)
        if total_score > 0:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "my-stats-total-score", value=total_score),
                    id="total_score",
                )
            )
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "my-stats-high-score", value=high_score),
                    id="high_score",
                )
            )

        # Skill rating
        rating_helper = RatingHelper(self._db, game_type)
        rating = rating_helper.get_rating(user.uuid)
        if rating.mu != 25.0 or rating.sigma != 25.0 / 3:  # Non-default rating
            items.append(
                MenuItem(
                    text=Localization.get(
                        user.locale,
                        "my-stats-rating",
                        value=round(rating.ordinal),
                        mu=round(rating.mu, 1),
                        sigma=round(rating.sigma, 1),
                    ),
                    id="rating",
                )
            )
        else:
            items.append(
                MenuItem(
                    text=Localization.get(user.locale, "my-stats-no-rating"),
                    id="no_rating",
                )
            )

        # Game-specific stats from custom leaderboard configs
        self._add_custom_stats(user, game_class, game_results, items)

        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "my_game_stats",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "my_game_stats",
            "game_type": game_type,
            "game_name": game_name,
        }

    def _add_custom_stats(
        self,
        user: NetworkUser,
        game_class,
        game_results: list,
        items: list,
    ) -> None:
        """Add game-specific custom stats from leaderboard configs.

        Args:
            user: Acting user.
            game_class: Game class for leaderboard config.
            game_results: GameResult list for the game.
            items: Menu item list to append to.
        """
        for config in game_class.get_leaderboard_types():
            custom_stat = self._build_custom_stat(user, config, game_results)
            if not custom_stat:
                continue
            lb_id, text = custom_stat
            items.append(MenuItem(text=text, id=f"custom_{lb_id}"))

    def _build_custom_stat(
        self, user: NetworkUser, config: dict, game_results: list
    ) -> tuple[str, str] | None:
        """Build a custom stat string from leaderboard config."""
        lb_id = config["id"]
        aggregate = config.get("aggregate", "sum")
        decimals = config.get("decimals", 0)
        values, num_values, denom_values = self._collect_custom_stat_values(
            user, config, game_results
        )

        final_value = self._aggregate_custom_stat(values, num_values, denom_values, aggregate)
        if final_value is None:
            return None

        formatted_value = self._format_custom_stat_value(final_value, decimals)
        text = self._format_custom_stat_text(user, lb_id, formatted_value)
        return lb_id, text

    def _collect_custom_stat_values(
        self, user: NetworkUser, config: dict, game_results: list
    ) -> tuple[list[float], list[float], list[float]]:
        """Extract raw custom stat values for a user across game results."""
        path = config.get("path")
        numerator_path = config.get("numerator")
        denominator_path = config.get("denominator")

        values: list[float] = []
        num_values: list[float] = []
        denom_values: list[float] = []

        for result in game_results:
            player_name = self._find_player_name(result, user.uuid)
            if not player_name:
                continue

            custom_data = result.custom_data
            if path:
                resolved_path = self._resolve_stat_path(path, player_name, user.uuid)
                value = self._extract_path_value(custom_data, resolved_path)
                if value is not None:
                    values.append(value)
            elif numerator_path and denominator_path:
                num_path = self._resolve_stat_path(numerator_path, player_name, user.uuid)
                denom_path = self._resolve_stat_path(denominator_path, player_name, user.uuid)
                num_val = self._extract_path_value(custom_data, num_path)
                denom_val = self._extract_path_value(custom_data, denom_path)
                if num_val is not None and denom_val is not None:
                    num_values.append(num_val)
                    denom_values.append(denom_val)

        return values, num_values, denom_values

    def _find_player_name(self, result, player_id: str) -> str | None:
        """Find the player name for a given player id in a result."""
        for p in result.player_results:
            if p.player_id == player_id:
                return p.player_name
        return None

    def _resolve_stat_path(self, path: str, player_name: str, player_id: str) -> str:
        """Substitute player tokens in stat paths."""
        return path.replace("{player_name}", player_name).replace("{player_id}", player_id)

    def _aggregate_custom_stat(
        self,
        values: list[float],
        num_values: list[float],
        denom_values: list[float],
        aggregate: str,
    ) -> float | None:
        """Aggregate raw stat values based on config rules."""
        if values:
            if aggregate == "sum":
                return sum(values)
            if aggregate == "max":
                return max(values)
            if aggregate == "avg":
                return sum(values) / len(values)
            return None

        if num_values and denom_values:
            total_num = sum(num_values)
            total_denom = sum(denom_values)
            if total_denom > 0:
                return total_num / total_denom

        return None

    def _format_custom_stat_value(self, value: float, decimals: int) -> str:
        """Format a custom stat value for display."""
        if decimals > 0:
            return f"{value:.{decimals}f}"
        return str(round(value))

    def _format_custom_stat_text(self, user: NetworkUser, lb_id: str, formatted_value: str) -> str:
        """Build the localized text for a custom stat."""
        loc_key = f"my-stats-{lb_id.replace('_', '-')}"
        text = Localization.get(user.locale, loc_key, value=formatted_value)
        if text != loc_key:
            return text

        type_key = f"leaderboard-type-{lb_id.replace('_', '-')}"
        type_name = Localization.get(user.locale, type_key)
        return f"{type_name}: {formatted_value}"

    def _extract_path_value(self, data: dict, path: str) -> float | None:
        """Extract a value from nested dict using dot-notation path.

        Args:
            data: Nested dict to read from.
            path: Dot-separated path string.

        Returns:
            Float value if found, otherwise None.
        """
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        if isinstance(current, (int, float)):
            return float(current)
        return None

    async def _handle_my_stats_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle my stats game selection.

        Args:
            user: Acting user.
            selection_id: Selected menu item id.
            state: Current menu state.
        """
        if selection_id == "back":
            self._show_main_menu(user)
        elif selection_id.startswith("stats_"):
            game_type = selection_id[6:]  # Remove "stats_" prefix
            self._show_my_game_stats(user, game_type)

    async def _handle_my_game_stats_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle my game stats menu selection.

        Args:
            user: Acting user.
            selection_id: Selected menu item id.
            state: Current menu state.
        """
        if selection_id == "back":
            if not self._show_my_stats_menu(user):
                self._show_main_menu(user)
        # Other selections (stats entries) are informational only

    def on_table_destroy(self, table) -> None:
        """Handle table destruction.

        Args:
            table: Table being destroyed.
        """
        if not table.game:
            return
        # Return all human players to main menu
        for player in table.game.players:
            if not player.is_bot:
                player_user = self._users.get(player.name)
                if player_user:
                    self._show_main_menu(player_user, reset_history=True)

    def on_game_result(self, result) -> None:
        """Handle game result persistence.

        Args:
            result: GameResult instance.
        """
        from ..game_utils.game_result import GameResult

        if not isinstance(result, GameResult):
            return

        # Save to database
        self._db.save_game_result(
            game_type=result.game_type,
            timestamp=result.timestamp,
            duration_ticks=result.duration_ticks,
            players=[
                (p.player_id, p.player_name, p.is_bot, getattr(p, "is_virtual_bot", False))
                for p in result.player_results
            ],
            custom_data=result.custom_data,
        )

    def on_table_save(self, table, username: str) -> None:
        """Handle table save request.

        Args:
            table: Table to save.
            username: Requesting username.
        """
        import json
        from datetime import datetime

        game = table.game
        if not game:
            return

        # Generate save name
        save_name = f"{game.get_name()} - {datetime.now():%Y-%m-%d %H:%M}"

        # Get game JSON
        game_json = game.to_json()

        # Build members list (includes bot status)
        members_data = []
        for player in game.players:
            members_data.append(
                {
                    "username": player.name,
                    "is_bot": player.is_bot,
                }
            )
        members_json = json.dumps(members_data)

        # Save to database
        self._db.save_user_table(
            username=username,
            save_name=save_name,
            game_type=table.game_type,
            game_json=game_json,
            members_json=members_json,
        )

        # Broadcast save message and destroy the table
        game.broadcast_l("table-saved-destroying")
        game.destroy()

    async def _handle_keybind(self, client: ClientConnection, packet: dict) -> None:
        """Handle keybind events.

        Args:
            client: Client connection.
            packet: Incoming keybind payload.
        """
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        table = self._tables.find_user_table(username)
        if not table and user:
            if packet.get("key") == "w" and packet.get("control"):
                players = [
                    u.username
                    for u in self._users.values()
                    if u.approved and not self._tables.find_user_table(u.username)
                ]
                if not players:
                    user.speak_l("online-users-none")
                    return
                names = Localization.format_list_and(user.locale, players)
                key = "online-users-one" if len(players) == 1 else "online-users-many"
                user.speak_l(key, count=len(players), users=names)
            return
        if table and table.game and user:
            player = table.game.get_player_by_id(user.uuid)
            if player:
                table.game.handle_event(player, packet)
                # Check if player left the game (user replaced by bot or removed)
                game_user = table.game._users.get(user.uuid)
                if game_user is not user:
                    table.remove_member(username)
                    self._show_main_menu(user, reset_history=True)

    async def _handle_document_editor_packet(self, client: ClientConnection, packet: dict) -> None:
        """Forward document editor responses to the browsing mixin."""
        username = client.username
        if not username:
            return
        user = self._users.get(username)
        if not user:
            return
        state = self._user_states.get(username, {})
        await self._handle_document_editor_response(user, packet, state)

    async def _handle_editbox(self, client: ClientConnection, packet: dict) -> None:
        """Handle editbox submissions.

        Args:
            client: Client connection.
            packet: Incoming editbox payload.
        """
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        if not user:
            return

        # Check for admin editbox handlers
        state = self._user_states.get(username, {})
        current_menu = state.get("menu")

        if await self._handle_document_editbox(user, current_menu, packet, state):
            return

        if current_menu == "decline_reason_editbox":
            text = packet.get("text", "")
            await self._handle_decline_reason_editbox(user, text, state)
            return

        if current_menu == "ban_reason_editbox":
            text = packet.get("text", "")
            await self._handle_ban_reason_editbox(user, text, state)
            return

        if current_menu == "unban_reason_editbox":
            text = packet.get("text", "")
            await self._handle_unban_reason_editbox(user, text, state)
            return

        # Forward to game if user is in a table
        table = self._tables.find_user_table(username)
        if table and table.game:
            player = table.game.get_player_by_id(user.uuid)
            if player:
                table.game.handle_event(player, packet)
                # Check if player left the game (user replaced by bot or removed)
                game_user = table.game._users.get(user.uuid)
                if game_user is not user:
                    table.remove_member(username)
                    self._show_main_menu(user, reset_history=True)

    async def _handle_chat(self, client: ClientConnection, packet: dict) -> None:
        """Handle chat message."""
        username = client.username
        if not username:
            return

        convo = packet.get("convo", "local")
        message = packet.get("message", "")
        language = packet.get("language", "Other")

        chat_packet = {
            "type": "chat",
            "convo": convo,
            "sender": username,
            "message": message,
            "language": language,
        }

        if convo == "local":
            table = self._tables.find_user_table(username)
            if table:
                for member_name in [m.username for m in table.members]:
                    user = self._users.get(member_name)
                    if user and user.approved:  # Only send to approved users
                        await user.connection.send(chat_packet)
            else:
                for user in self._users.values():
                    if not user.approved:
                        continue
                    if self._tables.find_user_table(user.username):
                        continue
                    await user.connection.send(chat_packet)
        elif convo == "global":
            # Broadcast to all approved users only
            for user in self._users.values():
                if user.approved:
                    await user.connection.send(chat_packet)

    def _get_online_usernames(self) -> list[str]:
        """Return sorted list of online usernames."""
        return sorted(self._users.keys(), key=str.lower)

    def _format_online_users_lines(self, user: NetworkUser) -> list[str]:
        """Format online users with detailed info for menu display.

        Format: ``Username (Xh) - Status, Language LangName, ClientType (Platform)``
        All labels are localized to the requesting *user*'s locale.
        """
        lines: list[str] = []
        for username in self._get_online_usernames():
            online_user = self._users.get(username)

            # Time online
            if online_user and hasattr(online_user, "format_time_online"):
                time_str = online_user.format_time_online()
            else:
                time_str = ""

            # Status (game or waiting for approval)
            if online_user and not online_user.approved:
                status = Localization.get(user.locale, "online-user-waiting-approval")
            else:
                table = self._tables.find_user_table(username)
                if table:
                    game_class = get_game_class(table.game_type)
                    status = (
                        Localization.get(user.locale, game_class.get_name_key())
                        if game_class
                        else table.game_type
                    )
                else:
                    status = Localization.get(user.locale, "online-user-not-in-game")

            # Build detail parts after status
            parts = [status]

            # Language
            if online_user:
                lang_label = Localization.get(user.locale, "language")
                lang_name = Localization.get(user.locale, f"language-{online_user.locale}")
                parts.append(f"{lang_label} {lang_name}")

            # Client type and platform
            client_type = getattr(online_user, "client_type", "") if online_user else ""
            platform_str = getattr(online_user, "platform", "") if online_user else ""
            if client_type:
                if platform_str:
                    parts.append(f"{client_type} ({platform_str})")
                else:
                    parts.append(client_type)

            detail = ", ".join(parts)
            if time_str:
                line = f"{username} ({time_str}) - {detail}"
            else:
                line = f"{username} - {detail}"
            lines.append(line)
        if not lines:
            lines.append(Localization.get(user.locale, "online-users-none"))
        return lines

    def _show_online_users_menu(self, user: NetworkUser) -> None:
        """Show online users with games in a read-only menu."""
        current_state = self._user_states.get(user.username, {})
        previous_menu_id = current_state.get("menu")
        previous_menu = None
        if previous_menu_id:
            current_menus = getattr(user, "_current_menus", {})
            previous_menu = current_menus.get(previous_menu_id)

        items = [
            MenuItem(text=line, id="online_user") for line in self._format_online_users_lines(user)
        ]
        user.show_menu(
            "online_users",
            items,
            multiletter=False,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            position=0,
        )
        previous_music = getattr(user, "_current_music", None)
        user.play_music("playersmus.ogg")
        self._user_states[user.username] = {
            "menu": "online_users",
            "return_menu_id": previous_menu_id,
            "return_menu": previous_menu,
            "return_state": dict(current_state),
            "return_music": dict(previous_music) if isinstance(previous_music, dict) else None,
        }

    def _restore_previous_menu(self, user: NetworkUser, state: dict) -> None:
        """Restore the previous menu after closing the online users list."""
        previous_menu_id = state.get("return_menu_id")
        previous_menu = state.get("return_menu")
        if not previous_menu_id or not previous_menu:
            self._show_main_menu(user)
            return

        user.show_menu(
            previous_menu_id,
            previous_menu.get("items", []),
            multiletter=previous_menu.get("multiletter_enabled", True),
            escape_behavior=EscapeBehavior(previous_menu.get("escape_behavior", "keybind")),
            position=previous_menu.get("position"),
            grid_enabled=previous_menu.get("grid_enabled", False),
            grid_width=previous_menu.get("grid_width", 1),
        )
        return_music = state.get("return_music")
        if isinstance(return_music, dict):
            music_name = return_music.get("name")
            if isinstance(music_name, str) and music_name:
                user.play_music(music_name, looping=bool(return_music.get("looping", True)))
        restored_state = dict(state.get("return_state", {}))
        restored_state["menu"] = previous_menu_id
        self._user_states[user.username] = restored_state

    async def _handle_list_online(self, client: ClientConnection) -> None:
        """Handle request for online users list."""
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        if not user:
            return

        online = self._get_online_usernames()
        count = len(online)
        if count == 0:
            user.speak_l("online-users-none")
            return
        users_str = Localization.format_list_and(user.locale, online)
        if count == 1:
            user.speak_l("online-users-one", users=users_str)
        else:
            user.speak_l("online-users-many", count=count, users=users_str)

    async def _handle_list_online_with_games(self, client: ClientConnection) -> None:
        """Handle request for online users list with game info."""
        username = client.username
        if not username:
            return

        user = self._users.get(username)
        if not user:
            return

        table = self._tables.find_user_table(username)
        if table and table.game:
            player = table.game.get_player_by_id(user.uuid)
            if player:
                table.game.status_box(player, self._format_online_users_lines(user))
                return

        self._show_online_users_menu(user)

    async def _handle_ping(self, client: ClientConnection) -> None:
        """Handle ping request - respond immediately with pong."""
        await client.send({"type": "pong"})


async def run_server(
    host: str | None = None,
    port: int | None = None,
    ssl_cert: str | Path | None = None,
    ssl_key: str | Path | None = None,
    preload_locales: bool = False,
) -> None:
    """Run the server.

    Args:
        host: Host address to bind to (falls back to [server].bind_ip in config)
        port: Port number to listen on (falls back to [server].port in config, then 8000)
        ssl_cert: Path to SSL certificate file (falls back to [network].ssl_cert in config)
        ssl_key: Path to SSL private key file (falls back to [network].ssl_key in config)
        preload_locales: Whether to block on localization compilation.
    """
    _configure_logging()
    _install_exception_handlers(asyncio.get_running_loop())

    config_path = get_default_config_path()
    example_path = get_example_config_path()
    db_path = _ensure_var_server_dir() / "playpalace.db"

    if _ensure_config_file(config_path, example_path):
        return

    db_created, needs_owner = _inspect_database(db_path)
    if needs_owner:
        _ensure_server_owner(db_path, config_path, db_created)

    host = _resolve_bind_host(host, config_path)
    port = _resolve_port(port, config_path)
    ssl_cert, ssl_key = _resolve_ssl(ssl_cert, ssl_key, config_path)

    print(f"Starting PlayPalace v{VERSION} server...")
    server = Server(
        host=host,
        port=port,
        ssl_cert=ssl_cert,
        ssl_key=ssl_key,
        db_path=str(db_path),
        preload_locales=preload_locales,
    )
    await server.start()

    try:
        # Run forever
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await server.stop()


def _configure_logging() -> None:
    """Configure server error logging to both file and stderr."""
    log_dir = _ensure_var_server_dir()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    file_handler = logging.FileHandler(str(log_dir / "errors.log"))
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(fmt)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(fmt)

    root = logging.getLogger("playpalace")
    root.setLevel(logging.ERROR)
    root.addHandler(file_handler)
    root.addHandler(stderr_handler)


def _install_exception_handlers(loop: asyncio.AbstractEventLoop) -> None:
    """Install top-level exception handlers for the event loop."""

    def _log_uncaught(exc_type, exc, tb):
        """Log uncaught exceptions while skipping shutdown interrupts."""
        if exc_type in (KeyboardInterrupt, asyncio.CancelledError):
            return
        logging.getLogger("playpalace").exception(
            "Uncaught exception", exc_info=(exc_type, exc, tb)
        )

    def _asyncio_exception_handler(loop, context):
        """Log asyncio exceptions with consistent context details."""
        exc = context.get("exception")
        if isinstance(exc, asyncio.CancelledError):
            return
        if exc:
            logging.getLogger("playpalace").exception("Asyncio exception", exc_info=exc)
        else:
            logging.getLogger("playpalace").error("Asyncio error: %s", context.get("message"))

    sys.excepthook = _log_uncaught
    loop.set_exception_handler(_asyncio_exception_handler)


def _ensure_config_file(config_path: Path, example_path: Path) -> bool:
    """Ensure a server config exists; return True if created and exit needed."""
    if config_path.exists():
        return False
    if not example_path.exists():
        print(
            f"ERROR: Missing configuration template '{example_path}'.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    try:
        ensure_default_config_dir()
        shutil.copyfile(example_path, config_path)
    except OSError as exc:
        print(
            f"ERROR: Failed to create '{config_path}' from template: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    print(f"Created '{config_path}' from '{example_path}'.")
    print(
        "Review the generated configuration before running in production. "
        "TLS is required unless you explicitly allow insecure mode.\n"
        "Edit the file and run the server with:\n"
        "  uv run python main.py --ssl-cert <cert> --ssl-key <key>\n"
        "or set [network].allow_insecure_ws=true for local development."
    )
    return True


def _inspect_database(db_path: Path) -> tuple[bool, bool]:
    """Check if the database exists and whether an owner is required."""
    if not db_path.exists():
        return True, True

    try:
        database = Database(str(db_path))
        database.connect()
        user_count = database.get_user_count()
        owner = database.get_server_owner()
        database.close()
        return False, user_count == 0 or owner is None
    except Exception as exc:
        print(f"ERROR: Failed to open database '{db_path}': {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def _ensure_server_owner(db_path: Path, config_path: Path, db_created: bool) -> None:
    """Create the initial server owner if required."""
    from server.cli import bootstrap_owner

    if db_created:
        print(f"Creating database at '{db_path}'.")
    else:
        print("No server owner found in the database. Creating one now.")

    if not sys.stdin.isatty():
        print(
            "ERROR: Cannot prompt for a server owner in a non-interactive session. "
            "Run `uv run python -m server.cli bootstrap-owner --username <name>` "
            "to create the initial owner.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    min_user_len, max_user_len, min_pass_len, max_pass_len = _load_auth_limits(config_path)

    username = _prompt_username(min_user_len, max_user_len)
    password = _prompt_password(min_pass_len, max_pass_len)

    try:
        bootstrap_owner(
            db_path=str(db_path),
            username=username,
            password=password,
            quiet=True,
        )
        print(f"Created server owner '{username}'.")
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def _load_auth_limits(config_path: Path) -> tuple[int, int, int, int]:
    """Load auth length limits from config, falling back to defaults."""
    min_user_len = DEFAULT_USERNAME_MIN_LENGTH
    max_user_len = DEFAULT_USERNAME_MAX_LENGTH
    min_pass_len = DEFAULT_PASSWORD_MIN_LENGTH
    max_pass_len = DEFAULT_PASSWORD_MAX_LENGTH
    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        auth_cfg = data.get("auth")
        if isinstance(auth_cfg, dict):
            min_user_len = int(auth_cfg.get("username_min_length", min_user_len))
            max_user_len = int(auth_cfg.get("username_max_length", max_user_len))
            min_pass_len = int(auth_cfg.get("password_min_length", min_pass_len))
            max_pass_len = int(auth_cfg.get("password_max_length", max_pass_len))
    except (OSError, tomllib.TOMLDecodeError, TypeError, ValueError) as exc:
        LOG.debug("Failed to load auth limits from config: %s", exc)
    return min_user_len, max_user_len, min_pass_len, max_pass_len


def _prompt_username(min_len: int, max_len: int) -> str:
    """Prompt for a valid server owner username."""
    while True:
        username = input(f"Server owner username ({min_len}-{max_len} chars): ").strip()
        if not username:
            print("Username cannot be empty.")
            continue
        if not (min_len <= len(username) <= max_len):
            print(f"Username must be between {min_len} and {max_len} characters.")
            continue
        return username


def _prompt_password(min_len: int, max_len: int) -> str:
    """Prompt for a valid server owner password."""
    while True:
        password = getpass(f"Server owner password ({min_len}-{max_len} chars): ")
        if not password:
            print("Password cannot be empty.")
            continue
        if not (min_len <= len(password) <= max_len):
            print(f"Password must be between {min_len} and {max_len} characters.")
            continue
        confirm = getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match. Try again.")
            continue
        return password


def _resolve_bind_host(host: str | None, config_path: Path) -> str:
    """Resolve bind host from config when none provided."""
    if host is not None:
        return host
    server_config = load_server_config(config_path)
    bind_ip = server_config.get("bind_ip")
    if isinstance(bind_ip, str) and bind_ip.strip():
        return bind_ip.strip()
    return "127.0.0.1"


def _resolve_port(port: int | None, config_path: Path) -> int:
    """Resolve port from config when none provided on the command line."""
    if port is not None:
        return port
    server_config = load_server_config(config_path)
    cfg_port = server_config.get("port")
    if isinstance(cfg_port, int) and cfg_port > 0:
        return cfg_port
    return 8000


def _resolve_ssl(
    ssl_cert: str | Path | None,
    ssl_key: str | Path | None,
    config_path: Path,
) -> tuple[str | Path | None, str | Path | None]:
    """Resolve SSL cert/key from config when not provided on the command line.

    CLI arguments take precedence. If neither cert nor key was given via CLI,
    both are read from [network] in config.toml. A partial CLI override (one
    but not the other) is caught upstream in main.py before this is called.
    """
    if ssl_cert is not None or ssl_key is not None:
        return ssl_cert, ssl_key
    cfg = load_full_config(config_path)
    net_cfg = cfg.get("network", {})
    cfg_cert = net_cfg.get("ssl_cert")
    cfg_key = net_cfg.get("ssl_key")
    if cfg_cert and cfg_key:
        return cfg_cert, cfg_key
    if bool(cfg_cert) != bool(cfg_key):
        LOG.warning(
            "SSL misconfiguration in config.toml: both [network].ssl_cert and "
            "[network].ssl_key must be set together. SSL will not be enabled."
        )
    return None, None
