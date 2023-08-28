import asyncio
from datetime import datetime

import numpy as np

from logic.decorators import timed_lru_cache
from .constant import SS, FSB, REPORT_PARSE_LIMIT_PAGES, PARSE_LIMIT_PAGES, MM, ROOT
from .database.config import database


def max_min_params(car_input):
    car_input = car_input.split(SS)
    if car_input[4] == FSB:
        car_input[4] = str(MM["MIN_YEAR"])
    if car_input[5] == FSB:
        car_input[5] = str(MM["MAX_YEAR"])
    if car_input[6] == FSB:
        car_input[6] = str(MM["MIN_COST"])
    if car_input[7] == FSB:
        car_input[7] = str(MM["MAX_COST"])
    if car_input[8] == FSB:
        car_input[8] = str(MM["MIN_DIM"] * 1000)
    if car_input[9] == FSB:
        car_input[9] = str(MM["MAX_DIM"] * 1000)
    return car_input


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
    param_input = [
        "brands[0][brand]=",
        "brands[0][model]=",
        "engine_type[0]=",
        "transmission_type=",
        "year[min]=",
        "year[max]=",
        "price_usd[min]=",
        "price_usd[max]=",
        "engine_capacity[min]=",
        "engine_capacity[max]=",
    ]

    # База данных
    car_input = dict(zip(param_input, car_input))
    transmission = dict(a="1", m="2")
    motor = dict(b="1", bpb="2", bm="3", bg="4", d="5", dg="6", e="7")
    brand = car_input["brands[0][brand]="]
    model = car_input["brands[0][model]="]
    if model != FSB:
        cursor = await db.execute(
            f"select brands.av_by, models.av_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'"
        )
        rows = await cursor.fetchall()
        car_input["brands[0][brand]="] = rows[0][0]
        car_input["brands[0][model]="] = rows[0][1]
    else:
        cursor = await db.execute(
            f"select brands.av_by, models.av_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}'"
        )
        rows = await cursor.fetchall()
        car_input["brands[0][model]="] = FSB
        car_input["brands[0][brand]="] = rows[0][0]

    if car_input["engine_type[0]="] in motor:
        car_input["engine_type[0]="] = motor[car_input["engine_type[0]="]]
    if car_input["transmission_type="] in transmission:
        car_input["transmission_type="] = transmission[car_input["transmission_type="]]

    new_part = []
    for key in car_input:
        if car_input[key] != FSB:
            new_part.append(str(key) + str(car_input[key]))
    new_part_url = "&".join(new_part)
    if work is True:
        new_part.append("creation_date=10")
    full_url = f"https://api.av.by/offer-types/cars/filters/main/init?{new_part_url}"
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
        return full_url
    else:
        return None


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
        return full_url
    else:
        return None


@timed_lru_cache(300)
async def get_url_kufar(car_input, db, work):
    car_input = max_min_params(car_input)
    param_input = ["cbnd2=", "cmdl2=", "cre=", "crg=", "rgd=r:", "rgd_max", "prc=r:", "prc_max", "crca=r:", "crca_max"]
    car_input = dict(zip(param_input, car_input))
    transmission = dict(a="1", m="2")
    motor = dict(b="v.or:1", bpb="v.or:3", bm="v.or:6", bg="v.or:4", d="v.or:2", dg="v.or:7", e="v.or:5")
    brand = car_input["cbnd2="]
    model = car_input["cmdl2="]
    if model != FSB:
        cursor = await db.execute(
            f"select brands.kufar_by, models.kufar_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'"
        )
        rows = await cursor.fetchall()
        car_input["cbnd2="] = rows[0][0]
        car_input["cmdl2="] = rows[0][1]
    else:
        cursor = await db.execute(
            f"select brands.kufar_by, models.kufar_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}'"
        )
        rows = await cursor.fetchall()
        car_input["cmdl2="] = FSB
        car_input["cbnd2="] = rows[0][0]

    if car_input["cre="] in motor:
        car_input["cre="] = motor[car_input["cre="]]
    if car_input["crg="] in transmission:
        car_input["crg="] = transmission[car_input["crg="]]

    dim_k = [i for i in range(1000, 4100, 100)]
    dim_v = [
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        170,
        173,
        175,
        180,
        183,
        190,
        190,
        200,
        205,
        205,
        210,
        211,
        212,
        213,
        214,
        220,
    ]
    dim = dict(zip(dim_k, dim_v))

    minimus_d = car_input["crca=r:"]
    maximus_d = car_input["crca_max"]

    car_input["crca=r:"] = dim[int(minimus_d)] if (4000 > int(minimus_d) > 1000) and (int(minimus_d) in dim_k) else 1
    car_input["crca_max"] = dim[int(maximus_d)] if (4000 > int(maximus_d) > 1000) and (int(maximus_d) in dim_k) else 230

    if car_input["cmdl2="] != FSB:
        car_input["cbnd2="] = ""

    new_part = []
    for key in car_input:
        if car_input[key] != FSB:
            new_part.append(str(key) + str(car_input[key]))
    new_part_url = "&".join(new_part).replace("&rgd_max", ",").replace("&prc_max", ",").replace("&crca_max", ",")
    size = REPORT_PARSE_LIMIT_PAGES * 25 if work is True else PARSE_LIMIT_PAGES * 25
    full_url = (
        f"https://api.kufar.by/search-api/v1/search/"
        f"rendered-paginated?cat=2010&sort=lst.d&typ=sell&lang=ru&cur=USD&size={size}&{new_part_url}"
    )
    if car_input["cmdl2="] != FSB:
        full_url = full_url.replace("cbnd2=&", "")
    return full_url


async def all_json(link, work=False):
    async with database() as db:
        return dict(
            av_json=asyncio.run(get_url_av(link, db, work)),
            abw_json=asyncio.run(get_url_abw(link, db)),
            onliner_json=asyncio.run(get_url_onliner(link, db)),
            kufar_json=asyncio.run(get_url_kufar(link, db, work)),
        )


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
        return url
    except Exception as e:
        print('[cook_url.onliner_url_filter]', e)
        return ROOT['ONLINER']


@timed_lru_cache(300)
def av_url_filter(av_link_json):
    return ROOT['AV'] if av_link_json is None else f"https://cars.av.by/filter?{av_link_json.split('?')[1]}"


@timed_lru_cache(300)
def kufar_url_filter(kufar_link_json):
    if kufar_link_json is None:
        return ROOT['KUFAR']
    try:
        if '=category_2010.mark_' in kufar_link_json:
            kuf = kufar_link_json.replace('&cmdl2', '').replace('&cbnd2', '').split('=category_2010.mark_')
            kufar_link = kuf[1].replace('_', '-').replace('.model', '')
            kufar_link1, kufar_link2 = kufar_link, ''
            if '&' in kufar_link:
                kufar_link = kufar_link.split('&', 1)
                kufar_link1, kufar_link2 = kufar_link[0], kufar_link[1]
            kuf = kuf[0].split('/')[-1] \
                .replace('rendered-paginated?cat=2010', '').replace('&typ=sell', '').replace('&cur=USD', '')
            kufar_link = f"https://auto.kufar.by/l/cars/{kufar_link1}?cur=USD{kuf}&{kufar_link2}"
            return kufar_link
        else:
            return ROOT['KUFAR']
    except Exception as e:
        print('[cook_url.kufar_url_filter]', e)
        return ROOT['KUFAR']


@timed_lru_cache(300)
def abw_url_filter(abw_link_json):
    if abw_link_json is None:
        return ROOT['ABW']
    try:
        abw_link = f"https://abw.by/cars{abw_link_json.split('list')[1]}"
        return abw_link
    except Exception as e:
        print('[cook_url.abw_url_filter]', e)
        return ROOT['ABW']


def all_html(filter, json):
    """
    Получаем ссылки на человекочитаемые страницы
    :param filter: фильтр код из бд
    :param json: словарь с ссылками на json
    :return:
    """
    # сслыки на страницы с фильтром поиска
    av_link = av_url_filter(json['av_json'])
    onliner_link = onliner_url_filter(filter, json['onliner_json'])
    kufar_link = kufar_url_filter(json['kufar_json'])
    abw_link = abw_url_filter(json['abw_json'])
    return dict(
        av_link=av_link,
        onliner_link=onliner_link,
        abw_link=abw_link,
        kufar_link=kufar_link,
    )
