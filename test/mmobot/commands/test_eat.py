import pytest

from sqlalchemy.orm import Session

from mmobot.commands import eat_logic
from mmobot.db.models import (
    FluidContainerInstance,
    Player,
    PlayerStats,
    SolidFoodInstance,
    WeaponInstance
)
from mmobot.test.constants import (
    MESSAGE_TEST_PLAYER_INCAPACITATED,
    TEST_ITEM_ENTITY_NUMBER,
    TEST_ITEM_ENTITY_NUMBER_2,
    TEST_ITEM_ENTITY_NUMBER_3,
    TEST_ITEM_ENTITY_REFERENCE,
    TEST_PLAYER_DISCORD_ID,
    TEST_PLAYER_DISCORD_NAME,
    TEST_PLAYER_ENTITY_NUMBER
)
from mmobot.test.db import (
    add_to_database,
    delete_all_entities,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext


MESSAGE_EAT_RASPBERRY = '<@100> ate raspberry'
MESSAGE_EAT_RASPBERRY_JUICE = '<@100> ate raspberry-juice'
MESSAGE_RECOVER_1_HP = 'Recovered 1 HP'
MESSAGE_RECOVER_1_ENDURANCE = 'Recovered 1 endurance'
MESSAGE_RECOVER_3_HP = 'Recovered 3 HP'
MESSAGE_RECOVER_3_ENDURANCE = 'Recovered 3 endurance'

DESERT_SCIMITAR_ID = 'desert-scimitar'
RASPBERRY_ID = 'raspberry'
RASPBERRY_JUICE_ID = 'raspberry-juice'
STONE_BOWL_ID = 'stone-bowl'


engine = init_test_engine()


@pytest.fixture
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    stats = PlayerStats(hp=50, endurance=50, max_hp=100, max_endurance=100)
    player = Player(
        id=TEST_PLAYER_ENTITY_NUMBER,
        name=TEST_PLAYER_DISCORD_NAME,
        discord_id=TEST_PLAYER_DISCORD_ID,
        stats=stats,
        is_active=True
    )
    food_instance = SolidFoodInstance(
        id=TEST_ITEM_ENTITY_NUMBER,
        player_id=TEST_PLAYER_ENTITY_NUMBER,
        item_id=RASPBERRY_ID
    )
    non_food_instance = WeaponInstance(
        id=TEST_ITEM_ENTITY_NUMBER_2,
        player_id=TEST_PLAYER_ENTITY_NUMBER,
        item_id=DESERT_SCIMITAR_ID
    )
    container_instance = FluidContainerInstance(
        id=TEST_ITEM_ENTITY_NUMBER_3,
        player_id=TEST_PLAYER_ENTITY_NUMBER,
        item_id=STONE_BOWL_ID,
        nonsolid_id=RASPBERRY_JUICE_ID,
        units=3
    )
    add_to_database(session, player)
    add_to_database(session, food_instance)
    add_to_database(session, non_food_instance)
    add_to_database(session, container_instance)
    yield
    delete_all_entities(session)


@pytest.fixture
def eat_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)


@pytest.mark.asyncio
async def test_commandEat_solidWithName(eat_context, session):
    await eat_logic(eat_context, ['raspberry'], engine)
    assert len(eat_context.channel.messages) == 3
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_HP
    assert eat_context.channel.messages[2] == MESSAGE_RECOVER_1_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 51
    assert player.stats.endurance == 51
    assert len(player.inventory) == 2


@pytest.mark.asyncio
async def test_commandEat_solidWithEntityId(eat_context, session):
    await eat_logic(eat_context, [TEST_ITEM_ENTITY_REFERENCE], engine)
    assert len(eat_context.channel.messages) == 3
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_HP
    assert eat_context.channel.messages[2] == MESSAGE_RECOVER_1_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 51
    assert player.stats.endurance == 51
    assert len(player.inventory) == 2


@pytest.mark.asyncio
async def test_commandEat_solidHpDoesNotSurpassMax(eat_context, session):
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'stats.hp': 100})
    await eat_logic(eat_context, [RASPBERRY_ID], engine)
    assert len(eat_context.channel.messages) == 2
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 100
    assert player.stats.endurance == 51
    assert len(player.inventory) == 2


@pytest.mark.asyncio
async def test_commandEat_solidEnduranceDoesNotSurpassMax(eat_context, session):
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'stats.endurance': 100})
    await eat_logic(eat_context, [RASPBERRY_ID], engine)
    assert len(eat_context.channel.messages) == 2
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_HP

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 51
    assert player.stats.endurance == 100
    assert len(player.inventory) == 2


@pytest.mark.asyncio
async def test_commandEat_containerWithoutUnits(eat_context, session):
    await eat_logic(eat_context, ['stone-bowl'], engine)
    assert len(eat_context.channel.messages) == 3
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY_JUICE
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_HP
    assert eat_context.channel.messages[2] == MESSAGE_RECOVER_1_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 51
    assert player.stats.endurance == 51
    assert len(player.inventory) == 3
    assert player.inventory[2].units == 2


@pytest.mark.asyncio
async def test_commandEat_containerWithUnits(eat_context, session):
    await eat_logic(eat_context, ['stone-bowl', '3'], engine)
    assert len(eat_context.channel.messages) == 3
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY_JUICE
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_3_HP
    assert eat_context.channel.messages[2] == MESSAGE_RECOVER_3_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 53
    assert player.stats.endurance == 53
    assert len(player.inventory) == 3
    assert player.inventory[2].units == 0
    assert player.inventory[2].nonsolid_id is None


@pytest.mark.asyncio
async def test_commandEat_containerTooManyUnits(eat_context, session):
    await eat_logic(eat_context, ['stone-bowl', '900'], engine)
    assert len(eat_context.channel.messages) == 3
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY_JUICE
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_3_HP
    assert eat_context.channel.messages[2] == MESSAGE_RECOVER_3_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 53
    assert player.stats.endurance == 53
    assert len(player.inventory) == 3
    assert player.inventory[2].units == 0
    assert player.inventory[2].nonsolid_id is None


@pytest.mark.asyncio
async def test_commandEat_containerContentsNotEatable(eat_context, session):
    # TODO: Write this test when we introduce non-edible fluids/nonsolids
    pass


@pytest.mark.asyncio
async def test_commandEat_zeroUnitsProvided(eat_context, session):
    await eat_logic(eat_context, ['stone-bowl', '0'], engine)
    assert len(eat_context.channel.messages) == 3
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY_JUICE
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_HP
    assert eat_context.channel.messages[2] == MESSAGE_RECOVER_1_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 51
    assert player.stats.endurance == 51
    assert len(player.inventory) == 3
    assert player.inventory[2].units == 2


@pytest.mark.asyncio
async def test_commandEat_negativeUnitsProvided(eat_context, session):
    await eat_logic(eat_context, ['stone-bowl', '-15'], engine)
    assert len(eat_context.channel.messages) == 3
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY_JUICE
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_HP
    assert eat_context.channel.messages[2] == MESSAGE_RECOVER_1_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 51
    assert player.stats.endurance == 51
    assert len(player.inventory) == 3
    assert player.inventory[2].units == 2


@pytest.mark.asyncio
async def test_commandEat_nonnumericUnitsProvided(eat_context, session):
    await eat_logic(eat_context, ['stone-bowl', 'abc'], engine)
    assert len(eat_context.channel.messages) == 3
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY_JUICE
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_HP
    assert eat_context.channel.messages[2] == MESSAGE_RECOVER_1_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 51
    assert player.stats.endurance == 51
    assert len(player.inventory) == 3
    assert player.inventory[2].units == 2


@pytest.mark.asyncio
async def test_commandEat_containerHpDoesNotSurpassMax(eat_context, session):
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'stats.hp': 100})
    await eat_logic(eat_context, [STONE_BOWL_ID], engine)
    assert len(eat_context.channel.messages) == 2
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY_JUICE
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_ENDURANCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 100
    assert player.stats.endurance == 51
    assert len(player.inventory) == 3


@pytest.mark.asyncio
async def test_commandEat_containerEnduranceDoesNotSurpassMax(eat_context, session):
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'stats.endurance': 100})
    await eat_logic(eat_context, [STONE_BOWL_ID], engine)
    assert len(eat_context.channel.messages) == 2
    assert eat_context.channel.messages[0] == MESSAGE_EAT_RASPBERRY_JUICE
    assert eat_context.channel.messages[1] == MESSAGE_RECOVER_1_HP

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 51
    assert player.stats.endurance == 100
    assert len(player.inventory) == 3


@pytest.mark.asyncio
async def test_commandEat_notInZone(eat_context, non_zone_channel):
    eat_context.channel = non_zone_channel
    await eat_logic(eat_context, ['raspberry'], engine)
    assert len(eat_context.channel.messages) == 0


@pytest.mark.asyncio
async def test_commandEat_noArgsProvided(eat_context):
    await eat_logic(eat_context, [], engine)
    assert len(eat_context.channel.messages) == 1
    expected_message = 'Please indicate what item you would like to eat, for example: !eat food'
    assert eat_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEat_incapacitated(eat_context, session):
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'stats.hp': 0})
    await eat_logic(eat_context, [TEST_ITEM_ENTITY_REFERENCE], engine)
    assert len(eat_context.channel.messages) == 1
    assert eat_context.channel.messages[0] == MESSAGE_TEST_PLAYER_INCAPACITATED


@pytest.mark.asyncio
async def test_commandEat_nameNotFound(eat_context):
    await eat_logic(eat_context, ['bread'], engine)
    assert len(eat_context.channel.messages) == 1
    expected_message = '<@100> Could not find item to eat: bread'
    assert eat_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEat_referenceIdNotFound(eat_context):
    await eat_logic(eat_context, ['/nope'], engine)
    assert len(eat_context.channel.messages) == 1
    expected_message = '<@100> Could not find item to eat: /nope'
    assert eat_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandEat_itemNotEatable(eat_context, session):
    await eat_logic(eat_context, ['desert-scimitar'], engine)
    assert len(eat_context.channel.messages) == 1
    expected_message = '<@100> You cannot eat desert-scimitar!'
    assert eat_context.channel.messages[0] == expected_message

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.stats.hp == 50
    assert player.stats.endurance == 50
    assert len(player.inventory) == 3
