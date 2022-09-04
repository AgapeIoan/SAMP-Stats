import datetime
import os
import json
import disnake
import aiohttp
import views
import asyncio

from disnake.ext import commands
from bs4 import BeautifulSoup

from functii.debug import print_debug, print_log
from functii.samp_server_stats import get_server_data, format_server_data
from functii.creier import headers, color_by_list_lenght, sum_list_indexes
from panou.ruby.ruby import get_online_players, get_staff_list

with open("storage/factions/factiuni.json", "r") as f:
    factiuni_json = json.load(f)[1:] # Faction list, excepts "Civlian" aka first element


async def testers(faction):
    # nu verific aici daca parametrul este corect, verifica in main.py
    testers = []
    id = factiuni_json.index(faction) + 1

    async with aiohttp.ClientSession(headers=headers) as session:
        url = f"https://rubypanel.nephrite.ro/faction/members/{id}"
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            f2 = soup.findAll('div', {'class': 'col-md-12'})
        data = [
            [td.text for td in tr.find_all('td')]
            for table in f2 for tr in table.find_all('tr')
        ]

        for member in data[1:]:
            if "leader" in member[1].strip() or "tester" in member[1].strip():
                testers.append(member[0].strip())

        data = await get_online_players()

        matches = []
        for tester in testers:
            for date in data[1:]:
                if tester.lower() == date[0].lower():
                    matches.append(tester.lower())
                    break
        disponibilitate = color_by_list_lenght(testers, matches)
        to_send = ""
        for tester in testers:
            online_status = "🟢" if tester.lower() in matches else "🔴"
            to_send += online_status + " " + tester + "\n"

        return to_send