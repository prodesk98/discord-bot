from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from databases import CoinsHistory, User


async def registerCoinHistory(async_session: AsyncSession, user_id: int, amount: int) -> None:
    async with async_session as session:
        session.add(
            CoinsHistory(
                user_id=user_id,
                amount=amount,
            )
        )
        await session.commit()


async def hasCoinsAvailable(async_session: AsyncSession, user_id: int, amount: int) -> bool:
    async with async_session as session:
        balance = (await session.execute(
            select(func.sum(CoinsHistory.amount)).where(
                User.id == user_id
            )
        )).scalar()
        await session.close()

    return balance >= amount
