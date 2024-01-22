import asyncio

from discord import Interaction, Embed, File
from sqlalchemy import select, func
from sqlalchemy.sql import text, desc

from databases import CoinsHistory, User
from databases import async_session

from datetime import datetime
from config import env
from utils import PlayAudioEffect


async def CoinsCommand(
    interaction: Interaction
) -> tuple[Embed, File]:
    file = File("assets/gifs/coin.gif", filename="coin.gif")
    balance = 0.0
    rescue_message = ""

    async with async_session as session:
        user = await session.execute(select(User).where(
            User.discord_user_id == str(interaction.user.id)
        ))
        user = user.scalars().one_or_none()
        is_member = user is not None
        if not is_member:
            user = User(
                discord_user_id=str(interaction.user.id),
                discord_username=interaction.user.name,
                discord_nick=interaction.user.global_name,
            )

            session.add(user)
            await session.commit()
        else:
            balance = (await session.execute(
                select(func.sum(CoinsHistory.amount)).where(
                    CoinsHistory.user_id == user.id
                )
            )).scalar()

            lastCoinHistory: datetime = (await session.execute(
                select(CoinsHistory.created_at).where(CoinsHistory.user_id == user.id).order_by(
                    desc(CoinsHistory.created_at)
                )
            )).scalar()
            coin_history_timestamp = lastCoinHistory.timestamp()
            rescues_in_hours = (datetime.now().timestamp() - coin_history_timestamp) / 3600
            hourly_earnings = env.HOURLY_EARNINGS
            if rescues_in_hours >= 1:
                rescues_in_hours = 24 if rescues_in_hours > 24 else rescues_in_hours
                total_rescue = float(f"{(hourly_earnings * rescues_in_hours):.2f}")
                rescue_message = f"Você resgatou **{total_rescue} coins**.\nReceba +{hourly_earnings} coins por hora."
                session.add(
                    CoinsHistory(
                        user_id=user.id,
                        amount=total_rescue
                    )
                )
                balance += total_rescue
                await session.commit()
                await PlayAudioEffect(interaction, "coins.wav")

    if not is_member:
        coins_welcome = 100
        async with async_session as session:
            session.add(
                CoinsHistory(
                    user_id=user.id,
                    amount=coins_welcome
                )
            )
            await session.commit()

        embed = Embed(
            title=f"Bem-vindo!",
            description=f"Olá, {user.discord_nick}!\nVocê ganhou **{coins_welcome}** coins.",
            color=0xF5D920
        )
        embed.set_thumbnail(url="attachment://coin.gif")

        await PlayAudioEffect(interaction, "coins.wav")
        return embed, file

    embed = Embed(
        title="Saldo",
        description=f"{rescue_message}\n\n**{balance:.2f}** coins",
        color=0xF5D920
    )
    embed.set_thumbnail(url="attachment://coin.gif")
    return embed, file
