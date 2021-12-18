import json
import disnake

import panou.ruby

def disable_button(buton_fain):
    buton_fain.disabled = True
    buton_fain.style = disnake.ButtonStyle.gray

def enable_buttons(self):
    if len(self.children) > 5:
        self.remove_item(self.children[5])
    for i in self.children:
        if i.style != disnake.ButtonStyle.gray:
            i.disabled = False

def disable_not_working_buttons(view, soup):
    if not panou.ruby.vstats(soup):
        disable_button(view.children[1])
    if not panou.ruby.bstats(soup):
        disable_button(view.children[2])
    if not panou.ruby.fhstats(soup):
        disable_button(view.children[3])
    if not panou.ruby.get_clan_name(soup):
        disable_button(view.children[4])
    return view

def disable_all_buttons(self):
    if len(self.children) > 5:
        self.remove_item(self.children[5])
    for i in self.children:
        i.disabled = True