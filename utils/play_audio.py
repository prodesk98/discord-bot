import asyncio

from discord import Interaction, FFmpegOpusAudio, VoiceState, VoiceClient, AudioSource, utils
from pathlib import Path

from .permissions import has_bot_manager_permissions


async def PlayAudioEffect(interaction: Interaction, audio: str) -> None:
    if interaction.user.voice is None:
        return

    voice: VoiceState|VoiceClient = utils.get(
        interaction.client.voice_clients,
        guild=interaction.user.guild
    )
    if voice is None:
        await interaction.user.voice.channel.connect()
        return
    else:
        if voice.channel.id != interaction.user.voice.channel.id and (
            interaction.user.guild_permissions.manage_channels or
            interaction.user.guild_permissions.manage_guild or
            interaction.user.guild_permissions.administrator or
            has_bot_manager_permissions(interaction.user.roles)
        ):
            await voice.move_to(interaction.user.voice.channel)
            await asyncio.sleep(3)

    source = FFmpegOpusAudio(
        executable="ffmpeg",
        source=f"{Path(__file__).absolute().parent.parent}/assets/audio_effects/{audio}",
        **{'options': '-vn'}
    )

    if source.is_opus():
        if voice.is_playing():
            voice.stop()
        voice.play(source)
