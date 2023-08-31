import random
from datetime import datetime, timedelta

from aiohttp import ClientSession
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
from logic.parse_sites.abw_by import html_links_abw, html_links_cars_abw



params = 'a', 'b', 'c', 'd'










if __name__ == '__main__':
    pass
