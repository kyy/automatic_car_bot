from datetime import datetime
from functools import lru_cache
from .decorators import timed_lru_cache
import numpy as np
from logic.constant import ABW_ROOT, SS, MOTOR_DICT, ONLINER_ROOT, FSB
from logic.database.config import database
from logic.cook_url import all_get_url
from logic.parse_sites.abw_by import count_cars_abw
from logic.parse_sites.av_by import count_cars_av
from logic.parse_sites.onliner_by import count_cars_onliner
from aiocache import cached, Cache


@timed_lru_cache(300)
def get_count_cars(av_link_json, abw_link_json, onliner_link_json):
    # считаем сколько обявлений из json файлов
    all_cars_av = count_cars_av(av_link_json)
    all_cars_abw = count_cars_abw(abw_link_json)
    all_cars_onliner = count_cars_onliner(onliner_link_json)
    return all_cars_av, all_cars_abw, all_cars_onliner


@timed_lru_cache(300)
def get_search_links(cars, av_link_json, abw_link_json, onliner_link_json):
    # сслыки на страницы с фильтром поиска
    av_link = f"https://cars.av.by/filter?{av_link_json.split('?')[1]}"
    try:
        abw_link = f"https://abw.by/cars{abw_link_json.split('list')[1]}"
    except:
        abw_link = ABW_ROOT
    onliner_link = onliner_url_filter(cars, onliner_link_json)
    return av_link, onliner_link, abw_link


async def filter_import(callback, db):
    filter_id = callback.data.split('_')[1]     # id фильтра
    async with db:
        select_filter_cursor = await db.execute(f"""SELECT search_param FROM udata WHERE id = {filter_id}""")
        filter_name = await select_filter_cursor.fetchone()     # фильтр-код ('filter=...',)
    cars = filter_name[0][7:] # удаляем 'filter='
    return filter_id, filter_name, cars


@cached(ttl=300, cache=Cache.MEMORY, namespace="car_multidata")
async def car_multidata(cars):
    # cars - фильтр-код
    av_link_json, abw_link_json, onliner_link_json = await all_get_url(cars)
    all_cars_av, all_cars_abw, all_cars_onliner = get_count_cars(av_link_json, abw_link_json, onliner_link_json)
    av_link, onliner_link, abw_link = get_search_links(cars, av_link_json, abw_link_json, onliner_link_json)
    return (av_link_json, abw_link_json, onliner_link_json,     # ссылки к файлу Json
            all_cars_av, all_cars_abw, all_cars_onliner,    # количество объявлений
            av_link, abw_link, onliner_link)    # ссылка на страницу на сайте


@timed_lru_cache(300)
def onliner_url_filter(car_input, link):
    try:
        car = car_input.split(SS)
        brand, model = car[0:2]
        brands = np.load('logic/database/parse/onliner_brands.npy', allow_pickle=True).item()
        link = link.split('vehicles?')[1]
        brand_slug = brands[brand][1]
        if model != FSB:
            models = np.load('logic/database/parse/onliner_models.npy', allow_pickle=True).item()
            model_slug = models[brand][model][2]
            url = f'https://ab.onliner.by/{brand_slug}/{model_slug}?{link}'
        else:
            url = f'https://ab.onliner.by/{brand_slug}?{link}'
        return url
    except:
        return ONLINER_ROOT


@cached(ttl=300, cache=Cache.MEMORY, key='brands', namespace="get_brands")
async def get_brands() -> list[str]:
    async with database() as db:
        cursor = await db.execute(f"SELECT [unique] FROM brands ORDER BY [unique]")
        rows = await cursor.fetchall()
        brands = []
        for brand in rows:
            brands.append(brand[0])
    return brands


@cached(ttl=300, cache=Cache.MEMORY, namespace="get_models")
async def get_models(brand: str) -> list[str]:
    async with database() as db:
        cursor = await db.execute(f"SELECT models.[unique] FROM models "
                                  f"INNER JOIN brands on brands.id =  models.brand_id "
                                  f"WHERE brands.[unique] = '{brand}'")
        rows = await cursor.fetchall()
        models = []
        for brand in rows:
            models.append(brand[0])
    return models


@lru_cache()
def get_years(from_year: int = 1990, to_year=datetime.now().year) -> list[str]:
    return [str(i) for i in range(from_year, to_year + 1)]


@lru_cache()
def get_dimension(from_dim: float = 1, to_dim: float = 9, step: float = 0.1) -> list[str]:
    return [str(round(i, 1)) for i in np.arange(from_dim, to_dim + step, step)]


@lru_cache()
def get_cost(from_cost: int = 500, to_cost: int = 100000, step: int = 2500) -> list[str]:
    return [str(i) for i in range(from_cost, to_cost - step, step)]


# encode from strings = 'Citroen|C4|b|a|-|-|-|-|-|-' or list to full description
def decode_filter_short(string: str = None, lists: list = None, sep: str = SS):
    motor_dict_reverse = dict(zip(MOTOR_DICT.values(), MOTOR_DICT.keys()))
    if lists is None:
        c = (string.split(sep=sep))

        if c[2] in motor_dict_reverse:
            c[2] = motor_dict_reverse[c[2]]
        if c[8] != FSB:
            c[8] = str(int(c[8]) / 1000)
        if c[9] != FSB:
            c[9] = str(int(c[9]) / 1000)
        if c[3] != FSB:
            c[3] = 'автомат' if c[3] == 'a' else 'механика'
    else:
        c = lists
    text = f"{c[0].replace(FSB, 'все бренды')} {c[1].replace(FSB, 'все модели')} " \
           f"{c[2].replace(FSB, 'все типы двигателей')} {c[3].replace(FSB, 'все типы трансмиссий')} " \
           f"с {c[4].replace(FSB, get_years()[1])}  по {c[5].replace(FSB, str(datetime.now().year))} г " \
           f"от {c[6].replace(FSB, get_cost()[1])}  до {c[7].replace(FSB, str(get_cost()[-1]))} $ " \
           f"от {c[8].replace(FSB, get_dimension()[1])}  до {c[9].replace(FSB, str(get_dimension()[-1]))} л"
    return text if lists else text.replace('\n', ' | ')


# decode from lists of discription to 'filter=Citroen|C4|b|a|-|-|-|-|-|-'
def code_filter_short(cc: list = None):
    if cc[3] != FSB:
        cc[3] = 'a' if cc[3] == 'автомат' else 'm'
    if cc[2] in MOTOR_DICT:
        cc[2] = MOTOR_DICT[cc[2]]
    if cc[8] != FSB:
        cc[8] = str(int(cc[8].replace('.', '')) * 100)
    if cc[9] != FSB:
        cc[9] = str(int(cc[9].replace('.', '')) * 100)
    return 'filter=' + SS.join(cc)
