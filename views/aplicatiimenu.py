import disnake
import panou.ruby
import asyncio

from functii.discord import disable_all_buttons, enable_buttons, disable_not_working_buttons_aplicants
from functii.debug import print_debug
from panou.ruby.misc import get_aplicants


class AplicatiiList(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup: str, numar_pagina: int, aplicants=None, original_author=None, message=None, title_placeholder=""):
        self.original_author = original_author
        self.message = message
        self.soup = soup
        self.aplicants = aplicants
        self.numar_pagina = numar_pagina
        self.title_placeholder = title_placeholder

        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        for i in self.aplicants[(self.numar_pagina - 1) * 23:(self.numar_pagina * 23)]:
            aux = i.copy()
            
            skip = False
            for j in self.aplicants[self.aplicants.index(i)+1:(self.numar_pagina * 23)]:
                if aux[1] == j[1]:
                    skip = True
                    break
            if not skip:
                options.append(disnake.SelectOption(label=aux[1], description=f"ID: {aux[0]} | Data: {aux[2]}")) # TODO Emojis
            print_debug(f"Adaugat {aux[1]} la optiuni")

        if self.aplicants[(self.numar_pagina * 23):]:
            print_debug("Adaugat optiunea Inainte")
            options.append(
                disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de aplicanti", emoji="➡️"))

        super().__init__(placeholder=title_placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        aplicant_name = self.values[0]

        if aplicant_name == "Inapoi":
            if self.numar_pagina == 1:
                za_view = await disable_not_working_buttons_aplicants(AplicatiiMenu(self.soup), self.soup)

                za_view.original_author = self.original_author
                za_view.message = self.message
                await interaction.response.edit_message(
                    content=f"**Selecteaza o optiune:**", embed=None,
                    view=za_view)
            else:
                await interaction.response.edit_message(
                    view=AplicatiiListView(self.soup, self.numar_pagina - 1, self.aplicants, self.original_author, self.message, self.title_placeholder))
        elif aplicant_name == "Inainte":
            await interaction.response.edit_message(
                view=AplicatiiListView(self.soup, self.numar_pagina + 1, self.aplicants, self.original_author, self.message, self.title_placeholder))
        else:
            for i in self.aplicants:
                # print(i)
                if i[1] == aplicant_name:
                    await interaction.response.defer()
                    temp_soup = await panou.ruby.ruby.get_panel_data(aplicant_name)
                    embed = await panou.ruby.ruby.stats(temp_soup)
                    # embed = create_fh_embed(i, nickname=get_nickname(self.soup))
                    # embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            await interaction.edit_original_message(content="**Statistici jucator:**", embed=embed)

class AplicatiiListView(disnake.ui.View):
    def __init__(self, soup: str, numar_pagina: int, aplicants=None, original_author=None, message=None, title_placeholder=""):
        super().__init__()

        self.add_item(AplicatiiList(soup, numar_pagina, aplicants, title_placeholder=title_placeholder))
        self.children[0].original_author = original_author
        self.children[0].message = message

class AplicatiiMenu(disnake.ui.View):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup):
        super().__init__(timeout=600.0)
        self.soup = soup
        self.aplicatii = get_aplicants(soup)

    async def interaction_check(self, interaction):
        if interaction.author.id == self.original_author.id:
            return True
        await interaction.response.send_message("**❗ Nu poti folosi comanda deoarece nu esti autorul acesteia!**", ephemeral=True)
        return False

    async def on_timeout(self):
        if len(self.children) > 7:
            if self.children[6].options[-1].label == "Inainte":
                self.children[6].options.pop(-1)

            if self.children[6].options[0].label == "Inapoi":
                self.children[6].options[0] = disnake.SelectOption(
                    label="Butoanele au fost dezactivate datorita inactivitatii!",
                    description="Acestea nu mai pot fi selectate in acest mesaj.",
                    emoji="🔒"
                )
        for i in self.children[:6]:
            # i.style = disnake.ButtonStyle.red
            i.disabled = True

        # make sure to update the message with the new buttons
        await self.message.edit(content="**🔒 Butoanele au fost dezactivate datorita inactivitatii!**", view=self)
        try:
            await asyncio.sleep(60)
            await self.message.edit(content="")
        except disnake.HTTPException:
            pass

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Aplicatii noi", custom_id="aplicatii_0", row=0)
    async def aplicatii_noi(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        view = AplicatiiListView(soup=self.soup, numar_pagina=1, original_author=self.original_author, message=self.message, aplicants=self.aplicatii[0], title_placeholder="Aplicatii noi")
        await interaction.response.edit_message(content=f"**Numar aplicatii: {len(self.aplicatii[0])}**", view=view)

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Aplicatii acceptate", custom_id="aplicatii_1", row=0)
    async def aplicatii_acceptate(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        view = AplicatiiListView(soup=self.soup, numar_pagina=1, original_author=self.original_author, message=self.message, aplicants=self.aplicatii[1], title_placeholder="Aplicatii acceptate")
        await interaction.response.edit_message(content=f"**Numar aplicatii: {len(self.aplicatii[1])}**", view=view)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Aplicanti invitati", custom_id="aplicatii_2", row=0)
    async def aplicatii_invitate(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        view = AplicatiiListView(soup=self.soup, numar_pagina=1, original_author=self.original_author, message=self.message, aplicants=self.aplicatii[2], title_placeholder="Aplicanti invitati")
        await interaction.response.edit_message(content=f"**Numar aplicatii: {len(self.aplicatii[2])}**", view=view)

    @disnake.ui.button(style=disnake.ButtonStyle.red, label="Aplicatii respinse", custom_id="aplicatii_3", row=0)
    async def aplicatii_respinse(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        view = AplicatiiListView(soup=self.soup, numar_pagina=1, original_author=self.original_author, message=self.message, aplicants=self.aplicatii[3], title_placeholder="Aplicatii respinse")
        await interaction.response.edit_message(content=f"**Numar aplicatii: {len(self.aplicatii[3])}**", view=view)