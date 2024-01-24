from discord.ext import commands, tasks
from discord import Interaction, Embed
from orjson import loads
from cache import aget, adel
from commands import QuizFinished
from config import env

class QuizManager(commands.Cog):
    ABCD = {
        0: "A",
        1: "B",
        2: "C",
        3: "D"
    }

    def __init__(self, quiz_id: int, interaction: Interaction):
        self.counter = 0
        self.quiz_id = quiz_id
        self.interaction = interaction

    @tasks.loop(seconds=1.0)
    async def quizStatus(self):
        open_betes = await aget(f"quiz:open_bets:{self.quiz_id}")
        if open_betes is None:
            await QuizFinished(self.interaction, self.quiz_id, loads(await aget("quiz:opened"))["bets"])
            await adel(f"quiz:open_bets:{self.quiz_id}", "quiz:opened")
            self.quizStatus.cancel()
            return
        self.counter += 1

        data: dict = loads(open_betes)
        embed = Embed(
            title=data.get("question", "").capitalize(),
            description="**Prêmio: ** :coin: %.2f coins **%iX**\n**Bilhete: ** :tickets: %.2f" % (
                data.get("amount", 0) * env.QUIZ_MULTIPLIER,
                env.QUIZ_MULTIPLIER,
                data.get("amount", 0)
            ),
            color=0x147BBD
        )

        alternatives = data.get("alternatives", [])
        for q, alternative in enumerate(alternatives):
            embed.add_field(name=f"{self.ABCD.get(q)}) {alternative}"[:256], value="", inline=False)

        embed.set_footer(text=f"Encerra em {15 - self.counter} segundos...")
        await self.interaction.edit_original_response(embed=embed)