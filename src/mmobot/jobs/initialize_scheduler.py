from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from .cron import recover_endurance, recover_hp


EVERY_TWO_HOURS = '0-23/2'


def initialize_scheduler(engine):
    jobstores = {
        'default': SQLAlchemyJobStore(engine=engine)
    }
    scheduler = BackgroundScheduler(jobstores)

    # Initialize all the fixed cron jobs
    scheduler.add_job(recover_hp, 'cron', [engine], hour=EVERY_TWO_HOURS, minute=1)
    scheduler.add_job(recover_endurance, 'cron', [engine], hour=EVERY_TWO_HOURS, minute=31)
    return scheduler
