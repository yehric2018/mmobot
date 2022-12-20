import asyncio

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from mmobot.db import initialize_engine


engine = initialize_engine()

jobstores = {
    'default': SQLAlchemyJobStore(engine=engine)
}


async def print_message_async():
    print('Hello how are you')


scheduler = AsyncIOScheduler(jobstores=jobstores)
scheduler.add_job(print_message_async, 'interval', seconds=10, id='example')
scheduler.start()


print('Starting events bot...')
asyncio.get_event_loop().run_forever()
