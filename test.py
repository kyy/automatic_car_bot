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


def urls_html(html, work):
    cars = []
    return cars


async def bound_fetch_html(semaphore, url, session, result):
    async with semaphore:
        async with session.get(url) as response:
            page_content = await response.text()
            page_content = etree.HTML(str(page_content))
            pages = html_links_abw(abw, work)
            item = ([*html_links_cars_abw(pages)])
            result += item



async def run(html, result, work):
    tasks = []

    semaphore = asyncio.Semaphore(20)
    async with ClientSession(headers=HEADERS) as session:
        if html:
            for url in html:
                task = asyncio.ensure_future(bound_fetch_html(semaphore, url, session, result, work))
                tasks.append(task)

        await asyncio.gather(*tasks)


async def parse_main(json, html, tel_id, name, work=False, send_car_job=None):

    result = []


    html_links = urls_html(html, work)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(html_links, result, work))
    loop.run_until_complete(future)
    if work is True:
        await send_car_job(tel_id, result)
    else:
        np.save(f"logic/buffer/{name}.npy", result)
    return result
if __name__ == '__main__':
    pass
