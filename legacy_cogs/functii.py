import json
import requests
import discord

from aiofile import AIOFile
from bs4 import BeautifulSoup
from discord.ext import commands
from utils import default

#############
global numar_de_generari, id_server_home

strToReplaceList = ['</div>', """<div id="clanDescriptionText">""", '<li>', '<em>', '<p>', '</p>', '<ol>', '</ol>',
                    '<strong>', '</strong>', '</em>', '</li>', '</a>', '<a>', '<a href="', '">', '<br/>', "<ul>", "</ul>"]
numar_de_generari = 'none'
id_server_home = 722442573137969174

global este_player_online, dam_atac_in_panou, scriem_fisiere, numar_de_generari_plus, salvam_codul_sursa, \
    bagamBotiInPanou, scoateCifrelem, login_panou, get_nickname, chunks, este_mentenanta, cauta_clan, \
    empty_is_none


##################################################################################################
with open(f"./DateDeLogare.txt", "r+") as login:
    username = login.readline()
    parola = login.readline()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 | https://discord.gg/cuPkQbS"
}

login_data = {
    "_token": "",
    "login_username": username,
    "login_password": parola,
    "user_identifier": "***REMOVED***"
}

##################################################################################################
def empty_is_none(cuvant):
    try:
        if not cuvant:
            cuvant = "none"
    except IndexError:
        cuvant = "none"
    return cuvant

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
        clanname = str(clan[1])
        clantag = str(clan[2])
        # clanslots = str(clan[3])
        # clanrip = str(clan[4]) # Zile pana cand expira

        if clanid not in clanidlist:  # In caz ca dam de ceva nou, bagam in lista
            clanidlist.append(clanid)
            clannamelist.append(clanname)
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
        index = index_tag
    elif gasit_nume:  # Si din conditia anterioara nu avem *gasit_tag*
        index = index_nume
    else:
        index = None

    return index


def chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start + n]


def get_nickname(soup, player):
    f3 = soup.findAll('h3', {'class': 'profile-username'})
    f3 = str(f3)

    if "</i> <a data-original-title=" in f3:
        temp = -12 - len(player)
        nickname_player = f3[temp:-12]
    else:
        temp = -7 - len(player)
        nickname_player = f3[temp:-7]

    return nickname_player


def login_panou(s):
    url = "https://rubypanel.nephrite.ro/login"
    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features='html5lib')
    login_data['_token'] = soup.find('input', attrs={'name': '_token'})['value']
    r = s.post(url, data=login_data, headers=headers)

    return r


def deprecacy_notify(ctx):
    # Creates the message that notifies the user that the command will be deprecated soon
    # also, it will be sent to the channel where the command was executed and
    # informs about the new command

    gif_to_send = "https://img.agapeioan.ro/SAMP-Stats-Slash-Command-v1.gif"

    embed = discord.Embed(title=f"Comanda {ctx.command.name} va fi dezactivata de la 1 septembrie.\n", 
                            description=f"Alternativa noua este comanda slash `</stats:923741848873345074>`, ce combina multiple comenzi intr-una singura.\nDaca comanda slash nu apare, un administrator trebuie sa foloseasca butonul **Add to Server** de pe profilul de discord al bot-ului.",
                            color=0x00ff00)
    embed.set_image(url=gif_to_send)

    return embed

def scoate_cifrele(cuvant):
    cuvantnou = ""

    for i in cuvant:
        if i.isnumeric():
            cuvantnou += i
        else:
            break

    return cuvantnou


def este_mentenanta():
    with open("mentenanta.txt", "r+") as meen:
        skema = meen.readline()
        if "da" in skema.lower():
            motiv = meen.readline()  # Urmatorul rand, a nu se confunda cu randul pe care scrie "da"
            # print(motiv)
            return motiv
        else:
            return False


def salvam_codul_sursa(cod_intreg):  # merge doar cu atacul in panou efectuat corect
    skemaaa = open('logs ruby/html_debug' + numar_de_generari +
                   '.txt', 'w+', encoding="utf-8")
    skemaaa.write(str(cod_intreg))


def este_player_online(username, player):
    while True:
        ussr = username
        if '<i class="fa fa-circle text-success"></i>' in ussr:
            player_online_str = "online"
        else:
            player_online_str = "offline"
        lungime_nickname_player = len(player)
        if 'data-original-title' in ussr:
            capat_lungime_nickname_player = -12
            lungime_nickname_player = -lungime_nickname_player + capat_lungime_nickname_player
            server_de_provenienta = 'jade'
        else:
            capat_lungime_nickname_player = -7
            lungime_nickname_player = -lungime_nickname_player + capat_lungime_nickname_player
            server_de_provenienta = 'ruby'
        nickname_player = ussr[lungime_nickname_player:capat_lungime_nickname_player]
        break
    return nickname_player, player_online_str, server_de_provenienta

def numar_de_generari_plus():
    # cream o variabila cu numarul de stats cerute/generate si o salvam intr-un fisier text.
    fisiertxt_numar_de_generari = open(
        'logs ruby/NumarDeGenerariStats.txt', 'r+')
    global numar_de_generari
    # citim nr generari din fisier txt
    numar_de_generari = int(fisiertxt_numar_de_generari.readline())
    fisiertxt_numar_de_generari.close()

    numar_de_generari = numar_de_generari + 1  # marim nr de generari
    # il schimbam in string ca sa poata fi scris ulterior in fisier txt
    numar_de_generari = str(numar_de_generari)

    fisiertxt_numar_de_generari = open(
        'logs ruby/NumarDeGenerariStats.txt', "w+", encoding="utf-8")
    # actualizam fisier txt cu noul nr de generari
    fisiertxt_numar_de_generari.write(numar_de_generari)
    fisiertxt_numar_de_generari.close()

def scrape_panou(s, url, datas, supa=False):
    scrapped = []

    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features='html5lib')

    for dictionar in datas:
        dictionar = dict(dictionar)
        for k, v in dictionar.items():
            datele_mele = soup.find_all(k, v)
            scrapped.append(datele_mele)

    #if len(scrapped) == 1:
    #    scrapped = scrapped[0] # Sa nu pasam din greseala lista in loc de element

    if supa:
        scrapped.append(soup)
        return scrapped
    else:
        return scrapped

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
