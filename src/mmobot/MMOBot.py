import discord
from discord.ext import commands

DB_ENTRY_SEPERATOR = '\n====================\n'


class MMOBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(command_prefix='!', intents=intents)

        self._setup_zones()

    def _setup_zones(self):
        with open('db/static/zones.db', 'r') as f:
            file_text = f.read()
            zone_data = file_text.split(DB_ENTRY_SEPERATOR)
            self.zones = set()
            for data in zone_data:
                self.zones.add(data)
