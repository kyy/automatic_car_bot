import requests
from logic.constant import REPORT_PARSE_LIMIT_PAGES, HEADERS_JSON
from logic.decorators import timed_lru_cache


def count_cars_abw(url):
    if url is None:
        return 0
    try:
        r = requests.get(url, headers=HEADERS_JSON).json()
        return int(r['pagination']['total'])
    except Exception as e:
        print(e)
        return 0


@timed_lru_cache(300)
def json_links_abw(url):
    try:
        links_to_json = []
        r = requests.get(url, headers=HEADERS_JSON).json()
        page_count = r['pagination']['pages']
        links_to_json.append(url)
        i = 1
        if page_count >= REPORT_PARSE_LIMIT_PAGES:  # - - - - - - ограничение вывода страниц
            page_count = REPORT_PARSE_LIMIT_PAGES  # - - - - - - ограничение вывода страниц
            while page_count > 1:
                i += 1
                links_to_json.append(f'{url}?page={i}')
                page_count -= 1
        return links_to_json
    except Exception as e:
        print(e)
        return False


def json_parse_abw(json_data, work):
    car = []
    for i in range(len(json_data['items'])):
        r_t = json_data['items'][i]
        url = f"https://abw.by{r_t['link']}"
        if work is False:
            brand = r_t['title'].split(',')[0]
            price = r_t['price']['usd'].replace('USD', '').replace(' ', '')
            city = r_t['city']
            description = r_t['description'].split('/')
            km = description[0].replace(' <br', '').replace(' км', '')
            year = description[1].replace('г.', '').replace('>', '').replace(' ', '')
            dimension = description[2].split(' ')[1]
            motor = description[-4].replace(' ', '')
            transmission = description[-3].replace(' ', '')
            drive = description[-2].replace(' ', '')
            typec = description[-1]
            color = vin = exchange = days = ''
            car.append([
                str(url), 'comment', str(brand), str(price), str(motor), str(dimension),
                str(transmission), str(km), str(year), str(typec), str(drive), str(color), str(vin),
                str(exchange), str(days), str(city)
            ])
        if work is True:
            ...
            # response = requests.get(url, headers=headers)
            # soup = BeautifulSoup(response.content, 'html.parser')
            # time = soup.find('time', {'class': 'time'}).text
            # print(time)
            # car.append([str(url)])
    return car
