from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from mmobot.constants import ALL_SKILLS, TEACHING_COOLDOWN, TEACHING_DIFF
from mmobot.db.models import Player, PlayerSkill, PlayerSkillTeaching
from mmobot.utils.discord import is_mention


async def teach_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    if len(args) != 2:
        await context.send('Please supply teach arguments like this: **!teach player skill**')
        return

    skill_name = args[1]
    teacher_id = context.author.id
    if skill_name not in ALL_SKILLS:
        await context.send(f'Skill {skill_name} does not exist')
        return

    with Session(engine) as session:
        teaching_player = Player.select_with_discord_id(session, teacher_id)
        assert teaching_player is not None
        if teaching_player.hp == 0:
            message = f'<@{teaching_player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        if is_mention(args[0]):
            learning_player = Player.select_with_discord_id(
                session, args[0][2:-1], channel_id=context.channel.id
            )
        else:
            learning_player = Player.select_with_discord_name(
                session, args[0], channel_id=context.channel.id
            )
        if learning_player is None:
            await context.send(f'Could not find player {args[0]} in current location')
            return

        current_time = datetime.now()
        if teaching_player.last_taught + TEACHING_COOLDOWN > current_time:
            wait_time = teaching_player.last_taught + TEACHING_COOLDOWN - current_time
            wait_hours = '{:.1f}'.format(wait_time / timedelta(hours=1))
            await context.send(f'Must wait {wait_hours} hrs to teach another skill')
            return

        learner_skill = get_skill(learning_player, skill_name)
        teacher_skill = get_skill(teaching_player, skill_name)

        if learner_skill.skill_level + TEACHING_DIFF <= teacher_skill.skill_level:
            teaching = PlayerSkillTeaching(
                skill=skill_name,
                teacher_id=teaching_player.id,
                learner_id=learning_player.id,
                teaching_time=current_time
            )
            session.add(teaching)
            teaching_player.last_taught = current_time
        else:
            await context.send(f'Cannot teach {skill_name} to <@{learning_player.discord_id}>')
            return

        session.commit()
        message = '{0} taught {1} to <@{2}>!'.format(
            context.author.nick,
            skill_name,
            learning_player.discord_id
        )
        await context.send(message)


def get_skill(player, skill_name):
    for skill in player.skills:
        if skill.skill_name == skill_name:
            return skill
    return PlayerSkill(
        player_id=player.id,
        skill_name=skill_name,
        skill_level=0
    )
