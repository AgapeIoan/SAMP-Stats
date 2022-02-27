path = "_SampStats_logs (3).txt"

with open(path, "r", encoding='utf-8') as f:
    lines = f.readlines()

lines_to_remove = ["Ignoring exception in command None", "CommandNotFound:"]

with open(path, "w", encoding='utf-8') as f:
    for line in lines:
        if "disnake.ext.commands.errors.CommandNotFound" not in line:
            f.write(line)
