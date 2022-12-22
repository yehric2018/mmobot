-- Use these SQL commands to move items from Item class to more specific Resource class.
-- 1. Add the Items to the Resources table
-- 2. For each of the items in the Items table, set their item_type to 'resource'


INSERT INTO yehric_mmo_dev.Resources VALUES ('stone'), ('iron-ore');

UPDATE yehric_mmo_dev.Items
SET item_type = 'resource'
WHERE id = 'stone';

UPDATE yehric_mmo_dev.Items
SET item_type = 'resource'
WHERE id = 'iron-ore';

-- Or to do it all in one go:
UPDATE yehric_mmo_dev.Items
SET item_type = 'resource'
WHERE id NOT IN (SELECT id FROM yehric_mmo_dev.Weapons)
	AND id NOT IN (SELECT id FROM yehric_mmo_dev.Attires)
    AND id NOT IN (SELECT id FROM yehric_mmo_dev.Resources);

INSERT INTO yehric_mmo_dev.Resources (SELECT id
FROM yehric_mmo_dev.Items
WHERE id NOT IN (SELECT id FROM yehric_mmo_dev.Weapons)
	AND id NOT IN (SELECT id FROM yehric_mmo_dev.Attires)
    AND id NOT IN (SELECT id FROM yehric_mmo_dev.Resources));