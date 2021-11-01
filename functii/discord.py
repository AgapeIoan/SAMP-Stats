import json
import disnake

import panou.ruby

def disable_not_working_buttons(view, soup):
    if not panou.ruby.vstats(soup):
        disable_button(view.children[1])
    if not panou.ruby.bstats(soup):
        disable_button(view.children[2])
    if not panou.ruby.fhstats(soup):
        disable_button(view.children[3])

    return view

def disable_button(buton_fain):
    buton_fain.disabled = True
    buton_fain.style = disnake.ButtonStyle.gray

def enable_buttons(self):
    if len(self.children) > 5:
        self.remove_item(self.children[5])
    for i in self.children:
        if i.style != disnake.ButtonStyle.gray:
            i.disabled = False


# DEFAULT_PREFIX = config["prefix"][0]

def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    try:
        return prefixes[str(message.guild.id)]
    except AttributeError:  # E canal de DM
        return DEFAULT_PREFIX
    except KeyError: # NU GASIM GUILD IN CONFIG DE PREFIXES
        add_prefix(message.guild.id, DEFAULT_PREFIX)
        return DEFAULT_PREFIX

def add_prefix(guild, prefix):
    guild = str(guild)

    with open('prefixes.json', "r") as f:
        prefixes = json.load(f) # Luam lista de prefixe
    
    prefixes[guild] = [prefix] # Punem prefix

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4) # Salvam lista prefixe

def prefix_remove_guild(guild): # Scoatem guild din config-ul cu prefixe | Usecase cand bot-ul e scos dintr-un guild
    with open('prefixes.json', "r") as f:
        prefixes = json.load(f)
    
    prefixes[str(guild.id)].pop() # Scoatem din db cu prefixe

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)

def remove_prefix(guild, prefix):
    with open('prefixes.json', "r") as f:
        prefixes = json.load(f)

    try:
        prefixes[guild].remove(prefix)
    except ValueError:
        return None  # Prefixul pasat nu se afla in lista guild-ului

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)
        return prefix  # Functia a fost executata cu succes! (adica nu s-a oprit la return-ul cu ValueError)
        # Puteam da return la True, dar imo e mai useful sa dau return la prefix, poate il voi folosi la ceva idk
