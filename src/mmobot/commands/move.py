import discord
from sqlalchemy.orm import Session

from mmobot.db.models import Player, Zone


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

        zone = player.zone
        assert zone is not None
        next_zone = None
        if direction == 'n' and zone.can_move_north():
            next_zone = zone.north_zone
        elif direction == 'e' and zone.can_move_east():
            next_zone = zone.east_zone
        elif direction == 's' and zone.can_move_south():
            next_zone = zone.south_zone
        elif direction == 'w' and zone.can_move_west():
            next_zone = zone.west_zone
        if next_zone is None:
            await context.send(f'<@{player.discord_id}> You cannot travel {args[0]}.')
            return

        dest_channel = await context.guild.fetch_channel(next_zone.channel_id)
        await curr_channel.send(f'{member.mention} has left for {dest_channel.mention}.')
        await dest_channel.set_permissions(member, read_messages=True, send_messages=True)
        await curr_channel.set_permissions(member, read_messages=False, send_messages=False)
        await dest_channel.send(f'{member.mention} has arrived.')

        player.zone_id = next_zone.id
        session.commit()


def get_direction(direction_word):
    return direction_word[0].lower()
