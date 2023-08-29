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

data = '2 часов назад'


def html_links_abw(data: str):
    data_split = data.split(' ')
    num = data_split[0]
    if '' \
       'секунд' in data:
        return 0
    elif 'несколько минут' in data:
        return 1
    elif 'минут' in data and type(int(num)) is int:
        return int(num)
    elif 'часов' in data and type(int(num)) is int:
        return int(num) * 60
    elif 'дней' in data and type(int(num)) is int:
        return int(num) * 60 * 24


if __name__ == '__main__':
    print(html_links_abw(data))
