import json
import disnake

from bs4 import BeautifulSoup

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

    formated_car_stats+=f"{car_stats[1]}\n{car_stats[3]}\n"
    if car_stats[2] != "No":
        # Avem neon
        formated_car_stats+=f"Neon: {car_stats[2]}"

    embed.set_thumbnail(url="https://i.imgur.com/KC9rlJd.png")
    embed.add_field(name=car_stats[0], value=formated_car_stats, inline=False)

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
