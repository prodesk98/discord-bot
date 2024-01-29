from discord import Interaction, Embed, File

from utils import (
    has_user_guild, get_user_by_discord_user_id, recruit_guild,
    guild_members_count, guild_scores_count, get_guild_by_user_id, get_ranking_members_guild, scoreToSticker
)


async def MyGuildCommand(
    interaction: Interaction
):
    user = await get_user_by_discord_user_id(interaction.user.id)
    if user is None:
        raise Exception("Você precisa ter uma conta para executar esse comando.\n\nExecute /me")

    user_has_guild = await has_user_guild(user.id)
    if not user_has_guild:
        recruit = await recruit_guild(user.id)
        recruit_embed = Embed(
            title=recruit.name,
            description=f"Você foi recrutado para a Guilda **{recruit.name}**.\n"
                        f"Contribua com **xp** para manter\nsua guilda no topo.\n\n"
                        f"Membros: {await guild_members_count(recruit.id)}\n"
                        f"Experiência Total: {await guild_scores_count(recruit.id)}xp"
        )
        guild_emoji = File(fp=f"assets/gifs/guilds/guild_{recruit.emoji}.gif", filename=f"guild_{recruit.emoji}.gif")
        recruit_embed.set_image(url=f"attachment://guild_{recruit.emoji}.gif")
        await interaction.edit_original_response(
            embed=recruit_embed,
            attachments=[guild_emoji]
        )
        return

    guild = await get_guild_by_user_id(user.id)
    usernames = []
    scores = []

    for rank in (await get_ranking_members_guild(user.guild_id)):
        usernames.append(f"{scoreToSticker(rank.score)} <@{rank.discord_user_id}>")
        scores.append(f"{rank.score}xp")

    guild_embed = Embed(
        title=f"Guilda {guild.name}",
        description=f"Membros: {await guild_members_count(guild.id)}\n"
                    f"Experiência Total: {await guild_scores_count(guild.id)}xp\n\n"
                    f"TOP 10 MEMBROS DA GUILDA"
    )
    guild_emoji = File(fp=f"assets/gifs/guilds/guild_{guild.emoji}.gif", filename=f"guild_{guild.emoji}.gif")
    guild_embed.set_image(url=f"attachment://guild_{guild.emoji}.gif")
    guild_embed.add_field(name="Usuários", value="\n".join(usernames), inline=True)
    guild_embed.add_field(name="Experiências", value="\n".join(scores), inline=True)

    await interaction.edit_original_response(
        embed=guild_embed,
        attachments=[guild_emoji]
    )