import os

from dotenv import load_dotenv

from mmobot.constants import DB_ENTRY_SEPERATOR


load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')


def read_zone_names():
    zones = set()
    with open(os.path.join(PROJECT_PATH, 'src/mmobot/db/static/zones.db'), 'r') as f:
        file_text = f.read()
        zone_data = file_text.split(DB_ENTRY_SEPERATOR)
        for data in zone_data:
            zones.add(data)
    return zones
