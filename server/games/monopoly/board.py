"""Board definitions for Monopoly.

The gameplay engine is written against :class:`BoardDefinition` so themed
boards can be added later without changing the turn loop.
"""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_BOARD_ID = "classic"
BOARD_SIZE = 40
STARTING_CASH = 1500
PASS_GO_CASH = 200
TOTAL_HOUSES = 32
TOTAL_HOTELS = 12

PURCHASABLE_KINDS = {"street", "railroad", "utility"}


@dataclass(frozen=True)
class MonopolySpace:
    """A space on a Monopoly board."""

    index: int
    space_id: str
    name: str
    kind: str
    price: int = 0
    rents: tuple[int, ...] = ()
    color_group: str = ""
    house_cost: int = 0
    mortgage_value: int = 0
    tax_amount: int = 0

    @property
    def is_purchasable(self) -> bool:
        return self.kind in PURCHASABLE_KINDS


@dataclass(frozen=True)
class BoardDefinition:
    """Static data for one playable Monopoly board."""

    board_id: str
    name: str
    spaces: tuple[MonopolySpace, ...]
    starting_cash: int = STARTING_CASH
    pass_go_cash: int = PASS_GO_CASH
    total_houses: int = TOTAL_HOUSES
    total_hotels: int = TOTAL_HOTELS

    @property
    def space_by_id(self) -> dict[str, MonopolySpace]:
        return {space.space_id: space for space in self.spaces}

    @property
    def purchasable_spaces(self) -> tuple[MonopolySpace, ...]:
        return tuple(space for space in self.spaces if space.is_purchasable)

    @property
    def color_group_space_ids(self) -> dict[str, tuple[str, ...]]:
        groups: dict[str, list[str]] = {}
        for space in self.spaces:
            if space.color_group:
                groups.setdefault(space.color_group, []).append(space.space_id)
        return {group: tuple(ids) for group, ids in groups.items()}

    def get_space(self, space_id: str) -> MonopolySpace:
        return self.space_by_id[space_id]

    def get_space_at(self, index: int) -> MonopolySpace:
        return self.spaces[index % len(self.spaces)]


def _street(
    index: int,
    space_id: str,
    name: str,
    price: int,
    rents: tuple[int, int, int, int, int, int],
    color_group: str,
    house_cost: int,
) -> MonopolySpace:
    return MonopolySpace(
        index=index,
        space_id=space_id,
        name=name,
        kind="street",
        price=price,
        rents=rents,
        color_group=color_group,
        house_cost=house_cost,
        mortgage_value=price // 2,
    )


def _railroad(index: int, space_id: str, name: str) -> MonopolySpace:
    return MonopolySpace(
        index=index,
        space_id=space_id,
        name=name,
        kind="railroad",
        price=200,
        rents=(25, 50, 100, 200),
        mortgage_value=100,
    )


def _utility(index: int, space_id: str, name: str) -> MonopolySpace:
    return MonopolySpace(
        index=index,
        space_id=space_id,
        name=name,
        kind="utility",
        price=150,
        mortgage_value=75,
    )


CLASSIC_SPACES: tuple[MonopolySpace, ...] = (
    MonopolySpace(0, "go", "GO", "go"),
    _street(
        1,
        "mediterranean_avenue",
        "Mediterranean Avenue",
        60,
        (2, 10, 30, 90, 160, 250),
        "brown",
        50,
    ),
    MonopolySpace(2, "community_chest_1", "Community Chest", "community_chest"),
    _street(3, "baltic_avenue", "Baltic Avenue", 60, (4, 20, 60, 180, 320, 450), "brown", 50),
    MonopolySpace(4, "income_tax", "Income Tax", "tax", tax_amount=200),
    _railroad(5, "reading_railroad", "Reading Railroad"),
    _street(
        6,
        "oriental_avenue",
        "Oriental Avenue",
        100,
        (6, 30, 90, 270, 400, 550),
        "light_blue",
        50,
    ),
    MonopolySpace(7, "chance_1", "Chance", "chance"),
    _street(
        8,
        "vermont_avenue",
        "Vermont Avenue",
        100,
        (6, 30, 90, 270, 400, 550),
        "light_blue",
        50,
    ),
    _street(
        9,
        "connecticut_avenue",
        "Connecticut Avenue",
        120,
        (8, 40, 100, 300, 450, 600),
        "light_blue",
        50,
    ),
    MonopolySpace(10, "jail", "Jail / Just Visiting", "jail"),
    _street(
        11,
        "st_charles_place",
        "St. Charles Place",
        140,
        (10, 50, 150, 450, 625, 750),
        "pink",
        100,
    ),
    _utility(12, "electric_company", "Electric Company"),
    _street(13, "states_avenue", "States Avenue", 140, (10, 50, 150, 450, 625, 750), "pink", 100),
    _street(
        14,
        "virginia_avenue",
        "Virginia Avenue",
        160,
        (12, 60, 180, 500, 700, 900),
        "pink",
        100,
    ),
    _railroad(15, "pennsylvania_railroad", "Pennsylvania Railroad"),
    _street(
        16,
        "st_james_place",
        "St. James Place",
        180,
        (14, 70, 200, 550, 750, 950),
        "orange",
        100,
    ),
    MonopolySpace(17, "community_chest_2", "Community Chest", "community_chest"),
    _street(
        18,
        "tennessee_avenue",
        "Tennessee Avenue",
        180,
        (14, 70, 200, 550, 750, 950),
        "orange",
        100,
    ),
    _street(
        19,
        "new_york_avenue",
        "New York Avenue",
        200,
        (16, 80, 220, 600, 800, 1000),
        "orange",
        100,
    ),
    MonopolySpace(20, "free_parking", "Free Parking", "free_parking"),
    _street(
        21,
        "kentucky_avenue",
        "Kentucky Avenue",
        220,
        (18, 90, 250, 700, 875, 1050),
        "red",
        150,
    ),
    MonopolySpace(22, "chance_2", "Chance", "chance"),
    _street(
        23,
        "indiana_avenue",
        "Indiana Avenue",
        220,
        (18, 90, 250, 700, 875, 1050),
        "red",
        150,
    ),
    _street(
        24,
        "illinois_avenue",
        "Illinois Avenue",
        240,
        (20, 100, 300, 750, 925, 1100),
        "red",
        150,
    ),
    _railroad(25, "bo_railroad", "B. & O. Railroad"),
    _street(
        26,
        "atlantic_avenue",
        "Atlantic Avenue",
        260,
        (22, 110, 330, 800, 975, 1150),
        "yellow",
        150,
    ),
    _street(
        27,
        "ventnor_avenue",
        "Ventnor Avenue",
        260,
        (22, 110, 330, 800, 975, 1150),
        "yellow",
        150,
    ),
    _utility(28, "water_works", "Water Works"),
    _street(
        29,
        "marvin_gardens",
        "Marvin Gardens",
        280,
        (24, 120, 360, 850, 1025, 1200),
        "yellow",
        150,
    ),
    MonopolySpace(30, "go_to_jail", "Go to Jail", "go_to_jail"),
    _street(
        31,
        "pacific_avenue",
        "Pacific Avenue",
        300,
        (26, 130, 390, 900, 1100, 1275),
        "green",
        200,
    ),
    _street(
        32,
        "north_carolina_avenue",
        "North Carolina Avenue",
        300,
        (26, 130, 390, 900, 1100, 1275),
        "green",
        200,
    ),
    MonopolySpace(33, "community_chest_3", "Community Chest", "community_chest"),
    _street(
        34,
        "pennsylvania_avenue",
        "Pennsylvania Avenue",
        320,
        (28, 150, 450, 1000, 1200, 1400),
        "green",
        200,
    ),
    _railroad(35, "short_line", "Short Line"),
    MonopolySpace(36, "chance_3", "Chance", "chance"),
    _street(
        37,
        "park_place",
        "Park Place",
        350,
        (35, 175, 500, 1100, 1300, 1500),
        "dark_blue",
        200,
    ),
    MonopolySpace(38, "luxury_tax", "Luxury Tax", "tax", tax_amount=100),
    _street(39, "boardwalk", "Boardwalk", 400, (50, 200, 600, 1400, 1700, 2000), "dark_blue", 200),
)

CLASSIC_BOARD = BoardDefinition(
    board_id=DEFAULT_BOARD_ID,
    name="Classic Monopoly",
    spaces=CLASSIC_SPACES,
)

BOARDS: dict[str, BoardDefinition] = {CLASSIC_BOARD.board_id: CLASSIC_BOARD}

CHANCE_CARD_IDS: tuple[str, ...] = (
    "advance_to_go",
    "advance_to_illinois_avenue",
    "advance_to_st_charles_place",
    "advance_to_nearest_utility",
    "advance_to_nearest_railroad",
    "bank_dividend_50",
    "get_out_of_jail_free_chance",
    "go_back_three",
    "go_to_jail",
    "general_repairs",
    "speeding_fine_15",
    "take_trip_to_reading_railroad",
    "take_walk_on_boardwalk",
    "chairman_pay_50_each",
    "building_loan_matures_150",
    "crossword_competition_100",
)

COMMUNITY_CHEST_CARD_IDS: tuple[str, ...] = (
    "advance_to_go",
    "bank_error_collect_200",
    "doctor_fee_pay_50",
    "sale_of_stock_collect_50",
    "get_out_of_jail_free_community_chest",
    "go_to_jail",
    "holiday_fund_matures_100",
    "income_tax_refund_20",
    "birthday_collect_10_each",
    "life_insurance_matures_100",
    "hospital_fees_pay_100",
    "school_fees_pay_50",
    "consultancy_fee_collect_25",
    "street_repairs",
    "beauty_contest_collect_10",
    "inherit_100",
)

CARD_TEXT: dict[str, str] = {
    "advance_to_go": "Advance to GO. Collect $200.",
    "advance_to_illinois_avenue": "Advance to Illinois Avenue. If you pass GO, collect $200.",
    "advance_to_st_charles_place": "Advance to St. Charles Place. If you pass GO, collect $200.",
    "advance_to_nearest_utility": "Advance to the nearest Utility.",
    "advance_to_nearest_railroad": "Advance to the nearest Railroad.",
    "bank_dividend_50": "Bank pays you dividend of $50.",
    "get_out_of_jail_free_chance": "Get Out of Jail Free.",
    "go_back_three": "Go back 3 spaces.",
    "go_to_jail": "Go to Jail.",
    "general_repairs": "Make general repairs on all your property.",
    "speeding_fine_15": "Speeding fine. Pay $15.",
    "take_trip_to_reading_railroad": "Take a trip to Reading Railroad.",
    "take_walk_on_boardwalk": "Take a walk on Boardwalk.",
    "chairman_pay_50_each": "You have been elected Chairman of the Board. Pay each player $50.",
    "building_loan_matures_150": "Your building loan matures. Collect $150.",
    "crossword_competition_100": "You have won a crossword competition. Collect $100.",
    "bank_error_collect_200": "Bank error in your favor. Collect $200.",
    "doctor_fee_pay_50": "Doctor's fee. Pay $50.",
    "sale_of_stock_collect_50": "From sale of stock you get $50.",
    "get_out_of_jail_free_community_chest": "Get Out of Jail Free.",
    "holiday_fund_matures_100": "Holiday fund matures. Receive $100.",
    "income_tax_refund_20": "Income tax refund. Collect $20.",
    "birthday_collect_10_each": "It is your birthday. Collect $10 from each player.",
    "life_insurance_matures_100": "Life insurance matures. Collect $100.",
    "hospital_fees_pay_100": "Pay hospital fees of $100.",
    "school_fees_pay_50": "Pay school fees of $50.",
    "consultancy_fee_collect_25": "Receive $25 consultancy fee.",
    "street_repairs": "You are assessed for street repairs.",
    "beauty_contest_collect_10": "You have won second prize in a beauty contest. Collect $10.",
    "inherit_100": "You inherit $100.",
}


def get_board(board_id: str = DEFAULT_BOARD_ID) -> BoardDefinition:
    """Return a board definition, falling back to the classic board."""

    return BOARDS.get(board_id, CLASSIC_BOARD)
