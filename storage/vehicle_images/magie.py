import bs4
import requests
import os
from os.path import basename

links = []

def scrape_data():
    with requests.Session() as s:
        r = s.get("https://www.mtasa.com/vehicles/")
        soup = bs4.BeautifulSoup(r.text, "html.parser")

        root = 'https://wiki.multitheftauto.com/'
        r = s.get(root + 'wiki/Vehicle_IDs')

        soup = bs4.BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all('a', href=True):
            if "/wiki/File:" in a['href']:
                links.append(a['href'])
        
        for link in links:
            link = root + link
            print(link)
            r = s.get(link)
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all('a', href=True):
                if "images" in a['href']:
                    link = root + a['href']
                    r = s.get(link)
                    with open(basename(link), "wb") as f:
                        f.write(requests.get(link).content)
                    break


def rename_files():
    # Rename all files to lowercase
    for filename in os.listdir('.'):
        os.rename(filename, filename.lower())

rename_files()