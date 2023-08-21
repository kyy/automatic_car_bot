import asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from lxml import etree
import aiosqlite
import numpy as np
import requests
from tqdm import tqdm
from logic.constant import FSB, SS, HEADERS, ROOT
from logic.database.config import database

data_now = datetime.today().date()   # сегодняшняя дата

subscription_days = timedelta(days=900)  # купленные дни

subscription_data = data_now + subscription_days    # пишем в БД дату окончнаия

current = abs(data_now - subscription_data)   # осталось дней

# if data_now > subscription_data:
#     print('Подписка истекла')
# else:
#     print('Подписка истечет через',  str(current).replace('days', 'дней').replace('day', 'день').split(',')[0])
#     print('Подписка истечет ',  subscription_data)
#
#
# string_data = '2026-01-31'
#
#
# newdata = datetime.strptime(string_data, "%Y-%m-%d").date()
# print(newdata)


async def json_urls():
    async with database() as db:
        av_urls_cursor = await db.execute(
            f"""
            SELECT url, id FROM ucars 
            WHERE LOWER(url) LIKE 'https://cars.av.by/%' AND is_active = 1""")
        av_urls = await av_urls_cursor.fetchall()
        av_urls = [(f"https://api.av.by/offers/{i[0].split('/')[-1]}", i[1]) for i in av_urls]
        onliner_urls_cursor = await db.execute(
            f"""
            SELECT url, id FROM ucars
            WHERE LOWER(url) LIKE 'https://ab.onliner.by/%' AND is_active = 1""")
        onliner_urls = await onliner_urls_cursor.fetchall()
        onliner_urls = [(f"https://ab.onliner.by/sdapi/ab.api/vehicles/{i[0].split('/')[-1]}", i[1]) for i in onliner_urls]
        print([*av_urls, *onliner_urls])
        return [*av_urls, *onliner_urls]


if __name__ == '__main__':
    print([i for i in ROOT.values()])

