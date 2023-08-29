from datetime import datetime

import requests
from lxml import etree

from logic.constant import REPORT_PARSE_LIMIT_PAGES, HEADERS_JSON, HEADERS, PARSE_LIMIT_PAGES
from logic.decorators import timed_lru_cache


@timed_lru_cache(300)
def count_cars_abw(url):
    if url is None:
        return 0
    try:
        r = requests.get(url, headers=HEADERS_JSON).json()
        return int(r["pagination"]["total"])
    except Exception as e:
        print(e, '[abw_by.count_cars_abw]')
        return 0


@timed_lru_cache(300)
def json_links_abw(url):
    try:
        links_to_json = []
        r = requests.get(url, headers=HEADERS_JSON).json()
        page_count = r["pagination"]["pages"]
        links_to_json.append(url)
        i = 1
        if page_count >= REPORT_PARSE_LIMIT_PAGES:  # - - - - - - ограничение вывода страниц
            page_count = REPORT_PARSE_LIMIT_PAGES  # - - - - - - ограничение вывода страниц
            while page_count > 1:
                i += 1
                links_to_json.append(f"{url}?page={i}")
                page_count -= 1
        return links_to_json
    except Exception as e:
        print(e, '[abw_by.json_links_abw]')
        return False


def html_links_abw(html, work):
    try:
        links_to_html = []
        r = requests.get(html, headers=HEADERS).text
        dom = etree.HTML(str(r))

        cars = int(dom.xpath('//*[@class="list-proposal__quantity-bold"]/text()')[0].replace('\xa0', ''))
        page_count = cars // 20 if cars % 20 == 0 else cars // 20 + 1

        links_to_html.append(html)
        i = 1
        limit_page = PARSE_LIMIT_PAGES if work is True else REPORT_PARSE_LIMIT_PAGES
        if page_count >= limit_page:  # - - - - - - ограничение вывода страниц
            page_count = limit_page  # - - - - - - ограничение вывода страниц
            while page_count > 1:
                i += 1
                links_to_html.append(f"{html}?page={i}")
                page_count -= 1
        return links_to_html
    except Exception as e:
        print(e, '[abw_by.html_links_abw]')
        return False


def html_parse_abw(dom, work):
    car = []

    ln = len(dom.xpath('//*[@class="classified-card__title"]'))

    for i in range(ln):

        brand = dom.xpath('//*[@class="classified-card__title"]/text()')[i].split(', ')[0]
        price = dom.xpath('//*[@class="classified-card__usd"]/text()')[i].replace(' ', '').replace('≈', '').replace(
            'USD', '')
        city = dom.xpath('//*[@class="classified-card__city"]/text()')[i]
        km = dom.xpath('//*[@class="classified-card__description"]/text()[1]')[i].replace(' км', '')
        info = dom.xpath('//*[@class="classified-card__description"]/text()[2]')[i].split(' / ')
        year = info[0].replace(' ', '').replace('г.', '')
        dimension = info[1].split(' ')[0].replace('дизель', '').replace('бензин', '')
        drive = info[-2]
        transmission = info[-3]
        motor = info[-4]
        id_car = dom.xpath('//*[@class="lower-controls"]/button[1]/@id')[i]
        url = f'https://abw.by/cars/detail/{id_car}'
        data = dom.xpath('//*[@class="lower-time"]/text()')[i]

        published = ''
        days = ''
        typec = ''
        color = ''
        vin = ''
        exchange = ''

        if work is True:
            pass
        # fresh_minutes = datetime.now() - datetime.strptime(published, "%Y-%m-%dT%H:%M")
        # fresh_minutes = fresh_minutes.total_seconds() / 60
        # if fresh_minutes <= WORK_PARSE_CARS_DELTA * 60 + 180:
        #     car.append([str(url), str(price)])

        else:
            car.append(
                [
                    str(url),
                    "comment",
                    str(brand),
                    str(price),
                    str(motor),
                    str(dimension),
                    str(transmission),
                    str(km),
                    str(year),
                    str(typec),
                    str(drive),
                    str(color),
                    str(vin),
                    str(exchange),
                    str(days),
                    str(city),
                ]
            )
    return car


def json_parse_abw(json_data, work):
    car = []
    for i in range(len(json_data["items"])):
        r_t = json_data["items"][i]
        url = f"https://abw.by{r_t['link']}"
        if work is False:
            brand = r_t["title"].split(",")[0]
            price = r_t["price"]["usd"].replace("USD", "").replace(" ", "")
            city = r_t["city"]
            description = r_t["description"].split("/")
            km = description[0].replace(" <br", "").replace(" км", "")
            year = description[1].replace("г.", "").replace(">", "").replace(" ", "")
            dimension = description[2].split(" ")[1]
            motor = description[-4].replace(" ", "")
            transmission = description[-3].replace(" ", "")
            drive = description[-2].replace(" ", "")
            typec = description[-1]
            color = vin = exchange = days = ""
            car.append(
                [
                    str(url),
                    "comment",
                    str(brand),
                    str(price),
                    str(motor),
                    str(dimension),
                    str(transmission),
                    str(km),
                    str(year),
                    str(typec),
                    str(drive),
                    str(color),
                    str(vin),
                    str(exchange),
                    str(days),
                    str(city),
                ]
            )
        if work is True:
            pass
    return car
