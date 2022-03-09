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
        if isinstance(error, custom_errors.CommandErrorReport):
            print_debug(f"CommandErrorReport: {error.string_to_send}")
        print_log(f'za error {error}')
        # log the error to unique file
        with open(r'storage/logs/on_slash_command_error/errors.log', 'a') as f:
            f.write(f'{datetime.datetime.now()} - {error}\n')
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

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # This works only on legacy commands, the ones using @bot.command() decorator
        print_debug(f"on_command_error: {error}")


def setup(bot):
    bot.add_cog(Events(bot))
