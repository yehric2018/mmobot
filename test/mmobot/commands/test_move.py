import discord
from discord import Permissions

import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from mmobot.commands import move_logic
from mmobot.db.models.player import Player
from mmobot.test.constants import MESSAGE_TEST_PLAYER_INCAPACITATED
from mmobot.test.db import (
    add_player,
    delete_all_entities,
    get_player_with_name,
    init_test_engine,
    update_player
)
from mmobot.test.mock import MockContext, MockGuild, MockMember, MockTextChannel, MockThread

DEFAULT_PERMISSIONS = 0


engine = init_test_engine()
