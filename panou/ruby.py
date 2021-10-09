import discord
import requests

from bs4 import BeautifulSoup
from functii.samp import vezi_asociere
from functii.creier import scrape_panou, get_nickname, login_panou, este_player_online

def stats(player):

    with requests.Session() as s:
        lista_valori_scrape = [
            {'div': {'class': 'col-md-8'}},
            {'h3': {'class': 'profile-username'}},
            {'div': {'class': 'col-md-12 col-lg-12'}},
            {'div': {'class': 'alert bg-red'}}
        ]

        url = f'http://rubypanel.nephrite.ro/profile/{player}'
        psot, user_name_panou, badges_raw, ban_status_raw = scrape_panou(s, url, lista_valori_scrape)

        if not psot:
            return 'Nu am putut gasi jucatorul specificat. Verifica daca ai introdus corect nickname-ul!'

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

        nickname_player, player_online, server_de_provenienta = este_player_online(
            str(user_name_panou), player)

        embed = discord.Embed(
            title=nickname_player, description="Status: " + player_online, color=0x00ff00)
        if server_de_provenienta == "ruby":
            embed.set_thumbnail(url="https://i.imgur.com/mZvN9jZ.png")
        else:
            embed.set_thumbnail(url="https://i.imgur.com/jnTomOg.png")

        # Datele legate de player
        data = [
            [td.text for td in tr.find_all('td')]
            for table in psot for tr in table.find_all('tr')
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
        badges_de_trimis = ''
        data_badges = badges_raw[0].findAll('i')
        for badge in data_badges:
            badges_de_trimis += str(badge.nextSibling).title() + '\n'
        if data_badges:
            embed.add_field(name="Badges", value=badges_de_trimis)
        # Amu bagam datele playerului
        for date in data:
            try:
                nume = date[0]
                valoare = date[1]
                if not nume:
                    break
                embed.add_field(name=nume, value=valoare)
            except IndexError:
                pass

        embed.set_footer(text="Ruby Nephrite | ruby.nephrite.ro:7777")
        print("STATS DATA WAS RETURNED")
        return embed

async def stats_debug(player):
    embed = discord.Embed(
    title="nickDEBUG", description="Status: " + "DEBUGGING", color=0x00ff00)
    embed.set_thumbnail(url="https://i.imgur.com/mZvN9jZ.png")
        



async def vstats_debug(inter, player):
    car_list = [['Sandking (ID:9803)', '8997 kilometers', 'No', '1534 days', 'display location'], ['Comet (ID:14739)', '435 kilometers', 'No', '1507 days', 'display location'], ['NRG-500 (ID:19621)', '24400 kilometers', 'No', '1475 days', 'display location'], ['Bike (ID:19825)', '4 kilometers', 'No', '1474 days', 'display location'], ['Sultan (ID:25697)  VIP text: LiderAdv', '8853 kilometers', 'Green', '1439 days', 'display location'], ['Alpha (ID:29007)', '24 kilometers', 'No', '1418 days', 'display location'], ['Phoenix (ID:75826)  VIP text: Agency 510', '26 kilometers', 'No', '1104 days', 'display location'], ['Romero (ID:80068)  VIP text: Alexandrescu', '143 kilometers', 'No', '1070 days', 'display location'], ['Fortune (ID:166619)   Formerly ID: 50996', '415 kilometers', 'No', '1000 days', 'display location'], ['Premier (ID:103088)  VIP text: Taxi', '161 kilometers', 'No', '963 days', 'display location'], ['Stretch (ID:108589)  VIP text: TesterAdv', '299 kilometers', 'No', '908 days', 'display location'], ['Huntley (ID:123183)', '0 kilometers', 'No', '837 days', 'display location'], ['Bloodring Banger (ID:123944)', '746 kilometers', 'No', '832 days', 'display location'], ['Roadtrain (ID:187391)', '1271 kilometers', 'No', '563 days', 'display location'], ['Picador (ID:212281)  VIP text: SILV Rank 2', '11 kilometers', 'No', '519 days', 'display location'], ['Vortex (ID:225291)', '41 kilometers', 'No', '444 days', 'display location'], ['Huntley (ID:235951)', '0 kilometers', 'No', '389 days', 'display location'], ['Huntley (ID:273219)', '0 kilometers', 'No', '211 days', 'display location'], ['Buffalo (ID:287536)', '0 kilometers', 'No', '126 days', 'display location'], ['FCR-900 (ID:290093)', '0 kilometers', 'No', '95 days', 'display location'], ['ZR-350 (ID:290577)  VIP text: NULL', '0 kilometers', 'No', '92 days', 'display location'], ['Phoenix (ID:290596)', '0 kilometers', 'No', '92 days', 'display location'], ['Infernus (ID:295078)', '0 kilometers', 'No', '67 days', 'display location']]
    return car_list

async def vstats(inter, player):
    with requests.Session() as s:
        lista_valori_scrape = [
            {'div': {'class': 'col-md-8'}},
            {'h3': {'class': 'profile-username'}}
        ]
        url = f"https://rubypanel.nephrite.ro/profile/{player}"

        f2, user_name_panou, soup = scrape_panou(s, url, lista_valori_scrape, True)
        f2 = soup.findAll('div', {'class': 'col-md-8'})

        car_list = await extract_cars(f2)
        
        # with open("debug_cars.txt", "w+") as f:
        #     f.write(str(car_list))        
        # car_list = [['Infernus (ID:5621)  VIP text: John', '27502 kilometers', 'Blue', '1568 days', 'display location'], ['Intruder (ID:7021)', '2043 kilometers', 'No', '1556 days', 'display location'], ['Sandking (ID:9803)', '8997 kilometers', 'No', '1534 days', 'display location'], ['Comet (ID:14739)', '435 kilometers', 'No', '1507 days', 'display location'], ['NRG-500 (ID:19621)', '24400 kilometers', 'No', '1475 days', 'display location'], ['Bike (ID:19825)', '4 kilometers', 'No', '1474 days', 'display location'], ['Sultan (ID:25697)  VIP text: LiderAdv', '8853 kilometers', 'Green', '1439 days', 'display location'], ['Alpha (ID:29007)', '24 kilometers', 'No', '1418 days', 'display location'], ['Phoenix (ID:75826)  VIP text: Agency 510', '26 kilometers', 'No', '1104 days', 'display location'], ['Romero (ID:80068)  VIP text: Alexandrescu', '143 kilometers', 'No', '1070 days', 'display location'], ['Fortune (ID:166619)   Formerly ID: 50996', '415 kilometers', 'No', '1000 days', 'display location'], ['Premier (ID:103088)  VIP text: Taxi', '161 kilometers', 'No', '963 days', 'display location'], ['Stretch (ID:108589)  VIP text: TesterAdv', '299 kilometers', 'No', '908 days', 'display location'], ['Huntley (ID:123183)', '0 kilometers', 'No', '837 days', 'display location'], ['Bloodring Banger (ID:123944)', '746 kilometers', 'No', '832 days', 'display location'], ['Roadtrain (ID:187391)', '1271 kilometers', 'No', '563 days', 'display location'], ['Picador (ID:212281)  VIP text: SILV Rank 2', '11 kilometers', 'No', '519 days', 'display location'], ['Vortex (ID:225291)', '41 kilometers', 'No', '444 days', 'display location'], ['Huntley (ID:235951)', '0 kilometers', 'No', '389 days', 'display location'], ['Huntley (ID:273219)', '0 kilometers', 'No', '211 days', 'display location'], ['Buffalo (ID:287536)', '0 kilometers', 'No', '126 days', 'display location'], ['FCR-900 (ID:290093)', '0 kilometers', 'No', '95 days', 'display location'], ['ZR-350 (ID:290577)  VIP text: NULL', '0 kilometers', 'No', '92 days', 'display location'], ['Phoenix (ID:290596)', '0 kilometers', 'No', '92 days', 'display location'], ['Infernus (ID:295078)', '0 kilometers', 'No', '67 days', 'display location']]
        # DEBUGING

        return car_list

        nickname_player, player_online, server_de_provenienta = este_player_online(
            str(user_name_panou), player)

        embed = discord.Embed(
            title=nickname_player, description="Status: " + player_online, color=0x00ff00)
        if server_de_provenienta == "ruby":
            embed.set_thumbnail(
                url="https://i.imgur.com/mZvN9jZ.png")
        else:
            embed.set_thumbnail(
                url="https://i.imgur.com/jnTomOg.png")

        


async def extract_cars(f2):
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

        for i in lista_de_trimis:
            print(i)
        return lista_de_trimis