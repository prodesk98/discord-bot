from discord import Embed, Interaction
from aiohttp import ClientSession
from databases import async_session, User

from sqlalchemy import select
from typing import Union

from config import env

async def QuizCommand(
    interaction: Interaction,
    theme: str
) -> Embed:
    async with async_session as session:
        user: Union[User, None] = (await session.execute(
            select(User).where(User.discord_user_id == str(interaction.user.id)))).scalars().one_or_none()
        if user is None:
            await interaction.edit_original_response(embed=Embed(
                title="Acesso bloqueado!",
                description="Você precisa ter uma conta para executar esse comando.\n\nExecute /coins",
                color=0xE02B2B
            ))
            return None