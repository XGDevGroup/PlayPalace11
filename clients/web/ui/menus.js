export function createMenuView({
  store,
  listEl,
  onActivate,
  onSelectionSound,
  onActivateSound,
  onBoundaryRepeat,
}) {
  let renderVersion = 0;
  let lastStructureSnapshot = "";
  let lastSelection = -1;
  const isCoarsePointer = window.matchMedia("(pointer: coarse)").matches;
  const useActiveDescendant = !isCoarsePointer;
  let searchBuffer = "";
  let lastTypeTime = 0;
  const typeTimeoutSeconds = 0.15;
  let suppressClickUntil = 0;

  function menuStructureSnapshot(menu) {
    const itemsSnapshot = (menu.items || [])
      .map((item) => `${item?.id ?? ""}|${item?.text ?? ""}|${item?.sound ?? ""}`)
      .join("||");
    return [
      menu.menuId ?? "",
      menu.multiletterEnabled ? "1" : "0",
      menu.escapeBehavior ?? "",
      menu.gridEnabled ? "1" : "0",
      menu.gridWidth ?? 1,
      itemsSnapshot,
    ].join("::");
  }

  function currentOptionId(index) {
    return `menu-option-${renderVersion}-${index}`;
  }

  function setSelection(next) {
    const count = store.state.currentMenu.items.length;
    if (!count) {
      store.setMenu({ selection: 0 });
      return;
    }
    const bounded = Math.max(0, Math.min(count - 1, next));
    if (bounded === store.state.currentMenu.selection) {
      return;
    }
    store.setMenu({ selection: bounded });
    if (onSelectionSound) {
      onSelectionSound(store.state.currentMenu.items[bounded], bounded);
    }
  }

  function setSelectionSilently(next) {
    const count = store.state.currentMenu.items.length;
    if (!count) {
      store.setMenu({ selection: 0 });
      return 0;
    }
    const bounded = Math.max(0, Math.min(count - 1, next));
    if (bounded !== store.state.currentMenu.selection) {
      store.setMenu({ selection: bounded });
    }
    return bounded;
  }

  function moveSelection(delta) {
    const menu = store.state.currentMenu;
    const count = menu.items.length;
    if (!count) {
      return;
    }
    const current = menu.selection;
    const bounded = Math.max(0, Math.min(count - 1, current + delta));
    if (bounded === current) {
      if (onSelectionSound) {
        onSelectionSound(menu.items[current], current);
      }
      const currentItem = menu.items[current];
      if (currentItem && onBoundaryRepeat) {
        onBoundaryRepeat(currentItem.text);
      }
      return;
    }
    setSelection(bounded);
  }

  function handleTypeNavigation(char) {
    const menu = store.state.currentMenu;
    const count = menu.items.length;
    if (!count || !char) {
      return;
    }

    const now = performance.now() / 1000;
    if (now - lastTypeTime > typeTimeoutSeconds) {
      searchBuffer = "";
    }
    searchBuffer += char.toLowerCase();
    lastTypeTime = now;

    const current = menu.selection;
    const currentItem = menu.items[current];
    const currentText = String(currentItem?.text || "").toLowerCase();

    // Match desktop behavior: if extended buffer already matches current item, stay on it.
    if (searchBuffer.length > 1 && currentText.startsWith(searchBuffer)) {
      return;
    }

    const start = current >= 0 ? current : 0;
    for (let offset = 1; offset <= count; offset += 1) {
      const i = (start + offset) % count;
      const text = String(menu.items[i]?.text || "").toLowerCase();
      if (text.startsWith(searchBuffer)) {
        setSelection(i);
        return;
      }
    }
  }

  function activateSelection() {
    const menu = store.state.currentMenu;
    if (!menu.items.length) {
      return;
    }
    const item = menu.items[menu.selection];
    if (!item) {
      return;
    }
    onActivate(item, menu.selection);
    if (onActivateSound) {
      onActivateSound();
    }
  }

  function activateIndex(selectionIndex) {
    const menu = store.state.currentMenu;
    if (!menu.items.length) {
      return;
    }
    const bounded = setSelectionSilently(selectionIndex);
    const item = store.state.currentMenu.items[bounded];
    if (!item) {
      return;
    }
    onActivate(item, bounded);
    if (onActivateSound) {
      onActivateSound();
    }
  }

  function applySelection(selectionIndex) {
    const menu = store.state.currentMenu;
    const boundedSelection = Math.max(0, Math.min(menu.items.length - 1, selectionIndex));
    const children = listEl.children;
    for (let i = 0; i < children.length; i += 1) {
      const li = children[i];
      const active = i === boundedSelection;
      if (!isCoarsePointer) {
        li.setAttribute("aria-selected", active ? "true" : "false");
      }
      li.classList.toggle("active", active);
    }
    if (useActiveDescendant && menu.items.length > 0) {
      listEl.setAttribute("aria-activedescendant", currentOptionId(boundedSelection));
    } else {
      listEl.removeAttribute("aria-activedescendant");
    }
    lastSelection = boundedSelection;
  }

  function renderFull() {
    const menu = store.state.currentMenu;
    renderVersion += 1;
    searchBuffer = "";
    lastTypeTime = 0;
    listEl.innerHTML = "";
    if (isCoarsePointer) {
      listEl.removeAttribute("role");
      listEl.removeAttribute("aria-label");
    } else {
      listEl.setAttribute("role", "listbox");
    }
    menu.items.forEach((item, index) => {
      const li = document.createElement("li");
      li.id = currentOptionId(index);
      li.className = "menu-item";
      if (isCoarsePointer) {
        li.setAttribute("role", "presentation");
      } else {
        li.setAttribute("role", "option");
      }
      li.dataset.index = String(index);
      if (isCoarsePointer) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "menu-item-touch";
        button.textContent = item.text;
        let pointerStart = null;
        button.addEventListener("pointerdown", (event) => {
          if (event.pointerType !== "touch" && event.pointerType !== "pen") {
            pointerStart = null;
            return;
          }
          pointerStart = {
            id: event.pointerId,
            x: event.clientX,
            y: event.clientY,
            cancelled: false,
          };
        }, { passive: true });
        button.addEventListener("pointermove", (event) => {
          if (!pointerStart || pointerStart.id !== event.pointerId) {
            return;
          }
          const dx = Math.abs(event.clientX - pointerStart.x);
          const dy = Math.abs(event.clientY - pointerStart.y);
          if (dx > 12 || dy > 12) {
            pointerStart.cancelled = true;
          }
        }, { passive: true });
        button.addEventListener("pointercancel", () => {
          pointerStart = null;
        });
        button.addEventListener("pointerup", (event) => {
          if (!pointerStart || pointerStart.id !== event.pointerId) {
            return;
          }
          const started = pointerStart;
          pointerStart = null;
          if (started.cancelled) {
            return;
          }
          if (event.cancelable) {
            event.preventDefault();
          }
          suppressClickUntil = performance.now() + 750;
          activateIndex(index);
        });
        button.addEventListener("click", (event) => {
          if (performance.now() < suppressClickUntil) {
            event.preventDefault();
            return;
          }
          activateIndex(index);
        });
        li.appendChild(button);
      } else {
        li.textContent = item.text;
        li.addEventListener("click", () => {
          const wasSelected = index === store.state.currentMenu.selection;
          setSelection(index);
          if (wasSelected) {
            activateSelection();
          }
        });
        li.addEventListener("dblclick", () => {
          setSelection(index);
          activateSelection();
        });
      }
      listEl.appendChild(li);
    });
    applySelection(menu.selection);
  }

  listEl.addEventListener("focus", () => {
    applySelection(store.state.currentMenu.selection);
  });

  store.subscribe(() => {
    const menu = store.state.currentMenu;
    const nextStructureSnapshot = menuStructureSnapshot(menu);
    if (nextStructureSnapshot !== lastStructureSnapshot) {
      lastStructureSnapshot = nextStructureSnapshot;
      renderFull();
      return;
    }
    if (menu.selection !== lastSelection) {
      applySelection(menu.selection);
    }
  });
  lastStructureSnapshot = menuStructureSnapshot(store.state.currentMenu);
  renderFull();

  return {
    setSelection,
    moveSelection,
    handleTypeNavigation,
    activateSelection,
    getElement() {
      return listEl;
    },
    getCurrentItemText() {
      const menu = store.state.currentMenu;
      if (!menu.items.length) {
        return "";
      }
      const currentItem = menu.items[Math.max(0, Math.min(menu.selection, menu.items.length - 1))];
      return currentItem?.text || "";
    },
  };
}
