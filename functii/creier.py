from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 | https://discord.gg/bmfRfePXm7"
}
login_data = {
    "_token": "",
    "login_username": "***REMOVED***",
    "login_password": "***REMOVED***",
    "user_identifier": "***REMOVED***"
}

def login_panou(s):
    url = "https://rubypanel.nephrite.ro/login"
    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features='html5lib')
    login_data['_token'] = soup.find('input', attrs={'name': '_token'})['value']
    r = s.post(url, data=login_data, headers=headers)

    return r

def scrape_panou(s, url, datas, supa=False):
    scrapped = []

    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, features='html5lib')

    for dictionar in datas:
        dictionar = dict(dictionar)
        for k, v in dictionar.items():
            datele_mele = soup.find_all(k, v)
            scrapped.append(datele_mele)

    # if len(scrapped) == 1:
    #    scrapped = scrapped[0] # Sa nu pasam din greseala lista in loc de element

    if supa:
        scrapped.append(soup)

    return scrapped

def este_player_online(username, player):
    ussr = username
    while True:
        if '<i class="fa fa-circle text-success"></i>' in ussr:
            player_online_str = "online"
        else:
            player_online_str = "offline"
        lungime_nickname_player = len(player)
        if 'data-original-title' in ussr:
            capat_lungime_nickname_player = -12
            server_de_provenienta = 'jade'
        else:
            capat_lungime_nickname_player = -7
            server_de_provenienta = 'ruby'
        lungime_nickname_player = -lungime_nickname_player + capat_lungime_nickname_player
        nickname_player = ussr[lungime_nickname_player:capat_lungime_nickname_player]
        break
    return nickname_player, player_online_str, server_de_provenienta

def get_nickname(soup):
    f3 = soup.findAll('h3', {'class': 'profile-username'})
    nickname_ruby = f3[0].findAll('i', {'class': 'fa fa-circle text-danger'}) or f3[0].findAll('i', {'class': 'fa fa-circle text-success'})
    nickname_ruby = nickname_ruby[0].nextSibling.strip()

    return nickname_ruby or f3[0].findAll('a', {'data-toggle': 'tooltip'})[0].text # or nickname_jade
    # Puteam salva nickname_jade intr-o variabila si sa compar 2 variabile frumos la return insaaa
    # nickname_ruby va fi mereu gasit, nickname jade o sa dea IndexError si trebuie obligatoriu inca o conditie
    # sau un try except si ar fi fost mai spachetti cod-ul in caz ca mergeam pe ruta asta
    # As fi putut scapa si de nickname_ruby insa deja era prea lung return-ul


def get_player_id(soup):
    str_sursa = 'https://rubypanel.nephrite.ro/userbar/type/1/user'
    f2 = soup.findAll('img')

    for i in f2:
        if str_sursa in i['src']:
            return i['src'][50:]  # Player id