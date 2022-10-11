-- Added 2022/10/11
-- Run this in MySQL to add the minizone_parent field to Zone.
-- This field is null for normal zones, set to parent zone's channel_name for all minizones.

ALTER TABLE [database].Zones
ADD COLUMN minizone_parent  VARCHAR(40) REFERENCES Zones.channel_name ON DELETE CASCADE;