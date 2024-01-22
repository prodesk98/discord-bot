from discord import Role
from config import env
from typing import List

def has_bot_manager_permissions(roles: List[Role]):
    return env.BOT_MANAGE_ROLE in [role.name for role in roles]
