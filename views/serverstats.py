import disnake

class ServersMenu(disnake.ui.Select):
    message: disnake.Message
    original_author: disnake.User

    def __init__(self, soup: str, original_author = None, message = None, servers_data = None):
        self.soup = soup
        self.original_author = original_author
        self.message = message
        self.servers_data = servers_data

        options = [
            disnake.SelectOption(label='Inapoi', description='Reveniti la meniul principal', emoji='⬅️'),
        ]
        # https://cdn.discordapp.com/emojis/897425271475560481.png?size=44

        # servers_data o sa fie o lista de dictionare, dictionarele continand date legate de server ca in functia raportu din cogs/samp.py
        # Facem un meniu dropdown din lista de servere cu date comprimate.
        # Cand cineva selecteaza un server din dropdown, trimitem embed ca in functia raportu din cogs/samp.py
        # Putem face ca player-ul sa verifice si alte ip-uri, dar aici avem security risc ca poate dam ping la un honeypot si dupa luam flood-ul.
        super().__init__(placeholder='SAMP Servers', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        biz_name = self.values[0]

        if biz_name == "Inapoi":
            za_view = await disable_not_working_buttons(views.mainmenu.MainMenu(self.soup), self.soup)
            za_view.original_author = self.original_author
            za_view.message = self.message
            await interaction.response.edit_message(
                content=f"**Selecteaza o optiune pentru jucatorul `{get_nickname(self.soup)}`:**", embed=None,
                view=za_view)
        else:
            # print("SELF = ", self.bizes)
            for i in self.bizes:
                for k, v in i.items():
                    if v[0] == biz_name:
                        embed = create_biz_embed(i, nickname=get_nickname(self.soup))
                        embed.color = 0x00ff00 if este_player_online(self.soup) else 0xff0000

            await interaction.response.edit_message(embed=embed)