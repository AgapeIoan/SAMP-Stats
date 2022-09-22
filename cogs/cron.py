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

    @tasks.loop(seconds=3600)
    async def factions_aplication_status_fetcher(self):
        from functii.storage import status_aplicatii_factiuni
        async with aiohttp.ClientSession(headers=headers) as session:
            await login_panou(session)
            async with session.get("https://rubypanel.nephrite.ro/faction/list") as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                f2 = soup.findAll('button', {'class': 'btn btn-sm bg-olive'})
                
                if len(f2) < 25:
                    print_log("Factions aplication status fetcher: Nu am putut lua statusul aplicatiilor factiunilor!")
                    return
                    # Should be fixed odata cu issue #3

                for i, j in zip(f2, faction_ids):
                    if i.get('disabled') == 'true':
                        status_aplicatii_factiuni[j] = 0
                    else:
                        status_aplicatii_factiuni[j] = 1
        
        print_debug("Fetched factions aplication status")

    @factions_aplication_status_fetcher.before_loop
    async def before_factions_aplication_status_fetcher(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Crons(bot))