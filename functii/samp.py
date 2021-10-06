import json
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