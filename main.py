from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord import (
    Intents, Embed, Interaction,
    app_commands, File, Attachment, Message
)

from config import env
from loguru import logger

from commands import (
    CoinsCommand,
    InstructCommand,
    AskingCommand,
    QuizCommand,
    QuizFinished,
    RankingCommand,
    BettingEventCommand
)
from utils import has_bot_manager_permissions
from cache import aget, adel
from orjson import loads
from datetime import datetime
from manager import QuizManager
from re import findall

intents = Intents.default()
intents.message_content = True
intents.guild_messages = True

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

    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return
        bet_opened = await aget("event:bet:opened")
        if bet_opened is not None:
            result = findall(r"-?\d+\.?\d*", message.content)
            if len(result) > 0:
                await message.reply(content=f"Você apostou {result[0]} coins.")


bot = Bot()

@bot.tree.command(
    name="betting",
    description="Criar um evento de aposta"
)
@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
async def betting(interaction: Interaction, nome: str, capa: Attachment, a: str, b: str):
    if not has_bot_manager_permissions(interaction.user.roles):
        raise Exception("Você não tem permissão para criar um evento.")
    valid_content_types = ["image/gif", "image/jpeg"]
    if capa.content_type not in valid_content_types:
        raise Exception("Formato inválido! Válidos: %s" % ", ".join([f for f in valid_content_types]))
    await interaction.response.defer(ephemeral=False)
    embed, view, file, event_id = await BettingEventCommand(interaction, nome, capa, a, b)
    await interaction.edit_original_response(embed=embed, view=view, attachments=[file])

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

@bot.tree.command(
    name="level",
    description="Informações sobre xp e níveis"
)
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def level(interaction: Interaction):
    description = """:egg: (Egg) **1º Nível** - 0xp até 50xp
:crossed_swords: (Warrior) **2º Nível** - 51xp até 500xp
:gem: (Nobility) **3º Nível** - 501xp até 1000xp
:crown: (King) **4º Nível** - 1001xp+

:warning: Os pontos de experiência (XP) têm uma validade de **15 dias**. Certifique-se de **permanecer ativo** para evitar a **perda de níveis**.

Exiba o ranking do canal executando o comando /ranking."""

    embed = Embed(
        title="Níveis e pontos de experiência".upper(),
        description=description
    )
    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(
    name="ranking",
    description="Exiba o ranking do canal"
)
@app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.guild_id, i.user.id))
async def ranking(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = await RankingCommand(interaction)
    await interaction.edit_original_response(embed=embed)

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
@level.error
@ranking.error
@betting.error
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

