-- Some SQL actions taken to utilize inventory weights (should be pretty quick)
-- Step 1: Drop size (we aren't using it anymore for now)
ALTER TABLE [db].Items
    DROP COLUMN size;

ALTER TABLE [db].Agents
    ADD COLUMN inventory_weight FLOAT DEFAULT 0;
