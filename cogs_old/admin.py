import time
import aiohttp
import discord
import importlib
import os
import sys
import json
import asyncio
import requests

from asyncio.subprocess import PIPE
from discord.ext import commands
from utils import permissions, default, http
from io import BytesIO  

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self._last_result = None

    def change_config_value(self, value: str, changeto: str):
        """ Change a value from the configs """
        config_name = "config.json"
        with open(config_name, "r") as jsonFile:
            data = json.load(jsonFile)

        data[value] = changeto
        with open(config_name, "w") as jsonFile:
            json.dump(data, jsonFile, indent=2)

    @commands.command()
    @commands.check(permissions.is_owner)
    async def spune(self, ctx, *, mesaj: str):
        await ctx.send(mesaj)

    @commands.command()
    @commands.check(permissions.is_owner)
    async def anunt(self, ctx, *, msg):
        with open("CanaleUpdates.json", "r") as f:
            skema = json.load(f)
        
        attr_error_count = 0
        perm_error_count = 0
        mesaje_trimise = 0

        for soyey in skema.items():
            try:
                guildId, channelId = soyey
                canal = self.bot.get_guild(int(guildId)).get_channel(int(channelId))
                try:
                    await canal.send(msg)
                    mesaje_trimise += 1
                except:
                    await ctx.send(f"Nu am putut trimite la **{guildId}** | **{channelId}**, trec peste.")
                    perm_error_count += 1
            except AttributeError as err:
                await ctx.send(f"Uno problemo, `AttributeError`. Trecem peste si vedem ce iese. \nDetalii: \nsoyey = {soyey}\nraw error = {err}\n")
                attr_error_count += 1

        await ctx.send(f"Done! Am trimis anuntul super important pe exact {mesaje_trimise} canale.")
        await ctx.send(f" Am avut in total {attr_error_count} erori legat de AttributeError si {perm_error_count} erori legate de permisiuni (cred, ca Agape batman a pus except fara sa specifice eroarea).")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def ip(self, ctx):
        """ Trimite ip-ul botului """
        r = requests.get("https://api.ipify.org")
        await ctx.send(str(r.text))

    # TODO #5 Fix exec command cuz e shot, nu mere ;-; 
    @commands.command(aliases=['exec'])
    @commands.check(permissions.is_owner)
    async def execute(self, ctx, *, text: str):
        """ Do a shell command. """

        if ctx.author.id != 318348903114211328:
            return # Extra caution wannabe???

        message = await ctx.send(f"Loading...")
        proc = await asyncio.create_subprocess_shell(text, stdin=None, stderr=PIPE, stdout=PIPE)
        out = (await proc.stdout.read()).decode('utf-8').strip()
        err = (await proc.stderr.read()).decode('utf-8').strip()

        if not out and not err:
            await message.delete()
            return await ctx.message.add_reaction('👌')

        content = ""

        if err:
            content += f"Error:\r\n{err}\r\n{'-' * 30}\r\n"
        if out:
            content += out

        if len(content) > 1500:
            try:
                data = BytesIO(content.encode('utf-8'))
                await message.delete()
                await ctx.send(content=f"The result was a bit too long.. so here is a text file instead 👍",
                               file=discord.File(data, filename=default.timetext(f'Result')))
            except asyncio.TimeoutError as e:
                await message.delete()
                return await ctx.send(e)
        else:
            await message.edit(content=f"```fix\n{content}\n```")

    @commands.command()
    @commands.check(permissions.is_developer)
    async def amiadmin(self, ctx):
        """ Are you an admin? """
        if ctx.author.id in self.config["owners"]:
            return await ctx.send(f"Yes **{ctx.author.name}** you are an admin! ✅")

        # Please do not remove this part.
        # I would love to be credited as the original creator of the source code.
        #   -- AlexFlipnote
        if ctx.author.id == 86477779717066752:
            return await ctx.send(f"Well kinda **{ctx.author.name}**.. you still own the source code")

        # await ctx.send(f"**Daca vezi mesajul asta, ummm, ceva nu e ok {ctx.author.name}**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def load(self, ctx, name: str):
        """ Loads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def unload(self, ctx, name: str):
        """ Unloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reloadall(self, ctx):
        """ Reloads all extensions. """
        error_collection = []
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.bot.reload_extension(f"cogs.{name}")
                except Exception as e:
                    error_collection.append(
                        [file, default.traceback_maker(e, advance=False)]
                    )

        if error_collection:
            output = "\n".join(
                f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection
            )

            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{output}"
            )

        await ctx.send("Successfully reloaded all extensions")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reloadutils(self, ctx, name: str):
        """ Reloads a utils module. """
        name_maker = f"utils/{name}.py"
        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.send(f"Couldn't find module named **{name_maker}**")
        except Exception as e:
            error = default.traceback_maker(e)
            return await ctx.send(f"Module **{name_maker}** returned error and was not reloaded...\n{error}")
        await ctx.send(f"Reloaded module **{name_maker}**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reboot(self, ctx):
        """ Reboot the bot """
        await ctx.send("Rebooting now...")
        time.sleep(1)
        sys.exit(0)

    @commands.command()
    @commands.check(permissions.is_owner)
    async def dm(self, ctx, user_id: int, *, message: str):
        """ DM the user of your choice """
        user = self.bot.get_user(user_id)
        if not user:
            return await ctx.send(f"Could not find any UserID matching **{user_id}**")

        try:
            await user.send(message)
            await ctx.send(f"✉️ Sent a DM to **{user_id}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")

    @commands.group()
    @commands.check(permissions.is_owner)
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @change.command(name="playing")
    @commands.check(permissions.is_owner)
    async def change_playing(self, ctx, *, playing: str):
        """ Change playing status. """
        status = self.config["status_type"].lower()
        status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

        activity = self.config["activity_type"].lower()
        activity_type = {"listening": 2, "watching": 3, "competing": 5}

        try:
            await self.bot.change_presence(
                activity=discord.Game(
                    type=activity_type.get(activity, 0), name=playing
                ),
                status=status_type.get(status, discord.Status.online)
            )
            self.change_config_value("playing", playing)
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(name="username")
    @commands.check(permissions.is_owner)
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname")
    @commands.check(permissions.is_owner)
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @change.command(name="avatar")
    @commands.check(permissions.is_owner)
    async def change_avatar(self, ctx, url: str = None):
        """ Change avatar. """
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip("<>") if url else None

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio)
            await ctx.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            await ctx.send("You need to either provide an image URL or upload one with the command")


def setup(bot):
    bot.add_cog(Admin(bot))