import disnake

import views.mainmenu
import panou.ruby
from functii.creier import este_player_online
from functii.creier import get_nickname
from functii.discord import disable_not_working_buttons
from functii.samp import create_car_embed, create_fh_embed, format_car_data, format_faction_history_data, \
    format_biz_data, create_biz_embed, get_car_category, get_car_emoji_by_category

faction_emojis = panou.ruby.load_json("storage/factions/faction_emojis.json")

class PropertiesMenu(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup: str, original_author = None, message = None):
        self.soup = soup
        self.original_author = original_author
        self.message = message

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
            za_view = await disable_not_working_buttons(views.mainmenu.MainMenu(self.soup), self.soup)
            za_view.original_author = self.original_author
            za_view.message = self.message
            await interaction.response.edit_message(
                content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(self.soup)}`:**", embed=None,
                view=za_view)
        else:
            # print("SELF = ", self.bizes)
            for i in self.bizes:
                for k, v in i.items():
                    if (v[0] == biz_name):
                        embed = create_biz_embed(i, nickname=get_nickname(self.soup))
                        embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            await interaction.response.edit_message(embed=embed)


class VehiclesMenu(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup: str, numar_pagina: int, cars=None, original_author=None, message=None):
        self.original_author = original_author
        self.message = message
        self.soup = soup
        self.numar_pagina = numar_pagina
        self.cars = panou.ruby.vstats(soup) if not cars else cars
        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        # https://cdn.discordapp.com/emojis/897425271475560481.png?size=44
        # https://cdn.discordapp.com/emojis/913364393385934869.png?size=96
        for i in self.cars[(self.numar_pagina - 1) * 23:(self.numar_pagina * 23)]:
            aux = i.copy()
            car_name, car_specs = format_car_data(aux)
            if len(car_specs) > 95:
                # In caz de EMS sau ceva descriere lunga idk, edge cases mai pe scurt
                car_specs = car_specs[:95] + "..."

            # TODO: #9 Fix EMS edge cases https://prnt.sc/20hc3uf

            # Za name alternative: emoji="<:emoji:897425271475560481>"
            # options.append(disnake.SelectOption(label=car_name, description=car_specs, emoji="<:emoji:913364393385934869>"))
            categorie = get_car_category(car_name)
            # car_emoji = "❗" if not categorie else get_car_emoji_by_category(categorie)
            car_emoji = "❗" if not categorie else get_car_emoji_by_category(categorie)
            options.append(disnake.SelectOption(label=car_name, description=car_specs, emoji=car_emoji))

        # TODO De pasat erori in callback pentru a putea folosi await-ul
        # await send_error_message_to_error_channel(self.bot, "VehiclesMenu: " + str(self.cars))

        if self.cars[(self.numar_pagina * 23):]:
            options.append(
                disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de masini", emoji="➡️"))

        super().__init__(placeholder='Alege masina', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        car_name = self.values[0]

        if car_name == "Inapoi":
            if self.numar_pagina == 1:
                za_view = await disable_not_working_buttons(views.mainmenu.MainMenu(self.soup), self.soup)
                # TODO #36 Vezi ca odata ce iti faci un view nou, iti resetezi toate variabilele din view-ul vechi
                # astfel, ramai fara self.embeds. Ori faci sa le cari cu tine, ori inveti cum sa iti pastrezi view-ul vechi.
                # Vezi tu, te descurci, esti copil mare.
                za_view.original_author = self.original_author
                za_view.message = self.message
                await interaction.response.edit_message(
                    content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(self.soup)}`:**", embed=None,
                    view=za_view)
            else:
                await interaction.response.edit_message(
                    view=VehiclesMenuView(self.soup, self.numar_pagina - 1, self.cars, self.original_author, self.message))
        elif car_name == "Inainte":
            await interaction.response.edit_message(
                view=VehiclesMenuView(self.soup, self.numar_pagina + 1, self.cars, self.original_author, self.message))
        else:
            for i in self.cars:
                if (car_name in i[0]):
                    embed = create_car_embed(i, nickname=get_nickname(self.soup))
                    embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            # TODO: #2 In momentul in care alegem masina, sa se faca optiunea ca default ca sa apara in ui.Select
            await interaction.response.edit_message(embed=embed)


class FactionHistory(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup: str, numar_pagina: int, fh=None, original_author=None, message=None):
        self.original_author = original_author
        self.message = message
        self.soup = soup
        self.fh = panou.ruby.fhstats(soup) if not fh else fh
        self.numar_pagina = numar_pagina

        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        for i in self.fh[(self.numar_pagina - 1) * 23:(self.numar_pagina * 23)]:
            aux = i.copy()
            fh_name, fh_specs = format_faction_history_data(aux)
            emoji = faction_emojis[fh_name[fh_name.find("|") + 2:]]
            options.append(disnake.SelectOption(label=fh_name, description=fh_specs, emoji=emoji))

        if self.fh[(self.numar_pagina * 23):]:
            options.append(
                disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de factiuni", emoji="➡️"))

        super().__init__(placeholder='Faction History', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        fh_name = self.values[0]

        if fh_name == "Inapoi":
            if self.numar_pagina == 1:
                za_view = await disable_not_working_buttons(views.mainmenu.MainMenu(self.soup), self.soup)
                za_view.original_author = self.original_author
                za_view.message = self.message
                await interaction.response.edit_message(
                    content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(self.soup)}`:**", embed=None,
                    view=za_view)
            else:
                await interaction.response.edit_message(
                    view=FactionHistoryView(self.soup, self.numar_pagina - 1, self.fh, self.original_author, self.message))
        elif fh_name == "Inainte":
            await interaction.response.edit_message(
                view=FactionHistoryView(self.soup, self.numar_pagina + 1, self.fh, self.original_author, self.message))
        else:
            for i in self.fh:
                # print(i)
                if (i[0][:10] in fh_name):
                    embed = create_fh_embed(i, nickname=get_nickname(self.soup))
                    embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            await interaction.response.edit_message(content="**Statistici factiune:**", embed=embed)


class VehiclesMenuView(disnake.ui.View):
    def __init__(self, soup: str, numar_pagina: int, cars=None, original_author=None, message=None):
        super().__init__()

        self.add_item(VehiclesMenu(soup, numar_pagina, cars))
        self.children[0].original_author = original_author
        self.children[0].message = message


class FactionHistoryView(disnake.ui.View):
    def __init__(self, soup: str, numar_pagina: int, fh=None, original_author=None, message=None):
        super().__init__()

        self.add_item(FactionHistory(soup, numar_pagina, fh))
        self.children[0].original_author = original_author
        self.children[0].message = message

class PropertiesMenuView(disnake.ui.View):
    def __init__(self, soup: str, original_author=None, message=None):
        super().__init__()

        self.add_item(PropertiesMenu(soup))
        self.children[0].original_author = original_author
        self.children[0].message = message
