import disnake
from disnake import emoji
from disnake.ext.commands import bot
from functii.creier import get_nickname
import panou.ruby

from functii.samp import create_car_embed, format_car_data

class Vehicles_Menu(disnake.ui.Select):
    def __init__(self, soup: str):
        self.soup = soup

        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
#https://cdn.discordapp.com/emojis/897425271475560481.png?size=44
        self.cars = panou.ruby.vstats(soup)
        for i, contor in zip(self.cars, range(23)):
            aux = i.copy()
            car_name, car_specs = format_car_data(aux)
            print(i)
            print(car_name, car_specs)
            # Za name alternative: emoji="<:emoji:897425271475560481>"
            options.append(disnake.SelectOption(label=car_name, description=car_specs, emoji="🚗"))
        
        options.append(disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de masini", emoji="➡️"))

        super().__init__(placeholder='Alege masina', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        car_name = self.values[0]

        if car_name == "Inapoi":
            await interaction.response.edit_message(content="**Selecteaza o optiune:**", embed=None, view=Main_Menu(self.soup))
        else:
            for i in self.cars:
                if(car_name in i[0]):
                    embed = create_car_embed(i, nickname=get_nickname(self.soup))

            await interaction.response.edit_message(embed=embed)

# Define a simple View that gives us a counter button
class Main_Menu(disnake.ui.View):
    def __init__(self, soup: str):
        super().__init__()
        self.soup = soup

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Player Stats", custom_id="stats_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(embed=panou.ruby.stats(self.soup), view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Vehicles", custom_id="vehicles_button")
    async def vstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.add_item(Vehicles_Menu(self.soup))
        await interaction.response.edit_message(content="**Selecteaza o masina:**", view=self, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Properties", custom_id="properties_button")
    async def bstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(content="bstats", view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Faction History", custom_id="faction_button")
    async def fstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(content="fstats", view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Clan", custom_id="clan_button")
    async def cstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(content="cstats", view=self)


        # Define a simple View that gives us a confirmation menu
class Confirm(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @disnake.ui.button(label='Confirm', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @disnake.ui.button(label='Cancel', style=disnake.ButtonStyle.grey)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()


def lista_butoane_stats(stats=False, vstats=False, bstats=False, fstats=False, cstats=False):
    return disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Player Stats",
            custom_id="stats_button",
            disabled=stats
        )
    
    return ActionRow(
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Player Stats",
            custom_id="stats_button",
            disabled=stats
        ),
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Vehicles",
            custom_id="vehicles_button",
            disabled=vstats
        ),
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Properties",
            custom_id="properties_button",
            disabled=bstats
        ),
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Faction History",
            custom_id="faction_button",
            disabled=fstats
        ),
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Clan",
            custom_id="clan_button",
            disabled=cstats
        )
    )

