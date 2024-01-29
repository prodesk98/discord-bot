from database import AsyncDatabaseSession, User
from sqlalchemy import select

async def get_user_by_discord_user_id(discord_user_id: int, discord_guild_id: int) -> User|None:
    async with AsyncDatabaseSession as session:
        return (
            await session.execute(
                select(User)
                .where(User.discord_guild_id == str(discord_guild_id)) #type: ignore
                .where(User.discord_user_id == str(discord_user_id)) #type: ignore
            )
        ).scalar_one_or_none()
