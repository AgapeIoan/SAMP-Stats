import discord
import requests
import re

from bs4 import BeautifulSoup
from functii.samp import vezi_asociere
from functii.creier import scrape_panou, get_nickname, login_panou, este_player_online, get_server_provenienta, get_profile_data, headers

def get_panel_data(player):
    with requests.Session() as s:
        
        # TODO Ceva sa trag tot panel-ul si sa il salvez in memorie.
        # O sa verific daca player-ul exista INAINTE de a afisa butoanele
        
        # O sa am panel intr-un format ce o sa fie prelucrat in parte de vstats, stats, etc, FARA CONEXIUNE LA PANEL? SAU
        # la prima verificare a panel-ului sa imi salvez tot panel-ul undeva?
        # Imo cred ca ar fi mai bine sa merg pe prima varianta, cuz daca tot verific existenta player-ului,
        # automat o sa am tot panel-ul descarcat in memorie

        url = f'http://rubypanel.nephrite.ro/profile/{player}'
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.content, features='html5lib')

        if not get_nickname(soup):
            return None
        
        return soup




def stats(soup):
    with requests.Session() as s:
        lista_valori_scrape = [
            {'div': {'class': 'col-md-12 col-lg-12'}},
            {'div': {'class': 'alert bg-red'}}
        ]

        f2 = soup.findAll('div', {'class': 'tab-pane'})

        badges_raw, ban_status_raw = scrape_panou(soup, lista_valori_scrape)

        try:
            ban_string = ban_status_raw[0].findAll('h4')
            # TODO De infrumusetat urm secventa de linii de cod cand n-am cf
            detrmban = ban_string[0].nextSibling
            motiv_string_lista = []
            for _ in range(5):
                motiv_string_lista.append(detrmban)
                detrmban = detrmban.nextSibling
        except IndexError:
            motiv_string_lista = []

        # nickname_player, player_online, server_de_provenienta = este_player_online(
        #     str(user_name_panou), player)

        nickname_player = get_nickname(soup)
        player_online = "online" if este_player_online(soup) else "offline"
        culoare_player_online = 0x00ff00 if este_player_online(soup) else 0xff0000
        server_de_provenienta = get_server_provenienta(soup)

        embed = discord.Embed(
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
        badges_de_trimis = '' # Stiu ca puteam sa join() dar lasa asa
        data_badges = badges_raw[0].findAll('i')
        for badge in data_badges:
            badges_de_trimis += str(badge.nextSibling).title() + '\n'
        if data_badges:
            embed.add_field(name="Badges", value=badges_de_trimis)
        # Amu bagam datele playerului
        for date in data:
            embed.add_field(name=date[0], value=date[1])


        embed.set_footer(text="Ruby Nephrite | ruby.nephrite.ro:7777")
        print("STATS DATA WAS RETURNED")
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

        # for i in lista_de_trimis:
        #     print(i)
        return lista_de_trimis

def fhstats(soup):
    f2 = soup.findAll('ul', {'class': 'timeline timeline-inverse'})

    # embed = discord.Embed(
    #     title=get_nickname(soup), description="Status: " + "DEBUG", color=0x00ff00)

    # Datele legate de player
    data = [
        [td.text for td in tr.find_all('span')]
        for table in f2 for tr in table.find_all('div')
    ]

    for date in data:
        if len(date) == 1:
            data.remove(date)

    # pattern = "(.+?) was uninvited by (.+?) (.+?) from faction (.+?) ((.+?)) after (.+?) days, with (.+?) FP. Reason: (.+?)."
    # for date in data:
    #     try:
    #         found = re.search(pattern, date[1]).group(2)
    #     except AttributeError:
    #         found = ''
    #     print(found)

    # AgapeIoan was uninvited by Admin Rares. from faction Taxi Los Santos (rank 7) after 200 days, without FP. Reason: Finalizare mandat lider.
    mare_fh = []

    for date in data:
        faction_string = date[1]
        try:
            nickname = faction_string[0:faction_string.find(" was uninvited")]
            lider = re.search("by(.*)from", faction_string).group()[3:-5]
            factiune = re.search("faction(.*).rank", faction_string).group()[8:-6]
            rank = re.search("rank.\d", faction_string).group()[-1:]
            zile = re.search("after (\d+) days", faction_string).group()[6:-5]
            reason = re.search("Reason: (.*)", faction_string).group()[7:-1].strip()
            if "without FP" in faction_string or " 0 FP" in faction_string:
                fp = False
            else:
                fp = re.search("with (.*) FP", faction_string).group()

            # print(fp)
            
        except:
            continue

        # titlu_factiune = f"{factiune} | {zile} days | {rank}"
        # valoare_factiune = (f"Nickname: {nickname}\n" +
        #                     f"Uninvited by: {lider} ")

        # valoare_factiune_post_fp = (f"\nReason: {reason}\n" +
        #                             f"Data: {date[0]}\n")

        # valoare_factiune += (fp + valoare_factiune_post_fp) if fp else valoare_factiune_post_fp

        dictionar = {
            "faction": factiune,
            "days": zile,
            "rank": rank,
            "nickname": nickname,
            "leader": lider,
            "reason": reason,
            "date": date[0].strip(),
            "fp": fp
        }
        mare_fh.append(dictionar)

        # embed.add_field(name=titlu_factiune, value=valoare_factiune, inline=False)
        

    # embed.set_footer(text="Ruby Nephrite | ruby.nephrite.ro:7777")
    
    return mare_fh

def bstats_analyzer(soup):
    biz = bstats(soup)
    if not biz:
        return None
        # Posibil scoatem asta ca nu lasam functia sa ruleze de la inceput daca nu avem biz

    bizes_data = []

    for i in biz:
        print(i)
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

            bizes_data.append({apartament[1][:-3]: [apartament_name, "ID " + apartament_id, apartament_type, apartament_door, apartament_floor]})

    for i in bizes_data:
        print(i)
    return bizes_data

def bstats(soup):
    f2 = soup.findAll('div', {'class': 'tab-pane'}, {'id': 'properties'})

    # for i in f2:
    #     with open(f"skema{f2.index(i)}.txt", "w+", encoding='utf-8') as f:
    #         f.write(str(i))
    data = [
        [td.text for td in tr.find_all('td')]
        for table in [f2[5]] for tr in table.find_all('tr')
    ]
    return data[1:] # lista_properties

def get_clan_name(soup):
    data = get_profile_data(soup, 0)
    if data[4][0] != 'Clan':
        # Player nu are clan
        return None
    else:
        clan_name = data[4][1]
        clan_name = clan_name.split(',')
        # clan_rank = clan_name[1]
        clan_name = clan_name[0]
        return clan_name

def get_clan_list():
    with requests.Session() as s:
        url = f'https://rubypanel.nephrite.ro/clan/list'
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.content, features='html5lib')

        f2 = soup.findAll('table', {'class': 'table table-condensed table-hover'})
        data = [
            [td.text for td in tr.find_all('td')]
            for table in f2 for tr in table.find_all('tr')
        ]
        # for i in data[1:]:
        #     clan_id, clan_name, clan_tag, clan_members, clan_expire = i

        return data[1:]

def get_clan_data(clan_id):
    with requests.Session() as s:
        login_panou(s)
        url = 'https://rubypanel.nephrite.ro/clan/view/' + str(clan_id)
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.content, features='html5lib')
        #TODO Continuat comanda
        # Fac sa acceseze pe id care il luam ez din lista clanuri, dupa fac functii pentru vazut membrii, masini, etc.
        # Maybe fac sa vezi si logs clan?
        # Sa fac drq si baza pentru parcurs pagini in Select Menus
        # Sa se actualizeze cache clan de fiecare data cand folosesc /clans (o sa ajute la comanda /stats unde stim ca mereu clanul ala exista)
        # Pentru /clans folosesc paramatru ca search, sa zica omul primele litere din clan sau clantag, si in lista o sa se returneze rezultate
   
        f2 = soup.findAll('div', {'class': 'col-xs-5'})
        data = [
            [td.text for td in tr.find_all('td')]
            for table in f2 for tr in table.find_all('tr')
        ]

        for i in data:
            print(i)
