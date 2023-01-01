from datetime import datetime
from sqlalchemy.orm import Session

from mmobot.constants import (
    DIRECTION_NORTH,
    DIRECTION_EAST,
    DIRECTION_SOUTH,
    DIRECTION_WEST,
    MOVE_ENDURANCE_COST
)
from mmobot.db.models import Player


async def move_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) == 0:
        await context.send('Please specify a location to move to! For example: !move hawaii')
        return

    direction = get_direction(args[0])
    member = context.author
    curr_channel = context.channel
    with Session(engine) as session:
        player = Player.select_with_discord_id(session, context.author.id)
        assert player is not None
        if player.hp == 0:
            message = f'<@{player.discord_id}> You are incapacitated.'
            await context.send(message)
            return
        elif player.endurance < MOVE_ENDURANCE_COST + player.get_burden():
            await context.send(f'<@{player.discord_id}> You do not have enough endurance.')
            return

        zone = player.zone
        assert zone is not None
        next_zone = None
        if direction == DIRECTION_NORTH and zone.can_move_north():
            next_zone = zone.north_zone
        elif direction == DIRECTION_EAST and zone.can_move_east():
            next_zone = zone.east_zone
        elif direction == DIRECTION_SOUTH and zone.can_move_south():
            next_zone = zone.south_zone
        elif direction == DIRECTION_WEST and zone.can_move_west():
            next_zone = zone.west_zone
        if next_zone is None:
            await context.send(f'<@{player.discord_id}> You cannot travel {args[0]}.')
            return

        remaining_cooldown = player.get_remaining_move_cooldown(direction)
        if remaining_cooldown > 0:
            message = f'<@{player.discord_id}> You cannot travel {args[0]} '
            message += f'for {int(remaining_cooldown)} seconds'
            await context.send(message)
            return

        dest_channel = await context.guild.fetch_channel(next_zone.channel_id)
        await curr_channel.send(f'{member.mention} has left for {dest_channel.mention}.')
        await dest_channel.set_permissions(member, read_messages=True, send_messages=True)
        await curr_channel.set_permissions(member, read_messages=False, send_messages=False)
        await dest_channel.send(f'{member.mention} has arrived.')

        player.zone_id = next_zone.id
        player.guarding_entity_id = None
        player.endurance -= (MOVE_ENDURANCE_COST + player.get_burden())
        player.last_move_time = datetime.now()
        player.retreat_direction = reverse_direction(direction)
        session.commit()


def get_direction(direction_word):
    match direction_word[0].lower():
        case 'n':
            return DIRECTION_NORTH
        case 'e':
            return DIRECTION_EAST
        case 's':
            return DIRECTION_SOUTH
        case 'w':
            return DIRECTION_WEST
    return -1


def reverse_direction(direction):
    if direction == DIRECTION_NORTH:
        return DIRECTION_SOUTH
    elif direction == DIRECTION_EAST:
        return DIRECTION_WEST
    elif direction == DIRECTION_SOUTH:
        return DIRECTION_NORTH
    elif direction == DIRECTION_WEST:
        return DIRECTION_EAST
    else:
        return -1
