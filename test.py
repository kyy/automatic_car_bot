import asyncio
from datetime import datetime, timedelta

import numpy as np
from tqdm import tqdm

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

def con() -> None:
    url = 'https://api.kufar.by/catalog/v1/nodes&view=taxonomy?tag='
    brands = np.load(f'logic/database/parse/', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        r = requests.get(f'{url}{brands[item][0]}', headers=headers).json()
        models_dict = {}
        for car in r:
            name = car['label']['ru']
            id = car['value']
            slug = id.split('mark_')[1].replace('_', '-').replace('.', '-')
            models_dict.update({name: [id, name, slug]})
        brand_dict.update({item: models_dict})
    print(brands)

if __name__ == '__main__':
    con()