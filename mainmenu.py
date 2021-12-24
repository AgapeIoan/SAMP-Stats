import asyncio

import disnake

import panou.ruby
import stats_views
from functii.creier import este_player_online, get_nickname
from functii.discord import disable_all_buttons, enable_buttons
from functii.debug import print_debug


class MainMenu(disnake.ui.View):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup: str):
        # TODO #26 Maybe maybe dam reset la timeout la fiecare interactiune (apasare de buton, dropdown si ce o mai fi)
        super().__init__(timeout=180.0)
        self.soup = soup
        self.clan_embed = None

    # Timeout and error handling.
    async def on_timeout(self):
        if len(self.children) > 5:
            if self.children[5].options[-1].label == "Inainte":
                self.children[5].options.pop(-1)

            if self.children[5].options[0].label == "Inapoi":
                self.children[5].options[0] = disnake.SelectOption(
                    label="Butoanele au fost dezactivate datorita inactivitatii!",
                    description="Acestea nu mai pot fi selectate in acest mesaj.",
                    emoji="🔒"
                )
        for i in self.children[:5]:
            # i.style = disnake.ButtonStyle.red
            i.disabled = True

        # make sure to update the message with the new buttons
        await self.message.edit(content="**🔒 Butoanele au fost dezactivate datorita inactivitatii!**", view=self)
        try:
            await asyncio.sleep(60)
            await self.message.edit(content="")
        except disnake.HTTPException:
            pass

    async def interaction_check(self, interaction):
        # print_debug(f"{interaction.author.id} != {self.original_author.id}")
        # print_debug(interaction.author.id != self.original_author.id)

        if interaction.author.id == self.original_author.id:
            return True

        await interaction.response.send_message("**❗ Nu poti folosi comanda deoarece nu esti autorul acesteia!**",
                                                ephemeral=True)
        return False

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Player Stats", custom_id="stats_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if len(self.children) > 5:
            self.remove_item(self.children[5])
        await enable_buttons(self)
        button.disabled = True
        await interaction.response.edit_message(content="**Statistici jucator:**",
                                                embed=await panou.ruby.stats(self.soup), view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Vehicles", custom_id="vehicles_button")
    async def vstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        # await enable_buttons(self)
        # button.disabled = True
        view = stats_views.VehiclesMenuView(soup=self.soup, numar_pagina=1, original_author=self.original_author, message=self.message)
        await interaction.response.edit_message(content="**Selecteaza o masina:**", view=view, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Properties", custom_id="properties_button")
    async def bstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        view = stats_views.PropertiesMenuView(self.soup, self.original_author, self.message)
        view.original_author = self.original_author
        view.message = self.message
        await interaction.response.edit_message(content="**Lista proprietati:**", view=view, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Faction History", custom_id="faction_button")
    async def fstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        view = stats_views.FactionHistoryView(soup=self.soup, numar_pagina=1, original_author=self.original_author, message=self.message)
        await interaction.response.edit_message(content="**Lista factiuni:**", view=view, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Clan", custom_id="clan_button")
    async def cstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        if len(self.children) > 5:
            self.remove_item(self.children[5])

        if not self.clan_embed:
            await disable_all_buttons(self)
            await interaction.edit_original_message(content="**Caut datele de clan cerute...**", view=self, embed=None)

            clan_name = panou.ruby.get_clan_name(self.soup)
            clan_tag = await panou.ruby.get_clan_tag_by_name(clan_name)
            data, nicknames = await panou.ruby.get_clan_data_by_id(await panou.ruby.get_clan_id_by_name(clan_name), 'middle')
            player_stats = await panou.ruby.get_player_clan_data(data, get_nickname(self.soup), nicknames)
            print_debug(player_stats)
            # player_stats = ['7', 'Nickname', '$12,569,002', '937', '00:00', '']

            embed = disnake.Embed(title=f"[{clan_tag}] {clan_name}", color=0x00ff00)
            value_to_send = (f"Rank: {player_stats[0]}\n"
                             f"Bani seif: {player_stats[2]}\n"
                             f"Zile: {player_stats[3]}\n"
                             f"Ore last 7: {player_stats[4]}\n")

            embed.add_field(name="Clan stats", value=value_to_send)
            embed.set_footer(text=f"{player_stats[1]} | ruby.nephrite.ro")
            embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            self.clan_embed = embed

        await enable_buttons(self)
        button.disabled = True
        await interaction.edit_original_message(content="**Statistici clan:**", embed=self.clan_embed, view=self)
