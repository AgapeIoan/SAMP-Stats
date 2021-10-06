from discord.ext import commands
from dislash import slash_command, ActionRow, Button, ButtonStyle, Option, OptionType

from functii.creier import scrape_panou, login_panou
from functii.debug import empty_is_none, chunks
from functii.samp import cauta_clan, actualizeaza_lista_clanuri, salveaza_lista_clanuri, deschide_lista_clanuri

import panou.ruby

default_options_stats=[
    Option('nickname', 'Nickname-ul jucatorlui', OptionType.STRING, required=True)
]

class mycog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Example of a slash command in a cog
    @slash_command(description="Says Hello")
    async def hellocog(self, inter):
        await inter.respond("Hello from cog!")

    @slash_command(description="Vezi statisticile jucatorului specificat",
                    options = default_options_stats)
    async def stats(self, inter, nickname):
        await panou.ruby.stats(inter, nickname)

    @slash_command(description="Vezi masinile jucatorului specificat",
                    options = default_options_stats)
    async def vstats(self, inter, nickname):
        await panou.ruby.vstats(inter, nickname)

    # Buttons in cogs (no changes basically)
    @commands.command()
    async def testcog(self, ctx):
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
        msg = await ctx.send("This message has buttons", components=[row_of_buttons])
        # Wait for a button click
        def check(inter):
            return inter.author == ctx.author
        inter = await msg.wait_for_button_click(check=check)
        # Process the button click
        inter.reply(f"Button: {inter.button.label}", type=ResponseType.UpdateMessage)

def setup(bot):
    bot.add_cog(mycog(bot))