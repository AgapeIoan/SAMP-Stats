import disnake
import panou.ruby
from functii.debug import print_debug
from functii.creier import get_soup

# UNTESTED !!!
# Extras din vechiul clase_menus.py

faction_emojis = panou.ruby.load_json("storage/factions/faction_emojis.json")


class FactionMenu(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup):
        self.soup = soup
        options = []
        self.faction_data = panou.ruby.get_faction_names(self.soup)

        for faction in self.faction_data:
            emoji = faction_emojis[faction[0]]
            options.append(disnake.SelectOption(label=f"{self.faction_data.index(faction) + 1}. {faction[0]}", description=f"{faction[2].capitalize()} | {faction[1]}", emoji=emoji))

        super().__init__(placeholder='Factiuni', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        faction_name = self.values[0][3:].strip()
        for faction in self.faction_data:
            if faction[0] == faction_name:
                faction_index = self.faction_data.index(faction)
                break
        url = "https://rubypanel.nephrite.ro/faction/members/" + str(faction_index + 1)
        soup = await get_soup(url)
        members = panou.ruby.get_faction_data(soup)
        await interaction.response.edit_message(view=FactionMembersView(members))


class FactionMembers(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, members, numar_pagina):
        self.members = members
        self.numar_pagina = numar_pagina
        options = [disnake.SelectOption(label='Inapoi', description='Reveniti la pagina anterioara', emoji='⬅️'),] if numar_pagina > 1 else []

        for member in self.members[(self.numar_pagina - 1) * 23:(self.numar_pagina * 23)]:
            # TODO Aranjat frumos datele
            options.append(disnake.SelectOption(label=member[0], description=f"{member[1]} | {member[2]}"))
        
        if self.members[(self.numar_pagina * 23):]:
            options.append(
                disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de membri", emoji="➡️"))

        super().__init__(placeholder='Membri', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        member = self.values[0]

        if member == "Inapoi":
                await interaction.response.edit_message(
                    view=FactionMembersView(self.members, self.numar_pagina - 1))
        elif member == "Inainte":
            await interaction.response.edit_message(
                view=FactionMembersView(self.members, self.numar_pagina + 1))
        else:
            await interaction.response.edit_message(content=str(member))


class FactionMenuView(disnake.ui.View):
    def __init__(self, soup):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(FactionMenu(soup))

class FactionMembersView(disnake.ui.View):
    def __init__(self, members, numar_pagina=1):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(FactionMembers(members, numar_pagina))