from discord import Embed, Interaction, File
from aiohttp import ClientSession

from utils import (
    registerCoinHistory, hasCoinsAvailable, hasLevelPermissions,
    has_account, get_user_by_discord_user_id, get_score_by_user_id,
    get_pet, calc_pet_rarity
)

from orjson import loads
from config import env
from hashlib import md5


async def AskingCommand(
    interaction: Interaction,
    question: str
) -> None:
    if not (await has_account(interaction.user.id)):
        raise Exception("Você precisa ter uma conta para executar esse comando.\n\nExecute /me")

    user = await get_user_by_discord_user_id(interaction.user.id)
    pet = await get_pet(user.id)

    if pet is None:
        raise Exception("Você precisa ter um pet para executar esse comando."
                        "Por favor, execute /pet ou /pets para mais informações...")

    score = await  get_score_by_user_id(user.id)

    if not hasLevelPermissions(score, 2):
        raise Exception("Você precisa ter no mínimo 2 Níveis para executar esse comando.\n\nExecute /me - para ver o seu nível\nExecute /levels - para mais informações...")

    asking_cost = env.ASKING_COST
    if not (await hasCoinsAvailable(user.id, asking_cost)):
        raise Exception(f"Você precisa de {asking_cost} coins para executar esse comando.\n\nExecute /me")

    async with ClientSession() as session:
        async with session.post(f"{env.LEARN_BOT_ENDPOINT}/asking", headers={
            "Authorization": f"Bearer {env.LEARN_BOT_AUTHORIZATION}"
        }, json={
          "q": question,
          "username": user.discord_nick,
          "namespace": md5(f"{user.id}_{pet.id}".encode()).hexdigest(),
          "personality": pet.personality,
          "swear_words": pet.swear_words,
          "informal_greeting": pet.informal_greeting
        }) as response:
            if response.ok:
                data: dict = loads(await response.read())
                await registerCoinHistory(user.id, asking_cost * -1)

                asking_embed = Embed(
                    title=question.capitalize(),
                    description=f"%s\n\n**Responde: ** %s" % (
                        f"**{pet.name}**\n{calc_pet_rarity(pet.level).title()} ∘ Nível ({pet.level}) ",
                        data.get("response", "")
                    ),
                    color=0x147BBD
                )
                pet_thumbnail = File(f"assets/gifs/pets/{pet.thumbnail}", filename=pet.thumbnail)
                asking_embed.set_thumbnail(url=f"attachment://{pet.thumbnail}")

                await interaction.edit_original_response(
                    embed=asking_embed,
                    attachments=[pet_thumbnail]
                )
            else:
                raise Exception(f"Houve um erro com a resposta. Por favor, "
                                f"verifique a API de respostas: {env.LEARN_BOT_ENDPOINT}")