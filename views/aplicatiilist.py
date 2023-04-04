import disnake

import views.stats_views
from panou.ruby.misc import get_aplicants
from functii.creier import este_player_online
from functii.creier import get_nickname
from functii.discord import disable_not_working_buttons
from functii.samp import create_car_embed, create_fh_embed, format_car_data, format_faction_history_data, \
    format_biz_data, create_biz_embed, get_car_category, get_car_emoji_by_category

class AplicatiiList(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup: str, numar_pagina: int, aplicanti: list):
        self.soup = soup
        self.numar_pagina = numar_pagina
        self.cars = get_aplicants(soup) if cars is None else cars
        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        for i in self.cars[(self.numar_pagina - 1) * 23:(self.numar_pagina * 23)]:
            aux = i.copy()
            car_name, car_specs = format_car_data(aux)
            if len(car_specs) > 95:
                # In caz de EMS sau ceva descriere lunga idk, edge cases mai pe scurt
                car_specs = car_specs[:95] + "..."

            categorie = get_car_category(car_name)
            car_emoji = "❗" if not categorie else get_car_emoji_by_category(categorie)
            options.append(disnake.SelectOption(label=car_name, description=car_specs, emoji=car_emoji))

        if self.cars[(self.numar_pagina * 23):]:
            options.append(
                disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de masini", emoji="➡️"))

        super().__init__(placeholder='Alege masina', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        car_name = self.values[0]

        if car_name == "Inapoi":
            if self.numar_pagina == 1:
                za_view = await disable_not_working_buttons(views.mainmenu.MainMenu(self.soup), self.soup)
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
                if car_name in i[0]:
                    embed = create_car_embed(i, nickname=get_nickname(self.soup))
                    embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            await interaction.response.edit_message(embed=embed)

class VehiclesMenuView(disnake.ui.View):
    def __init__(self, soup: str, numar_pagina: int, cars=None, original_author=None, message=None):
        super().__init__()

        self.add_item(VehiclesMenu(soup, numar_pagina, cars))
        self.children[0].original_author = original_author
        self.children[0].message = message