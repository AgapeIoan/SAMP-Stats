# cron from cronjob, foarte inspirat

import datetime
import os
import json
import aiohttp

from bs4 import BeautifulSoup
from disnake.ext import tasks, commands

from functii.debug import print_debug, print_log
from functii.creier import login_panou, headers

faction_ids = (1, 2, 3, 8, 18, 11, 9, 7, 13, 17, 14, 19, 26, 4, 5, 6, 10, 15, 16, 20, 21, 23, 12, 22, 24, 25)
# Daca luam factiunile in ordinea de pe panel (pe categorii), asa ar veni id-urile

class Crons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.factions_aplication_status_fetcher.start()
        self.clan_list_fetcher.start()

    @tasks.loop(seconds=3600)
    async def clan_list_fetcher(self):
        from functii.storage import clan_dict
        async with aiohttp.ClientSession(headers=headers) as session:
            # await login_panou(session)
            # Se foloseste treaba de mai sus doar daca e vorba de better performance
            # TODO Benchmark la treaba mentionata anterior
            async with session.get("https://rubypanel.nephrite.ro/clan/list") as response:
                if response.status != 200:
                    print_log(f"Error while fetching clan list, status code: {response.status}")
                    return
                soup = BeautifulSoup(await response.text(), 'html.parser')
                f2 = soup.findAll('table', {'class': 'table table-condensed table-hover'})
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                for clan in data[1:]:
                    # ['85', 'Agency 510', 'A5', '71/150', 'in 52 days']
                    print_debug(clan)
                    clan_dict[int(clan[0])] = {"name": clan[1], "tag": clan[2], "members": clan[3], "days_left": int(clan[4].split(" ")[1])}
                
        print_debug("Fetched clan list")

    @tasks.loop(seconds=3600)
    async def factions_aplication_status_fetcher(self):
        from functii.storage import status_aplicatii_factiuni
        async with aiohttp.ClientSession(headers=headers) as session:
            await login_panou(session)
            async with session.get("https://rubypanel.nephrite.ro/faction/list") as response:
                if response.status != 200:
                    print_log(f"Error while fetching faction list, status code: {response.status}")
                    return
                soup = BeautifulSoup(await response.text(), 'html.parser')
                f2 = soup.findAll('button', {'class': 'btn btn-sm bg-olive'})
                
                for i, j in zip(f2, faction_ids):
                    if i.get('disabled') == 'true':
                        status_aplicatii_factiuni[j] = 0
                    else:
                        status_aplicatii_factiuni[j] = 1
        
        print_debug("Fetched factions aplication status")

    @factions_aplication_status_fetcher.before_loop
    async def before_factions_aplication_status_fetcher(self):
        await self.bot.wait_until_ready()

    @clan_list_fetcher.before_loop
    async def before_clan_list_fetcher(self):
        await self.bot.wait_until_ready()
def setup(bot):
    bot.add_cog(Crons(bot))