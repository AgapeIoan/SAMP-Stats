import os
import requests
import disnake
from disnake import Option, OptionType
from disnake.ext import commands

import views.mainmenu
import views.factions_menu
import panou.ruby

from functii.creier import get_nickname, login_panou_forced, dump_session_to_file
from functii.debug import print_debug, send_error_message_to_error_channel, print_log
from functii.discord import disable_not_working_buttons
from functii.bools import BOT_TOKEN, is_dev
from typing import List

# If 'test_guilds' param isn't specified, the commands are registered globally.
# Global registration takes up to 1 hour.

bot = commands.Bot(command_prefix=">")

@bot.command()
async def reset(ctx):
    if not is_dev(ctx.author.id):
        return

    var = is_dev(ctx.author.id)
    await ctx.send(f"{var}, {ctx.author.id}, running the commmand.")
    with requests.Session() as s:
        login_panou_forced(s)
        dump_session_to_file(s, "session.pkl")
    await ctx.send("Succesfully ran the command. Dumped the session to file.")


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

    view = await disable_not_working_buttons(views.mainmenu.MainMenu(soup), soup)
    view.original_author = inter.author
    view.bot = bot

    view.message = await inter.edit_original_message(
        content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(soup)}`:**", view=view)


# @bot.slash_command(
#     name="factions", # Defaults to the function name
#     description="Afiseaza lista de factiuni",
#     options=[
#         Option("param", "debug", OptionType.string, required=False)
#         # By default, Option is optional
#         # Pass required=True to make it a required arg
#     ]
# )
# async def factions(inter, param = None):
#     await inter.response.defer()
#     async with aiohttp.ClientSession(headers=headers) as session:
#         async with session.get("https://rubypanel.nephrite.ro/faction/list") as response:
#             soup = BeautifulSoup(await response.text(), 'html.parser')

#     view = views.factions_menu.FactionMenuMainView(soup)

#     await inter.edit_original_message(content=f"**FACTIONS**", view=view)


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

#     view = views.clase_menus.Clans_Menu_View(nr_pagina=1)

#     await inter.edit_original_message(content=f"**CLANS**", view=view)

@bot.listen()
async def on_ready():
    print_log("Ne-am conectat cu succes!")
    print_log(f"{bot.user}")
    print_log(f"Servers: {len(bot.guilds)}")
    print_log(f"Latency: {bot.latency}")
    print_log(f"Status: {bot.status}")
    print_log(f"")


print_log("Ne logam...")
# load cog
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")
        print_log(f"Incarcat cogs.{name}!")

bot.run(BOT_TOKEN)
