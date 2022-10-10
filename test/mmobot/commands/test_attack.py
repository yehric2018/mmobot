import os
import pytest
from mmobot.db.models.minable import Minable
import pytest_asyncio

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mmobot.commands import attack_logic
from mmobot.db.models import Player, PlayerStats
from mmobot.test.db import (
    add_player,
    add_to_database,
    add_weapon_instance,
    delete_all_entities,
    get_player_with_name,
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel
from mmobot.test.random import MockRandomInt
from mmobot.utils.zones import read_zone_names


load_dotenv()
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOSTNAME = os.getenv('MYSQL_HOSTNAME')
MYSQL_DATABASE_NAME = os.getenv('MYSQL_TEST_DATABASE_NAME')

connection_str = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
    MYSQL_USERNAME,
    MYSQL_PASSWORD,
    MYSQL_HOSTNAME,
    MYSQL_DATABASE_NAME
)

RANDOM_CALL = 'random.randint'

zones = read_zone_names()


@pytest.fixture(scope='module')
def engine():
    return create_engine(connection_str)


@pytest.fixture(scope='module')
def session(engine):
    return Session(engine)


@pytest.fixture
def member():
    return MockMember(100, 'player')


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    player_stats = PlayerStats(
        hp=100,
        endurance=100,
        max_endurance=100,
        luck=1,
        strength=100
    )
    player = Player(
        id=3333,
        name='player',
        is_active=True,
        discord_id=100,
        stats=player_stats,
        equipped_weapon_id=2222
    )
    add_player(session, player)
    yield
    delete_all_entities(session)


@pytest_asyncio.fixture
async def channel(member):
    channel = MockTextChannel(1, 'town-square', category='World')
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    return channel


@pytest_asyncio.fixture
async def non_zone_channel():
    return MockTextChannel(2, 'general')


@pytest.fixture
def guild(channel, non_zone_channel):
    guild = MockGuild()
    guild.add_channel(channel)
    guild.add_channel(non_zone_channel)
    return guild


@pytest.fixture
def attack_context(member, channel, guild):
    return MockContext(member, channel, guild)


@pytest.mark.asyncio
async def test_commandAttack_mining(attack_context, session, engine, monkeypatch):
    add_weapon_instance(session, 2222, 3333, 'basic-pickaxe')
    add_to_database(session, Minable(
        id=20,
        zone='town-square',
        stone_comp=8000,
        coal_comp=2000,
        iron_comp=2500,
        silver_comp=500,
        gold_comp=100,
        diamond_comp=15,
        platinum_comp=1
    ))
    session.commit()
    mock_random = MockRandomInt([20, 1])
    monkeypatch.setattr(RANDOM_CALL, lambda min, max: mock_random.next(min, max))
    await attack_logic(zones, attack_context, ['/k'], engine)

    assert len(attack_context.channel.messages) == 2
    expected_message1 = 'Mining [ /k ]...'
    assert attack_context.channel.messages[0] == expected_message1
    expected_message2 = 'Mined the following resource(s):\n'
    expected_message2 += '    - stone\n'
    assert attack_context.channel.messages[1] == expected_message2

    with Session(engine) as validation_session:
        final_player = get_player_with_name(validation_session, 'player')
        assert final_player.stats.hp == 100
        assert final_player.stats.endurance == 99
        assert len(final_player.inventory) == 2
        assert final_player.inventory[1].item_id == 'stone'
