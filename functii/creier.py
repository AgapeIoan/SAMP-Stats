import platform
import os
import pickle
import datetime
import time
from bs4 import BeautifulSoup

from functii.debug import print_debug

headers = {
    # "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 | https://discord.gg/bmfRfePXm7"
    "user-agent": "Mozilla/5.0 (https://discord.gg/bmfRfePXm7; CPU SAMP_Stats_Rewrite d.py_2.0 ) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/618076658678628383 Safari/537.36 "
}
login_data = {
    "_token": "",
    "login_username": "***REMOVED***",
    "login_password": "***REMOVED***",
    "user_identifier": "***REMOVED***"
}

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def get_profile_data(soup, f2_index: int):
    # 0 | stats 
    # 1 | clothes 
    # 2 | missions 
    # 3 | badges 
    # 4 | cars 
    # 5 | proprietes 
    # 6 | referral 
    # 7 | fh 
    # 8, 9, 10 | semnatura forum
    f2 = soup.findAll('div', {'class': 'tab-pane'}, {'id': 'properties'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in [f2[f2_index]] for tr in table.find_all('tr')
    ]

    return data


def dump_session_to_file(session, filename):
    with open(filename, 'wb') as f:
        pickle.dump(session.cookies, f)


def load_session_from_file(session, filename):
    with open(filename, 'rb') as f:
        session.cookies.update(pickle.load(f))


async def login_panou(s):
    unix_modification = os.path.getmtime("session.pkl")
    if time.time() - unix_modification > 250000: # ~3 days
        print_debug("Session expired, logging in again")
        url = "https://rubypanel.nephrite.ro/login"
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.content, features='html5lib')
        login_data['_token'] = soup.find('input', attrs={'name': '_token'})['value']
        r = s.post(url, data=login_data, headers=headers)
        dump_session_to_file(s, "session.pkl")
        return r
    else:
        print_debug("Session still valid. No need to login.")
        load_session_from_file(s, "session.pkl")
        return "1337" # Normal ar fi trebuit sa primim 200, asa ca nu primim nimic punem si noi ceva sa fie acolo


def scrape_panou(soup, datas):
    scrapped = []

    for dictionar in datas:
        dictionar = dict(dictionar)
        for k, v in dictionar.items():
            datele_mele = soup.find_all(k, v)
            scrapped.append(datele_mele)

    return scrapped

def este_player_online(soup):
    f3 = soup.findAll('h3', {'class': 'profile-username'})
    return f3[0].findAll('i')[0]['class'][2] != "text-danger"
    # Aflam daca e player online/offline | True/False

def get_nickname(soup):
    f3 = soup.findAll('h3', {'class': 'profile-username'})
    nickname_ruby = f3[0].findAll('i', {'class': 'fa fa-circle text-danger'}) or f3[0].findAll('i', {'class': 'fa fa-circle text-success'})
    nickname_ruby = nickname_ruby[0].nextSibling.strip()

    return nickname_ruby or f3[0].findAll('a', {'data-toggle': 'tooltip'})[0].text.strip() # or nickname_jade
    # Puteam salva nickname_jade intr-o variabila si sa compar 2 variabile frumos la return insaaa
    # nickname_ruby va fi mereu gasit, nickname jade o sa dea IndexError si trebuie obligatoriu inca o conditie
    # sau un try except si ar fi fost mai spachetti cod-ul in caz ca mergeam pe ruta asta
    # As fi putut scapa si de nickname_ruby insa deja era prea lung return-ul

def get_server_provenienta(soup):
    f3 = soup.findAll('h3', {'class': 'profile-username'})
    provenienta = f3[0].findAll('a')
    if provenienta: 
        return "jade" 
    else: 
        return "ruby"


def get_player_id(soup):
    str_sursa = 'https://rubypanel.nephrite.ro/userbar/type/1/user'
    f2 = soup.findAll('img')

    for i in f2:
        if str_sursa in i['src']:
            return i['src'][50:]  # Player id
