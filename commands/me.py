from discord import Interaction, Embed, File
from sqlalchemy import select, func
from sqlalchemy.sql import desc

from database import AsyncDatabaseSession, CoinsHistory, User, Scores

from datetime import datetime
from config import env
from utils import (
    PlayAudioEffect, scoreToLevel, LevelSticker,
    LevelNumber, normalize_value, registerCoinHistory
)


async def MeCommand(
    interaction: Interaction
) -> None:
    balance = 0.0
    score = 0.0
    score_received = 0.0
    rescue_message = ""

    async with AsyncDatabaseSession as session:
        user = await session.execute(select(User).where(
            User.discord_user_id == str(interaction.user.id) #type: ignore
        ))
        user = user.scalar()
        is_member = user is not None
        if not is_member:
            if interaction.guild_id is None:
                raise Exception("I only work within channels.")

            user = User(
                discord_user_id=str(interaction.user.id),
                discord_guild_id=str(interaction.guild_id),
                discord_username=interaction.user.name,
                discord_nick=interaction.user.global_name,
            )

            session.add(user)
            await session.commit()
        else:
            balance = normalize_value((await session.execute(select(func.sum(CoinsHistory.amount)).where(CoinsHistory.user_id == user.id))).scalar())

            score = normalize_value((await session.execute(select(func.sum(Scores.amount)).where(Scores.user_id == user.id))).scalar())

            last_coin_history: datetime = (
                await session.execute(
                    select(CoinsHistory.created_at)
                        .where(CoinsHistory.user_id == user.id)
                        .where(CoinsHistory.description == "recovery") #type: ignore
                        .order_by(
                            desc(CoinsHistory.created_at) #type: ignore
                        )
                    )
                ).scalar()

            coin_history_timestamp = last_coin_history.timestamp()
            rescues_in_hours = (datetime.now().timestamp() - coin_history_timestamp) / 3600
            hourly_earnings = env.HOURLY_EARNINGS
            hourly_score = 20

            if rescues_in_hours >= 1:
                rescues_in_hours = 24 if rescues_in_hours > 24 else rescues_in_hours
                score_received += hourly_score
                total_rescue = round(float(f"{(hourly_earnings * rescues_in_hours):.2f}"))
                rescue_message = f"Você resgatou **{total_rescue} coins** +{hourly_score}xp:zap:\nReceba +{hourly_earnings} coins por hora (acumula até 24 horas).\n\n**+{hourly_score}xp** por resgate a cada 1 hora (acumula até 1 hora)."
                session.add(
                    CoinsHistory(
                        user_id=user.id,
                        amount=total_rescue,
                        description="recovery"
                    )
                )
                session.add(
                    Scores(
                        user_id=user.id,
                        amount=score_received
                    )
                )
                balance += total_rescue
                score += score_received

            if user.discord_guild_id is None:
                user.discord_guild_id = str(interaction.guild_id)
            await session.commit()

    lvl = scoreToLevel(score)
    file = File(f"assets/gifs/levels/{lvl}.gif", filename=f"{lvl}.gif")

    if not is_member:
        coins_welcome = 100
        await registerCoinHistory(user.id, amount=coins_welcome, description="recovery")

        embed = Embed(
            title=f"Bem-vindo!",
            description=f"Olá, {user.discord_nick}!\nVocê ganhou **{coins_welcome}** coins.",
            color=0xF5D920
        )
        embed.set_thumbnail(url=f"attachment://{lvl}.gif")

        await PlayAudioEffect(interaction, "coins.wav")
        await interaction.edit_original_response(embed=embed, attachments=[file])
        return

    embed = Embed(
        title=f"{LevelSticker(lvl)} {LevelNumber(lvl)}º Nível",
        description=f"{rescue_message}\n\n** :zap:{score:.2f}** xp\n**:coin: {balance:.2f}** coins",
        color=0xF5D920
    )
    embed.set_thumbnail(url=f"attachment://{lvl}.gif")
    await interaction.edit_original_response(embed=embed, attachments=[file])
