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
            print_debug(f"Found clan {clan_name} with id {k}")
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
    data2 = f2[0].find_all('tr')
    online_statuses = []
    hrefs = []
    for tr in data2[1:]:
        if tr.find('i', {'class': 'fa fa-circle text-green'}):
            online_statuses.append("Online")
        elif tr.find('i', {'class': 'fa fa-circle text-red'}):
            online_statuses.append("Offline")
        else:
            online_statuses.append("Unknown")

        # get href
        hrefs.append(tr.find('a').get('href'))
    
    for on, player, href in zip(online_statuses, data[1:], hrefs):
        player[5] = on
        player.append(href)

    # [['7', ' AgapeIoan', '$12,569,002', '1225', '00:00', 'Offline (nu ma asteptam la altceva)']]
    # Rank, Name, Money, Days, Activity, Online status
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
    clan_info = []
    clan_info_temp = panels[0].text.strip().split('\n')
    clan_info_temp.pop(4) # junk
    for det in clan_info_temp:
        det = det.split(': ')
        clan_info.append(" ".join(det[1:])) # In caz ca omul are `:` in MOTD, asa nu luam paguba
    
    # HQ ID, Status, Radio, Furniture
    clan_hq = []
    clan_hq_temp = panels[1].text.strip().split('\n')
    for det in clan_hq_temp:
        det = det.split(': ')
        clan_hq.append(" ".join(det[1:]))
    
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

def clan_veh_list_counter(list_of_lists):
    # Counts the number of list occurences and returns it in a dict
    dict_list = {}
    for veh in list_of_lists:
        # ID_Name_Rank
        name = f"{veh[0]}_{veh[1]}_{veh[2]}"
        if name not in dict_list:
            dict_list[name] = 0
        dict_list[name] += 1

    return dict_list