from discord import Interaction, Embed, File
from aiohttp import ClientSession

from database import AsyncDatabaseSession, User
from sqlalchemy import select

from config import env
from utils import has_account


async def InstructCommand(
    interaction: Interaction,
    text: str
) -> None:
    if not (await has_account(interaction.user.id)):
        await interaction.edit_original_response(
            embed=Embed(
                title="Acesso bloqueado!",
                description="Você precisa ter uma conta para executar esse comando.\n\nExecute /me",
                color=0xE02B2B
            )
        )
        return

    async with AsyncDatabaseSession as session:
        user: User = (await session.execute(select(User).where(User.id == interaction.user.id))).scalar() # type: ignore

    async with ClientSession() as session:
        async with session.post(f"{env.LEARN_BOT_ENDPOINT}/upsert", headers={
            "Authorization": f"Bearer {env.LEARN_BOT_AUTHORIZATION}"
        }, json={
          "content": text,
          "username": user.discord_nick
        }) as response:
            if response.ok:
                embed = Embed(
                    title="Estou aprendendo...",
                    description="Agora o robô está em processo de aprendizagem a partir dessas informações...\n\n✅ Nenhuma ação adicional será necessária.\n⏰ Disponível em alguns minutos.\n",
                    color=0xDBF5Fe
                )
                file = File("assets/gifs/knowledge.gif", filename="knowledge.gif")
                embed.set_image(url="attachment://knowledge.gif")
                return embed, file

    await interaction.edit_original_response(
        embed=Embed(
            title="Error!",
            description=f"Houve um erro com o treinamento. Por favor, verifique a API de aprendizagem: {env.LEARN_BOT_ENDPOINT}",
            color=0xE02B2B
        )
    )
    return None, None