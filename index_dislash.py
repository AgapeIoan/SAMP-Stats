import json
import disnake
import asyncio

from disnake import ActionRow, Button, ButtonStyle, SelectMenu, SelectOption, Option, OptionType
from disnake import emoji
from disnake.ext import commands

import panou.ruby
import clase_menus

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
    name="buton", # Defaults to the function name
    description="butoane",
    guild_ids=test_guilds,
    options=[
        Option("nickname", "Introdu nickname-ul", OptionType.string, required=True)
        # By default, Option is optional
        # Pass required=True to make it a required arg
    ]
)
async def buton(inter, nickname):
    await inter.response.defer()

    try:
        soup = panou.ruby.get_panel_data(nickname)
    except IndexError:
        # TODO Sa isi dea seama bot-ul daca e vorba de panel picat, pagina blank, lipsa profil sau orice altceva se poate intampla
        # si sa afiseze un mesaj de eroare corespunzator
        await inter.edit_original_message(f"Jucatorul **{nickname}** nu a fost gasit. Verifica daca ai introdus corect nickname-ul!", ephemeral=True)
        return

    view = clase_menus.Main_Menu(soup)

    await inter.edit_original_message(content="**Selecteaza o optiune:**", view=view)

    # @on_click.not_from_user(inter.author, cancel_others=True, reset_timeout=False)
    # async def on_wrong_user(inter):
    #     await inter.reply("You're not the author", ephemeral=True)

    # @on_click.matching_id("vehicles_button", reset_timeout=True)
    # async def on_test_button(inter):
    #     await inter.reply(content='**Procesez comanda...**', components=[], embed=None, type=7)

    #     aux=[]
    #     lista_masini = await panou.ruby.vstats_debug(inter, nickname)
    #     # TODO Lista masini sa fie splited in grupe de cate 23. Prima optiune BACK te duce inapoi, ultima optiune NEXT te duce la urmatoarea grupa.
    #     # BACK-ul cand esti la prima lista te duce la meniul principal aka lista butoane panou
    #     aux.append(SelectOption("🔙 Inapoi 🔙", "back"))
    #     for masina in lista_masini:
    #         stats_masina_packed = f"{masina[0]}+{masina[1]}+{masina[2]}+{masina[3]}"
    #         aux.append(SelectOption(masina[0], stats_masina_packed))
    #         print(masina)
    #     aux.append(SelectOption("➡️ Inainte ➡️", "next"))

    #     row_cars = ActionRow(
    #         SelectMenu(
    #             custom_id="test",
    #             placeholder="Selecteaza o masina",
    #             max_values=1,
    #             options=aux
    #         )
    # )
    #     # row_cars.components[0].options[INDEX_MASINA].default = True
    #     await msg.edit(content="**Selecteaza o masina:**", components=[row_cars])

    #     values = [None]
    #     while values[0] != "back":
    #         inter = await msg.wait_for_dropdown()
    #         print(inter)
    #         # Send what you received
    #         # labels = [option.label for option in inter.select_menu.selected_options]
    #         values = [option.value for option in inter.select_menu.selected_options]
    #         print(values)
            
    #         if values[0] == "back":
    #             # Ne intoarcem la meniul anterior cu butoane selectie stats
    #             await inter.reply(content="**Selecteaza o optiune:**", embed=None, components=[row], type=7)
    #         else:
    #             # Trimitem frumos embed cu masina ceruta
    #             # Embedul o sa fie generat pe baza dev-value a selectiei
    #             await inter.reply(content='', embed=create_car_embed(values[0].split("+"), nickname), components=[row_cars], type=7)

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
    