import logging
from datetime import datetime

from logic.constant import FSB, ROOT
from logic.decorators import timed_lru_cache

import numpy as np

from sites.sites_fu import max_min_params


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
    param_input = [
        "brand_",
        "model_",
        "engine_",
        "transmission_",
        "year_",
        "year_max",
        "price_",
        "price_max",
        "volume_",
        "volume_max",
    ]
    # вставляем минимумы и максимумы вместо s_b
    min_max_values = ["benzin,dizel,gibrid,sug", "at,mt", "2000", datetime.now().year, "100", "500000", "0.2", "10.0"]
    # цену выдумать нельзя, берется из селектора

    car_input = car_input
    for i in range(len(car_input) - 2):
        if car_input[i + 2] == FSB:
            car_input[i + 2] = min_max_values[i]

    # База данных
    car_input = dict(zip(param_input, car_input))
    cost_selection: list = np.load("logic/database/parse/abw_price_list.npy", allow_pickle=True).tolist()  # noqa
    transmission = dict(a="at", m="mt")
    motor = dict(b="benzin", bpb="sug", bm="sug", bg="gibrid", d="dizel", dg="gibrid", e="elektro")

    # решаем проблему селектора диапазона цены
    minimus = int(car_input["price_"])
    maximus = int(car_input["price_max"])
    if (minimus or maximus) not in cost_selection:
        for i in range(len(cost_selection) - 1):
            if int(cost_selection[i]) < minimus and int(cost_selection[i + 1]) > minimus:
                car_input["price_"] = cost_selection[i]
            if int(cost_selection[i]) < maximus and int(cost_selection[i + 1]) > maximus:
                car_input["price_max"] = cost_selection[i + 1]

    brand = car_input["brand_"]
    model = car_input["model_"]

    if model != FSB:
        cursor = await db.execute(
            f"select brands.abw_by, models.abw_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'"
        )
        rows = await cursor.fetchall()
        car_input["brand_"] = rows[0][0]
        car_input["model_"] = rows[0][1]
    else:
        cursor = await db.execute(
            f"select brands.abw_by, models.abw_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}'"
        )
        rows = await cursor.fetchall()
        car_input["model_"] = FSB
        car_input["brand_"] = rows[0][0]

    if (car_input["brand_"] and car_input["model_"]) is not None:
        if car_input["engine_"] in motor:
            car_input["engine_"] = motor[car_input["engine_"]]
        if car_input["transmission_"] in transmission:
            car_input["transmission_"] = transmission[car_input["transmission_"]]
        param = [
            f"{car_input['brand_']}",
            f"{car_input['model_']}",
            f"engine_{car_input['engine_']}",
            f"transmission_{car_input['transmission_']}",
            f"year_{car_input['year_']}:{car_input['year_max']}",
            f"price_{car_input['price_']}:{car_input['price_max']}",
            f"volume_{car_input['volume_']}:{car_input['volume_max']}",
            "?sort=new",
        ]
        if FSB in param:
            param.remove(FSB)  # удаляем '?' если не выбраны все модели
        new_part_url = "/".join(param)
        full_url = f"https://b.abw.by/api/adverts/cars/list/{new_part_url}"
        logging.info(f'<JSON> {full_url}')
        return full_url
    else:
        return None


@timed_lru_cache(300)
def abw_url_filter(abw_link_json):
    url = ROOT['ABW']
    try:
        url = f"https://abw.by/cars{abw_link_json.split('list')[1]}"
    except Exception as e:
        logging.error(f'<abw_url_filter> {e}')
        return url
    logging.info(f'<HTML> {url}')
    return url
