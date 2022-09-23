import json
import requests
import os
import aiohttp
import asyncio

from bs4 import BeautifulSoup

url = "http://192.168.0.254/"

headers = {
    "user-agent": "Mozilla/5.0 (https://discord.gg/bmfRfePXm7; CPU SAMP_Stats_Rewrite d.py_2.0 ) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/618076658678628383 Safari/537.36 "
}

async def main():
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                # check response code
                if response.status != 200:
                    print(f"Error: {response.status}")
                    return
        except aiohttp.client_exceptions.ClientConnectorError:
            print("Error: Connection refused")
            return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())