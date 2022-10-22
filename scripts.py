import asyncio
from functii.debug import print_debug

import panou.ruby.clan as clan

async def main():
    clan_id = 85
    soup = await clan.get_clan_data(clan_id=clan_id)
    clan_members = await clan.get_clan_members(soup)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())