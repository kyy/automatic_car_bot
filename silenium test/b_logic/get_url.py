import numpy as np
from .constant_fu import s_s, s_b
import asyncio
import aiosqlite

# av.by
def get_url_av(car_input):
    """
    Формируем гет запрос для av.by
    :param car_input: filter_short
    :return: гет запрос
    """

    # Входные параметры
    param_input = ['brands[0][brand]=', 'brands[0][model]=', 'engine_type[0]=', 'transmission_type=', 'year[min]=',
                   'year[max]=', 'price_usd[min]=', 'price_usd[max]=', 'engine_capacity[min]=', 'engine_capacity[max]=']

    # База данных
    car_input = dict(zip(param_input, car_input.split(s_s)))
    transmission = {'a': '1', 'm': '2'}
    motor = {'b': '1', 'bpb': '2', 'bm': '3', 'bg': '4', 'd': '5', 'dg': '6', 'e': '7'}
    brands = np.load('base_data_av_by/brands_part_url.npy', allow_pickle=True).item()
    models = np.load(f'base_data_av_by/models_part_url/{car_input["brands[0][brand]="]}.npy', allow_pickle=True).item()

    # Корректируем данные для гет-запроса
    if car_input['brands[0][model]='] in models:
        car_input['brands[0][model]='] = models[car_input['brands[0][model]=']]
    if car_input['brands[0][brand]='] in brands:
        car_input['brands[0][brand]='] = brands[car_input['brands[0][brand]=']]
    brand = car_input['brands[0][brand]=']

    if car_input['engine_type[0]='] in motor:
        car_input['engine_type[0]='] = motor[car_input['engine_type[0]=']]
    if car_input['transmission_type='] in transmission:
        car_input['transmission_type='] = transmission[car_input['transmission_type=']]

    new_part = []
    for key in car_input:
        if car_input[key] != s_b:
            new_part.append(str(key)+str(car_input[key]))
    new_part_url = '&'.join(new_part)
    full_url = f'https://cars.av.by/filter?{new_part_url}'
    return full_url


# abw.by
def get_url_abw(car_input):
    """
    Формируем гет запрос для abw.by
    :param car_input: filter_short
    :return: гет запрос
    """
    pass

