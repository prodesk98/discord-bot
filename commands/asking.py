from discord import Embed, Interaction
from aiohttp import ClientSession
from database import AsyncDatabaseSession, User, Scores

from sqlalchemy import select, func
from typing import Union

from utils import registerCoinHistory, hasCoinsAvailable, hasLevelPermissions, has_account

from config import env


async def AskingCommand(
    interaction: Interaction,
    question: str
) -> None:
    if not (await has_account(interaction.user.id)):
        await interaction.edit_original_response(embed=Embed(
            title="Acesso bloqueado!",
            description="Você precisa ter uma conta para executar esse comando.\n\nExecute /me",
            color=0xE02B2B
        ))
        return None

    async with AsyncDatabaseSession as session:
        user: Union[User, None] = (
            await session.execute(
                select(User)
                .where(User.discord_user_id == str(interaction.user.id))) #type: ignore
        ).scalar()

    score = (
        await session.execute(
            select(func.sum(Scores.amount)).where(
                Scores.user_id == user.id  #type: ignore
            )
        )
    ).scalar()
    score = 0 if score is None else score
    if not hasLevelPermissions(score, 2):
        await interaction.edit_original_response(embed=Embed(
            title="Nível baixo!",
            description="Você precisa ter no mínimo 2 Níveis para executar esse comando.\n\nExecute /me - para ver o seu nível\nExecute /level - para mais informações...",
            color=0xE02B2B
        ))
        return None

    asking_cost = env.ASKING_COST
    if not (await hasCoinsAvailable(user.id, asking_cost)):
        await interaction.edit_original_response(
            embed=Embed(
                title="Sem saldo",
                description=f"Você precisa de {asking_cost} coins para executar esse comando.\n\nExecute /me",
                color=0xE02B2B
            )
        )
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
                await registerCoinHistory(AsyncDatabaseSession, user.id, -asking_cost)
                await interaction.edit_original_response(
                    embed=Embed(
                        title="🤖 ROBÔ RESPONDE",
                        description=f"**Pergunta: ** %s\n\n**Resposta: ** %s" % (
                            question.capitalize(),
                            data.get("response", "")
                        ),
                        color=0x147BBD
                    )
                )
                return None

    await interaction.edit_original_response(
        embed=Embed(
            title="Error!",
            description=f"Houve um erro com a resposta. Por favor, verifique a API de respostas: {env.LEARN_BOT_ENDPOINT}",
            color=0xE02B2B
        )
    )