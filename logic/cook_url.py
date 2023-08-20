from datetime import datetime
import asyncio
import numpy as np
from logic.decorators import timed_lru_cache
from .constant import SS, FSB, REPORT_PARSE_LIMIT_PAGES, PARSE_LIMIT_PAGES, MM
from .database.config import database


def max_min_params(car_input):
    car_input = car_input.split(SS)
    if car_input[4] == FSB:
        car_input[4] = str(MM['MIN_YEAR'])
    if car_input[5] == FSB:
        car_input[5] = str(MM['MAX_YEAR'])
    if car_input[6] == FSB:
        car_input[6] = str(MM['MIN_COST'])
    if car_input[7] == FSB:
        car_input[7] = str(MM['MAX_COST'])
    if car_input[8] == FSB:
        car_input[8] = str(MM['MIN_DIM']*1000)
    if car_input[9] == FSB:
        car_input[9] = str(MM['MAX_DIM']*1000)
    return '+'.join(car_input)


@timed_lru_cache(300)
async def get_url_av(car_input, db, work):
    """
    Формируем гет запрос для av.by
    :param car_input: filter_short
    :param db: database
    :return: гет запрос
    """
    car_input = max_min_params(car_input)
    # Входные параметры
    param_input = ['brands[0][brand]=', 'brands[0][model]=', 'engine_type[0]=', 'transmission_type=', 'year[min]=',
                   'year[max]=', 'price_usd[min]=', 'price_usd[max]=', 'engine_capacity[min]=', 'engine_capacity[max]=']

    # База данных
    car_input = dict(zip(param_input, car_input.split(SS)))
    transmission = dict(a='1', m='2')
    motor = dict(b='1', bpb='2', bm='3', bg='4', d='5', dg='6', e='7')
    brand = car_input['brands[0][brand]=']
    model = car_input['brands[0][model]=']
    if model != FSB:
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
        car_input['brands[0][model]='] = FSB
        car_input['brands[0][brand]='] = rows[0][0]

    if car_input['engine_type[0]='] in motor:
        car_input['engine_type[0]='] = motor[car_input['engine_type[0]=']]
    if car_input['transmission_type='] in transmission:
        car_input['transmission_type='] = transmission[car_input['transmission_type=']]

    new_part = []
    for key in car_input:
        if car_input[key] != FSB:
            new_part.append(str(key)+str(car_input[key]))
    new_part_url = '&'.join(new_part)
    if work is True:
        new_part.append('creation_date=10')
    full_url = f'https://api.av.by/offer-types/cars/filters/main/init?{new_part_url}'
    print(full_url)
    return full_url


@timed_lru_cache(300)
async def get_url_abw(car_input, db):
    """
    Формируем гет запрос для abw.by
    :param car_input: filter_short
    :param db: database
    :return: гет запрос
    """
    car_input = max_min_params(car_input)
    # Входные параметры
    param_input = ['brand_', 'model_', 'engine_', 'transmission_', 'year_',
                   'year_max', 'price_', 'price_max', 'volume_', 'volume_max']
    # вставляем минимумы и максимумы вместо s_b
    min_max_values = ['benzin,dizel,gibrid,sug', 'at,mt', '2000', datetime.now().year, '100', '500000', '0.2', '10.0']
    # цену выдумать нельзя, берется из селектора

    car_input = car_input.split(SS)
    for i in range(len(car_input) - 2):
        if car_input[i + 2] == FSB:
            car_input[i + 2] = min_max_values[i]

    # База данных
    car_input = dict(zip(param_input, car_input))
    cost_selection: list = np.load('logic/database/parse/abw_price_list.npy', allow_pickle=True).tolist()  # noqa
    transmission = dict(a='at', m='mt')
    motor = dict(b='benzin', bpb='sug', bm='sug', bg='gibrid', d='dizel', dg='gibrid', e='elektro')

    # решаем проблему селектора диапазона цены
    minimus = int(car_input['price_'])
    maximus = int(car_input['price_max'])
    if (minimus or maximus) not in cost_selection:
        for i in range(len(cost_selection)-1):
            if int(cost_selection[i]) < minimus and int(cost_selection[i+1]) > minimus:
                car_input['price_'] = cost_selection[i]
            if int(cost_selection[i]) < maximus and int(cost_selection[i+1]) > maximus:
                car_input['price_max'] = cost_selection[i+1]

    brand = car_input['brand_']
    model = car_input['model_']

    if model != FSB:
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
        car_input['model_'] = FSB
        car_input['brand_'] = rows[0][0]

    if (car_input['brand_'] and car_input['model_']) is not None:
        if car_input['engine_'] in motor:
            car_input['engine_'] = motor[car_input['engine_']]
        if car_input['transmission_'] in transmission:
            car_input['transmission_'] = transmission[car_input['transmission_']]
        param = [f"{car_input['brand_']}", f"{car_input['model_']}", f"engine_{car_input['engine_']}",
                 f"transmission_{car_input['transmission_']}", f"year_{car_input['year_']}:{car_input['year_max']}",
                 f"price_{car_input['price_']}:{car_input['price_max']}",
                 f"volume_{car_input['volume_']}:{car_input['volume_max']}", '?sort=new']
        if FSB in param:
            param.remove(FSB)       # удаляем '?' если не выбраны все модели
        new_part_url = '/'.join(param)
        full_url = f'https://b.abw.by/api/adverts/cars/list/{new_part_url}'
        print(full_url)
        return full_url
    else:
        return None


@timed_lru_cache(300)
async def get_url_onliner(car_input, db):
    car_input = max_min_params(car_input)

    param_input = ['car[0][manufacturer]=', 'car[0][model]=', 'engine_type[0]=', 'transmission[0]=', 'year[from]=',
                   'year[to]=', 'price[from]=', 'price[to]=', 'engine_capacity[from]=', 'engine_capacity[to]=']

    # База данных
    car_input = dict(zip(param_input, car_input.split(SS)))
    if car_input['engine_capacity[from]='] != FSB:
        car_input['engine_capacity[from]='] = float(car_input['engine_capacity[from]=']) / 1000
    if car_input['engine_capacity[to]='] != FSB:
        car_input['engine_capacity[to]='] = float(car_input['engine_capacity[to]=']) / 1000

    transmission = {'a': 'automatic', 'm': 'mechanical'}
    motor = dict(b='gasoline', bpb='gasoline&gas=true', bm='gasoline&gas=true', bg='gasoline&hybrid=true', d='diesel',
                 dg='diesel&hybrid=true', e='electric')
    brand = car_input['car[0][manufacturer]=']
    model = car_input['car[0][model]=']
    if model != FSB:
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
        car_input['car[0][model]='] = FSB
        car_input['car[0][manufacturer]='] = rows[0][0]

    if (car_input['car[0][manufacturer]='] and car_input['car[0][model]=']) is not None:
        if car_input['engine_type[0]='] in motor:
            car_input['engine_type[0]='] = motor[car_input['engine_type[0]=']]
        if car_input['transmission[0]='] in transmission:
            car_input['transmission[0]='] = transmission[car_input['transmission[0]=']]

        new_part = []
        for key in car_input:
            if car_input[key] != FSB:
                new_part.append(str(key) + str(car_input[key]))
        new_part.append("order=created_at:desc")
        new_part.append("price[currency]=USD")
        new_part_url = '&'.join(new_part)
        full_url = f'https://ab.onliner.by/sdapi/ab.api/search/vehicles?{new_part_url}'
        print(full_url)
        return full_url
    else:
        return None


@timed_lru_cache(300)
async def get_url_kufar(car_input, db, work):
    car_input = max_min_params(car_input)
    param_input = ['cbnd2=', 'cmdl2=', 'cre=', 'crg=', 'rgd=r:', 'rgd_max', 'prc=r:', 'prc_max', 'crca=r:', 'crca_max']

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

    minimus_d = car_input['crca=r:']
    maximus_d = car_input['crca_max']
    car_input['crca=r:'] = float(minimus_d)/10 if minimus_d != FSB else minimus_d
    car_input['crca_max'] = float(maximus_d)/10 if maximus_d != FSB else maximus_d

    if car_input['cmdl2='] != FSB:
        car_input['cbnd2='] = ''

    new_part = []
    for key in car_input:
        if car_input[key] != FSB:
            new_part.append(str(key) + str(car_input[key]))
    new_part_url = '&'.join(new_part).replace('&rgd_max', ',').replace('&prc_max', ',').replace('&crca_max', ',')
    size = REPORT_PARSE_LIMIT_PAGES * 25 if work is True else PARSE_LIMIT_PAGES * 25
    full_url = f'https://api.kufar.by/search-api/v1/search/' \
               f'rendered-paginated?cat=2010&sort=lst.d&typ=sell&lang=ru&cur=USD&size={size}&{new_part_url}'
    if car_input['cmdl2='] != FSB:
        full_url = full_url.replace('cbnd2=&', '')
    print(full_url)
    return full_url


async def all_get_url(link, work=False):
    async with database() as db:
        return dict(
            av_json=asyncio.run(get_url_av(link, db, work)),
            abw_json=asyncio.run(get_url_abw(link, db)),
            onliner_json=asyncio.run(get_url_onliner(link, db)),
            kufar_json=asyncio.run(get_url_kufar(link, db, work)),
        )
