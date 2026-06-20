export function createHistoryView({
  store,
  historyEl,
  historyLogEl,
  historyContentEl,
  historyToggleEl,
  bufferSelectEl,
  a11y,
}) {
  const mutedBuffers = new Set();
  const bufferPositions = {};
  const isMobileLike = window.matchMedia("(pointer: coarse)").matches;
  let mobileCollapsed = isMobileLike;
  let renderedLogBuffer = "";
  let renderedLogValue = null;
  let renderScheduled = false;

  function ensureBufferPosition(bufferName) {
    if (!Object.hasOwn(bufferPositions, bufferName)) {
      bufferPositions[bufferName] = 0;
    }
  }

  function getBufferNames() {
    return Object.keys(store.state.historyBuffers);
  }

  function getCurrentBufferName() {
    return store.state.historyBuffer || "all";
  }

  function getCurrentBufferLines() {
    const bufferName = getCurrentBufferName();
    return store.state.historyBuffers[bufferName] || [];
  }

  function getCurrentBufferInfo() {
    const name = getCurrentBufferName();
    const lines = getCurrentBufferLines();
    const position = bufferPositions[name] || 0;
    return {
      name,
      count: lines.length,
      position,
      muted: mutedBuffers.has(name),
    };
  }

  function announceBufferInfo() {
    const info = getCurrentBufferInfo();
    const muted = info.muted ? ", muted" : "";
    a11y.announce(`${info.name}${muted}. ${info.count} items`, { assertive: true });
  }

  function getCurrentItemText() {
    const lines = getCurrentBufferLines();
    if (!lines.length) {
      return "";
    }
    const name = getCurrentBufferName();
    const position = Math.max(0, Math.min(lines.length - 1, bufferPositions[name] || 0));
    const index = lines.length - 1 - position;
    if (index < 0 || index >= lines.length) {
      return "";
    }
    return lines[index] || "";
  }

  function announceCurrentItem() {
    const text = getCurrentItemText();
    if (text) {
      a11y.announce(text, { assertive: true });
    }
  }

  function flushRender() {
    renderScheduled = false;
    for (const name of getBufferNames()) {
      ensureBufferPosition(name);
    }
    const bufferName = store.state.historyBuffer;
    const lines = store.state.historyBuffers[bufferName] || [];
    const joined = lines.join("\n");

    // Skip the DOM work entirely when nothing in the visible buffer changed.
    // notify() fires on every state change (menu navigation, audio, etc.), so
    // most flushes here are no-ops — this keeps arrow-key menu moves cheap.
    if (bufferName === renderedLogBuffer && joined === renderedLogValue) {
      return;
    }
    renderedLogBuffer = bufferName;
    renderedLogValue = joined;

    historyEl.value = joined;
    historyEl.scrollTop = historyEl.scrollHeight;

    if (historyLogEl) {
      // Rebuild from scratch (bounded by the store's per-buffer cap). A full
      // rebuild is correct even when the cap trims lines off the front, which
      // the previous incremental count-based append could not detect.
      const fragment = document.createDocumentFragment();
      for (const line of lines) {
        const row = document.createElement("p");
        row.className = "history-line";
        row.textContent = line;
        fragment.appendChild(row);
      }
      historyLogEl.replaceChildren(fragment);
      historyLogEl.scrollTop = historyLogEl.scrollHeight;
    }
  }

  // Coalesce bursts of notify() calls (a single tap can append many lines, each
  // firing notify()) into one render per animation frame instead of one render
  // per line. This is what turns the old O(lines added * buffer size) churn per
  // tap into a single bounded render.
  function render() {
    if (renderScheduled) {
      return;
    }
    renderScheduled = true;
    if (typeof requestAnimationFrame === "function") {
      requestAnimationFrame(flushRender);
    } else {
      flushRender();
    }
  }

  function renderMobileVisibility() {
    if (!historyContentEl || !historyToggleEl || !historyLogEl) {
      return;
    }
    if (!isMobileLike) {
      historyToggleEl.hidden = false;
      historyToggleEl.tabIndex = -1;
      historyToggleEl.setAttribute("aria-expanded", "true");
      historyContentEl.hidden = false;
      historyLogEl.setAttribute("aria-live", "off");
      historyLogEl.hidden = true;
      return;
    }
    historyToggleEl.tabIndex = 0;
    historyContentEl.hidden = mobileCollapsed;
    historyLogEl.setAttribute("aria-live", "off");
    historyLogEl.hidden = false;
    historyToggleEl.setAttribute("aria-expanded", mobileCollapsed ? "false" : "true");
  }

  function addEntry(text, options = {}) {
    const {
      buffer = "misc",
      announce = true,
      assertive = false,
    } = options;

    store.addHistory(buffer, text);
    const incomingBufferMuted = mutedBuffers.has(buffer);
    if (announce && !incomingBufferMuted) {
      a11y.announce(text, { assertive });
    }
  }

  function switchBuffer({ step = 0, boundary = null } = {}) {
    const names = getBufferNames();
    if (!names.length) {
      return;
    }

    let nextIndex = Math.max(0, names.indexOf(getCurrentBufferName()));
    if (boundary === "first") {
      nextIndex = 0;
    } else if (boundary === "last") {
      nextIndex = names.length - 1;
    } else {
      nextIndex = Math.max(0, Math.min(names.length - 1, nextIndex + step));
    }
    store.setHistoryBuffer(names[nextIndex]);
    announceBufferInfo();
  }

  function moveInCurrentBuffer(direction) {
    const info = getCurrentBufferInfo();
    const maxPosition = Math.max(0, info.count - 1);
    let next = info.position;

    if (direction === "older") {
      next = Math.min(maxPosition, info.position + 1);
    } else if (direction === "newer") {
      next = Math.max(0, info.position - 1);
    } else if (direction === "oldest") {
      next = maxPosition;
    } else if (direction === "newest") {
      next = 0;
    }

    bufferPositions[info.name] = next;
    announceCurrentItem();
  }

  function toggleMuteCurrentBuffer() {
    const info = getCurrentBufferInfo();
    if (!info.name) {
      return;
    }
    if (mutedBuffers.has(info.name)) {
      mutedBuffers.delete(info.name);
    } else {
      mutedBuffers.add(info.name);
    }
    const status = mutedBuffers.has(info.name) ? "muted" : "unmuted";
    a11y.announce(`Buffer ${info.name} ${status}.`, { assertive: true });
  }

  if (bufferSelectEl) {
    bufferSelectEl.addEventListener("change", () => {
      store.setHistoryBuffer(bufferSelectEl.value);
    });
  }
  if (historyToggleEl) {
    historyToggleEl.addEventListener("click", () => {
      mobileCollapsed = !mobileCollapsed;
      renderMobileVisibility();
    });
  }

  store.subscribe(render);
  renderMobileVisibility();
  render();

  return {
    addEntry,
    render,
    previousBuffer() {
      switchBuffer({ step: -1 });
    },
    nextBuffer() {
      switchBuffer({ step: 1 });
    },
    firstBuffer() {
      switchBuffer({ boundary: "first" });
    },
    lastBuffer() {
      switchBuffer({ boundary: "last" });
    },
    olderMessage() {
      moveInCurrentBuffer("older");
    },
    newerMessage() {
      moveInCurrentBuffer("newer");
    },
    oldestMessage() {
      moveInCurrentBuffer("oldest");
    },
    newestMessage() {
      moveInCurrentBuffer("newest");
    },
    toggleCurrentBufferMute: toggleMuteCurrentBuffer,
    setCollapsed(collapsed) {
      mobileCollapsed = Boolean(collapsed);
      renderMobileVisibility();
    },
  };
}
