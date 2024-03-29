from datetime import datetime
import disnake
import panou.ruby.ruby
import asyncio
import functii.lazyfuncs as lf
from functii.debug import print_debug
from functii.creier import get_soup

FACTION_EMOJIS = panou.ruby.ruby.load_json("storage/factions/faction_emojis.json") # indexare de la 0

class FactionMenuMain(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup):
        options = []
        self.faction_data = panou.ruby.ruby.FACTION_CATEGORIES
        print_debug(self.faction_data)
        self.soup = soup

        for k,v in self.faction_data.items():
            print_debug(f"k={k} v={v}")
            emoji = v[0]
            options.append(disnake.SelectOption(label=f"{k}", emoji=emoji))

        super().__init__(placeholder='Factiuni', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        faction_indexes = panou.ruby.ruby.FACTION_CATEGORIES[self.values[0]][1]
        factions = [
            panou.ruby.ruby.FACTION_NAMES[faction_index]
            for faction_index in faction_indexes
        ]

        print_debug(factions)
        await interaction.response.edit_message(view=FactionMenuView(self.soup, factions))

class FactionMenu(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup, faction_names):
        self.soup = soup
        options = []
        self.faction_data_big = panou.ruby.ruby.get_faction_names(self.soup)
        self.faction_names = faction_names

        for faction_name in self.faction_names:
            faction_name = panou.ruby.ruby.get_closest_faction_name(faction_name)
            emoji = FACTION_EMOJIS[faction_name.lower()]
            faction_data = panou.ruby.ruby.find_faction_data_by_name(self.faction_data_big, faction_name)
            for data in self.faction_data_big:
                fname = panou.ruby.ruby.get_closest_faction_name(data[0])
                if fname == faction_name:
                    faction_index = self.faction_data_big.index(data)
                    break
            options.append(disnake.SelectOption(label=f"{faction_index + 1}. {faction_name}", description=f"{faction_data[2].capitalize()} | {faction_data[1]}", emoji=emoji))

        super().__init__(placeholder='Factiuni', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        faction_name = self.values[0][3:]
        faction_data = panou.ruby.ruby.find_faction_data_by_name(self.faction_data_big, faction_name)
        to_send = f"• {faction_data[1]}\n• Requirements: {faction_data[2].strip()}"
        embed = disnake.Embed(title=faction_data[0], description=to_send, color=0x00ff00)
        embed.set_footer(text="ruby.nephrite.ro")
        embed.timestamp = datetime.now()
        embed.set_thumbnail(url="https://img.agapeioan.ro/samp/logo.png") # DEBUG, trebe sa fac lista custom cu poze de genul pentru toate factiunile
        # TODO Dictionar thumbnails per faction
        view = MainMenu(faction_name)
        await interaction.response.edit_message(embed=embed, view=view)


class FactionMembers(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, members, numar_pagina):
        self.members = members
        self.numar_pagina = numar_pagina
        options = [disnake.SelectOption(label='Inapoi', description='Reveniti la pagina anterioara', emoji='⬅️'),] if numar_pagina > 1 else []

        for member in self.members[(self.numar_pagina - 1) * 23:(self.numar_pagina * 23)]:
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

class MainMenu(disnake.ui.View):
    message: disnake.Message
    original_author: disnake.User
    embed: disnake.Embed

    def __init__(self, faction_name: str):
        super().__init__(timeout=400.0)
        self.faction_name = faction_name
        self.clan_embed = None
        self.faction_embed = None
        

    # Timeout and error handling.
    async def on_timeout(self):
        if len(self.children) > 7:
            if self.children[2].options[-1].label == "Inainte":
                self.children[2].options.pop(-1)

            if self.children[2].options[0].label == "Inapoi":
                self.children[2].options[0] = disnake.SelectOption(
                    label="Butoanele au fost dezactivate datorita inactivitatii!",
                    description="Acestea nu mai pot fi selectate in acest mesaj.",
                    emoji="🔒"
                )
        for i in self.children[:2]:
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

        await interaction.response.send_message("**❗ Nu poti folosi comanda deoarece nu esti autorul acesteia!**",
                                                ephemeral=True)
        return False

    @disnake.ui.button(style=disnake.ButtonStyle.green, label="Testers", custom_id="testers_button", row=0)
    async def testers(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if len(self.children) > 2:
            self.remove_item(self.children[2])
        self.embed.add_field(name="Online Testers", value=await lf.testers(self.faction_name), inline=False)
        button.disabled = True
        await interaction.response.edit_message(embed=self.embed, view=self)

class FactionMenuView(disnake.ui.View):
    def __init__(self, soup, index):
        super().__init__()

        self.add_item(FactionMenu(soup, index))

class FactionMenuMainView(disnake.ui.View):
    def __init__(self, soup):
        super().__init__()

        self.add_item(FactionMenuMain(soup))

class FactionMembersView(disnake.ui.View):
    def __init__(self, members, numar_pagina=1):
        super().__init__()

        self.add_item(FactionMembers(members, numar_pagina))