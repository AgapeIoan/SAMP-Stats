import json
import requests
import os
import aiohttp
import asyncio

from bs4 import BeautifulSoup

url = "https://rubypanel.nephrite.ro/faction/logs/13?page=" # max page is 120

headers = {
    "user-agent": "Mozilla/5.0 (https://discord.gg/bmfRfePXm7; CPU SAMP_Stats_Rewrite d.py_2.0 ) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/618076658678628383 Safari/537.36 "
}

async def main():
    with open("logs.txt", "w") as f:
        async with aiohttp.ClientSession(headers=headers) as session:
            for i in range(1, 121):
                url = "https://rubypanel.nephrite.ro/faction/logs/13?page=" + str(i)
                print("Scrapping page " + str(i))
                async with session.get(url) as response:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                f2 = soup.findAll('div', {'class': 'col-md-10'})
                data = [
                    [td.text for td in tr.find_all('td')]
                    for table in [f2[0]] for tr in table.find_all('tr')
                ]

                for i in data:
                    timestamp, log = i
                    f.write(f"{timestamp} | {log}\n")



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())