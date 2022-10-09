import pytest
from mmobot.db.models import Minable, PlayerStats, Weapon, WeaponInstance
from mmobot.utils.mining import get_mining_outcome, get_mining_resource_distribution


RANDOM_CALL = 'random.randint'


@pytest.fixture
def player_stats():
    return PlayerStats(
        hp=100,
        endurance=100,
        max_endurance=100,
        luck=1,
        strength=100
    )


@pytest.fixture
def basic_pickaxe():
    pickaxe = Weapon(
        weapon_type='pickaxe',
        strength=15
    )
    return WeaponInstance(item=pickaxe)


@pytest.fixture
def basic_sword():
    sword = Weapon(
        weapon_type='sword',
        strength=15
    )
    return WeaponInstance(item=sword)


@pytest.fixture
def empty_minable():
    return Minable(
        stone_comp=0,
        coal_comp=0,
        iron_comp=0,
        silver_comp=0,
        gold_comp=0,
        diamond_comp=0,
        platinum_comp=0
    )


@pytest.fixture
def equal_minable():
    return Minable(
        stone_comp=10,
        coal_comp=10,
        iron_comp=10,
        silver_comp=10,
        gold_comp=10,
        diamond_comp=10,
        platinum_comp=10
    )


@pytest.fixture
def standard_minable():
    return Minable(
        stone_comp=8000,
        coal_comp=2000,
        iron_comp=2500,
        silver_comp=500,
        gold_comp=100,
        diamond_comp=15,
        platinum_comp=1
    )


@pytest.fixture
def rich_minable():
    return Minable(
        stone_comp=8000,
        coal_comp=2000,
        iron_comp=2500,
        silver_comp=1000,
        gold_comp=200,
        diamond_comp=40,
        platinum_comp=20
    )


def test_getMiningResourceDistribution(
    empty_minable, equal_minable, standard_minable, rich_minable
):
    expected1 = [0, 0, 0, 0, 0, 0, 0]
    actual1 = get_mining_resource_distribution(empty_minable)
    assert expected1 == actual1

    expected2 = [10, 20, 30, 40, 50, 60, 70]
    actual2 = get_mining_resource_distribution(equal_minable)
    assert expected2 == actual2

    expected3 = [8000, 10000, 12500, 13000, 13100, 13115, 13116]
    actual3 = get_mining_resource_distribution(standard_minable)
    assert expected3 == actual3

    expected4 = [8000, 10000, 12500, 13500, 13700, 13740, 13760]
    actual4 = get_mining_resource_distribution(rich_minable)
    assert expected4 == actual4


def test_getMiningOutcome_noResourcesMined(
    player_stats, basic_pickaxe, standard_minable, monkeypatch
):
    random_values = iter([0])
    random_calls = []

    def mock_random(min, max):
        random_calls.append((min, max))
        return next(random_values)
    monkeypatch.setattr(RANDOM_CALL, mock_random)
    assert len(get_mining_outcome(player_stats, basic_pickaxe, standard_minable)) == 0

    assert len(random_calls) == 1
    assert random_calls[0] == (0, 116)

    assert player_stats.endurance == 99
    assert player_stats.hp == 100

    assert standard_minable.stone_comp == 8000


def test_getMiningOutcome_oneStoneMined(
    player_stats, basic_pickaxe, standard_minable, monkeypatch
):
    random_values = iter([20, 1])
    random_calls = []

    def mock_random(min, max):
        random_calls.append((min, max))
        return next(random_values)
    monkeypatch.setattr(RANDOM_CALL, mock_random)
    result = get_mining_outcome(player_stats, basic_pickaxe, standard_minable)
    assert len(result) == 1
    assert result[0].id == 'stone'

    assert len(random_calls) == 2
    assert random_calls[0] == (0, 116)
    assert random_calls[1] == (1, 13116)

    assert player_stats.endurance == 99
    assert player_stats.hp == 100

    assert standard_minable.stone_comp == 7999


def test_getMiningOutcome_borderCases(
    player_stats, basic_pickaxe, standard_minable, monkeypatch
):
    random_values = iter([81, 8000, 12499, 13098, 13113])
    random_calls = []

    def mock_random(min, max):
        random_calls.append((min, max))
        return next(random_values)
    monkeypatch.setattr(RANDOM_CALL, mock_random)
    result = get_mining_outcome(player_stats, basic_pickaxe, standard_minable)
    assert len(result) == 4
    assert result[0].id == 'stone'
    assert result[1].id == 'iron-ore'
    assert result[2].id == 'golden-ore'
    assert result[3].id == 'platinum-ore'

    assert len(random_calls) == 5
    assert random_calls[0] == (0, 116)
    assert random_calls[1] == (1, 13116)
    assert random_calls[2] == (1, 13115)
    assert random_calls[3] == (1, 13114)
    assert random_calls[4] == (1, 13113)

    assert player_stats.endurance == 99
    assert player_stats.hp == 100

    assert standard_minable.stone_comp == 7999
    assert standard_minable.coal_comp == 2000
    assert standard_minable.iron_comp == 2499
    assert standard_minable.silver_comp == 500
    assert standard_minable.gold_comp == 99
    assert standard_minable.diamond_comp == 15
    assert standard_minable.platinum_comp == 0


def test_getMiningOutcome_maxLuck(
    player_stats, basic_pickaxe, standard_minable, monkeypatch
):
    random_values = iter([20, 1])
    random_calls = []

    def mock_random(min, max):
        random_calls.append((min, max))
        return next(random_values)
    monkeypatch.setattr(RANDOM_CALL, mock_random)
    player_stats.luck = 7
    get_mining_outcome(player_stats, basic_pickaxe, standard_minable)

    assert len(random_calls) == 2
    assert random_calls[0] == (0, 122)
    assert random_calls[1] == (1, 13116)


def test_getMiningOutcome_weakStrength(
    player_stats, basic_pickaxe, standard_minable, monkeypatch
):
    random_values = iter([20, 1])
    random_calls = []

    def mock_random(min, max):
        random_calls.append((min, max))
        return next(random_values)
    monkeypatch.setattr(RANDOM_CALL, mock_random)
    player_stats.strength = 15
    get_mining_outcome(player_stats, basic_pickaxe, standard_minable)

    assert len(random_calls) == 2
    assert random_calls[0] == (0, 31)
    assert random_calls[1] == (1, 13116)


def test_getMiningOutcome_strongWeapon(
    player_stats, basic_pickaxe, standard_minable, monkeypatch
):
    random_values = iter([20, 1])
    random_calls = []

    def mock_random(min, max):
        random_calls.append((min, max))
        return next(random_values)
    monkeypatch.setattr(RANDOM_CALL, mock_random)
    basic_pickaxe.strength = 75
    get_mining_outcome(player_stats, basic_pickaxe, standard_minable)

    assert len(random_calls) == 2
    assert random_calls[0] == (0, 116)
    assert random_calls[1] == (1, 13116)


def test_getMiningOutcome_lowEndurance(
    player_stats, basic_pickaxe, standard_minable, monkeypatch
):
    random_values = iter([20, 1])
    random_calls = []

    def mock_random(min, max):
        random_calls.append((min, max))
        return next(random_values)
    monkeypatch.setattr(RANDOM_CALL, mock_random)
    player_stats.endurance = 10
    get_mining_outcome(player_stats, basic_pickaxe, standard_minable)

    assert len(random_calls) == 2
    assert random_calls[0] == (0, 26)
    assert random_calls[1] == (1, 13116)


def test_getMiningOutcome_noWeapon(
    player_stats, standard_minable, monkeypatch
):
    random_values = iter([20, 1])
    random_calls = []

    def mock_random(min, max):
        random_calls.append((min, max))
        return next(random_values)
    monkeypatch.setattr(RANDOM_CALL, mock_random)
    get_mining_outcome(player_stats, None, standard_minable)

    assert len(random_calls) == 2
    assert random_calls[0] == (0, 101)
    assert random_calls[1] == (1, 13116)

    assert player_stats.hp == 98
    assert player_stats.endurance == 96


def test_getMiningOutcome_usingNonPickaxe(
    player_stats, basic_sword, standard_minable, monkeypatch
):
    random_values = iter([20, 1])
    random_calls = []

    def mock_random(min, max):
        random_calls.append((min, max))
        return next(random_values)
    monkeypatch.setattr(RANDOM_CALL, mock_random)
    get_mining_outcome(player_stats, basic_sword, standard_minable)

    assert len(random_calls) == 2
    assert random_calls[0] == (0, 104)
    assert random_calls[1] == (1, 13116)

    assert player_stats.hp == 100
    assert player_stats.endurance == 98
