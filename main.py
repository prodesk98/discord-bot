import os

from discord.ext import commands
from discord import Intents
from config import env
from loguru import logger

intents = Intents.default()

class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(env.PREFIX),
            intents=intents,
            help_command=None,
        )
        self.database = None

    async def load_cogs(self) -> None:
        for file in os.listdir(f"{os.path.relpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                ext = file[:-3]
                try:
                    await self.load_extension(f"cogs.{ext}")
                    logger.info(f"Loaded extension '{ext}'")
                except Exception as e:
                    logger.error(e)

    async def setup_hook(self) -> None:
        logger.info(f"Logged in as {self.user.name}")
        await self.tree.sync()
        await self.load_cogs()

bot = Bot()
bot.run(env.TOKEN)
