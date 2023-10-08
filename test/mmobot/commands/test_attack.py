import pytest

from sqlalchemy.orm import Session

from mmobot.commands import attack_logic
from mmobot.db.models import Minable, Player
from mmobot.test.constants import (
    MESSAGE_TEST_PLAYER_INCAPACITATED,
    TEST_TOWN_SQUARE_ZONE_ID
)
from mmobot.test.db import (
    add_player,
    add_to_database,
    add_weapon_instance,
    delete_all_entities,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext
from mmobot.test.random import MockRandomInt


RANDOM_CALL = 'random.randint'


engine = init_test_engine()


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    player = Player(
        id=3333,
        name='player',
        is_active=True,
        discord_id=100,
        hp=100, endurance=100, max_endurance=100, strength=100,
        equipped_weapon_id=2222
    )
    add_player(session, player)
    yield
    delete_all_entities(session)


@pytest.fixture
def attack_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)
