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
from functii.creier import headers

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
        guild_ids=[921316017584631829],

    )
    async def id(inter, nickname):
        await inter.response.defer()

        url = "https://rubypanel.nephrite.ro/online"
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                f2 = soup.findAll('div', {'class': 'col-xs-12'})
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

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

def setup(bot):
    bot.add_cog(Legacy(bot))
