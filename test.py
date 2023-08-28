import random
from datetime import datetime, timedelta

from lxml import etree

from logic.constant import REPORT_PARSE_LIMIT_PAGES, HEADERS, PARSE_LIMIT_PAGES
from logic.cook_url import abw_url_filter
from logic.database.config import database
import asyncio
import aiosqlite
import requests


# data_now = datetime.today().date()  # сегодняшняя дата
# subscription_days = timedelta(days=900)  # купленные дни
# subscription_data = data_now + subscription_days  # пишем в БД дату окончнаия
# current = abs(data_now - subscription_data)  # осталось дней
#
# if data_now > subscription_data:
#     print('Подписка истекла')
# else:
#     print('Подписка истечет через', str(current).replace('days', 'дней').replace('day', 'день').split(',')[0])
#     print('Подписка истечет ', subscription_data)
#
# string_data = '2026-01-31'
#
# newdata = datetime.strptime(string_data, "%Y-%m-%d").date()
# print(newdata)
#
# sequence = 1, 2, 3
# a = random.choice(sequence)



url = 'https://abw.by/cars/engine_benzin,dizel,gibrid,sug/transmission_at,mt/year_2000:2023/price_500:100000/volume_1000:9000?sort=new'


def html_links_abw(url=url, work=True):

    car = []

    r = requests.get(url, headers=HEADERS).text
    dom = etree.HTML(str(r))

    ln = len(dom.xpath('//*[@class="classified-card__title"]'))

    for i in range(ln):

        brand = dom.xpath('//*[@class="classified-card__title"]/text()')[i].split(', ')[0]
        price = dom.xpath('//*[@class="classified-card__usd"]/text()')[i].replace(' ', '').replace('≈', '').replace('USD', '')
        city = dom.xpath('//*[@class="classified-card__city"]/text()')[i]
        km = dom.xpath('//*[@class="classified-card__description"]/text()[1]')[i].replace(' км', '')
        info = dom.xpath('//*[@class="classified-card__description"]/text()[2]')[i].split(' / ')
        year = info[0]
        dimension = info[1].split(' ')[0]
        motor = info[2]
        transmission = info[3]
        drive = info[4]
        id_car = dom.xpath('//*[@class="lower-controls"]/button/@id')[i]
        url = f'https://abw.by/cars/detail/{id_car}'
        data = dom.xpath('//*[@class="lower-time"]/text()')[i]
        days = ''
        typec = ''
        color = ''
        vin = ''
        exchange = ''
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
    count = int(dom.xpath('//*[@class="list-proposal__quantity-bold"]/text()')[0].replace('\xa0', ''))
    print(count)


if __name__ == '__main__':
    html_links_abw()
