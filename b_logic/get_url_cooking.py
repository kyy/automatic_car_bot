from datetime import datetime
import asyncio
import aiosqlite
import numpy as np
from .constant_fu import s_s, s_b
from .database.config import db_name


async def get_url_av(car_input, db):
    """
    Формируем гет запрос для av.by
    :param car_input: filter_short
    :param db: database
    :return: гет запрос
    """

    # Входные параметры
    param_input = ['brands[0][brand]=', 'brands[0][model]=', 'engine_type[0]=', 'transmission_type=', 'year[min]=',
                   'year[max]=', 'price_usd[min]=', 'price_usd[max]=', 'engine_capacity[min]=', 'engine_capacity[max]=']

    # База данных
    car_input = dict(zip(param_input, car_input.split(s_s)))
    transmission = {'a': '1', 'm': '2'}
    motor = {'b': '1', 'bpb': '2', 'bm': '3', 'bg': '4', 'd': '5', 'dg': '6', 'e': '7'}
    brand = car_input['brands[0][brand]=']
    model = car_input['brands[0][model]=']
    if model != s_b:
        cursor = await db.execute(f"select brands.av_by, models.av_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'")
        rows = await cursor.fetchall()
        car_input['brands[0][brand]='] = rows[0][0]
        car_input['brands[0][model]='] = rows[0][1]
    else:
        cursor = await db.execute(f"select brands.av_by, models.av_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}'")
        rows = await cursor.fetchall()
        car_input['brands[0][model]='] = s_b
        car_input['brands[0][brand]='] = rows[0][0]

    if car_input['engine_type[0]='] in motor:
        car_input['engine_type[0]='] = motor[car_input['engine_type[0]=']]
    if car_input['transmission_type='] in transmission:
        car_input['transmission_type='] = transmission[car_input['transmission_type=']]

    new_part = []
    for key in car_input:
        if car_input[key] != s_b:
            new_part.append(str(key)+str(car_input[key]))
    new_part_url = '&'.join(new_part)
    full_url = f'https://api.av.by/offer-types/cars/filters/main/init?{new_part_url}'
    print(full_url)
    return full_url


async def get_url_abw(car_input, db):
    """
    Формируем гет запрос для abw.by
    :param car_input: filter_short
    :param db: database
    :return: гет запрос
    """
    # Входные параметры
    param_input = ['brand_', 'model_', 'engine_', 'transmission_', 'year_',
                   'year_max', 'price_', 'price_max', 'volume_', 'volume_max']
    # вставляем минимумы и максимумы вместо s_b
    min_max_values = ['benzin,dizel,gibrid,sug', 'at,mt', '2000', datetime.now().year, '100', '500000', '0.2', '10.0']
    # цену выдумать нельзя, берется из селектора

    car_input = car_input.split(s_s)
    for i in range(len(car_input) - 2):
        if car_input[i + 2] == s_b:
            car_input[i + 2] = min_max_values[i]

    # База данных
    car_input = dict(zip(param_input, car_input))
    cost_selection = np.load('b_logic/database/parse/abw_price_list.npy', allow_pickle=True).tolist()
    transmission = {'at': '1', 'mt': '2'}
    motor = {'b': 'benzin', 'bpb': 'sug', 'bm': 'sug', 'bg': 'gibrid', 'd': 'dizel', 'dg': 'gibrid', 'e': 'elektro'}

    # решаем проблему селектора диапазона цены
    min = car_input['price_']
    max = car_input['price_max']
    i = 0
    if (min or max) not in cost_selection:
        for i in range(len(cost_selection)-1):
            if cost_selection[i] < min and cost_selection[i+1] > min:
                car_input['price_'] = cost_selection[i]
            if cost_selection[i] < max and cost_selection[i+1] > max:
                car_input['price_max'] = cost_selection[i+1]
            i += 1

    brand = car_input['brand_']
    model = car_input['model_']

    if model != s_b:
        cursor = await db.execute(f"select brands.abw_by, models.abw_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'")
        rows = await cursor.fetchall()
        car_input['brand_'] = rows[0][0]
        car_input['model_'] = rows[0][1]
    else:
        cursor = await db.execute(f"select brands.abw_by, models.abw_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}'")
        rows = await cursor.fetchall()
        car_input['model_'] = s_b
        car_input['brand_'] = rows[0][0]

    if (car_input['brand_'] and car_input['model_']) is not None:
        if car_input['engine_'] in motor:
            car_input['engine_'] = motor[car_input['engine_']]
        if car_input['transmission_'] in transmission:
            car_input['transmission_'] = transmission[car_input['transmission_']]

        param = [f"{car_input['brand_']}",
                 f"{car_input['model_']}",
                 f"engine_{car_input['engine_']}",
                 f"transmission_{car_input['transmission_']}",
                 f"year_{car_input['year_']}:{car_input['year_max']}",
                 f"price_{car_input['price_']}:{car_input['price_max']}",
                 f"volume_{car_input['volume_']}:{car_input['volume_max']}"
                 ]
        if s_b in param:
            param.remove(s_b)       # удаляем '?' если не выбраны все модели
        new_part_url = '/'.join(param)
        full_url = f'https://b.abw.by/api/adverts/cars/list/{new_part_url}'
        print(full_url)
        return full_url
    else:
        return None


async def get_url_onliner(car_input, db):
    param_input = ['car[0][manufacturer]=', 'car[0][model]=', 'engine_type[0]=', 'transmission[0]=', 'year[from]=',
                   'year[to]=', 'price[from]=', 'price[to]', 'engine_capacity[from]=', 'engine_capacity[to]=']

    # База данных
    car_input = dict(zip(param_input, car_input.split(s_s)))
    if car_input['engine_capacity[from]='] != s_b:
        car_input['engine_capacity[from]='] = int(car_input['engine_capacity[from]='])
        car_input['engine_capacity[from]='] /= 1000
    if car_input['engine_capacity[to]='] != s_b:
        car_input['engine_capacity[to]='] = int(car_input['engine_capacity[to]='])
        car_input['engine_capacity[to]='] /= 1000
    transmission = {'a': 'automatic', 'm': 'mechanical'}
    motor = {'b': 'gasoline', 'bpb': 'gasoline&gas=true', 'bm': 'gasoline&gas=true', 'bg': 'gasoline&hybrid=true',
             'd': 'diesel', 'dg': 'diesel&hybrid=true', 'e': 'electric'}
    brand = car_input['car[0][manufacturer]=']
    model = car_input['car[0][model]=']
    if model != s_b:
        cursor = await db.execute(f"select brands.onliner_by, models.onliner_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'")
        rows = await cursor.fetchall()
        car_input['car[0][manufacturer]='] = rows[0][0]
        car_input['car[0][model]='] = rows[0][1]
    else:
        cursor = await db.execute(f"select brands.onliner_by, models.onliner_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}'")
        rows = await cursor.fetchall()
        car_input['car[0][model]='] = s_b
        car_input['car[0][manufacturer]='] = rows[0][0]

    if (car_input['car[0][manufacturer]='] and car_input['car[0][model]=']) is not None:
        if car_input['engine_type[0]='] in motor:
            car_input['engine_type[0]='] = motor[car_input['engine_type[0]=']]
        if car_input['transmission[0]='] in transmission:
            car_input['transmission[0]='] = transmission[car_input['transmission[0]=']]

        new_part = []
        for key in car_input:
            if car_input[key] != s_b:
                new_part.append(str(key) + str(car_input[key]))
        new_part_url = '&'.join(new_part)+'&price[currency]=USD'
        full_url = f'https://ab.onliner.by/sdapi/ab.api/search/vehicles?{new_part_url}'
        print(full_url)
        return full_url
    else:
        return None


async def all_get_url(link):
    async with aiosqlite.connect(db_name) as db:
        return (asyncio.run(get_url_av(link, db)),
                asyncio.run(get_url_abw(link, db)),
                asyncio.run(get_url_onliner(link, db)),
                )


if __name__ == '__main__':
    pass
