# TODO Event on_command for command usage print in console
# TODO Event on_command_error for command error print in console

import datetime
import os
import json

from disnake.ext import commands
import custom_errors

from functii.debug import print_debug, print_log

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        print_log(f'Error: {error}')
        # log the error to unique file
        with open(r'storage/logs/on_slash_command_error/errors.log', 'a') as f:
            f.write(f'{str(datetime.datetime.now())} - {str(error)}\n')
    # LOG THE INTER
        data = {
            "author": str(inter.author),
            "author_id": int(inter.author.id),
            "filled_options": inter.filled_options,
            "options": inter.options,
            "permissions": int(inter.permissions.value),
            "channel": str(inter.channel),
            "guild": str(inter.guild),
        }
        try:
            data["channel_id"] = int(inter.channel_id)
            data["guild_id"] = int(inter.guild_id)
        except:
            data["channel_id"] = None
            data["guild_id"] = None

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

def setup(bot):
    bot.add_cog(Events(bot))
