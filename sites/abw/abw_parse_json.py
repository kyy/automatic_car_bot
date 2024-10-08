import asyncio
import logging

from aiohttp import ClientSession
from lxml import etree
from logic.constant import REPORT_PARSE_LIMIT_PAGES, HEADERS, PARSE_LIMIT_PAGES
from datetime import datetime, timedelta


def abw_data(data: str):
    mon = {
        'Сентября': 'Sep',
        'Октября': 'Oct',
        'Ноября': 'Nov',
        'Декабря': 'Dec',
        'Января': 'Jan',
        'Февраля': 'Feb',
        'Марта': "Mar",
        'Апреля': 'Apr',
        'Мая': 'May',
        'Июня': 'Jun',
        'Июля': 'Jul',
        'Августа': 'Aug',
    }
    wee = {
        'Понедельник': 1,
        'Вторник': 2,
        'Среда': 3,
        'Четверг': 4,
        'Пятница': 5,
        'Суббота': 6,
        'Воскресенье': 7,
    }
    d = datetime.today()
    data_split = data.split(' ')
    num = data_split[0].replace(',', '')
    num1 = data_split[1]
    num2 = data_split[-1]
    if 'секунд' in data:
        d = d
    elif 'несколько минут' in data:
        d = d - timedelta(minutes=2)
    elif 'минут' in data and type(int(num)) is int:
        d = d - timedelta(minutes=int(num))
    elif 'часов' in data and type(int(num)) is int:
        d = d - timedelta(hours=int(num))
    elif 'дней' in data and type(int(num)) is int:
        d = d - timedelta(days=int(num))
    elif 'Сегодня' in data:
        h, m = num2.split(':')
        d = d - timedelta(hours=int(h), minutes=int(m))
    elif 'Вчера' in data:
        h, m = num2.split(':')
        d = d - timedelta(days=1, hours=int(h), minutes=int(m))
    elif num in [i for i in wee.keys()]:
        h, m = num2.split(':')
        days = d.isoweekday() - wee[num]
        d = d - timedelta(days=days, hours=int(h), minutes=int(m))
    elif num1 in [i for i in mon.keys()]:
        data = data.replace(num1, mon[num1])
        d = datetime.strptime(data, '%d %b %Y')
    return d


async def count_cars_abw(url, session):
    if url is None:
        return 0
    try:
        async with session.get(url=url, headers=HEADERS) as resp:
            r = await resp.json(content_type=None)
            return int(r["pagination"]["total"])
    except Exception as e:
        logging.error(f'<count_cars_abw> {e}')
        return 0


async def json_links_abw(url, session):
    try:
        links_to_json = []
        async with session.get(url=url, headers=HEADERS) as resp:
            r = await resp.json(content_type=None)
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
        logging.error(f'<json_links_abw> {e}')
        return False


async def html_links_abw(html, work):
    try:
        links_to_html = []
        async with ClientSession as session:
            async with session.get(url=html, headers=HEADERS) as resp:
                r = resp.text()
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


def html_links_cars_abw(dom):
    links_to_html = []
    ln = len(dom.xpath('//*[@class="classified-card__title"]'))
    for j in range(ln):
        id_car = dom.xpath('//*[@class="lower-controls"]/button[1]/@id')[j]
        url = f'https://abw.by/cars/detail/{id_car}'
        links_to_html.append(url)
    return links_to_html


def html_parse_abw(dom, work):
    car = []

    brand = dom.xpath('//*[@class="header-title"]/text()')[0].split(', ')[0].replace('Продажа ', '')
    price = dom.xpath('//*[@class="price-usd"]/text()')[0].replace(' ', '').replace('≈', '').replace('USD', '')
    city = dom.xpath('//*[@class="city"]/text()')[0]
    km = dom.xpath('//*[@class="description"]/text()[1]')[0].replace(' км', '')
    info = dom.xpath('//*[@class="description"]/text()[2]')[0].split(' / ')

    dimension = info[1].replace(' л', '')
    drive = info[-1]
    transmission = info[-2]
    motor = info[3]
    year = ''

    id_car = dom.xpath('//*[@class="controls"]/button[1]/@id')[0]
    url = f'https://abw.by/cars/detail/{id_car}'

    data = dom.xpath('//*[@class="header-actions"]/text()')[0]
    days = ''
    typec = ''
    color = ''
    vin = ''
    exchange = ''

    if work is True:
        pass
    # fresh_minutes = (datetime.now() - published).total_seconds() / 60
    # if fresh_minutes <= WORK_PARSE_CARS_DELTA * 60:
    #     print(data, published)
    #     print(fresh_minutes)
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
            year = r_t["title"].split(",")[1].replace(" ", "")
            price = r_t["price"]["usd"].replace("USD", "").replace(" ", "")
            city = r_t["city"]
            description = r_t["description"].split("/")

            km = description[0].replace(" <br", "").replace(" км", "")
            dimension = description[1].split(" ")[1]
            motor = description[3].replace(" ", "")
            transmission = description[3].replace(" ", "")
            drive = description[-2].replace(" ", "")
            typec = description[-1].replace(" 5 дв.", "")
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


async def bf(semaphore, url, session, result):
    async with semaphore:
        async with session.get(url) as response:
            page_content = await response.text()
            page_content = etree.HTML(str(page_content))
            item = ([*html_links_cars_abw(page_content)])
            result += item


async def run(html, result):
    tasks = []
    semaphore = asyncio.Semaphore(20)
    async with ClientSession(headers=HEADERS) as session:
        if html:
            for url in html:
                task = asyncio.ensure_future(bf(semaphore, url, session, result))
                tasks.append(task)
        await asyncio.gather(*tasks)


async def parse_pages_abw(html, work):
    result = []

    html_links = html_links_abw(html, work)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(html_links, result))
    loop.run_until_complete(future)
    return result


async def abw_html_by_url(url, session):
    try:
        async with session.get(url=url, headers=HEADERS) as response:
            page_content = await response.text()
            page_content = etree.HTML(str(page_content))
        return page_content
    except Exception as e:
        logging.error(f'<abw_html_by_url> {e}')
        return False


def html_parse_price_abw(dom, url):
    price = dom.xpath('//*[@class="price-usd"]')[0].text
    price = price.replace(' ', '').replace('USD', '')
    return [[int(price), url]]


async def get_abw_photo(url, session):
    dom = await abw_html_by_url(url, session)
    image = dom.xpath('//*[@class="main-slide-img"]/@src')[0]
    return image


async def get_abw_stalk_name(url, session):
    try:
        dom = await abw_html_by_url(url, session)
        price = dom.xpath('//*[@class="price-usd"]')[0].text.replace(' ', '').replace('USD', '')
        brand_model = dom.xpath('//*[@class="header-title"]/text()')[0].split(', ')[0].replace('Продажа ', '')
        return brand_model, int(price)

    except Exception as e:
        logging.error(f'<get_av_stalk_name> abw_url: {url} {e}')
        return ' '.join(url.split('/')[-2:]), 0
