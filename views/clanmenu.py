import disnake
import panou.ruby.ruby
import asyncio

from functii.debug import print_debug
from functii.creier import get_soup
from datetime import datetime

from functii.storage import DICT_EMOJIS_CUSTOM_VEHICLES
from panou.ruby.clan import clan_veh_list_counter, get_clan_members, get_clan_vehicles

class MainMenu(disnake.ui.View):
    message: disnake.Message
    original_author: disnake.User
    embed: disnake.Embed

    def __init__(self, soup: str):
        super().__init__(timeout=400.0)
        self.soup = soup

    # Timeout and error handling.
    async def on_timeout(self):
        if len(self.children) > 3:
            if self.children[3].options[-1].label == "Inainte":
                self.children[3].options.pop(-1)

            if self.children[3].options[0].label == "Inapoi":
                self.children[3].options[0] = disnake.SelectOption(
                    label="Butoanele au fost dezactivate datorita inactivitatii!",
                    description="Acestea nu mai pot fi selectate in acest mesaj.",
                    emoji="🔒"
                )
        for i in self.children[:3]:
            i.disabled = True

        await self.message.edit(content="**🔒 Butoanele au fost dezactivate datorita inactivitatii!**", view=self)
        try:
            await asyncio.sleep(60)
            await self.message.edit(content="")
        except disnake.HTTPException:
            pass

    async def interaction_check(self, interaction):
        if interaction.author.id == self.original_author.id:
            return True
        await interaction.response.send_message("**❗ Nu poti folosi comanda deoarece nu esti autorul acesteia!**", ephemeral=True)
        return False

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Members", custom_id="clan_members_button", row=0)
    async def clan_members(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        if self.children[1].disabled:
            self.children[1].disabled = False
            self.remove_item(self.children[2])
        members = await get_clan_members(self.soup)
        self.add_item(ClanMembers(members, self))
        await interaction.response.edit_message(view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Vehicles", custom_id="clan_vehicles_button", row=0)
    async def clan_vehicles(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        if self.children[0].disabled:
            self.children[0].disabled = False
            self.remove_item(self.children[2])
        vehicles = await get_clan_vehicles(self.soup)
        self.add_item(ClanVehicles(vehicles, self))
        await interaction.response.edit_message(view=self)

    """
    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Description", custom_id="clan_description_button", row=0)
    async def clan_description(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        members = await get_clan_members(self.soup)
        self.add_item(ClanMembers(members, self))
        await interaction.response.edit_message(view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Ranks", custom_id="clan_ranks_button", row=0)
    async def clan_ranks(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        members = await get_clan_members(self.soup)
        self.add_item(ClanMembers(members, self))
        await interaction.response.edit_message(view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Logs", custom_id="clan_logs_button", row=0)
    async def clan_logs(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        members = await get_clan_members(self.soup)
        self.add_item(ClanMembers(members, self))
        await interaction.response.edit_message(view=self)
    """

class ClanVehicles(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, vehicles, mainmenuview, numar_pagina=1):
        self.vehicles = vehicles
        self.numar_pagina = numar_pagina
        self.mainmenu = mainmenuview
        options = [disnake.SelectOption(label='Inapoi', description='Reveniti la pagina anterioara', emoji='⬅️'),] if numar_pagina > 1 else []

        veh_count = clan_veh_list_counter(vehicles)
        print_debug(veh_count)

        for vehicle in list(veh_count)[(self.numar_pagina - 1) * 23:(self.numar_pagina * 23)]:
            veh_temp = vehicle.split("_")
            print_debug(veh_temp)
            za_emoji = DICT_EMOJIS_CUSTOM_VEHICLES[veh_temp[1].lower()]
            options.append(disnake.SelectOption(label=veh_temp[1], description=f"ID: {veh_temp[0]} | Rank {veh_temp[2]} | {veh_count[vehicle]} pcs", emoji=f"<:emoji:{za_emoji}>"))
            # TODO Emojis pentru fiecare masina pe dropdown lista de vehs clan

        if self.vehicles[(self.numar_pagina * 23):]:
            options.append(
                disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de membri", emoji="➡️"))
        
        super().__init__(placeholder='Vehicule', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        member = self.values[0]

        if member == "Inapoi":
                self.mainmenu.remove_item(self.mainmenu.children[-1])
                self.mainmenu.add_item(ClanVehicles(self.vehicles, self.mainmenu, self.numar_pagina - 1))
                await interaction.response.edit_message(
                    view=self.mainmenu)
        elif member == "Inainte":
            self.mainmenu.remove_item(self.mainmenu.children[-1])
            self.mainmenu.add_item(ClanVehicles(self.vehicles, self.mainmenu, self.numar_pagina + 1))
            await interaction.response.edit_message(
                view=self.mainmenu)
        else:
            await interaction.response.defer()

class ClanMembers(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, members, mainmenuview, numar_pagina=1):
        self.members = members
        self.numar_pagina = numar_pagina
        self.mainmenu = mainmenuview
        options = [disnake.SelectOption(label='Inapoi', description='Reveniti la pagina anterioara', emoji='⬅️'),] if numar_pagina > 1 else []

        for member in self.members[(self.numar_pagina - 1) * 23:(self.numar_pagina * 23)]:
            # TODO Aranjat frumos datele
            options.append(disnake.SelectOption(label=member[1], description=f"{member[0]} | {member[2]}", emoji="🧑")) # TODO Emojis per rank
        
        if self.members[(self.numar_pagina * 23):]:
            options.append(
                disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de membri", emoji="➡️"))

        super().__init__(placeholder='Membri', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        member = self.values[0]

        if member == "Inapoi":
                self.mainmenu.remove_item(self.mainmenu.children[-1])
                self.mainmenu.add_item(ClanMembers(self.members, self.mainmenu, self.numar_pagina - 1))
                await interaction.response.edit_message(
                    view=self.mainmenu)
        elif member == "Inainte":
            self.mainmenu.remove_item(self.mainmenu.children[-1])
            self.mainmenu.add_item(ClanMembers(self.members, self.mainmenu, self.numar_pagina + 1))
            await interaction.response.edit_message(
                view=self.mainmenu)
        else:
            for x in self.members:
                if x[1] == member:
                    href = x[-1]
                    break

            await interaction.response.defer()