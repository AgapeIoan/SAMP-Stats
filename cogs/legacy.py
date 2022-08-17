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

# Cog de urgenta pentru portat comenzi legacy
class Legacy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

def setup(bot):
    bot.add_cog(Legacy(bot))
