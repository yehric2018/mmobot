SELECT 
  TABLE_NAME,COLUMN_NAME,CONSTRAINT_NAME, REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME
FROM
  INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE
  REFERENCED_TABLE_SCHEMA = '[database]' AND
  REFERENCED_TABLE_NAME = 'Zones' AND
  REFERENCED_COLUMN_NAME = 'channel_name';


ALTER TABLE [database].Interactions
DROP CONSTRAINT [foreign key name];

ALTER TABLE [database].ItemInstances
DROP CONSTRAINT [foreign key name];

ALTER TABLE [database].Interactions
DROP COLUMN zone;

ALTER TABLE [database].ItemInstances
DROP COLUMN zone_name;

ALTER TABLE [database].Entities
ADD COLUMN zone VARCHAR(40) REFERENCES yehric_test.Zones.channel_name;
