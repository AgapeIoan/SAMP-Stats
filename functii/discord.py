import disnake
import panou.ruby

async def disable_button(buton_fain):
    buton_fain.disabled = True
    buton_fain.style = disnake.ButtonStyle.gray


async def enable_buttons(self):
    if len(self.children) > 6:
        self.remove_item(self.children[6])
    for i in self.children:
        if i.style != disnake.ButtonStyle.gray:
            i.disabled = False


async def disable_not_working_buttons(view, soup):
    if not panou.ruby.vstats(soup):
        await disable_button(view.children[1])
    if not panou.ruby.bstats(soup):
        await disable_button(view.children[2])
    if not panou.ruby.fhstats(soup):
        await disable_button(view.children[3])
    if "Civilian" in await panou.ruby.get_faction_name(soup):
        await disable_button(view.children[4])
    if not panou.ruby.get_clan_name(soup):
        await disable_button(view.children[5])
    return view


async def disable_all_buttons(self):
    if len(self.children) > 6:
        self.remove_item(self.children[6])
    for i in self.children:
        i.disabled = True
