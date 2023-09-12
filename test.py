import random
from datetime import datetime, timedelta

from aiogram.client.session import aiohttp
from aiohttp import ClientSession
from lxml import etree
from tqdm import tqdm

from logic.constant import REPORT_PARSE_LIMIT_PAGES, HEADERS, PARSE_LIMIT_PAGES, ROOT_URL, HEADERS_JSON
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


# def get_car_html(id_car):
#     url = f'{ROOT["KUFAR"]}vi/{id_car}'
#     try:
#         response = requests.get(url, HEADERS)
#         page_content = response.text
#         return etree.HTML(str(page_content))
#     except Exception as e:
#         return False
#
#
# id_car = 206938906
#
# dom = get_car_html(id_car)
#
# price = dom.xpath('//*[@data-name="additional-price"]')[0].text
# city = dom.xpath('//*[@data-name="ad_region_listing"]')[0].text
#
#
# print(
#     price,
#     city,
# )


async def read_website():
    url = 'https://api.av.by/home/filters/home/init'
    brands = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            r = await resp.json()
            for car in tqdm(r['blocks'][0]['rows'][0]['propertyGroups'][0]['properties'][0]['value'][0][1]['options']):
                id = car['id']
                name = car['label']
                async with session.get(url='https://api.av.by/offer-types/cars/landings/',
                                       headers=HEADERS_JSON) as resp2:
                    rr = await resp2.json()
                    for ids in rr['seo']['links']:
                        if ids['label'] == name:
                            slug = ids['url'].split('/')[-1]
                        brands.update({name: [id, slug]})
            print(brands)


# loop = asyncio.get_event_loop()
# loop.run_until_complete(read_website())
# # Zero-sleep to allow underlying connections to close
# loop.run_until_complete(asyncio.sleep(0.1))
# loop.close()
asyncio.run(read_website())
if __name__ == '__main__':
    pass
