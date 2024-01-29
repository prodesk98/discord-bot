from discord import Embed, Interaction
from aiohttp import ClientSession
from database import Quizzes
from cache import aget, aset
from orjson import loads, dumps

from manager import QuizManager
from utils import (
    registerQuizzesHistory,
    PlayAudioEffect, has_account, get_user_by_discord_user_id, quiz_is_limited_by_time, register_count_current_time
)
from config import env
from models import Quiz, QuizEnumStatus, ALTERNATIVES
from views import QuizChoicesButtons


async def create(data: Quiz, theme: str, amount: int, interaction: Interaction) -> None:
    embed = Embed(
        title=data.question,
        description="**Prêmio Inicial: ** :coin: %.2f coins **+bônus**\n**Bilhete: ** :tickets: %.2f" % (
            amount * env.QUIZ_MULTIPLIER,
            amount
        ),
        color=0x147BBD
    )

    for q, alternative in enumerate(data.alternatives):
        embed.add_field(name=f"{ALTERNATIVES.get(q + 1, None)}) {alternative}"[:256], value="", inline=False)
    embed.set_footer(text="Encerra em 15 segundos...")

    metadata = dict(
        status=QuizEnumStatus.opened,
        amount=amount,
        theme=theme,
        question=data.question,
        alternatives=data.alternatives,
        truth=data.truth,
        voice_url=data.voice_url
    )
    quizzes = Quizzes(**metadata)

    user = await get_user_by_discord_user_id(interaction.user.id, interaction.guild_id)

    await registerQuizzesHistory(quizzes)
    await aset(f"quiz:opened:{user.discord_guild_id}", str(quizzes.id).encode(), ex=17)
    await aset(f"quiz:payload:{user.discord_guild_id}:{quizzes.id}", dumps(metadata), ex=15)
    await PlayAudioEffect(interaction, "quiz_started.wav")

    QuizManager(interaction=interaction, buttons=QuizChoicesButtons(quizzes.id, user.discord_guild_id, amount)).quizStatus.start()


async def QuizCommand(
    interaction: Interaction,
    theme: str,
    amount: int
) -> None:
    if not (await has_account(interaction.user.id, interaction.guild_id)):
        raise Exception("Você precisa ter uma conta para executar esse comando.\n\nExecute /me")

    user = await get_user_by_discord_user_id(interaction.user.id, interaction.guild_id)

    has_quiz_opened = await aget(f"quiz:opened:{interaction.guild_id}")
    if has_quiz_opened is not None:
        raise Exception("Aguarde o encerramento do último quiz para abrir um novo.")

    if amount > 500:
        raise Exception("O valor da aposta não pode exceder 500 coins.")
    elif amount < 50:
        raise Exception("O valor mínimo não pode ser inferior a 50 coins.")

    quiz_limited = (await quiz_is_limited_by_time())
    if not quiz_limited.allowed:
        raise Exception(f"Foi atingido o limite no horário {quiz_limited.current_time}, por favor, tente novamente mais tarde.")

    async with ClientSession() as session:
        async with session.post(f"{env.LEARN_BOT_ENDPOINT}/questionnaire", headers={
            "Authorization": f"Bearer {env.LEARN_BOT_AUTHORIZATION}"
        }, json={
          "theme": theme,
          "amount": amount,
          "namespace": f"default_{user.discord_guild_id}"
        }) as response:
            if response.ok:
                data: Quiz = Quiz(**loads(await response.content.read()))
                await create(data, theme, amount, interaction)
                await register_count_current_time()
            else:
                raise Exception(f"Houve um erro com a resposta. Por favor, verifique a API de respostas: http(s)//<END_POINT>/questionnaire")
