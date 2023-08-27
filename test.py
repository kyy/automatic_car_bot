# import random
# from datetime import datetime, timedelta
#
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
import asyncio

import aiosqlite
import requests

from logic.constant import REPORT_PARSE_LIMIT_PAGES, HEADERS, PARSE_LIMIT_PAGES
from logic.database.config import database
from logic.func import kufar_url_filter, abw_url_filter

url = 'https://b.abw.by/api/adverts/cars/list/brand_audi/model_a6/engine_benzin,dizel,gibrid,sug/transmission_at,mt/year_2000:2023/price_500:100000/volume_1000:9000/?sort=new'


def html_links_abw(url=url, work=True):
    url_html = abw_url_filter(url)
    print(url_html)
    try:
        links_to_html = []
        r = requests.get(url, headers=HEADERS).json()
        page_count = r["pagination"]["pages"]
        links_to_html.append(url_html)
        i = 1
        limit_page = PARSE_LIMIT_PAGES if work is True else REPORT_PARSE_LIMIT_PAGES
        if page_count >= limit_page:  # - - - - - - ограничение вывода страниц
            page_count = limit_page  # - - - - - - ограничение вывода страниц
            while page_count > 1:
                i += 1
                links_to_html.append(f"{url_html}?page={i}")
                page_count -= 1
        print(links_to_html)
        return links_to_html
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    html_links_abw()
