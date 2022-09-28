import discord
from discord.ext import commands

from db.zones import Zone

DB_ENTRY_SEPERATOR = '\n====================\n'


class MMOBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(command_prefix='!', intents=intents)

        self._setup_zones()

    def _setup_zones(self):
        with open('db/zones.db', 'r') as f:
            file_text = f.read()
            zone_data = file_text.split(DB_ENTRY_SEPERATOR)
            self.zones = {}
            for data in zone_data:
                zone = Zone(data)
                self.zones[zone.channel_name] = zone
