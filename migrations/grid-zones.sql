-- Step 1: Add new fields to Zones and Entities tables.
ALTER TABLE [db].Zones
    ADD COLUMN id INT,
    ADD COLUMN channel_id VARCHAR(40) UNIQUE;
ALTER TABLE [db].Entities
    ADD COLUMN zone_id VARCHAR(40);

-- Step 2: Clear out ZonePaths and Zones tables so they can be repopulated again
DELETE FROM [db].ZonePaths;
DELETE FROM [db].Zones;

-- Step 3: Run a script to repopulate the channel with new zones, and add the zones
-- to the database.
