import discord


async def move_logic(bot, context, args):
    if context.channel.name not in bot.zones:
        return
    if len(args) == 0:
        await context.send('Please specify a location to move to! For example: !move hawaii')
        return

    zone_name = args[0]
    if zone_name not in bot.zones:
        await context.send(f'{zone_name} is not an existing location')
        return
    if zone_name not in bot.zones[context.channel.name].navigation:
        await context.send(f'You cannot travel to {zone_name} from {context.channel.name}')
        return
    member = context.author
    curr_channel = discord.utils.get(context.guild.channels, name=context.channel.name)
    dest_channel = discord.utils.get(context.guild.channels, name=zone_name)

    if curr_channel.name not in ['general', 'dev'] and not member.guild_permissions.administrator:
        await dest_channel.set_permissions(member, read_messages=True, send_messages=True)
        await curr_channel.set_permissions(member, read_messages=False, send_messages=False)
