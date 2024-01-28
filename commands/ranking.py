from discord import Interaction, Embed, File
from loguru import logger

from database import Scores, User, AsyncDatabaseSession
from sqlalchemy import select, func, desc, asc

from utils import scoreToSticker, get_guild_by_user_id


async def RankingCommand(interaction: Interaction) -> None:
    usernames = []
    scores = []
    guild_top_one = None
    async with AsyncDatabaseSession as session:
        ranking = (await session.execute(
            select(
                User.id,
                User.discord_user_id,
                func.sum(Scores.amount).label('rank')
            )
            .join(User)
            .where(User.id == Scores.user_id) # type: ignore
            .group_by(User.id, User.discord_user_id)
            .order_by(desc("rank"), asc("id"))
            .limit(10)
        )).fetchall()
        for i, rank in enumerate(ranking):
            user_id, discord_user_id, score = rank
            if i == 0:
                guild_top_one = await get_guild_by_user_id(user_id)

            usernames.append(f"{scoreToSticker(score)} <@{discord_user_id}>")
            scores.append(f"{score}xp")
    embed = Embed(
        title="TOP 10 RANKING",
        description=""
    )

    guild_emoji = None
    if guild_top_one is not None:
        guild_emoji = File(fp=f"assets/gifs/guilds/guild_{guild_top_one.emoji}.gif", filename=f"guild_{guild_top_one.emoji}.gif")
        embed.set_image(url=f"attachment://guild_{guild_top_one.emoji}.gif")

    embed.add_field(name="Usuários", value="\n".join(usernames), inline=True)
    embed.add_field(name="Experiências", value="\n".join(scores), inline=True)
    await interaction.edit_original_response(embed=embed, attachments=[guild_emoji] if guild_emoji is not None else [])
