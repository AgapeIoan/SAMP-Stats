import json
import discord
import asyncio
from discord import embeds

from discord.ext import commands
from dislash import InteractionClient, ActionRow, Button, ButtonStyle, SelectMenu, SelectOption, ContextMenuInteraction, Option, OptionType

import panou.ruby

with open("config.json", "r") as f:
    config = json.load(f)

test_guilds = [722442573137969174]
BOT_TOKEN = config["BOT_TOKEN"]
POZA_MASINA_SAMP = "https://i.imgur.com/KC9rlJd.png"

bot = commands.Bot(command_prefix="!")
inter_client = InteractionClient(bot, test_guilds = [722442573137969174])
# If 'test_guilds' param isn't specified, the commands are registered globally.
# Global registration takes up to 1 hour.

def lista_butoane_stats(stats=False, vstats=False, bstats=False, fstats=False, cstats=False):
    return ActionRow(
        Button(
            style=ButtonStyle.blurple,
            label="Player Stats",
            custom_id="stats_button",
            disabled=stats
        ),
        Button(
            style=ButtonStyle.blurple,
            label="Vehicles",
            custom_id="vehicles_button",
            disabled=vstats
        ),
        Button(
            style=ButtonStyle.blurple,
            label="Properties",
            custom_id="properties_button",
            disabled=bstats
        ),
        Button(
            style=ButtonStyle.blurple,
            label="Faction History",
            custom_id="faction_button",
            disabled=fstats
        ),
        Button(
            style=ButtonStyle.blurple,
            label="Clan",
            custom_id="clan_button",
            disabled=cstats
        )
    )

def create_car_embed(car_name, nickname):
    embed=discord.Embed(color=0x00ff00)

    if car_name:
        embed.set_thumbnail(url="https://i.imgur.com/KC9rlJd.png")
        embed.add_field(name=car_name, value="DETALII_MASINA", inline=False)

    embed.set_footer(text=f"{nickname} | ruby.nephrite.ro")

    return embed

@bot.listen()
async def on_ready():
    print("Hatz cu buna dimineata, a pornit botu")

@inter_client.user_command(name="Press me")
async def press_me(inter):
    # User commands are visible in user context menus
    # They can be global or per guild, just like slash commands
    await inter.respond("Hello there!")

@inter_client.message_command(name="Resend")
async def resend(inter):
    # Message commands are visible in message context menus
    # inter is instance of ContextMenuInteraction
    await inter.respond(inter.message.content)



@bot.command()
async def test2(ctx):
    msg = await ctx.send(
        "This message has a select menu!",
        components=[
            SelectMenu(
                custom_id="test",
                placeholder="Choose up to 2 options",
                max_values=2,
                options=[
                    SelectOption("Option 1", "value 1"),
                    SelectOption("Option 2", "value 2"),
                    SelectOption("Option 3", "value 3")
                ]
            )
        ]
    )
    # Wait for someone to click on it
    inter = await msg.wait_for_dropdown()
    # Send what you received
    labels = [option.label for option in inter.select_menu.selected_options]



    await inter.reply(content=f"Options: {', '.join(labels)}")
    await inter.send(embed=embed)




@bot.command()
async def test(ctx):
    # Make a row of buttons
    row_of_buttons = ActionRow(
        Button(
            style=ButtonStyle.green,
            label="Green button",
            custom_id="green"
        ),
        Button(
            style=ButtonStyle.red,
            label="Red button",
            custom_id="red"
        )
    )
    # Send a message with buttons
    msg = await ctx.send(
        "This message has buttons!",
        components=[row_of_buttons]
    )
    # Wait for someone to click on them
    def check(inter):
        return inter.message.id == msg.id
    inter = await ctx.wait_for_button_click(check)
    # Send what you received
    button_text = inter.clicked_button.label
    await inter.reply(f"Button: {button_text}")
    await msg.delete()




@inter_client.slash_command(
    name="buton", # Defaults to the function name
    description="butoane",
    guild_ids=test_guilds,
    options=[
        Option("nickname", "Introdu nickname-ul", OptionType.STRING, required=True)
        # By default, Option is optional
        # Pass required=True to make it a required arg
    ]
)
async def buton(ctx, nickname):
    
    row = lista_butoane_stats()
    msg = await ctx.send(content="**Selecteaza o optiune:**", components=[row])

    on_click = msg.create_click_listener(timeout=60) # TODO Vedem ce iese si marim la nevoie

    @on_click.not_from_user(ctx.author, cancel_others=True, reset_timeout=False)
    async def on_wrong_user(inter):
        await inter.reply("You're not the author", ephemeral=True)

    @on_click.matching_id("stats_button", reset_timeout=True)
    async def on_test_button(inter):
        print(inter)
        # This function only works if the author presses the button
        # Becase otherwise the previous decorator cancels this one
        # empty_embed=discord.Embed(color=0x00ff00)
        # empty_embed.set_footer(text=f"{nickname} | ruby.nephrite.ro")
        await inter.reply(content='**Procesez comanda...**', components=[], embed=None, type=7)

        await msg.edit(content=None, embed=panou.ruby.stats(nickname), components=[lista_butoane_stats(stats=True)])
        # TODO In momentul in care aflam datele pe care vrem sa le afisam, salvam embed-ul undeva local pe aici si il folosim iar
        # daca respectivul vrea sa revina la meniul anterior, in caz ca pleaca la alt meniu 

    @on_click.matching_id("vehicles_button", reset_timeout=True)
    async def on_test_button(inter):
        await inter.reply(content='**Procesez comanda...**', components=[], embed=None, type=7)

        aux=[]
        lista_masini = await panou.ruby.vstats_debug(inter, nickname) 
        # TODO Lista masini sa fie splited in grupe de cate 23. Prima optiune BACK te duce inapoi, ultima optiune NEXT te duce la urmatoarea grupa.
        # BACK-ul cand esti la prima lista te duce la meniul principal aka lista butoane panou
        aux.append(SelectOption("🔙 Inapoi 🔙", "valoare_back"))
        for masina in lista_masini:
            aux.append(SelectOption(masina[0], lista_masini.index(masina)))
            print(masina)
        aux.append(SelectOption("➡️ Inainte ➡️", "valoare_next"))

        row_cars = ActionRow(
            SelectMenu(
                custom_id="test",
                placeholder="Selecteaza o masina",
                max_values=1,
                options=aux
            )
    )
        # row_cars.components[0].options[INDEX_MASINA].default = True
        await msg.edit(content="**Selecteaza o masina:**", components=[row_cars])

        labels = []
        while labels != ['🔙 Inapoi 🔙']:
            inter = await msg.wait_for_dropdown()
            print(inter)
            # Send what you received
            labels = [option.label for option in inter.select_menu.selected_options]
            print(labels[0])
            
            if labels != ['🔙 Inapoi 🔙']:
                await inter.reply(content='', embed=create_car_embed(f"{', '.join(labels)}", "nickname"), components=[row_cars], type=7)
            else:
                await inter.reply(content="**Selecteaza o optiune:**", embed=None, components=[row], type=7)

    @on_click.timeout
    async def on_timeout():
        await msg.edit(content="Mesajul a fost inactiv pentru prea mult timp, astfel butoanele au fost dezactivate.", components=[lista_butoane_stats(True, True, True, True, True)])
        await asyncio.sleep(180)
        try:
            await msg.edit(content='', components=[])
        except discord.errors.HTTPException:
            pass

bot.load_extension("cogs.mycog")
print("LOADED ZA COG, STARTING ZA BOT")
# TODO Fac ceva event on_ready() sa anunte ca so logat botu
bot.run(BOT_TOKEN)