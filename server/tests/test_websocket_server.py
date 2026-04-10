"""Tests for WebSocket server helpers and client handling."""

import json

import pytest

from server.network import websocket_server
from server.network.websocket_server import ClientConnection, WebSocketServer


class DummyWebSocket:
    def __init__(self):
        self.sent = []
        self.closed = False

    async def send(self, data):
        self.sent.append(data)

    async def close(self):
        self.closed = True

    @property
    def remote_address(self):
        return ("127.0.0.1", 1234)


@pytest.mark.asyncio
async def test_client_connection_send_and_close():
    ws = DummyWebSocket()
    conn = ClientConnection(websocket=ws, address="127.0.0.1:1234")

    await conn.send({"type": "pong"})
    assert json.loads(ws.sent[-1]) == {"type": "pong"}

    await conn.close()
    assert ws.closed


@pytest.mark.asyncio
async def test_websocket_server_broadcast_and_send_to_user():
    server = WebSocketServer()
    c1 = ClientConnection(DummyWebSocket(), "a:1")
    c1.authenticated = True
    c1.username = "alice"

    c2 = ClientConnection(DummyWebSocket(), "b:1")
    c2.authenticated = False
    c2.username = "bob"

    c3 = ClientConnection(DummyWebSocket(), "c:1")
    c3.authenticated = True
    c3.username = "carol"

    server.clients.update(
        {
            c1.address: c1,
            c2.address: c2,
            c3.address: c3,
        }
    )
    server.register_username(c1)
    server.register_username(c3)

    broadcast_packet = {
        "type": "chat",
        "convo": "global",
        "sender": "server",
        "message": "hello",
        "language": "English",
    }

    await server.broadcast(broadcast_packet, exclude=c1)
    assert c1.websocket.sent == []  # excluded
    assert c2.websocket.sent == []  # not authenticated
    assert json.loads(c3.websocket.sent[-1]) == broadcast_packet

    notice_packet = {"type": "speak", "text": "hi"}
    sent = await server.send_to_user("alice", notice_packet)
    assert sent
    notice_payload = json.loads(c1.websocket.sent[-1])
    assert notice_payload["type"] == "speak"
    assert notice_payload["text"] == "hi"

    assert not await server.send_to_user("unknown", notice_packet)
    assert server.get_client_by_username("carol") is c3
    assert server.get_client_by_username("nobody") is None


@pytest.mark.asyncio
async def test_websocket_server_passes_max_size(monkeypatch):
    recorded_kwargs = {}

    class DummyContext:
        def __init__(self):
            self.closed = False

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def close(self):
            self.closed = True

        async def wait_closed(self):
            return

    def fake_serve(*args, **kwargs):
        recorded_kwargs.update(kwargs)
        return DummyContext()

    monkeypatch.setattr(websocket_server, "serve", fake_serve)

    ws_server = WebSocketServer(max_message_size=2048)
    await ws_server.start()
    assert recorded_kwargs.get("max_size") == 2048
    await ws_server.stop()
