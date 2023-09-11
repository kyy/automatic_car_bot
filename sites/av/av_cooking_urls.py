import logging

from logic.constant import FSB, ROOT
from logic.decorators import timed_lru_cache
from sites.fu_sites import max_min_params


@timed_lru_cache(300)
async def get_url_av(car_input, db):
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
    new_part.append('&sort=4')
    new_part_url = "&".join(new_part)
    full_url = f"https://api.av.by/offer-types/cars/filters/main/init?{new_part_url}"
    logging.info(f'<JSON> {full_url}')
    return full_url


@timed_lru_cache(300)
def av_url_filter(av_link_json):
    url = ROOT['AV']
    try:
        url = f"https://cars.av.by/filter?{av_link_json.split('?')[1]}"
        logging.info(f'<HTML> {url}')
    except Exception as e:
        logging.error(f'<av_url_filter> {e}')
        return url
    return url
