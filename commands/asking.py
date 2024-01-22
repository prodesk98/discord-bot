from discord import Embed, Interaction
from aiohttp import ClientSession
from databases import async_session, User

from sqlalchemy import select
from typing import Union

from utils import registerCoinHistory, hasCoinsAvailable

from config import env


async def AskingCommand(
    interaction: Interaction,
    question: str
) -> Embed:
    async with async_session as session:
        user: Union[User, None] = (await session.execute(select(User).where(User.discord_user_id == str(interaction.user.id)))).scalars().one_or_none()
        if user is None:
            await interaction.edit_original_response(embed=Embed(
                title="Acesso bloqueado!",
                description="Você precisa ter uma conta para executar esse comando.\n\nExecute /coins",
                color=0xE02B2B
            ))
            return None

    if not (await hasCoinsAvailable(async_session, user.id, 20)):
        await interaction.edit_original_response(embed=Embed(
            title="Sem saldo",
            description="Você precisa de 20 coins para executar esse comando.\n\nExecute /coins",
            color=0xE02B2B
        ))
        return None

    async with ClientSession() as session:
        async with session.post(f"{env.LEARN_BOT_ENDPOINT}/asking", headers={
            "Authorization": f"Bearer {env.LEARN_BOT_AUTHORIZATION}"
        }, json={
          "q": question,
          "username": user.discord_nick
        }) as response:
            if response.ok:
                data: dict = await response.json()
                await registerCoinHistory(async_session, user.id, -20)
                return Embed(
                    title="🤖 ROBÔ RESPONDE",
                    description=f"**Pergunta: ** %s\n\n**Resposta: ** %s" % (
                        question.capitalize(),
                        data.get("response", "")
                    ),
                    color=0x147BBD
                )

    await interaction.edit_original_response(
        embed=Embed(
            title="Error!",
            description=f"Houve um erro com a resposta. Por favor, verifique a API de respostas: {env.LEARN_BOT_ENDPOINT}",
            color=0xE02B2B
        )
    )
    return None