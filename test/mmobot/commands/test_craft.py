import os
import pytest

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from mmobot.commands import craft_logic
from mmobot.db.index import ItemIndex
from mmobot.db.models import (
    FluidFood,
    ItemInstance,
    Player,
    PlayerSkill,
    ToolInstance,
    Weapon,
    WeaponInstance
)
from mmobot.test.constants import (
    TEST_ITEM_ENTITY_NUMBER,
    TEST_ITEM_ENTITY_REFERENCE,
    TEST_ITEM_ENTITY_NUMBER_2,
    TEST_ITEM_ENTITY_REFERENCE_2,
    TEST_ITEM_ENTITY_NUMBER_3,
    TEST_PLAYER_ENTITY_NUMBER,
    TEST_PLAYER_DISCORD_ID,
    TEST_PLAYER_DISCORD_NAME,
    TEST_TOWN_SQUARE_ZONE_ID
)
from mmobot.test.db import (
    add_to_database,
    delete_all_entities,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext, MockItemIndex

load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
DATA_PATH = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'index', 'data')

engine = init_test_engine()
item_index = MockItemIndex()

sword_filepath = os.path.join(DATA_PATH, 'items', 'weapons', 'iron-sword.yaml')
sword_yaml = item_index.load_yaml(sword_filepath)
sword = Weapon.from_yaml(sword_yaml)
item_index.index[sword.id] = sword
item_index.recipes[sword.id] = ItemIndex.get_recipes(sword, sword_yaml)

item_index.index['no-recipe-item'] = sword
item_index.recipes['no-recipe-item'] = []

nonsolid = FluidFood(id='test-fluid')
item_index.index['test-fluid'] = nonsolid
item_index.recipes['test-fluid'] = ItemIndex.get_recipes(sword, sword_yaml)
item_index.recipes['test-fluid'][0].product = nonsolid

item_index.index['skill-test-item'] = sword
item_index.recipes['skill-test-item'] = ItemIndex.get_recipes(sword, sword_yaml)
item_index.recipes['skill-test-item'][0].skills = {'test': 100}


MESSAGE_IRON_SWORD_SUCCESS = '<@100> Successfully crafted iron-sword!'
MESSAGE_LOSE_ENDURANCE_45 = 'Lost 45 endurance'
MESSAGE_LOSE_ENDURANCE_10 = 'Lost 10 endurance'
MESSAGE_LOSE_HP_35 = 'Lost 35 HP'
MESSAGE_NO_ARGS_PROVIDED = (
    '<@100> Please supply craft arguments like this:'
    ' **!craft item ingredient1 ingredient2 ...**'
)
MESSAGE_FAKE_ITEM = '<@100> item-that-does-not-exist does not exist.'
MESSAGE_NO_RECIPES = '<@100> You cannot craft no-recipe-item.'
MESSAGE_INVALID_REFERENCE = '<@100> Invalid reference ID: invalid'
MESSAGE_NOT_ENOUGH_HP = '<@100> You do not have enough endurance/hp to craft.'


@pytest.fixture
def session():
    return Session(engine)


@pytest.fixture(autouse=True)
def prepare_database(session):
    delete_all_entities(session)
    billet = ItemInstance(
        id=TEST_ITEM_ENTITY_NUMBER,
        item_id='iron-billet',
        owner_id=TEST_PLAYER_ENTITY_NUMBER
    )
    anvil = ToolInstance(
        id=TEST_ITEM_ENTITY_NUMBER_2,
        item_id='iron-anvil',
        zone_id=TEST_TOWN_SQUARE_ZONE_ID
    )
    hammer = WeaponInstance(
        id=TEST_ITEM_ENTITY_NUMBER_3,
        item_id='iron-hammer',
        zone_id=TEST_TOWN_SQUARE_ZONE_ID,
        owner_id=TEST_PLAYER_ENTITY_NUMBER
    )
    player_skills = [
        PlayerSkill(skill_name='smithing', skill_level=30),
        PlayerSkill(skill_name='forging', skill_level=15)
    ]
    player = Player(
        id=TEST_PLAYER_ENTITY_NUMBER,
        name=TEST_PLAYER_DISCORD_NAME,
        zone_id=TEST_TOWN_SQUARE_ZONE_ID,
        equipped_weapon_id=hammer.id,
        discord_id=TEST_PLAYER_DISCORD_ID,
        is_active=True,
        hp=100, endurance=100, max_endurance=100,
        skills=player_skills
    )
    add_to_database(session, player)
    add_to_database(session, billet)
    add_to_database(session, anvil)
    add_to_database(session, hammer)
    yield
    delete_all_entities(session)


@pytest.fixture
def iron_sword_args():
    return ['iron-sword', TEST_ITEM_ENTITY_REFERENCE, TEST_ITEM_ENTITY_REFERENCE_2]


@pytest.fixture
def craft_context(member, town_square_channel, test_guild):
    return MockContext(member, town_square_channel, test_guild)


@pytest.mark.asyncio
async def test_commandCraft_simpleRecipe(craft_context, session, iron_sword_args):
    await craft_logic(craft_context, iron_sword_args, engine, item_index)

    assert len(craft_context.channel.messages) == 2
    assert craft_context.channel.messages[0] == MESSAGE_IRON_SWORD_SUCCESS
    assert craft_context.channel.messages[1] == MESSAGE_LOSE_ENDURANCE_45

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER_3
    assert player.inventory[0].item_id == 'iron-hammer'
    assert player.inventory[1].item_id == 'iron-sword'
    assert player.hp == 100
    assert player.endurance == 55


@pytest.mark.asyncio
async def test_commandCraft_notInZone(craft_context, non_zone_channel, iron_sword_args, session):
    craft_context.channel = non_zone_channel
    await craft_logic(craft_context, iron_sword_args, engine, item_index)
    assert len(craft_context.channel.messages) == 0

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER
    assert player.inventory[1].id == TEST_ITEM_ENTITY_NUMBER_3


@pytest.mark.asyncio
async def test_commandCraft_noArgsProvided(craft_context):
    await craft_logic(craft_context, [], engine, item_index)
    assert len(craft_context.channel.messages) == 1
    assert craft_context.channel.messages[0] == MESSAGE_NO_ARGS_PROVIDED


@pytest.mark.asyncio
async def test_commandCraft_nonExistingItem(craft_context, iron_sword_args, session):
    iron_sword_args[0] = 'item-that-does-not-exist'
    await craft_logic(craft_context, iron_sword_args, engine, item_index)
    assert len(craft_context.channel.messages) == 1
    assert craft_context.channel.messages[0] == MESSAGE_FAKE_ITEM

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER
    assert player.inventory[1].id == TEST_ITEM_ENTITY_NUMBER_3


@pytest.mark.asyncio
async def test_commandCraft_itemNotCraftable(craft_context, iron_sword_args, session):
    iron_sword_args[0] = 'no-recipe-item'
    await craft_logic(craft_context, iron_sword_args, engine, item_index)
    assert len(craft_context.channel.messages) == 1
    assert craft_context.channel.messages[0] == MESSAGE_NO_RECIPES

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER
    assert player.inventory[1].id == TEST_ITEM_ENTITY_NUMBER_3


@pytest.mark.asyncio
async def test_commandCraft_invalidReference(craft_context, iron_sword_args, session):
    iron_sword_args[1] = 'invalid'
    await craft_logic(craft_context, iron_sword_args, engine, item_index)
    assert len(craft_context.channel.messages) == 1
    assert craft_context.channel.messages[0] == MESSAGE_INVALID_REFERENCE

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER
    assert player.inventory[1].id == TEST_ITEM_ENTITY_NUMBER_3


@pytest.mark.asyncio
async def test_commandCraft_missingIngredients(craft_context, session):
    await craft_logic(craft_context, ['iron-sword'], engine, item_index)
    assert len(craft_context.channel.messages) == 1
    assert 'ingredient' in craft_context.channel.messages[0]

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER
    assert player.inventory[1].id == TEST_ITEM_ENTITY_NUMBER_3


@pytest.mark.asyncio
async def test_commandCraft_missingContainer(craft_context, iron_sword_args, session):
    iron_sword_args[0] = 'test-fluid'
    await craft_logic(craft_context, iron_sword_args, engine, item_index)
    assert len(craft_context.channel.messages) == 1
    assert 'container' in craft_context.channel.messages[0]

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER
    assert player.inventory[1].id == TEST_ITEM_ENTITY_NUMBER_3


@pytest.mark.asyncio
async def test_commandCraft_insufficientSkill(craft_context, iron_sword_args, session):
    iron_sword_args[0] = 'skill-test-item'
    await craft_logic(craft_context, iron_sword_args, engine, item_index)
    assert len(craft_context.channel.messages) == 1
    assert 'skill' in craft_context.channel.messages[0]

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER
    assert player.inventory[1].id == TEST_ITEM_ENTITY_NUMBER_3


@pytest.mark.asyncio
async def test_commandCraft_notEnoughEndurance(craft_context, iron_sword_args, session):
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'endurance': 10})
    await craft_logic(craft_context, iron_sword_args, engine, item_index)
    assert len(craft_context.channel.messages) == 1
    assert '!craftx' in craft_context.channel.messages[0]

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.endurance == 10
    assert player.hp == 100
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER
    assert player.inventory[1].id == TEST_ITEM_ENTITY_NUMBER_3


@pytest.mark.asyncio
async def test_commandCraft_notEnoughEnduranceOrHP(craft_context, iron_sword_args, session):
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'endurance': 10, 'hp': 10})
    await craft_logic(craft_context, iron_sword_args, engine, item_index, use_hp=True)
    assert len(craft_context.channel.messages) == 1
    assert craft_context.channel.messages[0] == MESSAGE_NOT_ENOUGH_HP

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.endurance == 10
    assert player.hp == 10
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER
    assert player.inventory[1].id == TEST_ITEM_ENTITY_NUMBER_3


@pytest.mark.asyncio
async def test_commandCraft_useHP(craft_context, iron_sword_args, session):
    update_player(session, TEST_PLAYER_ENTITY_NUMBER, {'endurance': 10})
    await craft_logic(craft_context, iron_sword_args, engine, item_index, use_hp=True)
    assert len(craft_context.channel.messages) == 3
    assert craft_context.channel.messages[0] == MESSAGE_IRON_SWORD_SUCCESS
    assert craft_context.channel.messages[1] == MESSAGE_LOSE_ENDURANCE_10
    assert craft_context.channel.messages[2] == MESSAGE_LOSE_HP_35

    player = get_player_with_name(session, TEST_PLAYER_DISCORD_NAME)
    assert len(player.inventory) == 2
    assert player.inventory[0].id == TEST_ITEM_ENTITY_NUMBER_3
    assert player.inventory[0].item_id == 'iron-hammer'
    assert player.inventory[1].item_id == 'iron-sword'
    assert player.hp == 65
    assert player.endurance == 0
