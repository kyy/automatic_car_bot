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



HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Host': 'api.kufar.by',
    'Origin': 'https://auto.kufar.by',
    'Referer': 'https://auto.kufar.by/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
}


import requests

model = 'https://api.kufar.by/catalog/v1/nodes?tag=category_2010.mark_audi&view=taxonomy'
brand = 'https://api.kufar.by/catalog/v1/nodes?tag=category_2010&view=taxonomy'
search = 'https://api.kufar.by/search-api/v1/search/rendered-paginated?cat=2010&cbnd2=category_2010.mark_gmc&cmdl2=category_2010.mark_gmc.model_terrain&cre=v.or:1&cur=USD&lang=ru&mlg=r:5000,999999&prc=r:6666,66666&rgd=r:2000,2023&size=30&sort=lst.d&typ=sell'

data = aiosqlite.connect(database='auto_db')

async def get_url_kufar(db, car_input='BMW+X5+d+a+2000+2023+666+6666+1.120+250', work=False):

    param_input = [
        'cbnd2=',
        'cmdl2=',
        'cre=',
        'crg=',
        'rgd=r:',
        'rgd_max',
        'prc=r:',
        'prc_max',
        'crca=r:',
        'crca_max'
    ]

    car_input = dict(zip(param_input, car_input.split(SS)))
    transmission = dict(a='1', m='2')
    motor = dict(b='v.or:1', bpb='v.or:3', bm='v.or:6', bg='v.or:4', d='v.or:2', dg='v.or:7', e='v.or:5')
    brand = car_input['cbnd2=']
    model = car_input['cmdl2=']
    if model != FSB:
        cursor = await db.execute(f"select brands.kufar_by, models.kufar_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'")
        rows = await cursor.fetchall()
        car_input['cbnd2='] = rows[0][0]
        car_input['cmdl2='] = rows[0][1]
    else:
        cursor = await db.execute(f"select brands.kufar_by, models.kufar_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}'")
        rows = await cursor.fetchall()
        car_input['cmdl2='] = FSB
        car_input['cbnd2='] = rows[0][0]

    if car_input['cre='] in motor:
        car_input['cre='] = motor[car_input['cre=']]
    if car_input['crg='] in transmission:
        car_input['crg='] = transmission[car_input['crg=']]

    new_part = []
    for key in car_input:
        if car_input[key] != FSB:
            new_part.append(str(key)+str(car_input[key]))
    new_part_url = '&'.join(new_part).replace('&rgd_max', ',').replace('&prc_max', ',').replace('&crca_max', ',')
    if work is True:
        new_part.append('creation_date=10')
    full_url = f'https://api.kufar.by/search-api/v1/search/rendered-paginated?cat=2010&sort=lst.d&typ=sell&lang=ru&size=30&{new_part_url}'


async def main():
    async with data as db:
        await get_url_kufar(db=db)

if __name__ == '__main__':
    asyncio.run(main())
