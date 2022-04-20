import disnake
import panou.ruby
from functii.debug import print_debug

# UNTESTED !!!
# Extras din vechiul clase_menus.py

class Clans_Menu(disnake.ui.Select):
    def __init__(self, numar_pagina, clans = None):
        super().__init__()

        options = [disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️')] if numar_pagina > 1 else []
        self.clans = panou.ruby.get_clan_list() if not clans else clans
        self.numar_pagina = numar_pagina

        for i in list(self.clans.items())[(self.numar_pagina-1)*23:(self.numar_pagina*23)]:
            # TODO Rewrite this for dictionary usage instead of list
            k, v = i
            clan_name, clan_tag, clan_members, clan_expire = v
            clan_id = k
            options.append(disnake.SelectOption(label=f"[{clan_tag}] {clan_name}", description=f"ID: {clan_id} | {clan_members} members | expires in {clan_expire}"))

        options.append(disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de masini", emoji="➡️"))

        super().__init__(placeholder='Alege clanul | Pagina ' + str(numar_pagina), min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        clan_name_selectat = self.values[0]
        if clan_name_selectat == "Inapoi":
            await interaction.response.edit_message(view=Clans_Menu_View(self.numar_pagina - 1))
        elif clan_name_selectat == "Inainte":
            await interaction.response.edit_message(view=Clans_Menu_View(self.numar_pagina + 1))
        else:
            for i in list(self.clans.items())[(self.numar_pagina-1)*23:(self.numar_pagina*23)]:
                k, v = i
                clan_name, clan_tag, clan_members, clan_expire = v
                clan_id = k
                if f"[{clan_tag}] {clan_name}" == clan_name_selectat:
                    print_debug('procesam')
                    # TODO #10 Scrapping cum trebuie pentru left si right, "panou.ruby.get_clan_data_by_id(clan_id, 'left/right')"
                    panou.ruby.get_clan_data_by_id(clan_id, 'middle')
                    print_debug('procesat')
                    await interaction.edit_original_message(content = "done")
                    break


class Clans_Menu_View(disnake.ui.View):
    def __init__(self, nr_pagina):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Clans_Menu(nr_pagina))
