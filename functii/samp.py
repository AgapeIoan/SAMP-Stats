from functii.debug import print_debug
import json
import disnake
import datetime

from bs4 import BeautifulSoup
from disnake.channel import _guild_channel_factory

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 | https://discord.gg/bmfRfePXm7"
}

def save_json_users(dict_clan):
    with open("Users.json", "w+", encoding='utf-8') as clanurilista:
        json.dump(dict_clan, clanurilista, indent=4)  # Salvam json

def salveaza_lista_clanuri(dict_clan):
    with open("clans.json", "w+", encoding='utf-8') as clanurilista:
        json.dump(dict_clan, clanurilista, indent=4)  # Salvam json


def deschide_lista_clanuri():
    with open("clans.json", "r+", encoding='utf-8') as clanurilista:
        dict_clan = json.load(clanurilista)
        clanidlist = dict_clan.get("clanid")
        clannamelist = dict_clan.get("clanname")
        clantaglist = dict_clan.get("clantag")
    return dict_clan, clanidlist, clannamelist, clantaglist


def actualizeaza_lista_clanuri(s):
    dict_clan, clanidlist, clannamelist, clantaglist = deschide_lista_clanuri()

    url = "https://rubypanel.nephrite.ro/clan/list"
    # FACEM LISTA DE CLANURI, LE PUNEM DUPA INTR-UN JSON CARE IL ACTUALIZAM REGULAT
    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    f2 = soup.findAll('table', {'class': 'table table-condensed table-hover'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in f2 for tr in table.find_all('tr')
    ]

    # Iteram prin lista de clans & date
    for clan in data[1:]:  # Am pus interval [1:] ca sa sara peste data[0] aka variabila goala.
        clanid = str(clan[0])
        # clanslots = str(clan[3])
        # clanrip = str(clan[4]) # Zile pana cand expira

        if clanid not in clanidlist:  # In caz ca dam de ceva nou, bagam in lista
            clanidlist.append(clanid)
            clanname = str(clan[1])
            clannamelist.append(clanname)
            clantag = str(clan[2])
            clantaglist.append(clantag)

    salveaza_lista_clanuri(dict_clan)


def cauta_clan(clan_sau_tag):
    dict_clan, clanidlist, clannamelist, clantaglist = deschide_lista_clanuri()

    gasit_tag = False
    gasit_nume = False

    for i in range(len(clannamelist)):
        if clan_sau_tag.lower() in clantaglist[i].lower():  # Avem tag gasit
            gasit_tag = True
            index_tag = i
            break
        elif clan_sau_tag.lower() in clannamelist[i].lower():  # Avem nume gasit
            gasit_nume = True
            index_nume = i
            if gasit_tag:
                break

    if gasit_tag:
        return index_tag
    elif gasit_nume:  # Si din conditia anterioara nu avem *gasit_tag*
        return index_nume
    else:
        return None

def este_asociat(user_id):
    with open("Users.json", "r+", encoding='utf-8') as utilizatori:
        dict_membri = json.load(utilizatori)
        memberlist = dict_membri.get("members")
        idlist = dict_membri.get("ids")
        discordlist = dict_membri.get("discords")  # Citim lista

    if str(user_id) in discordlist:
        index = discordlist.index(str(user_id))
        nickname = memberlist[index]
        player_id = idlist[index]
        return nickname
    else:
        return None

def vezi_asociere(player, ctx):
    if not player:
        player = este_asociat(ctx.author.id)
        if player:
            player = str(player)
    return player

def get_car_image_link(car_name):
    # car_name = "Picador (ID:212281)"
    car_name = car_name[:car_name.find('(ID:')]
    car_name = car_name.strip()

    with open("storage/vehicles_urls.json") as f:
        data = json.load(f)
    for car in data:
        if car_name.lower() == car.lower():
            return data[car]

def create_car_embed(car_stats, nickname):
    embed=disnake.Embed(color=0x00ff00)

    formated_car_stats = ''

    # 'Stretch (ID:128170)   Formerly ID: 47132 VIP text: ksn'
    if "VIP text:" in car_stats[0]:
        # De exemplu, din "Picador (ID:212281)  VIP text: SILV Rank 2"
        # o sa extragem doar "VIP text: SILV Rank 2"
        vip_text = car_stats[0][car_stats[0].find("VIP text: "):]
        formated_car_stats+=vip_text+'\n'
        car_stats[0] = car_stats[0].replace(vip_text, '').strip()

    if "Formerly ID: " in car_stats[0]:
        # 'Fortune (ID:166619)   Formerly ID: 50996'
        # Nu are cum sa faca cineva prank cu Formerly ID in VIP text, ca VIP text-ul se scoate in if-ul de mai sus :creier:
        formerly_id = car_stats[0][car_stats[0].find("Formerly ID: "):]
        formated_car_stats+=formerly_id+'\n'
        car_stats[0] = car_stats[0].replace(formerly_id, '').strip()
        formated_car_stats+=f"{formerly_id}\n"

    formated_car_stats+=f"{car_stats[1]}\n{car_stats[3]}\n"
    if car_stats[2] != "No":
        # Avem neon
        formated_car_stats+=f"Neon: {car_stats[2]}"

    image = get_car_image_link(car_stats[0])
    embed.set_thumbnail(url=image)
    embed.add_field(name=car_stats[0], value=formated_car_stats, inline=False)

    embed.set_footer(text=f"{nickname} | ruby.nephrite.ro")

    return embed

def create_biz_embed(biz_stats, nickname):
    embed=disnake.Embed(color=0x00ff00)
    formated_biz_stats = ''

    # O sa parcurgem o singura data
    print("BIZ_STATS", biz_stats)
    for k, v in biz_stats.items():
        # Putin ciudata treaba asta cu emoji, insa la cum e gandita, emoji ala il trag cand ma joc cu output-ul
        # si dupa il scot din descriere sa fie totul ok

        for i in v[1:]:
            formated_biz_stats += i + '\n'

    embed.add_field(name=v[0], value=formated_biz_stats, inline=False)
    
    # embed.set_thumbnail(url="https://i.imgur.com/KC9rlJd.png")
    # Aici la thumbnail ori facem 3 imagini, mai exact pentru casa, biz si apartament, ori facem imagine cu fiecare biz in-game
    # La poze in-game ar trebui 72 poze cu fiecare business
    # Maxim 3 poze la case cred, desi o poza reprezentativa ar fi suficienta, ca nu sunt nebun sa fac 554 poze pentru fiecare casa din joc
    # Sincer la case cred ca ar merge si locatia pe harta
    # La apartamente e ez, o poza cu blocul de apartamente si ayaye
    # TODO #14
    # !!! Sincer, cred ca embed-ul ar trebui sa fie complementar. Multe detalii sunt deja afisate foarte frumos cum trebuie in lista de optiuni,
    # in embed ar trebui sa fie chestii suplimentare si mult mai complexe. Poate poate o productie (ca la asta s-ar astepta sampistu), o locatie pe harta, o poza cu bizu, o glumita cu sanse random de aparitie acolo.


    embed.set_footer(text=f"{nickname} | ruby.nephrite.ro")

    return embed


def format_car_data(car_data):
    formated_car_data = ''

        # 'Stretch (ID:128170)   Formerly ID: 47132 VIP text: ksn'
    if "VIP text:" in car_data[0]:
        # De exemplu, din "Picador (ID:212281)  VIP text: SILV Rank 2"
        # o sa extragem doar "VIP text: SILV Rank 2"
        vip_text = car_data[0][car_data[0].find("VIP text: "):]
        formated_car_data+=vip_text+' | '
        car_data[0] = car_data[0].replace(vip_text, '').strip()

    if "Formerly ID: " in car_data[0]:
        # 'Fortune (ID:166619)   Formerly ID: 50996'
        # Nu are cum sa faca cineva prank cu Formerly ID in VIP text, ca VIP text-ul se scoate in if-ul de mai sus :creier:
        formerly_id = car_data[0][car_data[0].find("Formerly ID: "):]
        formated_car_data+=formerly_id+' | '
        car_data[0] = car_data[0].replace(formerly_id, '').strip()

    if car_data[2] != "No":
        # Avem neon
        formated_car_data+=f"Neon: {car_data[2]} | "

    formated_car_data+=f"{car_data[1]} | {car_data[3]}"

    return car_data[0], formated_car_data

def format_biz_data(biz_data):
    emoji_list = {
        "house": "🏠",
        "business": "🏢",
        "apartament": "🏨"
    }

    formated_biz_data = ''

    for k, v in biz_data.items():
        formated_biz_data = emoji_list.get(k)
        # Putin ciudata treaba asta cu emoji, insa la cum e gandita, emoji ala il trag cand ma joc cu output-ul
        # si dupa il scot din descriere sa fie totul ok

        for i in v[1:]:
            formated_biz_data += " | " + i

        return v[0], formated_biz_data

def format_faction_history_data(fh):
    menu_text = f"{fh[0][:10]} | {fh[2]}"
    specs = ''
    # print(fh)
    fh[3] = fh[3][0].capitalize() + fh[3][1:]
    if len(fh) == 4:
        # Avem joined sau lider
        specs = "Leader | " + fh[3] if "Promoted" in fh[3] else "Joined | " + fh[3]
    elif len(fh) == 6:
        # Avem left
        specs = "/quitgroup " + fh[5] + " | " + fh[3] + " | " + fh[4]
    else:
        # Avem uninvited
        fh[6] = fh[6][0].capitalize() + fh[6][1:]
        specs = fh[6] + " | " + fh[3] + " | " + fh[4] + " | " + fh[5] + " | Reason: " + fh[7]

    return menu_text, specs

def create_fh_embed(fh_original, nickname):
    embed=disnake.Embed(color=0x00ff00)

    fh = fh_original.copy()

    menu_text = f"{fh[2]}"
    specs = f"Nickname: {fh[1]}\n"
    # TODO: Fiecare factiune sa aiba cate o poza gen logo, hyperlink spre forum maybe?

    fh[3] = fh[3][0].capitalize() + fh[3][1:]
    if len(fh) == 4:
        # Avem joined sau lider
        specs = "Leader\n" + fh[3] if "Promoted" in fh[3] else "Joined\n" + fh[3]
    elif len(fh) == 6:
        # Avem left
        specs = "/quitgroup " + fh[5] + "\n" + fh[3] + "\n" + fh[4]
    else:
        # Avem uninvited
        fh[6] = fh[6][0].capitalize() + fh[6][1:] + " " + fh[5]
        specs = fh[6] + "\n" + fh[3] + "\n" + fh[4] + "\nReason: " + fh[7]

    embed.add_field(name=menu_text, value=specs, inline=False)

    embed.set_footer(text=f"{nickname} | ruby.nephrite.ro  •  {fh[0]}")

    return embed