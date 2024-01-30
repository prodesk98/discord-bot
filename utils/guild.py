from typing import List

from database import AsyncDatabaseSession, Guild, User, Scores
from sqlalchemy import select, func, asc, desc, distinct, null

from models import GuildMemberRanking, GuildRanking
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

async def get_guild_by_user_id(user_id: int) -> Guild:
    async with AsyncDatabaseSession as session:
        guild = (await session.execute(
            select(Guild).join(User).where(User.id == user_id).where(Guild.id == User.guild_id) # type: ignore
        )).scalar()
        return guild

async def get_guild_by_id(guild_id: int) -> Guild|None:
    async with AsyncDatabaseSession as session:
        return (await session.execute(
            select(Guild).where(Guild.id == guild_id) # type: ignore
        )).scalar()

async def guild_ranking(discord_guild_id: int) -> List[GuildRanking]:
    result: List[GuildRanking] = []
    async with AsyncDatabaseSession as session:
        guilds = (await session.execute(
            select(
                Guild.name,
                Guild.id,
                func.coalesce(func.sum(Scores.amount), 0).label('xp'),
                func.count(distinct(User.id)).label('members') # type: ignore
            )
            .select_from(Guild)
            .outerjoin(
                User,
                ((Guild.id == User.guild_id) & (User.discord_guild_id == str(discord_guild_id)))) # type: ignore
            .outerjoin(
               Scores,
               (User.id == Scores.user_id) &
               (User.guild_id == Guild.id)
            )
            .group_by(Guild.id, Guild.name)
            .order_by(desc("xp"), asc(Guild.id))  # type: ignore
            .limit(10)
        )).fetchall()
    for guild in guilds:
        name, id, xp, members = guild
        result.append(
            GuildRanking(
                id=id,
                name=name,
                xp=xp,
                members=members
            )
        )
    return result

async def get_ranking_members_guild(guild_id: int, discord_guild_id: int) -> List[GuildMemberRanking]:
    async with AsyncDatabaseSession as session:
        subquery = (
            select(
                User.discord_user_id,
                func.coalesce(func.sum(Scores.amount), 0).label('xp')
            )
            .select_from(Guild)
            .outerjoin(User,
                       ((Guild.id == guild_id) & (User.guild_id == guild_id) & (User.discord_guild_id == str(discord_guild_id))))  # type: ignore
            .outerjoin(Scores, User.id == Scores.user_id) # type: ignore
            .group_by(User.discord_user_id, Guild.id)
            .order_by(desc("xp"), asc(Guild.id))  # type: ignore
            .alias()
        )
        results = (await session.execute(
            select(
                subquery.c.discord_user_id,
                func.sum(subquery.c.xp).label('xp')
            )
            .select_from(subquery)
            .where(subquery.c.discord_user_id != null())
            .group_by(subquery.c.discord_user_id)
            .order_by(desc(func.sum(subquery.c.xp)), subquery.c.discord_user_id)
            .limit(10)
        )).fetchall()
        ranking_members: List[GuildMemberRanking] = []
        for result in results:
            discord_user_id, xp = result
            ranking_members.append(
                GuildMemberRanking(
                    score=xp,
                    discord_user_id=discord_user_id
                )
            )
        return ranking_members

async def guild_members_count(guild_id: int, discord_guild_id: int) -> int:
    async with AsyncDatabaseSession as session:
        return normalize_value((await session.execute(
            select(func.count(User.id).label("members"))
            .select_from(Guild)
            .join(User)
            .where(User.discord_guild_id == str(discord_guild_id)) # type: ignore
            .where(User.guild_id == guild_id) # type: ignore
            .group_by(User.guild_id)
        )).scalar())

async def guild_scores_count(guild_id: int, discord_guild_id: int) -> int:
    async with AsyncDatabaseSession as session:
        return normalize_value((await session.execute(
            select(func.sum(Scores.amount).label("xp"))
            .select_from(Scores)
            .join(User)
            .join(Guild)
            .where(User.discord_guild_id == str(discord_guild_id))  # type: ignore
            .where(User.guild_id == guild_id) # type: ignore
            .where(User.id == Scores.user_id)
        )).scalar())

async def recruit_guild(user_id: int, discord_guild_id: int) -> Guild:
    async with AsyncDatabaseSession as session:
        guild_available = await session.execute(
            select(
                Guild.id,
                func.count(User.id).label("members")
            )
            .select_from(Guild)
            .outerjoin(User, ((Guild.id == User.guild_id) & (User.discord_guild_id == str(discord_guild_id)))) # type: ignore
            .group_by(Guild.id)
            .order_by(asc("members"), asc(Guild.id)) # type: ignore
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
