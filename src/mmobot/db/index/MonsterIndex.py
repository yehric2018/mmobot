import os
import yaml
from dotenv import load_dotenv

from mmobot.db.models import Monster


load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
DATA_PATH = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'index', 'data')


class MonsterIndex:
    def __init__(self):
        self.index = {}
        self._setup_index()

    def load_to_database(self, session):
        for monster in self.index:
            print(self.index[monster])
            session.merge(self.index[monster])
        session.commit()

    def _setup_index(self):
        monsters_path = os.path.join(DATA_PATH, 'monsters')
        for monster_filename in os.listdir(monsters_path):
            with open(os.path.join(monsters_path, monster_filename), 'r') as f:
                try:
                    monster_yaml = yaml.safe_load(f)
                    monster = Monster.from_yaml(monster_yaml)
                    self.index[monster.id] = monster
                except yaml.YAMLError as exc:
                    print(exc)
