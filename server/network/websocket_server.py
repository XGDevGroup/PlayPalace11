"""WebSocket server for client connections."""

import errno
import json
import logging
import ssl
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Coroutine

import websockets
from pydantic import ValidationError
from websockets.asyncio.server import serve, ServerConnection

from .packet_models import SERVER_TO_CLIENT_PACKET_ADAPTER

PACKET_LOGGER = logging.getLogger("playpalace.packets")


@dataclass
class ClientConnection:
    """Represents a connected client."""

    websocket: ServerConnection
    address: str
    username: str | None = None
    authenticated: bool = False
    replaced: bool = False
    client_type: str = ""
    platform: str = ""

    async def send(self, packet: dict) -> None:
        """Send a packet to this client."""
        try:
            packet_model = SERVER_TO_CLIENT_PACKET_ADAPTER.validate_python(packet)
            payload = packet_model.model_dump(exclude_none=True)
        except ValidationError as exc:
            identifier = self.username or self.address
            PACKET_LOGGER.warning(
                "Refusing to send invalid packet (type=%s) to %s: %s",
                packet.get("type", "?"),
                identifier,
                exc,
            )
            return

        try:
            await self.websocket.send(json.dumps(payload))
        except websockets.exceptions.ConnectionClosed:
            identifier = self.username or self.address
            PACKET_LOGGER.debug(
                "Dropped packet type=%s to disconnected client %s",
                payload.get("type", "?"),
                identifier,
            )

    async def close(self) -> None:
        """Close this connection."""
        try:
            await self.websocket.close()
        except (OSError, RuntimeError, websockets.exceptions.ConnectionClosed) as exc:
            PACKET_LOGGER.debug("Failed to close websocket: %s", exc)


class WebSocketServer:
    """
    Async WebSocket server for handling client connections.

    The server is async, but game logic is synchronous. Messages are
    queued and processed synchronously, then responses are sent async.
    """

    def __init__(
        self,
        host: str = "::",
        port: int = 8000,
        on_connect: Callable[[ClientConnection], Coroutine] | None = None,
        on_disconnect: Callable[[ClientConnection], Coroutine] | None = None,
        on_message: Callable[[ClientConnection, dict], Coroutine] | None = None,
        ssl_cert: str | Path | None = None,
        ssl_key: str | Path | None = None,
        max_message_size: int | None = None,
    ):
        self.host = host
        self.port = port
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_message = on_message
        self._clients: dict[str, ClientConnection] = {}
        self._username_index: dict[str, ClientConnection] = {}
        self._server = None
        self._running = False
        self._ssl_context = None
        self._max_message_size = max_message_size

        # Configure SSL if certificates provided
        if ssl_cert and ssl_key:
            self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            try:
                self._ssl_context.load_cert_chain(str(ssl_cert), str(ssl_key))
            except Exception as exc:  # pylint: disable=broad-except
                print(
                    f"ERROR: Failed to load TLS certificate or key ({ssl_cert}, {ssl_key}): {exc}",
                    file=sys.stderr,
                )
                raise SystemExit(1) from exc

    @property
    def clients(self) -> dict[str, ClientConnection]:
        """Get all connected clients keyed by address."""
        return self._clients

    async def start(self) -> None:
        """Start the WebSocket server."""
        self._running = True
        # Manually enter the context manager to control lifecycle
        try:
            self._server = await serve(
                self._handle_client,
                self.host,
                self.port,
                ssl=self._ssl_context,
                max_size=self._max_message_size,
            ).__aenter__()
        except OSError as exc:
            print(
                f"ERROR: Failed to bind WebSocket server on {self.host}:{self.port}: {exc}",
                file=sys.stderr,
            )
            if exc.errno in (errno.EADDRINUSE, 48, 10048):
                print(
                    "Hint: That port is already in use. "
                    "If another PlayPalace server is running, stop it or choose a new port.",
                    file=sys.stderr,
                )
                print(
                    "To find the process: `lsof -i :{port}` or `ss -ltnp | rg :{port}`".format(
                        port=self.port
                    ),
                    file=sys.stderr,
                )
            raise SystemExit(1) from exc

        protocol = "wss" if self._ssl_context else "ws"
        print(f"WebSocket server started on {protocol}://{self.host}:{self.port}")

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()

        # Close all client connections
        for client in list(self._clients.values()):
            await client.close()
        self._clients.clear()
        self._username_index.clear()

    async def _handle_client(self, websocket: ServerConnection) -> None:
        """Handle a client connection."""
        address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        client = ClientConnection(websocket=websocket, address=address)
        self._clients[address] = client

        try:
            if self._on_connect:
                await self._on_connect(client)

            async for message in websocket:
                try:
                    packet = json.loads(message)
                    if self._on_message:
                        await self._on_message(client, packet)
                except json.JSONDecodeError:
                    identifier = client.username or client.address
                    PACKET_LOGGER.warning("Malformed JSON from %s", identifier)
                except Exception:
                    # Safety net: log and continue so the connection survives.
                    # The server layer should catch and handle errors before
                    # they reach here, but this prevents silent disconnects.
                    identifier = client.username or client.address
                    PACKET_LOGGER.exception(
                        "Unhandled error processing message from %s", identifier
                    )

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if client.username:
                if self._username_index.get(client.username) is client:
                    self.unregister_username(client.username)
            if address in self._clients:
                del self._clients[address]
            if self._on_disconnect:
                await self._on_disconnect(client)

    async def broadcast(self, packet: dict, exclude: ClientConnection | None = None) -> None:
        """Broadcast a packet to all authenticated clients."""
        for client in self._clients.values():
            if client.authenticated and client != exclude:
                await client.send(packet)

    def register_username(self, client: ClientConnection) -> None:
        """Register a client in the username index for O(1) lookup."""
        if client.username:
            self._username_index[client.username] = client

    def unregister_username(self, username: str) -> None:
        """Remove a username from the index."""
        self._username_index.pop(username, None)

    async def send_to_user(self, username: str, packet: dict) -> bool:
        """Send a packet to a specific user."""
        client = self._username_index.get(username)
        if client:
            await client.send(packet)
            return True
        return False

    def get_client_by_username(self, username: str) -> ClientConnection | None:
        """Get a client by username."""
        return self._username_index.get(username)
