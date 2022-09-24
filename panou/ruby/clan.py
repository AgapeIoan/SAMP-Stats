import aiohttp
import asyncio
from bs4 import BeautifulSoup
from functii.debug import print_debug

from functii.storage import clan_dict
from functii.creier import login_panou, headers

def get_clan_names(clan_list):
    names = []
    for k,v in clan_list.items():
        names.append(v['name'])
    return names

def get_clan_id_by_name(clan_name):
    for k,v in clan_dict.items():
        if v['name'] == clan_name:
            return k
    return None

async def get_clan_data(clan_id=None, clan_name=None):
    if clan_id is None:
        clan_id = get_clan_id_by_name(clan_name)
    if clan_id is None:
        return "Not found"
    async with aiohttp.ClientSession(headers=headers) as session:
        await login_panou(session)
        async with session.get(f"https://rubypanel.nephrite.ro/clan/view/{clan_id}") as resp:
            if resp.status != 200:
                return "Page error"
            return BeautifulSoup(await resp.text(), 'html.parser') # soup

async def get_clan_members(soup):
    f2 = soup.findAll('div', {'class': 'col-xs-5'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in f2 for tr in table.find_all('tr')
    ]

    # [['7', ' AgapeIoan', '$12,569,002', '1225', '00:00', '']]
    # Rank, Name, Money, Days, Activity, None
    return data[1:]

async def get_clan_vehicles(soup):
    f2 = soup.findAll('div', {'class': 'col-xs-4'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in f2 for tr in table.find_all('tr')
    ]
    
    # [['482', 'Burrito', '1', ' ', 'display location']]
    # ID, Name, Rank, None, None

    return data[1:]

async def get_clan_info(soup):
    f2 = soup.findAll('div', {'class': 'col-xs-3'})
    panels = f2[0].findAll('div', {'class': 'panel-body'})
    
    # Name, Tag, Members, MOTD, Expires
    clan_info = panels[0].text.strip().split('\n')
    clan_info.pop(4) # junk
    
    # HQ ID, Status, Radio, Furniture
    clan_hq = panels[1].text.strip().split('\n')
    
    # String
    clan_description = panels[2].text.strip()
    clan_forum = panels[3].find('a').get('href')

    # List of ranks from 1 to 7
    clan_ranks = panels[4].text.strip().split('\n')

    clan_info_dict = {
        "clan_info": clan_info,
        "clan_hq": clan_hq,
        "clan_description": clan_description,
        "clan_forum": clan_forum,
        "clan_ranks": clan_ranks
    }
    return clan_info_dict

async def get_clan_logs_snippet(soup):
    f2 = soup.findAll('div', {'class': 'col-xs-4'})
    data = [
        [li.text for li in ul.find_all('li')]
        for table in f2 for ul in table.find_all('ul')
    ]
    
    logs = []
    for log in data[0]:
        logs.append(log.strip())
    
    return logs