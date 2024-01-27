from hashlib import md5

from discord import Interaction, Embed, File
from aiohttp import ClientSession

from config import env
from utils import has_bot_manager_permissions, hasLevelPermissions, get_score_by_user_id, \
    get_user_by_discord_user_id, get_pet


async def InstructCommand(
    interaction: Interaction,
    text: str
) -> None:
    user = await get_user_by_discord_user_id(interaction.user.id)

    if user is None:
        raise Exception("Você precisa ter uma conta para executar esse comando.\n\nExecute /me")

    score = await  get_score_by_user_id(user.id)
    has_manager = has_bot_manager_permissions(interaction.user.roles)
    if not has_manager and not hasLevelPermissions(score, 2):
        raise Exception("Você não tem permissão para executar este comando. Apenas líderes ou usuários de nível 3 têm permissão.\n\nExecute /levels para obter mais informações...")

    pet = await get_pet(user.id)

    if pet is None:
        raise Exception("Você precisa ter um pet para executar esse comando.\n\n"
                        "Por favor, execute /pet\n\n"
                        "Ou /pets para mais informações...")

    async with ClientSession() as session:
        async with session.post(f"{env.LEARN_BOT_ENDPOINT}/upsert", headers={
            "Authorization": f"Bearer {env.LEARN_BOT_AUTHORIZATION}"
        }, json={
          "content": text,
          "username": user.discord_nick,
          "namespace": md5(f"{user.id}_{pet.id}".encode()).hexdigest() if not has_manager else "default"
        }) as response:
            if response.ok:
                embed = Embed(
                    title=pet.name if not has_manager else "Estou aprendendo...",
                    description=f"{pet.name if not has_manager else 'Agora o robô'} está em processo de aprendizagem a partir dessas informações...\n\n✅ Nenhuma ação adicional será necessária.\n⏰ Disponível em alguns minutos.\n",
                    color=0xDBF5Fe
                )
                thumbnail = File(f"assets/gifs/{'pets/%s' % pet.thumbnail if not has_manager else 'settings/knowledge.gif'}", filename=f"{pet.thumbnail if not has_manager else 'knowledge.gif'}")
                embed.set_thumbnail(url=f"attachment://{pet.thumbnail if not has_manager else 'knowledge.gif'}")
                await interaction.edit_original_response(embed=embed, attachments=[thumbnail])
            else:
                raise Exception(f"Houve um erro com o treinamento. Por favor, verifique a API de aprendizagem: {env.LEARN_BOT_ENDPOINT}")
