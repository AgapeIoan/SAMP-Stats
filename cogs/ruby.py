import disnake
import json
import aiohttp

from bs4 import BeautifulSoup
from typing import List
from disnake.ext import commands

from functii.debug import print_debug
from functii.storage import LISTA_FACTIUNI, LISTA_FACTIUNI_CATEGORIES
from functii.creier import headers
from functii.discord import disable_not_working_buttons_aplicants

from panou.ruby.misc import get_aplicants
from views.aplicatiimenu import AplicatiiMenu

async def autocomplete_factions(inter, string: str) -> List[str]:
    x = [lang for lang in LISTA_FACTIUNI[1:] if string.lower() in lang.lower()]
    return x[:25]

class Ruby(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="aplicatii",
        description="Afiseaza aplicantii din cadrul factiunii specificate",
        guild_ids=[722442573137969174],
    )
    async def aplicatii(self, inter: disnake.CommandInteraction, factiune: str = commands.Param(autocomplete=autocomplete_factions),):
        await inter.response.defer()
        try:
            index_factiune = LISTA_FACTIUNI.index(factiune)
        except ValueError:
            await inter.edit_original_message(content="**" + inter.author.name + "**, nu am putut gasi factiunea specificata.")
            return

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"https://rubypanel.nephrite.ro/faction/applications/{index_factiune}") as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')

        aplicatii = get_aplicants(soup)

        view = await disable_not_working_buttons_aplicants(AplicatiiMenu(soup), soup)
        view.original_author = inter.author
        view.message = await inter.edit_original_message(content=f"[DEBUG] **Aplicatii {factiune}**", view=view)

def setup(bot):
    bot.add_cog(Ruby(bot))