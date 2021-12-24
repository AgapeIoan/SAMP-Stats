import json
import os

from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import disnake
import asyncio
from disnake import Option, OptionType
from disnake.ext import commands

import mainmenu
import panou.ruby
from functii.creier import get_nickname
from functii.debug import print_debug, send_error_message_to_error_channel, print_log
from functii.discord import disable_not_working_buttons

with open("config.json", "r") as f:
    config = json.load(f)

test_guilds = [722442573137969174, 921316017584631829]
BOT_TOKEN = config["BOT_TOKEN"]

# If 'test_guilds' param isn't specified, the commands are registered globally.
# Global registration takes up to 1 hour.

bot = commands.Bot(command_prefix="!", test_guilds=[722442573137969174, 921316017584631829])


@bot.slash_command(
    name="ping",
    description="Pings the bot.",
)
async def ping(inter):
    za_ping = round(bot.latency * 1000)
    await inter.response.send_message(f'**Pong!**\n🏓 {za_ping} ms')
    await send_error_message_to_error_channel(bot, f"{inter.author.name}#{inter.author.discriminator} pinged the bot \w " + str(za_ping) + "ms.")

@bot.slash_command(
    name="stats",  # Defaults to the function name
    description="Afiseaza statisticile jucatorului specificat",
    guild_ids=test_guilds,
    options=[
        Option("nickname", "Introdu nickname-ul", OptionType.string, required=True)
        # By default, Option is optional
        # Pass required=True to make it a required arg
    ]
)
async def stats(inter, nickname):
    try:
        await inter.response.defer()
    except disnake.errors.NotFound:
        print_debug("DEFER ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # TODO #16 Bug mult prea dubios la response.defer()

    try:
        print_debug(f"Getting za data for {nickname}")
        soup = await panou.ruby.get_panel_data(nickname)
    except IndexError:
        # TODO #3 Sa isi dea seama bot-ul daca e vorba de panel picat, pagina blank, lipsa profil sau orice altceva se poate intampla
        # si sa afiseze un mesaj de eroare corespunzator
        await inter.edit_original_message(
            content=f"Jucatorul **{nickname}** nu a fost gasit. Verifica daca ai introdus corect nickname-ul!")
        return

    view = await disable_not_working_buttons(mainmenu.MainMenu(soup), soup)
    view.original_author = inter.author

    view.message = await inter.edit_original_message(
        content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(soup)}`:**", view=view)


# @bot.slash_command(
#     name="clans", # Defaults to the function name
#     description="Afiseaza lista de clanuri",
#     guild_ids=test_guilds,
#     options=[
#         Option("param", "debug", OptionType.string, required=False)
#         # By default, Option is optional
#         # Pass required=True to make it a required arg
#     ]
# )
# async def clans(inter, param = None):
#     await inter.response.defer()

#     view = clase_menus.Clans_Menu_View(nr_pagina=1)

#     await inter.edit_original_message(content=f"**CLANS**", view=view)

# # TODO #19 Fix comanda raportu
# @bot.slash_command(
#     name="raportu", # Defaults to the function name
#     description="Afiseaza lista de servere samp",
#     guild_ids=test_guilds,
#     options=[
#         Option("server", "Specifica adresa server", OptionType.string, required=False)
#         # By default, Option is optional
#         # Pass required=True to make it a required arg
#     ]
# )
# async def raportu(inter, server = None):
#     await inter.response.defer()

#     embed = disnake.Embed(title="SAMP Servers", color=0x00ff00)
#     with open("storage\\servers_dns.json", "r") as f:
#         servers = json.load(f)

#     if server:
#         for i in servers:
#             if server in i: # Vedem daca avem keyword matching
#                 server = i
#                 break

#         if server.find(".") == -1: # Nu avem ".", adica nu este corect specificat server-ul
#             await inter.edit_original_message(content = f"Serverul **{server}** nu a fost gasit. Verifica daca ai introdus corect adresa sau numele serverului!")
#             return
#         hostname, data = format_server_data(get_server_data(server))
#         if not hostname:
#             await inter.edit_original_message(content = f"Serverul **{server}** nu a fost gasit. Verifica daca ai introdus corect adresa sau numele serverului!")
#             return
#         embed.add_field(name=hostname, value=data)
#     else:
#         for server in servers:
#             hostname, data = format_server_data(get_server_data(server))
#             if not hostname:
#                 continue
#             embed.add_field(name=hostname, value=data)

#     await inter.edit_original_message(embed=embed)

@bot.listen()
async def on_ready():
    print_log("Ne-am conectat cu succes!")
    print_log(f"{bot.user}")
    print_log(f"Servers: {len(bot.guilds)}")
    print_log(f"Latency: {bot.latency}")
    print_log(f"Status: {bot.status}")
    print_log(f"")


print_log(f"Ne logam...")
# load cog
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")
        print_log(f"Incarcat cogs.{name}!")

bot.run(BOT_TOKEN)
