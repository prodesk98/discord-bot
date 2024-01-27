from sqlalchemy import select, func
from database import CoinsHistory, AsyncDatabaseSession


async def registerCoinHistory(user_id: int, amount: int) -> None:
    async with AsyncDatabaseSession as session:
        session.add(
            CoinsHistory(
                user_id=user_id,
                amount=amount,
            )
        )
        await session.commit()


async def hasCoinsAvailable(user_id: int, amount: int) -> bool:
    async with AsyncDatabaseSession as session:
        balance = (await session.execute(
            select(func.sum(CoinsHistory.amount)).where(
                CoinsHistory.user_id == user_id # type: ignore
            )
        )).scalar()
        await session.close()

    return balance >= amount
