ALTER TABLE [db].Players
DROP COLUMN skills_id;

DROP TABLE [db].PlayerSkills;

CREATE TABLE [db].PlayerSkills (
	player_id INT REFERENCES Players,
    skill_name VARCHAR(20),
    skill_level INT,
    PRIMARY KEY (player_id, skill_name)
);

ALTER TABLE [db].Players
ADD COLUMN last_learned DATETIME,
ADD COLUMN last_taught DATETIME;

ALTER TABLE [db].PlayerStats
ADD COLUMN stat_points INT,
ADD COLUMN skill_points INT;

ALTER TABLE [].PlayerSkillTeachings
MODIFY id INT NOT NULL AUTO_INCREMENT;