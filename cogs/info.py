import time
import discord
import psutil
import os
import random

from datetime import datetime
from discord.ext import commands
from utils import default


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.process = psutil.Process(os.getpid())

    @commands.command(aliases=["av"])
    async def avatar(self, ctx, user: discord.Member = None):
        """ Afiseaza avatarul utilizatorului de discord specificat """
        user = user or ctx.author
        embed = discord.Embed(title=str(user))
        embed.set_image(url=user.avatar_url_as(size=1024))
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))

        # n = random.randint(1, 100)
        # if n > 50:
        #     message = await ctx.send("🏓 aaa samp")
        # else:
        #     message = await ctx.send("🏓 Pong")

        message = await ctx.send("🏓 aaa samp")
        # TODO Sa fac ceva sa las pentru cateva ms in plus mesajul cu aaa samp sa fie relativ vizibil
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command(aliases=['joinme', 'join', 'botinvite'])
    async def invite(self, ctx):
        """ Invita bot-ul pe serverul tau """
        # TODO: Invite frumos in embed sau, daca prind in discord.py 2.0, cu buttons slash si alte nebunii.
        # Link invite sa fie intr-un hyperlink shit de arata frumos si trebe doar sa apesi pe el, se poate face treaba asta usor cu Embed shits. 
        n = random.randint(1, 100)
        if n > 70: # Sanse de 30% | TODO cand si daca o fi botul mai mare, scad sansa. Totusi, ar fi nevoie de asta doar daca dau baietii multe invites.
            await ctx.send(
                f"**{ctx.author.name}**, foloseste acest link ca sa mi-l inviti\n<{discord.utils.oauth_url(self.bot.user.id)}>")
        else:
            await ctx.send(
                f"**{ctx.author.name}**, foloseste acest link ca sa ma inviti\n<{discord.utils.oauth_url(self.bot.user.id)}>")

    @commands.command()
    async def source(self, ctx):
        """ Sursa pe care ruleaza bot-ul """
        # Do not remove this command, this has to stay due to the GitHub LICENSE.
        # TL:DR, you have to disclose source according to MIT.
        # Reference: https://github.com/AlexFlipnote/discord_bot.py/blob/master/LICENSE
        await ctx.send(
            f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/AlexFlipnote/discord_bot.py")

    # @commands.command(aliases=["supportserver", "feedbackserver"])
    # async def botserver(self, ctx):
    #     """ Get an invite to our support server! """
    #     if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 722442573137969174:
    #         return await ctx.send(f"**Here you go {ctx.author.name} 🍻\n<{self.config['botserver']}>**")
    #     await ctx.send(f"**{ctx.author.name}** this is my home you know :3")

    @commands.command(aliases=["supportserver", "feedbackserver"])
    async def botserver(self, ctx):
        try:
            await ctx.author.send("Salut! Aici este serverul meu de development: \nhttps://discord.gg/Dv68UJXQ")
            await ctx.send("Ti-am trimis in privat invite catre serverul meu de development.")
        except discord.Forbidden:
            await ctx.send("Nu pot sa iti trimit mesaj deoarece ai DM-urile blocate.")

    @commands.command(aliases=['idee', 'idea'])  # 722365521722474497
    async def sugestie(self, ctx, *, sugestie):
        """Fa o sugestie pentru bot"""
        nume = ctx.author
        with open("sugestii.txt", "r") as f:
            sugestii = "".join(f)

        detrm = f"{nume} | {sugestie}\n"

        with open("sugestii.txt", "w") as f:
            f.write(str(sugestii))
            f.write(detrm)

        guild = ctx.bot.get_guild(614414114852438017)
        channel = guild.get_channel(722365521722474497)
        await channel.send(detrm)  # Trimite info raw pe AgapeBots

        guild = ctx.bot.get_guild(722442573137969174)
        channel = guild.get_channel(722444042314448927)
        detrm = f"Idee sugerata de cineva: {sugestie}"
        await channel.send(detrm)  # Trimite info cenzurat pe RubyBOT Home

        await ctx.send(f"**{nume}**, sugestia a fost trimisa cu succes.")

    @commands.command()
    async def samp(self, ctx):
        """ aaa samp """
        await ctx.send("da, samp")

    @commands.command(aliases=["info"])
    async def about(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024**2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)

        embedColour = discord.Embed.Empty
        if hasattr(ctx, "guild") and ctx.guild is not None:
            embedColour = ctx.me.top_role.colour

        embed = discord.Embed(colour=embedColour)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="Last boot", value=default.timeago(datetime.now() - self.bot.uptime), inline=True)
        # embed.add_field(
        #     name=f"Developer{'' if len(self.config['owners']) == 1 else 's'}",
        #     value=", ".join([str(self.bot.get_user(x)) for x in self.config["owners"]]),
        #     inline=True
        # )
        embed.add_field(name="Developer", value="Agape#9318")

        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers:,.2f} users/server )", inline=True)
        embed.add_field(name="Commands loaded", value=len([x.name for x in self.bot.commands]), inline=True)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=True)

        await ctx.send(content=f"ℹ About **{ctx.bot.user}** | **{self.config['version']}**", embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
