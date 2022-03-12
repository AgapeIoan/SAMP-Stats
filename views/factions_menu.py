import disnake
import panou.ruby
from functii.debug import print_debug

# UNTESTED !!!
# Extras din vechiul clase_menus.py

faction_emojis = panou.ruby.load_json("storage/factions/faction_emojis.json")


class FactionMenu(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup):
        self.soup = soup
        options = []
        faction_data = panou.ruby.get_faction_data(self.soup)

        for faction in faction_data:
            emoji = faction_emojis[faction[0]]
            options.append(disnake.SelectOption(label=f"{faction_data.index(faction) + 1}. {faction[0]}", description=f"{faction[2].capitalize()} | {faction[1]}", emoji=emoji))

        super().__init__(placeholder='Factiuni', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        faction_name = self.values[0][3:].strip()

        await interaction.response.edit_message(content=f"Factiunea **{faction_name}** a fost selectata!")


class FactionMenuView(disnake.ui.View):
    def __init__(self, soup):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(FactionMenu(soup))
