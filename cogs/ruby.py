import json
import requests
from discord.ext import commands

import discord
from functii.creier import scrape_panou, login_panou
from functii.debug import empty_is_none, chunks
from functii.samp import cauta_clan, actualizeaza_lista_clanuri, salveaza_lista_clanuri, deschide_lista_clanuri
from utils import default

strToReplaceList = ['</div>', """<div id="clanDescriptionText">""", '<li>', '<em>', '<p>', '</p>', '<ol>', '</ol>',
                    '<strong>', '</strong>', '</em>', '</li>', '</a>', '<a>', '<a href="', '">', '<br/>', "<ul>",
                    "</ul>"] # mortii tei ioane ce e cu codul asta


# Linia 680, poate reusim sa scrape mai clean si scapam de lista asta de cacao

class RubyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()

    @commands.cooldown(rate=10, per=5.0, type=commands.BucketType.user)
    @commands.command(aliases=['tester'])
    async def testers(self, ctx, *, factiune):
        """ Afiseaza lista testerilor online din factiunea specificata """
        async with ctx.channel.typing():
            with open("factiuniAliases.json", "r+", encoding='utf-8') as aliases:
                dict_aliases = json.load(aliases)
            try:
                id = int(factiune)
                keye = list(dict_aliases)
                nume = keye[id - 1]
            except ValueError:
                i = 0
                for facc in dict_aliases.items():
                    i += 1
                    if factiune.lower() in facc[0].lower() or factiune.lower() in facc[1].lower():
                        id = i
                        nume = facc[0]
                        break
            try:
                id
            except UnboundLocalError:
                await ctx.send("Nu am putut gasi factiunea specificata!")
                return

            # ================== PANA AICI FUSE COD FURAT DE LA COMANDA APLICANTI ==================
            # ======================= URMEAZA COD FURAT DE LA COMANDA FSTATS =======================

            testeri = []
            online_testers = ""

            with requests.Session() as s:
                url = f"https://rubypanel.nephrite.ro/faction/members/{id}"
                f2, _ = scrape_panou(s, url, [{'div': {'class': 'col-md-12'}}], True)
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                for i in range(1, len(data)):
                    skema = data[i]

                    rank = skema[1]
                    if "tester" in rank:
                        # Verificam daca e on, cea mai simpla varianta e sa luam cod de la
                        # Comanda >id, mai simplu decat sa verificam panel la fiecare
                        # EDIT: Aparent pe >id vad cel mai rpd cand cineva e on pe sv, restul mai greu
                        testeri.append(skema[0].replace('\n', '').replace(' ', ''))  # Scapam de \n si spatii

                    elif "co-leader" in rank:
                        coleader = skema[0].replace('\n', '').replace(' ', '')

                    elif "leader" in rank:
                        leader = skema[0].replace('\n', '').replace(' ', '')

                    if "4" in rank or len(testeri) == 3:
                        break
                        # Nu are rost sa mergem mai jos de rank 5
                        # sau mai departe de 3 testeri
                        # ca nu mai gasim nimic

                # ================== AMU CONTINUAM CU COD FURAT DE LA COMANDA ID ==================

                url = "https://rubypanel.nephrite.ro/online"
                f2, _ = scrape_panou(s, url, [{'div': {'class': 'col-xs-12'}}], True)
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                # await ctx.send(testeri)
                # print(leader)
                # print(coleader)

                embed = discord.Embed(title=nume, color=0x00ff00)

                trimis_tester = False
                trimis_leader = False
                trimis_coleader = False

                ###############################
                # DE FACUT FUNCTIE PENTRU SKEMA ASTA SA NU MA REPET

                try:
                    coleader
                except UnboundLocalError:
                    coleader = '.'

                try:
                    leader
                except UnboundLocalError:
                    leader = '.'

                ################################

                for statsPlayer in data[1:]:  # Trecem de primul element cuz e gol
                    nick = statsPlayer[0]

                    if any(item == nick for item in testeri):
                        trimis_tester = True
                        online_testers += f"{nick}\n"
                        # await ctx.send(f"Tester {nick} este online.")

                    elif coleader == nick and not trimis_coleader:
                        embed.add_field(name=f"Online Co-leader", value=nick)
                        trimis_coleader = True
                        # await ctx.send(f"Co-leader {nick} este online")

                    elif leader == nick and not trimis_leader:
                        embed.add_field(name=f"Online Leader", value=nick)
                        trimis_leader = True
                        # await ctx.send(f"Leader {nick} este online.")
                if online_testers:
                    embed.add_field(name=f"Online Testers", value=online_testers)

            if trimis_tester or trimis_coleader or trimis_leader:
                try:
                    await ctx.send(embed=embed)
                except discord.errors.Forbidden:
                    await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')
            else:
                await ctx.send(f'Nu este nici un tester sau lider online din **{nume}**!')

    @commands.cooldown(rate=10, per=5.0, type=commands.BucketType.user)
    @commands.command(aliases=['aplicati', 'aplicatii'])
    async def aplicanti(self, ctx, *, factiune_sau_id):
        """ Afiseaza lista aplicantilor din factiunea specificata """
        async with ctx.channel.typing():
            with open('factiuniAliases.json', "r+", encoding='utf-8') as aliases:
                dict_aliases = json.load(aliases)
            try:
                id = int(factiune_sau_id)
                keye = list(dict_aliases)
                nume = keye[id - 1]
            except ValueError:
                i = 0
                for facc in dict_aliases.items():
                    i += 1
                    if factiune_sau_id.lower() in facc[0].lower() or factiune_sau_id.lower() in facc[1].lower():
                        id = i
                        nume = facc[0]
                        break

            # Intram la posts
            try:
                id
            except UnboundLocalError:
                await ctx.send("Nu am putut gasi factiunea specificata!")
                return

            # await ctx.send(id)
            with requests.Session() as s:
                url = f"https://rubypanel.nephrite.ro/faction/applications/{id}"
                lista_links_tags = [{'div': {'class': 'col-md-8'}},
                                    {'h3': {'class': 'box-title'}},
                                    {'a': {'class': 'btn btn-xs bg-black'}}]
                f2, aplicatii, links = scrape_panou(s, url, lista_links_tags)

                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                # for i in data:
                #    print(i) # LISTA DE LINKS
                # noi = []
                # acceptati = []

                # for i in aplicatii:
                #    await ctx.send(i.text)
                #    print(i.text) # LISTA DE NR APLICATII

                # AFLAM NUMARUL DE APLICATII SI DUPA MERGEM IN FUNCTIE DE NUMAR
                aplicatii_noi = int(
                    aplicatii[0].text[aplicatii[0].text.find("(") + 1:-2])  # Putin cam strans dar in esenta
                # Ma uit dupa paranteza si citesc nr din paranteza. Btw e spatiu la final de string
                aplicatii_acceptate = int(aplicatii[1].text[aplicatii[1].text.find("(") + 1:-2])
                aplicatii_acceptate_aux = aplicatii_acceptate
                # aplicatii_invitati = aplicatii[1].text[aplicatii[1].text.find("(")+1:-2]
                # aplicatii_respinsi = aplicatii[1].text[aplicatii[1].text.find("(")+1:-2]

                # print(data)
                noi = data[1:aplicatii_noi + 1]
                if data[:2] == [[], []]:  # Navem aplicatii noi
                    acceptati = data[2:aplicatii_acceptate_aux + 2]
                else:
                    acceptati = data[aplicatii_noi + 2:aplicatii_noi + 2 + aplicatii_acceptate]

                # await ctx.send(f"Aplicatii noi: {aplicatii_noi}")
                # await ctx.send(noi)
                # await ctx.send("=========")
                # await ctx.send(f"Aplicatii acceptate: {aplicatii_acceptate}")
                # await ctx.send(acceptati)

                embed = discord.Embed(title="Aplicatii noi", color=0x00ff00)
                embed.set_footer(text=nume)

                if noi:
                    for i in noi:
                        detrm = f"ID: {i[0]}\nNickname: {i[1]}\nData: {i[2]}\n"
                        embed.add_field(name=i[1], value=detrm)

                    try:
                        await ctx.send(embed=embed)
                    except discord.errors.Forbidden:
                        await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')
                        return

                embed = discord.Embed(title="Aplicatii acceptate", color=0x00ff00)
                embed.set_footer(text=nume)

                if acceptati:
                    try:
                        for i in acceptati:
                            detrm = f"ID: {i[0]}\nNickname: {i[1]}\nData: {i[2]}\n"
                            embed.add_field(name=i[1], value=detrm)
                        try:
                            await ctx.send(embed=embed)
                        except discord.errors.Forbidden:
                            await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')
                            return
                    except IndexError:
                        acceptati = []
                        pass

                if not acceptati and not noi:
                    await ctx.send(f"Factiunea **{nume}** nu are aplicanti in prezent!")

    @commands.cooldown(rate=10, per=5.0, type=commands.BucketType.user)
    @commands.command()
    async def forum(self, ctx, nickname):
        """Verifica forumul jucatorului specificat"""
        async with ctx.channel.typing():
            lista_forum = []

            with requests.Session() as s:
                url = f"https://rubypanel.nephrite.ro/profile/{nickname}"
                f2, _ = scrape_panou(s, url, [{'div': {'class': 'col-md-12'}}], True)
                try:
                    statsforum = f2[3]
                except IndexError:
                    await ctx.send("Nu am putut gasi un jucator cu nickname-ul specificat!")
                    return

                # for i in statsforum.findAll('a'):
                #     link_forum = i['href']
                # for i in statsforum.findAll('img'):
                #     img_forum = i['src']
                for i in statsforum.findAll('b'):
                    skema = i.find_all(text=True)
                    lista_forum.append(skema)

                try:
                    lista_forum[-6][0]
                except IndexError:
                    await ctx.send("Jucatorul specificat nu are contul de forum asociat pe panel!")
                    return

                try:
                    steam = empty_is_none(lista_forum[-1][0])
                except IndexError:
                    steam = 'none'
                try:
                    discord_acc = empty_is_none(lista_forum[-2][0])
                except IndexError:
                    discord_acc = 'none'
                try:
                    skype = empty_is_none(lista_forum[-3][0])
                except IndexError:
                    skype = 'none'
                try:
                    aim = empty_is_none(lista_forum[-4][0])
                except IndexError:
                    aim = 'none'
                reputation = lista_forum[-5][0]
                posts = lista_forum[-6][0]
                roles_raw = lista_forum[1:-6]
                forum_acc = lista_forum[0][0]
                roles = ''
                for rol in roles_raw:
                    # roles += (rol + '\n')
                    print(rol)
                    roles += rol[0]
                    roles += ' | '
                roles = roles[:-3]  # Scapam de |
                # print(lista_forum)
                embed = discord.Embed(title="Forum Account", color=0x00ff00)
                # embed.set_thumbnail(
                #    url=img_forum)
                # await ctx.send(img_forum)
                embed.add_field(name=forum_acc,
                                value=(f"Roles: {roles}\n" +
                                       f"Posts: {posts}\n" +
                                       f"Reputation: {reputation}\n" +
                                       f"AIM: {aim}\n" +
                                       f"Skype: {skype}\n" +
                                       f"Discord: {discord_acc}\n" +
                                       f"Steam: {steam}")
                                )

        try:
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')

    @commands.cooldown(rate=10, per=5.0, type=commands.BucketType.user)
    @commands.command(aliases=['lideri'])
    async def leaders(self, ctx):
        """ Afiseaza lista liderilor online """
        async with ctx.channel.typing():
            # await ctx.send('incepem')
            with requests.Session() as s:
                url = "https://rubypanel.nephrite.ro/staff"
                f2, soup = scrape_panou(s, url, [{'div': {'class': 'col-xs-12'}}], True)
                f1 = soup.findAll('a', href=True)
                for a in f1:
                    if "tab_leaders" in a['href']:
                        a = str(a)
                        slots_admin = a[a.find("Leaders ["):-4]

                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                data2 = f2[0].findAll('i')
                data2_adv = []
                staff_members = []
                data_adv = []

                for skema in data2:
                    if 'data-original-title="Online"' in str(skema) or 'data-original-title="Offline"' in str(skema):
                        data2_adv.append(str(skema))
                # print(data2_adv[0])

                # Curatam lista de staff
                faranumar = 0
                numar_admini_si_helperi = 0
                for i in data:
                    if i and faranumar < 4:
                        numar_admini_si_helperi += 1
                    elif not i:
                        faranumar += 1
                    if faranumar >= 4 and i:
                        data_adv.append(i)
                    if faranumar == 5:
                        break

                # Ii verificam daca sunt on
                # print(data_adv)
                # print(numar_admini_si_helperi)
                for staff, online in zip(data_adv, data2_adv[numar_admini_si_helperi:]):
                    player = staff[0].replace(' ', '')  # Scapam de spatii goale
                    lvl = staff[1]
                    zile = staff[2]
                    # print(player)
                    # print(online)
                    if "Online" in str(online):
                        staff_members.append([player, lvl, zile])

                embed = discord.Embed(title=f"Online {slots_admin}", color=0x00ff00)  # TODO Poate schimb culoarea?

                for membru in staff_members:
                    embed.add_field(name=membru[0], value=f"Leader of {membru[1]}\nFaction days: {membru[2]}")

                try:
                    await ctx.send(embed=embed)
                except discord.errors.Forbidden:
                    await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')

    @commands.cooldown(rate=10, per=5.0, type=commands.BucketType.user)
    @commands.command()
    async def helpers(self, ctx):
        """ Afiseaza lista helperilor online """
        async with ctx.channel.typing():
            with requests.Session() as s:
                url = "https://rubypanel.nephrite.ro/staff"
                f2, soup = scrape_panou(s, url, [{'div': {'class': 'col-xs-12'}}], True)
                f1 = soup.findAll('a', href=True)
                for a in f1:
                    if "tab_helpers" in a['href']:
                        a = str(a)
                        slots_admin = a[a.find("Helpers ["):-4]

                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                data2 = f2[0].findAll('i')
                data2_adv = []
                staff_members = []
                data_adv = []

                for skema in data2:
                    if 'data-original-title="Online"' in str(skema) or 'data-original-title="Offline"' in str(skema):
                        data2_adv.append(str(skema))
                # print(data2_adv[0])

                # Curatam lista de staff
                faranumar = 0
                numar_admini = 0
                for i in data:
                    if i and faranumar < 3:
                        numar_admini += 1
                    elif not i:
                        faranumar += 1
                    if faranumar >= 3 and i:
                        data_adv.append(i)
                    if faranumar == 4:
                        break

                # Ii verificam daca sunt on
                for staff, online in zip(data_adv, data2_adv[numar_admini:]):
                    player = staff[0].replace(' ', '')  # Scapam de spatii goale
                    lvl = staff[1]
                    # print(player)
                    # print(online)
                    if "Online" in str(online):
                        staff_members.append([player, lvl])

                embed = discord.Embed(title=f"Online {slots_admin}", color=0x00ff00)  # TODO Poate schimb culoarea?

                for membru in staff_members:
                    embed.add_field(name=membru[0], value=f"Helper level {membru[1]}")

                try:
                    await ctx.send(embed=embed)
                except discord.errors.Forbidden:
                    await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')

    @commands.cooldown(rate=10, per=5.0, type=commands.BucketType.user)
    @commands.command()
    async def admins(self, ctx):
        """ Afiseaza lista adminilor online """
        async with ctx.channel.typing():
            with requests.Session() as s:
                url = "https://rubypanel.nephrite.ro/staff"
                f2, soup = scrape_panou(s, url, [{'div': {'class': 'col-xs-12'}}], True)
                f1 = soup.findAll('a', href=True)
                for a in f1:
                    if "tab_admins" in a['href']:
                        a = str(a)
                        slots_admin = a[a.find("Admins ["):-4]

                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                data2 = f2[0].findAll('i')
                data2_adv = []
                staff_members = []
                data_adv = []

                for skema in data2:
                    if 'data-original-title="Online"' in str(skema) or 'data-original-title="Offline"' in str(skema):
                        data2_adv.append(str(skema))
                # print(data2_adv[0])

                # Curatam lista de staff
                faranumar = 0
                for i in data:
                    if i:
                        data_adv.append(i)
                    else:
                        faranumar += 1
                    if faranumar == 3:
                        break  # Terminam cu adminii

                # Ii verificam daca sunt on
                for staff, online in zip(data_adv, data2_adv):
                    player = staff[0].replace(' ', '')  # Scapam de spatii goale
                    lvl = staff[1]
                    badges = staff[2]
                    # print(player)
                    # print(online)
                    if "Online" in str(online):
                        staff_members.append([player, lvl, badges])

                embed = discord.Embed(title=f"Online {slots_admin}", color=0x00ff00)  # TODO Poate schimb culoarea?

                for membru in staff_members:
                    valoare = f"Admin level {membru[1]}"
                    badges = membru[2].replace('\n', '')
                    if badges:
                        parts = badges.split()
                        capitalized_parts = [p.capitalize() for p in parts]
                        badges_adv = " ".join(capitalized_parts)
                        valoare += f"\n{badges_adv}"

                    embed.add_field(name=membru[0], value=valoare)

                try:
                    await ctx.send(embed=embed)
                except discord.errors.Forbidden:
                    await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')

    @commands.cooldown(rate=10, per=5.0, type=commands.BucketType.user)
    @commands.command(aliases=['faction'])
    async def factiune(self, ctx, *, factiune):
        """ Afiseaza detalii legate de factiunea specificata """
        async with ctx.channel.typing():
            # await ctx.send('incepem')
            with requests.Session() as s:
                login_panou(s)
                url = "https://rubypanel.nephrite.ro/faction/list"
                f2, _ = scrape_panou(s, url, [{'div': {'class': 'col-xs-12'}}], True)
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]
                embed = discord.Embed(title="Faction", color=0x00ff00)
                avem_factiune = False
                with open('factiuniAliases.json', "r+", encoding='utf-8') as aliases:
                    dict_aliases = json.load(aliases)
                # print(dict_aliases)
                for skema, fAlias in zip(data[1:], dict_aliases.items()):
                    if factiune.lower() in skema[1].lower() or factiune.lower() in fAlias[1].lower():
                        avem_factiune = True
                        if "applications closed or you are not logged in" in skema[4]:  # Daca aplicatiile sunt inchise
                            status_aplicatii = "closed"
                        else:
                            status_aplicatii = "open"
                        embed.add_field(name=skema[1],
                                        value=(f"ID: {skema[0]}\n" +
                                               f"Members: {skema[2]}\n" +
                                               f"Applications: {status_aplicatii}\n" +
                                               f"Requirements: {skema[5]}")
                                        )
                try:
                    if avem_factiune:
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("Nu am putut gasi factiunea specificata!")
                except discord.errors.Forbidden:
                    await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')

    @commands.cooldown(rate=10, per=5.0, type=commands.BucketType.user)
    @commands.command()
    async def id(self, ctx, nickname: str):
        """ Afiseaza jucatorii online dupa nickname-ul specificat """
        async with ctx.channel.typing():
            with requests.Session() as s:
                url = "https://rubypanel.nephrite.ro/online"
                f2, _ = scrape_panou(s, url, [{'div': {'class': 'col-xs-12'}}], True)
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                nicks = []
                levels = []
                factions = []
                hours = []
                rps = []

                for statsPlayer in data[1:]:  # Trecem de primul element cuz e gol
                    if nickname.lower() in statsPlayer[0].lower():
                        nicks.append(statsPlayer[0])
                        levels.append(statsPlayer[1])
                        factions.append(statsPlayer[2])
                        hours.append(statsPlayer[3])
                        rps.append(statsPlayer[4])

                embed = discord.Embed(title="Online Players", color=0x00ff00)
                sent = False
                for i in range(len(nicks)):
                    embed.add_field(name=nicks[i],
                                    value=(f"Level: {levels[i]}\n" +
                                           f"Group: {factions[i]}\n" +
                                           f"Hours Played: {hours[i]}\n" +
                                           f"Respect Points: {rps[i]}")
                                    )
                    sent = True
                    if i == 20:
                        break

                if sent:
                    # embed.set_footer(text='https://nephritestats.cf')
                    try:
                        await ctx.send(embed=embed)
                    except discord.errors.Forbidden:
                        await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')
                else:
                    await ctx.send('Nu am gasit jucatori online care sa contina nickname-ul introdus.')

    @commands.cooldown(rate=5, per=5.0, type=commands.BucketType.user)
    @commands.command()
    async def clan(self, ctx, *, clan_sau_tag: str):
        """ Afiseaza statisticile clanului specificat (nume sau tag) """

        async with ctx.channel.typing():
            # await ctx.send("incepem")
            with requests.Session() as s:
                index = cauta_clan(clan_sau_tag)
                if not index:  # Nu este clanul in lista, in cazul asta actualizam jsonu
                    actualizeaza_lista_clanuri(s)
                    index = cauta_clan(clan_sau_tag)

                dict_clan, clanidlist, clannamelist, clantaglist = deschide_lista_clanuri()

                try:
                    id_clan = clanidlist[index]
                    tag = clantaglist[index]
                    clanname = clannamelist[index]
                    embed = discord.Embed(title=f"{tag} | {clanname}", color=0x00ff00)
                except TypeError:
                    await ctx.send(content="Nu am putut gasi clanul specificat!")
                    return

                login_panou(s)  # Ne logam pe panou
                url = f"https://rubypanel.nephrite.ro/clan/view/{id_clan}"  # Intram pe pagina clanului
                descriere_raw, _ = scrape_panou(s, url, [{'div': {'id': 'clanDescriptionText'}}], True)
                # soup.prettify().encode('ascii', 'replace')

                try:
                    str(descriere_raw[0])
                except IndexError:  # Incercam sa intram pe un clan care nu mai exista
                    # await ctx.send("DEBUG: Actualizez json")
                    clanidlist.pop(index)  # Scoatem clanul problema
                    clannamelist.pop(index)  # Scoatem clanul problema
                    clantaglist.pop(index)  # Scoatem clanul problema
                    salveaza_lista_clanuri(dict_clan)
                    index = cauta_clan(clan_sau_tag)
                    if not index:  # Nu este clanul in lista, in cazul asta actualizam jsonu
                        actualizeaza_lista_clanuri(s)
                        index = cauta_clan(clan_sau_tag)
                    try:
                        id_clan = clanidlist[index]
                        tag = clantaglist[index]
                        clanname = clannamelist[index]
                        embed = discord.Embed(title=f"{tag} | {clanname}", color=0x00ff00)
                    except TypeError:
                        await ctx.send(content="Nu am putut gasi clanul specificat!")
                        return

                    url = f"https://rubypanel.nephrite.ro/clan/view/{id_clan}"  # Intram pe pagina clanului, IAR

                descriere_raw, f2, soup = scrape_panou(s, url, [{'div': {'id': 'clanDescriptionText'}},
                                                                {'div': {'class': 'col-xs-3'}}], True)
                descriere = str(descriere_raw[0])

                # Vedem daca are HQ locked sau unlocked
                locked = None
                if soup.findAll('i', {'class': 'fa fa-unlock text-green'}):
                    locked = False
                    locked_str = "Unlocked"
                elif soup.findAll('i', {'class': 'fa fa-lock text-red'}):
                    locked = True
                    locked_str = "Locked"

                # print(descriere)
                # Curatam descrierea
                for strToReplace in strToReplaceList:
                    skema_to_replace = ' --> ' if strToReplace == '">' else ''
                    descriere = descriere.replace(strToReplace, skema_to_replace)
                # print(descriere)
                # await ctx.send(descriere)
                # data=[b.string for b in f2[0].findAll('b')]

                data = {tag.text: tag.nextSibling for tag in f2[0].findAll('b')}
                # data = {tag.text: str(tag.nextSibling).replace(':', '').strip() for tag in tags}
                # Posibil sa folosim rand-ul asta ca sa curatam dictionarul
                # Folosim *dictionary comprehension* mai sus la data,
                # scoatem din f2[0] cuz avem un singur element in f2.

                # print(data)
                valori_clan = ''  # Pentru embed mai tz
                iteme = iter(data.items())
                for _ in range(3):  # Sarim peste primele 3 elemente
                    next(iteme)

                for contor, valori in enumerate(iteme, start=1):  # Iteram prind dictionar
                    for valoare in valori:
                        valori_clan += f"{valoare} "
                        if valoare == "Status:":
                            valori_clan += f"{locked_str} "  # Status clanHQ
                    valori_clan += '\n'
                    # print(valoare)
                    if contor == 3:  # Done Clan Info
                        embed.add_field(name='Clan Info', value=valori_clan)
                        valori_clan = ' '
                    elif contor == 7 and locked is not None:  # Done Clan HQ
                        embed.add_field(name='Clan HQ', value=valori_clan)
                        valori_clan = ' '

                embed.add_field(name='Clan Ranks', value=valori_clan.replace(" None", ''))  # Restul, adica Clan Ranks
                if descriere != '':
                    for chunk in chunks(descriere, 1000):
                        embed.add_field(name="Clan Description", value=chunk)
                try:
                    await ctx.send(embed=embed)
                except discord.errors.Forbidden:
                    await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')

    @commands.cooldown(rate=5, per=2.0, type=commands.BucketType.user)
    @commands.command(aliases=["raport"])
    async def raportu(self, ctx, *, servers="all"):
        """ Afiseaza statisticile serverului specificat"""

        await ctx.send("Comanda este in curs de rescriere.")

def setup(bot):
    bot.add_cog(RubyBot(bot))
