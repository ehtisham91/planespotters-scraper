import requests
import bs4 as bs
from xlsxwriter import Workbook
from fake_useragent import UserAgent

header = {'user-agent': UserAgent().chrome}

workbook = Workbook('airlines.xlsx')
worksheet = workbook.add_worksheet()
row_number = 0
worksheet.write(row_number, 0, 'Airline Name')
worksheet.write(row_number, 1, 'ICAO')
worksheet.write(row_number, 2, 'IATA')
worksheet.write(row_number, 3, 'Callsign')
worksheet.write(row_number, 4, 'Country')


def find_all_page_index(soup):
    row_number = 1
    all_airlines = []
    airline_index_divs = soup.find_all('div', attrs={'class': 'pages'})
    airline_index_urls = airline_index_divs[0].find_all('a', href=True)

    # A B C D E F G H.......
    for airline_index in airline_index_urls:
        data = requests.get('https://www.planespotters.net{}'.format(airline_index['href']), headers=header)
        data = bs.BeautifulSoup(data.content, 'lxml')
        airline_index_divs = data.find_all('div', attrs={'class': 'pages'})

        tables = data.findChildren('table')
        rows = tables[0].findChildren('tr')

        for row in rows:
            td = row.find('td')
            if td:
                a = td.find('a')
                if a:
                    all_airlines.append('https://www.planespotters.net{}'.format(a['href']))
                all_columns = row.find_all('td')
                for index, column in enumerate(all_columns):
                    worksheet.write(row_number, index, column.text)
                row_number += 1
        # if pagination exists, start from page 2
        if len(airline_index_divs) > 1:
            airline_index_pages = airline_index_divs[1].find_all('a', href=True)


            # loop over pages 1 2 3 4 5 6 (pagination).....
            for page in airline_index_pages:
                data = requests.get('https://www.planespotters.net{}'.format(page['href']), headers=header)
                data = bs.BeautifulSoup(data.content, 'lxml')
                tables = data.findChildren('table')
                rows = tables[0].findChildren('tr')

                for row in rows:
                    td = row.find('td')
                    if td:
                        a = td.find('a')
                        if a:
                            all_airlines.append('https://www.planespotters.net{}'.format(a['href']))
                        all_columns = row.find_all('td')
                        for index, column in enumerate(all_columns):
                            worksheet.write(row_number, index, column.text)
                        row_number += 1
    workbook.close()


main_page = requests.get('https://www.planespotters.net/airlines', headers=header)
soup = bs.BeautifulSoup(main_page.content, 'lxml')
find_all_page_index(soup)
