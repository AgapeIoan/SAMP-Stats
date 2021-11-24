from functii.creier import get_nickname
import json
import disnake
import asyncio

from disnake import ActionRow, Button, ButtonStyle, SelectMenu, SelectOption, Option, OptionType
from disnake import emoji
from disnake.ext import commands

import panou.ruby
import clase_menus
from functii.discord import disable_button, disable_not_working_buttons
from functii.debug import print_debug

with open("config.json", "r") as f:
    config = json.load(f)

test_guilds = [722442573137969174]
BOT_TOKEN = config["BOT_TOKEN"]
POZA_MASINA_SAMP = "https://i.imgur.com/KC9rlJd.png"

bot = commands.Bot(command_prefix="!", test_guilds = [722442573137969174])
# If 'test_guilds' param isn't specified, the commands are registered globally.
# Global registration takes up to 1 hour.



@bot.slash_command()
async def ping(inter):
    await inter.response.send_message('pong')

@bot.slash_command(
    name="stats", # Defaults to the function name
    description="butoane",
    guild_ids=test_guilds,
    options=[
        Option("nickname", "Introdu nickname-ul", OptionType.string, required=True)
        # By default, Option is optional
        # Pass required=True to make it a required arg
    ]
)
async def stats(inter, nickname):
    await inter.response.defer()

    try:
        soup = panou.ruby.get_panel_data(nickname)
    except IndexError:
        # TODO #3 Sa isi dea seama bot-ul daca e vorba de panel picat, pagina blank, lipsa profil sau orice altceva se poate intampla
        # si sa afiseze un mesaj de eroare corespunzator
        await inter.edit_original_message(f"Jucatorul **{nickname}** nu a fost gasit. Verifica daca ai introdus corect nickname-ul!")
        return

    view = disable_not_working_buttons(clase_menus.Main_Menu(soup), soup)
    
    await inter.edit_original_message(content=f"**`debug` Selecteaza o optiune pentru jucatorul `{get_nickname(soup)}`:**", view=view)

@bot.slash_command(
    name="clans", # Defaults to the function name
    description="Afiseaza lista de clanuri",
    guild_ids=test_guilds,
    options=[
        Option("param", "debug", OptionType.string, required=False)
        # By default, Option is optional
        # Pass required=True to make it a required arg
    ]
)
async def clans(inter, param = None):
    await inter.response.defer()

    view = clase_menus.Clans_Menu_View(nr_pagina=1)

    await inter.edit_original_message(content=f"**CLANS**", view=view)
 


@bot.listen()
async def on_ready():
    print_debug("Ne-am conectat cu succes!")
    print_debug(f"{bot.user}")
    print_debug(f"Servers: {len(bot.guilds)}")
    print_debug(f"Latency: {bot.latency}")
    print_debug(f"Status: {bot.status}")
    
print_debug(f"Ne logam...")
# TODO #4 Fac ceva event on_ready() sa anunte ca so logat botu
bot.run(BOT_TOKEN)
    