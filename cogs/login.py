import json
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from functii.creier import get_nickname, get_player_id
from functii.samp import save_json_users
from utils import default

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}


class Login(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()

    @commands.command()
    async def login(self, ctx, nickname):
        """ Asociezi contul de pe joc cu cel de discord """

        lista_forum = []

        with requests.Session() as s:
            if "https://rubypanel.nephrite.ro" in nickname:  # Este link
                temp = nickname.find('profile/') + 8
                nickname = nickname[temp:].replace('/', '')
            else:
                nickname = nickname

            url = f"https://rubypanel.nephrite.ro/profile/{nickname}"
            r = s.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html5lib')
            nickname_real = get_nickname(soup)
            player_id = get_player_id(soup)
            if not nickname_real:
                await ctx.send("Nu am putut gasi jucatorul specificat! Verifica daca ai introdus corect nickname-ul.")
            else:
                f2 = soup.findAll('div', {'class': 'col-md-12'})
                statsforum = f2[3]
                for i in statsforum.findAll('b'):
                    skema = i.find_all(text=True)
                    lista_forum.append(skema)
                try:
                    discord_acc = lista_forum[-2][0]
                except IndexError:
                    await ctx.send("Jucatorul specificat nu are contul de forum asociat pe panel!")
                    return

                # await ctx.send(f"{discord_acc} | {ctx.author}")
                discord_acc = str(discord_acc)
                # Mai jos verificam daca avem string de forma alphanumeric#xxxx unde x este integer
                if not (discord_acc[-4:].isnumeric() and discord_acc[-5:-4] == "#" and len(discord_acc) > 5):
                    await ctx.send(
                        f"{ctx.author.mention}, jucatorul specificat nu are contul de discord asociat celui de forum!")
                    return

                if discord_acc[-6] == ' ':
                    discord_acc = discord_acc[:-6] + discord_acc[-5:]

                if str(discord_acc).strip() == str(ctx.author):
                    with open("Users.json", "r+", encoding='utf-8') as utilizatori:
                        dict_membri = json.load(utilizatori)
                        memberlist = dict_membri.get("members")
                        idlist = dict_membri.get("ids")
                        discordlist = dict_membri.get("discords")  # Citim lista

                    if str(ctx.author.id) in discordlist:
                        index = discordlist.index(str(ctx.author.id))
                        memberlist[index] = nickname_real
                        idlist[index] = player_id
                        save_json_users(dict_membri)
                        print("if")
                    else:
                        memberlist.append(nickname_real)
                        idlist.append(player_id)
                        discordlist.append(str(ctx.author.id))  # Actualizam lista
                        save_json_users(dict_membri)
                        print("else")

                    await ctx.send(
                        f"{ctx.author.mention}, am asociat jucatorul **{nickname_real}** cu id unic **{player_id}** contului tau de discord.")
                else:
                    await ctx.send(
                        f"{ctx.author.mention}, jucatorul specificat are username-ul de discord **{discord_acc}** asociat contului de forum!\nDaca **{nickname_real}** este contul tau, trebuie sa schimbi username-ul de discord in **{str(ctx.author)}** sau sa contactezi un developer!")

    @commands.command()
    async def getid(self, ctx, nickname):
        """ Afiseaza id-ul unic al jucatorului specificat """
        # <img src = "https://rubypanel.nephrite.ro/userbar/type/1/user/80249"></img>

        with requests.Session() as s:
            url = f"https://rubypanel.nephrite.ro/profile/{nickname}"
            r = s.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html5lib')
            player_nickname = get_nickname(soup)
            if not player_nickname:
                await ctx.send("Nu am putut gasi jucatorul specificat! Verifica daca ai introdus corect nickname-ul.")
            else:
                player_id = get_player_id(soup)
                await ctx.send(f"Id-ul unic al jucatorului **{player_nickname}** este **{player_id}**.")


def setup(bot):
    bot.add_cog(Login(bot))
