import json
import disnake
import asyncio

from disnake import ActionRow, Button, ButtonStyle, SelectMenu, SelectOption, Option, OptionType
from disnake import emoji
from disnake.ext import commands

import panou.ruby
import clase_menus
from functii.discord import disable_button

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
        # TODO Sa isi dea seama bot-ul daca e vorba de panel picat, pagina blank, lipsa profil sau orice altceva se poate intampla
        # si sa afiseze un mesaj de eroare corespunzator
        await inter.edit_original_message(f"Jucatorul **{nickname}** nu a fost gasit. Verifica daca ai introdus corect nickname-ul!", ephemeral=True)
        return

    view = clase_menus.Main_Menu(soup)

    if not panou.ruby.vstats(soup):
        disable_button(view.children[1])
    if not panou.ruby.bstats(soup):
        disable_button(view.children[2])
    if not panou.ruby.fhstats(soup):
        disable_button(view.children[3])
    
    await inter.edit_original_message(content=f"**Selecteaza o optiune pentru jucatorul `{nickname}`:**", view=view)
    # print(view)

    # @on_click.not_from_user(inter.author, cancel_others=True, reset_timeout=False)
    # async def on_wrong_user(inter):
    #     await inter.reply("You're not the author", ephemeral=True)

    # @on_click.timeout
    # async def on_timeout():
    #     await msg.edit(content="Mesajul a fost inactiv pentru prea mult timp, astfel butoanele au fost dezactivate.", components=[lista_butoane_stats(True, True, True, True, True)])
    #     await asyncio.sleep(180)
    #     # TODO Ar fi bine sa verificam inainte de sleep daca picam in except-ul de mai jos, astfel economisim timp si resurse yeeee
    #     try:
    #         await msg.edit(content='', components=[])
    #     except disnake.errors.HTTPException:
    #         pass


@bot.listen()
async def on_ready():
    print("Hatz cu buna dimineata, a pornit botu")
    
print("LOADED ZA COG, STARTING ZA BOT")
# TODO Fac ceva event on_ready() sa anunte ca so logat botu
bot.run(BOT_TOKEN)
    