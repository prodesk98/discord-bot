from discord import Interaction, Embed, File
from aiohttp import ClientSession

from databases import async_session, User
from sqlalchemy import select

from typing import Union

from config import env

async def InstructCommand(
    interaction: Interaction,
    text: str
) -> tuple[Embed, File]:
    file = File("assets/gifs/knowledge.gif", filename="knowledge.gif")

    async with async_session as session:
        user: Union[User, None] = (await session.execute(select(User).where(User.discord_user_id == str(interaction.user.id)))).scalars().one_or_none()
        if user is None:
            await interaction.edit_original_response(embed=Embed(
                title="Acesso bloqueado!",
                description="Você precisa ter uma conta para executar esse comando.\n\nExecute /me",
                color=0xE02B2B
            ))
            return None, None

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