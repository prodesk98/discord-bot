from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from databases import Scores, User


async def registerScore(async_session: AsyncSession, user_id: int, amount: int) -> None:
    async with async_session as session:
        session.add(
            Scores(
                user_id=user_id,
                amount=amount,
            )
        )
        await session.commit()

async def getStickerByIdUser(async_session, user_id: int) -> str:
    async with async_session as session:
        score = (
            await session.execute(
                select(func.sum(Scores.amount)).where(
                    Scores.user_id == user_id
                )
            )

        ).scalar()
        score = 0 if score is None else score
        return LevelSticker(scoreToLevel(score))

def hasLevelPermissions(score: int, minimo: int = 1) -> bool:
    return LevelNumber(scoreToLevel(score)) >= minimo

def scoreToLevel(score: int) -> str:
    LEVELS = {
        0: "coin",
        1: "gold",
        2: "diamond",
        3: "king"
    }
    if score < 50:
        return LEVELS.get(0)
    elif 50 <= score < 500:
        return LEVELS.get(1)
    elif 500 <= score < 1000:
        return LEVELS.get(2)
    return LEVELS.get(3)

def LevelSticker(level: str) -> str:
    STICKERS = {
        "coin": ":egg:",
        "gold": ":crossed_swords:",
        "diamond": ":gem:",
        "king": ":crown:"
    }
    return STICKERS.get(level, "coin")

def LevelNumber(level: str) -> int:
    LVL_NUMBER = {
        "coin": 1,
        "gold": 2,
        "diamond": 3,
        "king": 4
    }
    return LVL_NUMBER.get(level, 1)