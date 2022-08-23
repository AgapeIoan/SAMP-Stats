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


class Factions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(
        name="faction",
        description="Afiseaza statisticile factiunii specificate",
        guild_ids=[722442573137969174],
    )
    async def faction(self, inter: disnake.CommandInteraction, faction: str = commands.Param(autocomplete=autocomplete_factions),):
        await inter.response.defer()
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("https://rubypanel.nephrite.ro/faction/list") as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
        view = views.factions_menu.FactionMenuMainView(soup)
        view.original_author = inter.author
        view.message = await inter.edit_original_message(content=f"**DEBUG**", view=view)

    """
    @commands.slash_command(
        name="testers",
        description="Afiseaza lista testerilor din cadrul factiunii specificate",
        guild_ids=[722442573137969174],
    )
    async def testers(self, inter: disnake.CommandInteraction, faction: str = commands.Param(autocomplete=autocomplete_factions),):
        await inter.response.defer()
        await inter.edit_original_message(content="**" + inter.author.name + "**, asteapta... ||mult si bine||")


    @commands.slash_command(
        name="aplicatii",
        description="Afiseaza aplicantii din cadrul factiunii specificate",
        guild_ids=[722442573137969174],
    )
    async def aplicatii(self, inter: disnake.CommandInteraction, faction: str = commands.Param(autocomplete=autocomplete_factions),):
        await inter.response.defer()
        await inter.edit_original_message(content="**" + inter.author.name + "**, asteapta... ||mult si bine||")
    """

def setup(bot):
    bot.add_cog(Factions(bot))
