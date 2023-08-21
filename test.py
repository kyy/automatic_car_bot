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



URL = 'https://cars.av.by/acura/tsx/105530026123'

r = requests.get(url=URL, headers=HEADERS)



print(r)
if __name__ == '__main__':
    pass


