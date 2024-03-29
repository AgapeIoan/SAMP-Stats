import disnake
import re
import json
import os
import time
import aiohttp

import functii.typo_proof as typo

from bs4 import BeautifulSoup
from functii.creier import scrape_panou, get_nickname, login_panou, este_player_online, get_server_provenienta, \
    get_profile_data, headers
from functii.debug import print_debug

def load_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return json.load(f)

def dump_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

FACTION_NAMES = load_json('storage/factions/factiuni.json')
FACTION_CATEGORIES = load_json('storage/factions/faction_categories.json') # Contine emojis pe fiecare categorie si
# index-ul fiecarai factiuni in FACTION_NAMES

async def get_staff_list():
    # staff = [[owners], [admins], [helpers], [leaders]]

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get("https://rubypanel.nephrite.ro/staff") as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            f2 = soup.findAll('div', {'class': 'col-xs-12'})
            data = [
                [td.text for td in tr.find_all('td')]
                for table in f2 for tr in table.find_all('tr')
            ]
            i_tags = f2[0].find_all('i')
        
            staff = [[],[],[],[]]
            online_statuses = []
            staff_index = -1
        
            for i in i_tags:
                original_title = i.get('data-original-title')
                if original_title == "Online" or original_title == "Offline":
                    online_statuses.append(original_title)
        
            for date in data[1:]:
                if not date:
                    staff_index += 1
                    continue
                staff[staff_index].append(date)
            
            staff[0], staff[1], staff[2], staff[3] = staff[3], staff[0], staff[1], staff[2] # bruh
            return staff, online_statuses

async def get_online_players():
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get("https://rubypanel.nephrite.ro/online") as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            f2 = soup.findAll('div', {'class': 'col-xs-12'})
            data = [
                [td.text for td in tr.find_all('td')]
                for table in f2 for tr in table.find_all('tr')
            ]
    
    return data

async def get_panel_data(player):
    async with aiohttp.ClientSession(headers=headers) as session:
        if player.lower() != "managera5":
            await login_panou(session)
        url = f'https://rubypanel.nephrite.ro/profile/{player}'
        print_debug("Requesting: " + url)
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
        print_debug("Done.")

        if not get_nickname(soup):
            return None

        return soup

async def get_faction_name(soup):
    f2 = soup.findAll('div', {'class': 'tab-pane'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in [f2[0]] for tr in table.find_all('tr')
    ]

    return data[0][1]

async def fstats(soup):
    faction = await get_faction_name(soup)
    for i in FACTION_NAMES:
        if i.lower() in faction.lower():
            faction = i
            faction_index = FACTION_NAMES.index(i)
            break

    if faction_index == 0:
        print_debug("Faction: Civilian")
        return None

    # https://rubypanel.nephrite.ro/faction/members/1

    url = f'https://rubypanel.nephrite.ro/faction/members/{faction_index}'
    print_debug("Requesting: " + url)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            soup2 = BeautifulSoup(await response.text(), 'html.parser')
        print_debug("Done.")

    f2 = soup2.findAll('div', {'class': 'col-md-12'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in [f2[0]] for tr in table.find_all('tr')
    ]

    for date in data[1:]:
        # ['\n  Seek3r \n', '5\n', '0/3', '48 zile', '2022-02-22 23:40:47',
        #  '\n\n\nore jucate: 07:26/07:00licente de condus suspendate: 5/5jucatori arestati/ucisi: 30/30 \n',
        #  'pe data de 26/02/2022 in jurul orelor 20:00-20:30', ' ']

        # zunake 5 0/3 66 zile 2022-02-25 22:18:21 ore jucate: 00:00/07:00materiale depozitate: 0/150000ucideri: 948 / decese: 398 pe data de 04/03/2022 in jurul orelor 23:00-23:30

        nickname = date[0].replace('\n', '').strip()
        rank = date[1].replace('\n', '').strip()
        fw = date[2].replace('\n', '').strip()
        days = date[3].replace('\n', '').strip()
        last_online = date[4].replace('\n', '').strip()
        raport = date[5].replace('\n', '').strip()
        reset = date[6].replace('\n', '').strip()

        raport_formated = []
        aux = ''
        i=0
        while i < len(raport):
            if not raport[i].isdigit():
                aux += raport[i]
                i+=1
            else:
                try:
                    while raport[i].isdigit() or raport[i] == ':' or raport[i] == '/' or raport[i] == ',':
                        aux += raport[i]
                        i+=1
                except IndexError:
                    pass
                raport_formated.append(aux.replace(' / ', ''))
                aux = ''

        if nickname == get_nickname(soup):
            print(nickname, rank, fw, days, last_online, raport_formated, reset)
            culoare_player_online = 0x00ff00 if este_player_online(soup) else 0xff0000
            to_send = f"Rank: **{rank}**\nFW: **{fw}**\nMembru de: **{days}**"
            for i in raport_formated:
                i = i.capitalize().replace(': ', ': **') + "**"
                to_send += f"\n{i}"

            if reset.find("pe data de") != -1:
                reset = reset.replace("pe data de", "pe data de **")
            else:
                reset =  "**" + reset
            reset = reset.replace("in jurul orelor", "** in jurul orelor **") + "**"

            to_send += f"\n\nPrimeste reset {reset}"
            embed = disnake.Embed(title=faction, description=to_send, color=culoare_player_online)

            embed.set_footer(text=f"{nickname} | ruby.nephrite.ro")
            return embed

async def stats(soup):
    lista_valori_scrape = [
        {'div': {'class': 'col-md-12 col-lg-12'}},
        {'div': {'class': 'alert bg-red'}}
    ]

    f2 = soup.findAll('div', {'class': 'tab-pane'})

    badges_raw, ban_status_raw = scrape_panou(soup, lista_valori_scrape)

    try:
        ban_string = ban_status_raw[0].findAll('h4')
        detrmban = ban_string[0].nextSibling
        motiv_string_lista = []
        for _ in range(5):
            motiv_string_lista.append(detrmban)
            detrmban = detrmban.nextSibling
    except IndexError:
        motiv_string_lista = []

    nickname_player = get_nickname(soup)
    player_online = "online" if este_player_online(soup) else "offline"
    culoare_player_online = 0x00ff00 if este_player_online(soup) else 0xff0000
    server_de_provenienta = get_server_provenienta(soup)

    embed = disnake.Embed(
        title=nickname_player, description="Status: " + player_online, color=culoare_player_online)
    if server_de_provenienta == "ruby":
        embed.set_thumbnail(url="https://i.imgur.com/mZvN9jZ.png")
    else:
        embed.set_thumbnail(url="https://i.imgur.com/jnTomOg.png")

    # Datele legate de player
    data = [
        [td.text for td in tr.find_all('td')]
        for table in [f2[0]] for tr in table.find_all('tr')
    ]

    # Daca e banat bagam si de aia
    if motiv_string_lista:
        autor_ban = str(motiv_string_lista[1])[str(motiv_string_lista[1]).find(r'>') + 1:-4]
        lungime_ban = str(motiv_string_lista[2])[4:-10]  # Nu e lungime, e defapt data cand so dat dar ayaye
        motiv_ban = str(motiv_string_lista[3])[3:-4]
        expira_ban = str(motiv_string_lista[4])[str(motiv_string_lista[4]).find("expire") + 6:]
        de_trm_ban = f"By {autor_ban}\nOn {lungime_ban}\nReason: {motiv_ban}\nExpire {expira_ban}"
        embed.add_field(name="Banned", value=de_trm_ban)

    # Bagam badges sa fie treaba buna
    badges_de_trimis = ''  # Stiu ca puteam sa join() dar lasa asa
    data_badges = badges_raw[0].findAll('i')
    for badge in data_badges:
        badges_de_trimis += str(badge.nextSibling).title() + '\n'
    if data_badges:
        embed.add_field(name="Badges", value=badges_de_trimis)
    # Amu bagam datele playerului
    for date in data:
        embed.add_field(name=date[0], value=date[1])

    embed.set_footer(text=f"{nickname_player} | ruby.nephrite.ro")
    return embed


def vstats(soup):
    return extract_cars(soup.findAll('div', {'class': 'col-md-8'}))


def extract_cars(f2):
    # Functie de returneaza lista cu masinile jucatorului specificat
    data = [
        [td.text for td in tr.find_all('td')]
        for table in f2 for tr in table.find_all('tr')
    ]

    lista_de_trimis = []

    for aux in data:
        if len(aux) == 8:
            # Aparent fiecare lista de masini are lungimea exacta de 8 elemente
            aux_list = []
            for aux_2 in aux:
                aux_2 = aux_2.strip()
                if aux_2:
                    aux_list.append(aux_2)
            lista_de_trimis.append(aux_list)

    return lista_de_trimis


def fhstats(soup):
    f2 = soup.findAll('ul', {'class': 'timeline timeline-inverse'})

    # Datele legate de player
    data = [
        [td.text for td in tr.find_all('span')]
        for table in f2 for tr in table.find_all('div')
    ]

    for date in data:
        if len(date) == 1:
            data.remove(date)
    # AgapeIoan was uninvited by Admin Rares. from faction Taxi Los Santos (rank 7) after 200 days, without FP. Reason: Finalizare mandat lider.
    # SindYcate left faction Los Aztecas (rank 1) after 6 days using /quitgroup, with 40 FP.
    # speak has joined the group Las Venturas Police Department (invited by Storck)
    # SindYcate is now the leader of faction Crips Gang (promoted by yani).
    # Awake was uninvited by Coco from faction Hitman Agency (rank 5) after 125 days, with 0 FP. Reason: Cerere de demisie

    mare_fh = []

    for date in data:
        faction_string = date[1]
        # print_debug(date)

        if "was uninvited by" in faction_string:
            pattern = r"(.+?) was (.+?) from faction (.+?) \((.+?)\) after (.+?), (.+?)\. Reason: (.*)"
            name, uninvited_by, faction, rank, zile, fp, reason = re.search(pattern, faction_string).groups()
            mare_fh.append([date[0].strip(), name, faction, rank, zile, fp, uninvited_by, reason])
        elif "left faction" in faction_string:
            pattern = r"(.+?) left faction (.+?) \((.+?)\) after (.+?) using /quitgroup, (.*)"
            name, faction, rank, zile, fp = re.search(pattern, faction_string).groups()
            mare_fh.append([date[0].strip(), name, faction, rank, zile, fp])
        elif "is now the leader of faction" in faction_string:
            pattern = r"(.+?) is now the leader of faction (.+?) \((.+?)\)"
            name, faction, promoted_by = re.search(pattern, faction_string).groups()
            mare_fh.append([date[0].strip(), name, faction, promoted_by])
        elif "joined the group" in faction_string:
            pattern = r"(.+?) has joined the group (.+?) \((.+?)\)"
            name, faction, invited_by = re.search(pattern, faction_string).groups()
            mare_fh.append([date[0].strip(), name, faction, invited_by])

    return mare_fh


def bstats_analyzer(soup):
    biz = bstats(soup)
    if not biz:
        return None
        # Posibil scoatem asta ca nu lasam functia sa ruleze de la inceput daca nu avem biz

    bizes_data = []

    for i in biz:
        # print_debug(i)
        if i[1] == 'house []':
            house = i
            house_id = house[0]
            house_name = house[2]
            house_type = house[3][:house[3].find("Size")]
            house[3] = house[3].replace(house_type, '')
            if "Garage" in house[3]:
                house_garage = house[3][house[3].find('Garage:'):].strip()
                house[3] = house[3].replace(house_garage, '')
            else:
                house_garage = "Garage: None"
            house_size = house[3]

            bizes_data.append({house[1][:-3]: [house_name, "ID " + house_id, house_size, house_type, house_garage]})

        elif i[1] == 'business []':
            bizz = i
            bizz_id = bizz[0]
            bizz_name = bizz[2]
            bizz_price = bizz[3][:bizz[3].find("Type")]
            bizz[3] = bizz[3].replace(bizz_price, '')
            bizz_fee = bizz[3][bizz[3].find('Fee:'):]
            bizz[3] = bizz[3].replace(bizz_fee, '')
            bizz_type = bizz[3]

            bizes_data.append({bizz[1][:-3]: [bizz_name, "ID " + bizz_id, bizz_fee, bizz_price, bizz_type]})

        elif i[1] == 'apartament []':
            apartament = i
            apartament_id = apartament[0]
            apartament_name = apartament[2]
            apartament_type = apartament[3][:apartament[3].find("Floor:")]
            apartament[3] = apartament[3].replace(apartament_type, '')
            apartament_door = apartament[3][apartament[3].find('Door status:'):]
            apartament[3] = apartament[3].replace(apartament_door, '')
            apartament_floor = apartament[3]

            bizes_data.append({apartament[1][:-3]: [apartament_name, "ID " + apartament_id, apartament_type,
                                                    apartament_door, apartament_floor]})

    return bizes_data


def bstats(soup):
    f2 = soup.findAll('div', {'class': 'tab-pane'}, {'id': 'properties'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in [f2[5]] for tr in table.find_all('tr')
    ]
    return data[1:]  # lista_properties


def get_faction_names(soup):
    print_debug("Getting faction data...")
    f2 = soup.findAll('div', {'class': 'col-xs-12'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in f2 for tr in table.find_all('tr')
    ]

    faction_data = []
    for i in data[1:]:
        print_debug(i)
        try:
            faction_name = i[0]
            faction_members = i[1]
            faction_requirements = i[4]

            faction_data.append([faction_name, faction_members, faction_requirements])
        except IndexError:
            print_debug("IndexError")
            pass
    print_debug("RETURNEZ FACTION DATA")
    return faction_data

def find_faction_data_by_name(faction_data, faction_name):
    for i in faction_data:
        if typo.is_lev_legit(typo.compare_faction_names(i[0], faction_name)):
            return i
    return None

def get_closest_faction_name(faction_name):
    faction_name = faction_name.lower()
    for name in FACTION_NAMES:
        aux = name
        name = name.lower()
        if typo.is_lev_legit(typo.compare_faction_names(faction_name, name)):
            return aux
    return None    

def get_faction_data(soup):
    f2 = soup.findAll('div', {'class': 'col-md-12'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in f2 for tr in table.find_all('tr')
    ]
    members = []
    for date in data[1:]:
        # ['\n  Seek3r \n', '5\n', '0/3', '48 zile', '2022-02-22 23:40:47',
        #  '\n\n\nore jucate: 07:26/07:00licente de condus suspendate: 5/5jucatori arestati/ucisi: 30/30 \n',
        #  'pe data de 26/02/2022 in jurul orelor 20:00-20:30', ' ']

        # zunake 5 0/3 66 zile 2022-02-25 22:18:21 ore jucate: 00:00/07:00materiale depozitate: 0/150000ucideri: 948 / decese: 398 pe data de 04/03/2022 in jurul orelor 23:00-23:30

        nickname = date[0].replace('\n', '').strip()
        rank = date[1].replace('\n', '').strip()
        fw = date[2].replace('\n', '').strip()
        days = date[3].replace('\n', '').strip()
        last_online = date[4].replace('\n', '').strip()
        raport = date[5].replace('\n', '').strip()
        reset = date[6].replace('\n', '').strip()

        raport_formated = []
        aux = ''
        i=0
        while i < len(raport):
            if not raport[i].isdigit():
                aux += raport[i]
                i+=1
            else:
                try:
                    while raport[i].isdigit() or raport[i] == ':' or raport[i] == '/' or raport[i] == ',':
                        aux += raport[i]
                        i+=1
                except IndexError:
                    pass
                raport_formated.append(aux.replace(' / ', ''))
                aux = ''

        members.append([nickname, rank, fw, days, last_online, raport, reset])
    return members



def get_clan_name(soup):
    data = get_profile_data(soup, 0)
    if data[4][0] != 'Clan':
        # Player nu are clan
        return None

    clan_name = data[4][1]
    clan_name = clan_name.split(',')
    # clan_rank = clan_name[1]
    clan_name = clan_name[0]
    return clan_name


async def get_clan_list():
    print_debug("Getting clan list...")

    unix_modification = os.path.getmtime("storage/clans/clan_list.json")
    if time.time() - unix_modification < 30400:  # Juma de zi aprox
        with open("storage/clans/clan_list.json", "r", encoding='utf-8') as f:
            clan_dict = json.load(f)
        print_debug("Clan list loaded from file.")
        return clan_dict

    async with aiohttp.ClientSession(headers=headers) as session:
        url = 'https://rubypanel.nephrite.ro/clan/list'
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')

        f2 = soup.findAll('table', {'class': 'table table-condensed table-hover'})
        data = [
            [td.text for td in tr.find_all('td')]
            for table in f2 for tr in table.find_all('tr')
        ]
        clan_dict = {}
        for i in data[1:]:
            clan_id, clan_name, clan_tag, clan_members, clan_expire = i
            clan_dict[clan_id] = [clan_name, clan_tag, clan_members, clan_expire]

        dump_json('storage/clans/clan_list.json', clan_dict)
        print_debug("Clan list loaded from web.")
        return clan_dict


async def get_clan_id_by_name(clan_name):
    clan_dict = await get_clan_list()
    for i in clan_dict:
        if clan_dict[i][0] == clan_name:
            return i
    return None


async def get_clan_tag_by_name(clan_name):
    clan_dict = await get_clan_list()
    for i in clan_dict:
        if clan_dict[i][0] == clan_name:
            return clan_dict[i][1]
    return None


async def get_clan_data_by_id(clan_id, pozitie, forced=False):
    print_debug(f"Getting clan data for clan {clan_id}...")
    cols = {
        "left": {'class': 'col-xs-3'},
        "middle": {'class': 'col-xs-5'},
        "right": {'class': 'col-xs-4'}
    }

    if pozitie not in cols:
        raise ValueError(f"Pozitie invalida: {pozitie}")

    async with aiohttp.ClientSession(headers=headers) as session:
        print_debug("Logging in...")
        if not forced:
            await login_panou(session)
        else:
            print_debug("Forced login...")
            await login_panou(session, forced_login=True)
        print_debug("Logged in.")
        url = 'https://rubypanel.nephrite.ro/clan/view/' + str(clan_id)
        print_debug(f"Getting clan data from {url}...")
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
        f2 = soup.findAll('div', cols[pozitie])
        data = [
            [td.text for td in tr.find_all('td')]
            for table in f2 for tr in table.find_all('tr')
        ]
        hrefs = [a.get('href') for a in soup.find_all('a')]
        nicknames = []
        for href in hrefs:
            if "https://rubypanel.nephrite.ro/profile/" in href:
                nickname = href[38:]
                nicknames.append(nickname)

        print_debug("Clan data loaded.")
        print_debug(f"Clan data: {data}")
        return data, nicknames


async def get_player_clan_data(data, nickname_original, nicknames):
    data.pop(0)
    for i in nicknames:
        if i == nickname_original:
            return data[nicknames.index(i)]
