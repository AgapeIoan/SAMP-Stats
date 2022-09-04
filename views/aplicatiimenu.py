import disnake

from functii.discord import disable_all_buttons, enable_buttons
from functii.debug import print_debug

class AplicatiiMenu(disnake.ui.View):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup):
        super().__init__(timeout=600.0)
        self.soup = soup

    async def interaction_check(self, interaction):
        if interaction.author.id == self.original_author.id:
            return True
        await interaction.response.send_message("**❗ Nu poti folosi comanda deoarece nu esti autorul acesteia!**", ephemeral=True)
        return False

    async def on_timeout(self):
        await self.message.edit("[DEBUG] TIMEOUT GO BRRRRR")

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Aplicatii noi", custom_id="aplicatii_1", row=0)
    async def aplicatii_noi(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        await interaction.response.edit_message(content="**noi**", view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Aplicatii acceptate", custom_id="aplicatii_2", row=0)
    async def aplicatii_acceptate(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        await interaction.response.edit_message(content="**acceptate**", view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Aplicanti invitati", custom_id="aplicatii_3", row=0)
    async def aplicatii_invitate(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        await interaction.response.edit_message(content="**invitati**", view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.red, label="Aplicatii respinse", custom_id="aplicatii_4", row=0)
    async def aplicatii_respinse(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        await interaction.response.edit_message(content="**respinse**", view=self)