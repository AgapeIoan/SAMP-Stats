from functii import *

async def search(ctx, player):
    async with ctx.channel.typing():
        with grequests.Session() as s:
            url = f"https://earthpanel.og-times.ro/search?name={player}"
            skema = s.get(url, headers=headers)
            hei = skema.json()
            if not hei:
                await ctx.send("test navem")
            else:
                await ctx.send("test avem")


async def stats(ctx, player):
    player = vezi_favorit(player, ctx)
    if not player:
        await ctx.send("```.[stats|check|status] <player>\n\nVerifica statisticile jucatorului specificat ```")
        return

    async with ctx.channel.typing():
        with grequests.Session() as s:
            """
            url = f"https://earthpanel.og-times.ro/search?name={player}"
            skema = s.get(url, headers=headers)
            skema = skema.json()

            if not skema:
                await ctx.send(
                    'Nu am putut gasi jucatorul specificat. Verifica daca ai introdus corect nickname-ul!')
                return
            # Nu mai punem else cuz oricum se opreste programul la kkt-ul anterior
            nickname = skema[0]['nickname']
            """
            nickname = player



            lista_valori_scrape = [
                {'div': {'class': 'col-lg-12 col-xl-6'}},
                {'i': {'class': 'fa fa-circle txt-success'}},
                {'div': {'class': 'technical-skill'}},
                {'div': {'class': 'alert alert-danger'}}
            ]

            url = f'https://earthpanel.og-times.ro/profile/{nickname}'
            psot, logat, skills, banat, soup = scrape_panou(s, url, lista_valori_scrape, True)

            # Datele legate de player
            data_key = [
                [th.text for th in tr.find_all('th')]
                for table in psot for tr in table.find_all('tr')
            ]
            data_value = [
                [td.text for td in tr.find_all('td')]
                for table in psot for tr in table.find_all('tr')
            ]

            # Setam online/offline
            if logat:
                online_status = 'Online'
            else:
                online_status = 'Offline'

            # Cream link embed pentru trimis pe discord
            embed = discord.Embed(
                title=nickname, description="Status: " + online_status, color=0x00ff00)

            # print(banat)
            if banat:
                banlist = banat[0].findAll('b')
                print(banlist)
                print(str(banlist[1]).replace('<b>', '').replace('</b>', ''))
                motiv_ban = f"By {str(banlist[1]).replace('<b>', '').replace('</b>', '').strip()}\n"
                motiv_ban += f"On {str(banlist[2]).replace('<b>', '').replace('</b>', '').strip()}\n"
                motiv_ban += f"Reason: {str(banlist[3]).replace('<b>', '').replace('</b>', '').strip()}\n"
                if "permanent" not in str(banlist[-1]):
                    motiv_ban += f"Expire on {str(banlist[5]).replace('<b>', '').replace('</b>', '').strip()}"
                else:
                    motiv_ban += "Permanent ban."
                embed.add_field(name="Banned", value=motiv_ban)
            # Iteram prin valorile de la stats si facem campuri de valori
            for keye, valoare in zip(data_key, data_value):
                val = valoare[0].strip()
                cheie = keye[0].strip()
                # print(f"{cheie} | {val}")
                embed.add_field(name=cheie, value=val)

            # await ctx.send(f'{nickname_player} | {player_online} | {server_de_provenienta}')

            embed.set_footer(text="Earth OG-Times | earth.og-times.ro:7777")
            try:
                await ctx.send(embed=embed)
            except discord.errors.Forbidden:
                await ctx.send('Am nevoie de permisiuni sa trimit **Embed Links**!')
