import asyncio
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import AsyncDatabaseSession, Scores
from sqlalchemy import delete


async def expired_score():
    async with AsyncDatabaseSession as session:
        await session.execute(
            delete(Scores).where(Scores.created_at <= datetime.now() - timedelta(days=15)) # type: ignore
        )
        await session.commit()


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(expired_score, 'interval', minutes=15)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass