import os

import discord

from dotenv import load_dotenv


load_dotenv()
GUILD_ID = os.getenv('TEST_GUILD_ID')


class TestBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)

        self.guild = self.get_guild(GUILD_ID)

    async def send_message(self, channel_name, message):
        channel = discord.utils.get(self.guild.channels, name=channel_name)
        await channel.send(message)
