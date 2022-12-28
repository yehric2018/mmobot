-- Step 1: Migrate data from Players to Agents
INSERT INTO [db].Agents
(id, is_active, hp, endurance, max_hp, max_endurance, strength, mobility, guarding_entity_id)
SELECT P.id, P.is_active, S.hp, S.endurance, S.max_hp, S.max_endurance, S.strength, S.mobility, P.guarding_entity
FROM [db].Players AS P, yehric_mmo_dev.PlayerStats AS S
WHERE P.stats_id = S.id;

-- Step 2: DROP current foreign key constraints, add a foreign key constraint so
-- Players now points to Agents instead of Entities
SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE REFERENCED_TABLE_SCHEMA IS NOT NULL
    AND TABLE_SCHEMA = '[db]'
    AND TABLE_NAME = 'Players';
ALTER TABLE [db].Players
    DROP FOREIGN KEY Players_ibfk_1,
    DROP FOREIGN KEY Players_ibfk_2,
    DROP FOREIGN KEY Players_ibfk_3,
    DROP FOREIGN KEY Players_ibfk_4,
    DROP FOREIGN KEY Players_ibfk_5;
ALTER TABLE [db].Players
    ADD CONSTRAINT Players_ibfk_1 FOREIGN KEY (id)
    REFERENCES [db].Agents (id)
    ON DELETE CASCADE;
ALTER TABLE [db].Players
    ADD CONSTRAINT Players_ibfk_2 FOREIGN KEY (stats_id)
    REFERENCES [db].PlayerStats (id)
    ON DELETE CASCADE;

-- Step 3: Drop the redundant columns in Players
-- We are keeping stats_id so that we continue to pass the tests, we will drop this
-- column as well once everything is deprecated.
ALTER TABLE [db].Players
    DROP COLUMN is_active,
    DROP COLUMN stance,
    -- DROP COLUMN stats_id,
    DROP COLUMN guarding_entity,
    DROP COLUMN guarding_path,
    DROP COLUMN last_attack,
    DROP COLUMN last_location;

-- Step 4: Move skill_points and stat_points columns from PlayerStats to Players
-- We will reset everyone' skill_points and stat_points to 0 for now. :(
ALTER TABLE [db].Players
    ADD COLUMN stat_points INT DEFAULT 0,
    ADD COLUMN skill_points INT DEFAULT 0;


-- Step 5: Remove stats_id from Players, then drop the PlayerStats table.
SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE REFERENCED_TABLE_SCHEMA IS NOT NULL
    AND TABLE_SCHEMA = '[db]'
    AND TABLE_NAME = 'Players';
ALTER TABLE [db].Players
    DROP FOREIGN KEY Players_ibfk_2;
ALTER TABLE [db].Players
    DROP COLUMN stats_id;
DROP TABLE [db].PlayerStats;
