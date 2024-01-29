from discord import ui, ButtonStyle, Interaction, Embed
from discord.utils import MISSING

from config import env
from utils import get_user_by_discord_user_id, get_pet, calc_pet_level, hasCoinsAvailable, pet_card, pet_level_up, \
    registerCoinHistory


class PetButtons(ui.View):
    def __init__(self, pet_id: int) -> None:
        super().__init__()
        self.pet_id = pet_id

    @ui.button(label="Level up!", style=ButtonStyle.primary)
    async def level_up(self, interaction: Interaction, button: ui.Button):
        await self.level_upgrade(interaction)

    @staticmethod
    async def level_upgrade(interaction: Interaction):
        user = await get_user_by_discord_user_id(interaction.user.id, interaction.guild_id)
        pet = await get_pet(user.id)

        amount = calc_pet_level(pet.level)
        if not (await hasCoinsAvailable(user.id, amount)):
            await interaction.response.send_message(embed=Embed( # type: ignore
                title="Saldo insuficiente",
                description="Você não tem coins suficiente para executar um upgrade de nível.",
                color=0xE02B2B
            ))
            return

        if pet.level >= env.PET_LEVEL_LIMIT:
            await interaction.response.send_message(embed=Embed(  # type: ignore
                title="Nível máximo",
                description="Você não pode mais fazer upgrade de nível neste pet.",
                color=0xE02B2B
            ))
            return

        await pet_level_up(pet)

        pet_embed, pet_thumbnail = pet_card(await get_pet(user.id))
        await registerCoinHistory(user.id, amount * -1)
        await interaction.response.send_message( # type: ignore
            embed=pet_embed,
            files=[pet_thumbnail],
            view=MISSING if pet.level+1 >= env.PET_LEVEL_LIMIT else PetButtons(pet.id),
            ephemeral=True
        )