import datetime
import os
import json
import disnake

from typing import List
from disnake.ext import commands

from functii.debug import print_debug, print_log
from functii.samp_server_stats import get_server_data, format_server_data

with open("storage/factions/factiuni.json", "r") as f:
    factiuni_json = json.load(f)["factiune"][1:] # Faction list, excepts "Civlian" aka first element

async def autocomplete_factions(inter, string: str) -> List[str]:
    return [lang for lang in factiuni_json if string.lower() in lang.lower()][:24]


class Ruby(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(
        name="faction",
        description="Afiseaza statisticile serverului de SAMP specificat",
        guild_ids=[722442573137969174],
    )
    async def faction(self, inter: disnake.CommandInteraction, faction: str = commands.Param(autocomplete=autocomplete_factions),):
        await inter.response.defer()
        await inter.edit_original_message(content="**" + inter.author.name + "**, asteapta... ||mult si bine||")

def setup(bot):
    bot.add_cog(Ruby(bot))
