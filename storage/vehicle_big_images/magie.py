import requests
import json

from bs4 import BeautifulSoup
from imgurpython import ImgurClient

# link = "https://rubypanel.nephrite.ro/images/vehicles/Vehicle_400.jpg"

def dump_to_json(dict):
    with open("../vehicles.json", "w") as f:
        json.dump(dict, f, indent=4)

def not_main():
    link = "https://rubypanel.nephrite.ro/images/vehicles/"

    vehicleIds = [400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415,
        416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433,
        434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451,
        452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469,
        470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487,
        488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505,
        506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523,
        524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541,
        542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559,
        560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577,
        578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595,
        596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    }

    with requests.Session() as s:
        for id in vehicleIds:
            url = link + "Vehicle_" + str(id) + ".jpg"
            print(url)
            r = s.get(url, headers=headers)
            with open(str(id) + ".jpg", "wb") as f:
                f.write(r.content)


def not_main2():
    link = "http://weedarr.wikidot.com/veh"

    lista_ids = []
    lista_vehs = []
    vehs_dict = {}

    with requests.Session() as s:
        r = s.get(link)
        soup = BeautifulSoup(r.content, "html.parser")

        f2 = soup.findAll('table', {'class': 'wiki-content-table'})

        for f in f2:
            x = f.findAll('tr')
            vehs = x[0].findAll('td')
            ids = x[1].findAll('td')

            for i in vehs:
                lista_vehs.append(i.text)
            for i in ids:
                lista_ids.append(i.text)

        for i in range(len(lista_ids)):
            vehs_dict[lista_ids[i]] = lista_vehs[i]
        
        dump_to_json(vehs_dict)

def skema_imgur(headers):

    url = "https://imgur.com/a/LwCwKA4"

    with requests.Session() as s:
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        f2 = soup.findAll('div', {'class': 'PostContent-imageWrapper-rounded'})

        print(soup)

        for f in f2:
            x = f.findAll('img')
            print(x[0]['src'])
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
}
skema_imgur(headers=headers)