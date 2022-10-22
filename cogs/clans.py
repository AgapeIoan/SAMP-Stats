from datetime import datetime
import os
import json
import disnake
import aiohttp
import asyncio
import panou.ruby.clan as clan

from typing import List
from disnake.ext import commands
from bs4 import BeautifulSoup

from functii.debug import print_debug, print_log
from functii.samp_server_stats import get_server_data, format_server_data
from functii.creier import headers
from views.clanmenu import MainMenu

async def autocomplete_clans(inter, string: str) -> List[str]:
    from functii.storage import clan_dict
    clans = []
    for k,v in clan_dict.items():
        # 85 - {'name': 'Agency 510', 'tag': 'A5', 'members': '71/150', 'days': 52}
        # **[A5]** Agency 510 | 71/150 members | expires in 52 days
        clans.append(f"[{v['tag']}] {v['name']} | {v['members']} members, expires in {v['days_left']} days")
    return [lang for lang in clans if string.lower() in lang.lower()][:24]


class Clans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="clan",
        description="Afiseaza statisticile clanului specificat",
        guild_ids=[722442573137969174],
    )
    async def clan(self, inter: disnake.CommandInteraction, clan_name: str = commands.Param(description="Selecteaza clanul" ,autocomplete=autocomplete_clans),):        
        await inter.response.defer()
        clan_name = clan_name.split("]")[1].split("|")[0].strip()
        clan_id = clan.get_clan_id_by_name(clan_name)
        if clan_id is None:
            await inter.response.send_message("[DEBUG] Clan not found")
            return

        soup = await clan.get_clan_data(clan_id=clan_id)
        if soup == "Page error":
            await inter.response.send_message("[DEBUG] Page error")
            return
        elif soup == "Not found":
            await inter.response.send_message("[DEBUG] Clan not found")
            return

        clan_info_dict = await clan.get_clan_info(soup)
        clan_info = clan_info_dict["clan_info"]

        embed = disnake.Embed(
            title=f"{clan_name}",
            description=f"**Tag:** {clan_info[1]}\n**Members:** {clan_info[2]}\n**MOTD:** {clan_info[3]}\n**Expires:** {clan_info[4]}",
            color=0x00ff00
        )
        embed.set_footer(text="ruby.nephrite.ro")
        # TODO HQ in embed
        # Hyperlink cu link forum

        view = MainMenu(soup)
        view.original_author = inter.author

        view.message = await inter.edit_original_message(
            content=f" ", embed=embed, view=view)

def setup(bot):
    bot.add_cog(Clans(bot))
