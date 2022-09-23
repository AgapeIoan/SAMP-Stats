import disnake
import json
import aiohttp

from bs4 import BeautifulSoup
from typing import List
from disnake.ext import commands

from functii.debug import print_debug
from functii.storage import LISTA_FACTIUNI
from functii.creier import headers
from functii.discord import disable_not_working_buttons_aplicants

from panou.ruby.misc import get_aplicants
from views.aplicatiimenu import AplicatiiMenu
LISTA_FACTIUNI = LISTA_FACTIUNI[1:]

async def autocomplete_factions(inter, string: str) -> List[str]:
    from functii.storage import status_aplicatii_factiuni
    print_debug(status_aplicatii_factiuni)
    factiuni = []
    for i in range(26):
        faction_status = "🟢" if status_aplicatii_factiuni[i+1] else "🔴"
        factiuni.append(f"{faction_status} {LISTA_FACTIUNI[i]}")

    return [lang for lang in factiuni if string.lower() in lang.lower()][:24]

class Ruby(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="aplicatii",
        description="Afiseaza aplicantii din cadrul factiunii specificate",
    )
    async def aplicatii(self, inter: disnake.CommandInteraction, factiune: str = commands.Param(autocomplete=autocomplete_factions),):
        await inter.response.defer()
        factiune = factiune[2:]
        try:
            index_factiune = LISTA_FACTIUNI.index(factiune) + 1
        except ValueError:
            await inter.edit_original_message(content="**" + inter.author.name + "**, nu am putut gasi factiunea specificata.")
            return

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"https://rubypanel.nephrite.ro/faction/applications/{index_factiune}") as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')

        view = await disable_not_working_buttons_aplicants(AplicatiiMenu(soup), soup)
        view.original_author = inter.author
        view.message = await inter.edit_original_message(content=f"Aplicatii **{factiune}**", view=view)

def setup(bot):
    bot.add_cog(Ruby(bot))