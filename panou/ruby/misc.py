def get_aplicants(soup):
    # The soup should represent https://rubypanel.nephrite.ro/faction/applications/{FACTION_INDEX}
    f2 = soup.findAll('div', {'class': 'col-md-8'})
    data = [
        [td.text for td in tr.find_all('td')]
        for table in [f2[0]] for tr in table.find_all('tr')
    ]

    aplicatii = []

    for i in range(4):
        aplicatii.append([]) # Aplicatii noi
        for j in data[i+1:]:
            if not j: 
                break
            aplicatii[i].append(j)
            data.remove(j)

    # aplicatii_noi, aplicatii_acceptate, aplicatii_invitate, aplicatii_respinse = aplicatii

    return aplicatii
