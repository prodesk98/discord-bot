from discord import Role
from config import env
from typing import List
from sqlalchemy import select, func
from .math import normalize_value
from database import AsyncDatabaseSession, User


def has_bot_manager_permissions(roles: List[Role]):
    return env.BOT_MANAGE_ROLE in [role.name for role in roles]

async def has_account(discord_user_id: int) -> bool:
    async with AsyncDatabaseSession as session:
        return normalize_value(
            (await session.execute(
            select(func.count(User.id).label("count")).where(User.discord_user_id == str(discord_user_id)))).scalar()) > 0  # type: ignore
