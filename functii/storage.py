import json
import os

storage = 'storage/'

with open(storage + 'factions/factiuni.json', 'r') as f:
    LISTA_FACTIUNI = json.load(f)

with open(storage + 'factions/faction_categories.json', 'r', encoding='utf-8') as f:
    LISTA_FACTIUNI_CATEGORIES = list(json.load(f).keys())

with open(storage + 'vehicles/vehicle_custom_emojis.json', 'r', encoding='utf-8') as f:
    DICT_EMOJIS_CUSTOM_VEHICLES = json.load(f)

status_aplicatii_factiuni = []
clan_dict = {}