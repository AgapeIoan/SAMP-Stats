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

async def autocomplete_clans(inter, string: str) -> List[str]:
    from functii.storage import clan_dict
    clans = []
    for k,v in clan_dict.items():
        # 85 - {'name': 'Agency 510', 'tag': 'A5', 'members': '71/150', 'days': 52}
        # [A5] Agency 510 | 71/150 members | expires in 52 days
        clans.append(f"[{v['tag']}] {v['name']} | {v['members']} members | expires in {v['days_left']} days")
    return [lang for lang in clans if string.lower() in lang.lower()][:24]


class Clans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(
        name="clan",
        description="Afiseaza statisticile clanului specificat",
        guild_ids=[722442573137969174],
    )
    async def clan(self, inter: disnake.CommandInteraction, clan_name: str = commands.Param(autocomplete=autocomplete_clans),):
        pass
        
        await inter.response.defer()
        await inter.edit_original_message(content="works")

def setup(bot):
    bot.add_cog(Clans(bot))
