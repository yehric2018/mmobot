import os
import pickle
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from mmobot.db.models import Zone
from mmobot.test.db import init_test_engine


load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
DATA_PATH = os.path.join(PROJECT_PATH, 'src', 'mmobot', 'db', 'world', 'data')

engine = init_test_engine()


class WorldMapBuilder:
    def initialize(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for i in range(cols)] for i in range(rows)]

    def load_from_file(self, filename):
        with open(os.path.join(DATA_PATH, filename), 'rb') as f:
            object_from_file = pickle.load(f)
            self.rows = object_from_file['rows']
            self.cols = object_from_file['cols']
            self.grid = object_from_file['grid']

    def save(self, filename):
        with open(os.path.join(DATA_PATH, filename), 'wb') as f:
            file_object = {
                'rows': self.rows,
                'cols': self.cols,
                'grid': self.grid
            }
            pickle.dump(file_object, f)

    def export_to_database(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self._update_zone_in_database(row, col, self.grid[row][col])

    def get_zone(self, row, col):
        if row >= self.rows or row < 0 or col >= self.cols or col < 0:
            print('Row/col index out of bounds')
        else:
            return self.grid[row][col]

    def set_zone(self, row, col, zone_id, channel_name):
        if row >= self.rows or row < 0 or col >= self.cols or col < 0:
            print('Row/col index out of bounds')
        else:
            self.grid[row][col] = {
                'zone_id': zone_id,
                'channel_name': channel_name,
                'north_wall': None,
                'south_wall': None,
                'east_wall': None,
                'west_wall': None
            }

    def set_id(self, row, col, zone_id):
        if row >= self.rows or row < 0 or col >= self.cols or col < 0:
            print('Row/col index out of bounds')
        elif self.grid[row][col] is None:
            print('Zone at this position has not been initialized')
        else:
            self.grid[row][col]['zone_id'] = zone_id

    def set_channel_name(self, row, col, channel_name):
        if row >= self.rows or row < 0 or col >= self.cols or col < 0:
            print('Row/col index out of bounds')
        elif self.grid[row][col] is None:
            print('Zone at this position has not been initialized')
        else:
            self.grid[row][col]['channel_name'] = channel_name

    def add_north_wall(self, row, col):
        self._add_wall(row, col, 'north_wall')

    def add_east_wall(self, row, col):
        self._add_wall(row, col, 'east_wall')

    def add_south_wall(self, row, col):
        self._add_wall(row, col, 'south_wall')

    def add_west_wall(self, row, col):
        self._add_wall(row, col, 'west_wall')

    def remove_north_wall(self, row, col):
        self._remove_wall(row, col, 'north_wall')

    def remove_east_wall(self, row, col):
        self._remove_wall(row, col, 'east_wall')

    def remove_south_wall(self, row, col):
        self._remove_wall(row, col, 'south_wall')

    def remove_west_wall(self, row, col):
        self._remove_wall(row, col, 'west_wall')

    def _update_zone_in_database(self, row, col, zone_data):
        if zone_data is None:
            return
        with Session(engine) as session:
            zone = Zone.select_with_id(session, zone_data['zone_id'])
            if zone is None:
                session.add(self._get_zone_from_data(row, col, zone_data))
            else:
                session.merge(self._get_zone_from_data(row, col, zone_data))
            session.commit()

    def _get_zone_from_data(self, row, col, zone_data):
        return Zone(
            id=zone_data['zone_id'],
            channel_name=zone_data['channel_name'],
            grid_row=row,
            grid_col=col
        )

    def _add_wall(self, row, col, wall_name):
        if row >= self.rows or row < 0 or col >= self.cols or col < 0:
            print('Row/col index out of bounds')
        elif self.grid[row][col] is None:
            print('Zone at this position has not been initialized')
        else:
            self.grid[row][col][wall_name] = {}

    def _remove_wall(self, row, col, wall_name):
        if row >= self.rows or row < 0 or col >= self.cols or col < 0:
            print('Row/col index out of bounds')
        elif self.grid[row][col] is None:
            print('Zone at this position has not been initialized')
        else:
            self.grid[row][col][wall_name] = None
