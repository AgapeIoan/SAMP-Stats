import platform
import os
import pickle
import time
import requests
import aiohttp
from bs4 import BeautifulSoup

from functii.debug import print_debug
from functii.bools import LOGIN_USERNAME, LOGIN_PASSWORD, USER_IDENTIFIER, USER_TOKEN

headers = {
    # "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 | https://discord.gg/bmfRfePXm7"
    "user-agent": "Mozilla/5.0 (https://discord.gg/bmfRfePXm7; CPU SAMP_Stats_Rewrite d.py_2.0 ) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/618076658678628383 Safari/537.36 "
}
login_data = {
    "_token": USER_TOKEN,
    "login_username": LOGIN_USERNAME,
    "login_password": LOGIN_PASSWORD,
    "user_identifier": USER_IDENTIFIER
}

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    stat = os.stat(path_to_file)
    try:
        return stat.st_birthtime
    except AttributeError:
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
        cookies = pickle.load(f)
    session.cookie_jar.update_cookies(cookies) # ONLY AIOHTTP, NOT REQUESTS

def login_panou_forced(s):
    url = "https://rubypanel.nephrite.ro/login"
    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features='html5lib')
    login_data['_token'] = soup.find('input', attrs={'name': '_token'})['value']
    print_debug("Logging in...")
    print_debug(f"Login data: {login_data}")
    print_debug(f"Headers: {headers}")
    r = s.post(url, data=login_data, headers=headers)

    return r

async def login_panou(session, forced_login=False):
    unix_modification = os.path.getmtime("session.pkl")
    if time.time() - unix_modification > 250000 or forced_login: # ~3 days
        with requests.Session() as s:
            url = "https://rubypanel.nephrite.ro/login"
            r = s.get(url, headers=headers)
            soup = BeautifulSoup(r.content, features='html5lib')
            login_data['_token'] = soup.find('input', attrs={'name': '_token'})['value']
            print_debug("Logging in...")
            print_debug(f"Login data: {login_data}")
            print_debug(f"Headers: {headers}")
            r = s.post(url, data=login_data, headers=headers)
            dump_session_to_file(s, "session.pkl")
            load_session_from_file(session, "session.pkl")
    else:
        print_debug("Session still valid. No need to login.")
        load_session_from_file(session, "session.pkl")
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

def get_server_provenienta(soup):
    f3 = soup.findAll('h3', {'class': 'profile-username'})
    provenienta = f3[0].findAll('a')
    if provenienta:
        return "jade"
    return "ruby"


def get_player_id(soup):
    str_sursa = 'https://rubypanel.nephrite.ro/userbar/type/1/user'
    f2 = soup.findAll('img')

    for i in f2:
        if str_sursa in i['src']:
            return i['src'][50:]  # Player id

async def get_soup(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return BeautifulSoup(await response.read(), features='html5lib')

def color_by_list_lenght(list_1, list_2):
    if len(list_2) > len(list_1):
        list_1, list_2 = list_2, list_1

    if len(list_2) == 0:
        return 0xff2d00
    if len(list_2) == len(list_1):
        return 0x50ff00
    else:
        return 0xff8e00

def sum_list_indexes(list_of_lists, index_to_stop):
    first_element = 0
    for i in range(0,index_to_stop):
        first_element += len(list_of_lists[i])
    return first_element
