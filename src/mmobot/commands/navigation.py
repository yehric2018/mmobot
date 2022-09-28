async def navigation_logic(bot, context):
    if context.channel.name not in bot.zones:
        return

    message = f'You can reach the following locations from {context.channel.name}:\n'
    for location in bot.zones[context.channel.name].navigation:
        zone_props = bot.zones[context.channel.name].navigation[location]
        message += f'    {location}'
        if zone_props['lockable'] and zone_props['locked']:
            message += ' (locked)'
        if zone_props['guardable'] and len(zone_props['guards']) > 0:
            guard_list = ', '.join(zone_props['guards'])
            message += f' (guarded by {guard_list})'
        message += '\n'

    await context.send(message, ephemeral=True)
