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


url = 'https://auto.kufar.by/vi/197066435?rank=1&searchId=292d5de15259399298a61584dd8ed2e66114'
url = f"{'/'.join(url.split('/')[:3])}/"
data = [''.join(i) for i in ROOT.values()]
print(url)
print(data)
if url in data and len(url.split('/')) >= 4:
    print(True)
else:
    print(False)


if __name__ == '__main__':
    pass

