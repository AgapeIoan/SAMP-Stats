import os
import requests
import disnake
import time
from disnake import Option, OptionType
from disnake.ext import commands

import views.mainmenu
import views.factions_menu
import panou.ruby.ruby

from functii.creier import get_nickname
from functii.debug import DEBUG_STATE, print_debug, send_error_message_to_error_channel, print_log
from functii.discord import disable_not_working_buttons
from functii.bools import BOT_TOKEN
from typing import List

# If 'test_guilds' param isn't specified, the commands are registered globally.
# Global registration takes up to 1 hour.

bot = commands.Bot(command_prefix=commands.when_mentioned)

@bot.slash_command(
    name="ping",
    description="Pings the bot.",
)
async def ping(inter):
    za_ping = round(bot.latency * 1000)
    await inter.response.send_message(f'**Pong!**\n🏓 {za_ping} ms')
    await send_error_message_to_error_channel(bot, f"{inter.author.name}#{inter.author.discriminator} pinged the bot \\w " + str(za_ping) + "ms.")


@bot.slash_command(
    name="stats",  # Defaults to the function name
    description="Afiseaza statisticile jucatorului specificat",
    options=[
        Option("nickname", "Introdu nickname-ul", OptionType.string, required=True)
    ]
)
async def stats(inter, nickname):
    try:
        await inter.response.defer()
    except disnake.errors.NotFound:
        pass

    try:
        print_debug(f"Getting za data for {nickname}")
        soup = await panou.ruby.ruby.get_panel_data(nickname)
    except IndexError:
        # TODO #3 Sa isi dea seama bot-ul daca e vorba de panel picat, pagina blank, lipsa profil sau orice altceva se poate intampla
        # si sa afiseze un mesaj de eroare corespunzator
        await inter.edit_original_message(
            content=f"Jucatorul **{nickname}** nu a fost gasit. Verifica daca ai introdus corect nickname-ul!")
        return

    view = await disable_not_working_buttons(views.mainmenu.MainMenu(soup), soup)
    view.original_author = inter.author
    view.bot = bot

    view.message = await inter.edit_original_message(
        content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(soup)}`:**", view=view)

@bot.listen()
async def on_ready():
    print_log("Ne-am conectat cu succes!")
    print_log(f"{bot.user}")
    print_log(f"Servers: {len(bot.guilds)}")
    print_log(f"Latency: {bot.latency}")
    print_log(f"Status: {bot.status}")
    print_log(f"")


# Proces de boot
print_log("Ne logam...\n")
if not DEBUG_STATE:
    print_log("DEBUG_STATE is False, urmeaza sa folosesti token-ul de productie!")
    print_log("Daca nu doresti sa folosesti token-ul de productie, trebuie sa modifici debug_state-ul!\n")
    for i in range(3):
        print_log("Bot-ul va porni in " + str(3*5 - i*5) + " secunde.")
        time.sleep(5)

# Initiam stuff
from functii.storage import status_aplicatii_factiuni
for i in range(27):
    status_aplicatii_factiuni.append(0) # Init status ca empty list

# load cog
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")
        print_log(f"Incarcat cogs.{name}!")

bot.run(BOT_TOKEN)
