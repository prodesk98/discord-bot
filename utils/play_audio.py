import asyncio

from discord import Interaction, FFmpegOpusAudio, VoiceState, VoiceClient
from pathlib import Path
import discord


async def PlayAudioEffect(interaction: Interaction, audio: str) -> None:
    if interaction.user.voice is None:
        return

    voice: VoiceState|VoiceClient = discord.utils.get(
        interaction.client.voice_clients,
        guild=interaction.user.guild
    )
    if voice is None:
        await interaction.user.voice.channel.connect()
        return
    else:
        if voice.channel.id != interaction.user.voice.channel.id:
            await voice.move_to(interaction.user.voice.channel)
            await asyncio.sleep(3)

    source = FFmpegOpusAudio(
        executable="ffmpeg",
        source=f"{Path(__file__).absolute().parent.parent}/assets/audio_effects/{audio}",
        **{'options': '-vn'}
    )
    if source.is_opus():
        voice.play(source)

