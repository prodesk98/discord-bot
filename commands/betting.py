from discord import Interaction, Embed, Attachment, File, ui, ButtonStyle
from discord.ui import View

from utils import PlayAudioEffect
from cache import aset

STATUS = {
    1: "Aberto",
    2: "Fechado"
}

LABEL = {
    "A": 1,
    "B": 2
}

class ViewBetButtons(ui.View):
    def __init__(self, event_id: int, a: str, b: str):
        super().__init__(timeout=None)
        self.event_id = event_id
        self.a = a.capitalize()
        self.b = b.capitalize()
        self.add_buttons()

    def add_buttons(self):
        button_a = ui.Button(label=f"1º {self.a}", style=ButtonStyle.secondary)
        button_b = ui.Button(label=f"2º {self.b}", style=ButtonStyle.secondary)

        button_a.callback = self.betA
        button_b.callback = self.betB
        self.add_item(button_a)
        self.add_item(button_b)

    async def betA(self, interaction: Interaction):
        await aset(f"event:bet:{self.event_id}:{interaction.user.id}", b"a:0", ex=60)
        await interaction.response.send_message(f"Quantos coins você deseja apostar no **{self.a}**?", ephemeral=True) #type: ignore

    async def betB(self, interaction: Interaction):
        await aset(f"event:bet:{self.event_id}:{interaction.user.id}", b"b:0", ex=60)
        await interaction.response.send_message(f"Quantos coins você deseja apostar no **{self.b}**?", ephemeral=True)  # type: ignore


async def BettingEventCommand(interaction: Interaction, name: str, banner: Attachment, a: str, b: str) -> None:
    description = f"""
**1º** {a.capitalize()} *#odd*(**x2.5**)
**2º** {b.capitalize()} *#odd*(**x3.5**)"""

    clock = File(f"assets/gifs/clock.gif", filename=f"clock.gif")
    embed = Embed(title=f"[#123] {name.upper()}", description=description, color=0xD30B0B)
    embed.set_image(url=banner.url)
    embed.set_footer(text=f"Status do Evento: {STATUS.get(1)}", icon_url="attachment://clock.gif")
    await PlayAudioEffect(interaction, "boxing_bell.wav")
    await aset(f"event:bet:opened", f"{123}".encode(), ex=60)
    await interaction.edit_original_response(
        embed=embed,
        view=ViewBetButtons(123, a, b),
        attachments=[clock]
    )
