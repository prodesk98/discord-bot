from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from databases import Quizzes

async def registerQuizzesHistory(async_session: AsyncSession, quizzes: Quizzes) -> None:
    async with async_session as session:
        session.add(quizzes)
        await session.commit()
