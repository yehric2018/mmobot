import datetime

import pytest
import pytest_asyncio
from freezegun import freeze_time
from sqlalchemy.orm import Session

from mmobot.commands import teach_logic
from mmobot.db.models import Player, PlayerSkill
from mmobot.test.constants import MESSAGE_TEST_PLAYER_INCAPACITATED
from mmobot.test.db import (
    add_to_database,
    delete_all_entities,
    get_player_skill_teachings,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel


engine = init_test_engine()

MESSAGE_TEACH_SUCCESS = 'teacher taught fighting to <@101>!'
TEST_TIMESTAMP_STR = '2012-01-14 12:00:01'
TEST_TIMESTAMP_DT = datetime.datetime(2012, 1, 14, 12, 0, 1)


@pytest.fixture()
def session():
    return Session(engine)


@pytest.fixture
def teaching_member():
    return MockMember(100, 'teacher')


@pytest.fixture
def learning_member():
    return MockMember(101, 'learner')


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    add_to_database(session, Player(
        id=1,
        name='teacher',
        discord_id=100,
        is_active=True,
        hp=100,
        zone='barracks'
    ))
    add_to_database(session, Player(
        id=2,
        name='learner',
        discord_id=101,
        is_active=True,
        zone='barracks'
    ))
    add_to_database(session, PlayerSkill(
        player_id=1,
        skill_name='fighting',
        skill_level=30
    ))
    add_to_database(session, PlayerSkill(
        player_id=2,
        skill_name='fighting',
        skill_level=5
    ))
    add_to_database(session, PlayerSkill(
        player_id=1,
        skill_name='masonry',
        skill_level=30
    ))
    add_to_database(session, PlayerSkill(
        player_id=2,
        skill_name='masonry',
        skill_level=50
    ))
    add_to_database(session, PlayerSkill(
        player_id=2,
        skill_name='weaving',
        skill_level=50
    ))
    yield
    delete_all_entities(session)


@pytest_asyncio.fixture
async def channel(teaching_member, learning_member):
    channel = MockTextChannel(1, 'barracks', category='World')
    await channel.set_permissions(teaching_member, read_messages=True, send_messages=True)
    await channel.set_permissions(learning_member, read_messages=True, send_messages=True)
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
def teaching_context(teaching_member, channel, guild):
    return MockContext(teaching_member, channel, guild)


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandTeach_withDiscordMention(teaching_context, session):
    await teach_logic(teaching_context, ['<@101>', 'fighting'], engine)
    assert len(teaching_context.channel.messages) == 1
    assert teaching_context.channel.messages[0] == MESSAGE_TEACH_SUCCESS
    teaching_player = get_player_with_name(session, 'teacher')
    assert teaching_player.last_taught == TEST_TIMESTAMP_DT
    assert teaching_player.skills[0].skill_level == 30
    learning_player = get_player_with_name(session, 'learner')
    assert learning_player.skills[0].skill_level == 5
    teaching_entry = get_player_skill_teachings(session, 1, 'fighting')[0]
    assert teaching_entry.teacher_id == 1
    assert teaching_entry.learner_id == 2
    assert teaching_entry.teaching_time == TEST_TIMESTAMP_DT
    assert teaching_entry.skill == 'fighting'


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandTeach_withTextName(teaching_context, session):
    await teach_logic(teaching_context, ['learner', 'fighting'], engine)
    assert len(teaching_context.channel.messages) == 1
    assert teaching_context.channel.messages[0] == MESSAGE_TEACH_SUCCESS
    teaching_player = get_player_with_name(session, 'teacher')
    assert teaching_player.last_taught == TEST_TIMESTAMP_DT
    assert teaching_player.skills[0].skill_level == 30
    learning_player = get_player_with_name(session, 'learner')
    assert learning_player.skills[0].skill_level == 5
    teaching_entry = get_player_skill_teachings(session, 1, 'fighting')[0]
    assert teaching_entry.teacher_id == 1
    assert teaching_entry.learner_id == 2
    assert teaching_entry.teaching_time == TEST_TIMESTAMP_DT
    assert teaching_entry.skill == 'fighting'


@pytest.mark.asyncio
async def test_commandTeach_noArgsProvided(teaching_context):
    await teach_logic(teaching_context, [], engine)
    assert len(teaching_context.channel.messages) == 1
    expected_message = 'Please supply teach arguments like this: **!teach player skill**'
    assert teaching_context.channel.messages[0] == expected_message


@pytest.mark.asyncio
async def test_commandTeach_notInZone(teaching_context, non_zone_channel):
    teaching_context.channel = non_zone_channel
    await teach_logic(teaching_context, ['learner', 'fighting'], engine)
    assert len(teaching_context.channel.messages) == 0


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandTeach_learnerNotInZone(teaching_context, learning_member, session):
    await teaching_context.channel.set_permissions(
        learning_member,
        read_messages=False,
        send_messages=False
    )
    update_player(session, 2, {'zone': 'town-square'})
    await teach_logic(teaching_context, ['learner', 'fighting'], engine)
    assert len(teaching_context.channel.messages) == 1
    expected_message = 'Could not find player learner in current location'
    assert teaching_context.channel.messages[0] == expected_message
    assert len(get_player_skill_teachings(session, 1, 'fighting')) == 0


@pytest.mark.asyncio
async def test_commandTeach_incapacitated(teaching_context, session):
    update_player(session, 1, {'hp': 0})
    await teach_logic(teaching_context, ['learner', 'fighting'], engine)
    assert len(teaching_context.channel.messages) == 1
    expected_message = MESSAGE_TEST_PLAYER_INCAPACITATED
    assert teaching_context.channel.messages[0] == expected_message
    assert len(get_player_skill_teachings(session, 1, 'fighting')) == 0


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandTeach_teacherSkillTooLow(teaching_context, session):
    await teach_logic(teaching_context, ['learner', 'masonry'], engine)
    assert len(teaching_context.channel.messages) == 1
    expected_message = 'Cannot teach masonry to <@101>'
    assert teaching_context.channel.messages[0] == expected_message
    assert len(get_player_skill_teachings(session, 1, 'masonry')) == 0
    assert len(get_player_skill_teachings(session, 1, 'masonry')) == 0


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandTeach_teacherSkillUnlearned(teaching_context, session):
    await teach_logic(teaching_context, ['learner', 'weaving'], engine)
    assert len(teaching_context.channel.messages) == 1
    expected_message = 'Cannot teach weaving to <@101>'
    assert teaching_context.channel.messages[0] == expected_message
    assert len(get_player_skill_teachings(session, 1, 'weaving')) == 0
    assert len(get_player_skill_teachings(session, 1, 'weaving')) == 0


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandTeach_teachingOnCooldown(teaching_context, session):
    update_player(session, 1, {'last_taught': TEST_TIMESTAMP_DT})
    await teach_logic(teaching_context, ['<@101>', 'fighting'], engine)
    assert len(teaching_context.channel.messages) == 1
    expected_message = 'Must wait 8.0 hrs to teach another skill'
    assert teaching_context.channel.messages[0] == expected_message
    assert len(get_player_skill_teachings(session, 1, 'fighting')) == 0


@pytest.mark.asyncio
@freeze_time(TEST_TIMESTAMP_STR)
async def test_commandTeach_skillDoesNotExist(teaching_context, session):
    await teach_logic(teaching_context, ['<@101>', 'fake_skill'], engine)
    assert len(teaching_context.channel.messages) == 1
    expected_message = 'Skill fake_skill does not exist'
    assert teaching_context.channel.messages[0] == expected_message
    assert len(get_player_skill_teachings(session, 1, 'fake_skill')) == 0
