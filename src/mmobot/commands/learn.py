from datetime import datetime
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from mmobot.constants import ALL_SKILLS, LEARNING_COOLDOWN
from mmobot.db.models import Player, PlayerSkill, PlayerSkillTeaching


async def learn_logic(context, args, engine):
    if context.channel.category.name != 'World':
        return
    use_points = False
    if len(args) != 1:
        if len(args) == 2 and args[1] == 'points':
            use_points = True
        else:
            message = 'Please supply learn arguments like this: **!learn skill**\n'
            message += 'To use skill points: **!learn skill points**'
            await context.send(message)
            return

    skill_name = args[0]
    if skill_name not in ALL_SKILLS:
        await context.send(f'Skill {skill_name} does not exist')
        return

    with Session(engine) as session:
        select_player_statement = (
            select(Player)
            .where(Player.discord_id == context.author.id)
            .where(Player.is_active)
        )
        player = session.scalars(select_player_statement).one()
        if player.hp == 0:
            message = f'<@{player.discord_id}> You are incapacitated.'
            await context.send(message)
            return

        skill = get_skill(session, player, skill_name)
        player_teachings = session.scalars(
            select(PlayerSkillTeaching)
            .where(PlayerSkillTeaching.skill == skill_name)
            .where(PlayerSkillTeaching.learner_id == player.id)
        ).all()

        if not use_points and len(player_teachings) > 0:
            current_time = datetime.now()
            teacher = player_teachings[0].teacher
            if player.last_learned + LEARNING_COOLDOWN > current_time:
                wait_time = player.last_learned + LEARNING_COOLDOWN - current_time
                wait_hours = '{:.1f}'.format(wait_time / timedelta(hours=1))
                message = f'Must wait {wait_hours} hrs to learn from {teacher.name}.\n'
                message += 'To use skill points instead, supply learn arguments like this:' \
                    ' **!learn skill points**'
                await context.send(message)
            else:
                if skill.skill_level == ALL_SKILLS[skill_name]['max']:
                    await context.send(f'Skill {skill_name} is already maxed.')
                    session.delete(player_teachings[0])
                else:
                    skill.skill_level += 1
                    player.last_learned = current_time

                    await context.send(f'Learned {skill_name} from {teacher.name}!')
                    session.delete(player_teachings[0])
                session.commit()
            return

        if player.skill_points == 0:
            await context.send('You do not have any skill points remaining.')
            return
        if skill.skill_level == ALL_SKILLS[skill_name]['max']:
            await context.send(f'Skill {skill_name} is already maxed.')
            return
        skill.skill_level += 1
        player.skill_points -= 1
        session.commit()

        await context.send(f'Learned {skill_name}!')
        return


def get_skill(session, player, skill_name):
    skill = session.scalars(
        select(PlayerSkill)
        .where(PlayerSkill.player_id == player.id)
        .where(PlayerSkill.skill_name == skill_name)
    ).one_or_none()
    if skill is None:
        skill = PlayerSkill(
            player_id=player.id,
            skill_name=skill_name,
            skill_level=0
        )
        session.add(skill)
    return skill
