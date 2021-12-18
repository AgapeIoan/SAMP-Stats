import disnake
import asyncio
import stats_views
import panou.ruby

from functii.discord import disable_all_buttons, enable_buttons
from functii.creier import este_player_online, get_nickname
from functii.debug import print_debug

class Main_Menu(disnake.ui.View):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup: str):
        super().__init__(timeout=150.0)
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
            await asyncio.sleep(15)
            await self.message.edit(content="")
        except disnake.HTTPException:
            pass


    async def interaction_check(self, interaction):
        # print_debug(f"{interaction.author.id} != {self.original_author.id}")
        # print_debug(interaction.author.id != self.original_author.id)

        if interaction.author.id == self.original_author.id:
            return True

        await interaction.response.send_message("**❗ Nu poti folosi comanda deoarece nu esti autorul acesteia!**", ephemeral=True)
        return False



    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Player Stats", custom_id="stats_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if len(self.children) > 5:
            self.remove_item(self.children[5])
        enable_buttons(self)
        button.disabled = True
        await interaction.response.edit_message(content="**Statistici jucator:**", embed=panou.ruby.stats(self.soup), view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Vehicles", custom_id="vehicles_button")
    async def vstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        enable_buttons(self)
        button.disabled = True
        self.add_item(stats_views.Vehicles_Menu(soup=self.soup, numar_pagina=1))
        await interaction.response.edit_message(content="**Selecteaza o masina:**", view=self, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Properties", custom_id="properties_button")
    async def bstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        enable_buttons(self)
        button.disabled = True
        self.add_item(stats_views.Properties_Menu(self.soup))
        await interaction.response.edit_message(content="**Lista proprietati:**", view=self, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Faction History", custom_id="faction_button")
    async def fstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        enable_buttons(self)
        button.disabled = True
        self.add_item(stats_views.Faction_History(soup=self.soup, numar_pagina=1))
        await interaction.response.edit_message(content="**Lista factiuni:**", view=self, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Clan", custom_id="clan_button")
    async def cstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        if len(self.children) > 5:
            self.remove_item(self.children[5])

        if not self.clan_embed:
            disable_all_buttons(self)
            await interaction.edit_original_message(content="**Caut datele cerute...**", view=self)

            clan_name = panou.ruby.get_clan_name(self.soup)
            clan_tag = panou.ruby.get_clan_tag_by_name(clan_name)
            data = panou.ruby.get_clan_data_by_id(panou.ruby.get_clan_id_by_name(clan_name), 'middle')
            player_stats = panou.ruby.get_player_clan_data(data, get_nickname(self.soup))
            # player_stats = ['7', 'Nickname', '$12,569,002', '937', '00:00', '']

            embed = disnake.Embed(title=f"[{clan_tag}] {clan_name}", color=0x00ff00)
            value_to_send = (f"Rank: {player_stats[0]}\n" \
                            f"Bani seif: {player_stats[2]}\n" \
                            f"Zile: {player_stats[3]}\n" \
                            f"Ore last 7: {player_stats[4]}\n")

            embed.add_field(name="Clan stats", value=value_to_send)
            embed.set_footer(text=f"{player_stats[1]} | ruby.nephrite.ro")
            embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            self.clan_embed = embed

        enable_buttons(self)
        button.disabled = True
        await interaction.edit_original_message(content="**Statistici clan:**", embed=self.clan_embed, view=self)
