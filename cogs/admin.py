from datetime import datetime
import os
import json
import disnake
import aiohttp
import asyncio
import requests

import functii.bools as bools

from typing import List
from disnake.ext import commands
from bs4 import BeautifulSoup

from functii.debug import print_debug, print_log
from functii.creier import login_panou_forced, dump_session_to_file

class Admins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(bools.is_dev)
    async def reset(self, ctx):
        await ctx.send(f"Running the commmand.")
        with requests.Session() as s:
            login_panou_forced(s)
            dump_session_to_file(s, "session.pkl")
        await ctx.send("Succesfully ran the command. Dumped the session to file.")

    @commands.command()
    @commands.check(bools.is_dev)
    async def riperrors(self, ctx):
        await ctx.send(f"Running the commmand.")
        channels = await ctx.guild.fetch_channels()
        for channel in channels:
            if channel.name == "error":
                await channel.delete()
        await ctx.send("Succesfully ran the command. Deleted the error channels.")

    @commands.command()
    @commands.check(bools.is_dev)
    async def load(self, ctx, name: str):
        """ Loads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}\n```")
        await ctx.send(f"Loaded extension **{name}.py**")
        print_log(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.check(bools.is_dev)
    async def unload(self, ctx, name: str):
        """ Unloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}\n```")
        await ctx.send(f"Unloaded extension **{name}.py**")
        print_log(f"Unloaded extension **{name}.py**")

    @commands.command()
    @commands.check(bools.is_dev)
    async def reload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}\n```")
        await ctx.send(f"Reloaded extension **{name}.py**")
        print_log(f"Reloaded extension **{name}.py**")

def setup(bot):
    bot.add_cog(Admins(bot))
