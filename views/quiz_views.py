from discord import ui, ButtonStyle, Interaction, Embed
from loguru import logger

from cache import aget, aset
from models import get_alternative_by_name, ALTERNATIVES, QuizEnumChoices
from utils import (
    has_account, has_quiz_bet, bet_quiz,
    get_user_by_discord_user_id, hasCoinsAvailable, registerCoinHistory
)


class QuizChoicesButtons(ui.View):
    def __init__(self, quiz_id: int, guild_id: str, amount: int):
        super().__init__(timeout=None)
        self.quiz_id = quiz_id
        self.guild_id = guild_id
        self.amount = amount

    @ui.button(label="A", style=ButtonStyle.primary, custom_id="A")
    async def A(self, interaction: Interaction, button: ui.Button):
        await self.bet(interaction, button)

    @ui.button(label="B", style=ButtonStyle.primary, custom_id="B")
    async def B(self, interaction: Interaction, button: ui.Button):
        await self.bet(interaction, button)

    @ui.button(label="C", style=ButtonStyle.primary, custom_id="C")
    async def C(self, interaction: Interaction, button: ui.Button):
        await self.bet(interaction, button)

    @ui.button(label="D", style=ButtonStyle.primary, custom_id="D")
    async def D(self, interaction: Interaction, button: ui.Button):
        await self.bet(interaction, button)

    async def bet(self, interaction: Interaction, button: ui.Button):
        if not (await has_account(interaction.user.id)):
            await interaction.response.send_message( # type: ignore
                embed=Embed(
                    title="Acesso bloqueado!",
                    description="Você precisa ter uma conta para executar esse comando.\n\nExecute /me",
                    color=0xE02B2B
                )
            )
            return

        user = await get_user_by_discord_user_id(interaction.user.id)

        logger.info(f"[QUIZ BUTTON EVENT] {user.discord_nick} chose {button.custom_id}")
        has_quiz_opened = await aget(f"quiz:opened:{interaction.guild_id}")
        if has_quiz_opened is None:
            await interaction.response.send_message( # type: ignore
                embed=Embed(
                    title="Quiz fechado!",
                    description="Você não pode participar de um quiz que já foi finalizado.",
                    color=0xE02B2B
                ),
                ephemeral=True
            )
            return

        if await has_quiz_bet(user.id, self.quiz_id):
            user_choice = await aget(f"quiz:{self.quiz_id}:betting:{user.id}")
            await interaction.response.send_message( # type: ignore
                embed=Embed(
                    title="Já houve uma escolha!",
                    description="Você já escolheu uma alternativa. %s" % (
                        f"Sua escolha foi alternativa **{ALTERNATIVES.get(int(user_choice.decode()))}**."
                        if user_choice is not None else ""
                    ),
                    color=0xE02B2B
                ),
                ephemeral=True
            )
            return

        if not (await hasCoinsAvailable(user.id, self.amount)):
            await interaction.response.send_message(  # type: ignore
                embed=Embed(
                    title="Para aí!",
                    description="Você não têm money para pagar o bilhete.",
                    color=0xE02B2B
                ),
                ephemeral=True
            )
            return

        choice = get_alternative_by_name(button.custom_id)
        await bet_quiz(
            user_id=user.id,
            quiz_id=self.quiz_id,
            guild_id=self.guild_id,
            choice=QuizEnumChoices(choice),
            amount=self.amount
        )
        await aset(f"quiz:{self.quiz_id}:betting:{user.id}", str(choice).encode(), ex=35)
        await registerCoinHistory(user.id, self.amount * -1)
        await interaction.response.send_message(f"Você escolheu a alternativa **{ALTERNATIVES.get(choice, None)}**.", ephemeral=True) # type: ignore

