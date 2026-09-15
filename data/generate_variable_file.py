from bs4 import BeautifulSoup
import json

soup = BeautifulSoup(open("./data/BARRA2 Parameter Descriptions - NCI Data Collections & Publishing - Opus - NCI Confluence.html", 'r'), 'lxml')

main_content = soup.find('div', id='main-content')
tables = main_content.find_all('table')

out_dict = {} # key -> parameter

for table in tables:
    for table_row in table.find_all('tr'):
        tds = table_row.find_all('td')
        if len(tds) == 0:
            continue # It's the header row
        if len(tds) == 2:
            continue # It's the variable classification table

        c_data = {
            'class': tds[0].text,
            'name': tds[2].text,
            'desc': tds[3].text,
            'mdf': tds[4].text.split(", "),
            'comment': tds[5].text
        }
        var_name = tds[1].text

        if "(" in var_name:
            # We have multiple parameters under this one thing
            var_name = var_name.split("(")[1][:-1].split(",")
        else:
            var_name = [var_name]

        for v in var_name:
            out_dict[v.strip()] = c_data

json.dump(out_dict, open('./src/barra2_downloader/barra_variables.json', 'w'))