from discord import Interaction, Embed, File
from database import Scores, User, AsyncDatabaseSession
from sqlalchemy import select, func, desc

from utils import scoreToSticker


async def RankingCommand(interaction: Interaction) -> None:
    usernames = []
    scores = []
    async with AsyncDatabaseSession as session:
        ranking = (await session.execute(
            select(
                User.discord_user_id,
                func.sum(Scores.amount).label('rank')
            )
            .join(Scores)
            .group_by(User.discord_user_id)
            .order_by(desc("rank"))
            .limit(10)
        )).fetchall()
        for rank in ranking:
            discord_user_id, score = rank
            usernames.append(f"{scoreToSticker(score)} <@{discord_user_id}>")
            scores.append(f"{score}xp")
    embed = Embed(
        title="TOP 10 RANKING",
        description=""
    )
    image = File(fp="assets/gifs/fire.gif", filename="fire.gif")
    embed.set_image(url="attachment://fire.gif")
    embed.add_field(name="Usuário", value="\n".join(usernames), inline=True)
    embed.add_field(name="Experiência", value="\n".join(scores), inline=True)
    await interaction.edit_original_response(embed=embed, attachments=[image])
