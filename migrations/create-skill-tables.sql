CREATE TABLE [database].PlayerSkills (
    id INT PRIMARY KEY,
    skill_points INT,
    last_learned DATETIME,
    last_taught DATETIME,
    fighting INT,
    marksmanship INT,
    smithing INT,
    farming INT,
    cooking INT,
    fishing INT,
    weaving INT,
    carpentry INT,
    masonry INT,
    medicine INT
);

CREATE TABLE [database].PlayerSkillTeachings (
    id INT PRIMARY KEY,
    skill VARCHAR(20),
    teacher INT REFERENCES Players,
    learner INT REFERENCES Players,
    teaching_time DATETIME
);

ALTER TABLE [database].Players
ADD COLUMN skills_id INT UNIQUE NOT NULL REFERENCES PlayerSkills;

ALTER TABLE [database].PlayerStats
DROP COLUMN experience,
DROP COLUMN fighting_skill,
DROP COLUMN hunting_skill,
DROP COLUMN mining_skill,
DROP COLUMN cooking_skill,
DROP COLUMN crafting_skill;
