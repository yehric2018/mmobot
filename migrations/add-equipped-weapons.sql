-- Added 2022/10/02
-- Run this in MySQL to add the equipped_weapon_id to the Players table

ALTER TABLE [database].Players
ADD COLUMN equipped_weapon_id INT;