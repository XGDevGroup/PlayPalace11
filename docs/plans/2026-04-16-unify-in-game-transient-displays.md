# Unify In-Game Transient Displays

## Summary
Refactor all in-game temporary displays so they use one shared server-side display system instead of separate ad hoc paths like `status_box`, `game_options_view`, and context-specific special cases. The new system should support both:
- flat read-only displays like detailed scores, board views, and in-game Who’s Online
- nested read-only displays like `Alt+O` game options

The server will own modal behavior. When a transient display is open for a player, server-side event handling should ignore other game commands and only accept input for that display until it is closed.

## Implementation Changes
- Add a single per-player transient-display state to `server/games/base.py`, replacing the current split between `_status_box_open` and `_game_options_view_path`.
  - Store one object per player with at least:
    - display type/id
    - current navigation path
    - whether leaf Enter closes or is ignored
  - Keep `_actions_menu_open` separate; it is a different interaction model.

- Replace the current `status_box` primitive in `server/game_utils/menu_management_mixin.py` with a more general read-only display API.
  - Introduce one shared method to show a transient display menu for a player.
  - Support flat displays by passing prebuilt line items.
  - Support nested displays by passing a display id plus a builder callback or resolver on the game/options side.
  - Preserve the current UX for flat displays:
    - listbox presentation
    - `EscapeBehavior.SELECT_LAST`
    - Enter on a leaf closes for legacy score/board style displays
  - Support configurable leaf behavior for nested displays:
    - `Alt+O` leaf Enter should be ignored
    - submenu items should navigate
    - `Back` should navigate up and close at root

- Move `Alt+O` off its custom `game_options_view` menu id in `server/game_utils/options.py` and reimplement it on top of the shared transient-display API.
  - Reuse the existing readonly option label generation and nested path logic.
  - Keep nested group and multiselect navigation.
  - Keep `No Game Options` behavior for games without an `options` field.

- Update event handling in `server/game_utils/event_handling_mixin.py`.
  - Before processing `keybind`, `menu`, or `editbox` events for normal gameplay, check whether the player currently has a transient display open.
  - If a transient display is open:
    - allow only display-related input
    - ignore unrelated game keybinds and game menu actions server-side
    - do not speak error messages for ignored blocked commands
  - Route menu events for transient displays through one shared handler instead of separate `status_box` and `game_options_view` branches.
  - Remove the current scattered rebuild guards that special-case `_status_box_open` and `_game_options_view_path`, replacing them with one “transient display open” check.

- Migrate existing display producers to the unified path.
  - Shared detailed scores in `server/game_utils/game_scores_mixin.py`
  - Yahtzee scoresheet in `server/games/yahtzee/game.py`
  - Ludo board in `server/games/ludo/game.py`
  - Chess board in `server/games/chess/game.py`
  - In-game Who’s Online from `server/core/server.py`
  - `Alt+O` game options in `server/game_utils/options.py`

## Behavioral Rules
- Flat display behavior:
  - Enter on any item closes the display
  - Escape closes via select-last behavior
  - No gameplay keybinds/actions should execute while open
- Nested display behavior:
  - Enter on submenu items navigates in
  - Enter on `Back` navigates up or closes at root
  - Enter on leaf read-only items does nothing and does not speak an error
  - No gameplay keybinds/actions should execute while open
- Rebuild behavior:
  - While a transient display is open, turn-menu rebuild/update calls should not replace it
  - Closing the display restores the normal turn menu cleanly

## Test Plan
- Add focused tests for the shared transient-display handler:
  - opening a flat display suppresses normal rebuilds
  - opening a nested display suppresses normal rebuilds
  - unrelated keybinds are ignored while any transient display is open
  - unrelated menu actions are ignored while any transient display is open
  - flat Enter closes
  - nested leaf Enter is ignored
  - nested Back unwinds path and closes at root
- Update existing tests that currently assume `_status_box_open` or `game_options_view` internals.
- Keep explicit regression coverage for:
  - `Shift+S` detailed scores
  - Yahtzee scoresheet
  - Ludo board
  - in-game `Shift+F2`
  - `Alt+O` with and without game options

## Assumptions
- Server-side blocking is the source of truth; no client changes are required for command blocking
- `Actions menu` remains a separate interaction model and is not merged into the transient-display state
- The visible UI stays listbox/menu based; this is a behavioral unification refactor, not a presentation redesign
