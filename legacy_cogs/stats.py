import discord
from functii import *


def vezi_asociere(player, ctx):
    if not player:
        player = este_asociat(ctx.author.id)
        if player:
            player = str(player)
    return player


class RubyStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.cooldown(rate=10, per=5.0, type=commands.BucketType.user)
    @commands.command(aliases=['bstatus', 'bcheck'])
    async def bstats(self, ctx, *, nickname_sau_biz_sau_id):
        # TODO http://theautomatic.net/2019/01/19/scraping-data-from-javascript-webpage-python/ , de implementat suport pentru js pentru productie
        """Verifica statisticile biz-ului specificat"""
        # style_pret_productie_biz = r"""-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: end; font-family: sans-serif; font-size: 12px; font-weight: normal;"""
        async with ctx.channel.typing():
            if este_mentenanta():
                if ctx.guild.id != id_server_home:
                    motiv = este_mentenanta()
                    await ctx.send(f"Comanda dezactivata temporar! Motiv: {motiv}")
                    return
                else:
                    pass

            gasit = False  # Pentru daca gasim biz

            with requests.Session() as s:
                url = "https://rubypanel.nephrite.ro/businesses"
                lista_valori_scrape = [
                    {'div': {'class': 'col-xs-12'}}
                ]
                f2, _ = scrape_panou(s, url, lista_valori_scrape, True)
                # print(style_pret_productie_biz)
                # f1 = soup.findAll('div', {'class': 'chart'})
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                embed = discord.Embed(title="Businesses", color=0x00ff00)

                for bizstats in data[1:]:
                    id = bizstats[0]
                    descriere = bizstats[1]
                    tip = bizstats[2]
                    owner = bizstats[3]
                    fee = bizstats[5]

                    if nickname_sau_biz_sau_id in id or nickname_sau_biz_sau_id.lower() in owner.lower() or nickname_sau_biz_sau_id.lower() in tip.lower():
                        gasit = True
                        embed.add_field(name=tip,
                                        value=(f"ID: {id}\n" +
                                               f"Name: {descriere}\n" +
                                               f"Owner: {owner}\n" +
                                               f"Fee: {fee}")
                                        )

                if not gasit:
                    await ctx.send("Nu am putut gasi business-uri dupa id-ul, owner-ul sau tipul specificat!")
                else:
                    try:
                        await ctx.send(embed=embed)
                        # print(f"trimis pe {ctx.channel.name}")
                    except discord.errors.Forbidden:
                        await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')

    @commands.cooldown(rate=5, per=5.0, type=commands.BucketType.user)
    @commands.command(aliases=['cstatus', 'ccheck'])
    async def cstats(self, ctx, player: str = None):
        """Verifica stats din clanul jucatorului specificat"""

        player = vezi_asociere(player, ctx)
        if not player:
            await ctx.send("```.[cstats|ccheck|cstatus] <player>\n\nVerifica stats din clanul jucatorului specificat```")
            return

        async with ctx.channel.typing():
            if este_mentenanta():
                if ctx.guild.id != id_server_home:
                    motiv = este_mentenanta()
                    await ctx.send(f"Comanda dezactivata temporar! Motiv: {motiv}")
                    return
                else:
                    pass

            with requests.Session() as s:
                lista_valori_scrape = [
                    {'div': {'class': 'col-md-8'}}
                ]
                url = f"https://rubypanel.nephrite.ro/profile/{player}"

                f2, soup = scrape_panou(s, url, lista_valori_scrape, True)
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                numar_de_generari_plus()

                nickname_player = get_nickname(soup, player)
                if nickname_player == "":
                    await ctx.send("Nu am putut gasi jucatorul specificat!")
                    return  # Gata comanda

                # print(data)

                if "Clan" not in data[4][0]:
                    await ctx.send("Jucatorul specificat nu face parte dintr-un clan!")
                else:
                    clan = data[4][1]
                    clan_org = clan[:clan.find(",")]  # Scoate ", rank x" din string
                    # await ctx.send(clan_org)

                    # Il trimitem la clanuri

                    # Citim jsonu cu liste info clanuri
                    with open("clans.json", "r+", encoding='utf-8') as clanurilista:
                        dict_clan = json.load(clanurilista)
                        clanidlist = dict_clan.get("clanid")
                        clannamelist = dict_clan.get("clanname")
                        clantaglist = dict_clan.get("clantag")

                    if clan_org not in clannamelist:  # Nu este clanul in lista, in cazul asta actualizam jsonu
                        # url = "https://rubypanel.nephrite.ro/clan/list"
                        # FACEM LISTA DE CLANURI, LE PUNEM DUPA INTR-UN JSON CARE IL ACTUALIZAM REGULAT
                        lista_valori_scrape = [
                            {'div': {'class': 'box-body table-responsive'}}
                        ]
                        url = "https://rubypanel.nephrite.ro/clan/list"

                        f2 = scrape_panou(s, url, lista_valori_scrape)
                        f2 = f2[0]
                        data = [
                            [td.text for td in tr.find_all('td')]
                            for table in f2 for tr in table.find_all('tr')
                        ]

                        for clan in data[1:]:  # Am pus interval [1:] ca sa sara peste data[0] aka variabila goala.
                            clanid = str(clan[0])
                            clanname = str(clan[1])
                            clantag = str(clan[2])
                            # clanslots = str(clan[3])
                            # clanrip = str(clan[4]) # Zile pana cand expira

                            if clanid in clanidlist:  # In caz de nume sau tag schimbat
                                index = clanidlist.index(clanid)
                                clannamelist[index] = clanname
                                clantaglist[index] = clantag

                            if clanid not in clanidlist:  # In caz ca dam de ceva nou, bagam in lista
                                clanidlist.append(clanid)
                                clannamelist.append(clanname)
                                clantaglist.append(clantag)

                        with open("clans.json", "w+", encoding='utf-8') as clanurilista:
                            json.dump(dict_clan, clanurilista, indent=4)  # Salvam json

                    index = clannamelist.index(clan_org)

                    login_panou(s)

                    id_clan: object = clanidlist[index]
                    tag = clantaglist[index]
                    url = f"https://rubypanel.nephrite.ro/clan/view/{id_clan}"
                    # await ctx.send(url)
                    # E ora 1:20 AM continui mai tz haipa
                    # A trecut aproape o luna aparent, abia acuma ma pun sa continui,
                    # aparent atat inseamna "mai tz" =)))

                    lista_valori_scrape = [
                        {'div': {'class': 'col-xs-5'}}
                    ]  # Cautam stats, recomand sa iei cod de la fstats sau sistem de rankup
                    f2, soup = scrape_panou(s, url, lista_valori_scrape, True) # Punem soup ca avem un singur element
                    # Si se buguieste

                    #r = s.get(url, headers=headers)
                    #soup = BeautifulSoup(r.content, 'html5lib')
                    #f2 = soup.findAll('div', {
                    #    'class': 'col-xs-5'})

                    data = [
                        [td.text for td in tr.find_all('td')]
                        for table in f2 for tr in table.find_all('tr')
                    ]
                    # TODO De adaugat logo clan nush
                    embed = discord.Embed(title=f"{tag} | {clan_org}", color=0x00ff00)
                    # await ctx.send(nickname_player)
                    for i in range(len(data)):
                        if i == 0:
                            continue
                        # await ctx.send(f"{data[i][1].lower()} ||| {nickname_player.lower()}")
                        if nickname_player.lower() not in data[i][1].lower():
                            continue
                        else:
                            rank = data[i][0]
                            nume = data[i][1]
                            bani = data[i][2]
                            zile = data[i][3]
                            ore = data[i][4]
                            embed.add_field(name=nume,
                                            value=f"Rank: {rank}\nZile: {zile}\nBani seif: {bani}\nOre last 7: {ore}")
                    try:
                        await ctx.send(embed=embed)
                        await ctx.send(embed=deprecacy_notify(ctx))
                    except discord.errors.Forbidden:
                        await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')


    @commands.cooldown(rate=5, per=5.0, type=commands.BucketType.user)
    @commands.command(aliases=['fcheck', 'fstatus'])
    async def fstats(self, ctx, player: str = None):
        """ Verifica stats din factiunea jucatorului specificat"""
        player = vezi_asociere(player, ctx)
        if not player:
            await ctx.send("```.[fstats|fcheck|fstatus] <player>\n\nVerifica stats din factiunea jucatorului specificat```")
            return

        async with ctx.channel.typing():
            if este_mentenanta():
                if ctx.guild.id != id_server_home:
                    motiv = este_mentenanta()
                    await ctx.send(f"Comanda dezactivata temporar! Motiv: {motiv}")
                    return
                else:
                    pass
            players = player.split()

            with requests.Session() as s:
                numes = []
                ranks = []
                fws = []
                ziles = []
                lasts = []
                raports = []
                uninvites = []

                for player in players:  # UN SINGUR PLAYER DEOCAMDATA
                    lista_valori_scrape = [
                        {'div': {'class': 'col-md-8'}}
                    ]
                    url = f"https://rubypanel.nephrite.ro/profile/{player}"
                    f2, soup = scrape_panou(s, url, lista_valori_scrape, True)
                    data = [
                        [td.text for td in tr.find_all('td')]
                        for table in f2 for tr in table.find_all('tr')
                    ]

                    numar_de_generari_plus()

                    if not data:
                        await ctx.send("Jucatorul introdus nu exista! Verifica daca ai introdus nickname-ul corect.")
                        break

                    nickname_player = get_nickname(soup, player)

                    factiune_raw = data[0][1]
                    factiune = factiune_raw[:factiune_raw.find(",")]

                    # print(data)

                    with open("factiuni.json", "r+") as fp:
                        dict_factiuni = json.load(fp)
                        factiuni_list = dict_factiuni.get("factiune")

                    id_factiune = factiuni_list.index(factiune)
                    if id_factiune == 0:
                        embed = discord.Embed(
                            title="Statistici factiune", color=0x00ff00)
                        embed.add_field(name=nickname_player,
                                        value="Factiune: Civilian Mafia")
                        try:
                            await ctx.send(embed=embed)
                        except discord.errors.Forbidden:
                            await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')
                        break

                    # login_panou(s) # NU TRB LOGIN SA VAD MEMBRII

                    url = f"https://rubypanel.nephrite.ro/faction/members/{id_factiune}"
                    lista_valori_scrape = [
                        {'div': {'class': 'col-md-12'}}
                    ]
                    f2, _ = scrape_panou(s, url, lista_valori_scrape, True)
                    # print(url)
                    data = [
                        [td.text for td in tr.find_all('td')]
                        for table in f2 for tr in table.find_all('tr')
                    ]

                    # print(data)

                    for i in range(1, len(data)):
                        skema = data[i]

                        numes.append(skema[0])
                        ranks.append(skema[1])
                        fws.append(skema[2])
                        ziles.append(skema[3])
                        lasts.append(skema[4])
                        raports.append(skema[5])
                        uninvites.append(skema[6])

                    embed = discord.Embed(
                        title="Statistici factiune", color=0x00ff00)

                    for i in range(len(numes)):
                        if player.lower() in numes[i].lower():
                            rank = ranks[i].strip('\n')
                            fw = fws[i].strip('\n')
                            zile = ziles[i].strip('\n')
                            last = lasts[i].strip('\n')
                            raport = raports[i].strip('\n')
                            uninvite = uninvites[i].strip('\n')

                            raportu = ""
                            j = 0
                            while True:
                                if "Ucideri:" in raportu:
                                    raportu = raportu[:-4] + raportu[-2:]

                                raportu += raport[j].upper()
                                j += 1
                                while ":" not in raport[j]:
                                    raportu += raport[j]
                                    j += 1
                                try:
                                    while not raport[j].isalpha():
                                        raportu += raport[j]
                                        j += 1
                                except IndexError:
                                    raportu += "\n"
                                    break

                                raportu += "\n"
                                # print(raportu)

                            valoare = ""
                            valoare += f"{factiune}\n"
                            valoare += f"Rank: {rank}\n"
                            valoare += f"FW: {fw}\n"
                            if zile[1:3] == "00":  # Multiplu de 100
                                zile += " (gg mane)"
                            valoare += f"{zile}\n"
                            valoare += f"Last online: {last}\n"
                            valoare += f"{raportu}\n"
                            valoare += f"Reset: {uninvite}\n"

                            # print(f"{numes[i]} || {valoare}")

                            embed.add_field(name=numes[i], value=valoare)

                    try:
                        await ctx.send(embed=embed)
                    except discord.errors.Forbidden:
                        await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')

    @commands.cooldown(rate=5, per=5.0, type=commands.BucketType.user)
    @commands.command(aliases=['vcheck', 'vstatus'])
    async def vstats(self, ctx, player: str = None, *, masini="toate"):
        """ Verifica vehiculele jucatorului specificat """
        player = vezi_asociere(player, ctx)
        if not player:
            await ctx.send("```.[vstats|vcheck|vstatus] <player>\n\nVerifica vehiculele jucatorului specificat ```")
            return

        trimis = False

        async with ctx.channel.typing():
            if este_mentenanta():
                if ctx.guild.id != id_server_home:
                    motiv = este_mentenanta()
                    await ctx.send(f"Comanda dezactivata temporar! Motiv: {motiv}")
                    return
                else:
                    pass

            masini = masini.split()

            with requests.Session() as s:
                lista_valori_scrape = [
                    {'div': {'class': 'col-md-8'}},
                    {'h3': {'class': 'profile-username'}}
                ]
                url = f"https://rubypanel.nephrite.ro/profile/{player}"

                f2, user_name_panou, soup = scrape_panou(s, url, lista_valori_scrape, True)
                f2 = soup.findAll('div', {'class': 'col-md-8'})
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in f2 for tr in table.find_all('tr')
                ]

                nickname_player, player_online, server_de_provenienta = este_player_online(
                    str(user_name_panou), player)

                embed = discord.Embed(
                    title=nickname_player, description="Status: " + player_online, color=0x00ff00)
                if server_de_provenienta == "ruby":
                    embed.set_thumbnail(
                        url="https://i.imgur.com/mZvN9jZ.png")
                else:
                    embed.set_thumbnail(
                        url="https://i.imgur.com/jnTomOg.png")

                i = 0
                nrtrm = 0
                for manevra in data:
                    i += 1
                    if not manevra:
                        break
                for manevra in data[i:]:  # Amu incepem de la masini
                    if not manevra:
                        break  # Navem masina ramasa
                    valoare = ''

                    lista_masina = manevra[1:5]
                    vehicle_name = lista_masina[0]
                    km = lista_masina[1]
                    neon = lista_masina[2]
                    days = lista_masina[3]

                    # Gasim vip textu
                    temp = vehicle_name.find("VIP")
                    vip_text = vehicle_name[temp:-1]
                    if vip_text:
                        vehicle_name = vehicle_name.replace(vip_text, '')
                        valoare += vip_text + '\n'
                    # Gasim formely
                    temp = vehicle_name.find("Formerly")
                    formely_text = vehicle_name[temp:-1]
                    if formely_text:
                        vehicle_name = vehicle_name.replace(formely_text, '')
                        valoare += formely_text.replace('ID', ' ID') + '\n'
                    valoare += (f"{days}\n" +
                                f"{km}\n" +
                                f"Neon: {neon}\n")

                    # print(masini)
                    if masini == ['toate']:
                        avem = True
                    else:
                        for masina in masini:
                            if masina.lower() in vehicle_name.lower():
                                avem = True
                            else:
                                avem = False

                    if not avem:
                        continue
                    embed.add_field(name=vehicle_name,
                                    value=valoare)
                    nrtrm += 1
                    if nrtrm == 20:
                        trimis = True
                        nrtrm = 0
                        try:
                            await ctx.send(embed=embed)
                            await ctx.send(embed=deprecacy_notify(ctx))
                            embed = discord.Embed(
                                title=nickname_player, description="Status: " + player_online, color=0x00ff00)
                        except discord.errors.Forbidden:
                            await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')
                            return
                try:
                    if not nrtrm and trimis:  # Sa nu trimita mesaj gol
                        return
                    elif nrtrm:
                        await ctx.send(embed=embed)
                        await ctx.send(embed=deprecacy_notify(ctx))
                    elif not nrtrm and not trimis:
                        await ctx.send(f"**{nickname_player}** nu detine nici o masina!")
                except discord.errors.Forbidden:
                    await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')
                    return

    ################################################################################################################
    ################################################################################################################

    @commands.command(aliases=['check', 'status'])
    @commands.cooldown(rate=5, per=5.0, type=commands.BucketType.user)
    async def stats(self, ctx, player: str = None):
        """ Verifica statisticile jucatorului specificat """
        player = vezi_asociere(player, ctx)
        if not player:
            await ctx.send("```.[stats|check|status] <player>\n\nVerifica statisticile jucatorului specificat ```")
            return

        async with ctx.channel.typing():
            if este_mentenanta():
                if ctx.guild.id != id_server_home:
                    motiv = este_mentenanta()
                    await ctx.send(f"Comanda dezactivata temporar! Motiv: {motiv}")
                    return
                else:
                    pass
            with requests.Session() as s:
                lista_valori_scrape = [
                    {'div': {'class': 'col-md-8'}},
                    {'h3': {'class': 'profile-username'}},
                    {'div': {'class': 'col-md-12 col-lg-12'}},
                    {'div': {'class': 'alert bg-red'}}
                ]

                url = f'http://rubypanel.nephrite.ro/profile/{player}'
                psot, user_name_panou, badges_raw, ban_status_raw = scrape_panou(s, url, lista_valori_scrape)

                if not psot:
                    await ctx.send(
                        'Nu am putut gasi jucatorul specificat. Verifica daca ai introdus corect nickname-ul!')
                    return

                try:
                    ban_string = ban_status_raw[0].findAll('h4')
                    # TODO De infrumusetat urm secventa de linii de cod cand n-am cf
                    detrmban = ban_string[0].nextSibling
                    motiv_string_lista = []
                    for _ in range(5):
                        motiv_string_lista.append(detrmban)
                        detrmban = detrmban.nextSibling
                except IndexError:
                    motiv_string_lista = []

                nickname_player, player_online, server_de_provenienta = este_player_online(
                    str(user_name_panou), player)
                # await ctx.send(f'{nickname_player} | {player_online} | {server_de_provenienta}')

                embed = discord.Embed(
                    title=nickname_player, description="Status: " + player_online, color=0x00ff00)
                if server_de_provenienta == "ruby":
                    embed.set_thumbnail(url="https://i.imgur.com/mZvN9jZ.png")
                else:
                    embed.set_thumbnail(url="https://i.imgur.com/jnTomOg.png")

                # Datele legate de player
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in psot for tr in table.find_all('tr')
                ]

                # Daca e banat bagam si de aia
                if motiv_string_lista:
                    autor_ban = str(motiv_string_lista[1])[str(motiv_string_lista[1]).find(r'>') + 1:-4]
                    lungime_ban = str(motiv_string_lista[2])[4:-10]  # Nu e lungime, e defapt data cand so dat dar ayaye
                    motiv_ban = str(motiv_string_lista[3])[3:-4]
                    expira_ban = str(motiv_string_lista[4])[str(motiv_string_lista[4]).find("expire") + 6:]
                    de_trm_ban = f"By {autor_ban}\nOn {lungime_ban}\nReason: {motiv_ban}\nExpire {expira_ban}"
                    embed.add_field(name="Banned", value=de_trm_ban)
                    # await ctx.send(f'DEBUG: Am adaugat name=Banned value={de_trm_ban}')

                # Bagam badges sa fie treaba buna
                badges_de_trimis = ''
                data_badges = badges_raw[0].findAll('i')
                for badge in data_badges:
                    badges_de_trimis += str(badge.nextSibling).title() + '\n'
                if data_badges:
                    embed.add_field(name="Badges", value=badges_de_trimis)
                    # await ctx.send(f'DEBUG: Am adaugat name=Badges value={badges_de_trimis}')
                # Amu bagam datele playerului
                for date in data:
                    try:
                        nume = date[0]
                        valoare = date[1]
                        if not nume:
                            break
                        # print(f"{nume} | {valoare}")
                        embed.add_field(name=nume, value=valoare)
                        # await ctx.send(f'DEBUG: Am adaugat name={nume} value={valoare}')
                    except IndexError:
                        pass

                try:
                    await ctx.send(embed=embed)
                    await ctx.send(embed=deprecacy_notify(ctx))
                except discord.errors.Forbidden:
                    await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')


def setup(bot):
    bot.add_cog(RubyStats(bot))

