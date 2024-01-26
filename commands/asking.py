from discord import Embed, Interaction, File
from aiohttp import ClientSession

from utils import (
    registerCoinHistory, hasCoinsAvailable, hasLevelPermissions,
    has_account, get_user_by_discord_user_id, get_score_by_user_id
)
from orjson import loads

from config import env


async def AskingCommand(
    interaction: Interaction,
    question: str
) -> None:
    if not (await has_account(interaction.user.id)):
        raise Exception("Você precisa ter uma conta para executar esse comando.\n\nExecute /me")

    user = await get_user_by_discord_user_id(interaction.user.id)
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
          "namespace": "default"
        }) as response:
            if response.ok:
                data: dict = loads(await response.read())
                await registerCoinHistory(user.id, asking_cost * -1)

                asking_embed = Embed(
                    title=question.capitalize(),
                    description=f"%s\n\n**Resposta: ** %s" % (
                        ":wolf: **Anny** ∘ Nível (162) ",
                        data.get("response", "")
                    ),
                    color=0x147BBD
                )
                pet = File("assets/gifs/pets/pet_anny.gif", filename="pet_anny.gif")
                asking_embed.set_thumbnail(url="attachment://pet_anny.gif")

                await interaction.edit_original_response(
                    embed=asking_embed,
                    attachments=[pet]
                )
            else:
                raise Exception(f"Houve um erro com a resposta. Por favor, "
                                f"verifique a API de respostas: {env.LEARN_BOT_ENDPOINT}")