-- Step 1: Add new fields to Zones and Entities tables.
ALTER TABLE [db].Zones
    ADD COLUMN id INT,
    ADD COLUMN channel_id VARCHAR(40) UNIQUE;
ALTER TABLE [db].Entities
    ADD COLUMN zone_id INT;

-- Step 2: Clear out ZonePaths and Zones tables so they can be repopulated again
DELETE FROM [db].ZonePaths;
DELETE FROM [db].Zones;

-- Step 3: Run a script to repopulate the channel with new zones, and add the zones
-- to the database.

-- Step 4: Delete the ZonePaths table.
DROP TABLE [db].ZonePaths;

-- Step 5: Adjust the key constraints for both Zones and Entities
SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE REFERENCED_TABLE_SCHEMA IS NOT NULL
    AND TABLE_SCHEMA = '[db]'
    AND TABLE_NAME = 'Entities';
ALTER TABLE [db].Entities
    DROP FOREIGN KEY Entities_ibfk_1;
ALTER TABLE [db].Zones
    DROP PRIMARY KEY;
ALTER TABLE [db].Zones
    MODIFY COLUMN id INT PRIMARY KEY;
ALTER TABLE [db].Entities
    ADD CONSTRAINT Entities_ibfk_1 FOREIGN KEY (zone_id)
    REFERENCES [db].Zones (id)
    ON DELETE CASCADE;

ALTER TABLE [db].Entities
    DROP COLUMN zone_id;
ALTER TABLE [db].Entities
    ADD COLUMN zone_id INT REFERENCES [db].Zones;

-- Step 6: Remove the minizone_parent column since we aren't using it anymore.
ALTER TABLE [db].Zones
	DROP COLUMN minizone_parent;
