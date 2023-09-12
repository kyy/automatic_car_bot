import logging

import numpy as np

from logic.constant import FSB, ROOT, SS
from logic.decorators import timed_lru_cache
from sites.sites_fu import max_min_params


@timed_lru_cache(300)
async def get_url_onliner(car_input, db):
    car_input = max_min_params(car_input)

    param_input = [
        "car[0][manufacturer]=",
        "car[0][model]=",
        "engine_type[0]=",
        "transmission[0]=",
        "year[from]=",
        "year[to]=",
        "price[from]=",
        "price[to]=",
        "engine_capacity[from]=",
        "engine_capacity[to]=",
    ]

    # База данных
    car_input = dict(zip(param_input, car_input))
    if car_input["engine_capacity[from]="] != FSB:
        car_input["engine_capacity[from]="] = float(car_input["engine_capacity[from]="]) / 1000
    if car_input["engine_capacity[to]="] != FSB:
        car_input["engine_capacity[to]="] = float(car_input["engine_capacity[to]="]) / 1000

    transmission = {"a": "automatic", "m": "mechanical"}
    motor = dict(
        b="gasoline",
        bpb="gasoline&gas=true",
        bm="gasoline&gas=true",
        bg="gasoline&hybrid=true",
        d="diesel",
        dg="diesel&hybrid=true",
        e="electric",
    )
    brand = car_input["car[0][manufacturer]="]
    model = car_input["car[0][model]="]
    if model != FSB:
        cursor = await db.execute(
            f"select brands.onliner_by, models.onliner_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'"
        )
        rows = await cursor.fetchall()
        car_input["car[0][manufacturer]="] = rows[0][0]
        car_input["car[0][model]="] = rows[0][1]
    else:
        cursor = await db.execute(
            f"select brands.onliner_by, models.onliner_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}'"
        )
        rows = await cursor.fetchall()
        car_input["car[0][model]="] = FSB
        car_input["car[0][manufacturer]="] = rows[0][0]

    if (car_input["car[0][manufacturer]="] and car_input["car[0][model]="]) is not None:
        if car_input["engine_type[0]="] in motor:
            car_input["engine_type[0]="] = motor[car_input["engine_type[0]="]]
        if car_input["transmission[0]="] in transmission:
            car_input["transmission[0]="] = transmission[car_input["transmission[0]="]]

        new_part = []
        for key in car_input:
            if car_input[key] != FSB:
                new_part.append(str(key) + str(car_input[key]))
        new_part.append("order=created_at:desc")
        new_part.append("price[currency]=USD")
        new_part_url = "&".join(new_part)
        full_url = f"https://ab.onliner.by/sdapi/ab.api/search/vehicles?{new_part_url}"
        logging.info(f'<JSON> {full_url}')
        return full_url
    else:
        return None


@timed_lru_cache(300)
def onliner_url_filter(car_input, onliner_link_json):
    """
    Ссылка на сайт
    :param car_input:фильтр-код
    :param onliner_link_json: ссылка на json
    :return:
    """
    if onliner_link_json is None:
        return ROOT['ONLINER']
    try:
        car = car_input.split(SS)
        brand, model = car[0:2]
        brands: dict = np.load('logic/database/parse/onliner_brands.npy', allow_pickle=True).item()
        link = onliner_link_json.split('vehicles?')[1]
        brand_slug = brands[brand][1]
        if model != FSB:
            models: dict = np.load('logic/database/parse/onliner_models.npy', allow_pickle=True).item()
            model_slug = models[brand][model][2]
            url = f'https://ab.onliner.by/{brand_slug}/{model_slug}?{link}'
        else:
            url = f'https://ab.onliner.by/{brand_slug}?{link}'
        logging.info(f'<HTML> {url}')
        return url
    except Exception as e:
        logging.error(f'<onliner_url_filter> {e}')
        return ROOT['ONLINER']
