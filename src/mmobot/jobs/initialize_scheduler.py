from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .cron import decrement_hp, recover_endurance


EVERY_TWO_HOURS = '0-23/2'


def initialize_scheduler(engine, client):
    jobstores = {
        'default': SQLAlchemyJobStore(engine=engine)
    }
    scheduler = AsyncIOScheduler(jobstores=jobstores)

    # Initialize all the fixed cron jobs
    # scheduler.add_job(
    #     decrement_hp,
    #     'cron',
    #     [client, scheduler],
    #     hour=EVERY_TWO_HOURS,
    #     minute=4
    # )
    scheduler.start()
    return scheduler
