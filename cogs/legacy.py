import datetime
import os
import json
import disnake
import aiohttp
import views
import asyncio

from typing import List
from disnake.ext import commands
from bs4 import BeautifulSoup

from functii.debug import print_debug, print_log
from functii.samp_server_stats import get_server_data, format_server_data
from functii.creier import headers, color_by_list_lenght, sum_list_indexes
from panou.ruby.ruby import get_online_players, get_staff_list

with open("storage/factions/factiuni.json", "r") as f:
    factiuni_json = json.load(f)[1:] # Faction list, excepts "Civlian" aka first element

async def autocomplete_factions(inter, string: str) -> List[str]:
    return [lang for lang in factiuni_json if string.lower() in lang.lower()][:24]

# Cog de urgenta pentru portat comenzi legacy
class Legacy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    @commands.slash_command(
        name="legacy",
        description="Template comanda legacy de portat",
        #guild_ids=[722442573137969174],
        guild_ids=[921316017584631829],
    )
    async def legacy(self, inter: disnake.CommandInteraction, param: str = commands.Param(autocomplete=autocomplete_func_if_needed),):
        # Daca nu vrem autocomplete sau nu e de folos, specificam options in decorator si luam ca argument simplu
        await inter.response.defer()

        # ! Stuff goes here dupa putin curatat cod si asigurat ca inca functioneaza ca juma din botu vechi pare a fi puscat

        await inter.edit_original_message(content=f"**OUTPUT**", embed=embed)
    """
    

    @commands.slash_command(
        name="id",  # Defaults to the function name
        description="Verifica daca jucatorul specificat este online, cu o precizie de cateva minute",
        options=[
            disnake.Option("nickname", "Introdu nickname-ul", disnake.OptionType.string, required=True)
        ],
    )
    async def id(inter, nickname):
        await inter.response.defer()

        data = await get_online_players()

        matches = []
        for date in data[1:]:
            print_debug(date)
            if nickname.lower() in date[0].lower():
                matches.append(date)

        if not matches:
            await inter.edit_original_message(content=f"Jucatorul {nickname} nu este online!")
            return

        embed = disnake.Embed(title="Online Players", description=f"{len(data[1:])}/1000", color=0x7cfc00)
        for match in matches:
            embed.add_field(name=match[0], value=f"Level: {match[1]}\nFaction: {match[2]}\nHours Played: {match[3]}")
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name="testers",
        description="[Legacy] Afiseaza lista testerilor online din factiunea specificata",
    )
    async def testers(self, inter: disnake.CommandInteraction, faction: str = commands.Param(autocomplete=autocomplete_factions),):
        if faction not in factiuni_json:
            await inter.response.send_message(content="Nu am putut gasi factiunea specificata, verifica daca ai scris numele corect!", ephemeral=True)
            return

        await inter.response.defer()

        testers = []
        id = factiuni_json.index(faction) + 1

        async with aiohttp.ClientSession(headers=headers) as session:
            url = f"https://rubypanel.nephrite.ro/faction/members/{id}"
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                f2 = soup.findAll('div', {'class': 'col-md-12'})
            data = [
                [td.text for td in tr.find_all('td')]
                for table in f2 for tr in table.find_all('tr')
            ]

            for member in data[1:]:
                if "leader" in member[1].strip() or "tester" in member[1].strip():
                    testers.append(member[0].strip())

            data = await get_online_players()

            matches = []
            for tester in testers:
                for date in data[1:]:
                    if tester.lower() == date[0].lower():
                        matches.append(tester.lower())
                        break
            disponibilitate = color_by_list_lenght(testers, matches)
            to_send = ""
            for tester in testers:
                online_status = "🟢" if tester.lower() in matches else "🔴"
                to_send += online_status + " " + tester + "\n"
            embed = disnake.Embed(title="Online Testers", description=to_send, color=disponibilitate)
            embed.set_footer(text = faction + " | ruby.nephrite.ro")
            
            await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name="leaders",
        description="[Legacy] Afiseaza lista liderilor de factiuni",
    )
    async def leaders(self, inter: disnake.CommandInteraction):
        await inter.response.defer()
        
        staff_list, online_statuses = await get_staff_list()
        online_statuses = online_statuses[sum_list_indexes(staff_list, 3):] # Fereasca ce am putut gandi
        leaders = staff_list[3]
        text_to_send = ""
        for leader in leaders:
            # [' Baster.', 'Paramedic Department SF', '136', '2022-08-23 21:32:46']
            # Paramedic Department SF - Baster - 136 days
            # text_to_send += f"{leader[1]} - {leader[0]} - {leader[2]} days\n"
            if online_statuses[leaders.index(leader)] == "Online":
                text_to_send += f"🟢 **{leader[0]}** - {leader[1]} - {leader[2]} days\n"
            else:
                text_to_send += f"🔴 **{leader[0]}** - {leader[1]} - {leader[2]} days\n"

            embed = disnake.Embed(title="Online Leaders", description=text_to_send, color=0x7cfc00)
            embed.set_footer(text = "ruby.nephrite.ro")
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name="helpers",
        description="[Legacy] Afiseaza lista helperilor de pe server",
        #guild_ids=[722442573137969174],
        guild_ids=[921316017584631829],
    )
    async def helpers(self, inter: disnake.CommandInteraction):
        await inter.response.defer()
        
        staff_list, online_statuses = await get_staff_list()
        online_statuses = online_statuses[sum_list_indexes(staff_list, 2):] # Fereasca ce am putut gandi
        helpers = staff_list[2]
        text_to_send = ""
        for helper in helpers:
            if online_statuses[helpers.index(helper)] == "Online":
                text_to_send += f"🟢 **{helper[0]}** - Level {helper[1]}\n"
            else:
                text_to_send += f"🔴 **{helper[0]}** - Level {helper[1]}\n"

            embed = disnake.Embed(title="Online Helpers", description=text_to_send, color=0x7cfc00)
            embed.set_footer(text = "ruby.nephrite.ro")
        await inter.edit_original_message(embed=embed)


    @commands.slash_command(
        name="admins",
        description="[Legacy] Afiseaza lista adminilor de pe server",
    )
    async def admins(self, inter: disnake.CommandInteraction):
        await inter.response.defer()
        
        staff_list, online_statuses = await get_staff_list()
        online_statuses = online_statuses
        admins = staff_list[0] + staff_list[1]
        text_to_send = ""
        for admin in admins:
            print_debug(admin)
            # [' qThePoweR', '4\n manager paramedic  support, account moderator ', '\n manager paramedic  support, account moderator ', '2022-08-23 22:12:44']
            descriere_admin = admin[1].replace("  ", " | ").replace("\n ", " - ").replace("\n","").strip() # Quick fix, not the best, not the worst
            if online_statuses[admins.index(admin)] == "Online":
                text_to_send += f"🟢 **{admin[0]}** - Level {descriere_admin}\n"
            else:
                text_to_send += f"🔴 **{admin[0]}** - Level {descriere_admin}\n"

            embed = disnake.Embed(title="Online Admins", description=text_to_send, color=0x7cfc00)
            embed.set_footer(text = "ruby.nephrite.ro")
        await inter.edit_original_message(embed=embed)


def setup(bot):
    bot.add_cog(Legacy(bot))
