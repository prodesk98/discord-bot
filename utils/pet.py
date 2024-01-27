from discord import Embed, File

from database import AsyncDatabaseSession, Pet
from sqlalchemy import select, func

from .math import normalize_value
from config import Pet as PetModel, pets, env

async def has_pet(user_id: int) -> bool:
    async with AsyncDatabaseSession as session:
        count = normalize_value(
            (await session.execute(
                select(func.count(Pet.id).label("count"))
                .where(Pet.user_id == user_id) # type: ignore
            )).scalar_one_or_none()
        )
        return count > 0

async def register_pet(pet: Pet) -> None:
    async with AsyncDatabaseSession as session:
        session.add(pet)
        await session.commit()

async def get_pet(user_id: int) -> PetModel|None:
    async with AsyncDatabaseSession as session:
        pet: Pet|None = (await session.execute(
            select(Pet).where(Pet.user_id == user_id) # type: ignore
        )).scalar_one_or_none()
        pet_model: PetModel = next(iter([p for p in pets if p.id == pet.config_pet_id]))
        copy = pet_model.model_dump().copy()
        copy.update({"level": pet.level, "id": pet.id})
        return PetModel(**copy)

async def pet_level_up(pet: Pet) -> PetModel:
    async with AsyncDatabaseSession as session:
        pet: Pet = (await session.execute(
            select(Pet).where(Pet.id == pet.id)  # type: ignore
        )).scalar_one_or_none()
        pet.level += 1
        await session.commit()

        pet_model: PetModel = next(iter([p for p in pets if p.id == pet.config_pet_id]))
        copy = pet_model.model_dump().copy()
        copy.update({"level": pet.level, "id": pet.id})
        return PetModel(**copy)

def calc_pet_rarity(proba: float) -> str:
    if proba <= 0.02:
        return "ultra raro"
    elif proba <= 0.05:
        return "raro"
    return "normal"

def calc_pet_level(level: int) -> int:
    return normalize_value(env.PET_LEVEL_XP_BASE + (level - 1) * env.PET_LEVEL_XP_INCREASE_PEER_LEVEL)


def pet_card(pet: PetModel) -> tuple[Embed, File]:
    pet_rarity = calc_pet_rarity(pet.proba)
    pet_rarity_format = pet_rarity if pet_rarity == "normal" else f"**{pet_rarity}**"
    pet_level_format = pet.level if pet.level < 10 else f"**{pet.level}**"
    thumbnail = File(f"assets/gifs/pets/{pet.thumbnail}", filename=pet.thumbnail)
    embed = Embed(
        title=f"{pet.name}!",
        description=f"{pet.description}\n\n"
                    f"Raridade: {pet_rarity_format.title()}\n"
                    f"Nível: {pet_level_format}/{env.PET_LEVEL_LIMIT} %s" % (
                        f"\nNext Level({pet.level + 1}) :coin: {calc_pet_level(pet.level)} coins" if pet.level < env.PET_LEVEL_LIMIT else f"(Max)")
    )
    embed.set_thumbnail(url=f"attachment://{pet.thumbnail}")
    return embed, thumbnail
