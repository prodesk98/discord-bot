from discord.ext import commands
from discord import (
    Intents, Embed, Interaction,
    app_commands
)
from discord.ext.commands import Context

from config import env
from loguru import logger

from commands import (
    CoinsCommand
)

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
    name="ping",
    description="Server latency"
)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
@commands.has_guild_permissions()
async def ping(interaction: Interaction):
    embed = Embed(
        title="🏓 Pong!",
        description=f"The bot latency is {round(interaction.client.latency * 1000)}ms.",
        color=0x3836B5
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(
    name="coins",
    description="Show account balance"
)
@app_commands.checks.cooldown(2, 15, key=lambda i: (i.guild_id, i.user.id))
async def coins(interaction: Interaction):
    await interaction.response.send_message("buscando saldo...", ephemeral=True)
    embed, file = await CoinsCommand(interaction)
    await interaction.edit_original_response(embed=embed, attachments=[file])

@ping.error
@coins.error
async def on_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        embed = Embed(
            title="⌛ Cooldown!",
            description=f"You are executing the same command in a short amount of time.\n{error}",
            color=0xE02B2B
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    return Embed(
        title="Error!",
        description=f"{error}",
        color=0xE02B2B
    )


bot.run(env.TOKEN)

