import asyncio
import aiosqlite
import numpy as np
from datetime import datetime


s_s = '+'    # split symbol in filter
s_b = '?'    # skip button on keyboards

# constants of columns:keyboards: max = 8, default = 4
columns_motor = 3
columns_years = 5
columns_cost = 5
columns_dimension = 8

# root links
av_root_link = 'https://av.by/'
abw_root_link = 'https://abw.by/cars'
onliner_root_link = 'https://ab.onliner.by/'

# source of data for buttons
# make '' for delete button

motor_dict = {'бензин': 'b', 'бензин (пропан-бутан)': 'bpb', 'бензин (метан)': 'bm', 'бензин (гибрид)': 'bg',
              'дизель': 'd', 'дизель (гибрид)': 'dg', 'электро': 'e'}

motor = [s_b] + \
        ['бензин', 'дизель', 'электро', 'дизель (гибрид)', 'бензин (метан)', 'бензин (гибрид)', 'бензин (пропан-бутан)']

transmission = [s_b] + ['автомат', 'механика']


async def get_brands() -> list[str]:
    async with aiosqlite.connect('auto_db') as db:
        cursor = await db.execute(f"SELECT [unique] FROM brands ORDER BY [unique]")
        rows = await cursor.fetchall()
        brands = []
        for brand in rows:
            brands.append(brand[0])
    return brands


async def get_models(brand: str) -> list[str]:
    async with aiosqlite.connect('auto_db') as db:
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


def onliner_url_filter(car_input, link):
    try:
        car = car_input.split(s_s)
        brand, model = car[0:2]
        brands = np.load('b_logic/database/parse/onliner_brands.npy', allow_pickle=True).item()
        link = link.split('vehicles?')[1]
        brand_slug = brands[brand][1]
        if model != s_b:
            models = np.load('b_logic/database/parse/onliner_models.npy', allow_pickle=True).item()
            model_slug = models[brand][model][2]
            url = f'https://ab.onliner.by/{brand_slug}/{model_slug}?{link}'
        else:
            url = f'https://ab.onliner.by/{brand_slug}?{link}'
        return url
    except:
        return onliner_root_link


if __name__ == '__main__':
    asyncio.run(get_models(brand='BMW'))
