import datetime
import os
import json
import disnake

from typing import List
from disnake.ext import commands

from functii.debug import print_debug, print_log
from functii.samp_server_stats import get_server_data, format_server_data

with open("storage/servers/servers_dns.json", "r") as f:
    servers_dns = json.load(f) # list

async def autocomplete_servers(inter, string: str) -> List[str]:
    return [lang for lang in servers_dns if string.lower() in lang.lower()]


class Samp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(
        name="raportu",
        description="Afiseaza statisticile serverului de SAMP specificat",
    )
    async def raportu(self, inter: disnake.CommandInteraction, server_address: str = commands.Param(autocomplete=autocomplete_servers),):
        
        if server_address not in servers_dns:
            await inter.response.send_message(content = "Adresa specificata trebuie sa fie una dintre acestea: \n **- " + "\n- ".join(servers_dns) + "**\n" + "Pe viitor, mai multe servere o sa poata fi verificate.", ephemeral=True)
            return
        
        await inter.response.defer()
        server_data = format_server_data(get_server_data(server_address)) # Dictionary
        if not server_data:
            await inter.edit_original_message(content="**" + inter.author.name + "**, nu am putut gasi date legate de serverul specificat.")
            return
        
        description = (f"Gamemode: {server_data['gamemode']}\n" +
                       f"Language: {server_data['language']}\n" +
                       f"Players: {server_data['players']}")


        embed = disnake.Embed(title=server_data['hostname'], description=description, color=0x00ff00)

        await inter.edit_original_message(embed=embed)
    
    

def setup(bot):
    bot.add_cog(Samp(bot))
