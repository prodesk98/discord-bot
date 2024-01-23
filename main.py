from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord import (
    Intents, Embed, Interaction,
    app_commands, File
)

from config import env
from loguru import logger

from commands import (
    CoinsCommand,
    InstructCommand,
    AskingCommand,
    QuizCommand,
    QuizFinished
)
from utils import has_bot_manager_permissions
from cache import aget, adel
from orjson import loads

intents = Intents.default()

class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=".",
            intents=intents,
            help_command=None,
        )

    async def on_ready(self) -> None:
        logger.info(f"Loaded commands slash...")
        await self.tree.sync()

    async def setup_hook(self) -> None:
        logger.info(f"Logged in as {self.user.name}")


bot = Bot()

@bot.tree.command(
    name="quiz",
    description="Criar um Quiz"
)
@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
async def quiz(interaction: Interaction, tema: str, premio: int):
    if not has_bot_manager_permissions(interaction.user.roles):
        raise Exception("Você não tem permissão para criar um quiz.")
    if env.LEARN_BOT_ENDPOINT is None or env.LEARN_BOT_AUTHORIZATION is None:
        raise Exception("API não foi configurado corretamente.")
    if not env.LEARN_BOT_ENABLED:
        raise Exception("API desativada")

    theme_words_size = len(tema.split())
    if theme_words_size < 3:
        raise Exception("Tema muito pequeno, é necessário no mínimo 4 palavras.")
    elif len(tema) > 65:
        raise Exception("Tema excedeu o limite máximo de 65 caracteres.")

    await interaction.response.defer(ephemeral=False)

    embed, view, quiz_id = await QuizCommand(interaction, tema, premio)
    if embed is None:
        return
    await interaction.edit_original_response(embed=embed, view=view)

    QuizManager(quiz_id, interaction).quizStatus.start()

class QuizManager(commands.Cog):
    def __init__(self, quiz_id: int, interaction: Interaction):
        self.counter = 0
        self.quiz_id = quiz_id
        self.interaction = interaction
        self.ABCD = {
            0: "A",
            1: "B",
            2: "C",
            3: "D"
        }

    @tasks.loop(seconds=1.0)
    async def quizStatus(self):
        quizOpened = await aget(f"quiz:open_bets:{self.quiz_id}")
        if quizOpened is None:
            await QuizFinished(self.interaction, self.quiz_id, loads(await aget("quiz:opened"))["bets"])
            await adel(f"quiz:open_bets:{self.quiz_id}", "quiz:opened")
            self.quizStatus.cancel()
            return
        self.counter += 1

        data: dict = loads(quizOpened)
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

@bot.tree.command(
    name="asking",
    description="Perguntar ao robô"
)
@app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.guild_id, i.user.id))
async def asking(interaction: Interaction, pergunta: str):
    if env.LEARN_BOT_ENDPOINT is None or env.LEARN_BOT_AUTHORIZATION is None:
        raise Exception("API não foi configurado corretamente.")
    if not env.LEARN_BOT_ENABLED:
        raise Exception("API desativada")

    await interaction.response.defer(ephemeral=False)

    embed = await AskingCommand(interaction, pergunta)
    if embed is None:
        return
    await interaction.edit_original_response(embed=embed)


@bot.tree.command(
    name="instruct",
    description="Ensinar ao robô"
)
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def instruct(interaction: Interaction, texto: str):
    if not has_bot_manager_permissions(interaction.user.roles):
        raise Exception("Você não tem permissão para ensinar o robô.")
    if env.LEARN_BOT_ENDPOINT is None or env.LEARN_BOT_AUTHORIZATION is None:
        raise Exception("API não foi configurado corretamente.")
    if not env.LEARN_BOT_ENABLED:
        raise Exception("API desativada")

    text_size = len(texto)
    if text_size < 65:
        raise Exception("Texto muito pequeno, é necessário no mínimo 65 caracteres.")
    elif text_size > 4000:
        raise Exception("Texto excedeu o limite máximo de 4000 caracteres.")

    await interaction.response.defer(ephemeral=True)

    embed, file = await InstructCommand(interaction, texto)
    if embed is None:
        return
    await interaction.edit_original_response(embed=embed, content="", attachments=[file])


@bot.tree.command(
    name="ping",
    description="Latência do servidor"
)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
async def ping(interaction: Interaction):
    if not has_bot_manager_permissions(interaction.user.roles):
        raise Exception("Você não tem permissão para executar esse comando.")

    embed = Embed(
        title="🏓 Pong!",
        description=f"The bot latency is {round(interaction.client.latency * 1000)}ms.",
        color=0x3836B5
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="me",
    description="Minha conta"
)
@app_commands.checks.cooldown(2, 15, key=lambda i: (i.guild_id, i.user.id))
async def me(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    embed, file = await CoinsCommand(interaction)
    await interaction.edit_original_response(embed=embed, content="", attachments=[file])

@ping.error
@me.error
@instruct.error
@asking.error
@quiz.error
async def on_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        embed = Embed(
            title="⌛ Cooldown!",
            description=f"You are executing the same command in a short amount of time.\n{error}",
            color=0xE02B2B
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = Embed(
        title="❌ Error!",
        description=f"{error}",
        color=0xE02B2B
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


bot.run(env.TOKEN)

