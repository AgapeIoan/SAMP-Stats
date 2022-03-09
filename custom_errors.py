from disnake.ext import commands

class CommandErrorReport(commands.CommandError):
    def __init__(self, string_to_send, *args, **kwargs):
        self.string_to_send = string_to_send
        super().__init__(*args, **kwargs)
