from typing import List

from database import AsyncDatabaseSession, Guild, User, Scores
from sqlalchemy import select, func, asc, desc

from models import GuildRanking
from .math import  normalize_value


async def has_user_guild(user_id: int) -> bool:
    async with AsyncDatabaseSession as session:
        guild = normalize_value((
            await session.execute(
                select(func.count(Guild.id)).join(User).where(User.id == user_id).where(Guild.id == User.guild_id) # type: ignore
                )
            ).scalar()
        )
        return guild > 0

async def get_user_guild(user_id: int) -> Guild:
    async with AsyncDatabaseSession as session:
        guild = (await session.execute(
            select(Guild).join(User).where(User.id == user_id).where(Guild.id == User.guild_id) # type: ignore
        )).scalar()
        return guild

async def get_ranking_members_guild(guild_id: int) -> List[GuildRanking]:
    async with AsyncDatabaseSession as session:
        results = (await session.execute(
            select(User.discord_user_id, func.sum(Scores.amount).label('xp'))
            .select_from(Guild)
            .join(User)
            .join(Scores)
            .where(Guild.id == guild_id) # type: ignore
            .where(User.guild_id == Guild.id)
            .where(User.id == Scores.user_id)
            .group_by(User.discord_user_id)
            .order_by(desc("xp"))
            .limit(10)
        )).fetchall()
        ranking_members: List[GuildRanking] = []
        for result in results:
            discord_user_id, xp = result
            ranking_members.append(
                GuildRanking(
                    score=xp,
                    discord_user_id=discord_user_id
                )
            )
        return ranking_members

async def guild_members_count(guild_id: int) -> int:
    async with AsyncDatabaseSession as session:
        return normalize_value((await session.execute(
            select(func.count(User.id).label("members"))
            .select_from(Guild)
            .join(User)
            .where(User.guild_id == guild_id) # type: ignore
            .group_by(User.guild_id)
        )).scalar())

async def guild_scores_count(guild_id: int) -> int:
    async with AsyncDatabaseSession as session:
        return normalize_value((await session.execute(
            select(func.sum(Scores.amount).label("xp"))
            .select_from(Scores)
            .join(User)
            .join(Guild)
            .where(User.guild_id == guild_id) # type: ignore
            .where(User.id == Scores.user_id)
        )).scalar())

async def recruit_guild(user_id: int) -> Guild:
    async with AsyncDatabaseSession as session:
        guild_available = await session.execute(
            select(Guild.id, func.count(User.id).label("members"))
            .select_from(Guild)
            .outerjoin(User, Guild.id == User.guild_id) # type: ignore
            .group_by(Guild.id)
            .order_by(asc("members"))
            .limit(1)
        )
        available = guild_available.scalar()

        user: User = (await session.execute(
                select(User).where(User.id == user_id) # type: ignore
        )).scalar()
        user.guild_id = available

        guild = (await session.execute(
            select(Guild).join(User)
            .where(Guild.id == User.guild_id) # type: ignore
            .where(User.id == user_id)
        )).scalar()

        await session.commit()
        return guild
