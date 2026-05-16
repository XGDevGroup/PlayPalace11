function keyFromEvent(event) {
  if (event.key === " ") {
    return "space";
  }
  if (event.key === "Escape") {
    return "escape";
  }
  if (event.key === "Backspace") {
    return "backspace";
  }
  if (event.key === "Enter") {
    return "enter";
  }
  if (event.key.startsWith("F") && /^F\d+$/.test(event.key)) {
    return event.key.toLowerCase();
  }

  const lower = event.key.toLowerCase();
  if (/^[a-z0-9]$/.test(lower)) {
    return lower;
  }
  if (["arrowup", "arrowdown", "arrowleft", "arrowright"].includes(lower)) {
    return lower.replace("arrow", "");
  }
  return null;
}

function isTypingTarget(element) {
  if (!element) {
    return false;
  }
  const tag = element.tagName;
  return tag === "INPUT" || tag === "TEXTAREA" || element.isContentEditable;
}

function isEditableTarget(element) {
  if (!isTypingTarget(element)) {
    return false;
  }
  if (element.disabled) {
    return false;
  }
  if (element.readOnly) {
    return false;
  }
  return true;
}

export function installKeybinds({
  store,
  menuView,
  sendMenuSelection,
  sendEscape,
  sendKeybind,
  sendListOnline,
  sendListOnlineWithGames,
  onPreviousBuffer,
  onNextBuffer,
  onFirstBuffer,
  onLastBuffer,
  onOlderMessage,
  onNewerMessage,
  onOldestMessage,
  onNewestMessage,
  onToggleBufferMute,
  onAmbienceDown,
  onAmbienceUp,
  onMusicDown,
  onMusicUp,
  isModalOpen,
}) {
  document.addEventListener("keydown", (event) => {
    if (isModalOpen && isModalOpen()) {
      return;
    }

    const menu = store.state.currentMenu;
    const activeElement = document.activeElement;
    const typing = isTypingTarget(activeElement);
    const editing = isEditableTarget(activeElement);
    const menuFocused = activeElement === menuView.getElement();
    const connected = store.state.connection.authenticated;

    if (event.key === "Backspace" && !editing) {
      // Avoid browser navigation/context behavior outside editable controls.
      event.preventDefault();
      if (!menuFocused) {
        return;
      }
    }

    if (connected && !event.altKey && !event.ctrlKey && !event.metaKey) {
      if (event.key === "F2") {
        event.preventDefault();
        if (event.shiftKey) {
          sendListOnlineWithGames?.();
        } else {
          sendListOnline?.();
        }
        return;
      }
      if (menuFocused && event.key === "F4" && !event.shiftKey) {
        event.preventDefault();
        onToggleBufferMute?.();
        return;
      }
      if (event.key === "F7") {
        event.preventDefault();
        onAmbienceDown?.();
        return;
      }
      if (event.key === "F8") {
        event.preventDefault();
        onAmbienceUp?.();
        return;
      }
      if (event.key === "F9") {
        event.preventDefault();
        onMusicDown?.();
        return;
      }
      if (event.key === "F10") {
        event.preventDefault();
        onMusicUp?.();
        return;
      }
    }

    if (
      connected
      && (event.key === "w" || event.key === "W")
      && event.ctrlKey
      && !event.altKey
      && !event.metaKey
    ) {
      event.preventDefault();
      const menuIndex = menu.items.length ? menu.selection + 1 : null;
      const currentItem = menu.items[menu.selection] || null;
      sendKeybind({
        key: "w",
        control: true,
        alt: false,
        shift: event.shiftKey,
        menu_id: menu.menuId,
        menu_index: menuIndex,
        menu_item_id: currentItem?.id ?? null,
      });
      return;
    }

    if (menuFocused) {
      // Alt+Arrow: jump to grid row/column edges
      if (event.altKey && !event.ctrlKey && !event.metaKey && menu.gridEnabled && menu.gridWidth > 1) {
        const width = menu.gridWidth;
        const count = menu.items.length;
        const current = menu.selection;
        const row = Math.floor(current / width);
        const col = current % width;

        if (event.key === "ArrowLeft") {
          event.preventDefault();
          menuView.setSelection(row * width);
          return;
        }
        if (event.key === "ArrowRight") {
          event.preventDefault();
          menuView.setSelection(Math.min((row + 1) * width - 1, count - 1));
          return;
        }
        if (event.key === "ArrowUp") {
          event.preventDefault();
          menuView.setSelection(col);
          return;
        }
        if (event.key === "ArrowDown") {
          event.preventDefault();
          let bottom = col;
          while (bottom + width < count) {
            bottom += width;
          }
          menuView.setSelection(bottom);
          return;
        }
      }

      // Plain/Shift arrow: linear navigation (Ctrl+Arrow falls through to server keybinds)
      if (!event.ctrlKey && !event.altKey) {
        if (event.key === "ArrowUp" || event.key === "ArrowLeft") {
          event.preventDefault();
          menuView.moveSelection(-1);
          return;
        }
        if (event.key === "ArrowDown" || event.key === "ArrowRight") {
          event.preventDefault();
          menuView.moveSelection(1);
          return;
        }
      }
      if (event.key === "Home") {
        event.preventDefault();
        if (menu.gridEnabled && menu.gridWidth > 1) {
          const row = Math.floor(menu.selection / menu.gridWidth);
          menuView.setSelection(row * menu.gridWidth);
        } else {
          menuView.setSelection(0);
        }
        return;
      }
      if (event.key === "End") {
        event.preventDefault();
        if (menu.gridEnabled && menu.gridWidth > 1) {
          const row = Math.floor(menu.selection / menu.gridWidth);
          menuView.setSelection(Math.min((row + 1) * menu.gridWidth - 1, menu.items.length - 1));
        } else {
          menuView.setSelection(Math.max(0, menu.items.length - 1));
        }
        return;
      }
      if (event.key === "Enter" && !event.altKey && !event.ctrlKey && !event.shiftKey) {
        event.preventDefault();
        menuView.activateSelection();
        return;
      }

      const typedChar = event.key.length === 1 ? event.key.toLowerCase() : "";
      const isTypeNavChar = /^[a-z0-9 ]$/.test(typedChar);
      if (
        menu.multiletterEnabled
        && isTypeNavChar
        && !event.altKey
        && !event.ctrlKey
        && !event.metaKey
        && !event.shiftKey
      ) {
        event.preventDefault();
        menuView.handleTypeNavigation(typedChar);
        return;
      }

      if (!event.ctrlKey && !event.altKey && !event.metaKey) {
        if (event.key === "[") {
          event.preventDefault();
          if (event.shiftKey) {
            onFirstBuffer?.();
          } else {
            onPreviousBuffer?.();
          }
          return;
        }
        if (event.key === "]") {
          event.preventDefault();
          if (event.shiftKey) {
            onLastBuffer?.();
          } else {
            onNextBuffer?.();
          }
          return;
        }
        if (event.key === "," || event.key === "<") {
          event.preventDefault();
          if (event.shiftKey) {
            onOldestMessage?.();
          } else {
            onOlderMessage?.();
          }
          return;
        }
        if (event.key === "." || event.key === ">") {
          event.preventDefault();
          if (event.shiftKey) {
            onNewestMessage?.();
          } else {
            onNewerMessage?.();
          }
          return;
        }
      }
    }

    if (!menuFocused && !typing) {
      return;
    }

    if (event.key === "Escape" || (event.key === "Backspace" && menuFocused && !editing)) {
      if ((event.key === "Escape" || event.key === "Backspace") && menu.menuId === "main_menu") {
        event.preventDefault();
        return;
      }
      event.preventDefault();
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
      // keybind behavior: send actual key name so server-defined keybinds match.
      const menuIndex = menu.items.length ? menu.selection + 1 : null;
      const currentItem = menu.items[menu.selection] || null;
      sendKeybind({
        key: event.key === "Backspace" ? "backspace" : "escape",
        control: event.ctrlKey,
        alt: event.altKey,
        shift: event.shiftKey,
        menu_id: menu.menuId,
        menu_index: menuIndex,
        menu_item_id: currentItem?.id ?? null,
      });
      return;
    }

    if ((editing || !menuFocused) && event.key !== "Escape") {
      return;
    }

    const key = keyFromEvent(event);
    if (!key) {
      return;
    }

    const menuIndex = menu.items.length ? menu.selection + 1 : null;
    const currentItem = menu.items[menu.selection] || null;

    const isFunctionLike = [
      "escape",
      "space",
      "backspace",
      "enter",
      "up",
      "down",
      "left",
      "right",
      "f1",
      "f2",
      "f3",
      "f4",
      "f5",
      "f6",
      "f7",
      "f8",
      "f9",
      "f10",
    ].includes(key);

    const shouldSend = isFunctionLike || !menu.multiletterEnabled || event.altKey || event.ctrlKey || event.shiftKey;
    if (!shouldSend) {
      return;
    }

    event.preventDefault();
    sendKeybind({
      key,
      control: event.ctrlKey,
      alt: event.altKey,
      shift: event.shiftKey,
      menu_id: menu.menuId,
      menu_index: menuIndex,
      menu_item_id: currentItem?.id ?? null,
    });
  });
}
