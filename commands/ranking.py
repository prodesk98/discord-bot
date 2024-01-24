from discord import Interaction, Embed
from databases import Scores, User, async_session
from sqlalchemy import select, func, desc


async def RankingCommand(interaction: Interaction) -> Embed:
    async with async_session as session:
        rank = (await session.execute(
            select(
                func.sum(Scores.amount)
                .label('rank')
            ).join(User)
            .order_by(desc("rank"))
            .limit(10)
        )).scalars()
        print(rank)
    return Embed(
        title="Ranking",
        description="debug"
    )
