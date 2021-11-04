import disnake
from functii.creier import get_nickname
import panou.ruby

from functii.samp import create_car_embed, create_fh_embed, format_car_data, format_faction_history_data, format_biz_data, create_biz_embed
from functii.discord import enable_buttons, disable_not_working_buttons
from functii.creier import este_player_online

class Properties_Menu(disnake.ui.Select):
    def __init__(self, soup: str):
        self.soup = soup

        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        # https://cdn.discordapp.com/emojis/897425271475560481.png?size=44
        self.bizes = panou.ruby.bstats_analyzer(self.soup)

        for i in self.bizes:
            aux = i.copy()
            biz_name, biz_specs = format_biz_data(aux)
            options.append(disnake.SelectOption(label=biz_name, description=biz_specs[4:], emoji=biz_specs[0]))
        
        super().__init__(placeholder='Proprietati', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        biz_name = self.values[0]

        if biz_name == "Inapoi":
            await interaction.response.edit_message(content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(self.soup)}`:**", embed=None, view=disable_not_working_buttons(Main_Menu(self.soup), self.soup))
        else:
            print("SELF = ", self.bizes)
            for i in self.bizes:
                for k, v in i.items():
                    if(v[0] == biz_name):
                        embed = create_biz_embed(i, nickname=get_nickname(self.soup))
                        embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            await interaction.response.edit_message(embed=embed)

class Vehicles_Menu(disnake.ui.Select):
    def __init__(self, soup: str):
        self.soup = soup

        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        # https://cdn.discordapp.com/emojis/897425271475560481.png?size=44
        self.cars = panou.ruby.vstats(soup)
        # TODO #7 Buton de NEXT functional, care sa mearga prin masini
        for i, contor in zip(self.cars, range(23)):
            aux = i.copy()
            car_name, car_specs = format_car_data(aux)
            # print(i)
            # print(car_name, car_specs)
            # Za name alternative: emoji="<:emoji:897425271475560481>"
            options.append(disnake.SelectOption(label=car_name, description=car_specs, emoji="🚗"))
        
        options.append(disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de masini", emoji="➡️"))

        super().__init__(placeholder='Alege masina', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        car_name = self.values[0]

        if car_name == "Inapoi":
            await interaction.response.edit_message(content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(self.soup)}`:**", embed=None, view=disable_not_working_buttons(Main_Menu(self.soup), self.soup))
        else:
            for i in self.cars:
                if(car_name in i[0]):
                    embed = create_car_embed(i, nickname=get_nickname(self.soup))
                    embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            # TODO: #2 In momentul in care alegem masina, sa se faca optiunea ca default ca sa apara in ui.Select
            await interaction.response.edit_message(embed=embed)

class Faction_History(disnake.ui.Select):
    def __init__(self, soup: str):
        self.soup = soup

        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        self.fh = panou.ruby.fhstats(soup)
        for i, contor in zip(self.fh, range(23)):
            aux = i.copy()
            fh_name, fh_specs = format_faction_history_data(aux)
            options.append(disnake.SelectOption(label=fh_name, description=fh_specs, emoji="👮"))
        
        options.append(disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de factiuni", emoji="➡️"))

        super().__init__(placeholder='Faction History', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        fh_name = self.values[0]

        if fh_name == "Inapoi":
            await interaction.response.edit_message(content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(self.soup)}`:**", embed=None, view=disable_not_working_buttons(Main_Menu(self.soup), self.soup))
        else:
            for i in self.fh:
                if(i['date'][:10] in fh_name):
                    embed = create_fh_embed(i, nickname=get_nickname(self.soup))

            await interaction.response.edit_message(embed=embed)

class Clans_Menu(disnake.ui.Select):
    def __init__(self):
        super().__init__()

        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]

        self.clans = panou.ruby.get_clan_list()
        numar_pagina = 1
        # print(self.clans[0:23])
        for i in self.clans[:22]:
            clan_id, clan_name, clan_tag, clan_members, clan_expire = i
            options.append(disnake.SelectOption(label=f"[{clan_tag}] {clan_name}", description=f"ID: {clan_id} | {clan_members} members | expires in {clan_expire}"))

        options.append(disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de masini", emoji="➡️"))

        super().__init__(placeholder='Alege clanul', min_values=1, max_values=1, options=options)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Player Stats", custom_id="stats_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(embed=panou.ruby.stats(self.soup), view=self)


    async def callback(self, interaction: disnake.MessageInteraction):
        clan_name = self.values[0]
        print("Optiunea aleasa: ", clan_name)

class Clans_Menu_View(disnake.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Clans_Menu())

class Main_Menu(disnake.ui.View):
    def __init__(self, soup: str):
        super().__init__()
        self.soup = soup

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Player Stats", custom_id="stats_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if len(self.children) > 5:
            self.remove_item(self.children[5])
        enable_buttons(self)
        button.disabled = True
        await interaction.response.edit_message(embed=panou.ruby.stats(self.soup), view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Vehicles", custom_id="vehicles_button")
    async def vstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        enable_buttons(self)
        button.disabled = True
        self.add_item(Vehicles_Menu(self.soup))
        await interaction.response.edit_message(content="**Selecteaza o masina:**", view=self, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Properties", custom_id="properties_button")
    async def bstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        enable_buttons(self)
        button.disabled = True
        self.add_item(Properties_Menu(self.soup))
        await interaction.response.edit_message(content="**Lista proprietati:**", view=self, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Faction History", custom_id="faction_button")
    async def fstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        enable_buttons(self)
        button.disabled = True
        self.add_item(Faction_History(self.soup))
        await interaction.response.edit_message(content="**Lista factiuni:**", view=self, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Clan", custom_id="clan_button")
    async def cstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        panou.ruby.get_clan_name(self.soup)
        await interaction.response.edit_message(content="cstats", view=self, embed=None)


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