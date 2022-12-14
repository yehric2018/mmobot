import datetime

import pytest
from freezegun import freeze_time
from sqlalchemy.orm import Session

from mmobot.commands.learn import learn_logic
from mmobot.db.models import Player, PlayerSkill, PlayerSkillTeaching
from mmobot.test.constants import (
    MESSAGE_TEST_PLAYER_INCAPACITATED,
    TEST_PLAYER_DISCORD_NAME,
    TEST_TOWN_SQUARE_ZONE_ID
)
from mmobot.test.db import (
    add_to_database,
    delete_all_entities,
    get_player_skill,
    get_player_skill_teachings,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext


engine = init_test_engine()

MESSAGE_LEARN_FIGHTING_SUCCESS = 'Learned fighting!'
MESSAGE_LEARN_FIGHTING_FROM_TEACHER = 'Learned fighting from teacher!'
MESSAGE_LEARN_MASONRY_MAXED = 'Skill masonry is already maxed.'
TEST_TIMESTAMP_STR = '2012-01-14 12:00:01'
TEST_TIMESTAMP_DT = datetime.datetime(2012, 1, 14, 12, 0, 1)


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    add_to_database(session, Player(id=1, name='teacher', discord_id=200))
    add_to_database(session, Player(
        id=2,
        name=TEST_PLAYER_DISCORD_NAME,
        discord_id=100,
        is_active=True,
        hp=100, skill_points=1,
        zone_id=TEST_TOWN_SQUARE_ZONE_ID
    ))
    add_to_database(session, PlayerSkill(player_id=2, skill_name='fighting', skill_level=5))
    add_to_database(session, PlayerSkill(player_id=2, skill_name='masonry', skill_level=50))
    yield
    delete_all_entities(session)


@pytest.fixture
def learn_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandLearn_useSkillPoints(learn_context, session):
    await learn_logic(learn_context, ['fighting'], engine)
    assert len(learn_context.channel.messages) == 1
    assert learn_context.channel.messages[0] == MESSAGE_LEARN_FIGHTING_SUCCESS
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 0
    skill = get_player_skill(session, 2, 'fighting')
    assert skill is not None
    assert skill.skill_level == 6


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandLearn_overrideTeaching(learn_context, session):
    add_to_database(session, PlayerSkillTeaching(
        id=20, teacher_id=1, learner_id=2, skill='fighting'
    ))
    await learn_logic(learn_context, ['fighting', 'points'], engine)
    assert len(learn_context.channel.messages) == 1
    assert learn_context.channel.messages[0] == MESSAGE_LEARN_FIGHTING_SUCCESS
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 0
    skill = get_player_skill(session, 2, 'fighting')
    assert skill is not None
    assert skill.skill_level == 6


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandLearn_useSkillPointsSkillNotLearned(learn_context, session):
    await learn_logic(learn_context, ['weaving'], engine)
    assert len(learn_context.channel.messages) == 1
    assert learn_context.channel.messages[0] == 'Learned weaving!'
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 0
    skill = get_player_skill(session, 2, 'weaving')
    assert skill is not None
    assert skill.skill_level == 1


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandLearn_useSkillPointsSkillMaxed(learn_context, session):
    await learn_logic(learn_context, ['masonry'], engine)
    assert len(learn_context.channel.messages) == 1
    assert learn_context.channel.messages[0] == MESSAGE_LEARN_MASONRY_MAXED
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 1
    skill = get_player_skill(session, 2, 'masonry')
    assert skill is not None
    assert skill.skill_level == 50


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandLearn_useSkillPointsOutOfPoints(learn_context, session):
    update_player(session, 2, {'skill_points': 0})
    await learn_logic(learn_context, ['fighting'], engine)
    assert len(learn_context.channel.messages) == 1
    expected_message = 'You do not have any skill points remaining.'
    assert learn_context.channel.messages[0] == expected_message
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 0
    skill = get_player_skill(session, 2, 'fighting')
    assert skill is not None
    assert skill.skill_level == 5


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandLearn_useTeaching(learn_context, session):
    add_to_database(session, PlayerSkillTeaching(
        id=20, teacher_id=1, learner_id=2, skill='fighting'
    ))
    await learn_logic(learn_context, ['fighting'], engine)
    assert len(learn_context.channel.messages) == 1
    assert learn_context.channel.messages[0] == MESSAGE_LEARN_FIGHTING_FROM_TEACHER
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 1
    skill = get_player_skill(session, 2, 'fighting')
    assert skill is not None
    assert skill.skill_level == 6
    assert len(get_player_skill_teachings(session, 1, 'fighting')) == 0


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandLearn_useTeachingSkillNotLearned(learn_context, session):
    add_to_database(session, PlayerSkillTeaching(
        id=20, teacher_id=1, learner_id=2, skill='weaving'
    ))
    await learn_logic(learn_context, ['weaving'], engine)
    assert len(learn_context.channel.messages) == 1
    assert learn_context.channel.messages[0] == 'Learned weaving from teacher!'
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 1
    skill = get_player_skill(session, 2, 'weaving')
    assert skill is not None
    assert skill.skill_level == 1
    assert len(get_player_skill_teachings(session, 1, 'weaving')) == 0


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandLearn_useTeachingOnCooldown(learn_context, session):
    update_player(session, 2, {'last_learned': TEST_TIMESTAMP_DT})
    add_to_database(session, PlayerSkillTeaching(
        id=20, teacher_id=1, learner_id=2, skill='fighting'
    ))
    await learn_logic(learn_context, ['fighting'], engine)
    assert len(learn_context.channel.messages) == 1
    expected_message = 'Must wait 20.0 hrs to learn from teacher.\n'
    expected_message += 'To use skill points instead, supply learn arguments like this:' \
        ' **!learn skill points**'
    assert learn_context.channel.messages[0] == expected_message
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 1
    skill = get_player_skill(session, 2, 'fighting')
    assert skill is not None
    assert skill.skill_level == 5
    assert len(get_player_skill_teachings(session, 1, 'fighting')) == 1


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandLearn_useTeachingSkillMaxed(learn_context, session):
    add_to_database(session, PlayerSkillTeaching(
        id=20, teacher_id=1, learner_id=2, skill='masonry'
    ))
    await learn_logic(learn_context, ['masonry'], engine)
    assert len(learn_context.channel.messages) == 1
    assert learn_context.channel.messages[0] == MESSAGE_LEARN_MASONRY_MAXED
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 1
    skill = get_player_skill(session, 2, 'masonry')
    assert skill is not None
    assert skill.skill_level == 50
    assert len(get_player_skill_teachings(session, 1, 'masonry')) == 0


@pytest.mark.asyncio
async def test_commandLearn_noArgsProvided(learn_context, session):
    await learn_logic(learn_context, [], engine)
    assert len(learn_context.channel.messages) == 1
    expected_message = 'Please supply learn arguments like this: **!learn skill**\n'
    expected_message += 'To use skill points: **!learn skill points**'
    assert learn_context.channel.messages[0] == expected_message
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 1
    skill = get_player_skill(session, 2, 'fighting')
    assert skill is not None
    assert skill.skill_level == 5


@pytest.mark.asyncio
async def test_commandLearn_invalidSecondArg(learn_context, session):
    await learn_logic(learn_context, ['fighting', 'stuff'], engine)
    assert len(learn_context.channel.messages) == 1
    expected_message = 'Please supply learn arguments like this: **!learn skill**\n'
    expected_message += 'To use skill points: **!learn skill points**'
    assert learn_context.channel.messages[0] == expected_message
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 1
    skill = get_player_skill(session, 2, 'fighting')
    assert skill is not None
    assert skill.skill_level == 5


@pytest.mark.asyncio
async def test_commandLearn_invalidSkillName(learn_context, session):
    await learn_logic(learn_context, ['fake_skill'], engine)
    assert len(learn_context.channel.messages) == 1
    assert learn_context.channel.messages[0] == 'Skill fake_skill does not exist'
    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert player.skill_points == 1
    skill = get_player_skill(session, 2, 'fighting')
    assert skill is not None
    assert skill.skill_level == 5


@pytest.mark.asyncio
async def test_commandLearn_notInZone(learn_context, non_zone_channel, session):
    learn_context.channel = non_zone_channel
    await learn_logic(learn_context, ['fighting'], engine)
    assert len(learn_context.channel.messages) == 0


@pytest.mark.asyncio
async def test_commandLearn_incapacitated(learn_context, non_zone_channel, session):
    update_player(session, 2, {'hp': 0})
    await learn_logic(learn_context, ['fighting'], engine)
    assert len(learn_context.channel.messages) == 1
    expected_message = MESSAGE_TEST_PLAYER_INCAPACITATED
    assert learn_context.channel.messages[0] == expected_message
