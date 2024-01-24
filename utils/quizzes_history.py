from sqlalchemy.ext.asyncio import AsyncSession
from cache import aget, aset
from databases import Quizzes
from config import env
from datetime import datetime

from models import QuizLimitedByTimeResponse

async def registerQuizzesHistory(async_session: AsyncSession, quizzes: Quizzes) -> None:
    async with async_session as session:
        session.add(quizzes)
        await session.commit()

async def quiz_is_limited_by_time() -> QuizLimitedByTimeResponse:
    def normalize(value: str|None) -> int:
        if value is None:
            return 0
        return int(value)

    current_time = datetime.now()
    if 0 <= current_time.hour < 12:
        return QuizLimitedByTimeResponse(
            allowed=normalize(await aget("open_quiz:morning")) <= env.LIMIT_OPEN_QUIZ_BY_TIME,
            current_time="Manhã"
        )
    elif 12 <= current_time.hour < 18:
        return QuizLimitedByTimeResponse(
            allowed=normalize(await aget("open_quiz:afternoon")) <= env.LIMIT_OPEN_QUIZ_BY_TIME,
            current_time="Tarde"
        )
    return QuizLimitedByTimeResponse(
        allowed=normalize(await aget("open_quiz:night")) <= env.LIMIT_OPEN_QUIZ_BY_TIME * 2,  #boost x2
        current_time="Noite"
    )

async def register_count_current_time() -> None:
    def normalize(value: str|None) -> int:
        if value is None:
            return 0
        return int(value)

    current_time = datetime.now()
    current_time_id = "night"
    if 0 <= current_time.hour < 12:
        current_time_id = "morning"
    elif 12 <= current_time.hour < 18:
        current_time_id = "afternoon"

    await aset(
        name=f"open_quiz:{current_time_id}",
        value=str(normalize(await aget(f"open_quiz:{current_time_id}"))).encode(),
        ex=3600*7
    )
