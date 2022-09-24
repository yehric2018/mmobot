import discord

class Zone():
    def __init__(self, data):
        lines = data.split('\n')
        
        self.channel_name = lines[0]
        self._init_navigation(lines[1])
        self._init_spawns(lines[2])

    def _init_navigation(self, data):
        self.navigation = {}

        places = data.split(',')
        for place in places:
            if ':' not in place:
                self.navigation[place] = {}
                continue

            next_zone, static_props = place.split(':')
            props = {}
            if 'G' in static_props:
                props['guardable'] = True
                props['guards'] = []
            else:
                props['guardable'] = False
            
            if 'L' in static_props:
                props['lockable'] = True
                props['locked'] = False
            else:
                props['lockable'] = False
            
            self.navigation[next_zone] = props

    def _init_spawns(self, data):
        self.spawns = {}
        if not data:
            return

        monsters = data.split(',')
        for monster in monsters:
            name, chance = monster.split(':')
            self.spawns[name] = int(chance)
