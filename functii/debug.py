import datetime

DEBUG = True

def salvam_codul_sursa(cod_intreg):  # merge doar cu atacul in panou efectuat corect
    skemaaa = open('logs ruby/html_debug' + str(datetime.datetime.utcnow()) +
                   '.txt', 'w+', encoding="utf-8")
    skemaaa.write(str(cod_intreg))

def empty_is_none(cuvant):
    try:
        if not cuvant:
            cuvant = "none"
    except IndexError:
        cuvant = "none"
    return cuvant

def chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start + n]

def print_debug(output):
    if DEBUG:
        print(f"{datetime.datetime.now()} | {output}")

def print_log(output):
    print(f"{datetime.datetime.now()} | {output}")

async def send_error_message_to_error_channel(bot, message):
    # get channel by guild id and channel id
    channel = bot.get_guild(921316017584631829).get_channel(921764407535603753)
    # send message to channel
    await channel.send(f"[{datetime.datetime.now()}] " + message)
