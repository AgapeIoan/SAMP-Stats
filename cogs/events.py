# TODO Event on_command for command usage print in console
# TODO Event on_command_error for command error print in console

import disnake
from disnake.ext import commands

from functii.debug import print_debug

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Listen for commands
    @commands.Cog.listener()
    async def on_slash_command(self, inter):
        # https://prnt.sc/22ksw6z

        print_debug("author: " + str(inter.author))
        print_debug("channel: " + str(inter.channel))
        print_debug("channel_id: " + str(inter.channel_id))
        print_debug("data: " + str(inter.data))
        print_debug("filled_options: " + str(inter.filled_options))
        print_debug("guild: " + str(inter.guild))
        print_debug("guild_id: " + str(inter.guild_id))
        print_debug("options: " + str(inter.options))
        print_debug("permissions: " + str(inter.permissions))
        print_debug("response: " + str(inter.response))

        data = {
            "author": inter.author,
            "channel": inter.channel,
            "channel_id": inter.channel_id,
            "data": inter.data,
            "filled_options": inter.filled_options,
            "guild": inter.guild,
            "guild_id": inter.guild_id,
            "options": inter.options,
            "permissions": inter.permissions,
            "response": inter.response
        }
        

def setup(bot):
    bot.add_cog(Events(bot))