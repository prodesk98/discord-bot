from discord.ext import commands, tasks
from discord.ext.commands import Context
from discord import (
    Intents, Embed, Interaction,
    app_commands, File, Attachment, Message
)

from config import env, pets
from loguru import logger

from commands import (
    MeCommand,
    InstructCommand,
    AskingCommand,
    QuizCommand,
    RankingCommand,
    BettingEventCommand,
    PetCommand
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
            if len(message.content) < 55 and (await aget(f"event:bet:{bet_opened.decode()}:{message.author.id}")) is not None:
                if message.content == "cancel":
                    await adel(f"event:bet:{bet_opened.decode()}:{message.author.id}")
                    return

                result = findall(r"-?\d+\.?\d*", message.content)
                if len(result) > 0:
                    bet = round(sum([float(r) for r in result]))
                    await message.reply(content=f"Você apostou {bet} coins.")
                    await adel(f"event:bet:{bet_opened.decode()}:{message.author.id}")
                else:
                    await message.reply(content="Não compreendi o montante que você planeja apostar. Caso deseje cancelar sua aposta, envie \"cancel\".")


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
    await BettingEventCommand(interaction, nome, capa, a, b)

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

    await interaction.response.defer(ephemeral=False)
    await QuizCommand(interaction, tema, premio)

@bot.tree.command(
    name="levels",
    description="Informações sobre xp e níveis"
)
@app_commands.checks.cooldown(1, 300.0, key=lambda i: (i.guild_id, i.user.id))
async def level(interaction: Interaction):
    description = """:egg: (Egg) **1º Nível** - 0xp até 50xp
:crossed_swords: (Warrior) **2º Nível** - 51xp até 500xp
:gem: (Nobility) **3º Nível** - 501xp até 1000xp
:crown: (King) **4º Nível** - 1001xp+

:warning: Os pontos de experiência (XP) têm uma validade de **15 dias**. Certifique-se de **permanecer ativo** para evitar a **perda de níveis**.

Exiba o ranking do canal executando o comando /ranking."""

    await interaction.response.send_message(
        embed=Embed(
            title="Níveis e pontos de experiência".upper(),
            description=description
        ),
        ephemeral=True
    )

@bot.tree.command(
    name="pet",
    description="Meu pet"
)
@app_commands.checks.cooldown(1, 1.0, key=lambda i: (i.guild_id, i.user.id))
async def pet(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    await PetCommand(interaction)

@bot.tree.command(
    name="pets",
    description="Informações sobre pets"
)
@app_commands.checks.cooldown(1, 300.0, key=lambda i: (i.guild_id, i.user.id))
async def pets_informations(interaction: Interaction):
    informations = """**{name}**
{description}
**Probabilidade**: {proba}%"""

    await interaction.response.defer(ephemeral=True)
    embeds = []
    files = []
    for i, pet in enumerate(pets):
        embeds.append(
            Embed(
            description=informations.format(
                    name=pet.name,
                    description=pet.description,
                    proba=pet.proba * 100,
                )
            )
        )
        embeds[i].set_thumbnail(url=f"attachment://{pet.thumbnail}")
        files.append(File(fp=f"assets/gifs/pets/{pet.thumbnail}", filename=pet.thumbnail))
    await interaction.edit_original_response(embeds=embeds, attachments=files)


@bot.tree.command(
    name="ranking",
    description="Exiba o ranking do canal"
)
@app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.guild_id, i.user.id))
async def ranking(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    await RankingCommand(interaction)

@bot.tree.command(
    name="asking",
    description="Perguntar ao robô"
)
@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
async def asking(interaction: Interaction, pergunta: str):
    if env.LEARN_BOT_ENDPOINT is None or env.LEARN_BOT_AUTHORIZATION is None:
        raise Exception("API não foi configurado corretamente.")
    if not env.LEARN_BOT_ENABLED:
        raise Exception("API desativada")

    await interaction.response.defer(ephemeral=False)
    await AskingCommand(interaction, pergunta)


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

    await interaction.response.defer(ephemeral=True)
    await InstructCommand(interaction, texto)


@bot.tree.command(
    name="ping",
    description="Latência do servidor"
)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
async def ping(interaction: Interaction):
    if not has_bot_manager_permissions(interaction.user.roles):
        raise Exception("Você não tem permissão para executar esse comando.")

    await interaction.response.defer(ephemeral=True)
    await interaction.edit_original_response(
        embed=Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(interaction.client.latency * 1000)}ms.",
            color=0x3836B5
        )
    )


@bot.tree.command(
    name="me",
    description="Minha conta"
)
@app_commands.checks.cooldown(2, 15, key=lambda i: (i.guild_id, i.user.id))
async def me(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    await MeCommand(interaction)

@ping.error
@level.error
@pets_informations.error
@pet.error
@ranking.error
@betting.error
@instruct.error
@asking.error
@quiz.error
@me.error
async def on_error(interaction: Interaction, error: Exception) -> None:
    if isinstance(error, app_commands.CommandOnCooldown):
        embed = Embed(
            title="⌛ Cooldown!",
            description=f"You are executing the same command in a short amount of time.\n{error}",
            color=0xE02B2B
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    logger.error(error)
    await interaction.edit_original_response(
        embed=Embed(
            title="❌ Error!",
            description=f"{error}",
            color=0xE02B2B
        )
    )


if __name__ == "__main__":
    bot.run(env.TOKEN)

