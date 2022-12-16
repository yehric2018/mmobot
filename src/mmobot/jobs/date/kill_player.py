def kill_player_job(player_discord_id, engine):
    '''
    Checks if the given player is incapacitated (hp = 0 or satiety = 0).
    If so, this job was triggered 2 minutes from when they were first incapacitated,
    so this job will kill the player by doing the following:
    1. Set their is_active to False, and ensure they are not already dead
    2. Make an announcement in their channel that they are dead
    3. Move their location from the zone to the afterlife
    '''
    pass
