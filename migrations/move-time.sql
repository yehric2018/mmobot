-- Add some fields so we can determine when a player/monster can move based
-- on their current stats.
-- Step 1: Introduce last_move_time and retreat_direction fields.
-- last_move_time will be compared with the current time to see if the cooldown
-- has passed for a player to move.
-- retreat_direction determines what direction has half the cooldown refunded.
ALTER TABLE [db].Agents
    ADD COLUMN last_move_time DATETIME NOT NULL,
    ADD COLUMN retreat_direction INT DEFAULT 0;