import json
import os

storage = 'storage/'

with open(storage + 'factions/factiuni.json', 'r') as f:
    LISTA_FACTIUNI = json.load(f)

with open(storage + 'factions/faction_categories.json', 'r', encoding='utf-8') as f:
    LISTA_FACTIUNI_CATEGORIES = list(json.load(f).keys())

status_aplicatii_factiuni = []
for i in range(27):
    status_aplicatii_factiuni.append(0) # Init status ca empty list

# {
#     "factiune" : [
#     "Los Santos Police Department",
# "Federal Bureau of Investigation",
# "National Guard",
# "Los Aztecas",
# "Grove Street",
# "Crips Gang",
# "Taxi Las Venturas",
# "Las Venturas Police Department",
# "News Reporters",
# "Ballas",
# "Hitman",
# "School Instructors LV",
# "Taxi Los Santos",
# "Paramedic Department LV",
# "Red Dragon Triads",
# "The Russian Mafia",
# "Taxi San Fierro",
# "San Fierro Police Department",
# "Paramedic Department LS",
# "San Fierro Rifa",
# "The Italian Mafia",
# "School Instructors SF",
# "Da Nang Boys",
# "Tow Car Company LS",
# "Tow Car Company LV",
# "Paramedic Department SF"]
# }