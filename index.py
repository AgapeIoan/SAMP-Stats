from functii.creier import get_nickname
import json
import disnake
import asyncio
import os

from disnake import ActionRow, Button, ButtonStyle, SelectMenu, SelectOption, Option, OptionType
from disnake import emoji
from disnake.ext import commands
from functii.samp_server_stats import format_server_data, get_server_data

import panou.ruby
import main_menu
import clans_menu

from functii.discord import disable_button, disable_not_working_buttons
from functii.debug import print_debug

with open("config.json", "r") as f:
    config = json.load(f)

test_guilds = [722442573137969174, 921316017584631829]
BOT_TOKEN = config["BOT_TOKEN"]
POZA_MASINA_SAMP = "https://i.imgur.com/KC9rlJd.png"

bot = commands.Bot(command_prefix="!", test_guilds = [722442573137969174, 921316017584631829])
# If 'test_guilds' param isn't specified, the commands are registered globally.
# Global registration takes up to 1 hour.



@bot.slash_command(
    name="ping",
    description="Pings the bot.",
)
async def ping(inter):
    await inter.response.send_message(f'**Pong!**\n🏓 {round(bot.latency * 1000)}ms')

@bot.slash_command(
    name="file",
    description="testez",
)
async def file(inter):
    await inter.response.send_message(f'**Pong!**\n🏓 {round(bot.latency * 1000)}ms')
    with open("storage/vehicle_big_images/vehicles.json", "r") as f:
        data = json.load(f)
    
    for k,v in data.items():
        print_debug(f"{k} = {v}")
        await inter.send(content=k + " | " + v, file=disnake.File(fp=open(f"storage/vehicle_big_images/{k}.jpg", "rb"), filename=v + ".jpg"))

@bot.slash_command(
    name="stats", # Defaults to the function name
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
        print_debug("DEFER ERROR !!")
        # TODO #16 Bug mult prea dubios la response.defer()

    try:
        soup = panou.ruby.get_panel_data(nickname)
    except IndexError:
        # TODO #3 Sa isi dea seama bot-ul daca e vorba de panel picat, pagina blank, lipsa profil sau orice altceva se poate intampla
        # si sa afiseze un mesaj de eroare corespunzator
        await inter.edit_original_message(content=f"Jucatorul **{nickname}** nu a fost gasit. Verifica daca ai introdus corect nickname-ul!")
        return

    view = disable_not_working_buttons(main_menu.Main_Menu(soup), soup)
    view.original_author = inter.author
    
    view.message = await inter.edit_original_message(content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(soup)}`:**", view=view)

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
    print_debug("Ne-am conectat cu succes!")
    print_debug(f"{bot.user}")
    print_debug(f"Servers: {len(bot.guilds)}")
    print_debug(f"Latency: {bot.latency}")
    print_debug(f"Status: {bot.status}")
    print_debug(f"")

print_debug(f"Ne logam...")
# load cog
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")
        print_debug(f"Incarcat cogs.{name}!")


bot.run(BOT_TOKEN)