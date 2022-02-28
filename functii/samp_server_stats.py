import json
from samp_client.client import SampClient

def get_server_data(server_address):
    try:
        with SampClient(address=server_address, port=7777) as client:
            server_data = client.get_server_info()

        return server_data
    except Exception as e:
        print(e)
        return None

def format_server_data(server_data):
    # server_data = ServerInfo(password=False, players=219, max_players=1000, hostname='ruby.nephrite.ro - rpg server', gamemode='nephrite, 26 Nov 2021 23:00:21', language='RO/EN')
    if not server_data:
        return None, None

    hostname = server_data.hostname

    string_to_return = ""
    string_to_return += "Gamemode: " + server_data.gamemode + "\n"
    string_to_return += "Language: " + server_data.language + "\n"
    string_to_return += "Players: " + str(server_data.players) + "/" + str(server_data.max_players) + "\n"

    return hostname, string_to_return

if __name__ == '__main__':
    # Debug
    with open('storage\\servers_dns.json', 'r') as f:
        servers_dns = json.load(f)

    for server in servers_dns:
        print(server)
        hostname, string_to_return = format_server_data(get_server_data(server))
        print(hostname)
        print(string_to_return)
