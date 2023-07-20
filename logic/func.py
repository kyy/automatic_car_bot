from datetime import datetime
import numpy as np
from logic.constant import abw_root_link, s_s, s_b, motor_dict, onliner_root_link
from logic.database.config import database
from logic.parse_sites.abw_by import count_cars_abw
from logic.parse_sites.av_by import count_cars_av
from logic.parse_sites.onliner_by import count_cars_onliner


def get_count_cars(av_link_json, abw_link_json, onliner_link_json):
    # считаем сколько обявлений из json файлов
    all_cars_av = count_cars_av(av_link_json)
    all_cars_abw = count_cars_abw(abw_link_json)
    all_cars_onliner = count_cars_onliner(onliner_link_json)
    return all_cars_av, all_cars_abw, all_cars_onliner


def get_search_links(cars, av_link_json, abw_link_json, onliner_link_json):
    # сслыки на страницы с фильтром поиска
    av_link = f"https://cars.av.by/filter?{av_link_json.split('?')[1]}"
    try:
        abw_link = f"https://abw.by/cars{abw_link_json.split('list')[1]}"
    except:
        abw_link = abw_root_link
    onliner_link = onliner_url_filter(cars, onliner_link_json)
    return av_link, onliner_link, abw_link


def onliner_url_filter(car_input, link):
    try:
        car = car_input.split(s_s)
        brand, model = car[0:2]
        brands = np.load('logic/database/parse/onliner_brands.npy', allow_pickle=True).item()
        link = link.split('vehicles?')[1]
        brand_slug = brands[brand][1]
        if model != s_b:
            models = np.load('logic/database/parse/onliner_models.npy', allow_pickle=True).item()
            model_slug = models[brand][model][2]
            url = f'https://ab.onliner.by/{brand_slug}/{model_slug}?{link}'
        else:
            url = f'https://ab.onliner.by/{brand_slug}?{link}'
        return url
    except:
        return onliner_root_link


async def get_brands() -> list[str]:
    async with database() as db:
        cursor = await db.execute(f"SELECT [unique] FROM brands ORDER BY [unique]")
        rows = await cursor.fetchall()
        brands = []
        for brand in rows:
            brands.append(brand[0])
    return brands


async def get_models(brand: str) -> list[str]:
    async with database() as db:
        cursor = await db.execute(f"SELECT models.[unique] FROM models "
                                  f"INNER JOIN brands on brands.id =  models.brand_id "
                                  f"WHERE brands.[unique] = '{brand}'")
        rows = await cursor.fetchall()
        models = [s_b]
        for brand in rows:
            models.append(brand[0])
    return models


def get_years(from_year: int = 1990, to_year=datetime.now().year) -> list[str]:
    return [s_b] + [str(i) for i in range(from_year, to_year + 1)]


def get_dimension(from_dim: float = 1, to_dim: float = 9, step: float = 0.1) -> list[str]:
    return [s_b] + [str(round(i, 1)) for i in np.arange(from_dim, to_dim + step, step)]


def get_cost(from_cost: int = 500, to_cost: int = 100000, step: int = 2500) -> list[str]:
    return [s_b] + [str(i) for i in range(from_cost, to_cost - step, step)]


# encode from strings = 'Citroen|C4|b|a|-|-|-|-|-|-' or list to full description
def decode_filter_short(string: str = None, lists: list = None, sep: str = s_s):
    motor_dict_reverse = dict(zip(motor_dict.values(), motor_dict.keys()))
    if lists is None:
        c = (string.split(sep=sep))
        if c[2] in motor_dict_reverse:
            c[2] = motor_dict_reverse[c[2]]
        if c[8] != s_b:
            c[8] = str(int(c[8]) / 1000)
        if c[9] != s_b:
            c[9] = str(int(c[9]) / 1000)
        if c[3] != s_b:
            c[3] = 'автомат' if c[3] == 'a' else 'механика'
    else:
        c = lists
    text = f"{c[0].replace(s_b, '<все бренды>')} {c[1].replace(s_b, '<все модели>')}\n" \
           f"{c[2].replace(s_b, '<все типы двигателей>')} {c[3].replace(s_b, '<все типы трансмиссий>')}\n" \
           f"с {c[4].replace(s_b, get_years()[1])}  по {c[5].replace(s_b, str(datetime.now().year))} г\n" \
           f"от {c[6].replace(s_b, get_cost()[1])}  до {c[7].replace(s_b, str(get_cost()[-1]))} $\n" \
           f"от {c[8].replace(s_b, get_dimension()[1])}  до {c[9].replace(s_b, str(get_dimension()[-1]))} л"
    return text if lists else text.replace('\n', ' | ')


# decode from lists of discription to 'filter=Citroen|C4|b|a|-|-|-|-|-|-'
def code_filter_short(cc: list = None):
    if cc[3] != s_b:
        cc[3] = 'a' if cc[3] == 'автомат' else 'm'
    if cc[2] in motor_dict:
        cc[2] = motor_dict[cc[2]]
    if cc[8] != s_b:
        cc[8] = str(int(cc[8].replace('.', '')) * 100)
    if cc[9] != s_b:
        cc[9] = str(int(cc[9].replace('.', '')) * 100)
    return 'filter=' + s_s.join(cc)