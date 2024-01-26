from typing import List

from orjson import loads

from cache import aget, aset
from config import env
from datetime import datetime
from sqlalchemy import func, select, join
from models import QuizLimitedByTimeResponse, QuizEnumChoices, Quiz
from database import AsyncDatabaseSession, Quizzes, QuizBet, User

async def registerQuizzesHistory(quizzes: Quizzes) -> None:
    async with AsyncDatabaseSession as session:
        session.add(quizzes)
        await session.commit()

async def bet_quiz(user_id: int, guild_id: str, quiz_id: int, choice: QuizEnumChoices) -> int|None:
    payload: bytes|None = await aget(f"quiz:payload:{guild_id}:{quiz_id}")
    if payload is None:
        return None
    quiz: Quiz = Quiz(**loads(payload))
    bet = QuizBet(
        quiz_id=quiz_id,
        user_id=user_id,
        amount=quiz.amount,
        choice=choice
    )
    async with AsyncDatabaseSession as session:
        session.add(bet)
        await session.commit()
    return bet.id


async def has_quiz_bet(user_id: int, quiz_id: int) -> bool:
    async with AsyncDatabaseSession as session:
        quiz_bet = (await session.execute(select(
            func.count(QuizBet.id).label("count")
        ).where(QuizBet.user_id == user_id, QuizBet.quiz_id == quiz_id))).scalar() # type: ignore
        if quiz_bet is None or quiz_bet == 0:
            return False
        return True


async def get_quiz_all_bet(quiz_id: int) -> List[QuizBet|User]:
    async with AsyncDatabaseSession as session:
        return (await session.execute(
            select(QuizBet, User).select_from(join(QuizBet, User, onclause=QuizBet.user_id == User.id)) # type: ignore
            .where(QuizBet.quiz_id == quiz_id) # type: ignore
        )).fetchall()

async def get_quiz_by_id(quiz_id: int) -> Quiz|None:
    async with AsyncDatabaseSession as session:
        result: Quizzes|None = (await session.execute(select(Quizzes).where(Quizzes.id==quiz_id))).scalar_one_or_none() # type: ignore
        if result is None:
            return None
        return Quiz(
            question=result.question,
            truth=result.truth,
            alternatives=result.alternatives,
            amount=result.amount,
            voice_url=result.voice_url
        )


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
