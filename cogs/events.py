# TODO Event on_command for command usage print in console
# TODO Event on_command_error for command error print in console

import datetime
import disnake
import os
import json
from disnake import guild

from disnake.ext import commands

from functii.debug import print_debug, print_log

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        print_log(f'{error}')
        # log the error to unique file
        with open(r'storage/logs/on_slash_command_error/errors.log', 'a') as f:
            f.write(f'{datetime.datetime.now()} - {error}\n')
    # LOG THE INTER
        data = {
            "author": str(inter.author),
            "author_id": int(inter.author.id),
            "channel": str(inter.channel),
            "channel_id": int(inter.channel_id),
            "filled_options": inter.filled_options,
            "guild": str(inter.guild),
            "guild_id": int(inter.guild_id),
            "options": inter.options,
            "permissions": int(inter.permissions.value),
        }

        # log data to unique file
        za_time = str(datetime.datetime.now()).replace(":", "-")
        path = r"storage/logs/on_slash_command_error/" + str(inter.guild_id)
        log_file_path = path + "/" + f"[{za_time}]" + " " + str(inter.author.id) + ".json"
        # if the directory doesn't exist, create it
        if not os.path.exists(path):
            os.makedirs(path)
        # dump data to json file
        with open(log_file_path, "w") as f:
            json.dump(data, f, indent=4)


    # Listen for commands
    @commands.Cog.listener()
    async def on_slash_command(self, inter):
        # https://prnt.sc/22ksw6z

        # print_debug("author: " + str(inter.author))
        # print_debug("channel: " + str(inter.channel))
        # print_debug("channel_id: " + str(inter.channel_id))
        # print_debug("data: " + str(inter.data))
        # print_debug("filled_options: " + str(inter.filled_options))
        # print_debug("guild: " + str(inter.guild))
        # print_debug("guild_id: " + str(inter.guild_id))
        # print_debug("options: " + str(inter.options))
        # print_debug("permissions: " + str(inter.permissions))

        data = {
            "author": str(inter.author),
            "author_id": int(inter.author.id),
            "channel": str(inter.channel),
            "channel_id": int(inter.channel_id),
            "filled_options": inter.filled_options,
            "guild": str(inter.guild),
            "guild_id": int(inter.guild_id),
            "options": inter.options,
            "permissions": int(inter.permissions.value),
        }

        # someone used a command
        print_log(f"{inter.author} | Guild: {str(inter.guild)} | Channel: {str(inter.channel)} | /{str(inter.data.name)} {str(inter.options)}")

        # log data to unique file
        za_time = str(datetime.datetime.now()).replace(":", "-")
        path = r"storage/logs/on_slash_command/" + str(inter.guild_id)
        log_file_path = path + "/" + f"[{za_time}]" + " " + str(inter.author.id) + ".json"
        # if the directory doesn't exist, create it
        if not os.path.exists(path):
            os.makedirs(path)
        # dump data to json file
        with open(log_file_path, "w") as f:
            json.dump(data, f, indent=4)
            
        

def setup(bot):
    bot.add_cog(Events(bot))