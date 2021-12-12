import disnake
import asyncio

from disnake import player
from disnake.ui import view
from functii.creier import get_nickname
from functii.debug import print_debug
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
    def __init__(self, soup: str, numar_pagina: int, cars = None):
        self.soup = soup
        self.numar_pagina = numar_pagina
        self.cars = panou.ruby.vstats(soup) if not cars else cars
        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        # https://cdn.discordapp.com/emojis/897425271475560481.png?size=44
        # https://cdn.discordapp.com/emojis/913364393385934869.png?size=96
        for i in self.cars[(self.numar_pagina-1)*23:(self.numar_pagina*23)]:
            aux = i.copy()
            car_name, car_specs = format_car_data(aux)
            if len(car_specs) > 95:
                # In caz de EMS sau ceva descriere lunga idk, edge cases mai pe scurt
                car_specs = car_specs[:95] + "..."
            
            # TODO: #9 Fix EMS edge cases https://prnt.sc/20hc3uf

            # Za name alternative: emoji="<:emoji:897425271475560481>"
            # options.append(disnake.SelectOption(label=car_name, description=car_specs, emoji="<:emoji:913364393385934869>"))
            options.append(disnake.SelectOption(label=car_name, description=car_specs, emoji="🚗"))


        if self.cars[(self.numar_pagina*23):]:
            options.append(disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de masini", emoji="➡️"))

        super().__init__(placeholder='Alege masina', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        car_name = self.values[0]

        if car_name == "Inapoi":
            if self.numar_pagina == 1:
                await interaction.response.edit_message(content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(self.soup)}`:**", embed=None, view=disable_not_working_buttons(Main_Menu(self.soup), self.soup))
            else:
                await interaction.response.edit_message(view=Vehicles_Menu_View(self.soup, self.numar_pagina - 1, self.cars))
        elif car_name == "Inainte":
            await interaction.response.edit_message(view=Vehicles_Menu_View(self.soup, self.numar_pagina + 1, self.cars))
        else:
            for i in self.cars:
                if(car_name in i[0]):
                    embed = create_car_embed(i, nickname=get_nickname(self.soup))
                    embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            # TODO: #2 In momentul in care alegem masina, sa se faca optiunea ca default ca sa apara in ui.Select
            await interaction.response.edit_message(embed=embed)

class Faction_History(disnake.ui.Select):
    def __init__(self, soup: str, numar_pagina: int, fh = None):
        self.soup = soup
        self.fh = panou.ruby.fhstats(soup) if not fh else fh
        self.numar_pagina = numar_pagina

        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        faction_emojis = panou.ruby.load_json("storage/faction_emojis.json")
        print(faction_emojis)
        for i in self.fh[(self.numar_pagina-1)*23:(self.numar_pagina*23)]:
            aux = i.copy()
            fh_name, fh_specs = format_faction_history_data(aux)
            emoji = faction_emojis[fh_name[fh_name.find("|")+2:]]
            print(emoji)
            options.append(disnake.SelectOption(label=fh_name, description=fh_specs, emoji=emoji))
            # TODO #13 Emojis pentru fiecare factiune in parte

        if self.fh[(self.numar_pagina*23):]:
            options.append(disnake.SelectOption(label="Inainte", description="Afiseaza urmatoarea pagina de factiuni", emoji="➡️"))

        super().__init__(placeholder='Faction History', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        fh_name = self.values[0]

        if fh_name == "Inapoi":
            if self.numar_pagina == 1:
                await interaction.response.edit_message(content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(self.soup)}`:**", embed=None, view=disable_not_working_buttons(Main_Menu(self.soup), self.soup))
            else:
                await interaction.response.edit_message(view=Faction_History_View(self.soup, self.numar_pagina - 1, self.fh))
        elif fh_name == "Inainte":
            await interaction.response.edit_message(view=Faction_History_View(self.soup, self.numar_pagina + 1, self.fh))
        else:
            for i in self.fh:
                print(i)
                if(i[0][:10] in fh_name):
                    embed = create_fh_embed(i, nickname=get_nickname(self.soup))
                    embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            await interaction.response.edit_message(content="**Statistici factiune:**", embed=embed)

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
                    await interaction.edit_original_message(content = f"done")
                    break


class Clans_Menu_View(disnake.ui.View):
    def __init__(self, nr_pagina):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Clans_Menu(nr_pagina))

class Vehicles_Menu_View(disnake.ui.View):
    def __init__(self, soup: str, numar_pagina: int, cars = None):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Vehicles_Menu(soup, numar_pagina, cars))

class Faction_History_View(disnake.ui.View):
    def __init__(self, soup: str, numar_pagina: int, fh = None):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Faction_History(soup, numar_pagina, fh))

class Main_Menu(disnake.ui.View):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup: str):
        super().__init__(timeout=15.0)
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
        await self.message.edit(content="🔒 Butoanele au fost dezactivate datorita inactivitatii!", view=self)
        try:
            await asyncio.sleep(3)
            await self.message.edit(content="")
        except disnake.HTTPException:
            pass

    async def interaction_check(self, interaction):
        # print_debug(f"{interaction.author.id} != {self.original_author.id}")
        # TODO #18 Se intampla ceva dubiosenie aici, 
        # pana nu se executa print_debug-ul din ruby.py, partea cu printat-ul de fh, pot apasa pe orice buton,
        # insa dupa se reseteaza string-ul la main menu si dupa intra si conditia de mai jos la nevoie
        # De asemenea, nu se executa butoanele cum trebuie pana nu se incarca treaba specificata mai sus. 
        # Optiunile nu au emojis, nu primesc output din terminal de la views

        if interaction.author.id == self.original_author.id:
            await interaction.response.send_message("**❗ Nu poti folosi comanda deoarece nu esti autorul acesteia!**", ephemeral=True)
        else:
            return True



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
        self.add_item(Vehicles_Menu(soup=self.soup, numar_pagina=1))
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
        self.add_item(Faction_History(soup=self.soup, numar_pagina=1))
        await interaction.response.edit_message(content="**Lista factiuni:**", view=self, embed=None)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Clan", custom_id="clan_button")
    async def cstats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        if len(self.children) > 5:
            self.remove_item(self.children[5])
        enable_buttons(self)
        button.disabled = True

        if not self.clan_embed:
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

        await interaction.edit_original_message(content="**Statistici clan:**", embed=self.clan_embed, view=self)
