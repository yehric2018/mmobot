from datetime import datetime

import discord

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mmobot.db.models import Player


async def name_logic(context, args, engine):
    if context.channel.name != 'new-players':
        return
    if len(args) == 0:
        await context.send('Please enter the name of your hero! For example: !name Joanne')
        return
    if len(args) > 1:
        await context.send('Your name can only be one word, sorry!')
        return

    player_name = args[0]
    if len(player_name) < 2 or len(player_name) > 20:
        await context.send('Your name must be between 2 and 20 characters')
        return

    with Session(engine) as session:
        get_ancestors_statement = (
            select(func.max(Player.ancestry))
            .where(Player.discord_id == context.author.id)
        )
        max_ancestry = session.scalars(get_ancestors_statement).one_or_none()
        if max_ancestry is None:
            max_ancestry = 0
        else:
            max_ancestry = int(max_ancestry)
        birthday = datetime.now()
        new_player = Player(
            name=player_name,
            discord_id=f'{context.author.id}',
            ancestry=max_ancestry + 1,
            birthday=birthday,
            is_active=True,
            zone_id=0,
            hp=100,
            endurance=100,
            max_hp=100,
            max_endurance=100,
            strength=100,
            mobility=100,
            inventory_weight=0,
            last_move_time=birthday
        )

        try:
            session.add(new_player)
            session.commit()
        except IntegrityError:
            await context.send(f'Name {player_name} has already been taken')
            return

        member = context.author
        await member.edit(nick=player_name)

        town_square_channel = discord.utils.get(context.guild.channels, name='town-square')
        await town_square_channel.set_permissions(member, read_messages=True, send_messages=True)
