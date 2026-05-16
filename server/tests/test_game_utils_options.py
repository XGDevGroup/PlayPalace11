from dataclasses import dataclass
from types import SimpleNamespace

from server.game_utils.actions import ActionSet
from server.game_utils.options import (
    BoolOption,
    FloatOption,
    GameOptions,
    IntOption,
    MenuOption,
    MultiSelectOption,
    OptionGroupMeta,
    get_option_meta,
    get_option_field_group,
    get_visibility_conditions,
    multi_select_field,
    option_field,
    option_group,
)
from server.game_utils.options import OptionsHandlerMixin
from server.game_utils.event_handling_mixin import EventHandlingMixin
from server.games.base import Player, TransientDisplayState
from server.game_utils.menu_management_mixin import TRANSIENT_DISPLAY_MENU_ID
from server.messages.localization import Localization


class OptionsUser:
    def __init__(self, locale: str = "en"):
        self.locale = locale
        self._last_speak = None
        self.menus: list[tuple[str, list]] = []
        self.menu_kwargs: list[dict] = []
        self.removed_menus: list[str] = []
        self._current_menus: dict[str, dict] = {}

    def speak_l(self, key, **kwargs):
        self._last_speak = (key, kwargs)

    def show_menu(self, menu_id, items, **kwargs):
        self.menus.append((menu_id, items))
        self.menu_kwargs.append(kwargs)
        self._current_menus[menu_id] = {"items": items, **kwargs}

    def remove_menu(self, menu_id):
        self.removed_menus.append(menu_id)
        self._current_menus.pop(menu_id, None)


class OptionsGame:
    def __init__(self, user: OptionsUser):
        self._user = user
        self.players: list[Player] = []
        self._action_sets: dict[tuple[str, str], ActionSet] = {}
        self._options_path: dict[str, list[str]] = {}
        self._transient_display_state: dict[str, TransientDisplayState] = {}

    def get_user(self, player: Player) -> OptionsUser | None:
        return self._user

    def get_action_set(self, player: Player, name: str) -> ActionSet | None:
        return self._action_sets.get((player.id, name))

    def set_action_set(self, player: Player, action_set: ActionSet) -> None:
        self._action_sets[(player.id, action_set.name)] = action_set

    def _get_transient_display_state(self, player: Player) -> TransientDisplayState | None:
        return self._transient_display_state.get(player.id)


class ReadonlyOptionsGame(OptionsHandlerMixin):
    def __init__(self, user: OptionsUser, options: GameOptions):
        self._user = user
        self.options = options
        self.players: list[Player] = []
        self._transient_display_state: dict[str, TransientDisplayState] = {}
        self.rebuilt_players: list[str] = []

    def get_user(self, player: Player) -> OptionsUser | None:
        return self._user

    def rebuild_player_menu(self, player: Player) -> None:
        self.rebuilt_players.append(player.id)

    def _get_transient_display_state(self, player: Player) -> TransientDisplayState | None:
        return self._transient_display_state.get(player.id)

    def _show_transient_display(
        self,
        player: Player,
        *,
        kind: str,
        items: list,
        multiletter: bool,
        path: list[str] | None = None,
        position: int | None = None,
    ) -> None:
        existing = self._transient_display_state.get(player.id)
        self._transient_display_state[player.id] = TransientDisplayState(
            kind=kind,
            path=list(path or []),
            positions=existing.positions if existing else {},
        )
        self._user.show_menu(
            TRANSIENT_DISPLAY_MENU_ID,
            items,
            multiletter=multiletter,
            position=position,
        )

    def _close_transient_display(
        self,
        player: Player,
        *,
        speak_key: str | None = None,
        rebuild_menu: bool = True,
    ) -> None:
        self._user.remove_menu(TRANSIENT_DISPLAY_MENU_ID)
        self._transient_display_state.pop(player.id, None)
        if rebuild_menu:
            self.rebuild_player_menu(player)


class ViewerRebuildGuardGame(EventHandlingMixin, OptionsHandlerMixin):
    def __init__(self, user: OptionsUser, options: GameOptions):
        self._user = user
        self.options = options
        self.players: list[Player] = []
        self._transient_display_state: dict[str, TransientDisplayState] = {}
        self._pending_actions: dict[str, str] = {}
        self._actions_menu_open: set[str] = set()

    def get_user(self, player: Player) -> OptionsUser | None:
        return self._user

    def _get_transient_display_state(self, player: Player) -> TransientDisplayState | None:
        return self._transient_display_state.get(player.id)

    def _is_transient_display_open(self, player: Player) -> bool:
        return player.id in self._transient_display_state

    def _show_transient_display(
        self,
        player: Player,
        *,
        kind: str,
        items: list,
        multiletter: bool,
        path: list[str] | None = None,
        position: int | None = None,
    ) -> None:
        existing = self._transient_display_state.get(player.id)
        self._transient_display_state[player.id] = TransientDisplayState(
            kind=kind,
            path=list(path or []),
            positions=existing.positions if existing else {},
        )
        self._user.show_menu(
            TRANSIENT_DISPLAY_MENU_ID,
            items,
            multiletter=multiletter,
            position=position,
        )

    def _close_transient_display(
        self,
        player: Player,
        *,
        speak_key: str | None = None,
        rebuild_menu: bool = True,
    ) -> None:
        self._user.remove_menu(TRANSIENT_DISPLAY_MENU_ID)
        self._transient_display_state.pop(player.id, None)


@dataclass
class DemoOptions(GameOptions):
    target_score: int = option_field(
        IntOption(
            default=5,
            min_val=1,
            max_val=20,
            value_key="score",
            label="opt-score",
            prompt="opt-score-prompt",
            change_msg="opt-score-change",
        )
    )
    theme: str = option_field(
        MenuOption(
            default="classic",
            choices=["classic", "neon"],
            label="opt-theme",
            prompt="opt-theme-prompt",
            change_msg="opt-theme-change",
            choice_labels={"classic": "label-classic", "neon": "label-neon"},
        )
    )
    speed: float = option_field(
        FloatOption(
            default=1.5,
            min_val=0.5,
            max_val=3.0,
            decimal_places=1,
            label="opt-speed",
            prompt="opt-speed-prompt",
            change_msg="opt-speed-change",
        )
    )


def test_int_option_create_action_and_validate(monkeypatch):
    option = IntOption(
        default=5,
        min_val=1,
        max_val=10,
        value_key="score",
        label="opt-score",
        prompt="opt-score-prompt",
        change_msg="opt-score-change",
    )

    def fake_get(locale, key, **kwargs):
        return f"{key}:{kwargs.get('score', '')}"

    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        fake_get,
    )

    player = Player(id="p1", name="Alice")
    action = option.create_action("target_score", SimpleNamespace(), player, 7, "en")

    assert action.id == "set_target_score"
    assert action.input_request.prompt == "opt-score-prompt"

    ok, value = option.validate_and_convert("999")
    assert ok is True and value == 10

    ok, value = option.validate_and_convert("abc")
    assert ok is False and value == "abc"


def test_float_option_validate_and_convert(monkeypatch):
    option = FloatOption(
        default=2.0,
        min_val=0.5,
        max_val=5.0,
        decimal_places=2,
        label="opt-speed",
        prompt="opt-speed-prompt",
        change_msg="opt-speed-change",
    )

    ok, value = option.validate_and_convert("6.789")
    assert ok is True and value == 5.0

    ok, value = option.validate_and_convert("1.2345")
    assert ok is True and value == 1.23

    ok, value = option.validate_and_convert("not-a-number")
    assert ok is False and value == "not-a-number"


def test_menu_option_localized_choice_and_action(monkeypatch):
    menu = MenuOption(
        default="classic",
        choices=["classic", "neon"],
        label="opt-theme",
        prompt="opt-theme-prompt",
        change_msg="opt-theme-change",
        choice_labels={"classic": "label-classic"},
    )

    def fake_get(locale, key, **kwargs):
        mapping = {
            "label-classic": "Classic Label",
            "opt-theme": f"Theme:{kwargs.get('mode', '')}",
        }
        return mapping.get(key, key)

    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        fake_get,
    )

    assert menu.get_localized_choice("classic", "en") == "Classic Label"
    action = menu.create_action(
        "style",
        SimpleNamespace(),
        Player(id="p1", name="Alice"),
        "classic",
        "en",
    )
    assert action.id == "set_style"
    assert action.input_request.prompt == "opt-theme-prompt"


def test_option_field_and_get_option_meta():
    meta = get_option_meta(DemoOptions, "theme")
    assert isinstance(meta, MenuOption)

    option_instance = DemoOptions()
    metas = option_instance.get_option_metas()
    assert set(metas.keys()) == {"target_score", "theme", "speed"}


def test_game_options_create_action_set_and_update_labels(monkeypatch):
    options = DemoOptions()
    user = OptionsUser()
    game = OptionsGame(user)
    player = Player(id="p1", name="Alice")
    game.players = [player]

    def fake_get(locale, key, **kwargs):
        mapping = {
            "opt-score": f"Score:{kwargs.get('score', '')}",
            "opt-theme": f"Theme:{kwargs.get('mode', '')}",
            "opt-speed": f"Speed:{kwargs.get('value', '')}",
            "label-classic": "Classic",
            "label-neon": "Neon",
        }
        return mapping.get(key, key)

    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        fake_get,
    )

    action_set = options.create_options_action_set(game, player)
    game.set_action_set(player, action_set)

    assert action_set.get_action("set_target_score").label == "Score:5"
    assert action_set.get_action("set_theme").label == "Theme:Classic"

    options.target_score = 12
    options.theme = "neon"
    options.speed = 2.3

    options.update_options_labels(game)

    assert action_set.get_action("set_target_score").label == "Score:12"
    assert action_set.get_action("set_theme").label == "Theme:Neon"
    assert action_set.get_action("set_speed").label == "Speed:2.3"


# =========================================================================
# Linked visibility tests
# =========================================================================


@dataclass
class LinkedVisibilityOptions(GameOptions):
    reshuffle_limit: int = option_field(
        IntOption(
            default=3,
            min_val=0,
            max_val=10,
            label="opt-limit",
            prompt="opt-limit-prompt",
            change_msg="opt-limit-change",
        )
    )
    reshuffle_penalty: int = option_field(
        IntOption(
            default=1,
            min_val=0,
            max_val=5,
            label="opt-penalty",
            prompt="opt-penalty-prompt",
            change_msg="opt-penalty-change",
        ),
        visible_when=("reshuffle_limit", lambda v: v > 0),
    )


def test_visible_when_condition_true(monkeypatch):
    """Option is included when visible_when condition is true."""

    def fake_get(locale, key, **kwargs):
        return key

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    options = LinkedVisibilityOptions()
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    action_set = options.create_options_action_set(game, player)
    assert action_set.get_action("set_reshuffle_limit") is not None
    assert action_set.get_action("set_reshuffle_penalty") is not None


def test_visible_when_condition_false(monkeypatch):
    """Option is excluded when visible_when condition is false."""

    def fake_get(locale, key, **kwargs):
        return key

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    options = LinkedVisibilityOptions()
    options.reshuffle_limit = 0  # Condition: v > 0 → False
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    action_set = options.create_options_action_set(game, player)
    assert action_set.get_action("set_reshuffle_limit") is not None
    assert action_set.get_action("set_reshuffle_penalty") is None


def test_visible_when_updates_on_label_refresh(monkeypatch):
    """Visibility changes when referenced option changes and labels update."""

    def fake_get(locale, key, **kwargs):
        return key

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    options = LinkedVisibilityOptions()
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    action_set = options.create_options_action_set(game, player)
    game.set_action_set(player, action_set)
    assert action_set.get_action("set_reshuffle_penalty") is not None

    # Change limit to 0, update labels
    options.reshuffle_limit = 0
    options.update_options_labels(game)
    assert action_set.get_action("set_reshuffle_penalty") is None

    # Change back to non-zero
    options.reshuffle_limit = 5
    options.update_options_labels(game)
    assert action_set.get_action("set_reshuffle_penalty") is not None


def test_get_visibility_conditions_helper():
    """get_visibility_conditions returns the correct list or None."""
    conds = get_visibility_conditions(LinkedVisibilityOptions, "reshuffle_penalty")
    assert conds is not None
    assert len(conds) == 1
    assert conds[0][0] == "reshuffle_limit"
    assert conds[0][1](5) is True
    assert conds[0][1](0) is False

    assert get_visibility_conditions(LinkedVisibilityOptions, "reshuffle_limit") is None


# =========================================================================
# Option group tests
# =========================================================================


@dataclass
class GroupedOptions(GameOptions):
    rounds: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=10,
            label="opt-rounds",
            prompt="opt-rounds-prompt",
            change_msg="opt-rounds-change",
        )
    )
    bear_settings: None = option_group(label="opt-bear-settings")
    bear_speed: int = option_field(
        IntOption(
            default=5,
            min_val=1,
            max_val=10,
            label="opt-bear-speed",
            prompt="opt-bear-speed-prompt",
            change_msg="opt-bear-speed-change",
        ),
        group="bear_settings",
    )
    bear_aggression: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=10,
            label="opt-bear-aggr",
            prompt="opt-bear-aggr-prompt",
            change_msg="opt-bear-aggr-change",
        ),
        group="bear_settings",
    )


def test_option_group_top_level_shows_group_header(monkeypatch):
    """At top level, group header is shown but group children are not."""

    def fake_get(locale, key, **kwargs):
        return key

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    options = GroupedOptions()
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    action_set = options.create_options_action_set(game, player)
    # Top level: rounds + bear_settings group header
    assert action_set.get_action("set_rounds") is not None
    assert action_set.get_action("group_bear_settings") is not None
    # Children should NOT be at top level
    assert action_set.get_action("set_bear_speed") is None
    assert action_set.get_action("set_bear_aggression") is None


def test_option_group_navigate_into_group(monkeypatch):
    """Navigating into a group shows its children and a back action."""

    def fake_get(locale, key, **kwargs):
        return key

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    options = GroupedOptions()
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    # Navigate into bear_settings
    game._options_path[player.id] = ["bear_settings"]
    action_set = options.create_options_action_set(game, player)

    # Should show children + back
    assert action_set.get_action("set_bear_speed") is not None
    assert action_set.get_action("set_bear_aggression") is not None
    assert action_set.get_action("options_back") is not None
    # Should NOT show top-level options or the group header
    assert action_set.get_action("set_rounds") is None
    assert action_set.get_action("group_bear_settings") is None


def test_option_group_back_returns_to_top(monkeypatch):
    """Navigating back from a group shows top-level options again."""

    def fake_get(locale, key, **kwargs):
        return key

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    options = GroupedOptions()
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    # Start in group, then go back
    game._options_path[player.id] = ["bear_settings"]
    action_set = options.create_options_action_set(game, player)
    assert action_set.get_action("set_bear_speed") is not None

    # Go back
    game._options_path[player.id] = []
    action_set2 = options.create_options_action_set(game, player)
    assert action_set2.get_action("set_rounds") is not None
    assert action_set2.get_action("group_bear_settings") is not None
    assert action_set2.get_action("set_bear_speed") is None


def test_get_option_field_group_helper():
    """get_option_field_group returns correct group or None."""
    assert get_option_field_group(GroupedOptions, "bear_speed") == "bear_settings"
    assert get_option_field_group(GroupedOptions, "bear_aggression") == "bear_settings"
    assert get_option_field_group(GroupedOptions, "rounds") is None


def test_option_group_meta_from_class():
    """OptionGroupMeta is retrievable from the options class."""
    groups = GroupedOptions().get_option_group_metas()
    assert "bear_settings" in groups
    assert isinstance(groups["bear_settings"], OptionGroupMeta)
    assert groups["bear_settings"].label == "opt-bear-settings"


# =========================================================================
# Nested group tests (groups within groups)
# =========================================================================


@dataclass
class NestedGroupOptions(GameOptions):
    top_option: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=5,
            label="opt-top",
            prompt="opt-top-prompt",
            change_msg="opt-top-change",
        )
    )
    outer_group: None = option_group(label="opt-outer")
    inner_group: None = option_group(label="opt-inner")
    inner_option: int = option_field(
        IntOption(
            default=2,
            min_val=1,
            max_val=10,
            label="opt-inner-val",
            prompt="opt-inner-prompt",
            change_msg="opt-inner-change",
        ),
        group="inner_group",
    )
    outer_option: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=10,
            label="opt-outer-val",
            prompt="opt-outer-prompt",
            change_msg="opt-outer-change",
        ),
        group="outer_group",
    )


def _setup_nested_group_test(monkeypatch):
    """Helper: patch localization and return (options, game, player)."""
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )
    # inner_group is a child of outer_group
    # We need to set the group metadata on inner_group field
    # Actually we need to define inner_group with group="outer_group"
    # Let me re-check how option_group works - it uses field metadata, not option_field metadata
    # option_group doesn't take a group param. We need to check if groups can be nested.
    # Looking at the code: option_group creates a field with "option_group_meta" metadata.
    # get_option_field_group looks for "option_group" metadata.
    # To nest, we'd need option_group to also support a group param... but it doesn't currently.
    # For now, inner_group as defined above is a top-level group, not nested under outer_group.
    pass


# Note: To support groups within groups, option_group() would need a group parameter.
# The current implementation supports one level of nesting for groups.
# Deep nesting can be achieved by putting an option_group field inside a group.
# This would require extending option_group() with a group parameter - deferred for now.


# =========================================================================
# Multi-select tests
# =========================================================================


@dataclass
class MultiSelectOptions(GameOptions):
    packs: list[str] = multi_select_field(
        MultiSelectOption(
            default=["standard"],
            choices=["standard", "premium", "classic"],
            label="opt-packs",
            change_msg="opt-packs-change",
            min_selected=1,
        )
    )
    other_option: int = option_field(
        IntOption(
            default=5,
            min_val=1,
            max_val=10,
            label="opt-other",
            prompt="opt-other-prompt",
            change_msg="opt-other-change",
        )
    )


def test_multi_select_default_value():
    """Multi-select field has correct default value."""
    options = MultiSelectOptions()
    assert options.packs == ["standard"]


def test_multi_select_default_is_independent_copy():
    """Each instance gets its own copy of the default list."""
    o1 = MultiSelectOptions()
    o2 = MultiSelectOptions()
    o1.packs.append("premium")
    assert o2.packs == ["standard"]


def test_multi_select_top_level_shows_parent_action(monkeypatch):
    """At top level, multi-select shows a parent action with count."""

    def fake_get(locale, key, **kwargs):
        if key == "opt-packs":
            return f"Packs ({kwargs.get('count', 0)} selected)"
        return key

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    options = MultiSelectOptions()
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    action_set = options.create_options_action_set(game, player)
    parent = action_set.get_action("multiselect_packs")
    assert parent is not None
    assert "1 selected" in parent.label
    assert action_set.get_action("set_other_option") is not None


def test_multi_select_navigate_in_shows_toggles(monkeypatch):
    """Navigating into a multi-select shows toggle actions for each choice."""

    def fake_get(locale, key, **kwargs):
        return key

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    options = MultiSelectOptions()
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    # Navigate into multi-select
    game._options_path[player.id] = ["packs"]
    action_set = options.create_options_action_set(game, player)

    # Should show toggles for each choice + back
    assert action_set.get_action("mstoggle_packs_standard") is not None
    assert action_set.get_action("mstoggle_packs_premium") is not None
    assert action_set.get_action("mstoggle_packs_classic") is not None
    assert action_set.get_action("options_back") is not None
    # Parent action should NOT be shown
    assert action_set.get_action("multiselect_packs") is None


def test_multi_select_toggle_labels_show_on_off(monkeypatch):
    """Toggle labels show on/off state for each choice."""

    def fake_get(locale, key, **kwargs):
        return key

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    options = MultiSelectOptions()
    options.packs = ["standard", "premium"]
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]
    game._options_path[player.id] = ["packs"]

    action_set = options.create_options_action_set(game, player)

    standard = action_set.get_action("mstoggle_packs_standard")
    premium = action_set.get_action("mstoggle_packs_premium")
    classic = action_set.get_action("mstoggle_packs_classic")

    assert "option-on" in standard.label
    assert "option-on" in premium.label
    assert "option-off" in classic.label


def test_multi_select_option_meta():
    """MultiSelectOption metadata is accessible via get_option_meta."""
    meta = get_option_meta(MultiSelectOptions, "packs")
    assert isinstance(meta, MultiSelectOption)
    assert meta.min_selected == 1
    choices = meta.get_choices()
    assert choices == ["standard", "premium", "classic"]


def test_multi_select_with_callable_choices():
    """MultiSelectOption works with callable choices."""
    items = ["a", "b", "c"]
    meta = MultiSelectOption(
        default=["a"],
        choices=lambda: items,
        label="test",
        change_msg="test-change",
    )
    assert meta.get_choices() == ["a", "b", "c"]


def test_multi_select_choice_labels(monkeypatch):
    """MultiSelectOption supports localized choice labels."""

    def fake_get(locale, key, **kwargs):
        mapping = {"label-std": "Standard Pack", "label-prem": "Premium Pack"}
        return mapping.get(key, key)

    monkeypatch.setattr("server.game_utils.options.Localization.get", fake_get)

    meta = MultiSelectOption(
        default=["standard"],
        choices=["standard", "premium"],
        label="opt-packs",
        change_msg="opt-packs-change",
        choice_labels={"standard": "label-std", "premium": "label-prem"},
    )
    assert meta.get_localized_choice("standard", "en") == "Standard Pack"
    assert meta.get_localized_choice("premium", "en") == "Premium Pack"


def test_multi_select_max_selected():
    """MultiSelectOption respects max_selected (0 = no limit)."""
    meta = MultiSelectOption(
        default=["a"],
        choices=["a", "b", "c", "d"],
        label="test",
        change_msg="test-change",
        max_selected=2,
    )
    assert meta.max_selected == 2

    # Default (no limit)
    meta_no_limit = MultiSelectOption(
        default=["a"],
        choices=["a", "b", "c"],
        label="test",
        change_msg="test-change",
    )
    assert meta_no_limit.max_selected == 0


# =========================================================================
# Combined feature tests
# =========================================================================


@dataclass
class CombinedOptions(GameOptions):
    limit: int = option_field(
        IntOption(
            default=3,
            min_val=0,
            max_val=10,
            label="opt-limit",
            prompt="opt-limit-prompt",
            change_msg="opt-limit-change",
        )
    )
    penalty: int = option_field(
        IntOption(
            default=1,
            min_val=0,
            max_val=5,
            label="opt-penalty",
            prompt="opt-penalty-prompt",
            change_msg="opt-penalty-change",
        ),
        visible_when=("limit", lambda v: v > 0),
    )
    settings_group: None = option_group(label="opt-settings")
    inner_option: bool = option_field(
        BoolOption(
            default=False,
            label="opt-inner-bool",
            change_msg="opt-inner-bool-change",
        ),
        group="settings_group",
    )
    packs: list[str] = multi_select_field(
        MultiSelectOption(
            default=["a"],
            choices=["a", "b", "c"],
            label="opt-packs",
            change_msg="opt-packs-change",
        )
    )


def test_combined_top_level_all_features(monkeypatch):
    """Top level shows ungrouped options, group header, multi-select parent."""
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    options = CombinedOptions()
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    action_set = options.create_options_action_set(game, player)

    # Top-level options
    assert action_set.get_action("set_limit") is not None
    assert action_set.get_action("set_penalty") is not None  # limit > 0
    # Group header
    assert action_set.get_action("group_settings_group") is not None
    # Multi-select parent
    assert action_set.get_action("multiselect_packs") is not None
    # Group child hidden at top level
    assert action_set.get_action("toggle_inner_option") is None


def test_combined_visibility_hides_when_condition_false(monkeypatch):
    """Combined: linked visibility hides penalty when limit is 0."""
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    options = CombinedOptions()
    options.limit = 0
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    action_set = options.create_options_action_set(game, player)
    assert action_set.get_action("set_penalty") is None
    assert action_set.get_action("set_limit") is not None


def test_game_options_view_top_level_shows_groups_readonly_items_and_back(monkeypatch):
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    options = GroupedOptions()
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    items = options.build_game_options_view_items(game, player)
    item_ids = [item.id for item in items]

    assert "readonly_rounds" in item_ids
    assert "group_bear_settings" in item_ids
    assert "readonly_bear_speed" not in item_ids
    assert item_ids[-1] == "transient_display_back"


def test_game_options_view_multiselect_submenu_shows_readonly_entries(monkeypatch):
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    options = MultiSelectOptions()
    options.packs = ["standard", "premium"]
    game = OptionsGame(OptionsUser())
    player = Player(id="p1", name="Alice")
    game.players = [player]
    game._transient_display_state = {
        player.id: TransientDisplayState(kind="game_options", path=["packs"])
    }

    items = options.build_game_options_view_items(game, player)
    item_ids = [item.id for item in items]

    assert "readonly_packs_standard" in item_ids
    assert "readonly_packs_premium" in item_ids
    assert "readonly_packs_classic" in item_ids
    assert item_ids[-1] == "transient_display_back"


def test_game_options_view_leaf_selection_is_ignored(monkeypatch):
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    user = OptionsUser()
    game = ReadonlyOptionsGame(user, GroupedOptions())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    game._action_check_game_options(player, "check_game_options")
    assert user.menus[-1][0] == TRANSIENT_DISPLAY_MENU_ID

    game._handle_game_options_display_selection(player, "readonly_rounds")

    assert game._transient_display_state[player.id].path == []
    assert user.removed_menus == []
    assert game.rebuilt_players == []


def test_game_options_view_uses_non_multiletter_menu(monkeypatch):
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    user = OptionsUser()
    game = ReadonlyOptionsGame(user, GroupedOptions())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    game._action_check_game_options(player, "check_game_options")

    assert user.menu_kwargs[-1]["multiletter"] is False


def test_game_options_submenu_opens_with_first_item_focused(monkeypatch):
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    user = OptionsUser()
    game = ReadonlyOptionsGame(user, GroupedOptions())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    game._action_check_game_options(player, "check_game_options")
    game._handle_game_options_display_selection(player, "group_bear_settings")

    assert user.menu_kwargs[-1]["position"] == 1


def test_game_options_back_restores_previous_focus_position(monkeypatch):
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    user = OptionsUser()
    game = ReadonlyOptionsGame(user, GroupedOptions())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    game._action_check_game_options(player, "check_game_options")
    game._transient_display_state[player.id].positions[()] = 2
    game._handle_game_options_display_selection(player, "group_bear_settings")
    game._handle_game_options_display_selection(player, "transient_display_back")

    assert user.menu_kwargs[-1]["position"] == 2


def test_game_options_view_back_closes_at_root(monkeypatch):
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    user = OptionsUser()
    game = ReadonlyOptionsGame(user, GroupedOptions())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    game._action_check_game_options(player, "check_game_options")
    game._handle_game_options_display_selection(player, "transient_display_back")

    assert user.removed_menus == [TRANSIENT_DISPLAY_MENU_ID]
    assert player.id not in game._transient_display_state
    assert game.rebuilt_players == [player.id]


def test_check_game_options_without_options_speaks_message(monkeypatch):
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    user = OptionsUser()
    game = ReadonlyOptionsGame(user, GroupedOptions())
    del game.options
    player = Player(id="p1", name="Alice")
    game.players = [player]

    game._action_check_game_options(player, "check_game_options")

    assert user._last_speak == ("no-game-options", {})


def test_game_options_view_blocks_post_action_rebuilds(monkeypatch):
    monkeypatch.setattr(
        "server.game_utils.options.Localization.get",
        lambda locale, key, **kw: key,
    )

    user = OptionsUser()
    game = ViewerRebuildGuardGame(user, GroupedOptions())
    player = Player(id="p1", name="Alice")
    game.players = [player]

    assert game._should_rebuild_after_keybind(player, executed_any=True) is True

    game._action_check_game_options(player, "check_game_options")

    assert player.id in game._transient_display_state
    assert game._should_rebuild_after_keybind(player, executed_any=True) is False
