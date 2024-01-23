from discord import Embed, Interaction, ui, ButtonStyle, File
from typing import List, Dict

from aiohttp import ClientSession
from databases import async_session, User, Quizzes, Scores

from sqlalchemy import select
from typing import Union

from cache import aget, aset
from orjson import dumps, loads

from utils import registerQuizzesHistory, registerCoinHistory, registerScore, PlayAudioEffect, getStickerByIdUser
from config import env

from random import randint


ALTERNATIVES_LABEL = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4
}

ALTERNATIVES_NUMBER = {
    1: "A",
    2: "B",
    3: "C",
    4: "D"
}


class ViewQuizButtons(ui.View):
    def __init__(self, quiz_id: int):
        super().__init__(timeout=None)
        self.quiz_id = quiz_id

    @ui.button(label="A", style=ButtonStyle.primary)
    async def A(self, interaction: Interaction, button: ui.Button):
        await self.bet(interaction, button, "A")

    @ui.button(label="B", style=ButtonStyle.primary)
    async def B(self, interaction: Interaction, button: ui.Button):
        await self.bet(interaction, button, "B")

    @ui.button(label="C", style=ButtonStyle.primary)
    async def C(self, interaction: Interaction, button: ui.Button):
        await self.bet(interaction, button, "C")

    @ui.button(label="D", style=ButtonStyle.primary)
    async def D(self, interaction: Interaction, button: ui.Button):
        await self.bet(interaction, button, "D")

    async def bet(self, interaction: Interaction, button: ui.Button, id: str):
        quizCache = await aget("quiz:opened")
        if quizCache is None:
            await interaction.response.send_message(embed=Embed(
                title="Quiz fechado!",
                description="Você não pode participar de um quiz que já foi finalizado.",
                color=0xE02B2B
            ), ephemeral=True)
            return

        async with async_session as session:
            user: Union[User, None] = (await session.execute(
                select(User).where(User.discord_user_id == str(interaction.user.id)))).scalars().one_or_none()
            if user is None:
                await interaction.response.send_message(embed=Embed(
                    title="Acesso bloqueado!",
                    description="Você precisa ter uma conta para executar esse comando.\n\nExecute /me",
                    color=0xE02B2B
                ), ephemeral=True)
                return

        bet = await aget(f"quiz:{self.quiz_id}:bet:{user.discord_user_id}")
        if bet is not None:
            await interaction.response.send_message(embed=Embed(
                title="Você não tem permissão!",
                description="Você já escolheu uma alternativa.",
                color=0xE02B2B
            ), ephemeral=True)
            return

        data: dict = loads(quizCache)
        data.get("bets", []).append(
            {
                "discord_id": user.discord_user_id,
                "id": user.discord_user_id,
                "user_id": user.id,
                "choice": ALTERNATIVES_LABEL.get(id, -1)
            }
        )
        await aset("quiz:opened", dumps(data), ex=30)
        await aset(f"quiz:{self.quiz_id}:bet:{user.discord_user_id}", dumps({"bet": 1}), ex=60)
        await interaction.response.send_message(f"Você escolheu a alternativa **{id}**.", ephemeral=True)



async def QuizCommand(
    interaction: Interaction,
    theme: str,
    amount: int
) -> tuple[Embed, ui.View, int]:

    async with async_session as session:
        user: Union[User, None] = (await session.execute(
            select(User).where(User.discord_user_id == str(interaction.user.id)))).scalars().one_or_none()
        if user is None:
            await interaction.edit_original_response(embed=Embed(
                title="Acesso bloqueado!",
                description="Você precisa ter uma conta para executar esse comando.\n\nExecute /me",
                color=0xE02B2B
            ))
            return None, None, None

    quiz_opened = await aget("quiz:opened")
    if quiz_opened is not None:
        await interaction.edit_original_response(embed=Embed(
            title="Não permitido!",
            description="Aguarde o encerramento do último quiz para abrir um novo.",
            color=0xE02B2B
        ))
        return None, None, None

    async with ClientSession() as session:
        async with session.post(f"{env.LEARN_BOT_ENDPOINT}/million-show", headers={
            "Authorization": f"Bearer {env.LEARN_BOT_AUTHORIZATION}"
        }, json={
          "theme": theme,
          "amount": amount
        }) as response:
            if response.ok:
                data: dict = await response.json()
                embed = Embed(
                    title=data.get("question", "").capitalize(),
                    description="**Prêmio: ** :coin: %.2f coins **%iX**\n**Bilhete: ** :tickets: %.2f" % (
                        amount * env.QUIZ_MULTIPLIER,
                        env.QUIZ_MULTIPLIER,
                        amount
                    ),
                    color=0x147BBD
                )
                alternatives = data.get("alternatives", [])
                for q, alternative in enumerate(alternatives):
                    embed.add_field(name=f"{ALTERNATIVES_NUMBER.get(q)}) {alternative}"[:256], value="", inline=False)
                embed.set_footer(text="Encerra em 15 segundos...")
                quizzes = Quizzes(
                    status=1,
                    amount=amount,
                    theme=theme,
                    question=data.get("question", "").capitalize(),
                    alternatives=alternatives,
                    truth=data.get("truth", 99),
                    voice_url=data.get("voice_url", None)
                )
                await registerQuizzesHistory(
                    async_session,
                    quizzes
                )
                await aset("quiz:opened", dumps(
                    {
                        "id": quizzes.id,
                        "amount": quizzes.amount,
                        "truth": quizzes.truth,
                        "bets": []
                    }
                ), ex=30)
                await aset(f"quiz:open_bets:{quizzes.id}", dumps(dict(
                    status=1,
                    amount=amount,
                    theme=theme,
                    question=data.get("question", "").capitalize(),
                    alternatives=alternatives,
                    truth=data.get("truth", 99),
                    voice_url=data.get("voice_url", None)
                )), ex=15)
                await PlayAudioEffect(interaction, "quiz_started.wav")
                return embed, ViewQuizButtons(quizzes.id), quizzes.id

    await interaction.edit_original_response(
        embed=Embed(
            title="Error!",
            description=f"Houve um erro com a resposta. Por favor, verifique a API de respostas: {env.LEARN_BOT_ENDPOINT}",
            color=0xE02B2B
        )
    )

async def QuizFinished(
    interaction: Interaction,
    quiz_id: int,
    bets: List[Dict]
) -> None:
    async with async_session as session:
        quiz: Union[Quizzes, None] = (await session.execute(select(Quizzes).where(Quizzes.id==quiz_id))).scalars().one_or_none()
        if quiz is None:
            return

    total_prize = round(quiz.amount * env.QUIZ_MULTIPLIER, 2)
    alternatives_string = '\n'.join(['%s) %s' % (ALTERNATIVES_NUMBER[q+1], al) for q, al in enumerate(quiz.alternatives)])
    embed = Embed(
        title=quiz.question,
        description=f"{alternatives_string}"
                    f"\n\nPrêmio: :coin: {total_prize} coins\n"
                    f"Resposta correta: **({ALTERNATIVES_NUMBER.get(quiz.truth)})** "
                    f"{quiz.alternatives[quiz.truth - 1]}\n\n",
        color=0x3A8B63
    )

    awarded = ''
    losers = ''
    for bet in bets:
        discord_id = bet.get("discord_id", "")
        user_id = bet.get("user_id", 0)
        choice = bet.get("choice", -1)
        if 0 < choice == quiz.truth:
            score = randint(10, 20)
            awarded += f'\n{await getStickerByIdUser(async_session, user_id)} <@{discord_id}> +{score}xp:zap:'
            await registerCoinHistory(
                async_session,
                user_id=user_id,
                amount=total_prize
            )
            await registerScore(
                async_session,
                user_id=user_id,
                amount=score
            )
        else:
            losers += (f'\n({ALTERNATIVES_NUMBER[choice] if choice > 0 else "(-)"})'
                       f'{await getStickerByIdUser(async_session, user_id)} <@{discord_id}>')

    embed.add_field(name=":trophy: Acertos", value=awarded, inline=True)
    embed.add_field(name=":x: Erros", value=losers, inline=True)
    embed.remove_footer()
    await interaction.delete_original_response()
    await interaction.channel.send(embed=embed)
    await PlayAudioEffect(interaction, "quiz_finished.wav")
