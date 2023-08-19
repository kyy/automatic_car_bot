import asyncio
from datetime import datetime, timedelta

import aiosqlite
import numpy as np
from tqdm import tqdm

from logic.constant import FSB, SS
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


a = {'av_link': 'https://cars.av.by/filter?brands[0][brand]=1&brands[0][model]=3&engine_type[0]=5&year[min]=1990&year[max]=2023', 'onliner_link': 'https://ab.onliner.by/alfa-romeo/146?car[0][manufacturer]=3&car[0][model]=69&engine_type[0]=diesel&year[from]=1990&year[to]=2023&order=created_at:desc&price[currency]=USD', 'abw_link': 'https://abw.by/cars/brand_alfa-romeo/model_146/engine_dizel/transmission_at,mt/year_1990:2023/price_100:500000/volume_0.2:10.0/?sort=new', 'kufar_link': 'https://auto.kufar.by/l/cars/alfa-romeo-146?cur=USD&sort=lst.d&lang=ru&size=100&cre=v.or:2&rgd=r:1990,2023'}


if __name__ == '__main__':
    print(a['av_link'])
