from random import randint
from typing import List

from discord.ext import commands, tasks
from discord import Interaction, Embed, File
from orjson import loads
from cache import aget
from config import env
from database import User, QuizBet, AsyncDatabaseSession, CoinsHistory, Scores
from models import ALTERNATIVES, get_alternative_by_name, Quiz, QuizEnumStatus
from utils import (
    PlayAudioEffect, getStickerByIdUser, get_quiz_all_bet,
    get_quiz_by_id, count_quiz_erros, calc_bonus
)
from views import QuizChoicesButtons

async def QuizFinished(
    interaction: Interaction,
    quiz_id: int
) -> None:
    quiz = await get_quiz_by_id(quiz_id)
    if quiz is None:
        return

    erros_count = await count_quiz_erros(quiz_id, quiz.truth)
    total_prize: int = calc_bonus(quiz.amount * env.QUIZ_MULTIPLIER, 100, erros_count)

    alternatives_string = '\n'.join(['%s) %s' % (ALTERNATIVES.get(q+1, None), al) for q, al in enumerate(quiz.alternatives)])
    choice: int = get_alternative_by_name(quiz.truth.name)
    embed = Embed(
        title=quiz.question,
        description=f"{alternatives_string}"
                    f"\n\nPrêmio: :coin: {total_prize} coins\n"
                    f"Resposta correta: **({ALTERNATIVES.get(choice, None)})** "
                    f"{quiz.alternatives[choice - 1]}\n\n",
        color=0x3A8B63
    )

    results = await get_quiz_all_bet(quiz_id)

    awarded = ''
    losers = ''
    result: tuple[QuizBet, User]
    objects: List[CoinsHistory|Scores] = []

    async with AsyncDatabaseSession as session:
        for result in results:
            bet, user = result
            user_id = bet.user_id
            choice = bet.choice
            if choice == quiz.truth:
                score = randint(10, 20) * erros_count
                awarded += f'\n{await getStickerByIdUser(user_id)} <@{user.discord_user_id}> +{score}xp:zap:'
                objects.extend(
                    [
                        CoinsHistory(
                            user_id=user_id,
                            amount=total_prize,
                        ),
                        Scores(
                            user_id=user_id,
                            amount=score,
                        )
                    ]
                )
            else:
                losers += (f'\n({ALTERNATIVES.get(bet.choice.value)})'
                           f'{await getStickerByIdUser(user_id)} <@{user.discord_user_id}>')

        quiz.status = QuizEnumStatus.closed
        session.add_all(objects)
        await session.commit()

    embed.add_field(name=":trophy: Acertos", value=awarded, inline=True)
    embed.add_field(name=":x: Erros", value=losers, inline=True)
    embed.remove_footer()
    await interaction.delete_original_response()
    await interaction.channel.send(embed=embed)
    await PlayAudioEffect(interaction, "quiz_finished.wav")


class QuizManager(commands.Cog):
    def __init__(self, interaction: Interaction, buttons: QuizChoicesButtons):
        self.counter = 0
        self.buttons = buttons
        self.quiz_id = self.buttons.quiz_id
        self.guild_id = self.buttons.guild_id
        self.interaction = interaction
        self.quiz: Quiz|None = None
        self.finished: bool = False

    @tasks.loop(seconds=1.0)
    async def quizStatus(self) -> None:
        if self.finished:
            self.counter += 1
            if self.counter >= 18:
                await QuizFinished(self.interaction, self.quiz_id)
                self.quizStatus.cancel()
            return

        payload: bytes|None = await aget(f"quiz:payload:{self.guild_id}:{self.quiz_id}")
        if payload is None:
            quiz_finished_embed = Embed(
                title=self.quiz.question,
                description="**Prêmio Inicial: ** :coin: %.2f coins **+bônus**\n**Bilhete: ** :tickets: %.2f" % (
                    self.quiz.amount * env.QUIZ_MULTIPLIER,
                    self.quiz.amount
                ),
                color=0x147BBD
            )
            clock = File(f"assets/gifs/settings/clock.gif", filename=f"clock.gif")
            quiz_finished_embed.set_footer(text=f"Calculando...", icon_url="attachment://clock.gif")
            quiz_finished_embed.clear_fields()
            await self.interaction.edit_original_response(embed=quiz_finished_embed, attachments=[clock])
            self.finished = True
            return

        self.quiz: Quiz = self.quiz if self.quiz is not None else Quiz(**loads(payload))
        embed = Embed(
            title=self.quiz.question,
            description="**Prêmio Inicial: ** :coin: %.2f coins **+bônus**\n**Bilhete: ** :tickets: %.2f" % (
                self.quiz.amount * env.QUIZ_MULTIPLIER,
                self.quiz.amount
            ),
            color=0x147BBD
        )

        self.counter += 1
        if self.counter <= 15:
            embed.set_footer(text=f"Encerra em {15 - self.counter} segundos...")
            for q, alternative in enumerate(self.quiz.alternatives):
                embed.add_field(name=f"{ALTERNATIVES.get(q+1)}) {alternative}"[:256], value="", inline=False)

        else:
            embed.set_footer(text="calculando...")

        await self.interaction.edit_original_response(embed=embed, view=self.buttons)
