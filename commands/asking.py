from discord import Embed, Interaction
from aiohttp import ClientSession
from databases import async_session, User, Scores

from sqlalchemy import select, func
from typing import Union

from utils import registerCoinHistory, hasCoinsAvailable, hasLevelPermissions

from config import env


async def AskingCommand(
    interaction: Interaction,
    question: str
) -> Embed|None:
    asking_cost = env.ASKING_COST

    async with async_session as session:
        user: Union[User, None] = (
            await session.execute(
                select(User)
                .where(User.discord_user_id == str(interaction.user.id))) #type: ignore
        ).scalar()

        if user is None:
            await interaction.edit_original_response(embed=Embed(
                title="Acesso bloqueado!",
                description="Você precisa ter uma conta para executar esse comando.\n\nExecute /me",
                color=0xE02B2B
            ))
            return None

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
            description="Você precisa ter no mínimo 2 Níveis para executar esse comando.",
            color=0xE02B2B
        ))
        return None


    if not (await hasCoinsAvailable(async_session, user.id, asking_cost)):
        await interaction.edit_original_response(embed=Embed(
            title="Sem saldo",
            description="Você precisa de 20 coins para executar esse comando.\n\nExecute /me",
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
                await registerCoinHistory(async_session, user.id, -asking_cost)
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