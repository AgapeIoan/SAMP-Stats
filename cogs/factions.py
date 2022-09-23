from datetime import datetime
import os
import json
import disnake
import aiohttp
import views
import asyncio
import panou.ruby.ruby

from typing import List
from disnake.ext import commands
from bs4 import BeautifulSoup

from functii.debug import print_debug, print_log
from functii.samp_server_stats import get_server_data, format_server_data
from functii.creier import headers
from functii.storage import LISTA_FACTIUNI
LISTA_FACTIUNI = LISTA_FACTIUNI[1:]

async def autocomplete_factions(inter, string: str) -> List[str]:
    from functii.storage import status_aplicatii_factiuni
    print_debug(status_aplicatii_factiuni)
    factiuni = []
    for i in range(26):
        faction_status = "🟢" if status_aplicatii_factiuni[i+1] else "🔴"
        factiuni.append(f"{faction_status} {LISTA_FACTIUNI[i]}")

    return [lang for lang in factiuni if string.lower() in lang.lower()][:24]


class Factions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(
        name="faction",
        description="Afiseaza statisticile factiunii specificate",
    )
    async def faction(self, inter: disnake.CommandInteraction, faction: str = commands.Param(autocomplete=autocomplete_factions),):
        faction = faction[2:]
        if faction not in LISTA_FACTIUNI:
            await inter.response.send_message(content="Nu am putut gasi factiunea specificata, verifica daca ai scris numele corect!", ephemeral=True)
            return
        
        await inter.response.defer()
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("https://rubypanel.nephrite.ro/faction/list") as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
        
        faction_data_big = panou.ruby.ruby.get_faction_names(soup)
        faction_data = panou.ruby.ruby.find_faction_data_by_name(faction_data_big, faction)
        to_send = f"• {faction_data[1]}\n• Requirements: {faction_data[2].strip()}"
        embed = disnake.Embed(title=faction_data[0], description=to_send, color=0x00ff00)
        embed.set_footer(text="ruby.nephrite.ro")
        embed.timestamp = datetime.now()
        embed.set_thumbnail(url="https://img.agapeioan.ro/samp/logo.png") # DEBUG, trebe sa fac lista custom cu poze de genul pentru toate factiunile
        view = views.factions_menu.MainMenu(faction)
        view.original_author = inter.author
        view.embed = embed
        view.message = await inter.edit_original_message(embed=embed, view=view)

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
