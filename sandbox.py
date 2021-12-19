import requests
import pickle
import datetime
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0"
    # "user-agent": "Mozilla/5.0 (https://discord.gg/bmfRfePXm7; CPU SAMP_Stats_Rewrite d.py_2.0 ) "
    #               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/618076658678628383 Safari/537.36 "
}
login_data = {
    "_token": "***REMOVED***",
    "login_username": "***REMOVED***",
    "login_password": "***REMOVED***",
    "user_identifier": "***REMOVED***"
}


def print_debug(output):
    print(f"{datetime.datetime.now()} | {output}")


def login_panou(s):
    url = "https://rubypanel.nephrite.ro/login"
    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features='html5lib')
    login_data['_token'] = soup.find('input', attrs={'name': '_token'})['value']
    print_debug(f"Logging in...")
    print_debug(f"Login data: {login_data}")
    print_debug(f"Headers: {headers}")
    r = s.post(url, data=login_data, headers=headers)

    return r


def dump_to_file(session, filename):
    with open(filename, 'wb') as f:
        pickle.dump(session.cookies, f)


def load_from_file(session, filename):
    with open(filename, 'rb') as f:
        session.cookies.update(pickle.load(f))


def get_panel_data(s, player):

    url = f'http://rubypanel.nephrite.ro/profile/{player}'
    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features='html5lib')

    f2 = soup.findAll('div', {'class': 'tab-pane'})

    data = [
        [td.text for td in tr.find_all('td')]
        for table in [f2[0]] for tr in table.find_all('tr')
    ]

    for i in data:
        print_debug(i)


def get_clan_data_by_id(s, clan_id, pozitie):
    print_debug(f"Getting clan data for clan {clan_id}...")
    cols = {
        "left": {'class': 'col-xs-3'},
        "middle": {'class': 'col-xs-5'},
        "right": {'class': 'col-xs-4'}
    }

    if pozitie not in cols.keys():
        raise ValueError(f"Pozitie invalida: {pozitie}")

    url = 'https://rubypanel.nephrite.ro/clan/view/' + str(clan_id)
    print_debug(f"Getting clan data from {url}...")
    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features='html5lib')
    print_debug("Got clan data.")
    f2 = soup.findAll('div', cols[pozitie])
    data = [
        [td.text for td in tr.find_all('td')]
        for table in f2 for tr in table.find_all('tr')
    ]

    print_debug(f"Clan data loaded.")
    print(data)

if __name__ == '__main__':
    with requests.Session() as s:
        load_from_file(s, 'session.pkl')
        print_debug("Loaded from file!")
        print_debug("Getting data...")
        get_panel_data(s, '***REMOVED***')
        print_debug("Got data!")

