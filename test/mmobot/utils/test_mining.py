import pytest
import pytest_asyncio

from sqlalchemy.orm import Session

from mmobot.db.models import Minable, Player, PlayerStats, WeaponInstance
from mmobot.test.db import (
    add_player,
    delete_all_entities,
    get_player_with_name,
    init_test_engine
)
from mmobot.test.mock import MockContext, MockMember, MockTextChannel
from mmobot.test.random import MockRandomInt
from mmobot.utils.mining import (
    attack_command_mining,
    get_mining_outcome,
    get_mining_resource_distribution
)


RANDOM_CALL = 'random.randint'


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


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
def member():
    return MockMember(100, 'player')


@pytest.fixture
def basic_pickaxe():
    return WeaponInstance(id=2222, player_id=3333, item_id='basic-pickaxe')


@pytest.fixture
def basic_sword():
    return WeaponInstance(id=2222, player_id=3333, item_id='iron-sword')


@pytest.fixture
def player(player_stats, basic_pickaxe):
    return Player(
        id=3333,
        name='player',
        discord_id=100,
        stats=player_stats,
        equipped_weapon_id=2222,
        inventory=[basic_pickaxe]
    )


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    yield
    delete_all_entities(session)


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
        id=20,
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


@pytest_asyncio.fixture
async def channel(member):
    channel = MockTextChannel(1, 'mines')
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    return channel


@pytest.fixture
def mining_context(member, channel):
    return MockContext(member, channel, None)


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
    player, basic_pickaxe, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([0])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    player_stats = player.stats
    assert len(get_mining_outcome(player_stats, basic_pickaxe, standard_minable)) == 0

    assert len(mock_random.calls) == 1
    assert mock_random.calls[0] == (0, 116)

    assert player_stats.endurance == 99
    assert player_stats.hp == 100

    assert standard_minable.stone_comp == 8000


def test_getMiningOutcome_oneStoneMined(
    player, basic_pickaxe, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    player_stats = player.stats
    result = get_mining_outcome(player_stats, basic_pickaxe, standard_minable)
    assert len(result) == 1
    assert result[0].id == 'stone'

    assert len(mock_random.calls) == 2
    assert mock_random.calls[0] == (0, 116)
    assert mock_random.calls[1] == (1, 13116)

    assert player_stats.endurance == 99
    assert player_stats.hp == 100

    assert standard_minable.stone_comp == 7999


def test_getMiningOutcome_borderCases(
    player, basic_pickaxe, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([81, 8000, 12499, 13098, 13113])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    player_stats = player.stats
    result = get_mining_outcome(player_stats, basic_pickaxe, standard_minable)
    assert len(result) == 4
    assert result[0].id == 'stone'
    assert result[1].id == 'iron-ore'
    assert result[2].id == 'golden-ore'
    assert result[3].id == 'platinum-ore'

    assert len(mock_random.calls) == 5
    assert mock_random.calls[0] == (0, 116)
    assert mock_random.calls[1] == (1, 13116)
    assert mock_random.calls[2] == (1, 13115)
    assert mock_random.calls[3] == (1, 13114)
    assert mock_random.calls[4] == (1, 13113)

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
    player, basic_pickaxe, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    player_stats = player.stats
    player_stats.luck = 7
    get_mining_outcome(player_stats, basic_pickaxe, standard_minable)

    assert len(mock_random.calls) == 2
    assert mock_random.calls[0] == (0, 122)
    assert mock_random.calls[1] == (1, 13116)


def test_getMiningOutcome_weakStrength(
    player, basic_pickaxe, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    player.stats.strength = 15
    get_mining_outcome(player.stats, basic_pickaxe, standard_minable)

    assert len(mock_random.calls) == 2
    assert mock_random.calls[0] == (0, 31)
    assert mock_random.calls[1] == (1, 13116)


def test_getMiningOutcome_strongWeapon(
    player, basic_pickaxe, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    basic_pickaxe.strength = 75
    get_mining_outcome(player.stats, basic_pickaxe, standard_minable)

    assert len(mock_random.calls) == 2
    assert mock_random.calls[0] == (0, 116)
    assert mock_random.calls[1] == (1, 13116)


def test_getMiningOutcome_lowEndurance(
    player, basic_pickaxe, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    player.stats.endurance = 10
    get_mining_outcome(player.stats, basic_pickaxe, standard_minable)

    assert len(mock_random.calls) == 2
    assert mock_random.calls[0] == (0, 26)
    assert mock_random.calls[1] == (1, 13116)
    assert player.stats.endurance == 9


def test_getMiningOutcome_noWeapon(
    player, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    player.equipped_weapon_id = None
    add_player(session, player)
    player_stats = player.stats
    get_mining_outcome(player_stats, None, standard_minable)

    assert len(mock_random.calls) == 2
    assert mock_random.calls[0] == (0, 101)
    assert mock_random.calls[1] == (1, 13116)

    assert player_stats.hp == 98
    assert player_stats.endurance == 96


def test_getMiningOutcome_usingNonPickaxe(
    player, basic_sword, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    player.equipped_weapon_id = 2222
    player.inventory[0] = basic_sword
    add_player(session, player)
    player_stats = player.stats
    get_mining_outcome(player_stats, basic_sword, standard_minable)

    assert len(mock_random.calls) == 2
    assert mock_random.calls[0] == (0, 111)
    assert mock_random.calls[1] == (1, 13116)

    assert player_stats.hp == 100
    assert player_stats.endurance == 98


@pytest.mark.asyncio
async def test_attackCommandMining_noResourcesMined(
    mining_context, player, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([0])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    await attack_command_mining(mining_context, player, standard_minable, session)
    session.commit()

    assert len(mining_context.channel.messages) == 2
    expected_message1 = 'Mining [ /k ]...'
    assert mining_context.channel.messages[0] == expected_message1
    expected_message2 = 'No resources mined!'
    assert mining_context.channel.messages[1] == expected_message2

    with Session(engine) as validation_session:
        final_player = get_player_with_name(validation_session, 'player')
        assert final_player.stats.hp == 100
        assert final_player.stats.endurance == 99
        assert len(final_player.inventory) == 1


@pytest.mark.asyncio
async def test_attackCommandMining_oneStoneMined(
    mining_context, player, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    await attack_command_mining(mining_context, player, standard_minable, session)
    session.commit()

    assert len(mining_context.channel.messages) == 2
    expected_message1 = 'Mining [ /k ]...'
    assert mining_context.channel.messages[0] == expected_message1
    expected_message2 = 'Mined the following resource(s):\n'
    expected_message2 += '    - stone\n'
    assert mining_context.channel.messages[1] == expected_message2

    with Session(engine) as validation_session:
        final_player = get_player_with_name(validation_session, 'player')
        assert final_player.stats.hp == 100
        assert final_player.stats.endurance == 99
        assert len(final_player.inventory) == 2
        assert final_player.inventory[1].item_id == 'stone'


@pytest.mark.asyncio
async def test_attackCommandMining_resourceBorderCases(
    mining_context, player, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([81, 8000, 12499, 13098, 13113])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    add_player(session, player)
    await attack_command_mining(mining_context, player, standard_minable, session)
    session.commit()

    assert len(mining_context.channel.messages) == 2
    expected_message1 = 'Mining [ /k ]...'
    assert mining_context.channel.messages[0] == expected_message1
    expected_message2 = 'Mined the following resource(s):\n'
    expected_message2 += '    - stone\n'
    expected_message2 += '    - iron-ore\n'
    expected_message2 += '    - golden-ore\n'
    expected_message2 += '    - platinum-ore\n'
    assert mining_context.channel.messages[1] == expected_message2

    with Session(engine) as validation_session:
        final_player = get_player_with_name(validation_session, 'player')
        assert final_player.stats.hp == 100
        assert final_player.stats.endurance == 99
        assert len(final_player.inventory) == 5
        assert final_player.inventory[1].item_id == 'stone'
        assert final_player.inventory[2].item_id == 'iron-ore'
        assert final_player.inventory[3].item_id == 'golden-ore'
        assert final_player.inventory[4].item_id == 'platinum-ore'


@pytest.mark.asyncio
async def test_attackCommandMining_bareHands(
    mining_context, player, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    player.equipped_weapon_id = None
    add_player(session, player)
    await attack_command_mining(mining_context, player, standard_minable, session)
    session.commit()

    assert len(mining_context.channel.messages) == 3
    expected_message1 = 'Mining [ /k ]...'
    assert mining_context.channel.messages[0] == expected_message1
    expected_message2 = 'Mined the following resource(s):\n'
    expected_message2 += '    - stone\n'
    assert mining_context.channel.messages[1] == expected_message2
    expected_message3 = 'You lost 2 HP while mining with bare hands.'
    assert mining_context.channel.messages[2] == expected_message3

    with Session(engine) as validation_session:
        final_player = get_player_with_name(validation_session, 'player')
        assert final_player.stats.hp == 98
        assert final_player.stats.endurance == 96
        assert len(final_player.inventory) == 2
        assert final_player.inventory[1].item_id == 'stone'


@pytest.mark.asyncio
async def test_attackCommandMining_nonPickaxe(
    mining_context, player, basic_sword, standard_minable, session, monkeypatch
):
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    player.inventory[0] = basic_sword
    add_player(session, player)
    await attack_command_mining(mining_context, player, standard_minable, session)
    session.commit()

    assert len(mining_context.channel.messages) == 2
    expected_message1 = 'Mining [ /k ]...'
    assert mining_context.channel.messages[0] == expected_message1
    expected_message2 = 'Mined the following resource(s):\n'
    expected_message2 += '    - stone\n'
    assert mining_context.channel.messages[1] == expected_message2

    with Session(engine) as validation_session:
        final_player = get_player_with_name(validation_session, 'player')
        assert final_player.stats.hp == 100
        assert final_player.stats.endurance == 98
        assert len(final_player.inventory) == 2
        assert final_player.inventory[1].item_id == 'stone'
