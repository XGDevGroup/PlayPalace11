"""Typed packet schemas shared between server and client."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

# ---------------------------------------------------------------------------
# Helper field types

MenuIndex = Annotated[int, Field(ge=1)]
VolumePercent = Annotated[int, Field(ge=0, le=100)]
PanPercent = Annotated[int, Field(ge=-100, le=100)]
PitchPercent = Annotated[int, Field(ge=0, le=200)]
LoopFlag = Annotated[bool, Field(default=True)]


class BasePacket(BaseModel):
    """Base class for all packet models."""

    model_config = ConfigDict(extra="forbid")
    type: str


class MenuItemPayload(BaseModel):
    """Structured representation of a menu item."""

    text: str
    id: str | None = None
    sound: str | None = None


MenuItem = Annotated[Union[str, MenuItemPayload], Field(union_mode="left_to_right")]


# ---------------------------------------------------------------------------
# Client -> Server packets


class AuthorizePacket(BasePacket):
    type: Literal["authorize"] = "authorize"
    username: str
    password: str | None = None
    session_token: str | None = None
    locale: str | None = None
    major: int | None = None
    minor: int | None = None
    patch: int | None = None
    client_type: str | None = None
    platform: str | None = None

    @model_validator(mode="after")
    def _ensure_credentials(self) -> "AuthorizePacket":
        if not (self.password or self.session_token):
            raise ValueError("authorize requires password or session_token")
        return self


class RegisterPacket(BasePacket):
    type: Literal["register"] = "register"
    username: str
    password: str
    email: str | None = None
    bio: str | None = None
    locale: str | None = None


class RefreshSessionPacket(BasePacket):
    type: Literal["refresh_session"] = "refresh_session"
    refresh_token: str
    username: str | None = None
    client_type: str | None = None
    platform: str | None = None


class MenuSelectionPacket(BasePacket):
    type: Literal["menu"] = "menu"
    menu_id: str | None = None
    selection: MenuIndex | None = None
    selection_id: str | None = None


class EscapePacket(BasePacket):
    type: Literal["escape"] = "escape"
    menu_id: str | None = None


class KeybindPacket(BasePacket):
    type: Literal["keybind"] = "keybind"
    key: str
    control: bool = False
    alt: bool = False
    shift: bool = False
    menu_id: str | None = None
    menu_index: MenuIndex | None = None
    menu_item_id: str | None = None


class EditboxPacket(BasePacket):
    type: Literal["editbox"] = "editbox"
    text: str
    input_id: str | None = None


class DocumentEditorResponsePacket(BasePacket):
    type: Literal["document_editor"] = "document_editor"
    dialog_id: str
    action: Literal["save", "cancel"]
    content: str = ""


class ChatPacket(BasePacket):
    type: Literal["chat"] = "chat"
    convo: Literal["local", "global"] = "local"
    message: str
    language: str = "Other"


class PingPacket(BasePacket):
    type: Literal["ping"] = "ping"


class ListOnlinePacket(BasePacket):
    type: Literal["list_online"] = "list_online"


class ListOnlineWithGamesPacket(BasePacket):
    type: Literal["list_online_with_games"] = "list_online_with_games"


class PlaylistDurationResponsePacket(BasePacket):
    type: Literal["playlist_duration_response"] = "playlist_duration_response"
    request_id: str | int
    playlist_id: str
    duration_type: Literal["total", "elapsed", "remaining"]
    duration: int = Field(ge=0)


class ClientOptionsPacket(BasePacket):
    type: Literal["client_options"] = "client_options"
    options: dict[str, Any]


class SlashCommandPacket(BasePacket):
    type: Literal["slash_command"] = "slash_command"
    command: str
    args: str = ""


class AdminsCommandPacket(BasePacket):
    type: Literal["admins_cmd"] = "admins_cmd"


class BroadcastCommandPacket(BasePacket):
    type: Literal["broadcast_cmd"] = "broadcast_cmd"
    message: str


class SetTableVisibilityCommandPacket(BasePacket):
    type: Literal["set_table_visibility_cmd"] = "set_table_visibility_cmd"
    state: bool | None = None


class CheckTableVisibilityCommandPacket(BasePacket):
    type: Literal["check_table_visibility_cmd"] = "check_table_visibility_cmd"


class SetTablePasswordCommandPacket(BasePacket):
    type: Literal["set_table_pw_cmd"] = "set_table_pw_cmd"
    password: str


class RemoveTablePasswordCommandPacket(BasePacket):
    type: Literal["remove_table_pw_cmd"] = "remove_table_pw_cmd"


class CheckTablePasswordCommandPacket(BasePacket):
    type: Literal["check_table_pw_cmd"] = "check_table_pw_cmd"


ClientToServerPacket = Annotated[
    Union[
        AuthorizePacket,
        RegisterPacket,
        RefreshSessionPacket,
        MenuSelectionPacket,
        KeybindPacket,
        EscapePacket,
        EditboxPacket,
        DocumentEditorResponsePacket,
        ChatPacket,
        PingPacket,
        ListOnlinePacket,
        ListOnlineWithGamesPacket,
        PlaylistDurationResponsePacket,
        ClientOptionsPacket,
        SlashCommandPacket,
        AdminsCommandPacket,
        BroadcastCommandPacket,
        SetTableVisibilityCommandPacket,
        CheckTableVisibilityCommandPacket,
        SetTablePasswordCommandPacket,
        RemoveTablePasswordCommandPacket,
        CheckTablePasswordCommandPacket,
    ],
    Field(discriminator="type"),
]

CLIENT_TO_SERVER_PACKET_ADAPTER = TypeAdapter(ClientToServerPacket)


# ---------------------------------------------------------------------------
# Server -> Client packets


class AuthorizeSuccessPacket(BasePacket):
    type: Literal["authorize_success"] = "authorize_success"
    username: str
    version: str
    session_token: str | None = None
    session_expires_at: int | None = None
    refresh_token: str | None = None
    refresh_expires_at: int | None = None


class RefreshSessionSuccessPacket(BasePacket):
    type: Literal["refresh_session_success"] = "refresh_session_success"
    username: str
    version: str | None = None
    session_token: str
    session_expires_at: int
    refresh_token: str
    refresh_expires_at: int


class RefreshSessionFailurePacket(BasePacket):
    type: Literal["refresh_session_failure"] = "refresh_session_failure"
    message: str


class SpeakPacket(BasePacket):
    type: Literal["speak"] = "speak"
    text: str
    buffer: str | None = None
    muted: bool = False


class PlaySoundPacket(BasePacket):
    type: Literal["play_sound"] = "play_sound"
    name: str
    volume: VolumePercent = 100
    pan: PanPercent = 0
    pitch: PitchPercent = 100


class PlayMusicPacket(BasePacket):
    type: Literal["play_music"] = "play_music"
    name: str
    looping: bool = True


class StopMusicPacket(BasePacket):
    type: Literal["stop_music"] = "stop_music"


class PlayAmbiencePacket(BasePacket):
    type: Literal["play_ambience"] = "play_ambience"
    intro: str | None = None
    loop: str
    outro: str | None = None


class StopAmbiencePacket(BasePacket):
    type: Literal["stop_ambience"] = "stop_ambience"


class MenuPacket(BasePacket):
    type: Literal["menu"] = "menu"
    menu_id: str
    items: list[MenuItem]
    multiletter_enabled: bool | None = None
    escape_behavior: Literal["keybind", "select_last_option", "escape_event"] | None = None
    position: int | None = None
    selection_id: str | None = None
    grid_enabled: bool | None = None
    grid_width: MenuIndex | None = None
    play_selection_sound: bool | None = None


class RequestInputPacket(BasePacket):
    type: Literal["request_input"] = "request_input"
    input_id: str
    prompt: str
    default_value: str = ""
    multiline: bool = False
    read_only: bool = False
    content_format: Literal["text", "markdown"] = "text"


class DocumentEditorPacket(BasePacket):
    type: Literal["document_editor"] = "document_editor"
    dialog_id: str
    content: str = ""
    content_label: str = ""
    source_content: str | None = None
    source_label: str | None = None
    prompt: str = ""


class ClearUIPacket(BasePacket):
    type: Literal["clear_ui"] = "clear_ui"


class DisconnectPacket(BasePacket):
    type: Literal["disconnect"] = "disconnect"
    reconnect: bool = False
    show_message: bool = False
    return_to_login: bool = False
    message: str | None = None
    status_mode: Literal["initializing", "maintenance", "running"] | None = None
    retry_after: Annotated[int, Field(ge=1)] | None = None


class ServerStatusPacket(BasePacket):
    type: Literal["server_status"] = "server_status"
    mode: Literal["initializing", "maintenance", "running"]
    retry_after: Annotated[int, Field(ge=1)]
    message: str | None = None
    resume_at: str | None = None


class TableCreatePacket(BasePacket):
    type: Literal["table_create"] = "table_create"
    host: str
    game: str


class GameInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: str
    name: str


class UpdateOptionsListsPacket(BasePacket):
    type: Literal["update_options_lists"] = "update_options_lists"
    games: list[GameInfo]
    languages: dict[str, str] | list[str] | None = None


class PongPacket(BasePacket):
    type: Literal["pong"] = "pong"


class ChatBroadcastPacket(BasePacket):
    type: Literal["chat"] = "chat"
    convo: Literal["local", "global"]
    sender: str
    message: str
    language: str


class GameListEntry(BaseModel):
    id: str
    name: str
    type: str
    players: int = Field(default=0, ge=0)
    max_players: int = Field(default=0, ge=0)


class GameListPacket(BasePacket):
    type: Literal["game_list"] = "game_list"
    games: list[GameListEntry]


class AddPlaylistPacket(BasePacket):
    type: Literal["add_playlist"] = "add_playlist"
    playlist_id: str
    tracks: list[str]
    audio_type: Literal["music", "sound"] = "music"
    shuffle_tracks: bool = False
    repeats: int = 1
    auto_start: bool = True
    auto_remove: bool = True


class StartPlaylistPacket(BasePacket):
    type: Literal["start_playlist"] = "start_playlist"
    playlist_id: str


class RemovePlaylistPacket(BasePacket):
    type: Literal["remove_playlist"] = "remove_playlist"
    playlist_id: str


class GetPlaylistDurationPacket(BasePacket):
    type: Literal["get_playlist_duration"] = "get_playlist_duration"
    playlist_id: str
    duration_type: Literal["total", "elapsed", "remaining"] = "total"
    request_id: str | int | None = None


class OpenClientOptionsPacket(BasePacket):
    type: Literal["open_client_options"] = "open_client_options"
    options: dict[str, Any] = Field(default_factory=dict)


class OpenServerOptionsPacket(BasePacket):
    type: Literal["open_server_options"] = "open_server_options"
    options: dict[str, Any] = Field(default_factory=dict)


ServerToClientPacket = Annotated[
    Union[
        AuthorizeSuccessPacket,
        RefreshSessionSuccessPacket,
        RefreshSessionFailurePacket,
        SpeakPacket,
        PlaySoundPacket,
        PlayMusicPacket,
        StopMusicPacket,
        PlayAmbiencePacket,
        StopAmbiencePacket,
        MenuPacket,
        RequestInputPacket,
        DocumentEditorPacket,
        ClearUIPacket,
        DisconnectPacket,
        ServerStatusPacket,
        TableCreatePacket,
        UpdateOptionsListsPacket,
        PongPacket,
        ChatBroadcastPacket,
        GameListPacket,
        AddPlaylistPacket,
        StartPlaylistPacket,
        RemovePlaylistPacket,
        GetPlaylistDurationPacket,
        OpenClientOptionsPacket,
        OpenServerOptionsPacket,
    ],
    Field(discriminator="type"),
]

SERVER_TO_CLIENT_PACKET_ADAPTER = TypeAdapter(ServerToClientPacket)


__all__ = [
    "CLIENT_TO_SERVER_PACKET_ADAPTER",
    "ClientToServerPacket",
    "SERVER_TO_CLIENT_PACKET_ADAPTER",
    "ServerToClientPacket",
]
