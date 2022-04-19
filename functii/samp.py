import json
import disnake

with open("storage/vehicles/vehicles_urls.json") as f:
    VEHICLE_IMAGES = json.load(f)
with open("storage/vehicles/vehicle_categories.json") as f:
    VEHICLE_CATEGORIES = json.load(f)
with open("storage/vehicles/vehicle_emojis.json", encoding='utf-8') as f:
    VEHICLE_EMOJIS = json.load(f)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 | https://discord.gg/bmfRfePXm7"
}

def get_car_image_link(car_name):
    # car_name = "Picador (ID:212281)"
    car_name = car_name[:car_name.find('(ID:')]
    car_name = car_name.strip()

    for car in VEHICLE_IMAGES:
        if car_name.lower() == car.lower():
            return VEHICLE_IMAGES[car]
    return None

def get_car_category(car_name):
    car_name = car_name[:car_name.find('(ID:')]
    car_name = car_name.strip()
    # print_debug(car_name)

    for k, v in VEHICLE_CATEGORIES.items():
        if car_name in v:
            return k
    return None

def get_car_emoji_by_category(category):
    return VEHICLE_EMOJIS[category]

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
    if not image:
        image = "https://cdn.discordapp.com/attachments/921323525359407115/921748251684798514/POZA_EROARE_SAMP.png"
    embed.set_thumbnail(url=image)
    embed.add_field(name=car_stats[0], value=formated_car_stats, inline=False)

    embed.set_footer(text=f"{nickname} | ruby.nephrite.ro")

    return embed

def create_biz_embed(biz_stats, nickname):
    embed=disnake.Embed(color=0x00ff00)
    formated_biz_stats = ''

    # O sa parcurgem o singura data
    # print("BIZ_STATS", biz_stats)
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
        vip_text = car_data[0][car_data[0].find("VIP text:"):]
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
