from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from mmobot.constants import ALL_SKILLS, TEACHING_COOLDOWN, TEACHING_DIFF

from mmobot.db.models import Player, PlayerSkillTeaching
from mmobot.utils.discord import is_mention


async def teach_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) != 2:
        await context.send('Please supply give arguments like this: **!teach player skill**')
        return

    skill_name = args[1]
    teacher_id = context.author.id
    if skill_name not in ALL_SKILLS:
        await context.send(f'Skill {skill_name} does not exist')

    if is_mention(args[0]):
        learner_id = int(args[0][2:-1])
        learning_player_statement = (
            select(Player)
            .where(Player.discord_id == learner_id)
            .where(Player.is_active)
            .where(Player.zone == context.channel.name)
        )
    else:
        learner_name = args[0]
        learning_player_statement = (
            select(Player)
            .where(Player.name == learner_name)
            .where(Player.is_active)
            .where(Player.zone == context.channel.name)
        )

    with Session(engine) as session:
        learning_player = session.scalars(learning_player_statement).one_or_none()
        if learning_player is None:
            await context.send(f'Could not find player {args[0]} in current location')
            return
        teaching_player_statement = (
            select(Player)
            .where(Player.discord_id == teacher_id)
            .where(Player.is_active)
        )
        teaching_player = session.scalars(teaching_player_statement).one()

        if not await teach_skill(context, learning_player, teaching_player, skill_name):
            return

        message = '<@{0}> learned {1} from {2}!'.format(
            learning_player.discord_id,
            skill_name,
            context.author.nick
        )
        await context.send(message)


async def teach_skill(context, learning_player, teaching_player, skill_name, session):
    current_time = datetime.now()
    if teaching_player.last_taught + TEACHING_COOLDOWN > current_time:
        wait_time = teaching_player.last_taught + TEACHING_COOLDOWN - current_time
        await context.send(f'Must wait {wait_time.hours} to teach another skill')

    can_teach = False
    learner_skills = learning_player.skills
    teacher_skills = teaching_player.skills
    match skill_name:
        case 'fighting':
            can_teach = learner_skills.fighting + TEACHING_DIFF <= teacher_skills.fighting
        case 'marksmanship':
            can_teach = learner_skills.marksmanship + TEACHING_DIFF <= teacher_skills.marksmanship
        case 'smithing':
            can_teach = learner_skills.smithing + TEACHING_DIFF <= teacher_skills.smithing
        case 'farming':
            can_teach = learner_skills.farming + TEACHING_DIFF <= teacher_skills.farming
        case 'cooking':
            can_teach = learner_skills.cooking + TEACHING_DIFF <= teacher_skills.cooking
        case 'fishing':
            can_teach = learner_skills.fishing + TEACHING_DIFF <= teacher_skills.fishing
        case 'weaving':
            can_teach = learner_skills.weaving + TEACHING_DIFF <= teacher_skills.weaving
        case 'carpentry':
            can_teach = learner_skills.carpentry + TEACHING_DIFF <= teaching_player.carpentry
        case 'masonry':
            can_teach = learner_skills.masonry + TEACHING_DIFF <= teaching_player.masonry
        case 'medicine':
            can_teach = learner_skills.medicine + TEACHING_DIFF <= teaching_player.medicine

    if can_teach:
        teaching = PlayerSkillTeaching(
            skill='skill_name',
            teacher=teaching_player.id,
            learner=learning_player.id,
            teaching_time=datetime.now()
        )
        session.add(teaching)
        teacher_skills.last_taught = datetime.now()
    else:
        await context.send(f'Cannot teach {skill_name} to <@{learning_player.discord_id}>')
    return can_teach
