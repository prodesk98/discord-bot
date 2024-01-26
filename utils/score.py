from sqlalchemy import select, func
from database import Scores, AsyncDatabaseSession
from utils import math

LEVELS = {
    0: "coin",
    1: "gold",
    2: "diamond",
    3: "king"
}

STICKERS = {
    "coin": ":egg:",
    "gold": ":crossed_swords:",
    "diamond": ":gem:",
    "king": ":crown:"
}

LVL_NUMBER = {
    "coin": 1,
    "gold": 2,
    "diamond": 3,
    "king": 4
}


async def registerScore(user_id: int, amount: int) -> None:
    async with AsyncDatabaseSession as session:
        session.add(
            Scores(
                user_id=user_id,
                amount=amount,
            )
        )
        await session.commit()

async def getStickerByIdUser(user_id: int) -> str:
    async with AsyncDatabaseSession as session:
        score = (
            await session.execute(
                select(func.sum(Scores.amount)).where(
                    Scores.user_id == user_id # type: ignore
                )
            )
        ).scalar()
        score = math.normalize_value(score)
        return LevelSticker(scoreToLevel(score))

def hasLevelPermissions(score: int, minimo: int = 1) -> bool:
    return LevelNumber(scoreToLevel(score)) >= minimo


def scoreToSticker(score: int) -> str:
    return LevelSticker(scoreToLevel(score))

def scoreToLevel(score: int) -> str:
    if score <= 50:
        return LEVELS.get(0)
    elif 50 < score <= 500:
        return LEVELS.get(1)
    elif 500 < score <= 1000:
        return LEVELS.get(2)
    return LEVELS.get(3)

def LevelSticker(level: str) -> str:
    return STICKERS.get(level, "coin")

def LevelNumber(level: str) -> int:
    return LVL_NUMBER.get(level, 1)
