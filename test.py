import random
from datetime import datetime, timedelta

import numpy as np
from aiogram.client.session import aiohttp
from aiohttp import ClientSession
from lxml import etree
from tqdm import tqdm

from logic.constant import REPORT_PARSE_LIMIT_PAGES, HEADERS, PARSE_LIMIT_PAGES

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



def lenn(items):
    return sum([1 for item in items for sub_item in items[item]])   # noqa

folder = 'logic/database/parse/'

av_m = np.load(f'{folder}av_models.npy', allow_pickle=True).item()


if __name__ == '__main__':
    print(len(av_m))
    print(av_m["BMW"])
