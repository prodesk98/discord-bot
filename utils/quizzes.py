from typing import List

from cache import aget, aset
from config import env
from datetime import datetime
from sqlalchemy import func, select, join
from models import QuizLimitedByTimeResponse, QuizEnumChoices
from database import AsyncDatabaseSession, Quizzes, QuizBet, User
from .math import normalize_value

async def registerQuizzesHistory(quizzes: Quizzes) -> None:
    async with AsyncDatabaseSession as session:
        session.add(quizzes)
        await session.commit()

async def bet_quiz(user_id: int, guild_id: str, quiz_id: int, choice: QuizEnumChoices, amount: int) -> int|None:
    payload: bytes|None = await aget(f"quiz:payload:{guild_id}:{quiz_id}")
    if payload is None:
        return None
    bet = QuizBet(
        quiz_id=quiz_id,
        user_id=user_id,
        amount=amount,
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

async def count_quiz_erros(quiz_id: int, truth: QuizEnumChoices) -> int:
    async with AsyncDatabaseSession as session:
        return normalize_value(
            (await session.execute(
                select(func.count(QuizBet.id).label("count")).where(QuizBet.choice != truth).where(QuizBet.quiz_id == quiz_id) # type: ignore
            )).scalar()
        )

async def get_quiz_by_id(quiz_id: int) -> Quizzes|None:
    async with AsyncDatabaseSession as session:
        result: Quizzes|None = (await session.execute(select(Quizzes).where(Quizzes.id==quiz_id))).scalar_one_or_none() # type: ignore
        if result is None:
            return None
        return result

def get_time_id() -> str:
    current_time = datetime.now()
    current_time_id = "night"
    if 0 <= current_time.hour < 12:
        current_time_id = "morning"
    elif 12 <= current_time.hour < 18:
        current_time_id = "afternoon"
    return current_time_id

async def quiz_is_limited_by_time() -> QuizLimitedByTimeResponse:
    time_id = get_time_id()
    def translate(k: str) -> str:
        return {
            "night": "Noite",
            "morning": "Manhã",
            "afternoon": "Tarde"
        }.get(k, "night")
    return QuizLimitedByTimeResponse(
        allowed=normalize_value(await aget(f"open_quiz:{time_id}")) <= env.LIMIT_OPEN_QUIZ_BY_TIME * (2 if time_id == "night" else 1),  #boost x2 night
        current_time=translate(time_id)
    )

async def register_count_current_time() -> None:
    def normal(v: bytes|None) -> str:
        if v is None:
            return "0"
        return v.decode()

    time_id = get_time_id()
    count = normalize_value(normal(await aget(f"open_quiz:{time_id}"))) + 1
    await aset(
        name=f"open_quiz:{time_id}",
        value=str(count).encode(),
        ex=3600*7
    )

def calc_bonus(total: int, value_erros: int, total_erros) -> int:
    return total + (value_erros * total_erros)
