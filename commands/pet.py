from discord import Interaction, Embed, File

from database import User, Pet
from utils import (
    has_pet, register_pet, calc_pet_rarity,
    get_user_by_discord_user_id, get_pet,
    pet_card
)
from config import pets, Pet as PetModel, env
from random import uniform, randint

from views import PetButtons


async def capture_pet(user: User) -> PetModel:
    probabilities_sum = sum([pet.proba for pet in pets])
    sort_proba = uniform(0, probabilities_sum)
    accumulated = 0.0
    for pet in pets:
        accumulated += pet.proba
        if sort_proba <= accumulated:
            level_pet = randint(0, env.PET_LEVEL_LIMIT)
            await register_pet(
                Pet(
                    user_id=user.id,
                    config_pet_id=pet.id,
                    name=pet.name,
                    personality=pet.personality,
                    swear_words=pet.swear_words,
                    informal_greeting=pet.informal_greeting,
                    level=level_pet
                )
            )
            pet.level = level_pet
            return pet

async def PetCommand(interaction: Interaction) -> None:
    user = await get_user_by_discord_user_id(interaction.user.id)
    if user is None:
        raise Exception("Você precisa ter uma conta para executar esse comando.\n\nExecute /me")

    has_me_pet = await has_pet(user.id)
    if not has_me_pet:
        my_pet = await capture_pet(user)
        pet_rarity = calc_pet_rarity(my_pet.proba)
        pet_embed, pet_thumbnail = pet_card(my_pet)
        await interaction.edit_original_response(
            embed=pet_embed,
            attachments=[pet_thumbnail],
            view=None if my_pet.level >= env.PET_LEVEL_LIMIT else PetButtons(my_pet.id)
        )
        if pet_rarity != "normal":
            rarity_pet_thumbnail = File(fp=f"assets/gifs/pets/{my_pet.thumbnail}", filename=my_pet.thumbnail)
            pet_rarity_embed = Embed(
                title=my_pet.name,
                description=f"<@{user.discord_user_id}> Ganhou um pet **{pet_rarity.title()}**"
            )
            pet_rarity_embed.set_thumbnail(url=f"attachment://{my_pet.thumbnail}")
            await interaction.channel.send(
                embed=pet_rarity_embed,
                files=[rarity_pet_thumbnail],
                silent=True
            )
        return

    my_pet = await get_pet(user.id)
    pet_embed, pet_thumbnail = pet_card(my_pet)
    await interaction.edit_original_response(
        embed=pet_embed,
        attachments=[pet_thumbnail],
        view=None if my_pet.level >= env.PET_LEVEL_LIMIT else PetButtons(my_pet.id)
    )