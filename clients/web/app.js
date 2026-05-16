import { createStore } from "./store.js";
import { createA11y } from "./a11y.js";
import { createAudioEngine } from "./audio.js";
import { createHistoryView } from "./ui/history.js";
import { createMenuView } from "./ui/menus.js";
import { createChat } from "./ui/chat.js";
import { installKeybinds } from "./keybinds.js";
import { createDocumentEditor } from "./ui/document_editor.js";
import { createMarkdownViewer } from "./ui/markdown_viewer.js";
import { createNetworkClient, loadPacketValidator } from "./network.js";

const REMEMBERED_USERNAME_KEY = "playpalace.web.remembered_username";
const AUTH_USERNAME_KEY = "playpalace.web.auth.username";
const SESSION_TOKEN_KEY = "playpalace.web.auth.session_token";
const SESSION_EXPIRES_AT_KEY = "playpalace.web.auth.session_expires_at";
const REFRESH_TOKEN_KEY = "playpalace.web.auth.refresh_token";
const REFRESH_EXPIRES_AT_KEY = "playpalace.web.auth.refresh_expires_at";
const MUSIC_VOLUME_KEY = "playpalace.web.music_volume";
const AMBIENCE_VOLUME_KEY = "playpalace.web.ambience_volume";
const AUDIO_MUTED_KEY = "playpalace.web.audio_muted";
const DEFAULT_MUSIC_VOLUME = 20;
const DEFAULT_AMBIENCE_VOLUME = 100;
const SESSION_REFRESH_LEEWAY_SECONDS = 60;
const RECONNECT_WINDOW_MS = 60_000;
const RECONNECT_RETRY_DELAY_MS = 3_000;
const DEFAULT_APP_VERSION = "2026.02.17.1";
const DEFAULT_WEB_CLIENT_CONFIG = {
  serverUrl: "",
  serverPort: null,
  soundBaseUrl: "./sounds",
};
const WEB_CLIENT_CONFIG = {
  ...DEFAULT_WEB_CLIENT_CONFIG,
  ...(window.WEB_CLIENT_CONFIG || {}),
};
const APP_VERSION = String(
  window.PLAYPALACE_WEB_VERSION || DEFAULT_APP_VERSION
).trim();

function shouldForceHttpsPage() {
  if (window.location.protocol !== "http:") {
    return false;
  }

  const host = window.location.hostname;
  const isLocalHost = host === "localhost" || host === "127.0.0.1" || host === "::1";
  if (isLocalHost) {
    return false;
  }

  if (!WEB_CLIENT_CONFIG.serverUrl) {
    return false;
  }

  try {
    const configured = new URL(WEB_CLIENT_CONFIG.serverUrl);
    return configured.protocol === "wss:";
  } catch {
    return String(WEB_CLIENT_CONFIG.serverUrl).toLowerCase().startsWith("wss://");
  }
}

function redirectHttpToHttps() {
  if (!shouldForceHttpsPage()) {
    return;
  }
  const nextUrl = new URL(window.location.href);
  nextUrl.protocol = "https:";
  if (nextUrl.port === "80") {
    nextUrl.port = "";
  }
  window.location.replace(nextUrl.toString());
}

function getDefaultServerUrl() {
  if (WEB_CLIENT_CONFIG.serverUrl) {
    try {
      const configured = new URL(WEB_CLIENT_CONFIG.serverUrl);
      if (!configured.port && WEB_CLIENT_CONFIG.serverPort) {
        configured.port = String(WEB_CLIENT_CONFIG.serverPort);
      }
      return configured.toString().replace(/\/$/, "");
    } catch {
      return WEB_CLIENT_CONFIG.serverUrl;
    }
  }

  const host = window.location.hostname;
  const isLocalHost = host === "localhost" || host === "127.0.0.1" || host === "::1";
  if (isLocalHost) {
    const localPort = WEB_CLIENT_CONFIG.serverPort || 8000;
    return `ws://127.0.0.1:${localPort}`;
  }

  const isHttps = window.location.protocol === "https:";
  const wsScheme = isHttps ? "wss" : "ws";
  const port = WEB_CLIENT_CONFIG.serverPort
    ? String(WEB_CLIENT_CONFIG.serverPort)
    : window.location.port;
  const isDefaultPort = (!isHttps && port === "80") || (isHttps && port === "443");
  const portSuffix = port && !isDefaultPort ? `:${port}` : "";
  return `${wsScheme}://${host}${portSuffix}`;
}

function normalizeUsername(username) {
  return String(username || "").trim();
}

function clampPercent(value, fallback) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return fallback;
  }
  return Math.max(0, Math.min(100, Math.round(parsed)));
}

function loadStoredPercent(key, fallback) {
  try {
    return clampPercent(localStorage.getItem(key), fallback);
  } catch {
    return fallback;
  }
}

function saveStoredPercent(key, value) {
  try {
    localStorage.setItem(key, String(clampPercent(value, 0)));
  } catch {
    // Ignore persistence failures.
  }
}

function loadStoredBool(key, fallback = false) {
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) {
      return fallback;
    }
    return raw === "1" || raw === "true";
  } catch {
    return fallback;
  }
}

function saveStoredBool(key, value) {
  try {
    localStorage.setItem(key, value ? "1" : "0");
  } catch {
    // Ignore persistence failures.
  }
}

function loadStoredString(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? String(raw) : "";
  } catch {
    return "";
  }
}

function saveStoredString(key, value) {
  try {
    localStorage.setItem(key, String(value || ""));
  } catch {
    // Ignore persistence failures.
  }
}

function removeStoredKey(key) {
  try {
    localStorage.removeItem(key);
  } catch {
    // Ignore persistence failures.
  }
}

function loadStoredEpochSeconds(key) {
  const raw = loadStoredString(key);
  const parsed = Number(raw);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return 0;
  }
  return Math.floor(parsed);
}

const elements = {
  loginDialog: document.getElementById("login-dialog"),
  gameShell: document.getElementById("game-shell"),
  connectForm: document.getElementById("connect-form"),
  username: document.getElementById("username"),
  password: document.getElementById("password"),
  togglePassword: document.getElementById("toggle-password"),
  rememberMe: document.getElementById("remember-me"),
  openLoginBtn: document.getElementById("open-login-btn"),
  disconnectBtn: document.getElementById("disconnect-btn"),
  status: document.getElementById("status"),
  loginError: document.getElementById("login-error"),
  musicVolume: document.getElementById("music-volume"),
  musicVolumeValue: document.getElementById("music-volume-value"),
  ambienceVolume: document.getElementById("ambience-volume"),
  ambienceVolumeValue: document.getElementById("ambience-volume-value"),
  audioMute: document.getElementById("audio-mute"),

  menuList: document.getElementById("menu-list"),
  inlineInput: document.getElementById("inline-input"),
  inlineInputPrompt: document.getElementById("inline-input-prompt"),
  inlineInputValue: document.getElementById("inline-input-value"),
  inlineInputSubmit: document.getElementById("inline-input-submit"),
  inlineInputCancel: document.getElementById("inline-input-cancel"),

  history: document.getElementById("history"),
  historyLog: document.getElementById("history-log"),
  historyContent: document.getElementById("history-content"),
  historyToggle: document.getElementById("history-toggle"),
  historyBuffer: document.getElementById("history-buffer"),
  actionsBtn: document.getElementById("actions-btn"),
  actionsDialog: document.getElementById("actions-dialog"),
  actionsList: document.getElementById("actions-list"),
  actionsCancel: document.getElementById("actions-cancel"),

  chatForm: document.getElementById("chat-form"),
  chatInput: document.getElementById("chat-input"),

  politeLive: document.getElementById("live-polite"),
  assertiveLive: document.getElementById("live-assertive"),

  inputDialog: document.getElementById("input-dialog"),
  inputDialogForm: document.getElementById("input-dialog-form"),
  inputPrompt: document.getElementById("input-prompt"),
  inputValue: document.getElementById("input-value"),
  inputCancel: document.getElementById("input-cancel"),
  inputSubmit: document.getElementById("input-submit"),
  appVersion: document.getElementById("app-version"),
  documentEditorDialog: document.getElementById("document-editor-dialog"),
  markdownViewerDialog: document.getElementById("markdown-viewer-dialog"),
};

const store = createStore();
const a11y = createA11y({
  politeEl: elements.politeLive,
  assertiveEl: elements.assertiveLive,
});
const audio = createAudioEngine({
  soundBaseUrl: WEB_CLIENT_CONFIG.soundBaseUrl || "./sounds",
});
audio.setMusicVolumePercent(loadStoredPercent(MUSIC_VOLUME_KEY, DEFAULT_MUSIC_VOLUME));
audio.setAmbienceVolumePercent(loadStoredPercent(AMBIENCE_VOLUME_KEY, DEFAULT_AMBIENCE_VOLUME));
audio.setMuted(loadStoredBool(AUDIO_MUTED_KEY, false));

const historyView = createHistoryView({
  store,
  historyEl: elements.history,
  historyLogEl: elements.historyLog,
  historyContentEl: elements.historyContent,
  historyToggleEl: elements.historyToggle,
  bufferSelectEl: elements.historyBuffer,
  a11y,
});

function playMenuSelectionSound(item) {
  if (item?.sound) {
    audio.playSound({ name: item.sound, volume: 100 });
    return;
  }
  audio.playSound({ name: "menuclick.ogg", volume: 50 });
}

const menuView = createMenuView({
  store,
  listEl: elements.menuList,
  onSelectionSound: playMenuSelectionSound,
  onBoundaryRepeat: (text) => {
    if (text) {
      a11y.announce(text, { assertive: true });
    }
  },
  onActivateSound: () => {
    audio.playSound({ name: "menuenter.ogg", volume: 50 });
  },
  onActivate: (_, selectionIndex) => {
    sendMenuSelection(selectionIndex);
  },
});
const documentEditor = createDocumentEditor({
  dialogEl: elements.documentEditorDialog,
  onSubmit: (response) => {
    if (network) {
      network.send({ type: "document_editor", ...response });
    }
  },
});

const markdownViewer = createMarkdownViewer({
  dialogEl: elements.markdownViewerDialog,
  onSubmit: (response) => {
    if (network) {
      network.send({ type: "editbox", ...response });
    }
    focusMenuOnNextMenuPacket = true;
  },
});
let pendingInlineInput = null;
let focusMenuOnNextMenuPacket = false;
let pendingActionsMenuRequest = false;
let activeActionsMenu = null;
let pendingAuthMethod = null;
let refreshTimerId = null;
let reconnectTimerId = null;

const reconnectState = {
  active: false,
  deadlineMs: 0,
  attempts: 0,
  intentionalDisconnect: false,
  suppressNextDisconnectStatus: false,
};

const authState = {
  username: loadStoredString(AUTH_USERNAME_KEY),
  sessionToken: loadStoredString(SESSION_TOKEN_KEY),
  sessionExpiresAt: loadStoredEpochSeconds(SESSION_EXPIRES_AT_KEY),
  refreshToken: loadStoredString(REFRESH_TOKEN_KEY),
  refreshExpiresAt: loadStoredEpochSeconds(REFRESH_EXPIRES_AT_KEY),
};

let network = null;

function setStatus(text, isError = false) {
  elements.status.textContent = text;
  elements.status.classList.toggle("error", isError);
}

function renderVersion() {
  if (!elements.appVersion) {
    return;
  }
  elements.appVersion.textContent = `Web client version ${APP_VERSION}`;
}

function renderVolumeControls() {
  const music = audio.getMusicVolumePercent();
  const ambience = audio.getAmbienceVolumePercent();
  if (elements.musicVolume) {
    elements.musicVolume.value = String(music);
  }
  if (elements.musicVolumeValue) {
    elements.musicVolumeValue.textContent = `${music}%`;
  }
  if (elements.ambienceVolume) {
    elements.ambienceVolume.value = String(ambience);
  }
  if (elements.ambienceVolumeValue) {
    elements.ambienceVolumeValue.textContent = `${ambience}%`;
  }
  if (elements.audioMute) {
    elements.audioMute.checked = audio.isMuted();
  }
}

function setMusicVolumePercent(value, { announce = false } = {}) {
  const next = clampPercent(value, audio.getMusicVolumePercent());
  audio.setMusicVolumePercent(next);
  saveStoredPercent(MUSIC_VOLUME_KEY, next);
  renderVolumeControls();
  if (announce) {
    a11y.announce(`Music: ${next}%`, { assertive: true });
  }
}

function setAmbienceVolumePercent(value, { announce = false } = {}) {
  const next = clampPercent(value, audio.getAmbienceVolumePercent());
  audio.setAmbienceVolumePercent(next);
  saveStoredPercent(AMBIENCE_VOLUME_KEY, next);
  renderVolumeControls();
  if (announce) {
    a11y.announce(`Ambience: ${next}%`, { assertive: true });
  }
}

function clearLoginError() {
  if (!elements.loginError) {
    return;
  }
  elements.loginError.hidden = true;
  elements.loginError.textContent = "";
}

function setLoginError(text, { announce = true } = {}) {
  if (!text) {
    return;
  }
  if (elements.loginError) {
    elements.loginError.textContent = text;
    elements.loginError.hidden = false;
  }
  if (announce) {
    a11y.announce(text, { assertive: true });
  }
}

function setConnectedUi(connected) {
  elements.gameShell.hidden = !connected;
  elements.disconnectBtn.disabled = !connected;
  elements.openLoginBtn.disabled = connected;
  updateActionsButtonVisibility();
}

function clearRefreshTimer() {
  if (refreshTimerId !== null) {
    window.clearTimeout(refreshTimerId);
    refreshTimerId = null;
  }
}

function clearReconnectTimer() {
  if (reconnectTimerId !== null) {
    window.clearTimeout(reconnectTimerId);
    reconnectTimerId = null;
  }
}

function clearReconnectState({ preserveIntentionalDisconnect = false } = {}) {
  clearReconnectTimer();
  reconnectState.active = false;
  reconnectState.deadlineMs = 0;
  reconnectState.attempts = 0;
  if (!preserveIntentionalDisconnect) {
    reconnectState.intentionalDisconnect = false;
  }
}

function suppressNextDisconnectStatus() {
  reconnectState.suppressNextDisconnectStatus = true;
}

function consumeSuppressedDisconnectStatus() {
  if (!reconnectState.suppressNextDisconnectStatus) {
    return false;
  }
  reconnectState.suppressNextDisconnectStatus = false;
  return true;
}

function persistAuthState() {
  saveStoredString(AUTH_USERNAME_KEY, authState.username);
  saveStoredString(SESSION_TOKEN_KEY, authState.sessionToken);
  saveStoredString(SESSION_EXPIRES_AT_KEY, authState.sessionExpiresAt || 0);
  saveStoredString(REFRESH_TOKEN_KEY, authState.refreshToken);
  saveStoredString(REFRESH_EXPIRES_AT_KEY, authState.refreshExpiresAt || 0);
}

function clearAuthState() {
  authState.username = "";
  authState.sessionToken = "";
  authState.sessionExpiresAt = 0;
  authState.refreshToken = "";
  authState.refreshExpiresAt = 0;
  clearRefreshTimer();
  clearReconnectState();
  removeStoredKey(AUTH_USERNAME_KEY);
  removeStoredKey(SESSION_TOKEN_KEY);
  removeStoredKey(SESSION_EXPIRES_AT_KEY);
  removeStoredKey(REFRESH_TOKEN_KEY);
  removeStoredKey(REFRESH_EXPIRES_AT_KEY);
}

function updateAuthStateFromPacket(packet) {
  if (packet.username) {
    authState.username = normalizeUsername(packet.username);
  }
  if (packet.session_token) {
    authState.sessionToken = packet.session_token;
  }
  if (packet.session_expires_at) {
    authState.sessionExpiresAt = Number(packet.session_expires_at) || 0;
  }
  if (packet.refresh_token) {
    authState.refreshToken = packet.refresh_token;
  }
  if (packet.refresh_expires_at) {
    authState.refreshExpiresAt = Number(packet.refresh_expires_at) || 0;
  }
  persistAuthState();
}

function getPlatformString() {
  if (navigator.userAgentData && navigator.userAgentData.platform) {
    return navigator.userAgentData.platform;
  }
  return navigator.platform || "";
}

function buildAuthorizePacketFromSession(username, sessionToken) {
  return {
    type: "authorize",
    username: normalizeUsername(username),
    session_token: sessionToken,
    major: 11,
    minor: 0,
    patch: 0,
    client_type: "Web",
    platform: getPlatformString(),
  };
}

function buildRefreshPacket(refreshToken, username = "") {
  const packet = {
    type: "refresh_session",
    refresh_token: refreshToken,
    client_type: "Web",
    platform: getPlatformString(),
  };
  if (username) {
    packet.username = normalizeUsername(username);
  }
  return packet;
}

function nowSeconds() {
  return Math.floor(Date.now() / 1000);
}

function reconnectWindowRemainingMs() {
  return reconnectState.deadlineMs - Date.now();
}

function canUseSessionToken() {
  return (
    Boolean(authState.username && authState.sessionToken)
    && authState.sessionExpiresAt > (nowSeconds() + 5)
  );
}

function canUseRefreshToken() {
  return (
    Boolean(authState.username && authState.refreshToken)
    && authState.refreshExpiresAt > (nowSeconds() + 5)
  );
}

function buildStoredAuthAttempt() {
  if (canUseSessionToken()) {
    return {
      authPacket: buildAuthorizePacketFromSession(authState.username, authState.sessionToken),
      method: "session_token",
    };
  }
  if (canUseRefreshToken()) {
    return {
      authPacket: buildRefreshPacket(authState.refreshToken, authState.username),
      method: "refresh_token",
    };
  }
  return null;
}

function authMethodLabel(method) {
  if (method === "session_token") {
    return "saved session";
  }
  if (method === "refresh_token") {
    return "saved refresh token";
  }
  return "saved credentials";
}

function sendRefreshSession({ assertiveOnFailure = false } = {}) {
  if (!canUseRefreshToken() || !network?.isConnected() || !store.state.connection.authenticated) {
    return false;
  }
  const ok = network.send(buildRefreshPacket(authState.refreshToken, authState.username));
  if (!ok && assertiveOnFailure) {
    a11y.announce("Unable to refresh session.", { assertive: true });
  }
  return ok;
}

function scheduleSessionRefresh() {
  clearRefreshTimer();
  if (!canUseRefreshToken() || !authState.sessionExpiresAt) {
    return;
  }
  const targetEpoch = authState.sessionExpiresAt - SESSION_REFRESH_LEEWAY_SECONDS;
  const delayMs = Math.max(5000, (targetEpoch - nowSeconds()) * 1000);
  refreshTimerId = window.setTimeout(() => {
    sendRefreshSession();
  }, delayMs);
}

function resetDisconnectedUi() {
  audio.stopAll();
  closeInlineInput({ returnFocus: false });
  closeActionsDialog();
  setConnectedUi(false);
}

function showLoginRequiredState({
  statusText,
  loginMessage,
  historyMessage = "",
  isError = true,
  clearAuth = false,
} = {}) {
  pendingAuthMethod = null;
  if (clearAuth) {
    clearAuthState();
  } else {
    clearRefreshTimer();
    clearReconnectState();
  }
  store.setConnection({ authenticated: false, status: "disconnected" });
  setStatus(statusText || "Disconnected", isError);
  resetDisconnectedUi();
  if (historyMessage) {
    historyView.addEntry(historyMessage, {
      buffer: "activity",
      announce: true,
      assertive: isError,
    });
  }
  clearLoginError();
  openLoginDialog();
  if (loginMessage) {
    setLoginError(loginMessage, { announce: true });
  }
}

function expireReconnectWindow(message) {
  showLoginRequiredState({
    statusText: "Reconnect expired",
    loginMessage: message,
    historyMessage: message,
    isError: true,
    clearAuth: false,
  });
}

function queueReconnectAttempt(delayMs = RECONNECT_RETRY_DELAY_MS) {
  clearReconnectTimer();
  if (!reconnectState.active) {
    return;
  }
  if (reconnectWindowRemainingMs() <= 0) {
    expireReconnectWindow("Could not reconnect within 60 seconds. Please log in again.");
    return;
  }

  const boundedDelayMs = Math.max(0, Math.min(delayMs, reconnectWindowRemainingMs()));
  const nextAttempt = reconnectState.attempts + 1;
  const statusText = boundedDelayMs > 0
    ? `Reconnecting in ${Math.ceil(boundedDelayMs / 1000)} seconds...`
    : `Reconnecting... attempt ${nextAttempt}`;
  setStatus(statusText, true);
  reconnectTimerId = window.setTimeout(() => {
    reconnectTimerId = null;
    attemptReconnect();
  }, boundedDelayMs);
}

function attemptReconnect() {
  if (!reconnectState.active || reconnectState.intentionalDisconnect) {
    return;
  }

  const authAttempt = buildStoredAuthAttempt();
  if (!authAttempt) {
    showLoginRequiredState({
      statusText: "Login required",
      loginMessage: "Saved session is no longer valid. Please log in again.",
      historyMessage: "Saved session is no longer valid. Please log in again.",
      isError: true,
      clearAuth: true,
    });
    return;
  }
  if (reconnectWindowRemainingMs() <= 0) {
    expireReconnectWindow("Could not reconnect within 60 seconds. Please log in again.");
    return;
  }

  reconnectState.attempts += 1;
  pendingAuthMethod = authAttempt.method;
  const serverUrl = getDefaultServerUrl();
  store.setConnection({
    serverUrl,
    username: normalizeUsername(authState.username),
    status: "connecting",
    authenticated: false,
  });
  setStatus(`Reconnecting... attempt ${reconnectState.attempts}`, true);
  historyView.addEntry(
    `Reconnect attempt ${reconnectState.attempts} using ${authMethodLabel(authAttempt.method)}.`,
    { buffer: "activity" }
  );
  network.connect({ serverUrl, authPacket: authAttempt.authPacket });
}

function beginReconnectFlow({
  initialDelayMs = 0,
  historyMessage = "Connection lost. Trying to reconnect for up to 60 seconds.",
} = {}) {
  if (reconnectState.intentionalDisconnect) {
    return false;
  }
  if (!buildStoredAuthAttempt()) {
    return false;
  }

  clearLoginError();
  closeLoginDialog();
  clearRefreshTimer();
  resetDisconnectedUi();

  if (!reconnectState.active) {
    reconnectState.active = true;
    reconnectState.deadlineMs = Date.now() + RECONNECT_WINDOW_MS;
    reconnectState.attempts = 0;
    historyView.addEntry(historyMessage, {
      buffer: "activity",
      announce: true,
      assertive: true,
    });
  }

  queueReconnectAttempt(initialDelayMs);
  return true;
}

function finishReconnectSuccess() {
  if (!reconnectState.active) {
    return;
  }
  const attempts = reconnectState.attempts;
  clearReconnectState();
  if (attempts > 0) {
    historyView.addEntry(
      `Reconnected after ${attempts} attempt${attempts === 1 ? "" : "s"}.`,
      { buffer: "activity", announce: true }
    );
  }
}

function shouldAutoReconnectAfterTransportLoss() {
  if (reconnectState.intentionalDisconnect) {
    return false;
  }
  if (pendingAuthMethod === "password") {
    return false;
  }
  return Boolean(
    buildStoredAuthAttempt()
    && (store.state.connection.authenticated || pendingAuthMethod === "session_token" || pendingAuthMethod === "refresh_token")
  );
}

function loadRememberedUsername() {
  try {
    const raw = localStorage.getItem(REMEMBERED_USERNAME_KEY);
    if (!raw) {
      return "";
    }
    return normalizeUsername(raw);
  } catch {
    return "";
  }
}

function saveRememberedUsername(username) {
  const safeUsername = normalizeUsername(username);
  if (!safeUsername) {
    return;
  }
  try {
    localStorage.setItem(REMEMBERED_USERNAME_KEY, safeUsername);
  } catch {
    // Ignore persistence failures.
  }
}

function clearRememberedUsername() {
  try {
    localStorage.removeItem(REMEMBERED_USERNAME_KEY);
  } catch {
    // Ignore persistence failures.
  }
}

function applyRememberedUsernameToLoginForm() {
  const rememberedUsername = loadRememberedUsername();
  elements.username.value = rememberedUsername;
  elements.rememberMe.checked = Boolean(rememberedUsername);
}

function parseMenuItems(itemsRaw) {
  const items = [];
  for (const item of itemsRaw || []) {
    if (typeof item === "string") {
      items.push({ text: item, id: null, sound: null });
    } else {
      items.push({ text: item?.text || "", id: item?.id ?? null, sound: item?.sound ?? null });
    }
  }
  return items;
}

function canOpenActionsPopup() {
  if (!store.state.connection.authenticated) {
    return false;
  }
  const menu = store.state.currentMenu;
  if (!menu || !menu.menuId || menu.menuId === "main_menu") {
    return false;
  }
  if (!menu.items.length) {
    return false;
  }
  return menu.menuId === "turn_menu";
}

function updateActionsButtonVisibility() {
  if (!elements.actionsBtn) {
    return;
  }
  const connected = store.state.connection.authenticated && !elements.gameShell.hidden;
  const canOpen = connected && canOpenActionsPopup();
  elements.actionsBtn.hidden = !canOpen;
  elements.actionsBtn.disabled = !canOpen;
}

function sendMenuSelection(selectionIndex) {
  const menu = store.state.currentMenu;
  const item = menu.items[selectionIndex];
  if (!item) {
    return;
  }
  const packet = {
    type: "menu",
    menu_id: menu.menuId,
    selection: selectionIndex + 1,
  };
  if (item.id !== null && item.id !== undefined) {
    packet.selection_id = item.id;
  }
  network.send(packet);
}

function sendEscape() {
  network.send({
    type: "escape",
    menu_id: store.state.currentMenu.menuId,
  });
}

function sendKeybind(payload) {
  network.send({ type: "keybind", ...payload });
}

function runEscapeAction() {
  const menu = store.state.currentMenu;
  if (!menu || menu.menuId === "main_menu") {
    return;
  }
  if (menu.escapeBehavior === "escape_event") {
    sendEscape();
    return;
  }
  if (menu.escapeBehavior === "select_last_option") {
    const lastIndex = menu.items.length - 1;
    if (lastIndex >= 0) {
      menuView.setSelection(lastIndex);
      sendMenuSelection(lastIndex);
    }
    return;
  }

  const menuIndex = menu.items.length ? menu.selection + 1 : null;
  const currentItem = menu.items[menu.selection] || null;
  sendKeybind({
    key: "escape",
    control: false,
    alt: false,
    shift: false,
    menu_id: menu.menuId,
    menu_index: menuIndex,
    menu_item_id: currentItem?.id ?? null,
  });
}

function sendListOnline() {
  network.send({ type: "list_online" });
}

function sendListOnlineWithGames() {
  if (store.state.currentMenu.menuId === "online_users") {
    return;
  }
  network.send({ type: "list_online_with_games" });
}

function adjustAmbienceVolume(deltaPercent) {
  setAmbienceVolumePercent(audio.getAmbienceVolumePercent() + deltaPercent, { announce: true });
}

function adjustMusicVolume(deltaPercent) {
  setMusicVolumePercent(audio.getMusicVolumePercent() + deltaPercent, { announce: true });
}

function closeInlineInput({ returnFocus = true } = {}) {
  pendingInlineInput = null;
  elements.inlineInput.hidden = true;
  elements.inlineInputPrompt.textContent = "";
  elements.inlineInputValue.value = "";
  elements.inlineInputValue.readOnly = false;
  if (returnFocus && store.state.connection.authenticated) {
    elements.menuList.focus();
  }
}

function submitInlineInput(text) {
  if (!pendingInlineInput) {
    return;
  }
  network.send({
    type: "editbox",
    input_id: pendingInlineInput.input_id,
    text,
  });
  focusMenuOnNextMenuPacket = true;
  closeInlineInput({ returnFocus: false });
}

function showInlineInput(packet) {
  pendingInlineInput = packet;
  const promptText = packet.prompt || "Enter value";
  elements.inlineInputPrompt.textContent = promptText;
  elements.inlineInputValue.value = packet.default_value || "";
  elements.inlineInputValue.readOnly = Boolean(packet.read_only);
  elements.inlineInputValue.setAttribute("aria-label", promptText);
  elements.inlineInput.hidden = false;
  requestAnimationFrame(() => {
    elements.inlineInputValue.focus();
    elements.inlineInputValue.select();
  });
}

function openLoginDialog() {
  if (!elements.loginDialog.open) {
    elements.loginDialog.showModal();
  }
  applyRememberedUsernameToLoginForm();
  elements.password.value = "";
  elements.password.type = "password";
  if (elements.togglePassword) {
    elements.togglePassword.textContent = "Show password";
  }
  elements.username.focus();
}

function installLoginKeyboardFlow() {
  elements.username.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") {
      return;
    }
    event.preventDefault();
    elements.password.focus();
  });
}

function closeLoginDialog() {
  if (elements.loginDialog.open) {
    elements.loginDialog.close();
  }
}

function installInGameTabTrap() {
  function isElementVisible(el) {
    if (!el || el.hidden) {
      return false;
    }
    return el.getClientRects().length > 0;
  }

  function getHistoryFocusTarget() {
    if (isElementVisible(elements.history)) {
      return elements.history;
    }
    if (isElementVisible(elements.historyLog)) {
      return elements.historyLog;
    }
    return null;
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") {
      return;
    }
    if (!store.state.connection.authenticated) {
      return;
    }
    if (elements.loginDialog.open || elements.inputDialog.open) {
      return;
    }

    const historyTarget = getHistoryFocusTarget();
    const targets = pendingInlineInput
      ? [elements.menuList, historyTarget, elements.chatInput, elements.inlineInputValue]
      : [elements.menuList, historyTarget, elements.chatInput];
    const focusableTargets = targets.filter(Boolean);
    const activeIndex = focusableTargets.indexOf(document.activeElement);
    if (activeIndex === -1) {
      return;
    }
    event.preventDefault();
    const delta = event.shiftKey ? -1 : 1;
    const nextIndex = (activeIndex + delta + focusableTargets.length) % focusableTargets.length;
    focusableTargets[nextIndex].focus();
  });
}

function installFocusHotkeys() {
  document.addEventListener("keydown", (event) => {
    if (!event.altKey || event.ctrlKey || event.shiftKey || event.metaKey) {
      return;
    }
    if (!store.state.connection.authenticated) {
      return;
    }
    if (elements.loginDialog.open || elements.inputDialog.open) {
      return;
    }

    const key = event.key.toLowerCase();
    if (key === "m") {
      event.preventDefault();
      elements.menuList.focus();
      return;
    }
    if (key === "c") {
      event.preventDefault();
      elements.chatInput.focus();
      return;
    }
    if (key === "h") {
      event.preventDefault();
      if (elements.history?.getClientRects().length) {
        elements.history.focus();
      } else if (elements.historyLog?.getClientRects().length) {
        elements.historyLog.focus();
      }
    }
  });
}

function installDialogTabTrap(dialogEl, focusTargets) {
  dialogEl.addEventListener("keydown", (event) => {
    if (event.key !== "Tab" || !dialogEl.open) {
      return;
    }

    const targets = focusTargets.filter((el) => el && !el.disabled);
    if (!targets.length) {
      return;
    }

    const currentIndex = targets.indexOf(document.activeElement);
    event.preventDefault();

    if (currentIndex === -1) {
      targets[0].focus();
      return;
    }

    const delta = event.shiftKey ? -1 : 1;
    const nextIndex = (currentIndex + delta + targets.length) % targets.length;
    targets[nextIndex].focus();
  });
}

function installActionsDialogTabTrap(dialogEl) {
  dialogEl.addEventListener("keydown", (event) => {
    if (event.key !== "Tab" || !dialogEl.open) {
      return;
    }

    const itemButtons = Array.from(
      elements.actionsList?.querySelectorAll("button.actions-item-btn:not(:disabled)") || []
    );
    const targets = [...itemButtons, elements.actionsCancel].filter((el) => el && !el.disabled);
    if (!targets.length) {
      return;
    }

    const currentIndex = targets.indexOf(document.activeElement);
    event.preventDefault();

    if (currentIndex === -1) {
      targets[0].focus();
      return;
    }

    const delta = event.shiftKey ? -1 : 1;
    const nextIndex = (currentIndex + delta + targets.length) % targets.length;
    targets[nextIndex].focus();
  });
}

function closeActionsDialog({ sendEscapeForActions = false } = {}) {
  if (sendEscapeForActions && activeActionsMenu?.menuId) {
    network.send({
      type: "escape",
      menu_id: activeActionsMenu.menuId,
    });
  }
  pendingActionsMenuRequest = false;
  activeActionsMenu = null;
  if (elements.actionsList) {
    elements.actionsList.innerHTML = "";
  }
  if (elements.actionsDialog?.open) {
    elements.actionsDialog.close();
  }
}

function sendActionMenuSelection(actionsMenu, selectionIndex) {
  const item = actionsMenu.items[selectionIndex];
  if (!item) {
    return;
  }
  const packet = {
    type: "menu",
    menu_id: actionsMenu.menuId,
    selection: selectionIndex + 1,
  };
  if (item.id !== null && item.id !== undefined) {
    packet.selection_id = item.id;
  }
  network.send(packet);
}

function openActionsDialogForMenu(actionsMenu) {
  activeActionsMenu = actionsMenu;
  if (!elements.actionsList) {
    return;
  }
  elements.actionsList.innerHTML = "";
  actionsMenu.items.forEach((item, index) => {
    const li = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "actions-item-btn";
    button.textContent = item.text;
    button.addEventListener("click", () => {
      sendActionMenuSelection(actionsMenu, index);
      closeActionsDialog({ sendEscapeForActions: false });
      elements.menuList.focus();
    });
    li.appendChild(button);
    elements.actionsList.appendChild(li);
  });
  if (!elements.actionsDialog.open) {
    elements.actionsDialog.showModal();
  }
  requestAnimationFrame(() => {
    const first = elements.actionsList?.querySelector("button.actions-item-btn");
    (first || elements.actionsCancel)?.focus();
  });
}

function requestActionsDialog() {
  if (!canOpenActionsPopup()) {
    return;
  }
  pendingActionsMenuRequest = true;
  runEscapeAction();
}

function handleAuthorizeSuccess(packet, { refreshed = false } = {}) {
  finishReconnectSuccess();
  store.setConnection({
    authenticated: true,
    status: "authenticated",
    lastError: "",
    username: normalizeUsername(packet.username || store.state.connection.username),
  });
  clearLoginError();
  updateAuthStateFromPacket(packet);
  scheduleSessionRefresh();

  if (!refreshed && pendingAuthMethod === "password") {
    if (elements.rememberMe.checked) {
      saveRememberedUsername(packet.username || elements.username.value);
    } else {
      clearRememberedUsername();
    }
  }
  pendingAuthMethod = null;

  const versionLabel = packet.version ? ` (${packet.version})` : "";
  setStatus(`Connected as ${packet.username}${versionLabel}`);
  closeLoginDialog();
  setConnectedUi(true);
  historyView.addEntry(`Connected as ${packet.username}${packet.version ? ` (server ${packet.version})` : ""}`, {
    buffer: "activity",
  });
  elements.menuList.focus();
}

function handlePacket(packet) {
  switch (packet.type) {
    case "authorize_success": {
      handleAuthorizeSuccess(packet, { refreshed: false });
      break;
    }
    case "refresh_session_success": {
      handleAuthorizeSuccess(packet, { refreshed: true });
      break;
    }
    case "refresh_session_failure": {
      const message = packet.message || "Session refresh failed. Please log in again.";
      showLoginRequiredState({
        statusText: "Login required",
        loginMessage: message,
        historyMessage: message,
        isError: true,
        clearAuth: true,
      });
      break;
    }
    case "menu": {
      const previousMenu = store.state.currentMenu;
      const items = parseMenuItems(packet.items);

      if (pendingActionsMenuRequest) {
        if (packet.menu_id === "actions_menu") {
          pendingActionsMenuRequest = false;
          openActionsDialogForMenu({
            menuId: packet.menu_id,
            items,
          });
          return;
        }
        pendingActionsMenuRequest = false;
      }

      let selection = 0;

      if (packet.selection_id) {
        const byId = items.findIndex((item) => item.id === packet.selection_id);
        if (byId >= 0) {
          selection = byId;
        }
      } else if (typeof packet.position === "number") {
        selection = Math.max(0, Math.min(items.length - 1, packet.position));
      } else if (items.length > 0 && previousMenu.menuId === packet.menu_id) {
        const previousSelection = Math.max(
          0,
          Math.min(previousMenu.items.length - 1, previousMenu.selection)
        );
        const previousItem = previousMenu.items[previousSelection];

        if (previousItem?.id !== null && previousItem?.id !== undefined) {
          const byPreviousId = items.findIndex((item) => item.id === previousItem.id);
          if (byPreviousId >= 0) {
            selection = byPreviousId;
          } else {
            selection = Math.max(0, Math.min(items.length - 1, previousSelection));
          }
        } else if (previousItem?.text) {
          const byPreviousText = items.findIndex((item) => item.text === previousItem.text);
          if (byPreviousText >= 0) {
            selection = byPreviousText;
          } else {
            selection = Math.max(0, Math.min(items.length - 1, previousSelection));
          }
        } else {
          selection = Math.max(0, Math.min(items.length - 1, previousSelection));
        }
      }

      store.setMenu({
        menuId: packet.menu_id,
        items,
        selection,
        multiletterEnabled: packet.multiletter_enabled ?? true,
        escapeBehavior: packet.escape_behavior ?? "keybind",
        gridEnabled: packet.grid_enabled ?? false,
        gridWidth: packet.grid_width ?? 1,
      });
      if (packet.play_selection_sound && items.length > 0) {
        playMenuSelectionSound(items[Math.max(0, Math.min(selection, items.length - 1))]);
      }
      updateActionsButtonVisibility();
      if (focusMenuOnNextMenuPacket) {
        focusMenuOnNextMenuPacket = false;
        requestAnimationFrame(() => {
          elements.menuList.focus();
        });
      }
      break;
    }
    case "speak": {
      const text = packet.text || "";
      if (!text) {
        return;
      }
      if (!store.state.connection.authenticated && elements.loginDialog.open) {
        setLoginError(text, { announce: !packet.muted });
      }
      historyView.addEntry(text, {
        buffer: packet.buffer || "misc",
        announce: !packet.muted,
      });
      break;
    }
    case "chat": {
      const prefix = packet.convo === "global" ? `${packet.sender} globally` : packet.sender;
      const line = `${prefix}: ${packet.message}`;
      historyView.addEntry(line, { buffer: "chats", announce: true });
      audio.playSound({ name: packet.convo === "global" ? "chat.ogg" : "chatlocal.ogg" });
      break;
    }
    case "play_sound": {
      audio.playSound(packet);
      break;
    }
    case "play_music": {
      audio.playMusic(packet);
      break;
    }
    case "stop_music": {
      audio.stopMusic();
      break;
    }
    case "play_ambience": {
      audio.playAmbience(packet);
      break;
    }
    case "stop_ambience": {
      audio.stopAmbience();
      break;
    }
    case "request_input": {
      if (packet.content_format === "markdown") {
        if (!packet.default_value) {
          packet.default_value = "*No documentation available.*";
        }
        markdownViewer.show(packet);
      } else {
        showInlineInput(packet);
      }
      break;
    }
    case "document_editor": {
      documentEditor.show(packet);
      break;
    }
    case "clear_ui": {
      closeInlineInput({ returnFocus: false });
      store.clearUi();
      closeActionsDialog();
      updateActionsButtonVisibility();
      break;
    }
    case "disconnect": {
      suppressNextDisconnectStatus();
      const message = packet.message || "Disconnected by server.";
      if (packet.reconnect) {
        const retryDelayMs = Math.max(1, Number(packet.retry_after || 3)) * 1000;
        if (beginReconnectFlow({
          initialDelayMs: retryDelayMs,
          historyMessage: `${message} Trying to reconnect for up to 60 seconds.`,
        })) {
          setStatus(`Reconnecting in ${Math.ceil(retryDelayMs / 1000)} seconds...`, true);
          store.setConnection({ authenticated: false, status: "disconnected" });
          break;
        }
      }
      showLoginRequiredState({
        statusText: packet.return_to_login ? "Login required" : "Disconnected",
        loginMessage: packet.show_message || packet.return_to_login ? message : "",
        historyMessage: message,
        isError: packet.show_message || packet.return_to_login,
        clearAuth: packet.return_to_login && packet.reconnect === false,
      });
      break;
    }
    case "update_options_lists": {
      store.setServerOptions({
        games: packet.games || [],
        languages: packet.languages || {},
      });
      break;
    }
    default: {
      break;
    }
  }
}

function installAudioUnlock() {
  const unlockOnce = async () => {
    if (store.state.audioUnlocked) {
      return;
    }
    const unlocked = await audio.unlock();
    if (unlocked) {
      store.setAudioUnlocked(true);
      window.removeEventListener("pointerdown", unlockOnce, true);
      window.removeEventListener("keydown", unlockOnce, true);
    }
  };

  const events = ["pointerdown", "keydown"];
  for (const eventName of events) {
    window.addEventListener(eventName, unlockOnce, { capture: true, passive: true });
  }
}

async function bootstrap() {
  redirectHttpToHttps();
  if (window.location.protocol !== "https:" && shouldForceHttpsPage()) {
    return;
  }

  renderVersion();
  renderVolumeControls();
  const validator = await loadPacketValidator();

  network = createNetworkClient({
    validator,
    onStatus: (status) => {
      if (status === "connecting") {
        if (reconnectState.active) {
          const attemptLabel = reconnectState.attempts > 0 ? ` attempt ${reconnectState.attempts}` : "";
          setStatus(`Reconnecting${attemptLabel}...`, true);
        } else {
          setStatus("Connecting...");
        }
        setConnectedUi(false);
      } else if (status === "connected") {
        if (reconnectState.active) {
          setStatus("Reconnected. Authorizing...");
        } else if (pendingAuthMethod === "session_token") {
          setStatus("Connected. Restoring session...");
        } else if (pendingAuthMethod === "refresh_token") {
          setStatus("Connected. Refreshing session...");
        } else {
          setStatus("Connected. Authorizing...");
        }
      } else if (status === "disconnected") {
        if (consumeSuppressedDisconnectStatus()) {
          reconnectState.intentionalDisconnect = false;
          return;
        }
        pendingAuthMethod = null;
        clearRefreshTimer();
        if (reconnectState.active) {
          queueReconnectAttempt(RECONNECT_RETRY_DELAY_MS);
          return;
        }
        if (shouldAutoReconnectAfterTransportLoss() && beginReconnectFlow()) {
          return;
        }
        reconnectState.intentionalDisconnect = false;
        showLoginRequiredState({
          statusText: "Disconnected",
          loginMessage: "",
          historyMessage: "Disconnected.",
          isError: true,
          clearAuth: false,
        });
      } else if (status === "error") {
        if (reconnectState.active) {
          setStatus("Connection error. Retrying...", true);
          return;
        }
        if (shouldAutoReconnectAfterTransportLoss() && beginReconnectFlow({
          historyMessage: "Connection error. Trying to reconnect for up to 60 seconds.",
        })) {
          return;
        }
        store.setConnection({ status: "disconnected", authenticated: false });
        setStatus("Connection error", true);
        setLoginError("Connection error.", { announce: true });
        resetDisconnectedUi();
        openLoginDialog();
      }
    },
    onPacket: handlePacket,
    onError: (message) => {
      historyView.addEntry(message, { buffer: "activity", announce: true, assertive: true });
      if (!reconnectState.active) {
        setStatus(message, true);
      }
      if (!store.state.connection.authenticated && elements.loginDialog.open) {
        setLoginError(message, { announce: false });
      }
    },
  });

  createChat({
    chatFormEl: elements.chatForm,
    chatInputEl: elements.chatInput,
    onSend: ({ convo, message }) => {
      network.send({
        type: "chat",
        convo,
        message,
        language: "English",
      });
    },
  });

  installKeybinds({
    store,
    menuView,
    sendMenuSelection,
    sendEscape,
    sendKeybind,
    sendListOnline,
    sendListOnlineWithGames,
    onPreviousBuffer: () => historyView.previousBuffer(),
    onNextBuffer: () => historyView.nextBuffer(),
    onFirstBuffer: () => historyView.firstBuffer(),
    onLastBuffer: () => historyView.lastBuffer(),
    onOlderMessage: () => historyView.olderMessage(),
    onNewerMessage: () => historyView.newerMessage(),
    onOldestMessage: () => historyView.oldestMessage(),
    onNewestMessage: () => historyView.newestMessage(),
    onToggleBufferMute: () => historyView.toggleCurrentBufferMute(),
    onAmbienceDown: () => adjustAmbienceVolume(-10),
    onAmbienceUp: () => adjustAmbienceVolume(10),
    onMusicDown: () => adjustMusicVolume(-10),
    onMusicUp: () => adjustMusicVolume(10),
    isModalOpen: () => elements.loginDialog.open || elements.inputDialog.open,
  });

  elements.connectForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (store.state.connection.status === "connecting") {
      return;
    }
    clearLoginError();
    const serverUrl = getDefaultServerUrl();
    const username = normalizeUsername(elements.username.value);
    const password = elements.password.value;

    if (!username) {
      setStatus("Username is required.", true);
      return;
    }

    elements.username.value = username;
    elements.loginDialog.returnValue = "connect";
    store.setConnection({ serverUrl, username, status: "connecting", authenticated: false });
    pendingAuthMethod = "password";
    network.connect({
      serverUrl,
      authPacket: {
        type: "authorize",
        username,
        password,
        major: 11,
        minor: 0,
        patch: 0,
        client_type: "Web",
        platform: getPlatformString(),
      },
    });
  });

  elements.disconnectBtn.addEventListener("click", () => {
    reconnectState.intentionalDisconnect = true;
    suppressNextDisconnectStatus();
    clearReconnectState({ preserveIntentionalDisconnect: true });
    clearRefreshTimer();
    network.disconnect();
    reconnectState.intentionalDisconnect = false;
    store.setConnection({ status: "disconnected", authenticated: false });
    setStatus("Disconnected");
    resetDisconnectedUi();
    openLoginDialog();
    historyView.addEntry("Disconnected.", { buffer: "activity", announce: true });
  });

  elements.openLoginBtn.addEventListener("click", () => {
    openLoginDialog();
  });
  elements.togglePassword?.addEventListener("click", () => {
    const showing = elements.password.type === "text";
    elements.password.type = showing ? "password" : "text";
    elements.togglePassword.textContent = showing ? "Show password" : "Hide password";
    elements.password.focus();
  });
  elements.actionsBtn?.addEventListener("click", () => {
    requestActionsDialog();
  });
  elements.actionsCancel?.addEventListener("click", () => {
    closeActionsDialog({ sendEscapeForActions: true });
  });

  elements.musicVolume?.addEventListener("input", (event) => {
    const value = event.target?.value ?? "0";
    setMusicVolumePercent(value, { announce: false });
  });
  elements.musicVolume?.addEventListener("change", async (event) => {
    const value = event.target?.value ?? "0";
    setMusicVolumePercent(value, { announce: false });
    await audio.unlock();
  });
  elements.ambienceVolume?.addEventListener("input", (event) => {
    const value = event.target?.value ?? "0";
    setAmbienceVolumePercent(value, { announce: false });
  });
  elements.ambienceVolume?.addEventListener("change", async (event) => {
    const value = event.target?.value ?? "0";
    setAmbienceVolumePercent(value, { announce: false });
    await audio.unlock();
  });
  elements.audioMute?.addEventListener("change", (event) => {
    const nextMuted = Boolean(event.target?.checked);
    audio.setMuted(nextMuted);
    saveStoredBool(AUDIO_MUTED_KEY, nextMuted);
  });

  elements.menuList.addEventListener("click", () => {
    elements.menuList.focus();
  });
  elements.inlineInputSubmit.addEventListener("click", () => {
    submitInlineInput(elements.inlineInputValue.value);
  });
  elements.inlineInputCancel.addEventListener("click", () => {
    submitInlineInput("");
  });
  elements.inlineInputValue.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      submitInlineInput("");
      return;
    }
    if (event.key === "Enter" && !event.shiftKey && !event.ctrlKey && !event.altKey) {
      event.preventDefault();
      event.stopPropagation();
      submitInlineInput(elements.inlineInputValue.value);
      return;
    }
    const keyCode = event.key.length === 1 ? event.key.charCodeAt(0) : 0;
    const shouldPlayTyping = (
      !elements.inlineInputValue.readOnly
      && keyCode >= 32
      && keyCode <= 126
      && !event.ctrlKey
      && !event.altKey
      && !event.metaKey
    );
    if (shouldPlayTyping) {
      const soundNum = Math.floor(Math.random() * 4) + 1;
      audio.playSound({ name: `typing${soundNum}.ogg`, volume: 50 });
    }
  });
  elements.loginDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
  });

  installAudioUnlock();
  installInGameTabTrap();
  installFocusHotkeys();
  installLoginKeyboardFlow();
  installDialogTabTrap(elements.inputDialog, [
    elements.inputValue,
    elements.inputCancel,
    elements.inputSubmit,
  ]);
  installActionsDialogTabTrap(elements.actionsDialog);
  setConnectedUi(false);
  const serverUrl = getDefaultServerUrl();
  const bootstrapAuthAttempt = buildStoredAuthAttempt();
  if (bootstrapAuthAttempt) {
    pendingAuthMethod = bootstrapAuthAttempt.method;
    store.setConnection({
      serverUrl,
      username: normalizeUsername(authState.username),
      status: "connecting",
      authenticated: false,
    });
    network.connect({ serverUrl, authPacket: bootstrapAuthAttempt.authPacket });
  } else {
    openLoginDialog();
  }
}

void bootstrap();
