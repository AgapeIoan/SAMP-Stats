import disnake

# Define a simple View that gives us a counter button
class Main_Menu(disnake.ui.View):

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Player Stats", custom_id="stats_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(content="stats", view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Vehicles", custom_id="vehicles_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(content="stats", view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Properties", custom_id="properties_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(content="stats", view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Faction History", custom_id="faction_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(content="stats", view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.primary, label="Clan", custom_id="clan_button")
    async def stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(content="stats", view=self)


        # Define a simple View that gives us a confirmation menu
class Confirm(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @disnake.ui.button(label='Confirm', style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @disnake.ui.button(label='Cancel', style=disnake.ButtonStyle.grey)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()


def lista_butoane_stats(stats=False, vstats=False, bstats=False, fstats=False, cstats=False):
    return disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Player Stats",
            custom_id="stats_button",
            disabled=stats
        )
    
    return ActionRow(
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Player Stats",
            custom_id="stats_button",
            disabled=stats
        ),
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Vehicles",
            custom_id="vehicles_button",
            disabled=vstats
        ),
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Properties",
            custom_id="properties_button",
            disabled=bstats
        ),
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Faction History",
            custom_id="faction_button",
            disabled=fstats
        ),
        disnake.ui.Button(
            style=ButtonStyle.primary,
            label="Clan",
            custom_id="clan_button",
            disabled=cstats
        )
    )

